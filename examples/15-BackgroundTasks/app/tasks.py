"""백그라운드에서 실행될 "작업 함수"들만 모아 둔 모듈.

라우터(`app/main.py`)는 이 함수들을 `background_tasks.add_task(...)` 로 등록만 한다.
**응답이 클라이언트에게 모두 전송된 뒤** FastAPI 가 여기 함수들을 차례대로 실행한다.

작업 함수 설계의 두 가지 약속을 이 파일에서 그대로 보여 준다.

1. **예외 안전성** — 작업 함수가 예외를 던지면 그 뒤에 등록된 다른 작업이 실행되지
   않을 수 있다. 그래서 "실패해도 무방한" 부수 작업은 함수 안에서 예외를 직접
   삼키고(로그만 남기고) 조용히 끝낸다.
2. **멱등성(idempotency)** — 같은 입력으로 두 번 실행돼도 상태가 한 번 실행한 것과
   같아야 안전하다. 재시도·중복 호출에 대비한 기본 자세다.

이 예제는 학습용이라 "외부 시스템" 대신 인메모리 리스트(`app/state.py`)에 기록한다.
실무라면 이 자리에 이메일 발송·슬랙 알림·썸네일 생성 같은 코드가 들어간다.
"""

from __future__ import annotations

import logging

from app import state

logger = logging.getLogger("background-tasks")


def notify_welcome(username: str) -> None:
    """동기 작업 함수 — 가입 환영 알림을 "기록"한다.

    `def`(동기)로 선언했다는 점이 중요하다. FastAPI 는 동기 작업 함수를
    **스레드풀**에서 실행하므로, 여기서 약간의 블로킹 작업(파일 쓰기 등)을 해도
    이벤트 루프를 막지 않는다.
    """
    message = f"환영합니다, {username}님! 가입이 완료되었습니다."
    state.notifications.append(message)
    logger.info("welcome notification queued for %s", username)


async def record_signup_audit(username: str, *, source: str = "signup") -> None:
    """비동기 작업 함수 — 감사 로그를 한 줄 남긴다.

    작업 함수는 `def`(동기) 든 `async def`(비동기) 든 모두 등록할 수 있다.
    DB 세션·httpx 호출처럼 `await` 가 필요한 작업이라면 이렇게 `async def` 로 둔다.
    """
    state.audit_log.append({"username": username, "source": source})


def grant_starter_points(username: str, points: int = 100) -> None:
    """멱등성을 보여 주는 작업 함수 — 가입 보너스 포인트를 1회만 지급한다.

    같은 사용자에게 이 함수가 두 번 실행돼도(재시도·중복 등록) 포인트가 두 배로
    들어가지 않는다. "이미 지급했으면 건너뛴다" 는 조건 하나가 멱등성을 만든다.
    """
    if username in state.points:
        logger.info("starter points already granted for %s — skip", username)
        return
    state.points[username] = points


def risky_side_effect(username: str) -> None:
    """예외 안전성을 보여 주는 작업 함수.

    부수 작업(예: 외부 알림)이 실패할 수 있다고 가정한다. 이 작업이 실패해도
    **요청 처리 자체는 이미 끝났고**, 뒤에 등록된 다른 작업도 멈추면 안 된다.
    그래서 예외를 함수 안에서 잡아 로그만 남기고 조용히 끝낸다.
    """
    try:
        # 실무라면 여기서 외부 호출이 일어나고, 그게 실패할 수 있다.
        raise RuntimeError("외부 알림 서버 응답 없음")
    except Exception as exc:  # noqa: BLE001 - 부수 작업이라 광범위하게 잡아 삼킨다.
        state.failures.append(f"{username}: {exc}")
        logger.warning("side effect failed for %s: %s", username, exc)
