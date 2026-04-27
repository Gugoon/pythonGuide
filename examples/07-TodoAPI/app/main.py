"""FastAPI 앱 엔트리 포인트.

`uvicorn app.main:app --reload` 가 이 파일의 `app` 객체를 찾아 실행한다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import todos

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="07장 CRUD 예제 — 라우터 분리, 서비스 레이어, 통합 테스트가 포함된 Todo API.",
)

# CORS 미들웨어. 다른 도메인의 프론트엔드(예: localhost:3000) 가 이 API 를 호출할 때
# 브라우저가 막지 않도록 허용 헤더를 자동으로 붙여준다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    """로드밸런서·모니터링이 부르는 단순 OK 엔드포인트.

    DB 연결까지 점검하고 싶다면 여기서 `SELECT 1` 같은 가벼운 쿼리를 추가할 수 있다.
    """
    return {"status": "ok"}


# 도메인별 라우터 등록. 더 추가될 때마다 한 줄씩 늘어난다.
app.include_router(todos.router)
