# 10. 종합 예제 1 — Note API (처음부터 따라하기)

> **이 챕터의 목표**
> - 앞 챕터를 한 줄도 읽지 않은 독자도 **이 한 문서만** 따라하면 끝까지 가는 자기완결적 가이드를 만든다.
> - **회원가입 → 로그인 → JWT 발급 → 개인 메모 CRUD**까지 갖춘 작은 실전 REST API를 백지에서 완성한다.
> - 운영 환경의 실제 모양에 가깝게 **PostgreSQL + Docker Compose**로 개발하고, 같은 코드를 **Docker 이미지**로 묶어 띄운다.
> - 다른 사용자의 메모를 만지는 사고가 **구조적으로 불가능한** 라우트 패턴을 손에 익힌다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 6 ~ 10시간 (처음이면 하루~이틀, 같은 흐름이 익숙하면 한 번에 끝)

> **만들 것**: "내 메모만 쓰고 읽을 수 있는" 작은 백엔드. 스마트폰 메모 앱의 서버 부분이라고 생각하면 됩니다.

> **사용 스택**: Python 3.13 / FastAPI 0.115+ / Pydantic 2.x / SQLAlchemy 2.0 (async) + Alembic / PyJWT / **bcrypt 직접 사용** / PostgreSQL + Docker Compose / Uvicorn(개발) + Gunicorn(운영) / **uv**

> **참고**: 03~09장에서 다룬 내용 중 일부를 일부러 다시 짚습니다. 한 챕터만 봐도 실행되는 결과물이 손에 남도록 작성했기 때문입니다. 이미 익숙한 부분은 빠르게 넘기셔도 됩니다.

---

## 10.1 무엇을 만들 것인가

### 10.1.1 한 문장 요약

> 사용자가 회원가입과 로그인을 거쳐 **자기 메모만** 만들고, 목록을 보고, 수정·삭제할 수 있는 REST API를 만든다.

### 10.1.2 기능 요구사항

- **인증**
  - 이메일 + 비밀번호로 회원가입.
  - 로그인 → JWT 액세스 토큰 발급.
- **메모(Note) CRUD**
  - 생성: 제목, 본문, 태그(선택).
  - 목록: 본인 메모만, 페이지네이션, 태그 필터, 키워드 검색(제목·본문 부분 일치).
  - 단건 조회 / 부분 수정(PATCH) / 삭제.
- **보안**
  - 비밀번호는 절대 평문 저장 금지 — Bcrypt 해싱.
  - 모든 메모 라우트는 본인 소유 검사를 강제한다.
  - 다른 사용자의 메모 접근 시도는 **404 Not Found**로 응답한다(403이 아니다).
- **운영**
  - PostgreSQL을 Docker로 띄워 개발한다.
  - 앱도 Docker 이미지로 묶어, `docker compose up` 한 줄로 통째로 실행 가능.
  - 헬스 체크(`GET /health`) 한 줄.

### 10.1.3 엔드포인트 설계

| 메서드 | 경로 | 인증 | 성공 코드 | 한 줄 설명 |
|--------|------|------|-----------|------------|
| `POST` | `/auth/signup` | — | 201 | 회원가입 |
| `POST` | `/auth/login` | — | 200 | 로그인 (form: `username`=이메일, `password`) |
| `POST` | `/notes` | Bearer | 201 | 메모 생성 |
| `GET` | `/notes` | Bearer | 200 | 내 메모 목록(skip/limit/tag/search) |
| `GET` | `/notes/{note_id}` | Bearer | 200 | 단건 조회 (본인 소유만) |
| `PATCH` | `/notes/{note_id}` | Bearer | 200 | 부분 수정 (본인 소유만) |
| `DELETE` | `/notes/{note_id}` | Bearer | 204 | 삭제 (본인 소유만) |
| `GET` | `/health` | — | 200 | 헬스 체크 |

> **이 표가 10장의 모든 작업 목록입니다.** 8개의 엔드포인트, 두 개의 모델(User, Note), 한 개의 1:N 관계. 처음에는 적어 보이지만, "보안 + 본인 소유 검사 + 검색 + 페이지네이션 + 마이그레이션 + Docker"까지 들어가면 실전 백엔드의 첫 번째 모습으로 충분합니다.

### 10.1.4 흐름 한 그림

```
[클라이언트]                              [FastAPI 앱]                   [PostgreSQL]
     │                                        │                                │
     │ POST /auth/signup {email, password} ─▶ │                                │
     │                                        │  bcrypt.hashpw                 │
     │                                        │  INSERT user ────────────────▶ │
     │ ◀── 201 {id, email, ...} ─────────────  │                                │
     │                                        │                                │
     │ POST /auth/login (form) ──────────────▶ │                                │
     │                                        │  SELECT user                   │
     │                                        │  ◀────────────────────────────  │
     │                                        │  bcrypt.checkpw                │
     │                                        │  jwt.encode (HS256, exp 60분)  │
     │ ◀── 200 {access_token: "..."} ────────  │                                │
     │                                        │                                │
     │ POST /notes  Authorization: Bearer ──▶ │                                │
     │                                        │  jwt.decode → sub(user_id)     │
     │                                        │  INSERT note (user_id=...) ──▶ │
     │ ◀── 201 {id, title, body, ...} ───────  │                                │
     │                                        │                                │
     │ GET /notes/42  (다른 유저의 메모) ────▶ │                                │
     │                                        │  WHERE id=42 AND user_id=ME    │
     │                                        │  ◀── 결과 없음                  │
     │ ◀── 404 Not Found ────────────────────  │                                │
```

### 10.1.5 표준 프로젝트 구조

이 챕터의 결과물 폴더는 다음과 같이 생기게 됩니다.

```
10-NoteAPI/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml      # app + postgres
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial.py # users + notes
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI + CORS + 라우터 + /health
│   ├── config.py           # pydantic-settings
│   ├── db.py               # AsyncEngine, sessionmaker, get_session
│   ├── models.py           # User, Note (User 1:N Note)
│   ├── schemas.py          # User/Auth/Note Pydantic 모델
│   ├── security.py         # bcrypt + PyJWT
│   ├── deps.py             # get_current_user, get_current_active_user
│   ├── crud.py             # 서비스 레이어 (DB 작업)
│   └── routers/
│       ├── __init__.py
│       ├── auth.py         # /auth/signup, /auth/login
│       └── notes.py        # /notes 전체
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_notes.py
```

각 파일의 한 줄 정의를 미리 표로 정리해 둡니다.

| 파일 | 한 줄 책임 |
|------|----------|
| `app/main.py` | FastAPI 앱을 만들고 미들웨어와 라우터를 등록 |
| `app/config.py` | `.env` 환경 변수를 한 객체(`Settings`)로 모은다 |
| `app/db.py` | 비동기 엔진, 세션 팩토리, `Base`, `get_session` 의존성 |
| `app/models.py` | ORM 모델 — User, Note (1:N 관계) |
| `app/schemas.py` | 요청/응답 Pydantic 스키마 |
| `app/security.py` | 비밀번호 해싱·검증, JWT 발급·검증 (bcrypt + PyJWT) |
| `app/deps.py` | `get_current_user`, `get_current_active_user` |
| `app/crud.py` | DB 작업만 모인 서비스 레이어 (본인 소유 검사 포함) |
| `app/routers/auth.py` | `/auth/signup`, `/auth/login` |
| `app/routers/notes.py` | `/notes` 전체 — 본인 소유 검사 강제 |
| `alembic/env.py` | 비동기 엔진으로 마이그레이션을 실행 |
| `alembic/versions/0001_initial.py` | `users`, `notes` 두 표를 만드는 첫 마이그레이션 |
| `Dockerfile` | 멀티 스테이지 + 비루트 사용자 컨테이너 빌드 |
| `docker-compose.yml` | `db`(Postgres) + `app` 두 서비스 |
| `tests/conftest.py` | 인메모리 SQLite + 의존성 오버라이드 |
| `tests/test_notes.py` | 회원가입→로그인→메모 CRUD + 본인 소유 검사 |

이 표가 곧 우리의 작업 순서이기도 합니다. 위에서 아래로 한 파일씩 만들어 갑니다.

---

## 10.2 사전 준비

### 10.2.1 필요한 도구

