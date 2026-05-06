# 11. 종합 예제 2 — Blog API (처음부터 따라하기)

> **이 챕터의 목표**
> - 앞 챕터를 한 번도 펼치지 않고도 **이 한 문서만** 따라가면 동작하는 다중 사용자 블로그 API를 완성한다.
> - User · Post · Comment · Tag 네 모델 사이의 **1:N · N:M 관계**를 SQLAlchemy 2.0의 `relationship`/`secondary`로 표현한다.
> - **MySQL** 데이터베이스를 Docker Compose로 띄우고, **Alembic 마이그레이션**으로 다섯 개의 테이블을 한 번에 만든다.
> - 페이지네이션(`?page=1&size=20`), 검색(`?q=...`), 태그 필터(`?tag=python`), 정렬(`?sort=-created_at`)까지 한 라우트에 합친다.
> - 글에 **태그 이름 배열**(`tags: ["python","fastapi"]`)을 넘기면 자동으로 태그를 만들고 N:M으로 연결한다.
> - 공개 글은 누구나, 비공개 글은 작성자만. 댓글은 자기 댓글만 수정·삭제 — 라우트 단계에서의 **인가**를 체험한다.
> - **N+1 문제**를 인식하고 `selectinload`로 한 번에 해결한다.
> - Docker로 컨테이너 이미지를 만들고, Render·Fly.io·Ubuntu 서버 어디든 올릴 수 있는 형태로 마무리한다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 본문에서도 처음 등장하는 용어는 한 줄짜리 정의 박스로 함께 설명합니다.

> **소요 시간**: 8~12시간 (처음이면 이틀)

> **이 챕터의 위치**: 10장은 PostgreSQL을 썼습니다. 11장은 같은 패턴을 한 단계 키워 **MySQL + 다중 모델 + N:M**까지 다룹니다. 두 챕터는 **완전히 독립**입니다 — 10장을 건너뛰고 11장만 봐도 처음부터 끝까지 만들 수 있게 구성했습니다.

---

## 11.1 어떤 것을 만드는가

### 11.1.1 한 줄 요약

여러 사용자가 글을 쓰고, 태그를 붙이고, 서로 댓글을 다는 **다중 사용자 블로그 REST API**입니다. 회원가입·로그인·JWT 인증부터 페이지네이션까지 실제 서비스에서 보는 것을 한 프로젝트에 모았습니다.

### 11.1.2 도메인 한눈에 보기

| 모델 | 한 줄 정의 | 핵심 필드 |
|------|-----------|-----------|
| **User** | 일반 회원 | `id, email(uniq), password_hash, name, is_active, created_at` |
| **Post** | 글 | `id, user_id(FK), title, slug(uniq), body, published, published_at, created_at, updated_at` |
| **Comment** | 댓글 | `id, post_id(FK), user_id(FK), body, created_at` |
| **Tag** | 태그 | `id, name(uniq), slug(uniq)` |
| **PostTag** | Post ↔ Tag 다대다 연결 | `post_id, tag_id` (둘이 합쳐 PK) |

### 11.1.3 모델 사이의 관계 다이어그램

```
                    ┌──────────┐
                    │   User   │
                    └────┬─────┘
                         │ 1
              ┌──────────┴───────────┐
              │ N                    │ N
              ▼                      ▼
        ┌──────────┐          ┌────────────┐
        │   Post   │  1   N   │  Comment   │
        │          │◀─────────┤            │
        └────┬─────┘          └────────────┘
             │ N
             │
             │ N:M (PostTag 연결 테이블)
             │
             ▼ M
        ┌──────────┐
        │   Tag    │
        └──────────┘
```

말로 풀면 다음과 같습니다.

- **User 1 : N Post** — 한 사용자가 여러 글을 쓴다.
- **User 1 : N Comment** — 한 사용자가 여러 댓글을 단다.
- **Post 1 : N Comment** — 한 글에 여러 댓글이 달린다.
- **Post N : M Tag** — 한 글에 여러 태그, 한 태그가 여러 글에. 가운데 **PostTag** 라는 연결 테이블로 표현한다.

> **N:M(many-to-many)이란?** 두 표 사이가 "여러 대 여러"로 연결되는 관계입니다. RDBMS는 N:M을 직접 표현할 수 없어서, **연결 테이블(또는 pivot, junction 테이블)** 이라는 작은 표를 하나 더 만들어 두 표의 PK를 한 행에 묶습니다. PostTag가 그 역할입니다.

### 11.1.4 엔드포인트 표

| 메서드 | 경로 | 인증 | 설명 |
|--------|------|------|------|
| POST | `/auth/signup` | — | 회원가입 |
| POST | `/auth/login` | — | 로그인, JWT 토큰 발급 (form) |
| GET | `/auth/me` | Bearer | 내 정보 |
| GET | `/posts` | Optional | 글 목록(공개 + 본인 비공개), 페이지네이션·검색·태그 필터·정렬 |
| GET | `/posts/{id}` | Optional | 단건 조회. 비공개는 작성자만 |
| POST | `/posts` | Bearer | 글 작성. `tags: ["python","fastapi"]` 자동 연결 |
| PATCH | `/posts/{id}` | Bearer | 부분 수정 (작성자만) |
| DELETE | `/posts/{id}` | Bearer | 삭제 (작성자만) |
| POST | `/posts/{id}/publish` | Bearer | 공개 처리 |
| POST | `/posts/{id}/unpublish` | Bearer | 비공개 처리 |
| GET | `/posts/{id}/comments` | Optional | 댓글 목록 |
| POST | `/posts/{id}/comments` | Bearer | 댓글 작성 |
| PATCH | `/comments/{id}` | Bearer | 자기 댓글만 수정 |
| DELETE | `/comments/{id}` | Bearer | 자기 댓글만 삭제 |
| GET | `/tags` | — | 태그 목록 |
| GET | `/health` | — | 헬스체크 |

> **"Bearer / Optional / —" 의 차이**:
> - **—**: 인증이 필요 없는 공개 엔드포인트.
> - **Bearer**: `Authorization: Bearer <토큰>` 헤더가 반드시 필요. 없으면 401.
> - **Optional**: 토큰이 있어도 되고 없어도 됨. **있으면 사용자 정보를 활용**(예: 자기 비공개 글 보여주기).

### 11.1.5 사용 스택 요약

이 챕터에서 새로 깔거나 바꾸는 것만 표시했습니다.

| 구성요소 | 사용 버전 / 도구 | 비고 |
|----------|------------------|------|
| Python | 3.13+ | |
| FastAPI | 0.115.x+ | |
| Pydantic | 2.x + `pydantic[email]` | `EmailStr` 검증 |
| SQLAlchemy | 2.0 (async) | `relationship`, `secondary`로 N:M |
| Alembic | 1.13+ | 마이그레이션 |
| **asyncmy** | 0.2+ | **MySQL 비동기 드라이버** (10장의 PostgreSQL `asyncpg` 자리) |
| PyJWT | 2.8+ | 인증 |
| bcrypt | 4.x | 비밀번호 해싱 (직접 사용) |
| python-slugify | 8.x | 제목 → URL slug |
| Uvicorn | 0.30+ | 개발 서버 |
| Gunicorn | 23.x | 운영 |
| Docker / Docker Compose | latest | MySQL + 앱 통합 실행 |
| MySQL | 8.4 LTS | DB |
| uv | 0.4+ | 패키지·가상환경 |

> **왜 10장은 PostgreSQL이고 11장은 MySQL인가?** 두 DBMS가 점유율이 비슷하고, 회사·기존 코드와 통합할 때는 MySQL을 만나는 일이 흔합니다. SQLAlchemy 2.0의 비동기 ORM을 쓰면 **`DATABASE_URL` 한 줄만 바꾸면** 두 DB 사이를 거의 그대로 옮길 수 있다는 점을 두 챕터로 직접 보여 드리는 의도입니다.

> **MySQL 8.4를 쓰는 이유** — 2026년 4월 시점에서 **MySQL 8.4가 LTS(장기 지원)** 입니다. 8.0은 2026년 4월 30일에 Premier Support가 종료될 예정이므로 새 프로젝트는 8.4로 시작하시길 권합니다.

---

## 11.2 프로젝트 구조 한눈에

이번 챕터의 결과 폴더는 다음과 같은 모양이 됩니다. 절마다 한 파일씩 채워 나갈 것이니, 지금은 어떤 파일이 어디 위치하는지 머리에만 그림으로 새겨 두세요.

```
11-BlogAPI/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml      # app + mysql + migrate
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial.py     # 다섯 테이블을 한 번에 만든다
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 앱 조립
│   ├── config.py           # .env에서 설정 로딩
│   ├── db.py               # 비동기 엔진·세션 의존성
│   ├── models.py           # User · Post · Comment · Tag · PostTag
│   ├── schemas.py          # Pydantic 입출력
│   ├── security.py         # bcrypt + JWT
│   ├── deps.py             # get_current_user / get_optional_user
│   ├── crud.py             # slug, 태그 자동 생성, 검색·페이지 빌더
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── posts.py
│       ├── comments.py
│       └── tags.py
└── tests/
    ├── __init__.py
    ├── conftest.py         # 인메모리 DB + 의존성 override + 토큰 픽스처
    └── test_blog.py        # 10개의 통합 케이스
```

> **`crud.py`는 옛 DAO 패턴이 아닙니다** — 우리가 쓰는 건 "라우트가 직접 ORM을 부르되, 자주 쓰는 쿼리 빌더(예: 검색·페이지네이션 결합)는 `crud.py`에 모아 둔다"는 가벼운 분리입니다. 풀스케일 서비스에서는 `services/posts_service.py` 같은 더 두꺼운 레이어를 두기도 합니다.

---

## 11.3 사전 준비

### 11.3.1 필요한 것

- **macOS 또는 Linux** (Windows는 WSL2 안에서 작업 권장).
- **Python 3.13+** — `python --version`으로 확인.
- **uv** — 03장에서 깔았다면 그대로 사용. 없으면:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Docker Desktop** (또는 Linux의 `docker` + `docker compose` 플러그인).
- 터미널에서 `curl`, 가능하면 `jq` (curl 응답에서 토큰 뽑을 때 편함).

