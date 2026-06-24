"""FastAPI 앱 엔트리 포인트 — BackgroundTasks 예제.

`uvicorn app.main:app --reload` 가 이 파일의 `app` 객체를 찾아 실행한다.

이 예제가 보여 주는 것:
- `POST /signup` 은 사용자 등록 응답을 **즉시** 돌려주고, 환영 알림·감사 로그·보너스
  포인트 지급을 **백그라운드로** 처리한다(응답 전송 후 실행).
- `BackgroundTasks` 를 라우터 파라미터로 직접 받는 방법과, 의존성으로 주입받는 방법을
  둘 다 보여 준다.
- `GET /notifications`, `GET /audit-log` 로 백그라운드 작업이 실제로 수행됐는지 확인한다.
"""

from __future__ import annotations

from fastapi import BackgroundTasks, Depends, FastAPI, status
from pydantic import BaseModel, Field

from app import state, tasks

app = FastAPI(
    title="Background Tasks 예제",
    version="0.1.0",
    description="15장 — 응답을 먼저 보내고 뒤에서 처리하는 BackgroundTasks 예제.",
)


# --- 스키마 ----------------------------------------------------------------


class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)


class SignupResponse(BaseModel):
    username: str
    status: str = "registered"


class NotificationsResponse(BaseModel):
    notifications: list[str]


class AuditLogResponse(BaseModel):
    entries: list[dict[str, str]]


# --- 엔드포인트 ------------------------------------------------------------


@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["signup"],
    summary="회원가입 — 응답을 먼저 주고 알림은 백그라운드로",
)
async def signup(
    payload: SignupRequest,
    background_tasks: BackgroundTasks,
) -> SignupResponse:
    """가입 응답을 즉시 돌려주고, 뒤이어 여러 백그라운드 작업을 실행한다.

    `background_tasks: BackgroundTasks` 를 인자로 적기만 하면 FastAPI 가 객체를
    주입해 준다. `add_task` 로 등록한 함수들은 **이 함수가 응답을 반환하고, 그 응답이
    클라이언트에게 모두 전송된 뒤** 등록한 순서대로 실행된다.
    """
    # 여러 작업을 등록한다. 등록 순서대로 실행된다.
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    background_tasks.add_task(
        tasks.record_signup_audit, payload.username, source="signup"
    )
    background_tasks.add_task(tasks.grant_starter_points, payload.username)

    # 여기서 함수가 끝나면 클라이언트는 즉시 201 응답을 받는다.
    # 위에서 등록한 세 작업은 그 직후 백그라운드에서 실행된다.
    return SignupResponse(username=payload.username)


def audit_logger(background_tasks: BackgroundTasks) -> BackgroundTasks:
    """`BackgroundTasks` 를 의존성 안에서 주입받는 패턴.

    의존성 함수도 시그니처에 `BackgroundTasks` 를 적으면 FastAPI 가 **같은 객체**를
    주입해 준다(요청당 하나로 공유된다). 라우터마다 반복되는 "이런 요청엔 이 감사
    로그를 남긴다" 같은 공통 작업을 여기서 미리 등록해 두면, 라우터는 의존성을
    선언만 해도 그 작업이 함께 실행된다.

    반환값으로 같은 `background_tasks` 를 돌려주므로, 라우터는 이어서 다른 작업도
    등록할 수 있다.
    """
    background_tasks.add_task(
        tasks.record_signup_audit, "(dependency)", source="dependency"
    )
    return background_tasks


@app.post(
    "/signup-via-dependency",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["signup"],
    summary="의존성으로 BackgroundTasks 주입받기",
)
async def signup_via_dependency(
    payload: SignupRequest,
    background_tasks: BackgroundTasks = Depends(audit_logger),
) -> SignupResponse:
    """의존성(`audit_logger`)이 등록한 작업과, 라우터가 직접 등록한 작업이 함께
    실행되는 것을 보여 준다.

    `background_tasks` 는 `Depends(audit_logger)` 로 주입받는다. 의존성이 먼저 감사
    로그 작업을 등록했고, 라우터는 같은 객체에 환영 알림 작업을 이어 등록한다.
    """
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    return SignupResponse(username=payload.username)


@app.post(
    "/signup-with-risky-task",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["signup"],
    summary="실패할 수 있는 부수 작업과 안전한 작업을 함께 등록",
)
async def signup_with_risky_task(
    payload: SignupRequest,
    background_tasks: BackgroundTasks,
) -> SignupResponse:
    """실패할 수 있는 작업(`risky_side_effect`)을 먼저 등록해도, 그 작업이 예외를
    함수 안에서 삼키므로 뒤에 등록한 `notify_welcome` 이 정상 실행된다."""
    background_tasks.add_task(tasks.risky_side_effect, payload.username)
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    return SignupResponse(username=payload.username)


@app.get(
    "/notifications",
    response_model=NotificationsResponse,
    tags=["signup"],
    summary="기록된 환영 알림 조회(검증용)",
)
async def list_notifications() -> NotificationsResponse:
    return NotificationsResponse(notifications=list(state.notifications))


@app.get(
    "/audit-log",
    response_model=AuditLogResponse,
    tags=["signup"],
    summary="감사 로그 조회(검증용)",
)
async def list_audit_log() -> AuditLogResponse:
    return AuditLogResponse(entries=list(state.audit_log))
