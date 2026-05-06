"""애플리케이션 환경 설정.

`.env` 파일과 OS 환경 변수에서 값을 읽어 들입니다. 비밀키와 DB 접속 정보 등
민감한 값은 코드에 직접 박지 않고 한 곳에 모아 둡니다.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱이 동작할 때 필요한 설정 묶음.

    Pydantic v2의 BaseSettings는 클래스 속성을 환경 변수와 자동 매핑합니다.
    예: `secret_key` 속성 ↔ `SECRET_KEY` 환경 변수.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 데이터베이스 URL — MySQL + asyncmy(비동기) 드라이버.
    # 테스트에서는 이 값을 인메모리 SQLite로 덮어 씁니다(conftest.py 참고).
    database_url: str = (
        "mysql+asyncmy://blog_user:blog_pass@127.0.0.1:3306/blog_api"
    )

    # JWT 서명용 비밀키. 운영에서는 .env로 반드시 강한 난수를 주입합니다.
    # 기본값은 PyJWT 2.x의 InsecureKeyLengthWarning(<32바이트)을 피하기 위해
    # 32바이트 이상으로 둔 더미 문자열입니다.
    secret_key: str = "please-change-this-to-32-bytes-or-longer-random-string"

    # JWT 알고리즘 — 이 가이드는 단일 서버 가정 → HS256 고정.
    algorithm: str = "HS256"

    # 액세스 토큰 만료 시간(분).
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """설정을 한 번만 읽고 캐시한다(같은 인스턴스 반환)."""
    return Settings()
