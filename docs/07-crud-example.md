# 07. CRUD 예제 — Todo API

> **이 챕터의 목표**
> - 06장에서 익힌 SQLAlchemy 흐름을 한 단계 끌어올려, **라우터 분리·서비스 레이어·통합 테스트**가 갖춰진 작은 실전 API 를 처음부터 끝까지 만든다.
> - `APIRouter` 로 도메인별 엔드포인트를 묶고, `crud.py` 로 비즈니스 로직을 분리하는 표준 구조를 손에 익힌다.
> - HTTP 상태 코드(201 / 204 / 404)와 부분 수정(PATCH) 의 표준 패턴, `model_dump(exclude_unset=True)` 의 활용을 익힌다.
> - `pytest` + `httpx.AsyncClient` + 의존성 오버라이드로 통합 테스트 8~10개를 작성하고, `uv run pytest` 한 줄로 자동 실행한다.
> - Alembic 으로 첫 마이그레이션 파일을 생성·적용하는 흐름을 마무리한다.

> **소요 시간**: 3~5시간

> **전제**: 03~06장을 읽었다. 가상환경(`uv sync`), FastAPI 한 줄 라우트(`@app.get`), Pydantic 스키마, SQLAlchemy 비동기 세션, Alembic 의 존재를 한 번씩 만나봤다.

> **인증은 다루지 않는다**. 로그인·토큰·"이건 내 글이야" 같은 권한 검사는 다음 08장에서 본격적으로 배우고, 인증을 결합한 완성본은 10장(Note API)에서 만든다. 이번 장은 **CRUD 그 자체와 코드 구조에 집중**한다.

---

## 7.1 06장에서 만든 흐름 짧게 복습

06장에서 우리가 익힌 것을 한 문단으로 정리하면 다음과 같다.

- **`AsyncEngine`** 하나를 앱 전체에서 공유한다. 이게 곧 "DB 와 통신하는 입구"다.
- **`async_sessionmaker`** 로 매 요청마다 세션을 한 번씩 꺼낸다. 세션이 곧 한 묶음의 트랜잭션이다.
- **`DeclarativeBase`** 를 상속한 클래스가 한 테이블이 된다. `Mapped[...]` 와 `mapped_column(...)` 으로 컬럼을 적는다.
- **Pydantic 스키마**(`BaseModel`)와 **ORM 모델**(`Base` 의 자식)은 별개다. 둘을 잇기 위해 응답 스키마에 `from_attributes=True` 를 켠다.
- **`Depends(get_session)`** 로 라우터에 세션을 주입받는다.

> **세션이란?** ORM 이 한 묶음의 DB 작업을 처리하는 단위다. 한 요청 안에서 세션 하나를 만들고, 끝날 때 닫는다. 트랜잭션도 이 세션이 자동으로 관리한다. (인증의 "세션"과는 단어만 같고 의미는 다르다.)

> **트랜잭션이란?** "여러 SQL 을 한 묶음으로 실행하고, 도중에 실패하면 모두 되돌린다" 는 단위다. SQLAlchemy 세션은 기본적으로 한 묶음을 트랜잭션으로 다룬다. `commit()` 으로 확정하고, 예외가 나면 `rollback()` 한다.

06장은 한 파일(`main.py`) 안에 라우트와 DB 작업이 같이 살았다. 이번 장은 그 모든 것을 **여러 파일로 나누고**, **테스트까지 붙여서** 작은 실전 API 의 모양을 만든다.

---

## 7.2 큰 그림 — 무엇을 만들 것인가

만들 것은 **할 일 목록 API(Todo API)** 다. 기능 요구사항은 다음 정도로 잡는다.

- Todo 한 건을 만든다(POST).
- 목록을 페이지 단위로 가져온다(GET, 페이지네이션 지원).
- 단건 조회(GET).
- 부분 수정(PATCH) — 보낸 필드만 바꾼다.
- 삭제(DELETE).
- 헬스 체크(`GET /health`) 한 줄.

엔드포인트 표:

| 메서드 | 경로 | 설명 | 성공 상태 |
|--------|------|------|-----------|
| `POST` | `/todos` | 생성 | 201 Created |
| `GET` | `/todos` | 목록(skip / limit / is_done 필터) | 200 OK |
| `GET` | `/todos/{todo_id}` | 단건 조회 | 200 OK |
| `PATCH` | `/todos/{todo_id}` | 부분 수정 | 200 OK |
| `DELETE` | `/todos/{todo_id}` | 삭제 | 204 No Content |
| `GET` | `/health` | 헬스 체크 | 200 OK |

이 챕터에서 새롭게 익힐 것은 다음 다섯 가지다.

1. **라우터 분리** — 엔드포인트를 `app/routers/todos.py` 로 옮긴다.
2. **서비스 레이어** — 모든 DB 작업을 `app/crud.py` 한 모듈에 모은다.
3. **응답 모델 분리** — ORM 모델과 API 응답 스키마를 분리하고, `from_attributes=True` 로 잇는다.
4. **HTTP 상태 코드 일관성** — 201 / 204 / 404 / 422 가 어디에서 어떻게 나오는지를 손에 익힌다.
5. **통합 테스트** — `pytest` + `httpx.AsyncClient` + 의존성 오버라이드 패턴.

> **통합 테스트(integration test)란?** 한 함수만 따로 부르는 단위 테스트와 달리, **앱을 통째로 띄우고 HTTP 요청을 보내본 뒤** 응답이 기대대로 나오는지 확인하는 테스트다. FastAPI 는 이 테스트가 매우 짧고 가볍게 작성된다.

---

## 7.3 패키지 구조 한 그림

이 챕터의 결과물 폴더는 다음과 같다. 처음 보면 파일이 좀 많아 보이지만, **각 파일이 정확히 한 가지 일만 한다**는 걸 따라가면 어렵지 않다.

```
07-TodoAPI/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
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
│   ├── main.py            ← FastAPI 앱 + CORS + /health + 라우터 include
│   ├── config.py          ← 환경 변수 (pydantic-settings)
│   ├── db.py              ← 엔진 + 세션 팩토리 + get_session 의존성
│   ├── models.py          ← SQLAlchemy ORM 모델 (Todo)
│   ├── schemas.py         ← Pydantic 스키마 (요청/응답 DTO)
│   ├── crud.py            ← 비즈니스 로직 = 서비스 레이어
│   └── routers/
│       ├── __init__.py
│       └── todos.py       ← /todos 엔드포인트들
└── tests/
    ├── __init__.py
    ├── conftest.py        ← in-memory SQLite + 의존성 오버라이드
    └── test_todos.py
```

각 파일의 한 줄 정의:

