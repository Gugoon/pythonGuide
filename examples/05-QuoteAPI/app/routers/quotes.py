"""/quotes 라우트 모음.

학습용 메모리 저장소(_QUOTES, _NEXT_ID)를 사용한다. 서버를 끄면 자료가 사라진다.
06장에서 SQLAlchemy + SQLite로 자연스럽게 대체할 예정이다.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import QuoteCreate, QuoteRead, QuoteUpdate

router = APIRouter(prefix="/quotes", tags=["quotes"])

# 메모리 저장소 — 학습용. 서버 재시작 시 사라진다.
_QUOTES: dict[int, QuoteRead] = {}
_NEXT_ID: int = 1


def _now() -> datetime:
    return datetime.now(timezone.utc)


@router.get(
    "/",
    response_model=list[QuoteRead],
    summary="명언 목록",
)
def list_quotes(
    limit: int = Query(default=20, ge=1, le=100, description="한 번에 몇 개를 받을지"),
    offset: int = Query(default=0, ge=0, description="앞에서 몇 개를 건너뛸지"),
) -> list[QuoteRead]:
    """등록된 명언을 생성 시간 순으로 페이징해서 돌려줍니다."""
    items = sorted(_QUOTES.values(), key=lambda q: q.created_at)
    return items[offset : offset + limit]


@router.get(
    "/{quote_id}",
    response_model=QuoteRead,
    summary="명언 단건 조회",
    responses={404: {"description": "명언을 찾을 수 없음"}},
)
def get_quote(quote_id: int) -> QuoteRead:
    """기본 키로 명언 한 개를 조회합니다. 없으면 404."""
    quote = _QUOTES.get(quote_id)
    if quote is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    return quote


@router.post(
    "/",
    response_model=QuoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="명언 생성",
)
def create_quote(payload: QuoteCreate) -> QuoteRead:
    """새 명언을 만듭니다. 생성된 객체를 그대로 돌려줍니다."""
    global _NEXT_ID
    quote = QuoteRead(
        id=_NEXT_ID,
        text=payload.text,
        author=payload.author,
        created_at=_now(),
    )
    _QUOTES[quote.id] = quote
    _NEXT_ID += 1
    return quote


@router.put(
    "/{quote_id}",
    response_model=QuoteRead,
    summary="명언 전체 수정",
    responses={404: {"description": "명언을 찾을 수 없음"}},
)
def replace_quote(quote_id: int, payload: QuoteCreate) -> QuoteRead:
    """PUT은 전체 덮어쓰기 — 들어온 본문 그대로 반영합니다.

    생성 시간(`created_at`)은 그대로 유지합니다.
    """
    if quote_id not in _QUOTES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    existing = _QUOTES[quote_id]
    updated = QuoteRead(
        id=quote_id,
        text=payload.text,
        author=payload.author,
        created_at=existing.created_at,
    )
    _QUOTES[quote_id] = updated
    return updated


@router.patch(
    "/{quote_id}",
    response_model=QuoteRead,
    summary="명언 부분 수정",
    responses={404: {"description": "명언을 찾을 수 없음"}},
)
def update_quote(quote_id: int, payload: QuoteUpdate) -> QuoteRead:
    """PATCH는 일부만 갱신 — 사용자가 보낸 필드만 바꿉니다."""
    existing = _QUOTES.get(quote_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    data = existing.model_dump()
    # exclude_unset=True: 사용자가 실제로 보낸 필드만 추린다.
    patch = payload.model_dump(exclude_unset=True)
    data.update(patch)
    updated = QuoteRead(**data)
    _QUOTES[quote_id] = updated
    return updated


@router.delete(
    "/{quote_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="명언 삭제",
    responses={404: {"description": "명언을 찾을 수 없음"}},
)
def delete_quote(quote_id: int) -> None:
    """명언 한 개를 지웁니다. 성공 시 204(본문 없음)."""
    if quote_id not in _QUOTES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    del _QUOTES[quote_id]
    return None
