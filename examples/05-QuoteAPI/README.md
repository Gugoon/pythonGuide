# 05-QuoteAPI — 메모리 기반 명언 API

FastAPI 가이드 **5장 (라우팅과 Pydantic)** 의 실습 예제입니다. 메모리에 저장되는 명언(Quote) CRUD API를 통해 라우팅·경로/쿼리 매개변수·Pydantic 모델·응답 모델·`HTTPException`·`APIRouter`·테스트를 한 번에 익힙니다.

> 데이터베이스는 사용하지 않습니다 — 모든 자료는 파이썬 `dict`(메모리)에 잠시 들어 있다가 서버를 끄면 사라집니다. DB 연동은 06장에서 다룹니다.

## 프로젝트 구조

```
05-QuoteAPI/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 인스턴스 + 라우터 include
│   ├── schemas.py          # Pydantic 모델 (QuoteBase / Create / Update / Read)
│   └── routers/
│       ├── __init__.py
│       └── quotes.py       # /quotes 라우트들
└── tests/
    ├── __init__.py
    └── test_quotes.py      # TestClient 기반 통합 테스트
```

> `uv sync` 또는 `uv add`를 처음 실행하면 `uv.lock`(의존성 잠금 파일)이 자동으로 생성됩니다. 본 저장소에는 포함하지 않았으므로 위 트리에는 표시하지 않았습니다.

## 사전 준비

- Python 3.13 이상
- [uv](https://docs.astral.sh/uv/) (없다면 `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## 실행

저장소를 받은 직후, 이 폴더 안에서 다음 한 줄로 의존성을 깔고 서버를 띄웁니다.

```bash
uv sync                                   # uv.lock 기준으로 의존성 복원
uv run uvicorn app.main:app --reload      # 개발용 서버
```

성공 로그:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

이제 다음 주소를 열어 봅니다.

- http://127.0.0.1:8000/ — 인사 메시지
- http://127.0.0.1:8000/docs — Swagger UI (인터랙티브 문서)
- http://127.0.0.1:8000/redoc — ReDoc (읽기 좋은 문서)

## 엔드포인트 목록

| 메서드 | 경로 | 설명 | 성공 코드 |
|--------|------|------|----------|
| GET | `/` | 헬로 메시지 | 200 |
| GET | `/quotes/` | 명언 목록 (`limit`, `offset`) | 200 |
| GET | `/quotes/{quote_id}` | 명언 단건 조회 | 200 / 404 |
| POST | `/quotes/` | 명언 생성 | 201 |
| PUT | `/quotes/{quote_id}` | 명언 전체 수정 | 200 / 404 |
| PATCH | `/quotes/{quote_id}` | 명언 부분 수정 | 200 / 404 |
| DELETE | `/quotes/{quote_id}` | 명언 삭제 | 204 / 404 |

## curl로 시나리오 한 번 돌려보기

### 명언 생성 (201 Created)

```bash
curl -X POST http://127.0.0.1:8000/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Stay hungry, stay foolish.","author":"Steve Jobs"}'
```

응답 예시:

```json
{
  "text": "Stay hungry, stay foolish.",
  "author": "Steve Jobs",
  "id": 1,
  "created_at": "2026-04-25T10:30:00.123456+00:00"
}
```

### 목록 조회

```bash
curl http://127.0.0.1:8000/quotes/
curl "http://127.0.0.1:8000/quotes/?limit=5&offset=0"
```

### 단건 조회

```bash
curl http://127.0.0.1:8000/quotes/1
curl http://127.0.0.1:8000/quotes/999     # 404
```

### 부분 수정 (저자만 바꾸기)

```bash
curl -X PATCH http://127.0.0.1:8000/quotes/1 \
  -H "Content-Type: application/json" \
  -d '{"author":"S. Jobs"}'
```

### 검증 실패 — 빈 텍스트는 422

```bash
curl -X POST http://127.0.0.1:8000/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"text":"","author":"Anon"}'
```

### 삭제 (204 No Content)

```bash
curl -X DELETE http://127.0.0.1:8000/quotes/1 -i
```

## 테스트

```bash
uv run pytest -v
```

전체 6개 테스트 케이스가 모두 통과하면 환경 구축이 깔끔하게 끝난 것입니다.

```
tests/test_quotes.py::test_root PASSED
tests/test_quotes.py::test_create_and_list_quote PASSED
tests/test_quotes.py::test_get_quote_not_found PASSED
tests/test_quotes.py::test_create_validation_error_empty_text PASSED
tests/test_quotes.py::test_patch_partial_update PASSED
tests/test_quotes.py::test_delete_then_404 PASSED
```

## 다음 챕터로

이 예제의 메모리 저장소(`_QUOTES`, `_NEXT_ID`)는 **06장에서 SQLAlchemy + SQLite로 자연스럽게 대체**됩니다. 라우트 함수와 Pydantic 모델은 거의 그대로 둔 채 안쪽만 DB 호출로 바뀝니다 — 5장에서 입력·출력·DB 자료를 분리해 둔 보람이 그때 나타납니다.