| 파일 | 책임 한 줄 |
|------|------------|
| `app/main.py` | FastAPI 앱 인스턴스를 만들고, 미들웨어와 라우터를 등록한다 |
| `app/config.py` | 환경 변수(`.env`) 를 읽어 설정 객체로 만든다 |
| `app/db.py` | 엔진·세션·`Base`·`get_session` 의존성을 모두 모아둔다 |
| `app/models.py` | DB 표를 표현하는 ORM 클래스만 둔다 |
| `app/schemas.py` | 요청/응답 형태를 결정하는 Pydantic 스키마만 둔다 |
| `app/crud.py` | 모든 DB 작업(create/get/list/update/delete)을 함수로 모은다 |
| `app/routers/todos.py` | `/todos` 엔드포인트의 HTTP 처리. crud 를 호출만 한다 |
| `tests/conftest.py` | 테스트용 메모리 DB 와 클라이언트 fixture 를 정의한다 |
| `tests/test_todos.py` | 라우터의 정상/에러 케이스를 통합 테스트한다 |

이 표가 곧 우리의 **작업 순서**이기도 하다. 위에서 아래로 내려가며 한 파일씩 만든다.

---

## 7.4 프로젝트 만들기

### 7.4.1 폴더 만들기

```bash
mkdir 07-TodoAPI
cd 07-TodoAPI
```

### 7.4.2 uv 로 초기화하고 의존성 추가

```bash
uv init --bare                # 샘플 코드 없이 pyproject.toml 만 만든다
rm -f hello.py main.py        # 혹시 남아 있는 샘플 스크립트 정리

uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite
uv add pydantic-settings
uv add --dev pytest pytest-asyncio httpx

# 패키지 마커 빈 파일들을 만들어 둔다
# (테스트 디스커버리·import 안정성을 위해 명시적으로 두는 것을 권장)
mkdir -p app/routers tests
touch app/__init__.py app/routers/__init__.py tests/__init__.py
```

설치가 끝나면 폴더에 다음이 생긴다.

- `pyproject.toml` — 의존성 목록과 메타데이터
- `uv.lock` — 라이브러리들의 정확한 버전을 못 박은 잠금 파일
- `.venv/` — 가상환경 폴더 (`.gitignore` 에 등록)
- `.python-version` — Python 버전(3.13) 표시 파일

> **`pydantic-settings` 가 왜 따로 있나?** Pydantic 2 부터 환경 변수를 다루는 `BaseSettings` 가 별도 패키지(`pydantic-settings`)로 분리됐다. 핵심 검증 기능만 쓰는 사람이 더 가벼운 의존성으로 쓸 수 있게 하기 위함이다. 우리는 환경 변수를 다룰 거라 같이 깐다.

> **`pytest-asyncio` 는 뭔가요?** `pytest` 자체는 동기 테스트만 안다. `async def test_...` 모양의 비동기 테스트 함수를 자연스럽게 돌리려면 이 플러그인이 필요하다. `asyncio_mode = "auto"` 옵션을 켜두면 모든 `async def` 테스트가 자동으로 감지된다.

### 7.4.3 표준 명령 정리

이번 장에서 자주 쓸 명령들을 미리 정리해 둔다.

| 작업 | 명령 |
|------|------|
| 의존성 설치/동기화 | `uv sync` |
| 새 라이브러리 추가 | `uv add <이름>` |
| 개발용 라이브러리 추가 | `uv add --dev <이름>` |
| 서버 실행 | `uv run uvicorn app.main:app --reload` |
| 마이그레이션 생성 | `uv run alembic revision --autogenerate -m "..."` |
| 마이그레이션 적용 | `uv run alembic upgrade head` |
| 테스트 실행 | `uv run pytest` |

> **`uv run` 이 뭔가요?** "이 프로젝트의 가상환경 안에서 명령을 실행해 줘" 라는 접두사다. `source .venv/bin/activate` 를 매번 치는 대신 `uv run <명령>` 으로 같은 효과를 본다. 03장에서 처음 등장했고, 이 가이드의 표준이다.

### 7.4.4 `.python-version`, `.gitignore`, `.env.example`

`uv init` 이 `.python-version` 은 보통 자동으로 만들어 준다. `.gitignore` 와 `.env.example` 은 직접 만들자.

`.gitignore` 핵심 줄들:

```gitignore
__pycache__/
*.py[cod]
.venv/
.env
*.db
*.sqlite
*.sqlite3
.pytest_cache/
.ruff_cache/
.DS_Store
```

`.env.example`:

```dotenv
DATABASE_URL=sqlite+aiosqlite:///./todo.db
CORS_ALLOW_ORIGINS=*
APP_NAME=Todo API
```

> **왜 `.env` 가 아니라 `.env.example` 을 git 에 두는가?** 실제 비밀값(DB 비밀번호, JWT 시크릿)은 절대 git 에 올리면 안 된다. 그래서 진짜 값을 담는 `.env` 는 `.gitignore` 에 등록해 두고, **변수 이름과 의미만 기록한 `.env.example` 을 협업의 가이드로 둔다**. 새 팀원은 이 파일을 복사해 자기 환경에 맞춰 채운다.

---

## 7.5 `app/config.py` — 환경 변수를 한 객체로 모으기

설정값을 가장 먼저 만든다. 다른 모듈이 `from app.config import settings` 로 가져다 쓸 단일 진입점이다.

```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Todo API"
    database_url: str = "sqlite+aiosqlite:///./todo.db"
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.cors_allow_origins.strip()
        if raw == "" or raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


settings = Settings()
```

세 가지 포인트만 짚자.

1. **클래스 속성 = 환경 변수 이름** : `database_url` 이라고 적으면 `DATABASE_URL`(또는 `database_url`) 이라는 환경 변수를 찾는다. `case_sensitive=False` 로 대소문자 무시.
2. **기본값** : 환경 변수가 없으면 코드에 적힌 기본값이 쓰인다. 학습용 SQLite 가 기본이라 `.env` 가 없어도 곧장 돌아간다.
3. **모듈 끝의 `settings = Settings()`** : 한 번만 인스턴스화. 다른 모듈은 이 인스턴스를 공유한다.

> **왜 환경 변수로 설정을 빼는가?** "코드는 한 번 쓰지만 환경(개발 / 테스트 / 운영) 은 여러 개" 이기 때문이다. 같은 코드가 환경마다 다른 DB 를 봐야 한다. 환경 변수로 빼두면 코드를 안 고치고 환경만 바꿔치울 수 있다. 12-Factor App 의 기본 원칙이기도 하다.

---

## 7.6 `app/db.py` — 엔진, 세션, `Base`, `get_session`

