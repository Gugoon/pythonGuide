"""보안 관련 함수 한 곳 모음.

비밀번호 해싱·검증, JWT 발급·검증의 네 함수가 모여 있습니다. 다른 모듈은
이 함수들만 호출하고 bcrypt와 jwt 라이브러리를 직접 다루지 않습니다.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings
from app.schemas import TokenPayload

settings = get_settings()

# Bcrypt는 입력의 첫 72바이트만 사용한다. 그 이상이면 73번째 바이트부터는
# 무시되어 "긴 비밀번호 일부를 바꿔도 같다"는 헷갈리는 버그가 된다.
# 한국어는 UTF-8 기준 글자당 3바이트라, 24글자 근처에서 잘리기 시작한다.
MAX_PASSWORD_BYTES = 72


def hash_password(plain: str) -> str:
    """평문 비밀번호를 Bcrypt로 해싱한 뒤, DB 저장용 문자열로 돌려준다.

    Returns:
        Bcrypt 해시 문자열 (예: '$2b$12$...').

    Raises:
        ValueError: 입력이 UTF-8 기준 72바이트를 초과한 경우.
    """
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"비밀번호가 너무 깁니다(UTF-8 기준 {MAX_PASSWORD_BYTES}바이트 초과). "
            "한국어는 글자당 3바이트로 계산됩니다."
        )
    # bcrypt.gensalt()는 매번 새로운 솔트를 만들어 내므로
    # 같은 비밀번호라도 매번 다른 해시 결과가 나온다.
    hashed_bytes = bcrypt.hashpw(encoded, bcrypt.gensalt())
    # bytes → str. DB의 String 컬럼에 그대로 저장하기 위함.
    return hashed_bytes.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문이 저장된 해시와 일치하는지 검사한다.

    내부적으로 bcrypt.checkpw가 솔트와 코스트를 해시 문자열에서 꺼내
    같은 알고리즘으로 다시 계산해 비교한다. 상수 시간 비교라 타이밍 공격에도 안전.
    """
    encoded_plain = plain.encode("utf-8")
    encoded_hash = hashed.encode("utf-8")
    if len(encoded_plain) > MAX_PASSWORD_BYTES:
        # 정상적으로 회원가입했다면 이 길이는 이미 막혔어야 한다.
        # 안전을 위해 비교 단계에서도 거부.
        return False
    try:
        return bcrypt.checkpw(encoded_plain, encoded_hash)
    except ValueError:
        # DB에 잘못된 해시 문자열이 들어가 있는 경우(예: 평문 저장 후 마이그레이션 사고)
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """sub(=사용자 ID)를 담은 JWT 액세스 토큰을 만든다.

    Args:
        subject: 토큰의 주체. 보통 사용자 ID를 문자열로.
        expires_minutes: 만료까지 분. None이면 설정값 사용.
    """
    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_minutes

    # timezone-aware datetime을 사용해야 서버 환경별 시간대 차이로 인한
    # 만료 어긋남이 생기지 않는다. 항상 UTC.
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """JWT를 검증하고 TokenPayload로 돌려준다.

    검증 단계에서 일어날 수 있는 일:
    - 서명 불일치/형식 오류: jwt.InvalidTokenError 또는 그 하위 예외
    - 만료된 경우: jwt.ExpiredSignatureError (InvalidTokenError의 자식)

    호출하는 쪽(deps.py의 get_current_user)에서 두 예외를 분기 처리한다.

    `algorithms`는 반드시 리스트로, 명시적으로 한 가지만 적는다.
    이 인자를 비우거나 'none'을 포함시키면 위조 토큰이 통과될 수 있다.
    """
    raw = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    return TokenPayload(**raw)
