"""학습용 인메모리 상태.

실무라면 DB·메시지 큐·외부 서비스가 들어갈 자리지만, 이 챕터의 주제는
"백그라운드 작업이 응답 이후에 실제로 실행되는가" 이므로 가장 단순한 형태인
**프로세스 메모리 안의 리스트/딕셔너리**로 둔다.

`reset()` 은 테스트에서 매 테스트 전에 호출해 상태를 깨끗이 비운다. 인메모리
상태는 프로세스 수명 동안 계속 누적되므로, 격리를 위해 반드시 초기화가 필요하다.
"""

from __future__ import annotations

# 가입 환영 알림 기록(테스트 검증용). notify_welcome 가 여기에 append 한다.
notifications: list[str] = []

# 감사 로그. record_signup_audit 가 여기에 append 한다.
audit_log: list[dict[str, str]] = []

# 사용자별 가입 보너스 포인트. 멱등성 데모(grant_starter_points)에서 쓴다.
points: dict[str, int] = {}

# 실패한 부수 작업 기록. 예외 안전성 데모(risky_side_effect)에서 쓴다.
failures: list[str] = []


def reset() -> None:
    """모든 인메모리 상태를 초기화한다(주로 테스트에서 호출)."""
    notifications.clear()
    audit_log.clear()
    points.clear()
    failures.clear()
