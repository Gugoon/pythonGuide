"""애플리케이션 환경 설정.

`.env` 파일과 OS 환경 변수에서 값을 읽어 들입니다. 비밀키 등 민감한 값을
코드에 박지 않도록 한 곳에 모았습니다.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱이 동작할 때 필요한 설정 묶음.

    Pydantic v2의 BaseSettings는 클래스 속성을 환경 변수와 자동으로 매핑합니다.
    예: `secret_key` 속성 ↔ `SECRET_KEY` 환경 변수.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── DB ──────────────────────────────────────────────────────
    # 운영의 기본은 PostgreSQL + asyncpg.
    # 테스트(tests/conftest.py)는 이 값을 무시하고 메모리 SQLite를 직접 띄운다.
    database_url: str = (
        "postgresql+asyncpg://note_user:note_pass@localhost:5432/note_api"
    )

    # ── JWT ─────────────────────────────────────────────────────
    # 운영에서는 .env로 반드시 강한 난수를 주입.
    # 기본값은 PyJWT 2.x의 InsecureKeyLengthWarning(<32바이트)을 피하기 위해
    # 32바이트 이상으로 둔 더미 문자열이다.
    secret_key: str = "please-change-this-to-32-bytes-or-longer-random-string"
    # 이 가이드는 단일 서버 가정 → HS256 고정.
    algorithm: str = "HS256"
    # 액세스 토큰 만료 시간(분).
    access_token_expire_minutes: int = 60

    # ── CORS ────────────────────────────────────────────────────
    # 쉼표로 구분한 도메인 목록. "*"이면 모두 허용.
    cors_allow_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        """문자열을 리스트로 정리해 미들웨어에 넘기기 쉽게."""
        raw = self.cors_allow_origins.strip()
        if raw == "" or raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    """설정을 한 번만 읽고 캐시한다(함수가 여러 번 호출돼도 같은 인스턴스 반환)."""
    return Settings()
