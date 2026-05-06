"""FastAPI 앱 조립 — 미들웨어, 라우터 include, 헬스체크 한 줄.

개발: `uv run uvicorn app.main:app --reload`
운영: `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='*'`
어느 쪽으로도 띄울 수 있게 모듈 끝에서 `app`을 노출한다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth as auth_router
from app.routers import notes as notes_router

settings = get_settings()


def create_app() -> FastAPI:
    """애플리케이션 팩토리.

    테스트에서 의존성 오버라이드를 쓰기 좋도록 함수로 감쌌습니다.
    """
    app = FastAPI(
        title="Note API",
        description="10장 종합 예제 — 회원가입·로그인·개인 메모 CRUD",
        version="0.1.0",
    )

    # CORS — 프론트엔드가 다른 도메인일 때 브라우저의 차단을 풀어준다.
    # 운영에서는 ["*"] 대신 실제 도메인 목록을 명시할 것.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # 라우터 등록.
    app.include_router(auth_router.router)
    app.include_router(notes_router.router)

    @app.get("/health", tags=["health"], summary="헬스체크")
    async def health() -> dict[str, str]:
        """앱이 살아 있는지 확인하는 가벼운 체크.

        운영 환경의 로드밸런서·오케스트레이터가 주기적으로 호출한다.
        """
        return {"status": "ok"}

    return app


app = create_app()
