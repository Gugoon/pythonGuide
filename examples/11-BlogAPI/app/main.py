"""FastAPI 앱 조립.

라우터 등록, CORS 미들웨어 등록, 헬스체크 한 줄.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth as auth_router
from app.routers import comments as comments_router_module
from app.routers import posts as posts_router
from app.routers import tags as tags_router


def create_app() -> FastAPI:
    """애플리케이션 팩토리.

    테스트에서 의존성을 덮어쓰기 쉽도록 함수로 감쌌습니다.
    """
    app = FastAPI(
        title="Blog API",
        description=(
            "11장 — 종합 예제. User · Post · Comment · Tag (1:N, N:M) + "
            "JWT 인증 + MySQL."
        ),
        version="0.1.0",
    )

    # CORS — 운영에서는 ["*"] 대신 실제 도메인 목록을 명시할 것.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(auth_router.router)
    app.include_router(posts_router.router)
    app.include_router(comments_router_module.post_comments_router)
    app.include_router(comments_router_module.comments_router)
    app.include_router(tags_router.router)

    @app.get("/health", tags=["health"], summary="헬스체크")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