```python
# app/db.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """모든 ORM 모델이 상속하는 베이스."""


engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
)

SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

핵심만 다시 짚는다.

- **`Base` 는 단 하나만 둔다.** 다른 모델 모듈이 모두 이 `Base` 를 import 해 상속한다. 그래야 Alembic 이 "어떤 표가 있어야 하는지" 를 한 군데서 본다.
- **`engine` 도 단 하나만 만든다.** 엔진은 내부에 커넥션 풀을 들고 있는 비싼 객체라 매번 새로 만들면 안 된다. 모듈 로드 시 한 번이면 충분하다.
- **`expire_on_commit=False`** : 이걸 안 끄면 `commit()` 후에 객체의 속성에 접근할 때마다 SQL 이 다시 나간다. 비동기 컨텍스트에서 응답 직렬화 도중 에러를 낼 수 있어, 학습용으로는 끄는 쪽이 안전하다.
- **`get_session` 은 async generator** : `yield` 한 번. 라우터 함수가 끝나면 `async with` 블록을 빠져나오며 자동으로 close 된다. 도중에 예외가 나면 `rollback()` 을 한 번 해 준다.

> **`get_session` 이 의존성으로 어떻게 동작하나?** FastAPI 는 `Depends(get_session)` 을 만나면 이 함수를 부른다. `yield` 까지 진행해서 그 결과(`session`)를 라우터에 넘기고, 라우터가 끝나면 다시 이 함수의 `yield` 다음 줄로 돌아온다. 이 패턴 덕분에 "열고 → 쓰고 → 닫는다" 를 한 함수로 깔끔하게 표현할 수 있다.

---

## 7.7 `app/models.py` — Todo 한 표만

```python
# app/models.py
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    is_done: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        server_default=text("0"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

여기서 짚을 점:

- **컬럼 길이** : `String(200)`, `String(2000)` 처럼 명시한다. SQLite 는 길이를 강제하지 않지만, 운영 DB(MySQL/Postgres) 와 호환되려면 처음부터 적어 두는 게 좋다.
- **`is_done` 의 `default=False` + `server_default=text("0")`** : 두 가지를 함께 둔다. `default=False` 는 ORM 이 INSERT 직전에 채우는 Python 측 기본값, `server_default` 는 DB 측 기본값(직접 SQL 로 INSERT 해도 안전). 두 개를 함께 두면 `autogenerate` 가 마이그레이션과 모델 사이의 drift 를 잡지 않는다.
- **`server_default=func.now()`** : "INSERT 할 때 DB 가 알아서 현재 시각을 넣는다." 클라이언트가 보내지 않아도 채워지므로, Pydantic 응답 스키마에서는 이 두 필드를 안전하게 필수로 둘 수 있다.
- **`onupdate=func.now()`** : "UPDATE 할 때마다 갱신". `updated_at` 의 단골 패턴이다.

> **데이터 모델은 일부러 단순하게 둔다.** 이번 장은 "구조" 가 주제라서 모델 자체는 단순한 한 표로 둔다. 외래 키·관계는 11장(Blog API)에서 본격 다룬다.

---

## 7.8 `app/schemas.py` — 요청/응답 스키마

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_done: bool = False


class TodoCreate(TodoBase):
    """POST /todos 요청 본문."""


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 요청 본문. 모든 필드 Optional."""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_done: bool | None = None


class TodoRead(TodoBase):
    """API 응답에 쓰이는 스키마. ORM 인스턴스를 그대로 받을 수 있다."""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodosPage(BaseModel):
    items: list[TodoRead]
    total: int
    skip: int
    limit: int
```

이 작은 모듈에 이 챕터의 **두 가지 핵심 패턴**이 들어 있다.

### 7.8.1 ORM 모델과 응답 스키마의 분리

**왜 따로 두나?** 표는 시간이 지나면서 컬럼이 늘거나 이름이 바뀐다. API 의 응답 모양은 그것과 따로 진화해야 한다. 둘을 같은 클래스로 두면 이런 문제가 잘 일어난다.

- DB 에 새 컬럼(예: `internal_score`) 이 생겼을 뿐인데 **자동으로 클라이언트 응답에 포함**되어 버린다. 의도하지 않은 노출.
- DB 컬럼 이름은 `is_done` 인데, 외부에서는 `done` 으로 바꾸고 싶을 때 한 클래스 안에서 충돌이 난다.
- 응답 전용 가공 필드(예: 합계, 라벨) 를 모델에 끼워 넣다가 ORM 이 그 필드를 또 DB 컬럼으로 만들어 버린다.

규칙은 단순하다. **ORM 모델은 DB 표 그대로**. **외부 응답은 따로 만든 Pydantic 스키마**.

### 7.8.2 `from_attributes=True` 의 역할

기본적으로 Pydantic 모델은 **dict 같이 생긴 입력**을 받아 검증한다. 그런데 라우터에서는 ORM 인스턴스(클래스 인스턴스, 속성 접근으로 값을 꺼내는 객체)를 직접 응답으로 내보내고 싶을 때가 많다.

`model_config = ConfigDict(from_attributes=True)` 를 켜면 Pydantic 이 이렇게 동작한다.

- `TodoRead.model_validate(todo_orm)` 처럼 ORM 객체를 통째로 넘겨도, 알아서 `.id`, `.title`, ... 속성을 읽어 들인다.
- `response_model=TodoRead` 로 라우터에 적어두면, 라우터가 ORM 객체를 그대로 리턴해도 FastAPI 가 같은 변환을 자동으로 한다.

> **옛 Pydantic v1 의 `orm_mode=True`** 와 같은 역할이다. v2 부터 이름이 `from_attributes` 로 바뀌었다.

### 7.8.3 부분 수정용 `TodoUpdate` 의 형태

`TodoUpdate` 의 모든 필드는 Optional 이고 기본값이 None 이다. 이렇게 두면 클라이언트가 **바꾸고 싶은 필드만 보낼 수 있다**.

- `PATCH /todos/1` 의 본문 `{"title": "수정"}` → title 만 갱신.
- 본문 `{"is_done": true}` → is_done 만 true 로.
- 본문 `{}` → 아무 것도 갱신하지 않음(에러도 아님).

> **PUT 과 PATCH 의 차이** : PUT 은 "그 자원을 통째로 이 모양으로 덮어써라" 라는 의미라서 본문에 모든 필드가 와야 정석이다. PATCH 는 "보낸 부분만 바꿔라" 라서 일부 필드만 와도 된다. REST 의 약속이며, 이 챕터는 PATCH 쪽을 쓴다.

---

## 7.9 `app/crud.py` — 서비스 레이어

이 챕터의 **가장 중요한 한 절**이다. 라우터와 DB 작업을 분리하는 곳.

```python
# app/crud.py
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


async def create_todo(session: AsyncSession, payload: TodoCreate) -> Todo:
    todo = Todo(
        title=payload.title,
        description=payload.description,
        is_done=payload.is_done,
    )
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


async def get_todo(session: AsyncSession, todo_id: int) -> Todo | None:
    return await session.get(Todo, todo_id)


async def list_todos(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
    is_done: bool | None = None,
) -> tuple[Sequence[Todo], int]:
    base = select(Todo)
    if is_done is not None:
        base = base.where(Todo.is_done == is_done)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    page_stmt = base.order_by(Todo.created_at.desc()).offset(skip).limit(limit)
    items = (await session.execute(page_stmt)).scalars().all()

    return items, int(total)


async def update_todo(session: AsyncSession, todo: Todo, payload: TodoUpdate) -> Todo:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(todo, key, value)
    await session.commit()
    await session.refresh(todo)
    return todo


async def delete_todo(session: AsyncSession, todo: Todo) -> None:
    await session.delete(todo)
    await session.commit()
```

### 7.9.1 왜 라우터에서 DB 코드를 분리하는가

큰 그림은 단 한 줄로 표현된다.

> **라우터는 HTTP 만, crud 는 DB 만.**

이렇게 분리하면 다음을 얻는다.

1. **재사용** — 같은 비즈니스 로직을 다른 진입점에서 부를 수 있다. 예를 들어 CLI 에서 "지금 미완료 100개 가져와 보고서 만들기" 같은 백그라운드 작업이 필요해지면, `list_todos(...)` 를 그대로 import 해 쓰면 된다. 라우터를 흉내 낼 필요가 없다.
2. **테스트 단순화** — crud 함수 자체를 테스트할 수도, 라우터를 테스트할 때 crud 만 모킹할 수도 있다.
3. **가독성** — 라우터 한 함수가 길어지지 않는다. 라우터를 읽으면 "어떤 HTTP 동작인지" 가 한눈에 보이고, 자세한 SQL 은 `crud.py` 에 모여 있다.
4. **트랜잭션 경계가 명확** — commit / rollback 이 모두 crud 함수 안에서 일어난다. 라우터는 그 결과만 받는다.

> **이 분리는 어디까지 강제되는가?** 강제는 없다. FastAPI 가 정해주는 규칙이 아니라 우리가 선택한 약속이다. 다만 한 번 이렇게 살아 본 사람은, 다음 프로젝트에서도 자연스럽게 이 모양으로 돌아오게 된다. 코드가 자라는 방향이 좋아지기 때문이다.

### 7.9.2 `model_dump(exclude_unset=True)` 의 비밀

부분 수정의 표준 패턴이다.

```python
data = payload.model_dump(exclude_unset=True)
for key, value in data.items():
    setattr(todo, key, value)
```

여기서 `exclude_unset=True` 는 "**클라이언트가 명시적으로 보낸 필드만** dict 로 변환" 한다는 뜻이다. 보내지 않은 필드는 dict 에서 빠진다.

- 클라이언트 본문 `{"title": "X"}` → `data = {"title": "X"}` → title 만 setattr.
- 클라이언트 본문 `{"is_done": true}` → `data = {"is_done": true}` → is_done 만.
- 클라이언트 본문 `{}` → `data = {}` → for 루프가 한 바퀴도 안 돌고 끝. 그대로.

이 한 줄이 PATCH 의 본질을 그대로 표현한다. **default 값과 명시적 None 값을 구분**하기 때문에 가능한 일이다.

> **`exclude_none` 이 아닌 이유** : `exclude_none=True` 로 두면 클라이언트가 일부러 `null` 을 보내 "이 필드를 None 으로 만들고 싶어" 라고 한 의도까지 함께 사라진다. 부분 수정의 의미가 어긋난다. 우리가 원하는 건 "보냈냐 안 보냈냐" 의 구분이지, "값이 None 이냐 아니냐" 가 아니다.

### 7.9.3 페이지네이션 패턴

목록 조회는 두 개의 쿼리로 나눠 만든다.

1. `count_stmt` — 필터를 적용한 **전체 개수**.
2. `page_stmt` — 같은 필터 + 정렬 + offset/limit 을 적용한 **현재 페이지**.

총 개수를 함께 돌려주는 이유는 클라이언트가 **페이지 수**(`ceil(total / limit)`) 와 **다음 페이지 유무** 를 직접 계산할 수 있게 하기 위해서다.

> **skip 과 limit 이 뭔가?** "skip = 앞에서 몇 개를 건너뛸지", "limit = 그 다음 몇 개를 가져올지" 라는 SQL 의 표준 인자다. `skip=0, limit=20` 이면 첫 20개. `skip=20, limit=20` 이면 21~40번. 다른 프레임워크의 "page=1, per=10" 식 표기를 좋아한다면, `skip = (page-1)*per` 로 변환만 하면 된다.

> **OFFSET 페이지네이션의 한계** : 데이터가 매우 많아지면 OFFSET 이 비싸진다. 운영에서는 "커서 기반 페이지네이션"(`?after=<id>` 식) 이 더 빠를 수 있다. 학습 단계와 대부분의 실무에서는 OFFSET 으로 충분하다.

---

## 7.10 `app/routers/todos.py` — 엔드포인트 묶음

`APIRouter` 가 등장하는 곳이다.

```python
# app/routers/todos.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.schemas import TodoCreate, TodoRead, TodosPage, TodoUpdate

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED)
async def create_todo_endpoint(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    todo = await crud.create_todo(session, payload)
    return TodoRead.model_validate(todo)


@router.get("", response_model=TodosPage)
async def list_todos_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_done: bool | None = Query(None),
    session: AsyncSession = Depends(get_session),
) -> TodosPage:
    items, total = await crud.list_todos(
        session, skip=skip, limit=limit, is_done=is_done
    )
    return TodosPage(
        items=[TodoRead.model_validate(t) for t in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo_endpoint(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    return TodoRead.model_validate(todo)


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo_endpoint(
    todo_id: int,
    payload: TodoUpdate,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    updated = await crud.update_todo(session, todo, payload)
    return TodoRead.model_validate(updated)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_endpoint(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    await crud.delete_todo(session, todo)
```

### 7.10.1 `APIRouter` 가 뭔가요

지금까지 우리는 `@app.get("/...")` 식으로 메인 `app` 에 직접 라우트를 붙였다. 도메인이 늘어나면 이 방식은 빠르게 무너진다. `APIRouter` 는 **여러 라우트를 한 묶음의 모듈로 분리**할 수 있게 해 준다.

```python
router = APIRouter(prefix="/todos", tags=["todos"])
```

- `prefix="/todos"` — 이 라우터에 등록되는 모든 경로 앞에 자동으로 `/todos` 가 붙는다. 그래서 라우터 안에서는 `@router.post("")` 라고 빈 문자열을 쓰면 실제 경로는 `/todos` 가 된다. `@router.get("/{todo_id}")` 는 `/todos/{todo_id}` 가 된다.
- `tags=["todos"]` — `/docs` 의 그룹 라벨. 도메인이 여러 개면 라벨로 묶여서 보기 편하다.

`app.include_router(router)` 한 줄로 메인 앱에 합쳐진다(7.11 에서 한다).

> **여러 도메인이 생기면** : `app/routers/users.py`, `app/routers/posts.py` 같이 파일을 늘리고, `main.py` 에서 한 줄씩 include 한다. 11장 Blog API 에서 그 모양으로 자란다.

### 7.10.2 `Depends(get_session)` 의 흐름

라우터 함수의 시그니처를 다시 보자.

```python
async def create_todo_endpoint(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
```

세 가지가 일어난다.

1. **`payload: TodoCreate`** — FastAPI 가 들어온 JSON 바디를 `TodoCreate` 로 변환·검증한다. 검증 실패면 자동 422.
2. **`session: AsyncSession = Depends(get_session)`** — `get_session` 을 부르고, 그 결과를 `session` 인자로 주입한다.
3. **반환 타입 + `response_model=TodoRead`** — FastAPI 가 함수 반환값을 `TodoRead` 로 직렬화한다.

이 한 줄짜리 의존성 주입이 매우 중요하다. **테스트할 때 `get_session` 만 다른 함수로 갈아치우면**, 진짜 DB 대신 메모리 DB 를 쓸 수 있다(7.13 절에서 한다).

### 7.10.3 HTTP 상태 코드를 일관되게

각 라우트에 명시한 status_code 를 정리하면 다음 표가 된다.

| 라우트 | 성공 | 자원 없음 | 검증 실패 |
|--------|------|-----------|-----------|
| `POST /todos` | 201 Created | — | 422 |
| `GET /todos` | 200 OK | — | 422 (잘못된 limit 등) |
| `GET /todos/{id}` | 200 OK | 404 | — |
| `PATCH /todos/{id}` | 200 OK | 404 | 422 |
| `DELETE /todos/{id}` | 204 No Content | 404 | — |

규칙:

- **POST 의 성공은 201**. "새 자원이 만들어졌다" 는 의미를 명확히 한다.
- **DELETE 의 성공은 204**. 본문이 없다는 의미. 라우터 함수가 `None` 을 리턴하면 FastAPI 가 알아서 빈 응답으로 만든다.
- **자원이 없으면 404**. `HTTPException(status_code=404, detail=...)` 한 줄.
- **검증 실패는 422**. Pydantic 이 자동으로 만든다.

> **409 Conflict 는 언제?** "이미 존재해서 만들 수 없다" 같은 충돌에 쓴다. 예를 들어 사용자 이메일 중복 가입을 막을 때 `raise HTTPException(409, ...)`. 이번 Todo 모델에는 unique 제약이 없어서 등장하지 않지만, 08장 인증에서 다시 만난다.

### 7.10.4 `HTTPException` 으로 에러를 일관 처리

FastAPI 에서 에러를 표현하는 표준 방식은 `HTTPException` 이다.

```python
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail=f"Todo {todo_id} 를 찾을 수 없습니다",
)
```

- **`status_code`** — HTTP 응답 코드 정수.
- **`detail`** — 응답 본문에 들어갈 메시지. 자동으로 `{"detail": "..."}` JSON 으로 직렬화된다.

이 패턴을 일관되게 쓰면 `/docs` 에서도 가능한 응답 코드가 자동으로 표시되고, 클라이언트가 동일한 형태로 에러를 처리할 수 있다.

> **try/except 로 직접 응답을 만들면 안 되나요?** 가능은 하지만, FastAPI 의 자동 문서화 / 미들웨어 / 예외 핸들러와 잘 어울리지 않는다. **에러 = `HTTPException` 을 raise** 가 표준이다.

### 7.10.5 `Query(...)` 의 자동 검증

```python
limit: int = Query(20, ge=1, le=100),
```

이 한 줄이 무얼 보장하는가?

- 기본값은 20.
- 1 미만(`ge=1`) 이면 자동 422.
- 100 초과(`le=100`) 면 자동 422.
- `/docs` 에 이 제약이 그대로 표시된다.

별도 검증 코드를 쓰지 않아도 된다. 이런 식으로 **Pydantic 의 검증 능력을 쿼리/경로 파라미터에까지** 확장하는 게 FastAPI 의 큰 장점이다.

---

## 7.11 `app/main.py` — 앱 만들기와 라우터 등록

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import todos

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="07장 CRUD 예제 — 라우터 분리, 서비스 레이어, 통합 테스트가 포함된 Todo API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(todos.router)
```

세 줄짜리 정리:

- **`FastAPI(title=..., version=...)`** — 메타데이터. `/docs` 에 그대로 표시된다.
- **`add_middleware(CORSMiddleware, ...)`** — 다른 도메인의 프론트엔드가 이 API 를 부를 때 브라우저가 막지 않도록 허용 헤더를 자동으로 붙여주는 미들웨어. 한 줄로 끝난다.
- **`include_router(todos.router)`** — `/todos` 엔드포인트들이 이 시점에 앱에 등록된다.

### 7.11.1 헬스 체크는 왜 만드는가

```python
@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
```

운영 환경의 로드밸런서·오케스트레이터(쿠버네티스, ECS 등)는 주기적으로 "이 앱이 살아 있나?" 를 확인하기 위해 단순 HTTP 호출을 한다. 답이 200 이면 "살아 있다" 로 본다.

- 보통 `/health`, `/healthz`, `/ping` 등의 경로를 쓴다.
- 본문은 가벼운 JSON 으로 충분.
- 더 보수적으로는 DB 연결까지 점검하는 `/ready` 를 따로 두기도 한다.

> **개발 단계에서도 만드나요?** 만들어 두는 게 편하다. 배포 후 트러블슈팅의 첫 단추가 보통 "/health 가 200 을 돌려주나?" 이기 때문에, 처음부터 한 줄을 박아두면 나중에 손이 줄어든다.

### 7.11.2 CORSMiddleware 한 줄

CORS 는 **브라우저 안전 장치** 다. 그래서 백엔드만 잘 동작하면 끝나는 게 아니라, "이 도메인에서 요청이 와도 괜찮다" 고 백엔드가 응답 헤더로 알려줘야 한다. FastAPI 의 `CORSMiddleware` 가 그 헤더를 자동으로 붙여 준다.

- `allow_origins` — 허용 도메인 리스트. 개발에서는 `["*"]` 가 편하지만, 운영에서는 명시적으로 적는 게 좋다.
- `allow_methods=["*"]` — 모든 HTTP 메서드 허용.
- `allow_headers=["*"]` — 클라이언트가 보낼 수 있는 헤더 모두 허용.

> **`allow_credentials=True` 와 `allow_origins=["*"]` 는 동시에 쓰면 안 된다는 말이 있던데?** 정확하다. 자격 증명(쿠키·인증 헤더) 을 보낼 때는 `*` 가 아니라 명시적인 도메인을 적어야 브라우저가 받아준다. 학습 단계에서 인증을 안 쓰는 동안은 큰 문제가 없지만, 08장 이후에는 운영용 도메인을 명시적으로 적는 쪽으로 바꾸자.

---

## 7.12 Alembic 마이그레이션

이제 DB 표를 만들 차례다. 06장에서 한 번 다뤘다면 빠르게 복습이고, 처음이라면 절차가 더 또렷해진다.

### 7.12.1 alembic 초기화

```bash
uv run alembic init alembic
```

이 명령은 현재 폴더에 다음을 만든다.

- `alembic.ini` — Alembic 의 메인 설정 파일.
- `alembic/` 폴더와 그 안에 `env.py`, `script.py.mako`, `versions/` 폴더.

### 7.12.2 `alembic.ini` 손보기

`alembic.ini` 의 `sqlalchemy.url` 을 우리 DB URL 로 맞춘다. 다만 우리는 환경 변수에서 읽을 거라 `env.py` 에서 다시 덮어쓸 것이라, ini 의 값은 기본값 정도면 된다.

```ini
sqlalchemy.url = sqlite+aiosqlite:///./todo.db
```

### 7.12.3 `alembic/env.py` 를 비동기에 맞게

`alembic init` 이 만드는 `env.py` 는 동기 SQLAlchemy 를 가정한다. 우리 앱은 비동기 엔진을 쓰므로 약간 손봐야 한다. 핵심은 두 가지.

1. **앱의 모델 메타데이터를 `target_metadata` 로 등록**.
2. **비동기 엔진으로 마이그레이션을 돌릴 수 있게 `asyncio.run(...)`** 으로 감싸기.

아래 코드를 그대로 `alembic/env.py` 에 붙여 넣어 self-contained 로 동작하게 만든다(예제 폴더의 `alembic/env.py` 와 동일).

```python
# alembic/env.py
from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# alembic/ 가 프로젝트 루트의 자식이라는 전제로 sys.path 보정.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import settings  # noqa: E402
from app.db import Base  # noqa: E402
from app import models  # noqa: E402, F401  -- 모델 등록을 위해 필요

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드 — 실제 DB 에 연결하지 않고 SQL 문만 출력."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

여기서 짚을 점:

- **`from app import models`** : 한 줄이 매우 중요하다. Alembic 의 자동 생성 기능은 `Base.metadata` 를 본다. 그런데 `models.py` 가 import 된 적이 없으면 `Base.metadata` 에 우리 표가 등록되지 않은 상태다. 이 한 줄이 그 등록을 강제한다.
- **`render_as_batch=True`** : SQLite 는 ALTER TABLE 의 일부 형식만 지원한다. Alembic 의 batch 모드를 켜두면, 컬럼 변경 같은 작업이 SQLite 에서도 호환되게 처리된다.

### 7.12.4 첫 리비전 만들기

```bash
uv run alembic revision --autogenerate -m "create todos"
```

이 명령은 다음을 한다.

1. 현재 DB 의 스키마와 `Base.metadata` 를 비교한다.
2. 차이가 있으면 그 차이를 코드로 적은 새 리비전 파일을 `alembic/versions/` 에 만든다.

처음 실행할 때는 `todos` 표가 통째로 새로 만들어지는 리비전이 나온다. 파일명은 `<해시>_create_todos.py` 같은 모양. 본 예제에서는 보기 좋게 이름을 `0001_create_todos.py` 로 옮겨 두었다.

> **자동 생성을 무조건 믿어도 되나요?** 80% 정도. 컬럼 추가·삭제는 잘 잡지만, 컬럼 이름 변경은 "삭제 + 추가" 로 잘못 잡히곤 한다. 실수가 큰 작업(rename / type 변경) 은 생성된 리비전 파일을 사람이 한 번 읽고 손보는 게 안전하다.

### 7.12.5 적용

```bash
uv run alembic upgrade head
```

`head` 는 "리비전 트리에서 가장 최신" 을 가리킨다. 이 명령으로 DB 가 우리 모델과 같은 모양이 된다.

폴더에 `todo.db` 라는 SQLite 파일이 생기고, 그 안에 `todos` 와 `alembic_version` 두 표가 들어간다.

> **`alembic_version` 표** : Alembic 이 "현재 어느 리비전까지 적용됐는지" 를 기록하는 메타 표다. 사람이 직접 손대지 않는다.

### 7.12.6 되돌리기 / 새 리비전 더하기

```bash
# 한 단계 되돌리기
uv run alembic downgrade -1

# 새 변경(예: title 컬럼 길이 변경) 후 새 리비전
uv run alembic revision --autogenerate -m "extend title length"
uv run alembic upgrade head
```

운영에서는 "downgrade 는 거의 쓰지 않는다(데이터 손실 위험)" 가 안전 원칙이다. 학습 단계에서는 자유롭게 시험해 봐도 좋다.

---

## 7.13 통합 테스트 — `pytest` + `httpx.AsyncClient`

이제 마지막 큰 조각. 우리 라우터가 정말로 기대대로 동작하는지, **사람이 매번 curl 을 날리지 않고도** 자동으로 검증하자.

### 7.13.1 왜 통합 테스트인가

단위 테스트(`crud.create_todo` 만 부르는 테스트) 도 가능하지만, 라우터 + 의존성 주입 + 직렬화까지 포함한 **end-to-end 흐름**을 한 번에 검증하는 통합 테스트가 입문 단계에서 가장 가성비가 좋다. FastAPI 는 이 통합 테스트가 매우 짧게 작성된다.

### 7.13.2 의존성 오버라이드 — 핵심 아이디어

운영에서는 `get_session` 이 실제 SQLite/Postgres 에 연결한다. 테스트에서는 그 연결을 **메모리 DB** 로 갈아끼운다.

```python
app.dependency_overrides[get_session] = test_get_session
```

이 한 줄이 마법이다. FastAPI 의 의존성 주입은 "함수 → 함수" 로 갈아치울 수 있는 구조라서, **앱 코드는 한 글자도 안 바꾸고** 테스트 환경만 다르게 동작시킨다.

### 7.13.3 `tests/conftest.py`

```python
# tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import Base, get_session
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def sample_payload() -> dict:
    return {"title": "테스트 할 일", "description": "예시 설명", "is_done": False}
```

> **fixture 가 뭔가요?** pytest 의 핵심 개념이다. "테스트가 시작될 때 미리 만들어 두고, 끝날 때 정리할 자원" 을 함수로 묶어둔 것. 다른 fixture 가 인자로 그 fixture 이름을 적으면, pytest 가 알아서 이어 붙여 준다. `client` 는 `session_factory` 를 받고, `session_factory` 는 `engine` 을 받고… 자동으로 의존 그래프가 짜인다.

이 conftest 가 하는 일을 한 줄씩 짚자.

1. **`engine`** — 매 테스트 함수마다 깨끗한 메모리 DB 엔진을 만들고, `Base.metadata.create_all` 로 표를 만든다. 끝나면 drop + dispose.
2. **`session_factory`** — 그 엔진에 묶인 세션 팩토리.
3. **`client`** — `app.dependency_overrides` 로 진짜 `get_session` 을 우리 테스트용으로 갈아치운다. 그 다음 `httpx.AsyncClient(transport=ASGITransport(app=app))` 로 실제 네트워크 없이 앱에 직접 요청을 보낼 수 있는 클라이언트를 만든다.
4. **`sample_payload`** — 테스트마다 살짝 변형해서 쓸 기본 페이로드.

> **`ASGITransport(app=app)` 가 뭔가요?** httpx 의 트랜스포트 중 하나로, **HTTP 를 진짜 네트워크가 아니라 ASGI 인터페이스로 보내는 것** 이다. 진짜 서버를 띄우지 않으므로 매우 빠르고, 테스트 격리도 깔끔하다.

> **`TestClient` 와 어떻게 다른가요?** `from fastapi.testclient import TestClient` 도 거의 같은 일을 하지만 동기 인터페이스라서 비동기 fixture 와 살짝 어색하게 어울린다. 우리는 처음부터 비동기 흐름이라 `httpx.AsyncClient + ASGITransport` 를 쓰는 쪽이 자연스럽다.

### 7.13.4 `tests/test_todos.py`

테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다. 17개의 케이스를 만든다(전체 목록은 코드 블록 아래 참조).

```python
# tests/test_todos.py 일부
class TestCreateTodo:
    async def test_정상_생성은_201_과_본문을_돌려준다(
        self, client, sample_payload
    ):
        res = await client.post("/todos", json=sample_payload)
        assert res.status_code == 201
        body = res.json()
        assert body["id"] > 0
        assert body["title"] == sample_payload["title"]
        assert body["is_done"] is False

    async def test_제목이_빈_문자열이면_422(self, client):
        res = await client.post("/todos", json={"title": ""})
        assert res.status_code == 422

    async def test_제목_길이가_200자를_넘으면_422(self, client):
        too_long = "가" * 201
        res = await client.post("/todos", json={"title": too_long})
        assert res.status_code == 422


class TestListTodos:
    async def test_skip_limit_페이지네이션이_적용된다(self, client):
        for i in range(5):
            await client.post("/todos", json={"title": f"item {i}"})

        res = await client.get("/todos", params={"skip": 1, "limit": 2})
        body = res.json()
        assert body["total"] == 5
        assert body["skip"] == 1
        assert body["limit"] == 2
        assert len(body["items"]) == 2

    async def test_is_done_필터로_미완료만_가져온다(self, client):
        a = (await client.post("/todos", json={"title": "A"})).json()
        await client.post("/todos", json={"title": "B"})
        await client.patch(f"/todos/{a['id']}", json={"is_done": True})

        res = await client.get("/todos", params={"is_done": False})
        body = res.json()
        assert body["total"] == 1
        assert all(item["is_done"] is False for item in body["items"])


class TestUpdateTodo:
    async def test_부분_수정은_보낸_필드만_바꾼다(
        self, client, sample_payload
    ):
        created = (await client.post("/todos", json=sample_payload)).json()

        res = await client.patch(
            f"/todos/{created['id']}",
            json={"title": "수정된 제목"},
        )
        body = res.json()
        assert body["title"] == "수정된 제목"
        assert body["description"] == sample_payload["description"]
        assert body["is_done"] is False


class TestDeleteTodo:
    async def test_삭제는_204_를_돌려주고_본문이_없다(
        self, client, sample_payload
    ):
        created = (await client.post("/todos", json=sample_payload)).json()

        res = await client.delete(f"/todos/{created['id']}")
        assert res.status_code == 204
        assert res.content == b""

        res = await client.get(f"/todos/{created['id']}")
        assert res.status_code == 404
```

전체 파일은 예제 폴더의 `tests/test_todos.py` 에 있고, 다음 케이스를 포함한다.

1. 헬스 체크가 OK 를 돌려준다.
2. 정상 생성은 201 과 본문.
3. 빈 제목은 422.
4. 제목 누락은 422.
5. 제목 200자 초과는 422.
6. 없는 id 조회는 404.
7. 생성 후 단건 조회.
8. 목록 응답 구조.
9. skip/limit 페이지네이션.
10. is_done 필터.
11. limit 상한 위반은 422.
12. 부분 수정은 보낸 필드만 바꾼다.
13. 없는 id 수정은 404.
14. 빈 본문 PATCH 는 원본을 돌려준다.
15. 삭제는 204, 재조회는 404.
16. 없는 id 삭제는 404.
17. 생성 → 조회 → 수정 → 삭제 전체 흐름.

### 7.13.5 실행

```bash
uv run pytest -v
```

성공하면 다음과 비슷한 출력이 나온다.

```
tests/test_todos.py::TestHealthEndpoint::test_헬스_체크는_ok_를_돌려준다 PASSED
tests/test_todos.py::TestCreateTodo::test_정상_생성은_201_과_본문을_돌려준다 PASSED
tests/test_todos.py::TestCreateTodo::test_제목이_빈_문자열이면_422 PASSED
...
================== 17 passed in 0.85s ==================
```

매 테스트가 메모리 DB 위에서 따로 도므로 **순서에 의존하지 않는다**. 한 테스트가 만든 데이터가 다음 테스트에 새지 않는다.

### 7.13.6 `pyproject.toml` 의 pytest 옵션

테스트가 잘 돌게 하려면 `pyproject.toml` 에 작은 설정 한 블록이 필요하다.

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- `asyncio_mode = "auto"` — `async def test_...` 를 따로 데코레이터(`@pytest.mark.asyncio`) 없이도 자동으로 감지해 준다.
- `testpaths = ["tests"]` — 어디서 테스트 파일을 찾을지를 못박아둔다.

---

## 7.14 서버 띄우고 직접 호출해 보기

테스트를 다 통과했다면, 진짜 서버도 띄워서 한 번씩 눌러보자.

### 7.14.1 실행

```bash
# 만약 처음 실행이라면 .env.example 을 복사
cp .env.example .env

# DB 초기화
uv run alembic upgrade head

# 서버
uv run uvicorn app.main:app --reload
```

성공하면 다음과 같은 로그가 뜬다.

```
INFO:     Will watch for changes in these directories: ['/.../07-TodoAPI']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

### 7.14.2 헬스 체크

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

### 7.14.3 생성

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"우유 사기"}'
```

응답(201):

```json
{
  "id": 1,
  "title": "우유 사기",
  "description": null,
  "is_done": false,
  "created_at": "2026-04-25T12:30:00",
  "updated_at": "2026-04-25T12:30:00"
}
```

### 7.14.4 검증 실패

```bash
curl -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":""}'
```

응답(422):

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "title"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

422 본문은 Pydantic 이 생성한 **표준 에러 형식**이다. `loc` 가 어디서 검증이 실패했는지(여기서는 `body.title`) 정확히 알려준다.

### 7.14.5 목록 / 페이지네이션

```bash
# 기본
curl 'http://127.0.0.1:8000/todos'

# skip/limit
curl 'http://127.0.0.1:8000/todos?skip=0&limit=5'

# 미완료만
curl 'http://127.0.0.1:8000/todos?is_done=false'

# limit 위반은 자동 422
curl -i 'http://127.0.0.1:8000/todos?limit=1000'
```

### 7.14.6 부분 수정

```bash
curl -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done": true}'
```

응답:

```json
{
  "id": 1,
  "title": "우유 사기",
  "description": null,
  "is_done": true,
  "created_at": "2026-04-25T12:30:00",
  "updated_at": "2026-04-25T12:31:10"
}
```

`updated_at` 만 바뀐 것이 보인다.

### 7.14.7 삭제

```bash
curl -X DELETE -i http://127.0.0.1:8000/todos/1
```

응답:

```
HTTP/1.1 204 No Content
```

본문 없이 204 만 돌아온다.

### 7.14.8 자동 문서로 한 번 더 확인

브라우저에서 `http://127.0.0.1:8000/docs` 를 열면, 모든 라우트가 자동으로 등록되어 있고 "Try it out" 버튼으로 직접 호출도 된다. 이게 FastAPI 의 가장 큰 차별점 중 하나다.

---

## 7.15 흔한 실수 / 트러블슈팅

### 7.15.1 `from app...` import 가 빨간 줄로 표시됨

VS Code 가 다른 인터프리터를 보고 있을 때 흔하다. `Cmd/Ctrl+Shift+P → Python: Select Interpreter` 에서 `.venv` 안의 Python 을 골라 준다.

만약 알려진 디렉터리에서 모듈을 못 찾는다면, **명령을 어디서 실행하는지** 도 확인해야 한다. `uv run pytest`, `uv run uvicorn app.main:app` 모두 **프로젝트 루트(`pyproject.toml` 이 있는 곳)** 에서 실행해야 한다.

### 7.15.2 Alembic 자동 생성이 빈 마이그레이션을 만들어 낸다

원인 1: `env.py` 에서 `from app import models` 를 import 안 했다 → 모델이 `Base.metadata` 에 등록되지 않은 상태라 차이가 없는 것처럼 보인다.

원인 2: 이미 같은 표가 DB 에 존재한다 → "차이가 없으므로" 빈 리비전이 나온다. 의도와 다르다면 DB 파일(`todo.db`) 을 지우고 다시 시도.

### 7.15.3 `expire_on_commit` 관련 `MissingGreenlet` 또는 비동기 에러

세션을 만들 때 `expire_on_commit=True`(기본값) 인 상태에서, 커밋 후 객체 속성에 접근하면 SQLAlchemy 가 lazy load 를 시도하다가 비동기 컨텍스트에서 에러를 낼 수 있다. **`expire_on_commit=False`** 로 두면 이 종류의 에러를 거의 안 만난다.

### 7.15.4 PATCH 에서 보낸 필드가 안 갱신된다

`payload.model_dump()` 만 호출하면 **모든 필드가 dict 에 들어간다**. 보내지 않은 None 들이 그대로 None 으로 덮어써진다. 반드시 `model_dump(exclude_unset=True)` 를 쓰자.

### 7.15.5 응답에 `created_at` 이 빠져 있다

`TodoRead` 의 `model_config = ConfigDict(from_attributes=True)` 가 빠졌거나, 라우터에서 `response_model=TodoRead` 를 안 적었거나, dict 를 직접 만들어 `created_at` 키를 빼먹었을 가능성이 높다. ORM 객체를 그대로 리턴하고 `response_model` 에 맡기는 패턴이 가장 실수가 적다.

### 7.15.6 8000번 포트가 이미 사용 중

```
ERROR: [Errno 48] Address already in use
```

이전에 띄워두고 안 끈 uvicorn 이 있을 수 있다.

```bash
lsof -i :8000
# 또는 다른 포트로
uv run uvicorn app.main:app --reload --port 8001
```

### 7.15.7 테스트가 어떤 건 통과하고 어떤 건 실패한다(임의로)

테스트끼리 같은 DB 를 공유하고 있을 가능성이 크다. conftest 의 `engine` fixture 가 매 테스트마다 새로 만들어지는지 확인. `engine` fixture 의 스코프가 무심코 `module` 로 잡혀 있으면 실패한다(우리 예제는 기본 함수 스코프).

### 7.15.8 SQLite 의 `is_done=False` 가 0/1 로 보인다

SQLite 는 boolean 을 0/1 정수로 저장한다. SQLAlchemy 가 알아서 `bool` 로 변환해 주므로 Python 에서는 문제 없지만, DB 도구로 직접 들여다 볼 때 헷갈리지 않게 알아두자.

### 7.15.9 `OSError: [Errno 5] Input/output error` (테스트에서 가끔)

`pytest-asyncio` 의 모드를 명시하지 않았을 때 가끔 본다. `pyproject.toml` 의 `[tool.pytest.ini_options]` 에 `asyncio_mode = "auto"` 가 있는지 확인.

### 7.15.10 production 으로 오해할 만한 함정

- 학습용 SQLite 파일(`todo.db`) 을 git 에 올리지 말 것 — `.gitignore` 에 등록.
- `.env` 도 절대 커밋 금지(`.env.example` 만).
- `allow_origins=["*"]` 와 `allow_credentials=True` 동시에 쓰지 말 것.
- 운영 환경에서는 `--reload` 옵션을 절대 켜지 말 것(파일 와처가 무거움).

---

## 7.16 다른 DB 로 전환하기

이 예제를 PostgreSQL 로 돌리려면 두 줄만 바꾸면 된다.

### 7.16.1 드라이버 추가

```bash
uv add asyncpg
```

### 7.16.2 `.env`

```dotenv
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/todo
```

### 7.16.3 마이그레이션 다시 적용

```bash
uv run alembic upgrade head
```

`models.py`, `crud.py`, `routers/todos.py` 는 한 줄도 바꾸지 않는다. SQLAlchemy + Alembic 의 추상화 덕분이다.

> **production 에서는 PostgreSQL 을 권장**. SQLite 는 학습/단일 사용자에 적합하지만, 동시 쓰기·복제 등을 본격적으로 쓰기 시작하면 PostgreSQL/MySQL 쪽이 안전하다.

---

## 7.17 이 챕터 요약

- 도메인이 자라기 시작하면 **라우터 분리**(`APIRouter`) 와 **서비스 레이어 분리**(`crud.py`) 가 자연스러운 진화 방향이다. "라우터는 HTTP 만, crud 는 DB 만." 이 한 줄을 머리에 새기면 코드 구조가 흔들리지 않는다.
- **응답 모델 분리** 와 `from_attributes=True` 의 조합이 ORM 모델과 API 표면을 깔끔히 떼어준다. 향후 컬럼이 늘어도 응답이 자동으로 바뀌지 않는다.
- **HTTP 상태 코드 일관성** : 생성 201, 삭제 204, 자원 없음 404, 검증 실패 422. `HTTPException` 으로 에러를 raise.
- **부분 수정의 표준 패턴**은 `payload.model_dump(exclude_unset=True)` 한 줄. 보낸 필드만 갱신하는 의미를 그대로 표현한다.
- **페이지네이션** 은 같은 필터를 적용한 두 쿼리(count + page) 를 함께 돌려준다. 클라이언트가 페이지 수를 직접 계산할 수 있게.
- **Alembic 마이그레이션** 첫 적용 흐름: `alembic init alembic` → `env.py` 에서 `Base.metadata` 등록 → `alembic revision --autogenerate -m "..."` → `alembic upgrade head`.
- **통합 테스트** 는 `pytest` + `httpx.AsyncClient` + `app.dependency_overrides[get_session]` 로 메모리 DB 위에서 빠르게. fixture 한 번 만들어 두면 그 다음부터 테스트 함수 자체가 매우 짧아진다.
- 운영의 작은 마무리: `/health` 한 줄, `CORSMiddleware` 한 줄, `.env.example` 한 파일.

다음 챕터에서는 이 위에 **사용자 인증(회원가입·로그인·JWT)** 을 얹는다. 인증이 들어가면 "이 Todo 는 누구의 것인가?" 라는 질문이 생기고, 모델에 `user_id` 같은 외래 키가 자라기 시작한다. 그 흐름은 10장(Note API) 종합 예제에서 한 번 더 처음부터 함께 만든다.

---

← [06. SQLAlchemy 2.0과 데이터베이스 연동](06-sqlalchemy-database.md) | 다음 문서로 이동: **[08. 사용자 인증 — JWT와 Bcrypt →](08-authentication.md)**
