"""앱 설정 모듈.

환경 변수(또는 .env 파일)에서 값을 읽어 들여 한 객체(`settings`)로 모읍니다.
이 객체는 다른 모듈에서 `from app.config import settings` 로 가져다 씁니다.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """이 앱이 쓰는 환경 변수 묶음.

    - 클래스 속성으로 선언한 이름이 곧 환경 변수 이름이 됩니다(대소문자 무시).
    - .env 파일이 있으면 자동으로 읽습니다.
    - 환경 변수와 .env 둘 다 있으면 환경 변수가 우선합니다.
    """

    # 앱 표시용 이름. /docs 의 페이지 제목 등에 쓰입니다.
    app_name: str = "Todo API"

    # DB 접속 URL. 기본값은 같은 폴더의 todo.db 파일을 가리키는 SQLite.
    # PostgreSQL 로 바꾸려면 .env 의 DATABASE_URL 만 교체하면 됩니다.
    database_url: str = "sqlite+aiosqlite:///./todo.db"

    # CORS 허용 도메인. 콤마로 여러 개 지정 가능.
    # 예: "http://localhost:3000,https://example.com"
    # 개발 단계에서는 "*"(모든 도메인 허용) 도 허용합니다.
    cors_allow_origins: str = "*"

    # .env 파일을 읽도록 알려주는 설정.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """콤마로 구분된 문자열을 리스트로 변환."""
        raw = self.cors_allow_origins.strip()
        if raw == "" or raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


# 앱 어디서나 같은 인스턴스를 쓰도록 모듈 로드 시 한 번만 만듭니다.
settings = Settings()
