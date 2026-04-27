# 07-TodoAPI — FastAPI Todo API 예제

FastAPI 가이드 [07장 CRUD 예제](../../docs/07-crud-example.md)의 완성본입니다. 라우터 분리, 서비스 레이어(`crud.py`), Alembic 마이그레이션, 통합 테스트를 포함한 실전 입문용 Todo API입니다.

## 사용 기술

- Python 3.13
- FastAPI 0.115.x
- Pydantic 2.x + pydantic-settings
- SQLAlchemy 2.0 (async) + Alembic
- aiosqlite (SQLite 비동기 드라이버)
- pytest + httpx (테스트)
- uv (패키지/가상환경 매니저)

## 실행 방법

```bash
# 1) 의존성 설치 (가상환경은 uv가 자동으로 만듭니다)
uv sync

# 2) 환경 변수 파일 준비
cp .env.example .env

# 3) DB 스키마 생성 (Alembic 마이그레이션 적용)
uv run alembic upgrade head

# 4) 서버 실행
uv run uvicorn app.main:app --reload
```

서버가 뜨면 다음 주소에서 확인할 수 있습니다.

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- 헬스 체크: http://127.0.0.1:8000/health

## 테스트 실행

```bash
uv run pytest -v
```

테스트는 메모리 SQLite를 쓰므로 `todo.db` 파일에는 영향이 없습니다.

## 폴더 구조

```
07-TodoAPI/
├── pyproject.toml
├── uv.lock                   (uv sync 후 생성)
├── .python-version
├── .env.example              (.env로 복사해 사용)
├── .gitignore
├── README.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_todos.py
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 앱 + CORS + 라우터 등록 + /health
│   ├── config.py             # pydantic-settings 환경 변수
│   ├── db.py                 # AsyncEngine, get_session 의존성
│   ├── models.py             # SQLAlchemy ORM 모델 (Todo)
│   ├── schemas.py            # Pydantic 스키마 (요청/응답 DTO)
│   ├── crud.py               # 비즈니스 로직 = 서비스 레이어
│   └── routers/
│       ├── __init__.py
│       └── todos.py          # /todos 엔드포인트들
└── tests/
    ├── __init__.py
    ├── conftest.py           # in-memory SQLite + get_session 오버라이드
    └── test_todos.py
```

## 엔드포인트

| 메서드 | 경로 | 설명 | 성공 상태 |
|--------|------|------|-----------|
| `POST` | `/todos` | Todo 생성 | 201 |
| `GET` | `/todos` | 목록 조회 (`skip`, `limit`, `is_done`) | 200 |
| `GET` | `/todos/{todo_id}` | 단건 조회 | 200 |
| `PATCH` | `/todos/{todo_id}` | 부분 수정 | 200 |
| `DELETE` | `/todos/{todo_id}` | 삭제 | 204 |
| `GET` | `/health` | 헬스 체크 | 200 |

## 다음 단계

이 예제는 인증을 다루지 않습니다. 누가 어느 Todo를 만들고 수정·삭제할 수 있는지 결정하는 흐름은 **08장**에서 배웁니다. 사용자별 Todo로 확장한 완성본은 **10장(Note API)**에서 처음부터 다시 만듭니다.
