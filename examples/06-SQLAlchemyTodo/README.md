# 06-SQLAlchemyTodo — FastAPI + SQLAlchemy 2.0 (async) + Alembic

FastAPI 가이드 [06장](../../docs/06-sqlalchemy-database.md)의 예제 프로젝트입니다.
SQLite 위에서 동작하는 가장 단순한 Todo CRUD를 통해 SQLAlchemy 2.0의 비동기 ORM과 Alembic 마이그레이션을 익힙니다.

## 요구사항

- Python 3.13 이상
- [uv](https://docs.astral.sh/uv/) 0.4 이상 (없으면 `pip` + `venv` 로 대체 가능 — 03장 참조)

## 폴더 구조

```
06-SQLAlchemyTodo/
├── pyproject.toml
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── .gitkeep
└── app/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── db.py
    ├── models.py
    └── schemas.py
```

## 빠른 시작

### 1) 의존성 설치

```bash
uv sync
```

> `uv sync` 가 `pyproject.toml` 을 보고 `.venv/` 와 의존성을 자동으로 만들어 줍니다.
> 직접 추가했다면 `uv add fastapi "uvicorn[standard]" sqlalchemy alembic aiosqlite` 와 동일합니다.

### 2) 환경 변수 (선택)

기본값(`sqlite+aiosqlite:///./todo.db`)을 그대로 쓸 거라면 건너뛰어도 됩니다.
다른 DB를 쓰려면 `.env.example` 을 `.env` 로 복사해 수정하고 셸에 export 합니다.

```bash
cp .env.example .env
# 필요한 값을 수정한 뒤
export DATABASE_URL="postgresql+asyncpg://..."
```

### 3) 첫 마이그레이션 만들기 + 적용

```bash
# todos 테이블에 대한 마이그레이션 자동 생성
uv run alembic revision --autogenerate -m "create todos table"

# DB 에 실제로 적용
uv run alembic upgrade head
```

성공하면 프로젝트 루트에 `todo.db` 파일이 생기고, 그 안에 `todos` 테이블이 만들어집니다.

### 4) 서버 실행

```bash
uv run uvicorn app.main:app --reload
```

브라우저에서 자동 문서를 확인:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

### 5) curl 로 CRUD 한 바퀴

```bash
# 헬스 체크
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}

# 새 todo 만들기 (201 Created)
curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"우유 사기"}'

# 목록 조회 (200)
curl -s http://127.0.0.1:8000/todos

# 단건 조회 (200 또는 404)
curl -s http://127.0.0.1:8000/todos/1

# 부분 수정 (200)
curl -s -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done":true}'

# 삭제 (204 No Content)
curl -s -X DELETE http://127.0.0.1:8000/todos/1 -w "%{http_code}\n"
```

## 마이그레이션 명령

```bash
# 모델 변경 후 새 마이그레이션 자동 생성
uv run alembic revision --autogenerate -m "변경 설명"

# 적용 (모든 미적용 마이그레이션을 끝까지)
uv run alembic upgrade head

# 가장 최근 한 단계 되돌림
uv run alembic downgrade -1

# 모든 마이그레이션 되돌림(빈 DB)
uv run alembic downgrade base

# 히스토리 / 현재 적용 위치 확인
uv run alembic history
uv run alembic current
```

## 다른 DB 로 옮기기

코드 변경 없이 환경 변수만 바꾸면 됩니다.

### PostgreSQL

```bash
# 1) 비동기 드라이버 추가
uv add asyncpg

# 2) (선택) Docker 로 PostgreSQL 띄우기
docker run --name fastapi-pg \
  -e POSTGRES_DB=tododb \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass \
  -p 5432:5432 \
  -d postgres:17

# 3) DATABASE_URL 변경
export DATABASE_URL="postgresql+asyncpg://todouser:todopass@localhost:5432/tododb"

# 4) 마이그레이션 적용 + 서버 재시작
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

### MySQL

```bash
uv add asyncmy
export DATABASE_URL="mysql+asyncmy://todouser:todopass@localhost:3306/tododb"
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

## SQLite 파일 직접 살펴보기

```bash
sqlite3 todo.db
sqlite> .tables
alembic_version  todos
sqlite> .schema todos
sqlite> select * from todos;
sqlite> .quit
```

## 라우트 목록

| Method | Path             | 설명                  | 성공 코드 |
|--------|------------------|-----------------------|-----------|
| GET    | `/health`        | 헬스 체크            | 200       |
| POST   | `/todos`         | 새 todo 생성         | 201       |
| GET    | `/todos`         | 전체 목록(최신순)     | 200       |
| GET    | `/todos/{id}`    | 단건 조회            | 200 / 404 |
| PATCH  | `/todos/{id}`    | 부분 수정            | 200 / 404 |
| DELETE | `/todos/{id}`    | 삭제                 | 204 / 404 |

## 자주 만나는 문제

- **`sqlalchemy.exc.OperationalError: no such table: todos`** — 마이그레이션 미적용. `uv run alembic upgrade head`.
- **`alembic revision --autogenerate` 가 빈 파일을 만듦** — `alembic/env.py` 안의 `from app import models` 가 누락되었는지 확인.
- **`RuntimeWarning: coroutine ... was never awaited`** — 비동기 메서드 앞에 `await` 가 빠졌습니다.
- **PostgreSQL 연결 실패 (`password authentication failed`)** — DATABASE_URL 의 사용자/비밀번호가 실제 DB 와 일치하는지 확인.

## 다음 챕터로

[07장 — CRUD 예제, Todo API](../../docs/07-crud-example.md) 에서 이 프로젝트를 라우터 분리 + 페이지네이션 + 테스트로 확장합니다.