### 11.3.2 새 프로젝트 만들기

```bash
mkdir 11-BlogAPI
cd 11-BlogAPI

uv init
```

`uv init`이 만든 기본 `hello.py` 같은 파일은 우리에겐 필요 없으니 지워도 좋습니다.

### 11.3.3 의존성 설치

```bash
uv add fastapi "uvicorn[standard]" "gunicorn>=23" \
       "sqlalchemy[asyncio]>=2.0" alembic asyncmy aiosqlite \
       pyjwt bcrypt python-slugify python-multipart \
       pydantic-settings "pydantic[email]"

uv add --dev pytest pytest-asyncio httpx
```

각 라이브러리의 역할:

- **fastapi / uvicorn / gunicorn** — 웹 프레임워크와 ASGI 서버, 운영용 프로세스 매니저(선택). 본 가이드의 표준은 Uvicorn 자체 멀티워커이며 Gunicorn 은 graceful reload 가 필요할 때만 추가.
- **sqlalchemy[asyncio] / alembic / asyncmy** — ORM(asyncio extras 포함), 마이그레이션, MySQL 비동기 드라이버.
- **aiosqlite** — 테스트에서 인메모리 SQLite를 띄울 때 사용. 운영 코드는 MySQL.
- **pyjwt / bcrypt** — 08장에서 깐 그대로. JWT 발급·검증, 비밀번호 해싱.
- **python-slugify** — `"FastAPI 시작하기"` 같은 제목을 `"fastapi"` 같은 URL-safe 문자열로 바꿔 줍니다(11.7에서 사용).
- **python-multipart** — `OAuth2PasswordRequestForm`(`/auth/login` 의 폼 파싱)에 필수. 없으면 부팅 즉시 *Form data requires "python-multipart" to be installed* 로 실패합니다.
- **pydantic-settings / pydantic[email]** — `.env` 로딩과 이메일 형식 검증.

> **왜 운영 DB와 다른 SQLite도 같이 깔아 두나요?** 통합 테스트를 빠르게 돌리기 위해서입니다. 11.17의 `tests/conftest.py`는 매 테스트마다 인메모리 SQLite DB를 새로 만들어 격리합니다. 같은 ORM 코드가 두 DB에서 모두 동작한다는 점은 SQLAlchemy의 큰 장점입니다.

### 11.3.4 `.python-version`

3.13을 명시해 두면 `uv` 명령이 알아서 그 버전을 씁니다.

```bash
echo 3.13 > .python-version
```

### 11.3.5 `.gitignore`

다음 내용을 `.gitignore`에 적습니다(샘플은 예제 폴더 참고).

```gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/

# 가상환경
.venv/
venv/

# 환경 변수 (절대 커밋 금지)
.env
.env.local

# SQLite (테스트용으로만 사용)
*.db
*.sqlite
*.sqlite3

# 에디터/OS
.vscode/
.idea/
.DS_Store
```

> **`.env`는 절대 커밋하지 않습니다.** 비밀키와 DB 비밀번호가 들어가는 파일이라, 한번 git 히스토리에 들어가면 깔끔히 지우기 어렵습니다.

---

## 11.4 MySQL을 Docker로 띄우기

### 11.4.1 왜 Docker인가

MySQL을 직접 깔지 않고 Docker 컨테이너로 띄우면 다음이 좋습니다.

- 호스트 OS를 깨끗하게 유지(나중에 지울 때 컨테이너만 지우면 끝).
- 팀원·CI가 같은 명령으로 같은 환경을 띄울 수 있음.
- MySQL 버전을 프로젝트별로 바꾸기 쉬움.

> **컨테이너(container)란?** 앱과 그 의존성·OS 환경을 한 번에 묶어 어디서나 똑같이 돌릴 수 있게 만든 단위입니다. **이미지(image)**가 그 설계도, **컨테이너**는 그 설계도로 띄운 인스턴스입니다.

### 11.4.2 가장 짧은 방법 — 한 명령

```bash
docker run --name blog-mysql \
  -e MYSQL_DATABASE=blog_api \
  -e MYSQL_USER=blog_user \
  -e MYSQL_PASSWORD=blog_pass \
  -e MYSQL_ROOT_PASSWORD=root_pass \
  -v blog-mysql-data:/var/lib/mysql \
  -p 3306:3306 \
  -d mysql:8.4
```

옵션을 풀어 봅니다.

- `--name blog-mysql` — 컨테이너 이름.
- `-e MYSQL_*` — 자동으로 만들 DB 이름·사용자·비번. 공식 이미지가 첫 실행 시 이 값들을 사용합니다.
- `-v blog-mysql-data:/var/lib/mysql` — 데이터 영속성을 위한 볼륨. 컨테이너를 지워도 DB 내용은 남습니다.
- `-p 3306:3306` — 호스트 3306 포트 ↔ 컨테이너 3306 포트.
- `-d mysql:8.4` — 백그라운드 실행, MySQL 8.4 LTS 이미지.

준비 완료(20~40초)까지 기다리고 다음으로 확인.

```bash
docker logs blog-mysql 2>&1 | grep "ready for connections"
# "ready for connections" 가 보이면 OK
```

### 11.4.3 더 권장하는 방법 — Docker Compose

여러 서비스를 한 파일로 묶고, 마이그레이션·앱·DB를 함께 띄울 수 있어 협업에 좋습니다. 이 가이드는 **11.18 섹션**에서 `docker-compose.yml`을 통째로 작성합니다. 지금은 위의 단일 명령으로 시작해도 됩니다.

### 11.4.4 접속 테스트

호스트에 `mysql` 클라이언트가 깔려 있다면:

```bash
mysql -h 127.0.0.1 -P 3306 -u blog_user -pblog_pass blog_api
mysql> SHOW TABLES;
Empty set
mysql> exit
```

비어 있어야 정상입니다(아직 마이그레이션을 안 돌렸으니까).

---

## 11.5 `.env`와 `app/config.py`

### 11.5.1 `.env.example`

루트에 다음 내용을 적은 `.env.example`을 만듭니다.

```bash
# .env.example
DATABASE_URL=mysql+asyncmy://blog_user:blog_pass@127.0.0.1:3306/blog_api
# 32바이트 미만이면 PyJWT가 InsecureKeyLengthWarning 을 띄웁니다.
SECRET_KEY=please-change-this-to-32-bytes-or-longer-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

복사해서 실제 `.env`를 만들고 `SECRET_KEY`를 강한 난수로 교체합니다.

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
# 출력값을 .env의 SECRET_KEY 자리에 붙여 넣는다
```

> **`mysql+asyncmy://...`의 형식 풀이**: `드라이버명+비동기드라이버명://사용자:비번@호스트:포트/DB명`. 비밀번호에 `@` 같은 특수문자가 있으면 URL 인코딩(`%40`)이 필요합니다.

### 11.5.2 `app/config.py`

`pydantic-settings`로 환경 변수를 한 번에 읽습니다. 같은 모듈을 모든 다른 모듈이 import해 한 곳에서 설정을 가져갑니다.