- **Python 3.13 이상** — `python3.13 --version`이 통하면 OK.
- **uv** — `uv --version`. (없으면 `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Docker Desktop**(또는 같은 역할의 도구) — `docker --version`, `docker compose version`. PostgreSQL을 컨테이너로 띄울 거라 필요합니다.
- (선택) `curl` 또는 [HTTPie](https://httpie.io/), `jq` — 본문 예시는 `curl`을 씁니다. `jq`는 토큰 추출에서 한 번 등장하지만 없어도 손으로 복사·붙여넣기 가능합니다.

> **uv가 뭔가요?** 가상환경 생성·라이브러리 설치·잠금 파일 관리를 한 번에 해주는 차세대 도구입니다. 옛날 `pip` + `venv` + `pip-tools`의 일을 한 도구로 묶었고, 같은 일을 10~100배 빠르게 합니다. 본 가이드의 표준이며, 자세한 설치는 [03장 설치 가이드](03-installation.md)를 참고하세요.

> **Docker Compose란?** 여러 컨테이너(우리 경우엔 `app` + `db`)를 한 YAML 파일로 묶어 한 번에 띄우는 도구입니다. 개발 환경에서 매우 유용합니다. Docker Desktop이 깔려 있으면 `docker compose` 명령이 함께 들어옵니다.

> **왜 PostgreSQL인가?** 운영 환경에서 가장 표준적인 오픈소스 RDBMS입니다. 같은 SQLAlchemy 코드는 SQLite·MySQL에서도 동작하지만, 이 챕터는 운영의 모양에 더 가까워지기 위해 처음부터 PG를 씁니다. (테스트는 빠른 피드백을 위해 인메모리 SQLite를 씁니다 — 10.13에서 다룸.)

### 10.2.2 환경 점검 한 줄씩

```bash
python3.13 --version          # Python 3.13.x
uv --version                  # uv 0.4.x 이상
docker --version              # Docker version 27 정도
docker compose version        # Docker Compose version v2.x
```

위 네 명령이 모두 깨끗한 버전을 출력하면 다음 절로 넘어갑니다.

> **Windows를 쓰신다면** WSL2(Ubuntu) 안에서 작업하시는 것을 권장합니다. 본문 명령은 macOS/Linux 셸 기준입니다. 자세한 안내는 [03장](03-installation.md#3-5-windows--wsl2-한-단락-안내) 참고.

---

## 10.3 프로젝트 만들기 (`uv init` + 의존성)

### 10.3.1 폴더 만들고 uv로 초기화

작업 폴더는 어디든 좋습니다. 본 가이드는 홈 아래 `projects/`를 가정합니다.

```bash
mkdir -p ~/projects/10-NoteAPI
cd ~/projects/10-NoteAPI

uv init --no-readme           # uv가 만드는 hello.py / main.py는 곧 지울 거라 README는 안 만든다
rm -f hello.py main.py        # uv init이 만든 샘플 스크립트 정리
```

### 10.3.2 의존성 한 번에 추가

```bash
uv add fastapi "uvicorn[standard]" gunicorn \
       "sqlalchemy[asyncio]" alembic asyncpg aiosqlite \
       "pydantic[email]" pydantic-settings \
       pyjwt bcrypt python-multipart
uv add --dev pytest pytest-asyncio httpx
```

각 라이브러리의 역할 한 줄씩:

| 묶음 | 라이브러리 | 역할 |
|------|------------|------|
| 웹 | `fastapi` | 본체 프레임워크 |
| | `uvicorn[standard]` | 개발용 ASGI 서버 |
| | `gunicorn` | 운영용 프로세스 매니저 |
| DB | `sqlalchemy[asyncio]` | ORM (2.x async — `asyncio` extras 가 `greenlet` 까지 함께 깐다) |
| | `alembic` | 마이그레이션 도구 |
| | `asyncpg` | PostgreSQL 비동기 드라이버 |
| | `aiosqlite` | (테스트용) SQLite 비동기 드라이버 |
| 검증 | `pydantic[email]` | 요청/응답 검증 + 이메일 검증 |
| | `pydantic-settings` | `.env` 로딩 |
| 인증 | `pyjwt` | JWT 발급/검증 |
| | `bcrypt` | 비밀번호 해싱 (직접 사용) |
| 테스트 | `pytest`, `pytest-asyncio`, `httpx` | 통합 테스트 |

> **`uvicorn[standard]`의 대괄호?** "추가 옵션 묶음"입니다. `[standard]`로 받으면 자동 리로드용 `watchfiles`, JSON 로깅용 부가 라이브러리가 함께 깔립니다.

> **`pydantic[email]`?** 이메일 검증(`EmailStr`)에 필요한 부가 의존성(`email-validator`)까지 함께 깐다는 뜻입니다.

> **`bcrypt`만 쓰고 `passlib`은 안 쓰나요?** 네. 본 가이드의 약속입니다. 함수가 두 개뿐인 `bcrypt`를 직접 쓰는 쪽이 입문자에게 가장 단순하고 디버깅이 쉽습니다. 자세한 이유는 [08장 8.3.4](08-authentication.md)를 참고하세요.

설치가 끝나면 폴더에 다음이 생깁니다.

- `pyproject.toml` — 의존성 목록과 메타데이터
- `uv.lock` — 정확한 버전을 못 박은 잠금 파일 (다른 컴퓨터에서 `uv sync`로 똑같이 복원)
- `.venv/` — 가상환경 (이 폴더는 git에 올리지 않음)
- `.python-version` — Python 3.13

> **빈 `__init__.py` 들을 만들어 둡니다** — 10.1.5 트리에 표시된 `app/__init__.py`, `app/routers/__init__.py`, `tests/__init__.py` 세 개의 빈 파일을 지금 만들어 두세요. 본문이 한 단계씩 코드를 채워가는 동안 import 경로와 pytest 디스커버리가 안정적으로 동작합니다.
>
> ```bash
> mkdir -p app/routers tests
> touch app/__init__.py app/routers/__init__.py tests/__init__.py
> ```

### 10.3.3 `.gitignore`와 `.env.example`

`.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/

# 가상환경
.venv/
venv/

# 환경 변수 파일 (절대 커밋 금지)
.env
.env.local
.env.*.local

# SQLite (테스트용 임시 파일)
*.db
*.sqlite
*.sqlite3

# Docker 볼륨/로컬
postgres-data/

# 에디터 / OS
.vscode/
.idea/
.DS_Store
```

`.env.example`:

```bash
# DB 접속 URL — PostgreSQL + asyncpg
DATABASE_URL=postgresql+asyncpg://note_user:note_pass@localhost:5432/note_api

# JWT 서명에 쓰는 비밀키 — 운영에서는 반드시 강한 난수로!
# 32바이트 미만이면 PyJWT 가 InsecureKeyLengthWarning 을 띄웁니다.
SECRET_KEY=please-change-this-to-32-bytes-or-longer-random-string

ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

CORS_ALLOW_ORIGINS=*
```

> **왜 `.env`가 아니라 `.env.example`을 git에 두는가?** 진짜 비밀값(DB 비번, JWT 시크릿)은 절대 git에 올리지 않습니다. 그래서 `.env`는 `.gitignore`에 등록해 두고, "변수 이름과 의미만 적은" `.env.example`을 협업의 가이드로 둡니다. 새 팀원은 이 파일을 복사해 자기 환경에 맞춰 채웁니다.

당장 `.env`도 만들어 둡니다. `SECRET_KEY`는 한 줄 파이썬 명령으로 만들어 채웁니다.

```bash
cp .env.example .env

python -c "import secrets; print(secrets.token_urlsafe(48))"
# 출력값을 .env의 SECRET_KEY 자리에 붙여넣기
```

> **`secrets.token_urlsafe(n)`이란?** Python 표준 라이브러리의 `secrets` 모듈이 만드는 보안용 난수입니다. URL-safe 문자(영문·숫자·`-`·`_`)로 구성된 충분히 강한 비밀 값을 한 줄로 생성합니다. 48바이트면 Base64로 64자 정도가 나옵니다.

---

## 10.4 PostgreSQL을 Docker Compose로 띄우기

### 10.4.1 왜 Docker로?

로컬에 PostgreSQL을 직접 깔아도 됩니다(`brew install postgresql@17`). 하지만 다음 이점이 큽니다.

- **격리**: 호스트 OS를 더럽히지 않습니다. `docker compose down -v` 한 줄로 깨끗이 지웁니다.
- **버전 고정**: `postgres:17-alpine` 이미지를 고정하면 팀 전체가 같은 버전을 씁니다.
- **운영과 같은 모양**: 운영 환경도 보통 컨테이너로 띄우므로, 처음부터 같은 모양에서 학습하는 게 편합니다.

### 10.4.2 첫 `docker-compose.yml`

프로젝트 루트에 `docker-compose.yml`을 만들고 다음을 넣습니다. (앱 컨테이너는 10.15에서 추가합니다 — 일단 DB만.)

```yaml
services:
  db:
    image: postgres:17-alpine
    container_name: note-api-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: note_api
      POSTGRES_USER: note_user
      POSTGRES_PASSWORD: note_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U note_user -d note_api"]
      interval: 5s
      timeout: 5s
      retries: 10

volumes:
  postgres-data:
```

각 줄의 의미:

- **`image: postgres:17-alpine`** — 가벼운 Alpine 기반의 PostgreSQL 17.
- **`environment.POSTGRES_*`** — 컨테이너가 처음 떴을 때 만들 DB 이름·계정·비밀번호.
- **`ports: "5432:5432"`** — 호스트(=내 노트북)의 5432가 컨테이너의 5432에 묶입니다. 우리 앱이 `localhost:5432`로 접속할 수 있게 됩니다.
- **`volumes: postgres-data:/var/lib/postgresql/data`** — 명명된 볼륨에 데이터를 저장. 컨테이너를 지워도 데이터는 살아남습니다(`docker volume rm note-api_postgres-data`로 명시적으로 지우면 사라짐).
- **`healthcheck`** — `pg_isready`로 "연결 가능한 상태"를 주기적으로 확인합니다. `app` 서비스가 나중에 추가될 때 `condition: service_healthy`로 의존시키기 위함입니다.

> **`postgres:17-alpine` vs 그냥 `postgres:17`?** 알파인은 더 가벼운 베이스 이미지를 씁니다(약 80MB vs 400MB). 학습용으로는 알파인이 다운로드도 빠르고 디스크도 덜 먹어서 권장합니다.

> **5432 포트가 이미 사용 중이라고 나오면?** 다른 PostgreSQL이 떠 있다는 뜻입니다. `lsof -i :5432`로 누가 쓰는지 확인하고 끄거나, 본 docker-compose의 포트를 `"55432:5432"`로 바꾼 뒤 `.env`의 `DATABASE_URL` 포트도 `55432`로 맞추세요.

### 10.4.3 띄우고 확인

```bash
docker compose up -d db
# Creating volume "10-noteapi_postgres-data" with default driver
# Pulling db (postgres:17-alpine)... 
# Creating note-api-db ... done

docker compose ps
# NAME           STATUS              PORTS
# note-api-db    Up (healthy)        0.0.0.0:5432->5432/tcp
```

`Up (healthy)`가 되려면 5~15초 정도 걸립니다. 그 전에 마이그레이션을 돌리면 `connection refused`가 날 수 있으니 잠깐 기다립니다.

직접 들어가 보고 싶다면:

```bash
docker compose exec db psql -U note_user -d note_api -c "\l"
# 데이터베이스 목록이 출력됨
```

> **`-d` 플래그?** "detached" 모드. 백그라운드로 띄우고 셸을 돌려받습니다. 끄고 싶을 때는 `docker compose down`(데이터 유지) 또는 `docker compose down -v`(볼륨까지 삭제).

---

## 10.5 `app/config.py` — 설정 한 객체로 모으기

설정을 가장 먼저 만듭니다. 다른 모듈이 `from app.config import get_settings`로 가져다 쓸 단일 진입점입니다.

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

    # ── DB ───────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://note_user:note_pass@localhost:5432/note_api"
    )

    # ── JWT ──────────────────────────────────────────
    # PyJWT 2.x 의 InsecureKeyLengthWarning(<32바이트) 회피용 32바이트 이상 더미.
    # 운영에서는 .env로 반드시 강한 난수를 주입한다.
    secret_key: str = "please-change-this-to-32-bytes-or-longer-random-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── CORS ─────────────────────────────────────────
    cors_allow_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        raw = self.cors_allow_origins.strip()
        if raw == "" or raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

세 가지 포인트만 짚습니다.

1. **클래스 속성 = 환경 변수 이름** — `database_url` 속성은 `DATABASE_URL` 환경 변수와 자동 매핑됩니다. `case_sensitive=False`로 대소문자 무시.
2. **기본값** — `.env`가 없어도 곧장 동작하도록 합리적인 기본값을 둡니다. 단, `secret_key`는 운영에서 반드시 교체.
3. **`@lru_cache`** — 함수가 여러 번 호출돼도 같은 인스턴스를 반환합니다. 환경 변수를 매번 새로 파싱하지 않게 합니다.

> **왜 환경 변수로 빼는가?** "코드는 한 번 쓰지만 환경(개발 / 테스트 / 운영)은 여러 개"이기 때문입니다. 같은 코드가 환경마다 다른 DB·다른 시크릿을 바라봐야 합니다. 환경 변수로 빼두면 코드를 안 고치고 환경만 바꿔치울 수 있습니다(이 원칙을 [12-Factor App](https://12factor.net/ko/)이라고 부릅니다).

---

## 10.6 `app/db.py` — 비동기 엔진과 세션 의존성

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

engine = create_async_engine(settings.database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """모든 ORM 모델 클래스의 부모. SQLAlchemy 2.0의 declarative 베이스."""


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session
```

각 부분의 의미는 [06장 6.6](06-sqlalchemy-database.md)에서 자세히 다뤘습니다. 핵심만 다시 짚습니다.

- **`Base`는 단 하나만**. `models.py`의 모든 모델이 이걸 상속합니다.
- **`engine`도 단 하나만 만든다.** 엔진은 안에 커넥션 풀을 들고 있는 비싼 객체라 매번 새로 만들면 안 됩니다.
- **`expire_on_commit=False`** — `commit()` 후에도 객체 속성에 접근할 수 있게 합니다. 비동기 컨텍스트의 응답 직렬화 단계에서 lazy load가 일어나 에러가 나는 일을 막아 줍니다.
- **`get_session`**은 의존성 함수. `Depends(get_session)`으로 라우터가 받습니다. `async with`가 끝날 때 세션이 자동으로 닫힙니다.

---

## 10.7 `app/models.py` — User와 Note (1:N 관계)

```python
# app/models.py
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    notes: Mapped[list["Note"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(10_000), nullable=False)
    tag: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="notes")
```

세 가지 핵심 디자인 결정을 짚습니다.

### 10.7.1 외래 키와 cascade

`Note.user_id`는 `users.id`를 가리키는 외래 키이며, **`ondelete="CASCADE"`**로 두었습니다.

> **외래 키(Foreign Key)란?** 다른 테이블의 PK를 가리키는 열입니다. "이 메모의 작성자는 사용자 테이블의 그 사용자"라는 연결을 표현합니다. DB는 잘못된 FK 값(존재하지 않는 user)이 들어오는 것을 자동으로 막습니다.

> **CASCADE란?** "부모(User)가 사라지면 자식(Note)도 함께 사라진다"는 정책입니다. 회원이 탈퇴하면 그 사람의 메모를 별도로 정리할 필요가 없습니다. (만약 메모를 보존하고 싶으면 `SET NULL`을 쓰는데, 이 경우 메모의 작성자가 NULL이 되도록 모델을 바꿔야 함.)

### 10.7.2 `index=True`로 인덱스 명시

`User.email`과 `Note.user_id`에 `index=True`를 줬습니다.

- `email`은 로그인할 때 매 요청마다 검색되므로 인덱스가 필수.
- `user_id`는 "내 메모만" 조회를 위해 매 요청마다 `WHERE user_id = ME`로 거를 거라 인덱스가 큰 효과를 냅니다.

> **인덱스(index)란?** "이 값이 어느 행에 있는지"를 미리 정리해 둔 자료구조입니다. 책의 색인을 떠올리면 됩니다. 검색을 매우 빠르게 하지만, 디스크를 더 쓰고 INSERT/UPDATE 시 인덱스도 함께 갱신해야 해 살짝 느려집니다. 자주 검색하는 열에만 만드는 게 원칙입니다.

### 10.7.3 1:N 관계 — `relationship` 양쪽

User에는 `notes: list[Note]`, Note에는 `user: User`. 이 양쪽이 `back_populates`로 연결되어 있어, 한 쪽을 갱신하면 다른 쪽도 일관되게 보입니다.

> **이 챕터는 라우트 안에서 `user.notes`를 직접 사용하지 않습니다.** 대신 `crud.list_notes(user_id=...)`처럼 user_id를 직접 쿼리에 넣는 방식을 택했습니다. 그게 본인 소유 검사 패턴(10.11)과 잘 맞기 때문입니다. 11장 Blog API에서는 양방향 관계를 더 본격적으로 활용합니다.

---

## 10.8 `app/schemas.py` — 요청/응답 스키마

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── User ────────────────────────────────────────────────────


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


# ── Auth ────────────────────────────────────────────────────


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    iat: int
    exp: int


# ── Note ────────────────────────────────────────────────────


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)
    tag: str | None = Field(default=None, max_length=50)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=10_000)
    tag: str | None = Field(default=None, max_length=50)


