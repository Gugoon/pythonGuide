"""요청 ID 를 코드 어디에서나 꺼내 쓰기 위한 컨텍스트 저장소.

`contextvars.ContextVar` 는 "지금 처리 중인 요청 하나"에 묶이는 전역 변수다.
미들웨어가 요청 시작 시점에 ID 를 here 에 심어두면, 같은 요청을 처리하는
모든 코드(라우터, crud, 로깅 필터 등)가 인자로 ID 를 주고받지 않고도
`get_request_id()` 한 줄로 같은 값을 읽을 수 있다.

> 왜 그냥 전역 변수(`REQUEST_ID = ...`)가 아니라 ContextVar 인가?
> 비동기 서버는 여러 요청을 동시에(번갈아) 처리한다. 평범한 전역 변수는
> 요청들이 같은 값을 덮어써서 로그가 뒤섞인다. ContextVar 는 각 실행
> 흐름(async task)마다 독립된 값을 보관하므로 안전하다.
"""

from contextvars import ContextVar

# 기본값 "-" : 아직 미들웨어를 거치지 않은(요청 밖) 로그에도 안전하게 찍힌다.
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    """현재 요청의 ID 를 컨텍스트에 저장한다(미들웨어가 호출)."""
    _request_id_ctx.set(request_id)


def get_request_id() -> str:
    """현재 요청의 ID 를 읽는다. 요청 밖이면 '-' 를 돌려준다."""
    return _request_id_ctx.get()