```python
# app/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    database_url: str = (
        "mysql+asyncmy://blog_user:blog_pass@127.0.0.1:3306/blog_api"
    )
    # 기본값은 PyJWT 2.x 의 InsecureKeyLengthWarning(<32바이트) 회피용 더미.
    # 운영에서는 .env로 반드시 강한 난수를 주입.
    secret_key: str = "please-change-this-to-32-bytes-or-longer-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

`@lru_cache`는 "여러 모듈에서 `get_settings()`를 불러도 같은 인스턴스를 돌려준다"는 보장을 합니다. 환경 변수는 한 번만 읽으면 충분하니까요.

---

## 11.6 `app/db.py` — 비동기 엔진과 세션 의존성

06·08장과 같은 패턴이지만 MySQL용으로 **두 옵션**을 추가했습니다.

```python
# app/db.py
from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,    # 끊긴 연결 자동 감지
    pool_recycle=1800,     # 30분 지난 연결은 재연결
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """모든 ORM 모델 클래스의 부모."""


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
```

### 11.6.1 `pool_pre_ping=True`와 `pool_recycle=1800`이 왜 중요한가

MySQL 서버는 기본적으로 **8시간(`wait_timeout=28800s`)** 동안 활동이 없는 연결을 끊습니다. 우리 앱 쪽 커넥션 풀은 그 사실을 모르고 끊긴 연결을 그대로 재사용하다가 다음 쿼리에서 *Lost connection to MySQL server* 에러를 만납니다.

> **커넥션 풀(connection pool)이란?** "DB와의 연결"을 매번 새로 만드는 비용이 비싸기 때문에, 일정 개수를 미리 만들어 두고 재사용하는 패턴입니다. SQLAlchemy가 자동으로 관리합니다.

해결책 두 가지를 함께 적용했습니다.

- **`pool_pre_ping=True`** — 연결을 풀에서 꺼낼 때마다 가벼운 `SELECT 1`로 살아 있는지 확인. 죽었으면 새로 만든다.
- **`pool_recycle=1800`** — 30분(=1800초) 지난 연결은 강제로 재생성. MySQL의 8시간 한도보다 한참 짧게.

> **개발 단계에서 `echo=True`를 잠깐 켜 보세요.** `create_async_engine(...)` 인자에 `echo=True`를 넣으면 SQLAlchemy가 만들어 보내는 모든 SQL이 콘솔에 찍힙니다. N+1 문제(11.19)가 의심될 때 가장 먼저 보는 도구입니다.

---

## 11.7 모델 정의 — `app/models.py`

이 챕터의 가장 핵심 파일입니다. 다섯 클래스를 한 파일에 모아 두면 IDE의 점프와 검색이 편합니다(큰 프로젝트에서는 모델별로 파일 분리도 흔함).

### 11.7.1 전체 코드

```python
# app/models.py
from __future__ import annotations
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer,
    String, Text, UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    """timezone-aware UTC 현재 시각."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow, onupdate=_utcnow,
        nullable=False,
    )

    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.asc()",
    )
    tags: Mapped[list["Tag"]] = relationship(
        secondary="post_tags",
        back_populates="posts",
    )

    __table_args__ = (
        Index("ix_posts_published_created", "published", "created_at"),
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    body: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        secondary="post_tags",
        back_populates="tags",
    )


class PostTag(Base):
    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )
```

### 11.7.2 1:N 관계 — `relationship` + `back_populates`

`User`와 `Post` 사이의 1:N을 다시 봅니다.

```python
# User 쪽
posts: Mapped[list["Post"]] = relationship(
    back_populates="author",
    cascade="all, delete-orphan",
)

# Post 쪽
user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id", ondelete="CASCADE"),
    nullable=False, index=True,
)
author: Mapped["User"] = relationship(back_populates="posts")
```

세 가지 포인트.

1. **외래 키 컬럼은 Post 쪽에 둔다.** "여러 개"인 쪽이 "하나"인 쪽의 PK를 가리킵니다. `user_id INT REFERENCES users(id)`.
2. **`relationship(...)`은 Python 객체끼리의 연결을 표현**합니다. DB 레벨의 외래 키와는 별개의 정보입니다. 두 가지를 모두 선언해야 ORM이 양쪽으로 자유롭게 객체를 따라갑니다.
3. **`back_populates`** 는 양방향 관계의 "짝꿍 이름"을 알려줍니다. `User.posts`와 `Post.author`가 같은 관계의 두 면이라는 점을 SQLAlchemy에게 알려주는 셈입니다.

> **`back_populates` vs `backref`** — 옛 코드에서는 `backref="author"` 한 줄로 양쪽을 자동 선언하는 방식을 자주 봤습니다. SQLAlchemy 2.0의 권장 방식은 **양쪽에 명시적으로 `relationship + back_populates`** 입니다. IDE 자동 완성과 타입 체크가 더 정확하기 때문입니다.

### 11.7.3 cascade 정책 — `"all, delete-orphan"`

```python
posts: Mapped[list["Post"]] = relationship(
    back_populates="author",
    cascade="all, delete-orphan",
)
```

- **`"all"`**: 부모(User)에 대한 모든 작업(refresh, expire, expunge, delete, ...)을 자식(Post)에게도 전파.
- **`"delete-orphan"`**: 부모와 분리된(고아가 된) Post를 자동 삭제. 결과적으로 "사용자가 지워지면 그 사람의 글도 함께 사라진다"는 의미.

DB 레벨의 `ondelete="CASCADE"`도 동시에 걸어 두었으니, **두 줄이 함께 작용**해 어떤 경로로 삭제가 일어나도 자식 행이 남지 않게 합니다. 둘 중 하나만 두면 시나리오에 따라 고아 행이 남을 수 있습니다.

### 11.7.4 N:M 관계 — `secondary="post_tags"`

```python
# Post 쪽
tags: Mapped[list["Tag"]] = relationship(
    secondary="post_tags",
    back_populates="posts",
)

# Tag 쪽
posts: Mapped[list["Post"]] = relationship(
    secondary="post_tags",
    back_populates="tags",
)

# 별도 클래스
class PostTag(Base):
    __tablename__ = "post_tags"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ...), primary_key=True)
    tag_id:  Mapped[int] = mapped_column(ForeignKey("tags.id",  ...), primary_key=True)
```

`secondary=`에 연결 테이블 이름(또는 `__table__`)을 넘기면, SQLAlchemy가 알아서 다음을 처리해 줍니다.

- `post.tags.append(tag)` → `INSERT INTO post_tags (post_id, tag_id) VALUES (...)`
- `post.tags = [tag1, tag2]` → 기존 연결을 정리하고 새로 INSERT.
- `await session.delete(post)` → `ondelete=CASCADE` 덕분에 연결 행도 함께 사라짐.

> **PostTag 클래스를 따로 만들 필요가 있나요?** 단순한 N:M이라면 [`Table` 객체로만 정의](https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many)해도 됩니다. 우리는 (1) 명시적인 모델로 두면 Alembic이 더 깔끔하게 인식하고, (2) 나중에 연결 테이블에 새 컬럼(예: `created_at`)을 추가하기 쉬워서 클래스로 만들었습니다.

### 11.7.5 `created_at` / `updated_at` 자동 채움

```python
created_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=_utcnow, nullable=False,
)
updated_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True),
    default=_utcnow, onupdate=_utcnow,
    nullable=False,
)
```

- **`default=_utcnow`** — INSERT 직전에 값이 비어 있으면 함수를 호출해 채웁니다. **함수 자체를 넘기는 점**에 주의 — `default=_utcnow()`로 괄호를 붙이면 모듈 import 시점의 시각이 박힙니다.
- **`onupdate=_utcnow`** — UPDATE 직전에 자동으로 새 시각을 채웁니다.

### 11.7.6 인덱스 한 번 더 — 자주 검색하는 열에

```python
__table_args__ = (
    Index("ix_posts_published_created", "published", "created_at"),
)
```

이 복합 인덱스는 "공개 글의 최신순 목록"을 빠르게 가져오기 위함입니다. `WHERE published = TRUE ORDER BY created_at DESC` 쿼리가 자주 나가니까요.

> **인덱스(index)란?** 책의 색인처럼 "이 값이 어느 행에 있는지"를 미리 정리해 둔 자료구조입니다. `WHERE`나 `JOIN ON`에 쓰이는 열에 만들면 검색이 빨라지지만, INSERT/UPDATE 시 인덱스도 함께 갱신해야 해 약간의 비용이 듭니다.

---

## 11.8 Pydantic 스키마 — `app/schemas.py`

요청·응답의 모양을 정의합니다. ORM 모델과 한 번 더 분리해 두는 이유는 06·08장에서 본 그대로입니다.

```python
# app/schemas.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=80)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime


class AuthorSummary(BaseModel):
    """글·댓글 응답에 함께 노출하는 작성자 요약. 이메일은 비공개."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TagSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=50_000)
    published: bool = False
    tags: list[str] = Field(default_factory=list, max_length=10)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=50_000)
    published: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=10)


class PostRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    slug: str
    body: str
    published: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: AuthorSummary
    tags: list[TagSummary]