class NoteRead(NoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class NotesPage(BaseModel):
    items: list[NoteRead]
    total: int
    skip: int
    limit: int
```

> **`from_attributes=True`란?** Pydantic이 "이 스키마는 dict뿐 아니라 일반 객체의 속성에서도 값을 읽어 만들 수 있다"는 표시입니다. 우리가 ORM에서 받아온 `User`/`Note` 인스턴스를 그대로 `NoteRead.model_validate(note)`로 변환하거나, FastAPI의 `response_model=NoteRead`에 그대로 넘길 수 있게 됩니다. (옛 Pydantic v1의 `orm_mode=True`와 같은 의미.)

> **`UserRead`에 `hashed_password`가 없는 게 핵심입니다.** ORM 모델에는 있지만 응답 스키마에는 절대 포함하지 않습니다. 이 한 가지 분리가 "비밀번호 해시가 응답으로 새 나가는" 사고를 막아 주는 첫 번째 방어선입니다.

> **`NoteUpdate`의 모든 필드가 Optional**인 이유: 부분 수정(PATCH)이라서. 클라이언트가 보낸 필드만 갱신하고 나머지는 그대로 두는 게 표준입니다. `crud.update_note`에서 `model_dump(exclude_unset=True)` 한 줄로 그 의미를 그대로 표현합니다.

---

## 10.9 Alembic 초기화와 첫 마이그레이션

### 10.9.1 알아둘 명령 세 개

| 명령 | 용도 |
|------|------|
| `uv run alembic init alembic` | 처음 한 번 — Alembic 폴더 골격 생성 |
| `uv run alembic revision --autogenerate -m "..."` | 새 마이그레이션 파일 만들기 |
| `uv run alembic upgrade head` | 미적용 마이그레이션을 모두 적용 |

> **마이그레이션(migration)이란?** DB의 표 구조 변경(열 추가, 새 표 만들기 등)을 코드 파일로 기록·실행하는 작업입니다. **Alembic**이 그 도구입니다. 변경 이력이 git에 함께 들어가, 어느 시점·어느 환경의 DB든 같은 순서로 같은 구조에 도달할 수 있습니다.

### 10.9.2 폴더 골격 생성

```bash
uv run alembic init alembic
```

다음 파일이 생깁니다.

- `alembic.ini` — Alembic 메인 설정.
- `alembic/env.py` — 마이그레이션 명령 실행 시 호출되는 부트스트랩 코드. **여기를 비동기에 맞게 손봐야 합니다.**
- `alembic/script.py.mako` — `alembic revision`이 새 파일을 만들 때 쓰는 템플릿.
- `alembic/versions/` — 실제 마이그레이션 파일이 들어갈 폴더.

### 10.9.3 `alembic.ini` 손보기

`sqlalchemy.url` 줄을 임의의 기본값으로 둡니다(어차피 `env.py`에서 우리 설정으로 덮어쓸 거라 큰 의미는 없습니다).

```ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://note_user:note_pass@localhost:5432/note_api
```

### 10.9.4 `alembic/env.py`를 비동기용으로 교체

`alembic init`이 만든 `env.py`는 동기 SQLAlchemy를 가정합니다. 우리 앱은 비동기 엔진을 쓰므로 통째로 다음 내용으로 바꿉니다.

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
import app.models  # noqa: F401  (모델을 import 해야 Base.metadata 에 등록됨)


config = context.config
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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

핵심 포인트만 짚습니다.

- **`from app import models` (`import app.models`)** — 모델을 import해야 `Base.metadata`에 등록됩니다. **이 한 줄을 빼면 autogenerate가 빈 마이그레이션을 만듭니다.**
- **`config.set_main_option("sqlalchemy.url", settings.database_url)`** — `.env`의 `DATABASE_URL`을 마이그레이션 명령에도 그대로 쓰게 합니다.
- **`async_engine_from_config(...)`** — 비동기 엔진을 만듭니다.
- **`await connection.run_sync(do_run_migrations)`** — Alembic 본체는 동기 함수만 받으므로, 비동기 connection 안에서 동기 함수를 실행시키는 다리 역할입니다.
- **`compare_type=True`** — autogenerate가 열의 타입 변경(예: VARCHAR(100)→VARCHAR(200))도 감지하게 합니다.

### 10.9.5 첫 마이그레이션 자동 생성

DB가 떠 있어야 합니다.

```bash
docker compose ps   # db 가 (healthy) 인지 확인
```

이제 첫 마이그레이션 파일을 자동 생성합니다.

```bash
uv run alembic revision --autogenerate -m "initial: create users and notes"
```

`alembic/versions/` 아래에 `<해시>_initial_create_users_and_notes.py` 같은 파일이 한 개 생깁니다. 한 번 열어서 `op.create_table("users", ...)`와 `op.create_table("notes", ...)`가 들어 있는지 확인하세요.

본 가이드의 예제 폴더는 보기 좋게 파일명을 **`0001_initial.py`**로 바꿔 두었습니다. 직접 따라하실 때 이름을 바꾸시려면 **파일을 열어 `revision = "..."` 변수도 함께 `0001_initial` 로 바꿔야** 본문의 출력 로그(`Running upgrade  -> 0001_initial, ...`)와 일치합니다(파일명만 바꾸면 hash 식별자가 그대로 남아 로그에 다른 식별자가 찍힙니다).

> **autogenerate가 자동으로 만들어 준 파일은 항상 한 번 읽어보세요.** 100% 정확하지 않습니다. 인덱스 이름, 제약조건, 데이터 마이그레이션 같은 부분은 손으로 보강해야 할 때가 있습니다. 본 챕터처럼 단순한 표 두 개는 거의 항상 그대로 동작합니다.

### 10.9.6 적용

```bash
uv run alembic upgrade head
```

성공 출력:

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, initial: create users and notes
```

확인:

```bash
docker compose exec db psql -U note_user -d note_api -c "\dt"
# users, notes, alembic_version 세 개의 표가 보여야 정상.
```

> **`alembic_version` 표** — Alembic이 "현재 어느 리비전까지 적용됐는지"를 기억하는 메타 표입니다. 사람이 직접 손대지 않습니다.

---

## 10.10 `app/security.py` — bcrypt + PyJWT

이 파일이 인증의 두뇌입니다. 비밀번호 해싱·검증, JWT 발급·검증의 네 함수가 모여 있습니다.

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
    hashed_bytes = bcrypt.hashpw(encoded, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


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
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )
    return TokenPayload(**raw)
```

함수 네 개의 책임이 명확합니다.

| 함수 | 책임 |
|------|------|
| `hash_password(plain) -> str` | 회원가입 시 평문 → 저장용 해시 문자열 |
| `verify_password(plain, hashed) -> bool` | 로그인 시 일치 여부만 |
| `create_access_token(subject) -> str` | 로그인 성공 시 토큰 발급 |
| `decode_access_token(token) -> TokenPayload` | 보호된 라우트에서 토큰 검증 |

### 10.10.1 Bcrypt 72바이트 함정 다시 짚기

[08장 8.4.5](08-authentication.md)에서 자세히 다룬 함정을 한 번 더 복기합니다.

> **Bcrypt는 입력의 첫 72바이트만 사용합니다.** 73바이트째부터는 무시되어 "긴 비밀번호 일부를 바꿔도 같다"는 헷갈리는 버그가 됩니다. **한국어는 UTF-8 기준 한 글자가 3바이트**라서 한국어 24글자만 넘어가도 잘림이 시작됩니다. 사용자가 24글자짜리 한국어 문장으로 비밀번호를 만들었는데 25번째 글자를 바꿔도 로그인이 통과되는, 매우 헷갈리는 버그가 가능합니다.

본 가이드의 해결책은 **사전에 길이 제한을 명시하고, 넘으면 `ValueError`를 던지는** 것입니다. `hash_password`의 첫 줄이 그 검사입니다. 회원가입 라우트(10.12)는 이 예외를 422로 변환합니다. Pydantic 스키마(`UserCreate.password: str = Field(max_length=64)`)에서 한 번, `hash_password`에서 한 번, 총 두 단계로 막힙니다.

### 10.10.2 JWT의 두 함수 — `encode` / `decode`

> **JWT 한 줄 정리** — 서버가 "당신이 누구인지"를 적고 자기 비밀키로 서명한 작은 문자열입니다. 클라이언트는 이 문자열을 들고 다니다가 요청마다 `Authorization: Bearer <토큰>` 헤더에 실어 보내고, 서버는 서명만 확인하면 누가 보낸 요청인지 알 수 있습니다. **DB 조회 없이도** 신원이 식별되어, 서버가 여러 대로 늘어나도 한 비밀키만 같으면 모두 검증할 수 있습니다.

`create_access_token`이 만들어내는 토큰의 페이로드는 다음 모양입니다.

```json
{
  "sub": "42",                        // 사용자 ID (subject)
  "iat": 1717000000,                  // 발급 시각 (Unix timestamp)
  "exp": 1717003600                   // 만료 시각 (60분 후)
}
```

`decode_access_token`은 두 가지 예외를 낼 수 있습니다.

- **`jwt.ExpiredSignatureError`** — 만료된 토큰.
- **`jwt.InvalidTokenError`** — 그 외 검증 실패(서명 불일치, 형식 오류, 알고리즘 불일치 등).

호출하는 쪽(`deps.py`)에서 두 예외를 분기해 401 응답을 다르게 줍니다.

> **`algorithms`는 반드시 리스트로 명시**: `jwt.decode(token, SECRET, algorithms=["HS256"])`. 이걸 비우거나 `"none"`을 포함시키면 위조 토큰이 통과하는 보안 사고가 발생할 수 있습니다.

> **`SECRET_KEY`는 절대 코드에 박지 말 것.** `.env`로 주입하고, `.env`는 git에 커밋하지 않습니다. 운영 환경은 클라우드 비밀 관리자(AWS Secrets Manager 등)나 컨테이너 오케스트레이터의 비밀 기능으로 환경 변수를 주입합니다.

---

## 10.11 `app/deps.py` — `get_current_user`, `get_current_active_user`

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
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exc

    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise credentials_exc

    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exc

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
```

### 10.11.1 의존성 사슬 한 그림

```
요청 헤더의 Authorization
        │
        ▼
oauth2_scheme  (OAuth2PasswordBearer)
        │  → "Bearer ..." 에서 토큰 문자열만 꺼냄
        ▼
get_current_user
        │  → 토큰 검증 + DB에서 사용자 조회
        ▼
get_current_active_user
        │  → 활성 계정 검사
        ▼
라우트 함수의 인자: current_user: User
```

각 단계는 함수이고, 다음 단계가 `Depends(...)`로 주입받습니다. **의존성 위에 의존성을 합성하는 패턴**은 FastAPI의 핵심입니다. 권한 검사가 더 복잡해져도(역할, 자원 소유 등) 같은 모양으로 확장됩니다.

### 10.11.2 `OAuth2PasswordBearer`라는 이름이 무서워 보이지만

> **`OAuth2PasswordBearer`는 단지 "`Authorization: Bearer ...` 헤더에서 토큰 문자열을 꺼내주는 의존성"입니다.** 우리가 만드는 백엔드는 진짜 OAuth2 서버가 아닙니다. 이 클래스가 빌려오는 건 두 가지뿐입니다 — Bearer 토큰 헤더 형식, 그리고 Swagger UI의 "Authorize" 버튼이 어디로 로그인 요청을 보낼지 알려주는 `tokenUrl` 메타데이터.

자세한 배경은 [08장 8.7](08-authentication.md)을 참고하세요.

---

## 10.12 `app/crud.py` — 서비스 레이어 (DB 작업만)

이 챕터의 가장 중요한 한 절입니다. **본인 소유 검사**를 이 레이어가 책임집니다.

```python
# app/crud.py
from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, User
from app.schemas import NoteCreate, NoteUpdate, UserCreate
from app.security import hash_password


# ── User ───────────────────────────────────────────────


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ── Note ───────────────────────────────────────────────


async def create_note(
    session: AsyncSession,
    *,
    user_id: int,
    payload: NoteCreate,
) -> Note:
    note = Note(
        title=payload.title,
        body=payload.body,
        tag=payload.tag,
        user_id=user_id,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def get_owned_note(
    session: AsyncSession,
    *,
    note_id: int,
    user_id: int,
) -> Note | None:
    """본인 소유 메모 한 건. 다른 사람 메모면 None."""
    stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_notes(
    session: AsyncSession,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    tag: str | None = None,
    search: str | None = None,
) -> tuple[Sequence[Note], int]:
    base = select(Note).where(Note.user_id == user_id)

    if tag is not None and tag.strip() != "":
        base = base.where(Note.tag == tag)

    if search is not None and search.strip() != "":
        like = f"%{search}%"
        base = base.where(or_(Note.title.ilike(like), Note.body.ilike(like)))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    page_stmt = base.order_by(Note.updated_at.desc()).offset(skip).limit(limit)
    items = (await session.execute(page_stmt)).scalars().all()

    return items, int(total)


async def update_note(
    session: AsyncSession,
    *,
    note: Note,
    payload: NoteUpdate,
) -> Note:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(note, key, value)

    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, *, note: Note) -> None:
    await session.delete(note)
    await session.commit()
```

### 10.12.1 본인 소유 검사를 쿼리에 박는다 — 핵심 패턴

`get_owned_note`의 `WHERE` 절을 다시 보세요.

```python
stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
```

**`note_id`가 일치하는 행이 있어도 `user_id`가 다르면 결과가 빈 채로 돌아옵니다.** 라우트는 결과가 None이면 단순히 404를 던집니다. 의도치 않게 다른 사람의 메모를 만지는 길이 **구조적으로 차단**됩니다.

같은 패턴이 `list_notes`에도 적용됩니다 — `select(Note).where(Note.user_id == user_id)`로 시작합니다. 사용자는 자기 메모만 본다는 것이 쿼리의 첫 줄에 박혀 있습니다.

### 10.12.2 왜 404를 돌려주나? — "권한 없음" 정보 누설 방지

> **다른 사용자의 메모에 접근 시도 → 403이 아니라 404로 응답합니다.**
>
> 이유: "권한 없음(403)"이라고 알려주면 "그 ID의 메모가 다른 누군가에게 존재한다"는 정보를 공격자에게 줍니다. 공격자는 1, 2, 3, ...로 증가하는 ID로 GET을 반복해 "어느 ID가 존재하는지" 알아낼 수 있게 됩니다.
>
> 그래서 표준 보안 관행은 **"권한 없음"과 "없음"을 같은 응답(404)으로 통일**하는 것입니다. 정상 사용자 입장에서는 어차피 자기가 만든 적 없는 메모에 접근하지 않으므로 차이를 못 느끼고, 공격자에게는 정보가 새지 않습니다.
>
> 같은 이유로 로그인 실패 메시지도 "사용자 없음"과 "비번 틀림"을 같은 메시지로 통일합니다(10.13). 정보 누설 방지는 인증·인가 코드 곳곳에서 일관되게 지켜야 합니다.

### 10.12.3 `model_dump(exclude_unset=True)`의 비밀

`update_note`의 핵심 한 줄.

```python
data = payload.model_dump(exclude_unset=True)
```

여기서 `exclude_unset=True`는 "**클라이언트가 명시적으로 보낸 필드만** dict로 변환"합니다. 보내지 않은 필드는 dict에서 빠집니다.

- 본문 `{"title":"X"}` → `data = {"title":"X"}` → title만 setattr.
- 본문 `{"tag":"work"}` → `data = {"tag":"work"}` → tag만.
- 본문 `{}` → `data = {}` → for 루프가 한 바퀴도 안 돌고 끝. 그대로.

이 한 줄이 PATCH의 본질을 그대로 표현합니다.

> **`exclude_none`을 쓰면 안 되나요?** `exclude_none=True`로 두면 클라이언트가 일부러 `null`을 보내 "이 필드를 None으로 만들고 싶다"고 한 의도까지 함께 사라집니다. 부분 수정의 의미가 어긋나죠. 우리가 원하는 건 "보냈냐 안 보냈냐"의 구분이지 "값이 None이냐 아니냐"가 아닙니다. **항상 `exclude_unset=True`** 입니다.

### 10.12.4 검색 — `ILIKE`로 부분 일치 (대소문자 무시)

```python
like = f"%{search}%"
base = base.where(or_(Note.title.ilike(like), Note.body.ilike(like)))
```

`ILIKE`는 PostgreSQL의 대소문자 무시 부분 일치 연산자입니다(MySQL/SQLite에는 단순 `LIKE`만 있고 콜레이션에 따라 동작이 다름). SQLAlchemy의 `.ilike(...)`는 PG에서는 `ILIKE`로, 다른 DB에서는 적절히 변환되어 나갑니다.

> **검색이 더 본격적으로 필요하면**: PostgreSQL의 [Full Text Search](https://www.postgresql.org/docs/current/textsearch.html)나 별도 검색 엔진(Elasticsearch, Meilisearch)을 도입합니다. 본 챕터는 `ILIKE`로 단순 부분 검색만 다룹니다.

---

## 10.13 `app/routers/auth.py` — 회원가입과 로그인

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    email = payload.email.lower()

    if await crud.get_user_by_email(session, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다",
        )

    try:
        user = await crud.create_user(
            session, UserCreate(email=email, password=payload.password)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    return user


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    email = form.username.lower()
    user = await crud.get_user_by_email(session, email)

    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)
```

세 가지 디테일을 짚습니다.

1. **이메일 정규화** — `.lower()`로 항상 소문자로 통일합니다. `Alice@Example.com`과 `alice@example.com`을 같은 사용자로 처리.
2. **두 단계 비밀번호 검증** — Pydantic 스키마의 `Field(min_length=8, max_length=64)`에서 한 번 막히고, 한국어 등으로 UTF-8 바이트가 72를 넘으면 `hash_password`의 `ValueError`에서 한 번 더 막힙니다. 두 번째는 422로 변환합니다.
3. **로그인 실패 메시지 통일** — "사용자 없음"과 "비번 틀림"을 같은 메시지로 묶었습니다. 공격자에게 "이 이메일은 가입돼 있다"는 정보를 주지 않기 위함입니다.

> **`OAuth2PasswordRequestForm`은 form-encoded** — JSON이 아닙니다. 클라이언트는 `Content-Type: application/x-www-form-urlencoded`로 `username=...&password=...` 형식을 보내야 합니다. 필드 이름이 `username`인 것은 OAuth2 표준이라 어쩔 수 없습니다 — 우리가 라우트 안에서 그것을 "이메일"로 해석하면 됩니다.

---

## 10.14 `app/routers/notes.py` — 메모 CRUD (본인 소유 강제)

```python
# app/routers/notes.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.deps import get_current_active_user
from app.models import User
from app.schemas import NoteCreate, NoteRead, NotesPage, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_note_endpoint(
    payload: NoteCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    note = await crud.create_note(
        session, user_id=current_user.id, payload=payload
    )
    return NoteRead.model_validate(note)


@router.get("", response_model=NotesPage)
async def list_notes_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tag: str | None = Query(None),
    search: str | None = Query(None),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NotesPage:
    items, total = await crud.list_notes(
        session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        tag=tag,
        search=search,
    )
    return NotesPage(
        items=[NoteRead.model_validate(n) for n in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{note_id}", response_model=NoteRead)
async def get_note_endpoint(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    return NoteRead.model_validate(note)


@router.patch("/{note_id}", response_model=NoteRead)
async def update_note_endpoint(
    note_id: int,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    updated = await crud.update_note(session, note=note, payload=payload)
    return NoteRead.model_validate(updated)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    await crud.delete_note(session, note=note)
```

### 10.14.1 모든 라우트가 같은 패턴

다섯 개 라우트가 모두 같은 모양을 갖습니다.

1. `current_user: User = Depends(get_current_active_user)` — 인증 + 활성 검사.
2. 단건/수정/삭제는 `crud.get_owned_note(...)`로 본인 소유만 가져온다 → None이면 404.
3. 모든 DB 작업은 `crud.*` 함수에 위임.
4. 응답은 `NoteRead.model_validate(note)`로 깨끗하게 직렬화.

라우트 한 함수가 평균 5~6줄입니다. 이게 의존성 주입과 서비스 레이어 분리의 힘입니다.

### 10.14.2 응답 코드 정리

| 라우트 | 정상 | 404 | 422 | 401 |
|--------|------|-----|-----|-----|
| `POST /notes` | 201 | — | 검증 실패 | 토큰 없음 |
| `GET /notes` | 200 | — | 잘못된 쿼리 | 토큰 없음 |
| `GET /notes/{id}` | 200 | 없음/타인 | — | 토큰 없음 |
| `PATCH /notes/{id}` | 200 | 없음/타인 | 검증 실패 | 토큰 없음 |
| `DELETE /notes/{id}` | **204** | 없음/타인 | — | 토큰 없음 |

> **204 No Content** — DELETE의 표준 성공 코드. 본문 없이 코드만 돌아옵니다. 라우트가 `None`을 반환하면 FastAPI가 알아서 빈 응답으로 만듭니다.

---

## 10.15 `app/main.py` — 앱 조립

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import auth as auth_router
from app.routers import notes as notes_router

settings = get_settings()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Note API",
        description="10장 종합 예제 — 회원가입·로그인·개인 메모 CRUD",
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(auth_router.router)
    app.include_router(notes_router.router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

세 줄짜리 정리:

- **`FastAPI(title=...)`** — 메타데이터. `/docs`에 그대로 표시됩니다.
- **`CORSMiddleware`** — 다른 도메인의 프론트엔드가 이 API를 부를 때 브라우저가 막지 않도록. 한 줄.
- **`include_router(...)`** — `/auth`와 `/notes` 라우트가 이 시점에 앱에 등록됩니다.
- **`/health`** — 운영 환경의 로드밸런서가 주기적으로 호출하는 헬스체크 한 줄.

> **`allow_origins=["*"]`와 `allow_credentials=True`는 동시에 쓰면 안 된다**는 말이 있는데 정확합니다. 자격 증명(쿠키·인증 헤더)을 보낼 때는 `*`이 아닌 명시적인 도메인을 적어야 브라우저가 받아줍니다. 운영에서는 `CORS_ALLOW_ORIGINS=https://my-frontend.example.com`처럼 정확한 값으로 둡시다.

---

## 10.16 직접 호출해보기 — curl로 손에 익히기

지금까지 만든 모든 파일이 한 번에 동작하는지 확인해 봅니다.

### 10.16.1 서버 띄우기

```bash
# DB가 떠 있어야 합니다
docker compose ps

# 마이그레이션이 적용되어 있어야 합니다(이미 했다면 건너뛰세요)
uv run alembic upgrade head

# 개발 서버
uv run uvicorn app.main:app --reload
```

성공 로그:

```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Application startup complete.
```

브라우저에서 `http://127.0.0.1:8000/docs`를 열면 자동 생성된 Swagger UI가 보입니다. 우측 상단의 **Authorize** 버튼이 곧 우리의 친구입니다.

### 10.16.2 헬스 체크

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

### 10.16.3 회원가입

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"alicepass1234"}'
```

응답(201):

```json
{
  "id": 1,
  "email": "alice@example.com",
  "is_active": true,
  "created_at": "2026-04-25T10:00:00+00:00"
}
```

> **응답에 `hashed_password`나 `password`가 안 나오는지 한 번 확인**해 주세요. 안 나오는 게 정상입니다. `UserRead` 스키마에 두 필드가 없기 때문입니다.

### 10.16.4 같은 이메일 다시 가입 → 409

```bash
curl -i -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"another1234"}'
# HTTP/1.1 409 Conflict
# {"detail":"이미 사용 중인 이메일입니다"}
```

### 10.16.5 로그인 → 토큰 발급

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=alicepass1234"
```

응답(200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

토큰을 변수에 저장합시다. (jq가 깔려 있다고 가정)

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=alicepass1234" | jq -r .access_token)
echo "$TOKEN"
```

### 10.16.6 메모 생성

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"첫 메모","body":"FastAPI 시작!","tag":"diary"}'
```

응답(201):

```json
{
  "title": "첫 메모",
  "body": "FastAPI 시작!",
  "tag": "diary",
  "id": 1,
  "created_at": "2026-04-25T10:05:00+00:00",
  "updated_at": "2026-04-25T10:05:00+00:00"
}
```

### 10.16.7 목록 / 검색 / 페이지네이션

```bash
# 기본
curl "http://127.0.0.1:8000/notes" \
  -H "Authorization: Bearer $TOKEN"

# 페이지네이션
curl "http://127.0.0.1:8000/notes?skip=0&limit=5" \
  -H "Authorization: Bearer $TOKEN"

# 태그 필터
curl "http://127.0.0.1:8000/notes?tag=diary" \
  -H "Authorization: Bearer $TOKEN"

# 키워드 검색
curl "http://127.0.0.1:8000/notes?search=시작" \
  -H "Authorization: Bearer $TOKEN"

# limit 위반은 자동 422
curl -i "http://127.0.0.1:8000/notes?limit=1000" \
  -H "Authorization: Bearer $TOKEN"
```

### 10.16.8 단건 조회 / 부분 수정 / 삭제

```bash
NOTE_ID=1

# 단건
curl "http://127.0.0.1:8000/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN"

# 부분 수정 — title만
curl -X PATCH "http://127.0.0.1:8000/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"제목만 살짝"}'

# 삭제 → 204
curl -X DELETE -i "http://127.0.0.1:8000/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 204 No Content

# 다시 조회 → 404
curl -i "http://127.0.0.1:8000/notes/$NOTE_ID" \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 404 Not Found
```

### 10.16.9 본인 소유 검사 시연 — 다른 사용자

다른 사용자(Bob)로 회원가입·로그인한 뒤, Alice의 메모 ID로 GET을 시도해 봅시다.

```bash
# Bob 가입
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"bob@example.com","password":"bobpass12345"}'

# Bob 로그인
T2=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=bob@example.com&password=bobpass12345" | jq -r .access_token)

# Alice가 다시 메모 만들었다고 가정
curl -X POST http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"alice의 비밀","body":"ssh"}' > /dev/null

# Bob이 Alice의 메모 ID(예: 2번)로 접근 시도
curl -i "http://127.0.0.1:8000/notes/2" \
  -H "Authorization: Bearer $T2"
# HTTP/1.1 404 Not Found
# {"detail":"메모 2를 찾을 수 없습니다"}
```

**403이 아니라 404**가 돌아오는 걸 확인하세요. 이게 우리의 의도된 동작입니다.

### 10.16.10 인증 실패 케이스들

```bash
# 토큰 없이 → 401
curl -i http://127.0.0.1:8000/notes
# HTTP/1.1 401 Unauthorized

# 변조된 토큰 → 401
curl -i http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer THIS_IS_NOT_A_REAL_TOKEN"

# 잘못된 비밀번호 로그인 → 401
curl -i -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=wrong"
```

### 10.16.11 자동 문서로 한 번 더

브라우저에서 `http://127.0.0.1:8000/docs`를 열고:

1. **Authorize** 클릭 → username(이메일)과 password 입력 → **Authorize**
2. 보호된 엔드포인트(자물쇠 아이콘)가 모두 잠금 해제됨.
3. `POST /notes`를 펼치고 **Try it out → Execute** → 201 응답.

이 흐름은 `OAuth2PasswordBearer(tokenUrl="/auth/login")` 한 줄 등록만으로 자동 동작합니다.

---

## 10.17 통합 테스트 — `pytest` + `httpx.AsyncClient`

마지막 큰 조각. **사람이 매번 curl을 안 날려도** 동작이 깨졌는지 자동으로 검증되도록 만듭니다.

### 10.17.1 테스트 전략 — 인메모리 SQLite로 빠르게

> **운영은 PostgreSQL, 테스트는 인메모리 SQLite.** SQLAlchemy 모델 코드는 그대로 동작하므로, 의존성을 줄이고 매 테스트가 1초 안에 끝나도록 합니다. 진짜 PostgreSQL 동작은 Docker Compose로 별도 검증합니다.

핵심 트릭은 **의존성 오버라이드**입니다.

```python
app.dependency_overrides[get_session] = override_get_session
```

이 한 줄로 운영의 `get_session`을 테스트용 세션 함수로 갈아치웁니다. **앱 코드는 한 글자도 바꾸지 않고** 테스트 환경만 다르게 동작시킵니다.

### 10.17.2 `tests/conftest.py`

```python
# tests/conftest.py
from __future__ import annotations
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
def alice_signup() -> dict[str, str]:
    return {"email": "alice@example.com", "password": "alicepass1234"}


@pytest.fixture
def alice_login() -> dict[str, str]:
    return {"username": "alice@example.com", "password": "alicepass1234"}


@pytest.fixture
def bob_signup() -> dict[str, str]:
    return {"email": "bob@example.com", "password": "bobpass12345"}


@pytest.fixture
def bob_login() -> dict[str, str]:
    return {"username": "bob@example.com", "password": "bobpass12345"}


async def signup_and_login(client, signup, login) -> str:
    r = await client.post("/auth/signup", json=signup)
    assert r.status_code == 201
    r = await client.post("/auth/login", data=login)
    assert r.status_code == 200
    return r.json()["access_token"]
```

> **`StaticPool`이 핵심**: 인메모리 SQLite의 기본 풀은 연결마다 별도 메모리 공간을 잡아 테스트가 깨집니다. `StaticPool`을 쓰면 같은 연결을 재사용해 여러 세션이 같은 DB를 봅니다.

> **`ASGITransport(app=app)`**: 진짜 네트워크 없이 앱을 직접 호출하는 트랜스포트입니다. 매우 빠르고 격리도 깔끔.

### 10.17.3 `tests/test_notes.py` (핵심 케이스)

전체 코드는 예제 폴더에 있습니다. 여기서는 **본인 소유 검사** 테스트를 발췌해 봅니다. 발췌 코드의 `signup_and_login` 헬퍼는 같은 `tests/` 패키지의 `conftest.py` 에 정의되어 있으므로 파일 상단에 다음 한 줄 import 가 필요합니다(예제 파일에는 이미 들어 있습니다).

```python
from .conftest import signup_and_login   # ← tests/__init__.py 가 있어야 동작
```

이어지는 발췌:

```python
async def test_other_users_note_returns_404(
    client, alice_signup, alice_login, bob_signup, bob_login,
):
    # Alice가 메모 한 건 만든다.
    alice_token = await signup_and_login(client, alice_signup, alice_login)
    r = await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "alice의 비밀", "body": "ssh"},
    )
    assert r.status_code == 201
    alice_note_id = r.json()["id"]

    # Bob 가입·로그인
    bob_token = await signup_and_login(client, bob_signup, bob_login)
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob이 Alice의 메모를 GET 시도 → 404
    r = await client.get(f"/notes/{alice_note_id}", headers=bob_headers)
    assert r.status_code == 404

    # PATCH 시도 → 404
    r = await client.patch(
        f"/notes/{alice_note_id}",
        headers=bob_headers,
        json={"title": "bob이 훔쳤다"},
    )
    assert r.status_code == 404

    # DELETE 시도 → 404
    r = await client.delete(f"/notes/{alice_note_id}", headers=bob_headers)
    assert r.status_code == 404

    # Alice가 자기 메모를 다시 조회하면 잘 나옴 (안 망가졌는지)
    r = await client.get(
        f"/notes/{alice_note_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 200
```

전체 테스트 케이스(예제 폴더의 `tests/test_notes.py`):

1. 헬스체크 200.
2. 회원가입 → 로그인 → 메모 CRUD 한 바퀴 (단건 조회, 부분 수정, 삭제 후 404 확인).
3. 이메일 중복 → 409.
4. 잘못된 비밀번호 → 401.
5. 존재하지 않는 사용자로 로그인 → 401 (메시지 통일 확인).
6. 토큰 없이 보호된 라우트 → 401.
7. 빈 제목/본문으로 메모 생성 → 422.
8. **타인 메모 GET/PATCH/DELETE → 404 (본인 소유 검사)**.
9. 내 목록에 다른 사람 메모가 안 보이는지.
10. 페이지네이션, 태그 필터, 키워드 검색.
11. 빈 본문 PATCH는 원본 그대로.

### 10.17.4 `pyproject.toml`의 pytest 옵션

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- `asyncio_mode = "auto"` — `async def test_...`를 자동 감지.
- `testpaths = ["tests"]` — 어디서 테스트를 찾을지 못박음.

### 10.17.5 실행

```bash
uv run pytest -v
```

성공하면:

```
tests/test_notes.py::test_health PASSED
tests/test_notes.py::test_signup_login_me_flow PASSED
tests/test_notes.py::test_signup_duplicate_email_returns_409 PASSED
tests/test_notes.py::test_login_wrong_password_returns_401 PASSED
tests/test_notes.py::test_login_unknown_user_same_message PASSED
tests/test_notes.py::test_notes_without_token_returns_401 PASSED
tests/test_notes.py::test_create_note_validation_errors PASSED
tests/test_notes.py::test_other_users_note_returns_404 PASSED
tests/test_notes.py::test_list_notes_returns_only_my_notes PASSED
tests/test_notes.py::test_list_notes_pagination_and_filter PASSED
tests/test_notes.py::test_patch_with_empty_body_keeps_original PASSED
================== 11 passed in 1.2s ==================
```

매 테스트는 새 인메모리 DB를 받습니다. 한 테스트가 만든 데이터가 다음 테스트로 새지 않습니다.

---

## 10.18 Docker로 앱 빌드 — 멀티 스테이지 + 비루트

이제 운영 모양에 한 단계 더 가깝게 갑니다. **앱을 Docker 이미지로 만듭니다.**

### 10.18.1 멀티 스테이지 빌드란?

> **멀티 스테이지 빌드(multi-stage build)란?** 한 Dockerfile 안에 여러 단계를 두고, 마지막 단계만 최종 이미지로 남기는 패턴입니다. 첫 단계에서 빌드 도구로 의존성을 깔고, 마지막 단계에는 그 결과물만 복사해 가져옵니다. **결과 이미지가 작아지고**(빌드 도구가 안 들어감), **공격 표면이 줄어듭니다**.

### 10.18.2 `Dockerfile`

프로젝트 루트에 `Dockerfile`을 만듭니다.

```dockerfile
# syntax=docker/dockerfile:1.7

# ───────────── 1) 빌더 ─────────────
FROM python:3.13-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /usr/local/bin/

ENV UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini


# ───────────── 2) 런타임 ─────────────
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# 비루트 사용자 — 권한 사고를 줄인다.
RUN groupadd --system app && \
    useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

RUN chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
```

각 부분을 풀어 봅니다.

- **`FROM python:3.13-slim AS builder`** — 빌드 단계. slim은 Debian 베이스에서 일부 도구를 제외한 가벼운 이미지.
- **`COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /usr/local/bin/`** — uv 바이너리를 공식 이미지에서 가져옵니다. 버전을 박아두면 재현성이 좋아집니다(작성 시점 안정 태그; 새 마이너 출시 시 직접 갱신).
- **`UV_SYSTEM_PYTHON=1`** — uv가 `.venv` 대신 컨테이너의 시스템 site-packages에 곧장 설치하도록. 컨테이너 안은 격리가 이미 충분해서 `.venv`를 또 만들 이유가 없습니다.
- **의존성 메타데이터를 먼저 복사**(`pyproject.toml`, `uv.lock`)한 뒤 의존성을 설치하고, **그 다음에 앱 소스를 복사**합니다. 이 순서가 Docker의 레이어 캐시를 가장 잘 활용합니다 — 코드만 바뀌면 의존성 설치 단계는 캐시되어 다시 안 돌아갑니다.
- **런타임 단계**는 더 깨끗합니다. uv도 빌드 결과물도 그대로 가져오지만 빌드 도구는 가져오지 않습니다.
- **`ENV PYTHONPATH=/app`** — `--no-install-project` 로 빌드한 패키지 외에, 우리 `app/` 폴더가 cwd 기준 import 가능하도록 PATH 에 명시. console_script 가 cwd 를 자동으로 sys.path 에 안 넣는 환경(예: 일부 컨테이너 런타임)에서도 안전.
- **`useradd ... app`** + **`USER app`** — 비루트 사용자를 만들고 그 사용자로 실행합니다. 컨테이너 안에서 root로 도는 프로세스는 컨테이너 탈출 취약점이 발견되면 호스트 root와 가까워지므로, 일반 사용자로 두는 게 표준입니다.
- **`CMD ["uvicorn", ...]`** — 운영용 실행. **Uvicorn 자체 멀티워커 4개 + `--proxy-headers`** 로 띄웁니다. 개발 시에는 docker-compose에서 명령을 `uvicorn --reload` 로 덮어씁니다.

> **왜 Uvicorn 자체 멀티워커?** Uvicorn 0.30(2024-06)부터 자체 워커 매니저가 내장되어, 따로 Gunicorn 을 두지 않아도 N 워커를 띄울 수 있습니다. 옛 패턴인 `gunicorn -k uvicorn.workers.UvicornWorker` 는 deprecated 되어 0.31 에서 별도 패키지(`uvicorn-worker`)로 분리됐습니다. 이 가이드는 단순한 Uvicorn 한 줄을 표준으로 씁니다(09장 배포 가이드 참고).

> **워커 수는 어떻게 정하나?** 비동기 앱은 한 워커로도 동시 처리량이 크므로 보통 **CPU 코어 수** 정도가 출발점입니다. 1코어 환경이면 1~2, 2코어면 2~4. 위 Dockerfile 은 4로 박아두었지만, 실제 배포 시 CPU 환경과 메모리 사용량을 보며 조정하세요.

### 10.18.3 `.dockerignore` (선택이지만 권장)

루트에 `.dockerignore`를 만들면 이미지에 불필요한 파일이 안 들어가 빌드가 빠르고 결과 이미지가 작아집니다.

```
.git
.gitignore
.venv
__pycache__
*.pyc
.pytest_cache
.ruff_cache
.mypy_cache
*.db
*.sqlite
.env
.env.*
tests/
README.md
```

(예제 폴더에는 `.dockerignore`를 굳이 만들지 않았습니다 — 학습용 단순화)

### 10.18.4 이미지 빌드 한 번 해 보기

```bash
docker build -t note-api:0.1.0 .
docker images note-api
```

성공하면 이미지 한 개가 나옵니다. 직접 실행해 보려면 다음과 같지만, **DB가 같은 네트워크에 있어야** 하므로 일반적으로는 다음 절의 docker-compose로 함께 띄웁니다.

---

## 10.19 docker-compose에 `app` 서비스 추가

10.4의 `docker-compose.yml`에 `app` 서비스를 추가해 통째로 띄웁니다.

```yaml
services:
  db:
    image: postgres:17-alpine
    container_name: note-api-db
    restart: unless-stopped
    environment:
      POSTGRES_DB: note_api
      POSTGRES_USER: note_user
      POSTGRES_PASSWORD: note_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U note_user -d note_api"]
      interval: 5s
      timeout: 5s
      retries: 10

  app:
    build: .
    container_name: note-api-app
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgresql+asyncpg://note_user:note_pass@db:5432/note_api
      SECRET_KEY: ${SECRET_KEY:-please-change-this-to-32-bytes-or-longer-random-string}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: "60"
      CORS_ALLOW_ORIGINS: "*"
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head && \
             uvicorn app.main:app \
               --host 0.0.0.0 --port 8000 \
               --workers 4 \
               --proxy-headers --forwarded-allow-ips='*'"

volumes:
  postgres-data:
```

새로운 부분만 짚습니다.

- **`app.build: .`** — 같은 폴더의 `Dockerfile`로 이미지를 빌드.
- **`depends_on: db: condition: service_healthy`** — db가 healthy가 된 뒤에야 app이 시작됩니다. `pg_isready`로 검증되므로 "DB가 아직 안 뜬 상태에서 마이그레이션이 실패하는" 사고를 막아 줍니다.
- **`environment.DATABASE_URL`** — 호스트가 `localhost`가 아니라 **`db`(서비스 이름)** 입니다. 같은 docker network 안에서는 서비스 이름이 곧 호스트입니다.
- **`environment.SECRET_KEY: ${SECRET_KEY:-...}`** — 셸의 `SECRET_KEY` 환경 변수가 있으면 그것을, 없으면 기본값을 쓴다는 뜻. 운영에서는 반드시 셸 또는 외부 비밀 관리자에서 주입.
- **`command: sh -c "alembic upgrade head && uvicorn ..."`** — 컨테이너 시작 시 마이그레이션을 한 번 적용한 뒤 Uvicorn 멀티워커를 띄웁니다. 운영에서는 마이그레이션을 별도 단계로 분리하는 것이 일반적이지만, 학습용으로는 한 줄로 묶어 두면 편합니다.

> **`restart: unless-stopped` + `alembic upgrade head` 조합 주의**: 마이그레이션이 실패하면 컨테이너가 비정상 종료되고, restart 정책에 따라 무한 재시작(crash loop)이 일어납니다. 부팅이 계속 실패하면 우선 `docker compose logs app` 으로 첫 실패 로그를 확인하고, 마이그레이션을 별도 일회성 컨테이너로 분리하는 패턴(09.5.4 패턴 B)으로 옮기는 것을 고려하세요.

### 10.19.1 통째로 띄우기

기존 개발 서버는 종료한 뒤(포트 8000 충돌 방지):

```bash
# 만약 uvicorn이 떠 있으면 끄세요
# Ctrl+C로 종료

# .env에 SECRET_KEY를 강한 난수로 적어두었는지 확인
cat .env

# 빌드 + db + app 한 번에
docker compose --env-file .env up --build
```

성공 로그:

```
note-api-db   | ... database system is ready to accept connections
note-api-app  | INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, ...
note-api-app  | INFO:     Started parent process [1]
note-api-app  | INFO:     Started server process [8]
note-api-app  | INFO:     Started server process [9]
note-api-app  | INFO:     Started server process [10]
note-api-app  | INFO:     Started server process [11]
note-api-app  | INFO:     Application startup complete.
note-api-app  | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

이제 `http://localhost:8000/health`가 `{"status":"ok"}`를 돌려주면 성공입니다. 10.16의 curl 흐름을 그대로 다시 돌려보세요. 모두 동작합니다.

### 10.19.2 끄기

```bash
# 컨테이너만 종료(데이터는 보존)
docker compose down

# 데이터까지 삭제(완전 초기화)
docker compose down -v
```

---

## 10.20 배포 — Render 또는 Fly.io 한 가지만 짧게

> **자세한 배포 절차는 09장 [배포 가이드](09-deployment.md)에서 다룹니다.** 여기서는 우리 Note API를 컨테이너로 한 번 띄우는 가장 짧은 길만 안내합니다.

### 10.20.1 한 가지 선택 — Fly.io

[Fly.io](https://fly.io/)는 컨테이너 이미지를 그대로 받아 전 세계 엣지에 띄워주는 PaaS입니다. **무료 등급(Hobby Plan)**으로도 실험이 가능하고, Postgres 매니지드도 함께 제공합니다.

### 10.20.2 큰 흐름

1. **`flyctl` 설치** — `curl -L https://fly.io/install.sh | sh`
2. **로그인** — `flyctl auth login` → 브라우저 팝업.
3. **앱 생성** — 프로젝트 루트에서 `flyctl launch`. 인터랙티브 마법사가 다음을 묻습니다.
    - 앱 이름 (`note-api-yourname` 같이 유일한 이름)
    - 리전 (`nrt`(도쿄), `iad`(미 동부) 등)
    - **Postgres를 같이 만들지** — Yes
    - **즉시 배포할지** — 아직 No (환경 변수를 먼저 넣을 거라)
4. **`fly.toml` 점검** — 마법사가 만든 `fly.toml`에 `[build]`와 `[env]` 섹션이 들어 있습니다. `internal_port = 8000`인지, 빌드 방법이 우리 `Dockerfile`을 쓰도록 되어 있는지 확인.
5. **비밀 환경 변수 주입**
   ```bash
   flyctl secrets set SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
   flyctl secrets set ALGORITHM=HS256 ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
   `DATABASE_URL`은 Postgres 서비스를 함께 만들 때 Fly가 자동으로 `flyctl secrets`에 주입합니다.
6. **마이그레이션 실행** — Fly의 머신에 SSH로 들어가 한 번 적용.
   ```bash
   flyctl ssh console
   alembic upgrade head
   exit
   ```
7. **배포** — `flyctl deploy`. 빌드가 끝나면 `https://note-api-yourname.fly.dev`로 접근 가능.

> **위 절차는 현재 자세한 09장 가이드가 도착하면 그것으로 대체됩니다.** 본 챕터는 "한 번 띄워본다"는 경험에 초점을 맞추고, 운영급 절차(HTTPS·도메인·로그·모니터링)는 09장에 위임합니다.

### 10.20.3 대안 — Render

[Render](https://render.com/)도 같은 패턴이 가능합니다.

1. GitHub 저장소에 본 프로젝트를 푸시.
2. Render 대시보드에서 **New → Web Service** → 저장소 연결 → **Docker**를 빌드 환경으로.
3. Render의 PostgreSQL Add-on을 만들고, 발급된 `DATABASE_URL`을 환경 변수로 연결.
4. `SECRET_KEY` 등을 환경 변수로 추가.
5. 배포 후 Render의 Shell에서 `alembic upgrade head` 한 번.

> **둘 중 어느 쪽을 추천하나?** 둘 다 좋지만, **Fly.io가 컨테이너 그대로 운영의 모양에 더 가깝습니다.** Render는 더 단순한 UI를 선호한다면 좋습니다. 더 자세한 비교와 실전 절차는 09장 참고.

---

## 10.21 흔한 실수 / 보안 체크리스트

이 챕터의 코드를 다 따라 만든 뒤, 운영에 띄우기 전에 한 번씩 점검할 사항입니다.

### 10.21.1 코드/설정 점검

- [ ] **`.env`가 git에 커밋되지 않는지** — `git status`로 확인. `.gitignore`에 들어 있어야 정상.
- [ ] **`SECRET_KEY`를 더미 값(`please-change-this-...`)으로 두고 운영에 띄우지 않았는지** — `secrets.token_urlsafe(48)`로 만든 값으로 교체.
- [ ] **응답에 `hashed_password`가 새 나가지 않는지** — `UserRead` 스키마에 그 필드가 없어야 정상. `curl`로 한 번 직접 확인.
- [ ] **로그인 실패 메시지가 통일되어 있는지** — "사용자 없음"과 "비번 틀림"이 같은 메시지여야 함.
- [ ] **메모 라우트들이 본인 소유 검사를 거치는지** — `crud.get_owned_note(...)`나 `WHERE user_id == current_user.id`가 모든 핸들러에 있어야 함.
- [ ] **타인 메모 접근 시 404를 돌려주는지** — 403 아님.
- [ ] **CORS 설정** — 운영 환경에서 `["*"]`이면 위험. 정확한 도메인을 적어 둘 것.

### 10.21.2 인증·암호 관련

- [ ] **운영은 반드시 HTTPS** — JWT는 헤더에 평문으로 실립니다. 도청되면 그대로 사용 가능. 09장의 HTTPS 절차를 따를 것.
- [ ] **Bcrypt의 72바이트 함정**: `hash_password`가 사전에 `ValueError`를 내는지. 한국어 비번 25글자 이상 시 422가 떨어지는 걸 확인.
- [ ] **JWT의 `algorithms`가 리스트로 명시**: `algorithms=["HS256"]`. `"none"`은 절대 포함 금지.
- [ ] **토큰 만료 시간이 합리적인지**: 60분 권장. 금융 서비스 등 민감도가 높으면 더 짧게.
- [ ] **로그아웃 즉시 무효화가 필요하면**: JWT 단독으로는 어렵습니다(만료까지 유효). 블랙리스트 또는 짧은 액세스 토큰 + 갱신 토큰 도입을 검토.

### 10.21.3 DB / 마이그레이션

- [ ] **마이그레이션 파일을 한 번씩 읽고 commit** — autogenerate가 100% 정확하지 않습니다.
- [ ] **운영의 마이그레이션 적용 절차** — 컨테이너 시작 시 자동 적용은 학습용. 운영에서는 별도 단계로 분리하고, 변경에 동의한 뒤 적용.
- [ ] **DB 백업 정책** — Render·Fly의 매니지드 PG는 자동 스냅샷이 있지만, 한 번 점검.
- [ ] **`ondelete=CASCADE` 의도 확인** — 회원 탈퇴 시 메모를 정말 함께 지울지, 보존할지(=`SET NULL`).

### 10.21.4 일반 운영

- [ ] **운영에서는 `--reload` 플래그 사용 금지** — 파일 와처가 무겁고 불안정. Uvicorn 멀티워커(`--workers N --proxy-headers`)만 사용.
- [ ] **로그를 `stdout`으로** — `--access-logfile -`. 컨테이너 환경의 표준.
- [ ] **헬스체크 엔드포인트** — `/health` 가 200을 돌려주는지 외부에서 한 번 확인.
- [ ] **에러 응답에 민감 정보가 안 새는지** — `HTTPException(detail=...)`의 메시지가 사용자에게 노출됩니다. 내부 SQL 에러를 그대로 노출하지 않도록.

---

## 10.22 다음 단계로 가기

이 챕터를 다 마쳤다면 작은 백엔드의 첫 모습이 손에 남았습니다. 더 발전시킬 수 있는 방향을 짧게 정리합니다.

### 10.22.1 11장 Blog API에서 다루는 것

- **N:M 관계**: 한 글에 여러 태그, 한 태그가 여러 글. 본 챕터의 "단순 문자열 태그"를 별도 표(`tags`)와 연결 표(`post_tags`)로 분리합니다.
- **여러 도메인 모델**의 조합(User / Post / Comment / Tag).
- **소프트 삭제**, **인덱스 튜닝**, **N+1 문제와 `selectinload`**.
- 다른 DB(MySQL) 연결 옵션과 차이.

### 10.22.2 본 챕터를 이대로 확장한다면

- **갱신 토큰(refresh token)** — 액세스 토큰 만료를 5~15분으로 줄이고, 갱신 토큰(7~30일)을 별도 발급해 자동 재발급. 보안과 편의의 균형.
- **비밀번호 변경** 엔드포인트 — 현재 비밀번호 + 새 비밀번호.
- **비밀번호 재설정** — 이메일 링크. 외부 메일 서비스 연동(SendGrid, Mailgun 등).
- **메모 고정(pinned)** — `Note.is_pinned: bool` 추가, 목록에서 고정된 것 먼저.
- **메모 공유** — 다른 사용자에게 공유. `note_shares` 표 추가, 본인 소유 검사를 "공유받은 사용자"까지 확장.
- **검색 개선** — PostgreSQL의 `tsvector`/`tsquery`로 풀텍스트 검색.
- **레이트 리밋** — `slowapi`로 로그인 시도 횟수 제한.
- **이메일 인증** — 가입 직후 활성화 메일을 보내고, 클릭 전까지 `is_active=False`로 두기.

### 10.22.3 운영 단단하게 만들기

- 로그를 `structlog`로 구조화(JSON 로그) → 클라우드 로그 분석 도구와 호환.
- Sentry/Datadog로 에러·성능 추적.
- 백업 자동화, 복구 시뮬레이션.
- CI 파이프라인(GitHub Actions) → `pytest` 자동 실행, 실패 시 머지 차단.

---

## 10.23 전체 체크리스트

이 챕터를 따라하면서 한 번씩 확인하는 용도.

- [ ] `uv init` + 의존성 추가 (`fastapi`, `sqlalchemy`, `asyncpg`, `pyjwt`, `bcrypt`, `pydantic-settings`, ...)
- [ ] `.env` 만들고 `SECRET_KEY`를 강한 난수로
- [ ] `docker compose up -d db`로 PostgreSQL 띄우기
- [ ] `app/config.py` (Settings)
- [ ] `app/db.py` (AsyncEngine, get_session)
- [ ] `app/models.py` (User, Note + 1:N 관계)
- [ ] `app/schemas.py` (UserCreate/Read, Token, NoteCreate/Read/Update, NotesPage)
- [ ] `alembic init alembic` → `env.py` 비동기용으로 교체 → 첫 마이그레이션 자동 생성 → `alembic upgrade head`
- [ ] `app/security.py` (bcrypt + PyJWT 네 함수)
- [ ] `app/deps.py` (oauth2_scheme, get_current_user, get_current_active_user)
- [ ] `app/crud.py` (사용자/메모 함수, **본인 소유 검사 포함**)
- [ ] `app/routers/auth.py` (signup, login)
- [ ] `app/routers/notes.py` (CRUD, **본인 소유 강제, 타인 메모 → 404**)
- [ ] `app/main.py` (앱 + CORS + /health + 라우터 include)
- [ ] `tests/conftest.py` + `tests/test_notes.py` → `uv run pytest`
- [ ] `Dockerfile` (멀티 스테이지 + 비루트 + Gunicorn)
- [ ] `docker-compose.yml`에 `app` 서비스 추가 → `docker compose up --build`
- [ ] `/health`가 200, 회원가입→로그인→메모 CRUD가 모두 통과
- [ ] (선택) Fly.io 또는 Render로 한 번 배포

---

## 10.24 이 챕터 요약

- 이 챕터 한 문서만 따라하면 백지에서 **회원가입 + 로그인 + 개인 메모 CRUD**가 동작하는 작은 백엔드를 완성한다.
- 도구는 모두 본 가이드의 약속대로: **Python 3.13 / FastAPI 0.115+ / Pydantic 2 / SQLAlchemy 2 (async) + Alembic / PyJWT / bcrypt 직접 사용 / PostgreSQL + Docker Compose / Uvicorn(개발) + Gunicorn(운영) / uv**.
- 인증은 **JWT 한 가지**. 비밀번호는 **Bcrypt**로 해싱하고, 72바이트 함정을 사전 검증으로 막는다.
- 메모 라우트의 **본인 소유 검사**는 쿼리에 `WHERE user_id == current_user.id`를 박아 구조적으로 강제하고, 타인 메모 접근은 **404로 응답**해 정보 누설을 막는다.
- 페이지네이션(`skip`/`limit`), 태그 필터, 키워드 검색(`ILIKE`)을 한 라우트에서 함께 처리한다.
- **Alembic**으로 첫 마이그레이션을 만들고 적용한다 — `alembic revision --autogenerate -m "..."` → `alembic upgrade head`.
- **`Dockerfile`은 멀티 스테이지 + 비루트 사용자**로 작성하고, `docker-compose.yml`로 `app + db`를 한 번에 띄운다.
- **테스트는 인메모리 SQLite + 의존성 오버라이드**로 1초 안에 끝나게 만든다 — 운영 PostgreSQL 동작은 Docker Compose로 별도 검증.
- 다음 챕터(11장)는 같은 토대 위에 **N:M 관계, 여러 도메인 모델, 페이지네이션·정렬·검색의 본격적인 모양**을 다룬다.

---

← [09. 배포 가이드](09-deployment.md) | 다음 문서로 이동: **[11. 종합 예제 2 — Blog API →](11-project-blog-api.md)**
