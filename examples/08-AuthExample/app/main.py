"""FastAPI 앱 조립.

라우터 등록, CORS 미들웨어 등록, 헬스체크 한 줄.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth as auth_router
from app.routers import users as users_router


def create_app() -> FastAPI:
    """애플리케이션 팩토리.

    테스트에서 의존성을 덮어쓰기 쉽도록 함수로 감쌌습니다.
    """
    app = FastAPI(
        title="Auth Example",
        description="08장 — 회원가입·로그인·보호된 라우트 예제 (JWT + Bcrypt)",
        version="0.1.0",
    )

    # CORS — 프론트엔드가 다른 도메인일 때 브라우저의 차단을 풀어준다.
    # 이 예제는 JWT 를 Authorization 헤더로 주고받으므로 allow_credentials 가 필요 없다.
    # 주의: allow_origins=["*"] 와 allow_credentials=True 는 CORS 규약상 함께 쓸 수 없다.
    #       (쿠키 기반 인증으로 바꾸려면 allow_origins 에 실제 도메인을 명시해야 한다.)
    # 운영에서는 ["*"] 대신 실제 도메인 목록을 명시할 것.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    app.include_router(auth_router.router)
    app.include_router(users_router.router)

    @app.get("/health", tags=["health"], summary="헬스체크")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