class PostList(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    items: list[PostRead]
    page: int
    size: int
    total: int


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    body: str
    created_at: datetime
    author: AuthorSummary
```

핵심 포인트.

- **`AuthorSummary`** — 글이나 댓글에 작성자 정보를 같이 보여줄 때 이메일·생성 시각 같은 불필요한 정보까지 노출하지 않도록 분리한 작은 스키마.
- **`PostRead.author / .tags`** — 응답에 작성자 요약과 태그 목록이 함께 들어갑니다. **N+1 문제를 막으려면 라우트에서 `selectinload`로 미리 가져와야** 합니다(11.13).
- **`from_attributes=True`** — Pydantic v2의 옛 `orm_mode=True`. SQLAlchemy 모델 인스턴스에서 직접 속성을 읽어 만들 수 있게 합니다.

### 11.8.1 `PostUpdate.tags`의 세 가지 의미

| 클라이언트가 보낸 값 | 라우터의 행동 |
|----------------------|---------------|
| 키 자체가 없음 | 태그를 변경하지 않음 |
| `[]` (빈 배열) | 모든 태그 제거 |
| `["python","fastapi"]` | 그 목록으로 교체(없는 태그는 자동 생성) |

`exclude_unset=True`로 dict를 만들면 첫 번째 케이스("키 자체가 없음")가 자연스럽게 처리됩니다. 11.13.1에서 라우트가 이 분기를 어떻게 표현하는지 봅니다.

---

## 11.9 Alembic — 첫 마이그레이션

### 11.9.1 초기화

이미 의존성에 `alembic`이 들어 있으니 바로 골격을 만듭니다.

```bash
uv run alembic init alembic
```

`alembic/`, `alembic.ini`가 생깁니다. `alembic.ini`의 `sqlalchemy.url` 줄은 어떤 값이 들어 있어도 우리가 `env.py`에서 덮어쓸 것이므로 그대로 둬도 됩니다.

### 11.9.2 `alembic/env.py` 교체

기본 생성된 `env.py`는 동기 엔진을 가정합니다. 비동기 엔진과 우리 설정값을 쓰도록 통째로 교체합니다.

```python
# alembic/env.py
from __future__ import annotations
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import get_settings
from app.db import Base
import app.models  # noqa: F401  (import 만으로 Base.metadata 에 모델이 등록됨)


config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata,
        literal_binds=True, dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
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

`import app.models` 줄을 잊지 마세요. 모델이 `Base.metadata`에 등록되려면 어딘가에서 한 번은 import되어야 합니다. 빠뜨리면 `autogenerate`가 빈 마이그레이션을 만듭니다.

### 11.9.3 마이그레이션 파일 작성

`autogenerate`도 좋지만, 이 챕터는 다섯 테이블이 외래 키로 얽혀 있어 **순서를 직접 통제**하는 편이 안전합니다. 다음 파일을 손으로 만듭니다.

```python
# alembic/versions/0001_initial.py
"""initial — User · Post · Comment · Tag · PostTag.

외래 키 의존성 때문에 다음 순서로 만들어야 한다.
1) users
2) posts (users 참조)
3) comments (posts, users 참조)
4) tags
5) post_tags (posts, tags 참조)
"""
from __future__ import annotations
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False,
                  server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("slug", sa.String(length=220), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False,
                  server_default=sa.false()),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_posts_slug"),
    )
    op.create_index(op.f("ix_posts_user_id"), "posts", ["user_id"])
    op.create_index("ix_posts_published_created",
                    "posts", ["published", "created_at"])

    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("body", sa.String(length=2000), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False,
                  server_default=sa.func.current_timestamp()),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"])
    op.create_index(op.f("ix_comments_user_id"), "comments", ["user_id"])

    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("slug", sa.String(length=60), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_tags_name"),
        sa.UniqueConstraint("slug", name="uq_tags_slug"),
    )

    op.create_table(
        "post_tags",
        sa.Column("post_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("post_id", "tag_id"),
        sa.UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )


def downgrade() -> None:
    op.drop_table("post_tags")
    op.drop_table("tags")
    op.drop_index(op.f("ix_comments_user_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_table("comments")
    op.drop_index("ix_posts_published_created", table_name="posts")
    op.drop_index(op.f("ix_posts_user_id"), table_name="posts")
    op.drop_table("posts")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
```

> **자동 생성을 쓰고 싶다면** `uv run alembic revision --autogenerate -m "initial"`로 만든 뒤, 외래 키 순서가 맞는지·인덱스가 빠지지 않았는지 검토만 하시면 됩니다. 손으로 한 번 적어 보면 어떤 SQL이 생성되는지 머릿속에 더 또렷이 남습니다.

### 11.9.4 적용

MySQL이 떠 있는 상태에서:

```bash
uv run alembic upgrade head
```

성공 출력:

```
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, initial — User · Post · Comment · Tag · PostTag.
```

확인:

```bash
mysql -h 127.0.0.1 -P 3306 -u blog_user -pblog_pass blog_api -e "SHOW TABLES;"
# +-----------------------+
# | Tables_in_blog_api    |
# +-----------------------+
# | alembic_version       |
# | comments              |
# | post_tags             |
# | posts                 |
# | tags                  |
# | users                 |
# +-----------------------+
```

> **`alembic_version` 테이블의 의미** — 지금 DB가 어느 마이그레이션까지 적용됐는지 한 행으로 기록합니다. `alembic upgrade/downgrade`가 이 행을 보고 다음에 무엇을 적용할지 결정합니다.

---

## 11.10 보안 — `app/security.py`와 `app/deps.py`

08장과 거의 동일합니다. 새로 추가된 점은 **`get_optional_user`**(토큰이 없어도 통과하는 의존성) 한 가지뿐입니다.

### 11.10.1 `app/security.py`

```python
# app/security.py
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings
from app.schemas import TokenPayload

settings = get_settings()
MAX_PASSWORD_BYTES = 72


def hash_password(plain: str) -> str:
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"비밀번호가 너무 깁니다(UTF-8 기준 {MAX_PASSWORD_BYTES}바이트 초과). "
            "한국어는 글자당 3바이트로 계산됩니다."
        )
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    encoded_plain = plain.encode("utf-8")
    encoded_hash = hashed.encode("utf-8")
    if len(encoded_plain) > MAX_PASSWORD_BYTES:
        return False
    try:
        return bcrypt.checkpw(encoded_plain, encoded_hash)
    except ValueError:
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_minutes
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> TokenPayload:
    raw = jwt.decode(
        token, settings.secret_key, algorithms=[settings.algorithm]
    )
    return TokenPayload(**raw)
```

### 11.10.2 `app/deps.py`

```python
# app/deps.py
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/login", auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "토큰이 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exc

    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise credentials_exc

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exc
    return user


async def get_optional_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(oauth2_scheme_optional),
) -> User | None:
    """토큰이 없으면 None, 있으면 검증해서 사용자를 돌려준다."""
    if token is None:
        return None
    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        return None
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        return None
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user
```

> **`OAuth2PasswordBearer(auto_error=False)`** 가 핵심입니다. 기본값(`auto_error=True`)은 토큰이 없으면 자동으로 401을 던집니다. `False`로 두면 토큰 자리에 `None`을 넘겨주기만 합니다 — 우리가 직접 분기 처리할 수 있습니다. 공개 글 목록처럼 "비로그인도 200으로 응답하되 로그인 사용자는 추가 정보를 보여 주는" 라우트에서 자주 씁니다.

---

## 11.11 인증 라우트 — `app/routers/auth.py`

08장과 거의 동일합니다. `name` 필드가 추가된 점만 다릅니다.

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    email = payload.email.lower()
    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(409, "이미 사용 중인 이메일입니다")

    try:
        hashed = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(422, str(e))

    user = User(email=email, hashed_password=hashed, name=payload.name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    email = form.username.lower()
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            401, "이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            401, "비활성화된 계정입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(subject=str(user.id)))


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
```

### 11.11.1 정보 누설 방지

로그인 실패 응답이 항상 같은 메시지("이메일 또는 비밀번호가 올바르지 않습니다")인 점을 다시 강조합니다. **"이 이메일은 등록되어 있다"**는 사실을 공격자에게 흘리지 않기 위함입니다.

---

## 11.12 보조 모듈 — `app/crud.py`

라우트가 직접 ORM을 다루는 코드의 양을 줄이기 위해, 자주 쓰는 쿼리 빌더와 헬퍼를 한 파일에 모았습니다.

```python
# app/crud.py
from collections.abc import Sequence
from typing import Any

from slugify import slugify
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post, PostTag, Tag


# ── slug ──

async def make_unique_slug(session: AsyncSession, title: str) -> str:
    """제목으로부터 unique slug를 만든다."""
    base = slugify(title) or "post"
    candidate = base
    n = 2
    while True:
        existing = await session.execute(
            select(Post.id).where(Post.slug == candidate)
        )
        if existing.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"
        n += 1
        if n > 1000:
            raise RuntimeError("slug 후보 생성 한도 초과")


# ── tags ──

async def get_or_create_tags(
    session: AsyncSession, names: Sequence[str]
) -> list[Tag]:
    """이름 리스트를 받아 모두 Tag 인스턴스로 돌려준다(없으면 생성)."""
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in names:
        norm = raw.strip().lower()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        cleaned.append(norm)

    if not cleaned:
        return []

    result = await session.execute(select(Tag).where(Tag.name.in_(cleaned)))
    existing = list(result.scalars().all())
    by_name: dict[str, Tag] = {t.name: t for t in existing}

    new_tags: list[Tag] = []
    for name in cleaned:
        if name in by_name:
            continue
        tag = Tag(name=name, slug=slugify(name) or name)
        session.add(tag)
        new_tags.append(tag)
        by_name[name] = tag

    if new_tags:
        await session.flush()

    return [by_name[n] for n in cleaned]


# ── post 쿼리 빌더 ──

def base_post_query() -> Select[Any]:
    """본 SELECT — author·tags eager load."""
    return (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )


def base_count_query() -> Select[Any]:
    """카운트 전용 쿼리(eager 옵션은 무의미하므로 따로)."""
    return select(func.count(func.distinct(Post.id))).select_from(Post)


def apply_visibility(stmt: Select[Any], viewer_id: int | None) -> Select[Any]:
    if viewer_id is None:
        return stmt.where(Post.published.is_(True))
    return stmt.where(or_(Post.published.is_(True), Post.user_id == viewer_id))


def apply_search(stmt: Select[Any], q: str | None) -> Select[Any]:
    if not q:
        return stmt
    pattern = f"%{q}%"
    return stmt.where(or_(Post.title.like(pattern), Post.body.like(pattern)))


def apply_tag_filter(stmt: Select[Any], tag_name: str | None) -> Select[Any]:
    if not tag_name:
        return stmt
    norm = tag_name.strip().lower()
    return (
        stmt.join(PostTag, PostTag.post_id == Post.id)
        .join(Tag, Tag.id == PostTag.tag_id)
        .where(Tag.name == norm)
    )


def apply_sort(stmt: Select[Any], sort: str | None) -> Select[Any]:
    if sort == "created_at":
        return stmt.order_by(Post.created_at.asc(), Post.id.asc())
    return stmt.order_by(Post.created_at.desc(), Post.id.desc())


async def count_posts(session: AsyncSession, count_stmt: Select[Any]) -> int:
    result = await session.execute(count_stmt)
    return int(result.scalar_one())
```

### 11.12.1 함수 한 개씩 풀어 보기

- **`make_unique_slug`** — `python-slugify`로 영문·숫자·하이픈으로 정규화한 뒤, 같은 slug가 이미 있으면 `-2`, `-3`을 붙여 재시도합니다. 한국어만 있는 제목은 slug가 빈 문자열이 되므로 `"post"`를 기본으로 둡니다.
- **`get_or_create_tags`** — 입력의 strip + 소문자 정규화 + 중복 제거를 한 번에 처리합니다. DB에 이미 있는 태그는 SELECT로 가져오고, 없는 태그만 INSERT 큐에 올립니다. 같은 트랜잭션 안에서 `flush`로 PK를 채워 둔 뒤 입력 순서대로 정렬해 돌려줍니다.
- **`apply_*`** — `Select` 객체에 `.where`/`.join`을 누적해 돌려주는 빌더입니다. **본 쿼리와 카운트 쿼리에 같은 필터를 일관되게 적용**하기 위해 분리했습니다. 두 쿼리 모두 같은 `apply_*` 호출을 받습니다.
- **`base_count_query`** — `SELECT COUNT(DISTINCT posts.id)`를 만듭니다. `apply_tag_filter`가 JOIN을 끼면 같은 글이 여러 행으로 나타나므로 `DISTINCT`가 필요합니다.

> **왜 본 쿼리 / 카운트 쿼리를 따로 만드나요?** Eager loading 옵션(`selectinload`)은 카운트에 무의미하므로 분리해 두는 편이 빠르고, JOIN으로 행 수가 부풀어 오르는 효과를 카운트에서 정확히 다루려면 `DISTINCT`가 필요합니다.

---

## 11.13 글 라우트 — `app/routers/posts.py`

여러 기능이 한 라우트에 모이는 절입니다. 한 단계씩 봅니다.

### 11.13.1 전체 코드

```python
# app/routers/posts.py
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import (
    apply_search, apply_sort, apply_tag_filter, apply_visibility,
    base_count_query, base_post_query, count_posts,
    get_or_create_tags, make_unique_slug,
)
from app.db import get_session
from app.deps import get_current_user, get_optional_user
from app.models import Post, User
from app.schemas import PostCreate, PostList, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


def _post_visible_to(post: Post, viewer: User | None) -> bool:
    if post.published:
        return True
    return viewer is not None and post.user_id == viewer.id


# ── 목록 ──

@router.get("", response_model=PostList)
async def list_posts(
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    tag: str | None = Query(None),
    sort: str | None = Query(None),
) -> PostList:
    viewer_id = viewer.id if viewer is not None else None

    # 1) 카운트
    count_stmt = base_count_query()
    count_stmt = apply_visibility(count_stmt, viewer_id)
    count_stmt = apply_search(count_stmt, q)
    count_stmt = apply_tag_filter(count_stmt, tag)
    total = await count_posts(session, count_stmt)

    # 2) 본 SELECT
    stmt = base_post_query()
    stmt = apply_visibility(stmt, viewer_id)
    stmt = apply_search(stmt, q)
    stmt = apply_tag_filter(stmt, tag)
    stmt = apply_sort(stmt, sort)
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await session.execute(stmt)
    posts = list(result.unique().scalars().all())
    items = [PostRead.model_validate(p) for p in posts]
    return PostList(items=items, page=page, size=size, total=total)


# ── 단건 ──

@router.get("/{post_id}", response_model=PostRead)
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
) -> Post:
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None or not _post_visible_to(post, viewer):
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")
    return post


