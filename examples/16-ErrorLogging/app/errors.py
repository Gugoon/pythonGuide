"""커스텀 예외 + 일관된 에러 응답 스키마 + 전역 예외 핸들러.

이 모듈 하나가 "에러가 났을 때 클라이언트에게 무엇을 어떤 모양으로 돌려줄지"를
모두 결정한다. 핵심 아이디어 세 가지:

1. **도메인 예외**(`ResourceNotFound`, `BusinessRuleError`)를 정의한다.
   라우터·서비스 코드는 상황에 맞는 예외를 `raise` 하기만 한다.
2. **모든 에러 응답을 같은 JSON 모양**으로 만든다: ``{"error": {"code", "message", "detail"}}``.
   클라이언트는 항상 같은 자리에서 에러 코드를 읽을 수 있다.
3. 각 예외를 알맞은 HTTP 상태 코드로 변환하는 **전역 핸들러**를 등록한다.
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.request_context import get_request_id

logger = logging.getLogger("app.errors")


# ---------------------------------------------------------------------------
# 1) 일관된 에러 응답 스키마
# ---------------------------------------------------------------------------
class ErrorBody(BaseModel):
    """에러 응답의 `error` 안쪽 본문."""

    code: str  # 기계가 분기할 수 있는 짧은 식별자 (예: "resource_not_found")
    message: str  # 사람이 읽는 한 줄 설명
    detail: object | None = None  # 부가 정보(검증 에러 목록 등). 없으면 null.
    request_id: str  # 이 에러가 발생한 요청의 ID. 로그와 대조할 수 있다.


class ErrorResponse(BaseModel):
    """최상위 에러 응답. 모든 에러가 이 모양으로 나간다."""

    error: ErrorBody


def _render(
    *,
    status_code: int,
    code: str,
    message: str,
    detail: object | None = None,
) -> JSONResponse:
    """일관된 에러 JSON 응답을 만든다. 모든 핸들러가 이 함수를 거친다."""
    body = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            detail=detail,
            request_id=get_request_id(),
        )
    )
    return JSONResponse(
        status_code=status_code,
        # model_dump() 만으로는 datetime 등 일부 타입이 JSON 으로 안 바뀔 수 있어
        # jsonable_encoder 로 한 번 더 감싸 안전하게 직렬화한다.
        content=jsonable_encoder(body.model_dump()),
    )


# ---------------------------------------------------------------------------
# 2) 도메인(커스텀) 예외
# ---------------------------------------------------------------------------
class AppError(Exception):
    """이 앱의 모든 도메인 예외의 부모.

    공통 속성을 정의해 두면, 핸들러 하나로 자식 예외 전부를 처리할 수 있다.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"

    def __init__(self, message: str, *, detail: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class ResourceNotFound(AppError):
    """요청한 자원이 없을 때. 404 로 매핑된다."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "resource_not_found"

    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(
            message=f"{resource} {resource_id!r} 를 찾을 수 없습니다",
            detail={"resource": resource, "id": resource_id},
        )


class BusinessRuleError(AppError):
    """비즈니스 규칙 위반(예: 잔액 부족, 중복 신청). 409 로 매핑된다."""

    status_code = status.HTTP_409_CONFLICT
    code = "business_rule_violation"


# ---------------------------------------------------------------------------
# 3) 전역 예외 핸들러
# ---------------------------------------------------------------------------
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """우리가 정의한 도메인 예외를 일관된 JSON 으로 변환한다."""
    # 4xx(클라이언트 잘못)는 WARNING, 5xx(서버 잘못)는 ERROR 로 레벨을 나눈다.
    if exc.status_code >= 500:
        logger.error("도메인 예외(5xx): %s", exc.message, exc_info=exc)
    else:
        logger.warning("도메인 예외: %s (code=%s)", exc.message, exc.code)
    return _render(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
    )


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """`HTTPException`(과 Starlette 의 404 등)도 같은 에러 모양으로 통일한다.

    이렇게 해두면 직접 `raise HTTPException(...)` 한 곳, 존재하지 않는 경로(404),
    405 등 프레임워크가 자동으로 내는 에러까지 모두 같은 JSON 스키마로 나간다.
    """
    logger.warning("HTTP 예외: %s (status=%s)", exc.detail, exc.status_code)
    return _render(
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        message=str(exc.detail),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """요청 검증 실패(422)를 우리 스키마에 맞게 다듬는다.

    FastAPI 기본 422 응답은 `{"detail": [...]}` 모양이라 다른 에러와 형태가 다르다.
    여기서 같은 `{"error": {...}}` 스키마로 감싸고, Pydantic 이 준 상세 목록을
    `detail` 에 그대로 담아 클라이언트가 어느 필드가 틀렸는지 알 수 있게 한다.
    """
    logger.warning("검증 실패: %d 건", len(exc.errors()))
    return _render(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="요청 본문 검증에 실패했습니다",
        # errors() 안에는 예외 객체 등 JSON 으로 못 바꾸는 값이 섞일 수 있어
        # jsonable_encoder 로 안전하게 변환한다.
        detail=jsonable_encoder(exc.errors()),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """그 외 예상 못 한 모든 예외 → 500.

    트레이스백은 서버 로그에만 남기고, 클라이언트에게는 내부 구현을 노출하지
    않는 일반 메시지만 돌려준다(보안). 대신 `request_id` 를 함께 주므로,
    사용자가 그 ID 를 알려주면 운영자가 로그에서 정확한 트레이스백을 찾을 수 있다.
    """
    logger.error("처리되지 않은 예외", exc_info=exc)
    return _render(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="서버 내부 오류가 발생했습니다",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """위 핸들러들을 앱에 한꺼번에 등록한다(main.py 에서 한 줄 호출)."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
