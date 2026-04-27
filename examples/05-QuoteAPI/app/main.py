"""FastAPI 애플리케이션 엔트리 포인트.

`uv run uvicorn app.main:app --reload` 로 띄운다.
"""

from fastapi import FastAPI

from app.routers import quotes

app = FastAPI(
    title="Quote API",
    description="메모리 기반 명언 관리 REST API (FastAPI 가이드 5장 실습)",
    version="0.1.0",
)

app.include_router(quotes.router)


@app.get("/", tags=["root"], summary="헬로 메시지")
def root() -> dict[str, str]:
    """루트 엔드포인트. 배포 직후 살아있는지 확인용으로 자주 씁니다."""
    return {"message": "Hello, Quote API!", "docs": "/docs"}