# ── 작성 ──

@router.post("", response_model=PostRead, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    slug = await make_unique_slug(session, payload.title)
    now = datetime.now(timezone.utc)
    post = Post(
        user_id=current_user.id,
        title=payload.title,
        slug=slug,
        body=payload.body,
        published=payload.published,
        published_at=now if payload.published else None,
    )
    if payload.tags:
        post.tags = await get_or_create_tags(session, payload.tags)

    session.add(post)
    await session.commit()

    refreshed = await session.execute(
        select(Post).where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


# ── 수정 ──

@router.patch("/{post_id}", response_model=PostRead)
async def update_post(
    post_id: int,
    payload: PostUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    # tags 를 교체할 수 있으므로 처음부터 selectinload 로 함께 로드한다.
    # session.get() 만 쓰면 post.tags 가 lazy 상태라 비동기 컨텍스트 안에서
    # 재할당 시 MissingGreenlet 이 터진다.
    result = await session.execute(
        select(Post).where(Post.id == post_id)
        .options(selectinload(Post.tags))
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(403, "본인이 작성한 글만 수정할 수 있습니다")

    data = payload.model_dump(exclude_unset=True)
    if "title" in data:
        post.title = data["title"]
    if "body" in data:
        post.body = data["body"]
    if "published" in data:
        new_pub: bool = data["published"]
        if new_pub and not post.published:
            post.published_at = datetime.now(timezone.utc)
        post.published = new_pub
    if "tags" in data:
        post.tags = await get_or_create_tags(session, data["tags"] or [])

    await session.commit()

    refreshed = await session.execute(
        select(Post).where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


# ── 삭제 ──

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    # cascade="all, delete-orphan" 정책 때문에 session.delete(post) 가
    # 내부적으로 post.comments 를 훑어 본다. 비동기 컨텍스트에서 그 lazy load 는
    # MissingGreenlet 으로 터지므로, 처음부터 selectinload 로 함께 가져온다.
    # tags(N:M)도 같은 이유로 함께 로드한다.
    result = await session.execute(
        select(Post).where(Post.id == post_id)
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(403, "본인이 작성한 글만 삭제할 수 있습니다")
    await session.delete(post)
    await session.commit()


# ── 게시 토글 ──

@router.post("/{post_id}/publish", response_model=PostRead)
async def publish_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(403, "권한이 없습니다")

    if not post.published:
        post.published = True
        post.published_at = datetime.now(timezone.utc)
        await session.commit()

    refreshed = await session.execute(
        select(Post).where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


@router.post("/{post_id}/unpublish", response_model=PostRead)
async def unpublish_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(403, "권한이 없습니다")

    if post.published:
        post.published = False
        await session.commit()

    refreshed = await session.execute(
        select(Post).where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()
```

### 11.13.2 페이지네이션 한 줄 풀이

```python
stmt = stmt.offset((page - 1) * size).limit(size)
```

- **`page=1, size=20`** → OFFSET 0, LIMIT 20.
- **`page=3, size=20`** → OFFSET 40, LIMIT 20.
- 총개수(`total`)는 별도의 카운트 쿼리로 받아 응답의 메타데이터에 함께 실립니다.

> **OFFSET 페이지네이션의 한계** — `OFFSET 100000` 같은 큰 값은 DB가 그 만큼의 행을 건너뛰며 읽어야 해 매우 느려집니다. 큰 데이터에서는 **keyset(커서) 페이지네이션** — "마지막으로 본 created_at·id를 다음 호출에 넘겨 그보다 더 옛날 것을 가져와라" 식 — 이 표준입니다. 본 가이드는 단순한 OFFSET 방식만 다루고, 더 큰 규모로 가야 할 때 keyset를 도입하길 권합니다.

### 11.13.3 검색 — MySQL의 LIKE

```python
stmt.where(or_(Post.title.like(pattern), Post.body.like(pattern)))
```

`%keyword%` 모양의 LIKE는 단순하지만 **앞부분에 와일드카드가 있어 인덱스를 활용하지 못합니다**. 데이터가 적을 때는 충분하지만, 글 수가 수만 건이 되면 느려집니다.

> **MySQL FULLTEXT 인덱스로 단계 업** — `body` 같은 텍스트 컬럼에 `FULLTEXT` 인덱스를 만들고 `MATCH(body) AGAINST(?)`로 검색하면 자연어 검색이 빨라집니다. SQLAlchemy에서 raw SQL을 일부 섞어 쓰거나(`session.execute(text(...))`), 더 본격적으로는 Meilisearch / Elasticsearch / OpenSearch 같은 외부 검색엔진을 도입합니다. 이 가이드의 범위 밖이지만, 실서비스로 가기 전 한 번은 검토할 주제입니다.

### 11.13.4 태그 자동 생성과 N:M 연결

POST 본문의 `tags: ["python", "fastapi"]`가 라우트에 도달하면 흐름은 이렇습니다.

1. `get_or_create_tags(session, ["python", "fastapi"])` 호출.
2. 각 이름을 strip + 소문자 + 중복 제거.
3. DB에 있는 것은 SELECT로 가져오고, 없는 것만 새 Tag 인스턴스를 만든다.
4. `flush`로 PK를 채운다.
5. 라우트가 `post.tags = [...]` 한 줄로 N:M 연결을 표현한다 — SQLAlchemy가 알아서 `INSERT INTO post_tags`를 추가한다.

**이 한 흐름이 N:M의 일반적인 사용 패턴**입니다. PostTag 인스턴스를 직접 만들 일은 거의 없습니다.

---

## 11.14 댓글 라우트 — `app/routers/comments.py`

```python
# app/routers/comments.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user, get_optional_user
from app.models import Comment, Post, User
from app.schemas import CommentCreate, CommentRead, CommentUpdate

post_comments_router = APIRouter(prefix="/posts", tags=["comments"])
comments_router = APIRouter(prefix="/comments", tags=["comments"])


def _post_visible_to(post: Post, viewer: User | None) -> bool:
    if post.published:
        return True
    return viewer is not None and post.user_id == viewer.id


@post_comments_router.get("/{post_id}/comments", response_model=list[CommentRead])
async def list_comments(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
) -> list[Comment]:
    post = await session.get(Post, post_id)
    if post is None or not _post_visible_to(post, viewer):
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")

    result = await session.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    return list(result.scalars().all())


@post_comments_router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Comment:
    post = await session.get(Post, post_id)
    if post is None or not _post_visible_to(post, current_user):
        raise HTTPException(404, "해당 글을 찾을 수 없습니다")

    comment = Comment(post_id=post_id, user_id=current_user.id, body=payload.body)
    session.add(comment)
    await session.commit()

    result = await session.execute(
        select(Comment).where(Comment.id == comment.id)
        .options(selectinload(Comment.author))
    )
    return result.scalar_one()


@comments_router.patch("/{comment_id}", response_model=CommentRead)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Comment:
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, "해당 댓글을 찾을 수 없습니다")
    if comment.user_id != current_user.id:
        raise HTTPException(403, "본인이 작성한 댓글만 수정할 수 있습니다")
    comment.body = payload.body
    await session.commit()
    result = await session.execute(
        select(Comment).where(Comment.id == comment.id)
        .options(selectinload(Comment.author))
    )
    return result.scalar_one()


@comments_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, "해당 댓글을 찾을 수 없습니다")
    if comment.user_id != current_user.id:
        raise HTTPException(403, "본인이 작성한 댓글만 삭제할 수 있습니다")
    await session.delete(comment)
    await session.commit()
```

> **두 라우터를 분리한 이유** — 댓글 목록·작성은 글 ID에 종속이라 `/posts/{post_id}/comments` 아래에 두는 게 자연스럽고, 단건 수정·삭제는 글 ID 없이도 가능하니 `/comments/{comment_id}` 단독 경로가 깔끔합니다. 두 `APIRouter` 인스턴스를 만들고 `main.py`에서 둘 다 `include_router`합니다.

---

## 11.15 태그 라우트 — `app/routers/tags.py`

가장 간단합니다.

```python
# app/routers/tags.py
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Tag
from app.schemas import TagSummary

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagSummary])
async def list_tags(
    session: AsyncSession = Depends(get_session),
) -> list[Tag]:
    result = await session.execute(select(Tag).order_by(Tag.name.asc()))
    return list(result.scalars().all())
```

---

## 11.15.5 빈 `__init__.py` 들 (놓치기 쉬운 한 단계)

본문이 `app/`, `app/routers/`, `tests/` 폴더의 파일들을 한 단계씩 채워 왔습니다. 다음 11.16 의 `from app.routers import auth as auth_router` 같은 import 가 안정적으로 동작하려면 각 폴더에 빈 `__init__.py` 가 있어야 합니다(테스트 디스커버리도 마찬가지). 아직 안 만들었다면 한 번에:

```bash
mkdir -p app/routers tests
touch app/__init__.py app/routers/__init__.py tests/__init__.py
```

> Python 3.3+ 의 implicit namespace package 덕분에 빈 파일이 없어도 동작은 하지만, 일관된 패키지 인식·테스트 import·IDE 자동완성을 위해 명시적으로 두는 것을 권장합니다.

---

## 11.16 앱 조립 — `app/main.py`

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth as auth_router
from app.routers import comments as comments_router_module
from app.routers import posts as posts_router
from app.routers import tags as tags_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blog API",
        description=(
            "11장 — 종합 예제. User · Post · Comment · Tag (1:N, N:M) + "
            "JWT 인증 + MySQL."
        ),
        version="0.1.0",
    )

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

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

이 시점에서 모든 코드가 맞물려 있어야 `uv run uvicorn app.main:app --reload`로 서버가 떠야 합니다.

```bash
uv run uvicorn app.main:app --reload
```

브라우저로 `http://127.0.0.1:8000/docs`를 열면 Swagger UI에 우리 모든 엔드포인트가 자동 등록되어 있습니다. **"Authorize"** 버튼을 누르고 회원가입한 계정으로 로그인하면 자물쇠 마크가 풀리고 보호된 라우트도 직접 시험할 수 있습니다.

---

## 11.17 테스트 — `tests/conftest.py`와 `tests/test_blog.py`

운영은 MySQL이지만, 테스트는 **인메모리 SQLite**로 빠르게 돕니다. SQLAlchemy 2.0의 ORM 코드는 두 DB에서 동일하게 동작합니다.

### 11.17.0 `pyproject.toml` 의 pytest 설정

비동기 테스트가 자동 인식되도록 `pyproject.toml` 에 다음 한 블록을 둡니다(예제 폴더는 이미 들어 있습니다).

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- `asyncio_mode = "auto"` — `async def test_...` 함수가 자동으로 비동기 테스트로 인식. 없으면 데코레이터(`@pytest.mark.asyncio`)를 매 함수마다 붙여야 합니다.
- `testpaths = ["tests"]` — `pytest` 한 줄로 `tests/` 만 디스커버.

### 11.17.1 `tests/conftest.py`

```python
# tests/conftest.py
from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession, async_sessionmaker, create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app


@pytest_asyncio.fixture
async def _engine_and_factory():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine, SessionLocal
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(_engine_and_factory) -> AsyncIterator[AsyncSession]:
    _engine, SessionLocal = _engine_and_factory
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(_engine_and_factory) -> AsyncIterator[AsyncClient]:
    _engine, SessionLocal = _engine_and_factory

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
def alice_payload() -> dict[str, str]:
    return {"email": "alice@example.com", "password": "hunter22hunter", "name": "Alice"}


@pytest.fixture
def bob_payload() -> dict[str, str]:
    return {"email": "bob@example.com", "password": "anothersecret77", "name": "Bob"}


@pytest_asyncio.fixture
async def alice_token(client: AsyncClient, alice_payload: dict[str, str]) -> str:
    r = await client.post("/auth/signup", json=alice_payload)
    assert r.status_code == 201
    r = await client.post(
        "/auth/login",
        data={"username": alice_payload["email"], "password": alice_payload["password"]},
    )
    assert r.status_code == 200
    return str(r.json()["access_token"])


@pytest_asyncio.fixture
async def bob_token(client: AsyncClient, bob_payload: dict[str, str]) -> str:
    r = await client.post("/auth/signup", json=bob_payload)
    assert r.status_code == 201
    r = await client.post(
        "/auth/login",
        data={"username": bob_payload["email"], "password": bob_payload["password"]},
    )
    assert r.status_code == 200
    return str(r.json()["access_token"])
```

핵심 트릭은 **`StaticPool`** 입니다. 인메모리 SQLite는 같은 파일 핸들 = 같은 DB이므로, 여러 세션이 같은 DB를 보려면 단일 연결을 공유해야 합니다.

### 11.17.2 `tests/test_blog.py` (요약)

전체 코드는 예제 폴더의 `tests/test_blog.py`를 보시고, 여기서는 카테고리만 표로 정리합니다(총 10 케이스).

| # | 테스트 | 검증 포인트 |
|---|--------|-------------|
| 1 | `test_signup_login_me` | 정상 흐름, 응답에 `hashed_password` 미포함 |
| 2 | `test_create_and_list_posts_with_search_and_tag_filter` | 페이지네이션·검색·태그 필터 |
| 3 | `test_draft_invisible_to_anonymous_visible_to_owner` | 비공개 글 가시성 |
| 4 | `test_cannot_modify_others_post` | 인가 — 남의 글 수정·삭제 불가 |
| 5 | `test_publish_unpublish_toggle` | 게시 상태 토글 |
| 6 | `test_comment_crud_and_authorization` | 댓글 CRUD + 인가 |
| 7 | `test_tag_dedup_and_normalization` | 태그 자동 생성·정규화·중복 제거 |
| 8 | `test_post_tags_replace` | PATCH로 태그 전체 교체 |
| 9 | `test_delete_post_cascades_comments_and_tags` | 글 삭제 시 댓글·태그 cascade (lazy load 회귀 방지) |
| 10 | `test_health` | 헬스체크 |

실행:

```bash
uv run pytest -v
```

---

## 11.18 Docker / Docker Compose

### 11.18.1 `Dockerfile` (멀티스테이지)

```dockerfile
# Dockerfile
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# 작성 시점 안정 태그. 새 마이너 출시 시 직접 갱신.
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /usr/local/bin/

WORKDIR /app

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# 비루트 사용자로 실행해 권한 사고를 줄인다(컨테이너 탈출 취약점 시 호스트 root 와의 거리).
RUN groupadd --system app && \
    useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app
COPY --from=builder /app /app
RUN chown -R app:app /app
USER app

EXPOSE 8000

# Uvicorn 자체 멀티워커(0.30+ 내장). `gunicorn -k uvicorn.workers.UvicornWorker`
# 패턴은 deprecated 되어 별도 패키지(`uvicorn-worker`)로 분리되었습니다.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
```

> **멀티스테이지 빌드란?** 한 Dockerfile 안에 여러 빌드 단계를 두고, 마지막 단계에 필요한 결과물만 가져가는 방식입니다. 빌드 도구(uv, 컴파일러 등)는 최종 이미지에 들어가지 않아 이미지 크기가 작아지고, 보안 표면도 줄어듭니다.

### 11.18.2 `docker-compose.yml`

```yaml
# docker-compose.yml
services:
  db:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: blog_api
      MYSQL_USER: blog_user
      MYSQL_PASSWORD: blog_pass
      MYSQL_ROOT_PASSWORD: root_pass
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-uroot", "-proot_pass"]
      interval: 5s
      timeout: 3s
      retries: 20

  migrate:
    build: .
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: "mysql+asyncmy://blog_user:blog_pass@db:3306/blog_api"
      SECRET_KEY: "${SECRET_KEY:-dev-only-change-me}"
    command: ["alembic", "upgrade", "head"]

  app:
    build: .
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: "mysql+asyncmy://blog_user:blog_pass@db:3306/blog_api"
      SECRET_KEY: "${SECRET_KEY:-dev-only-change-me}"
      ALGORITHM: "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES: "60"
    ports:
      - "8000:8000"
    command:
      - "uvicorn"
      - "app.main:app"
      - "--host"
      - "0.0.0.0"
      - "--port"
      - "8000"
      - "--reload"
    volumes:
      - ./app:/app/app
      - ./alembic:/app/alembic
      - ./alembic.ini:/app/alembic.ini

volumes:
  mysql-data:
```

### 11.18.3 사용 흐름

```bash
# 1) 환경 변수 준비
cp .env.example .env
# .env의 SECRET_KEY를 강한 난수로 교체

# 2) MySQL만 먼저
docker compose up -d db

# 3) 마이그레이션 한 번
docker compose run --rm migrate

# 4) 앱 띄우기 (foreground; --reload 활성)
docker compose up app
```

`http://127.0.0.1:8000/docs`를 열면 됩니다.

> **`docker compose run --rm` 의 의미** — 일회성 컨테이너로 명령을 실행하고, 끝나면 자동으로 컨테이너를 지웁니다(`--rm`). 마이그레이션처럼 한 번 실행하고 끝나는 작업에 적합합니다.

---

## 11.19 N+1 문제 — 같은 함정, 같은 해결책

### 11.19.1 N+1이란

```python
# 안 좋은 예 — 코드가 두 줄이지만 실제로는 N+1번 쿼리
posts = (await session.execute(select(Post))).scalars().all()
for p in posts:
    print(p.author.name)   # ← 매 글마다 SELECT users WHERE id=...
```

위 코드는 다음과 같이 동작합니다.

1. `SELECT * FROM posts` → 1번
2. 첫 글의 `author`에 접근 → `SELECT * FROM users WHERE id=?` 1번
3. 두 번째 글의 `author`에 접근 → 또 1번
4. ... 글이 N개면 사용자 조회 N번

총 **N+1번 쿼리**가 나갑니다. 글이 100건이면 101번. DB 한 번 왕복에 1ms만 잡아도 100ms가 추가로 들고, 트래픽이 늘면 DB가 먼저 무너집니다.

### 11.19.2 `selectinload`로 한 번에 가져오기

```python
from sqlalchemy.orm import selectinload

stmt = (
    select(Post)
    .options(selectinload(Post.author), selectinload(Post.tags))
)
result = await session.execute(stmt)
posts = result.scalars().all()
for p in posts:
    print(p.author.name)   # 추가 쿼리 없음
```

`selectinload(Post.author)`는 SQLAlchemy에게 "Post들을 가져오고 나서, 그들의 `author`도 한 번에 가져와 달라"고 알려줍니다. 결과적으로 다음 두 SQL이 나갑니다.

```sql
-- 1) 본 SELECT
SELECT * FROM posts WHERE published = TRUE ORDER BY created_at DESC LIMIT 20;

-- 2) author 한 번에 모아오기
SELECT * FROM users WHERE id IN (1, 2, 3, ..., 20);
```

**N+1번이 2번**으로 줄어듭니다. tags처럼 N:M에 대해서도 같은 방식이 통합니다.

### 11.19.3 `selectinload` vs `joinedload`

| 옵션 | 어떻게 동작 | 언제 쓰면 좋은가 |
|------|-------------|-------------------|
| **`selectinload(Rel)`** | 본 쿼리 따로 + IN 쿼리 따로 | N:M, 1:N, 또는 결과 행 수가 많은 1:1 |
| **`joinedload(Rel)`** | LEFT JOIN으로 한 SQL에 합침 | 1:1 또는 작은 1:N |

`joinedload`는 한 번에 끝나서 좋아 보이지만, 1:N에서 부모 행이 자식 수만큼 곱해져 데이터가 부풀어 오르고 페이지네이션이 까다로워집니다. **이 가이드의 목록 라우트는 `selectinload`만 씁니다.**

### 11.19.4 의심될 때는 `echo=True`로 SQL을 본다

`app/db.py`의 엔진 생성 시 `echo=True`로 두면 모든 SQL이 콘솔에 찍힙니다. 한 요청에 SQL이 비정상적으로 많이 나가는지 가장 빠르게 확인할 수 있습니다. 학습용·디버깅용으로 잠깐만 켰다가 끄세요(운영 로그가 너무 시끄러워집니다).

```python
engine = create_async_engine(settings.database_url, echo=True)
```

---

## 11.20 페이지네이션 — OFFSET vs Keyset

### 11.20.1 OFFSET 방식 (이 가이드의 기본)

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 40;
```

장점:
- 단순. `page`, `size` 두 파라미터로 끝.
- 어느 페이지든 직접 점프 가능.

단점:
- `OFFSET 100000`처럼 큰 값에서 매우 느림(앞쪽 100,000행을 모두 읽어야 함).
- 동시에 새 글이 들어오면 페이지가 어긋남(같은 글이 두 페이지에 보이거나 누락).

이 챕터의 목록 라우트는 **OFFSET 방식**입니다. 일반 블로그 트래픽이면 충분합니다.

### 11.20.2 Keyset(=Cursor) 방식 (대용량용)

```sql
-- 첫 호출
SELECT * FROM posts ORDER BY created_at DESC, id DESC LIMIT 20;
-- 마지막 항목의 (created_at, id)를 기억

-- 두 번째 호출
SELECT * FROM posts
 WHERE (created_at, id) < (?, ?)   -- 마지막에 본 값
 ORDER BY created_at DESC, id DESC
 LIMIT 20;
```

장점:
- OFFSET이 0이라 항상 빠름(인덱스 활용).
- 페이지 어긋남 없음.

단점:
- "5페이지로 점프" 같은 임의 점프가 어렵다(=무한 스크롤 UX와 잘 맞음).
- 정렬 조합이 복잡해지면 WHERE 절이 커짐.

본 가이드는 OFFSET만 다루고, 큰 데이터로 가야 할 때 Keyset를 추가하라고만 안내합니다.

---

## 11.21 검색 — LIKE에서 시작해 어디까지

### 11.21.1 가장 단순한 LIKE

```python
stmt.where(or_(Post.title.like(pattern), Post.body.like(pattern)))
```

- `%foo%` 패턴은 인덱스를 못 씁니다(앞쪽 와일드카드 때문).
- 대소문자 — MySQL은 기본 collation에 따라 케이스 인센서티브일 수 있고 아닐 수도 있습니다(`utf8mb4_general_ci` 기준이면 인센서티브).

### 11.21.2 다음 단계 — MySQL FULLTEXT

> **FULLTEXT 인덱스로 한 단계 업** — 텍스트 컬럼 두 개에 대한 자연어 검색을 인덱스로 가속합니다.
>
> 1. 인덱스 만들기(마이그레이션에 추가):
>    ```sql
>    ALTER TABLE posts ADD FULLTEXT idx_posts_fts (title, body);
>    ```
> 2. 검색 쿼리:
>    ```sql
>    SELECT * FROM posts WHERE MATCH(title, body) AGAINST (?);
>    ```
> 3. SQLAlchemy에서:
>    ```python
>    from sqlalchemy import text
>    result = await session.execute(
>        text("SELECT * FROM posts WHERE MATCH(title, body) AGAINST (:q)"),
>        {"q": q},
>    )
>    ```
>
> InnoDB의 FULLTEXT는 한국어 형태소 분석은 못 하므로, 진지한 한국어 검색이 필요하면 **Meilisearch / Elasticsearch / OpenSearch** 같은 외부 검색엔진을 별도로 띄워야 합니다.

### 11.21.3 검색 결과의 정확도와 정렬

LIKE는 "포함만 하면 매치"라 정렬에 점수 개념이 없습니다. 운영 단계에서 검색 품질이 중요해지면 외부 엔진을 도입하면서 동시에 "title 매치는 가산점, body 매치는 일반점" 같은 가중치도 함께 설계합니다.

---

## 11.22 보안 — 자기 글만 수정·삭제, 공개와 비공개의 분리

11장의 인가는 두 가지 단순한 규칙으로 요약됩니다.

1. **수정·삭제는 본인만** — 라우트에서 `if post.user_id != current_user.id: 403`.
2. **비공개 글은 작성자만** — `_post_visible_to(post, viewer)`로 분기.

### 11.22.1 "존재하지 않는 듯이" 숨기기

비공개 글 단건 조회에서 우리는 권한이 없으면 **403이 아닌 404**를 반환합니다.

```python
if post is None or not _post_visible_to(post, viewer):
    raise HTTPException(404, "해당 글을 찾을 수 없습니다")
```

이는 "그 글이 존재한다"는 사실을 외부에 알리지 않기 위함입니다. 403이면 "있긴 한데 못 보여 준다"는 정보를 흘리지만, 404면 "있는지 없는지 모른다"가 됩니다. 작은 차이지만 사용자가 비공개로 둔 글의 존재 여부를 다른 사람이 알지 못하게 하는 한 가지 방법입니다.

### 11.22.2 한편 수정·삭제는 403

수정·삭제는 보통 글 ID를 직접 손에 든 경우(예: 본인이 만든 뒤 누군가에게 ID를 공유)라서, **권한 없음**을 명시적으로 알리는 편이 디버깅에 도움이 됩니다. 그래서 403을 씁니다. 두 케이스에서 코드 차이를 일관되게 유지하세요.

### 11.22.3 토큰만 보낸다고 끝이 아니다

자기 글이라는 검증은 **로그인된 사용자 ID == 글의 user_id** 한 줄로 끝납니다. 토큰이 유효하다고 해서 모든 글에 대한 권한이 자동으로 주어지지 않는다는 점이 중요합니다. 인증(AuthN)과 인가(AuthZ)는 다른 단계라는 8장의 가르침이 그대로 통합니다.

---

## 11.23 흔한 실수와 함정

이 챕터를 따라가다 자주 막히는 자리들입니다. 미리 짚어 둡니다.

### 11.23.1 모델 import 누락

`alembic/env.py`에 `import app.models`가 없으면 `Base.metadata`가 비어 있습니다. autogenerate 결과가 빈 마이그레이션이 됩니다. 이 한 줄을 잊지 마세요.

### 11.23.2 외래 키와 cascade의 두 층

`relationship(cascade=...)`는 ORM 레벨, `ForeignKey(ondelete=...)`는 DB 레벨. **두 층을 모두 두는 것이 안전**합니다. 한쪽만 두면 경로(예: SQL 직접 실행)에 따라 고아 행이 남을 수 있습니다.

### 11.23.3 N+1을 모르고 짠 첫 코드

처음 응답이 200으로 잘 나가는 듯해도, 글이 많아지면 갑자기 느려집니다. **목록 라우트는 항상 `selectinload`로 관계를 미리 로드**하는 습관을 들이세요. 11.19.

### 11.23.4 `tags=[]`와 "tags 키가 아예 없음"의 구분

`PostUpdate`의 `tags`를 처리할 때, `model_dump(exclude_unset=True)` 결과에 `"tags"` 키가 있는지로 분기합니다. `[]`가 들어 있으면 모든 태그 제거, 키 자체가 없으면 변경하지 않음.

### 11.23.5 페이지네이션의 `total`이 부풀어 오를 때

`apply_tag_filter`처럼 JOIN을 끼는 카운트는 `DISTINCT(posts.id)`를 세어야 부풀음을 막습니다. 본 가이드의 `base_count_query`가 이 패턴입니다.

### 11.23.6 비밀번호 길이 함정

Bcrypt는 입력의 첫 72바이트만 사용합니다. 한국어는 글자당 3바이트. 24글자 근처에서 잘림이 시작합니다. `hash_password`의 사전 검증을 빠뜨리면 "긴 한국어 비번 일부를 바꿔도 로그인이 통과되는" 헷갈리는 버그가 됩니다.

### 11.23.7 타임존 naive datetime

`datetime.now()`는 timezone-aware가 아닙니다. JWT의 `exp`/`iat`는 항상 `datetime.now(timezone.utc)`로. DB의 `DateTime(timezone=True)` 컬럼도 timezone-aware 값으로 저장하세요.

### 11.23.8 `.env`를 git에 커밋

처음 푸시하기 전에 `git status`로 한 번 확인. `.gitignore`에 `.env`가 들어 있는지 체크.

### 11.23.9 응답에 `hashed_password` 노출

`UserRead` 같은 응답 스키마에는 절대 `hashed_password`를 넣지 마세요. ORM 모델을 그대로 직렬화하면 모든 컬럼이 새 나갑니다. **응답은 항상 명시적인 Pydantic 모델로**.

### 11.23.10 `OAuth2PasswordBearer(tokenUrl=...)` 경로 불일치

`tokenUrl`이 실제 로그인 라우트와 정확히 같아야 Swagger UI의 Authorize 버튼이 동작합니다. 본 가이드는 `/auth/login`으로 통일합니다.

---

## 11.24 직접 호출해 보기 — curl 시나리오

### 11.24.1 회원가입 + 로그인

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"hunter22hunter","name":"Alice"}'

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=hunter22hunter" | jq -r .access_token)
echo $TOKEN
```

> **`jq` 가 없을 때** — 다음 한 줄을 그대로 쓸 수 있습니다(`jq -r .access_token` 자리에).
> ```bash
> python -c "import sys,json;print(json.load(sys.stdin)['access_token'])"
> ```

### 11.24.2 글 작성 + 태그

```bash
curl -X POST http://127.0.0.1:8000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title":"Hello FastAPI",
    "body":"FastAPI로 시작하는 백엔드.",
    "published": true,
    "tags": ["python","fastapi"]
  }'
```

응답:

```json
{
  "id": 1,
  "title": "Hello FastAPI",
  "slug": "hello-fastapi",
  "body": "FastAPI로 시작하는 백엔드.",
  "published": true,
  "published_at": "2026-04-25T10:00:00+00:00",
  "created_at": "2026-04-25T10:00:00+00:00",
  "updated_at": "2026-04-25T10:00:00+00:00",
  "author": {"id": 1, "name": "Alice"},
  "tags": [
    {"id": 1, "name": "python", "slug": "python"},
    {"id": 2, "name": "fastapi", "slug": "fastapi"}
  ]
}
```

### 11.24.3 비공개 글

```bash
curl -X POST http://127.0.0.1:8000/posts \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"draft","body":"...","published": false}'
```

### 11.24.4 비로그인 목록

```bash
curl "http://127.0.0.1:8000/posts?page=1&size=10"
# 공개 글만 나옴
```

태그 필터·검색:

```bash
curl "http://127.0.0.1:8000/posts?tag=python"
curl "http://127.0.0.1:8000/posts?q=FastAPI"
```

### 11.24.5 댓글

다른 사람으로 회원가입 → 로그인 → 댓글:

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"anothersecret77","name":"Bob"}'

TOKEN2=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=bob@example.com&password=anothersecret77" | jq -r .access_token)

POST_ID=1
curl -X POST "http://127.0.0.1:8000/posts/$POST_ID/comments" \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"body":"좋은 글이네요!"}'

curl "http://127.0.0.1:8000/posts/$POST_ID/comments"
```

### 11.24.6 권한 검증

다른 사람의 글을 수정해 보면 403:

```bash
curl -i -X PATCH "http://127.0.0.1:8000/posts/$POST_ID" \
  -H "Authorization: Bearer $TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{"title":"hijack"}'
# HTTP/1.1 403 Forbidden
```

---

## 11.25 배포 — Render·Fly.io·Ubuntu 짧게

09장 배포 가이드를 압축해 핵심만 정리합니다. 자세한 절차는 그 챕터를 참고하세요.

### 11.25.1 공통 준비

- **HTTPS 필수**: JWT가 평문으로 헤더에 실리므로, 인터넷에 노출되는 순간 HTTPS가 필수입니다.
- **`SECRET_KEY` 강한 난수**로 교체. `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- **DB 비밀번호 운영용**으로 변경. `docker-compose.yml`의 기본값은 개발용입니다.
- **CORS `allow_origins`** 를 실제 프런트엔드 도메인 목록으로 명시. `["*"]`은 학습용.
- **로그 회전** + **DB 정기 백업** + **모니터링**.

### 11.25.2 Render

- **MySQL은 별도 호스팅 또는 Render의 Private Service**(Render 자체는 PostgreSQL이 더 강함). MySQL을 외부에 둘 거면 PlanetScale·Aiven·AWS RDS 등을 검토.
- 앱은 **Web Service**로 배포. 빌드 명령은 `uv sync --frozen --no-dev`, 시작 명령은 `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2 --proxy-headers --forwarded-allow-ips='*'`.
- 환경 변수에 `DATABASE_URL`, `SECRET_KEY` 입력.
- 마이그레이션은 **Job** 또는 배포 스크립트에서 `alembic upgrade head`.

### 11.25.3 Fly.io

- `fly launch`로 시작. MySQL은 별도 외부 서비스를 가리키도록 `DATABASE_URL` 시크릿 등록.
- 앱 자체는 같은 Dockerfile을 그대로 사용.
- HTTPS는 자동.

### 11.25.4 Ubuntu 서버 직접

09장의 절차를 압축하면 다음과 같습니다.

```bash
# Ubuntu에서
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 코드 업로드 (rsync 또는 git)
rsync -avz --exclude '.venv' --exclude '__pycache__' ./ ubuntu@SERVER:/home/ubuntu/blog-api/

# 서버에서
cd /home/ubuntu/blog-api
cp .env.example .env
nano .env       # SECRET_KEY, MySQL 비번 강하게 교체
docker compose --env-file .env build
docker compose --env-file .env up -d db
docker compose --env-file .env run --rm migrate
docker compose --env-file .env up -d app
```

nginx 리버스 프록시 + Let's Encrypt:

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo nano /etc/nginx/sites-available/blog-api
# server { listen 80; server_name api.example.com;
#   location / { proxy_pass http://127.0.0.1:8000; ... } }
sudo ln -s /etc/nginx/sites-available/blog-api /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.example.com
```

확인:

```bash
curl https://api.example.com/health
# {"status":"ok"}
```

### 11.25.5 운영 체크리스트

- [ ] `.env`가 서버에 있고 git에는 없다
- [ ] HTTPS 적용 (Let's Encrypt 또는 PaaS 자동 TLS)
- [ ] MySQL 포트(3306)는 외부 공개 금지(컨테이너 내부 통신만)
- [ ] DB 정기 백업 (`mysqldump` 크론)
- [ ] 로그 회전 (`docker run --log-opt max-size=10m --log-opt max-file=3` 등)
- [ ] 모니터링 (UptimeRobot, Datadog 등)

---

## 11.26 다음 단계로 — 개선 아이디어

이 챕터의 코드를 베이스로 다음을 시도해 보세요. 모두 실서비스에서 흔한 기능입니다.

- **갱신 토큰(refresh token)** — 짧은 액세스 토큰 + 긴 갱신 토큰 패턴(8장 부록 참고).
- **본인 글의 비공개 포함 목록** — `/posts/me?include_drafts=true` 등.
- **좋아요 / 즐겨찾기** — `User × Post` N:M 추가.
- **팔로우 기능** — `User × User` 자기참조 N:M.
- **알림** — 댓글 시 글 작성자에게 행 추가.
- **이미지 업로드** — `multipart/form-data` 처리, S3 / Cloudflare R2 업로드.
- **검색 강화** — FULLTEXT 또는 외부 검색엔진(Meilisearch).
- **Keyset 페이지네이션** — 무한 스크롤 UX와 큰 데이터 모두에 유리.
- **API 버저닝** — `/api/v1/...`, `/api/v2/...` 분리.
- **WebSocket 실시간 댓글 알림** — FastAPI의 WebSocket 지원 활용.
- **OpenAPI 스펙 별도 배포** — 프런트엔드에 자동 클라이언트 생성기 도입.

---

## 11.27 전체 체크리스트

이 챕터를 다 마쳤는지 한 번에 점검하는 표입니다.

- [ ] `uv add fastapi "uvicorn[standard]" "gunicorn>=23" "sqlalchemy[asyncio]>=2.0" alembic asyncmy aiosqlite pyjwt bcrypt python-slugify python-multipart pydantic-settings "pydantic[email]"` 설치 완료
- [ ] Docker로 MySQL 8.4 컨테이너 띄움
- [ ] `.env` 작성 완료 (`SECRET_KEY`는 `secrets.token_urlsafe(48)` 결과로 교체)
- [ ] `app/config.py`, `app/db.py` 작성
- [ ] `app/models.py` — User · Post · Comment · Tag · PostTag 다섯 모델 + N:M 관계
- [ ] `app/schemas.py` — 입출력 스키마 + AuthorSummary, TagSummary, PostList
- [ ] `alembic/env.py` 비동기 + `import app.models`
- [ ] `alembic/versions/0001_initial.py` 작성 후 `uv run alembic upgrade head`
- [ ] `app/security.py` — bcrypt + JWT
- [ ] `app/deps.py` — `get_current_user`, `get_optional_user`
- [ ] `app/crud.py` — slug, 태그 자동 생성, 검색·필터·카운트 빌더
- [ ] `app/routers/auth.py`, `posts.py`, `comments.py`, `tags.py`
- [ ] `app/main.py`로 라우터 등록 + CORS + `/health`
- [ ] `tests/conftest.py` + `tests/test_blog.py` (10 케이스 통과)
- [ ] `Dockerfile` + `docker-compose.yml` 작성, `docker compose up`로 실행 확인
- [ ] Swagger UI(`/docs`)에서 회원가입 → 로그인 → 보호된 라우트 호출
- [ ] 운영 환경에 HTTPS 적용 (Let's Encrypt 또는 PaaS)

---

## 11.28 이 챕터 요약

- User · Post · Comment · Tag(+ PostTag) 다섯 모델로 **1:N · N:M 관계**를 모두 다뤘다.
- `relationship` + `back_populates`로 양방향 관계를, `secondary="post_tags"`로 N:M을 표현했다.
- `ondelete="CASCADE"`(DB 레벨)와 `cascade="all, delete-orphan"`(ORM 레벨)을 함께 두어 부모 삭제 시 자식이 따라 사라지게 했다.
- **MySQL + asyncmy** 비동기 드라이버로 운영 DB를 구성하고, 테스트는 인메모리 SQLite로 빠르게 돌렸다 — 같은 ORM 코드가 두 DB에서 모두 통한다는 SQLAlchemy의 강점을 활용.
- 페이지네이션(OFFSET/LIMIT) + 검색(LIKE) + 태그 필터(JOIN) + 정렬을 한 라우트에 합쳤고, **본 SELECT와 카운트 SELECT를 분리**해 정확한 `total`을 만들었다.
- 글 작성 시 `tags: ["python","fastapi"]`를 받아 **태그 자동 생성·정규화·중복 제거**를 거쳐 N:M으로 연결했다.
- **N+1 문제**를 인식하고 `selectinload`로 두 SELECT로 평탄화했다.
- 공개·비공개 글을 라우트 단에서 **`get_optional_user`** 와 `_post_visible_to`로 분기했다. 비공개 글의 존재 여부는 외부에 흘리지 않도록 일관되게 404로 응답.
- 자기 글·자기 댓글만 수정·삭제하는 **단순한 인가 규칙**을 코드로 한 줄씩 표현했다.
- Docker / Docker Compose로 앱·DB·마이그레이션을 한 명령으로 띄웠고, Render·Fly.io·Ubuntu 어디든 같은 이미지로 올릴 수 있다.
- 운영 체크리스트(HTTPS, 비밀키 회전, 백업, 로그 회전, 모니터링)를 점검했다.
- 다음 단계로 **갱신 토큰, 좋아요·팔로우, 검색 강화(FULLTEXT/Meilisearch), Keyset 페이지네이션** 등 흔한 확장 방향을 짚었다.

---

← [10. 종합 예제 1 — Note API](10-project-note-api.md) | 다음 문서로 이동: **[12. 유틸리티 및 라이브러리 →](12-utilities.md)**
