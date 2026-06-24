"""FastAPI 앱 엔트리 포인트 — 16장 에러 핸들링·로깅 심화 예제.

`uvicorn app.main:app --reload` 가 이 파일의 `app` 객체를 찾아 실행한다.

이 파일은 조립만 한다.

1. 로깅을 설정하고(`setup_logging`),
2. 요청 ID 미들웨어를 붙이고(`RequestIdMiddleware`),
3. 전역 예외 핸들러를 등록하고(`register_exception_handlers`),
4. 동작을 시연하는 엔드포인트 몇 개를 둔다.

각 동작의 자세한 구현은 errors.py / middleware.py / logging_config.py 에 나뉘어 있다.
"""

import logging

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.errors import BusinessRuleError, ResourceNotFound, register_exception_handlers
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware

# 앱이 import 되는 시점에 로깅을 한 번 설정한다.
setup_logging(level=logging.INFO)
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Error Logging Example",
    version="0.1.0",
    description="16장 — 커스텀 예외, 일관된 에러 응답, 요청 ID 미들웨어, 표준 logging.",
)

# 미들웨어 등록. add_middleware 로 붙인 것은 "가장 나중에 추가한 것이 가장 바깥"이다.
# 요청 ID 는 모든 처리의 가장 바깥에서 부여돼야 하므로 여기 한 줄이면 충분하다.
app.add_middleware(RequestIdMiddleware)

# 전역 예외 핸들러 등록(errors.py 의 핸들러 묶음).
register_exception_handlers(app)


# ---------------------------------------------------------------------------
# 시연용 자료와 스키마
# ---------------------------------------------------------------------------
# 학습용 인메모리 "DB". 실제 앱이라면 06~07장처럼 SQLAlchemy 가 들어온다.
ITEMS: dict[int, dict] = {
    1: {"id": 1, "name": "노트북", "stock": 3},
    2: {"id": 2, "name": "키보드", "stock": 0},
}


class OrderRequest(BaseModel):
    """주문 요청 본문. 검증 에러를 시연하기 위해 제약을 건다."""

    item_id: int = Field(ge=1, description="주문할 상품 ID (1 이상)")
    quantity: int = Field(ge=1, le=100, description="수량 (1~100)")


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    """살아 있는지 확인하는 정상 응답 엔드포인트."""
    return {"status": "ok"}


@app.get("/items/{item_id}", tags=["items"], summary="단건 조회(정상/404 시연)")
async def get_item(item_id: int) -> dict:
    """있으면 정상 200, 없으면 커스텀 예외 `ResourceNotFound` → 일관된 404 JSON."""
    item = ITEMS.get(item_id)
    if item is None:
        # HTTPException 대신 도메인 예외를 던진다. 변환은 전역 핸들러가 맡는다.
        raise ResourceNotFound("item", item_id)
    return item


@app.post("/orders", tags=["orders"], summary="주문(검증/비즈니스 규칙 시연)")
async def create_order(payload: OrderRequest) -> dict:
    """주문을 시도한다.

    - 본문 검증 실패(item_id<1, quantity 범위 밖 등) → 422 (검증 핸들러가 처리).
    - 없는 상품 → 404 (`ResourceNotFound`).
    - 재고 부족 → 409 (`BusinessRuleError`).
    - 정상 → 201 처럼 동작(여기서는 200 으로 단순화).
    """
    item = ITEMS.get(payload.item_id)
    if item is None:
        raise ResourceNotFound("item", payload.item_id)

    if payload.quantity > item["stock"]:
        # 비즈니스 규칙 위반. detail 에 부가 정보를 실어 보낸다.
        raise BusinessRuleError(
            "재고가 부족합니다",
            detail={"requested": payload.quantity, "in_stock": item["stock"]},
        )

    logger.info("주문 성공 item_id=%s quantity=%s", payload.item_id, payload.quantity)
    return {
        "ordered": True,
        "item_id": payload.item_id,
        "quantity": payload.quantity,
    }


@app.get("/boom", tags=["demo"], summary="예상 못 한 예외 시연(500)")
async def boom() -> dict:
    """일부러 평범한 예외를 던져 500 핸들러를 시연한다.

    클라이언트에게는 일반 메시지 + request_id 만, 서버 로그에는 트레이스백이 남는다.
    """
    raise ValueError("의도적으로 발생시킨 내부 오류")
