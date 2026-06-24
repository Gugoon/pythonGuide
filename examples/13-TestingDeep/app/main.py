"""테스트 심화 예제용 작은 FastAPI 앱.

이 앱은 "테스트 대상" 으로 일부러 작게 만들었다. DB 도 없이 인메모리 dict 하나만 쓴다.
대신 테스트로 다뤄볼 가치가 있는 세 가지를 갖췄다.

1. `GET /health` — 가장 단순한 엔드포인트.
2. `POST /quotes`, `GET /quotes/{id}` — 검증·에러 케이스가 있는 인메모리 CRUD 의 축소판.
3. `GET /rate/{code}` — **외부 API 를 호출**하는 엔드포인트. 외부 호출은 `app/services.py`
   의 `fetch_rate` 로 격리되어 있어, 테스트에서 monkeypatch 로 가짜 응답으로 바꿔치운다.

`uvicorn app.main:app --reload` 가 이 파일의 `app` 객체를 찾아 실행한다.
"""

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app import services

app = FastAPI(
    title="Testing Deep",
    version="0.1.0",
    description="13장 테스트 작성 심화 예제 — 픽스처, 파라미터화, 에러 케이스, 외부 호출 모킹.",
)


# ---------------------------------------------------------------------------
# 인메모리 저장소
# ---------------------------------------------------------------------------
# DB 대신 프로세스 메모리의 dict 하나로 명언(quote)을 저장한다.
# 학습 목적상 가장 단순한 저장소이며, "상태가 테스트 사이에 새지 않게 비우는 법"
# (conftest 의 reset_store 픽스처)을 보여주기에 딱 좋다.
_quotes: dict[int, "QuoteRead"] = {}
_next_id = 1


def reset_state() -> None:
    """인메모리 저장소를 초기 상태로 되돌린다(테스트 픽스처가 호출)."""
    global _next_id
    _quotes.clear()
    _next_id = 1


# ---------------------------------------------------------------------------
# 스키마
# ---------------------------------------------------------------------------
class QuoteCreate(BaseModel):
    text: str = Field(min_length=1, max_length=280)
    author: str = Field(min_length=1, max_length=100)


class QuoteRead(BaseModel):
    id: int
    text: str
    author: str


class RateRead(BaseModel):
    code: str
    rate: float


# ---------------------------------------------------------------------------
# 의존성: 외부 호출 함수를 "주입" 가능한 모양으로 감싼다
# ---------------------------------------------------------------------------
def get_rate_fetcher():
    """환율 조회 함수를 돌려주는 의존성.

    라우터가 `services.fetch_rate` 를 직접 부르지 않고 이 의존성을 거치게 해 두면,
    테스트에서 `app.dependency_overrides` 로 통째로 바꿔치우는 길도 열린다.
    이 챕터에서는 monkeypatch 방식과 dependency_overrides 방식 둘 다 보여준다.
    """
    return services.fetch_rate


# ---------------------------------------------------------------------------
# 엔드포인트
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/quotes",
    response_model=QuoteRead,
    status_code=status.HTTP_201_CREATED,
    tags=["quotes"],
)
async def create_quote(payload: QuoteCreate) -> QuoteRead:
    global _next_id
    quote = QuoteRead(id=_next_id, text=payload.text, author=payload.author)
    _quotes[_next_id] = quote
    _next_id += 1
    return quote


@app.get("/quotes/{quote_id}", response_model=QuoteRead, tags=["quotes"])
async def get_quote(quote_id: int) -> QuoteRead:
    quote = _quotes.get(quote_id)
    if quote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"명언 {quote_id} 를 찾을 수 없습니다",
        )
    return quote


@app.get("/quotes", response_model=list[QuoteRead], tags=["quotes"])
async def list_quotes() -> list[QuoteRead]:
    return list(_quotes.values())


@app.get("/rate/{code}", response_model=RateRead, tags=["rate"])
async def get_rate(code: str, fetch=Depends(get_rate_fetcher)) -> RateRead:
    """통화 코드의 환율을 외부 API 에서 가져와 돌려준다.

    실제 외부 호출은 `fetch`(기본값 `services.fetch_rate`)가 담당한다.
    외부가 실패하면 `RateUnavailableError` 가 올라오는데, 이를 503 으로 변환한다.
    """
    if not code.isalpha() or not (2 <= len(code) <= 5):
        raise HTTPException(
            status_code=422,
            detail="통화 코드는 2~5자의 알파벳이어야 합니다",
        )
    try:
        rate = await fetch(code)
    except services.RateUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"환율 정보를 가져올 수 없습니다: {exc}",
        ) from exc
    return RateRead(code=code.upper(), rate=rate)
