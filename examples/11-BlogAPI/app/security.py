"""보안 관련 함수 모음 — 비밀번호 해싱·검증, JWT 발급·검증.

이 파일은 08장의 같은 이름 모듈과 거의 동일합니다. 11장 종합 예제도
같은 인증 구조를 그대로 재사용합니다.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings
from app.schemas import TokenPayload

settings = get_settings()

# Bcrypt는 입력의 첫 72바이트만 사용한다. 한국어는 UTF-8 기준 글자당 3바이트라
# 24글자 근처에서 잘리기 시작하므로, 사전에 길이 검증을 둔다.
MAX_PASSWORD_BYTES = 72


def hash_password(plain: str) -> str:
    """평문 비밀번호를 Bcrypt로 해싱하고 DB 저장용 문자열로 돌려준다."""
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"비밀번호가 너무 깁니다(UTF-8 기준 {MAX_PASSWORD_BYTES}바이트 초과). "
            "한국어는 글자당 3바이트로 계산됩니다."
        )
    hashed_bytes = bcrypt.hashpw(encoded, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문이 저장된 해시와 일치하는지 검사한다."""
    encoded_plain = plain.encode("utf-8")
    encoded_hash = hashed.encode("utf-8")
    if len(encoded_plain) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(encoded_plain, encoded_hash)
    except ValueError:
        # DB에 잘못된 해시가 들어 있는 경우(예: 평문 저장 사고)
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """sub(=사용자 ID)를 담은 JWT 액세스 토큰을 만든다."""
    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_minutes

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    """JWT를 검증하고 TokenPayload로 돌려준다.

    - 서명 불일치/형식 오류: jwt.InvalidTokenError 또는 그 하위 예외
    - 만료된 경우: jwt.ExpiredSignatureError
    """
    raw = jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    return TokenPayload(**raw)
