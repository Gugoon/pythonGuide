# 12. 유틸리티 및 라이브러리 — 최신 버전과 사용 예제

> **이 챕터는 사전입니다.** 처음부터 끝까지 읽지 않아도 됩니다. 필요한 라이브러리가 생겼을 때 펼쳐 보세요.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 보세요.

> **버전 표기 안내**: 모든 버전은 2026년 4월 기준입니다. `uv add 패키지명`을 그대로 쓰면 최신 호환 버전이 설치됩니다. 특정 버전이 필요하면 `uv add "패키지명>=2.0,<3.0"` 식으로 범위를 지정합니다.

---

## 12.1 라이브러리 한눈에 보기

| 분류 | 핵심 도구 | 한 줄 용도 |
|------|----------|-----------|
| 패키지·환경 | uv, pip, venv, pre-commit | 라이브러리 설치·환경 격리·훅 자동 실행 |
| 코드 품질 | ruff, mypy | 린트·포맷·정적 타입 검사 |
| 데이터·스키마 | Pydantic, pydantic-settings | 요청/응답 검증·환경변수 로딩 |
| ORM·DB | SQLAlchemy 2.0, Alembic, aiosqlite/asyncpg/asyncmy | 표를 객체로·마이그레이션·드라이버 |
| 인증·보안 | PyJWT, bcrypt, secrets | 토큰·비밀번호 해싱·랜덤 |
| HTTP 클라이언트 | httpx, tenacity | 외부 API 호출·재시도 |
| 비동기 | asyncio, anyio, aiocache | 동시성·캐시·작업 큐 |
| 테스트 | pytest, httpx, factory-boy | 단위/통합 테스트·테스트 데이터 |
| 로깅·관측 | structlog, sentry-sdk | 구조화 로그·에러 추적 |
| 운영 | uvicorn, gunicorn, uvloop | ASGI 서버·워커·이벤트 루프 |

> **이 챕터의 모든 항목**은 다음 양식을 따릅니다.
> - **한 줄**: 무엇을 하는가
> - **언제 안 써도 되는가**: 도입을 미뤄도 되는 상황
> - **설치 명령**: `uv add ...` 한 줄
> - **최소 코드**: 5~20줄짜리 동작 가능한 예시
> - **자주 쓰는 패턴**: 실무에서 반복되는 사용 예
> - **함정**: 입문자가 자주 부딪히는 실수
> - **공식 문서 링크**

---

## A. 패키지·환경 도구

## 12.2 uv

> **한 줄**: Python 패키지 매니저 + 가상환경 관리 + 잠금 파일 생성을 한 도구로 묶은 차세대 CLI.
> **버전 (2026-04 기준)**: 0.4.x 이상
> **설치**: 운영체제에 직접 설치 (03장 참고). `curl -LsSf https://astral.sh/uv/install.sh | sh`
> **공식**: https://docs.astral.sh/uv/

### 왜 쓰는가

`pip`/`venv`/`pip-tools`/`poetry`가 따로따로 하던 일을 한 명령으로 처리합니다. 같은 작업을 10~100배 빠르게 합니다. 이 가이드의 권장 도구.

### 언제 안 써도 되는가

회사·학교 보안 정책상 외부 도구 설치가 막혀 있다면 표준 `pip`/`venv`로 진행해도 무방합니다(12.3 참고).

### 자주 쓰는 명령 치트시트

```bash
# 새 프로젝트 시작 (pyproject.toml 자동 생성)
uv init my-api
cd my-api

# 라이브러리 추가 / 제거
uv add fastapi "uvicorn[standard]" sqlalchemy
uv add --dev pytest ruff mypy
uv remove sqlalchemy

# 동기화 (pyproject.toml 또는 uv.lock 기반으로 모든 의존성 설치)
uv sync

# 가상환경 켜지 않고 명령 실행
uv run uvicorn app.main:app --reload
uv run pytest

# 잠금 파일 갱신
uv lock --upgrade
uv lock --upgrade-package fastapi

# Python 버전 직접 관리
uv python install 3.13
uv python pin 3.13     # 이 프로젝트에서 쓸 버전 고정
```

### 함정

- `uv add`와 `uv pip install`은 다릅니다. 전자는 `pyproject.toml`을 갱신하고, 후자는 한 번 설치만 합니다. 프로젝트 의존성은 항상 `uv add`를 쓰세요.
- `uv sync`는 `pyproject.toml`에 없는 라이브러리를 **자동으로 제거**합니다. 임시 실험용 라이브러리를 가상환경에 직접 설치해 두면 사라집니다.

---

## 12.3 pip / venv (대체 환경)

> **한 줄**: Python 표준 패키지 매니저(`pip`)와 가상환경 도구(`venv`).
> **버전**: Python 3.13에 기본 포함
> **설치**: 별도 설치 불필요
> **공식**: https://pip.pypa.io/, https://docs.python.org/ko/3/library/venv.html

### 왜 쓰는가

Python을 설치하면 따라옵니다. 어떤 환경에서도 항상 사용할 수 있는 최소 공통분모입니다.

### 언제 쓰는가

- `uv` 설치가 막혀 있을 때
- CI 빌드 이미지가 `pip`만 가지고 있을 때
- 공식 문서·강의에서 `pip` 명령으로 설명할 때 — 그대로 따라 하기 위해

### 명령 대응표

```bash
# 가상환경 생성 + 활성화
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
.venv\Scripts\activate             # Windows

# 라이브러리 설치
pip install fastapi "uvicorn[standard]"

# 잠금 파일 작성 (수동)
pip freeze > requirements.txt

# 잠금 파일 기반 설치
pip install -r requirements.txt

# 업그레이드
pip install --upgrade fastapi
```

### 함정

- `pip freeze`는 **현재 가상환경에 깔린 모든 것**을 나열합니다. 라이브러리의 의존성·하위 의존성까지 한꺼번에 적힙니다. 사람이 직접 관리하기 어렵습니다 → `pip-tools`나 `uv`를 권장.
- 가상환경을 활성화하지 않고 `pip install`을 하면 시스템 Python에 설치됩니다. 절대 그렇게 하지 마세요.

---

## 12.4 pre-commit

> **한 줄**: 커밋 직전에 ruff·mypy·테스트 같은 검사를 자동 실행해 주는 Git 훅 관리자.
> **버전 (2026-04 기준)**: 4.0.x
> **설치**: `uv add --dev pre-commit`
> **공식**: https://pre-commit.com/

### 왜 쓰는가

"포맷팅 안 한 코드를 푸시했다"는 사고를 사전 차단합니다. 팀원 모두 같은 검사를 같은 버전으로 거치므로 협업이 깔끔해집니다.

### 언제 안 써도 되는가

- 혼자 토이 프로젝트 — 익숙해지기 전에 부담일 수 있습니다.
- 이미 CI에서 같은 검사를 돌리고 있고, 푸시 전 검증을 굳이 한 번 더 할 이유가 없을 때.

### 최소 설정

프로젝트 루트에 `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.7.0
    hooks:
      - id: ruff           # 린트
      - id: ruff-format    # 포맷
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
        additional_dependencies: ["pydantic>=2.0"]
```

활성화:

```bash
uv run pre-commit install     # .git/hooks/pre-commit에 등록
uv run pre-commit run --all-files   # 전체 한 번 돌려보기
```

### 함정

- 처음 설치한 동료가 `pre-commit install`을 안 하면 훅이 안 돕니다. README에 "처음 클론한 뒤 `pre-commit install` 한 번 실행"이라고 적어두세요.
- 훅 버전은 `rev:`에 박혀 있습니다. 정기적으로 `pre-commit autoupdate`로 끌어올리세요.

---

## B. 코드 품질

## 12.5 ruff

> **한 줄**: 매우 빠른 Python 린터 + 포매터. 옛 `flake8` + `black` + `isort` + `pyupgrade`를 한 도구로 대체.
> **버전 (2026-04 기준)**: 0.7.x
> **설치**: `uv add --dev ruff`
> **공식**: https://docs.astral.sh/ruff/

### 왜 쓰는가

Rust로 짜여 다른 도구보다 100~1000배 빠릅니다. 한 도구가 린트·포맷·임포트 정렬까지 다 하므로 설정이 단순합니다.

### 최소 설정

`pyproject.toml`에 추가:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM"]
# E: pycodestyle, F: pyflakes, W: warning, I: isort
# N: pep8-naming, UP: pyupgrade, B: bugbear, SIM: simplify
ignore = ["E501"]   # 한 줄 길이는 포매터에 맡김
```

명령:

```bash
uv run ruff check .              # 린트
uv run ruff check . --fix        # 자동 수정 가능한 것 고치기
uv run ruff format .             # 포맷
```

### 함정

- `ruff format`(포매터)와 `ruff check --fix`(린트 자동 수정)는 별개입니다. 둘 다 돌려야 안전합니다.
- `select`에 너무 많은 규칙을 켜면 기존 코드가 빨갛게 변합니다. 신규 프로젝트에서만 적극적으로 켜고, 기존 프로젝트는 `select = ["E","F","I"]` 정도로 시작해 점진 확장하세요.

---

## 12.6 mypy

> **한 줄**: 정적 타입 체커. 타입 힌트가 실제로 맞는지 실행 전에 검사한다.
> **버전 (2026-04 기준)**: 1.13.x
> **설치**: `uv add --dev mypy`
> **공식**: https://mypy.readthedocs.io/

### 왜 쓰는가

Python은 런타임에 타입을 강제하지 않습니다. 그러나 mypy는 코드만 보고 "이 변수에 `str`이 들어와야 하는데 `int`가 들어가고 있다"를 미리 잡아냅니다. 큰 코드베이스에서 버그 예방 효과가 큽니다.

### 언제 안 써도 되는가

- 타입 힌트를 거의 쓰지 않는 작은 스크립트.
- 입문 단계에서 너무 빠르게 도입하면 좌절합니다 — 코드가 어느 정도 익숙해진 뒤에 도입하세요.

### 최소 설정

`pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.13"
strict = true
plugins = ["pydantic.mypy"]   # Pydantic 모델을 더 정확히 인식

# 타입 스텁이 부실한 라이브러리가 있으면 한 모듈에 한해 막아 둡니다.
# 예: ignore_missing_imports = true 로 import 누락만 무시.
# (fastapi/starlette 는 스텁이 잘 갖춰져 있어 별도 override 불필요.)
```

명령:

```bash
uv run mypy app/
```

### 자주 쓰는 패턴: SQLAlchemy 2.0 + mypy

SQLAlchemy 2.0의 `Mapped[...]` 표기와 mypy는 잘 맞습니다. 모델 클래스에서 `Mapped[int]`, `Mapped[str | None]` 등으로 적으면 mypy가 컬럼 타입을 정확히 추론합니다.

### 함정

- `strict = true`는 매우 엄격합니다. 처음 도입할 때는 끄고 시작하거나, `disallow_untyped_defs = false` 같은 옵션을 단계적으로 켜세요.
- 외부 라이브러리에 타입 정보가 없으면 `[import-untyped]` 에러가 뜹니다. 해당 모듈에 `# type: ignore[import-untyped]`를 붙이거나 `ignore_missing_imports = true`로 우회.

---

## 12.7 pyright / basedpyright (mypy 대안)

> **한 줄**: Microsoft의 정적 타입 체커. VS Code Pylance의 엔진. mypy보다 빠르고 추론이 강력하다.
> **버전 (2026-04 기준)**: pyright 1.1.x
> **설치**: `uv add --dev pyright`
> **공식**: https://github.com/microsoft/pyright, https://docs.basedpyright.com/

### 왜 mypy 대신?

- VS Code 사용자라면 이미 백그라운드에서 pyright(Pylance)가 돕고 있습니다. CLI에서도 같은 엔진을 쓰면 일관성이 좋습니다.
- mypy보다 보통 10배 정도 빠릅니다.
- `basedpyright`는 pyright의 포크로, mypy 호환 옵션과 추가 규칙을 갖춰 한국어권에서도 인기를 얻고 있습니다.

### 함정

- mypy와 결과가 100% 일치하지는 않습니다. 둘 중 하나만 쓰세요. 섞어 쓰면 서로 다른 경고에 시달립니다.
- 대규모 프로젝트에서 둘 다 시도해 보고 팀에 맞는 쪽을 정하면 됩니다. 이 가이드는 mypy 기준으로 안내했지만 pyright도 좋은 선택입니다.

---

## 12.8 bandit

> **한 줄**: Python 코드를 정적으로 훑어 보안 취약점을 잡아내는 린터.
> **버전 (2026-04 기준)**: 1.7.x
> **설치**: `uv add --dev bandit`
> **공식**: https://bandit.readthedocs.io/

### 왜 쓰는가

`eval()` 호출, 하드코딩된 비밀번호, `subprocess` 셸 인젝션 위험 등을 자동으로 탐지합니다. 보안 팀 없는 작은 회사에서 최소한의 검사를 자동화할 수 있습니다.

### 사용 예

```bash
uv run bandit -r app/      # app/ 폴더 재귀 검사
uv run bandit -r app/ -ll  # MEDIUM 이상만 표시
```

`pyproject.toml`로 제외 규칙 지정:

```toml
[tool.bandit]
exclude_dirs = ["tests", "migrations"]
skips = ["B101"]   # assert 사용 허용 (테스트에서 흔함)
```

### 함정

- 거짓 양성(false positive)이 꽤 있습니다. 본질적으로 정적 분석의 한계입니다.
- `bandit`이 잡아주는 건 매우 기초적인 보안 문제뿐입니다. 진짜 보안은 인증·CSRF·XSS·의존성 관리 등 더 큰 그림으로 봐야 합니다.

---

## C. 데이터·스키마

## 12.9 Pydantic v2

> **한 줄**: 클래스 정의만으로 JSON 검증·직렬화·문서화를 자동으로 해주는 데이터 모델 라이브러리.
> **버전 (2026-04 기준)**: 2.10.x 이상
> **설치**: FastAPI 설치 시 자동 포함. 단독으로는 `uv add pydantic`
> **공식**: https://docs.pydantic.dev/

### 왜 쓰는가

FastAPI의 데이터 처리 전체가 Pydantic 위에서 돕니다. 요청 본문, 응답 본문, 쿼리 파라미터, 환경변수 — 거의 모든 것이 Pydantic 모델입니다.

### 최소 코드

```python
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nickname: str | None = None

class UserOut(BaseModel):
    id: int
    email: EmailStr
    nickname: str | None
    created_at: datetime

# 검증
user = UserCreate(email="a@b.com", password="hello1234")
print(user.model_dump())   # dict로
print(user.model_dump_json())  # JSON 문자열로

# 잘못된 입력 → ValidationError
UserCreate(email="not-an-email", password="123")
```

> **`EmailStr`을 쓰려면**: `uv add "pydantic[email]"` 또는 `uv add email-validator`로 검증 라이브러리를 추가해야 합니다.

### Field 자주 쓰는 옵션

```python
class Article(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", description="본문 (선택)")
    view_count: int = Field(default=0, ge=0)        # 0 이상
    score: float = Field(default=0.0, ge=0.0, le=5.0)  # 0~5
    tags: list[str] = Field(default_factory=list, max_length=10)
```

### Validator (필드 단위 검증)

```python
from pydantic import BaseModel, field_validator

class SignupForm(BaseModel):
    username: str

    @field_validator("username")
    @classmethod
    def lowercase(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("영숫자만 가능합니다")
        return v.lower()
```

### Model Config

```python
from pydantic import BaseModel, ConfigDict

class StrictModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",          # 정의 안 된 필드가 들어오면 에러
        str_strip_whitespace=True,  # 자동 trim
        frozen=True,              # 불변
    )

class FromORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    # SQLAlchemy 모델을 그대로 받아 변환할 수 있음
```

### 자주 쓰는 패턴: 응답 모델 분리

```python
# 들어올 때(생성)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# DB 안의 형태(내부)
class UserInDB(BaseModel):
    id: int
    email: str
    password_hash: str

# 나갈 때(외부) - password_hash가 빠짐
class UserOut(BaseModel):
    id: int
    email: str
```

이 분리로 비밀번호 해시가 응답에 섞여 나가는 사고를 막습니다. 05장에서 자세히 다뤘습니다.

### 함정

- **v1 → v2 차이**: 옛 `dict()`, `json()` 메서드는 `model_dump()`, `model_dump_json()`으로 바뀌었습니다. 옛 글·답변을 보고 따라 했다면 메서드 이름을 확인하세요.
- `Optional[str]`보다 `str | None`(Python 3.10+)이 권장입니다.
- `from_attributes=True`(옛 `orm_mode`)가 없으면 SQLAlchemy 객체를 Pydantic으로 변환할 수 없습니다.

---

## 12.10 pydantic-settings

> **한 줄**: `.env` 파일과 환경 변수를 Pydantic 모델로 안전하게 읽어들이는 라이브러리.
> **버전 (2026-04 기준)**: 2.6.x
> **설치**: `uv add pydantic-settings`
> **공식**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/

### 왜 쓰는가

`os.getenv("DATABASE_URL")`을 직접 부르면 타입 변환·기본값·검증을 매번 손으로 해야 합니다. pydantic-settings는 그 모두를 모델로 자동 처리합니다.

### 최소 코드

`.env`:

```
APP_ENV=development
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/mydb
JWT_SECRET=super-secret-change-me
JWT_EXP_MINUTES=60
```

`config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "development"
    database_url: str
    jwt_secret: str
    jwt_exp_minutes: int = 60

settings = Settings()   # ← 한 줄로 .env 읽고 검증 끝
```

### 자주 쓰는 패턴: 캐시된 싱글톤

```python
from functools import lru_cache

@lru_cache
def get_settings() -> Settings:
    return Settings()

# FastAPI 의존성
from fastapi import Depends

def use_settings(s: Settings = Depends(get_settings)):
    return s
```

### 함정

- `.env`는 절대 git에 커밋하지 않습니다. `.env.example`만 커밋하고 실제 값은 환경 변수나 비밀 관리 시스템(AWS Secrets Manager 등)에서 주입.
- `extra="ignore"`를 안 켜면 `.env`에 `Settings`에 없는 변수가 있을 때 검증 에러가 납니다.

---

## 12.11 dataclasses와 Pydantic의 차이

> **dataclasses**(표준)는 "데이터를 담는 클래스를 짧게 적게 해주는 문법 설탕"입니다.
> **Pydantic**은 "검증·직렬화·문서화까지 해주는 데이터 모델"입니다.
>
> **차이 요약**:
> | 항목 | dataclass | Pydantic BaseModel |
> |------|-----------|--------------------|
> | 표준 라이브러리 | 예 | 아니오 (외부 의존성) |
> | 타입 강제 | 안 함 (힌트일 뿐) | 함 (런타임 검증) |
> | JSON 직렬화 | 직접 구현 | `model_dump_json()` |
> | OpenAPI 문서 | 안 됨 | FastAPI에서 자동 |
> | 속도 | 약간 빠름 | 충분히 빠름 (Rust 코어) |
>
> **언제 무엇을**:
> - 외부에서 들어오는 데이터(요청·응답·환경변수) → Pydantic
> - 내부 도메인 로직의 가벼운 값 객체 → dataclass

```python
from dataclasses import dataclass

@dataclass
class Coordinate:
    lat: float
    lng: float

c = Coordinate(lat="not-a-number", lng=0)  # 통과! 검증 없음
```

같은 코드를 Pydantic으로 작성하면 첫 줄에서 즉시 ValidationError가 납니다.

---

## D. ORM·DB

## 12.12 SQLAlchemy 2.0

> **한 줄**: Python에서 가장 널리 쓰이는 ORM. 표를 클래스로, SQL을 Python 표현식으로 다룬다.
> **버전 (2026-04 기준)**: 2.0.x (1.4 → 2.0으로 큰 변화 있었음)
> **설치**: `uv add "sqlalchemy[asyncio]>=2.0"` (비동기 사용 시. 동기만 쓸 때는 `uv add "sqlalchemy>=2.0"`)
> **공식**: https://docs.sqlalchemy.org/en/20/

### 왜 쓰는가

- 표 구조를 Python 클래스로 한 곳에 모음 → mypy/pyright와 잘 어울림.
- 비동기 지원이 정식이 됨 → FastAPI와 자연스럽게 결합.
- SQL 인젝션 위험 자동 회피.

### 모델 정의 (2.0 스타일)

```python
from datetime import datetime, timezone
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    # bcrypt 해시는 60자지만 알고리즘 교체(예: Argon2)나 prefix 변동을 대비해 여유를 둡니다.
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

`Mapped[...]` 표기 덕분에 IDE 자동완성과 mypy 추론이 정확해집니다.

### 비동기 세션 + select()

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/mydb",
    echo=False,
    pool_size=5,
    max_overflow=10,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as session:
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
```

### 자주 쓰는 패턴: 관계 로딩 옵션

```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload: 추가 IN 쿼리 한 번 (1:N에 적합)
stmt = select(User).options(selectinload(User.posts))

# joinedload: JOIN으로 한 번에 (1:1, 작은 N에 적합)
stmt = select(Post).options(joinedload(Post.author))
```

> **N+1 문제란?** 사용자 100명을 가져온 뒤 각각의 글을 또 100번 쿼리하면 총 101번 쿼리가 나갑니다. `selectinload`/`joinedload`로 한 번에 끌어오면 2번 또는 1번으로 줄어듭니다.

### 자주 쓰는 패턴: 세션을 의존성으로 주입

```python
from fastapi import Depends

async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

@app.get("/users/{user_id}")
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(404)
    return user
```

### 함정

- 1.4에서 2.0으로 올라오며 API가 크게 바뀌었습니다. 옛 글의 `Query(...)`, `db.query(User)` 같은 코드는 2.0 스타일이 아닙니다.
- `expire_on_commit=False`를 비동기에서 안 켜면 커밋 후 객체 속성 접근에서 추가 쿼리가 발생합니다.
- `await session.commit()`을 빼먹으면 변경 사항이 사라집니다.

---

## 12.13 Alembic

> **한 줄**: SQLAlchemy와 짝지어 쓰는 DB 마이그레이션 도구.
> **버전 (2026-04 기준)**: 1.13.x 이상
> **설치**: `uv add alembic`
> **공식**: https://alembic.sqlalchemy.org/

### 왜 쓰는가

DB 표 구조 변경(컬럼 추가, 타입 변경 등)을 코드 파일로 남깁니다. 팀원이 같은 순서로 적용할 수 있고, 운영 환경에서도 동일한 변화를 안전하게 반영합니다.

### 자주 쓰는 명령 치트시트

```bash
# 초기화 (alembic/ 디렉터리 생성)
uv run alembic init alembic

# 자동 생성 (모델 변경을 감지해 마이그레이션 파일 작성)
uv run alembic revision --autogenerate -m "add users table"

# 적용 (최신까지)
uv run alembic upgrade head

# 한 단계 되돌리기
uv run alembic downgrade -1

# 현재 적용된 리비전 확인
uv run alembic current

# 히스토리 보기
uv run alembic history
```

### env.py 비동기 설정 핵심

`alembic/env.py`에서 비동기 엔진을 쓰려면 **`do_run_migrations` 함수 정의가 반드시 있어야** 합니다(아래 예시 참고). 이 함수가 동기 connection 위에서 실제 마이그레이션을 실행합니다.

```python
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,   # SQLite ALTER TABLE 호환
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async def do_run():
        async with connectable.connect() as conn:
            await conn.run_sync(do_run_migrations)
        await connectable.dispose()
    asyncio.run(do_run())
```

자세한 템플릿은 06장과 10장 종합 예제에서 다뤘습니다(전체 self-contained 코드는 거기에 있음).

### 함정

- `--autogenerate`는 만능이 아닙니다. 인덱스 이름 변경, 컬럼 타입 정밀 변경 등은 수동 보정이 필요합니다. **항상 생성된 파일을 한 번 읽고 검토**하세요.
- 마이그레이션 파일은 git에 커밋합니다. 절대 운영 환경에서 즉석으로 ALTER TABLE을 치지 마세요 — 환경 간 불일치 사고의 원인.
- `target_metadata`에 모델의 `Base.metadata`를 연결해야 자동 감지가 작동합니다.

---

## 12.14 DB 드라이버 — aiosqlite / asyncpg / asyncmy

> **한 줄**: 각 DB와 비동기로 통신하는 저수준 라이브러리. SQLAlchemy 비동기 엔진의 백엔드.
> **공식**:
> - aiosqlite: https://github.com/omnilib/aiosqlite
> - asyncpg: https://github.com/MagicStack/asyncpg
> - asyncmy: https://github.com/long2ice/asyncmy

### 설치 명령

| DB | 드라이버 | 설치 | DSN 예시 |
|----|----------|------|----------|
| SQLite | aiosqlite | `uv add aiosqlite` | `sqlite+aiosqlite:///./app.db` |
| PostgreSQL | asyncpg | `uv add asyncpg` | `postgresql+asyncpg://user:pw@host:5432/db` |
| MySQL/MariaDB | asyncmy | `uv add asyncmy` | `mysql+asyncmy://user:pw@host:3306/db` |

> **DSN(Data Source Name)이란?** DB 접속 정보를 한 줄 문자열로 표현한 것. `방언+드라이버://사용자:비밀번호@호스트:포트/DB이름` 형식.

### 자주 쓰는 패턴: 환경별 DSN 분기

```python
# .env (개발)
DATABASE_URL=sqlite+aiosqlite:///./dev.db

# .env (운영)
DATABASE_URL=postgresql+asyncpg://...
```

코드는 그대로 두고 `.env`만 바꿉니다. 06장에서 자세히 다뤘습니다.

### 함정

- **동기 드라이버와 섞지 마세요**. `psycopg2`(동기)와 `asyncpg`(비동기)를 같이 쓰면 이벤트 루프가 막힙니다. async/await 코드 안에서 동기 DB 호출은 금기.
- SQLite는 동시 쓰기에 약합니다. 운영 환경에는 PostgreSQL 또는 MySQL을 권장.

---

## 12.15 SQLModel (옵션)

> **한 줄**: FastAPI 작성자(Sebastián)가 만든, Pydantic + SQLAlchemy를 통합한 모델 라이브러리.
> **버전 (2026-04 기준)**: 0.0.22+
> **설치**: `uv add sqlmodel`
> **공식**: https://sqlmodel.tiangolo.com/

### 이 가이드가 쓰지 않는 이유

- 한 클래스로 "DB 모델"과 "API 스키마"를 동시에 표현하는 매력적인 발상이지만, 두 책임을 분리하지 못해 큰 프로젝트에서 오히려 불편합니다.
- 2026년 4월 시점 1.0 미만이며, SQLAlchemy 2.0의 새 API와 일부 어긋나는 부분이 있습니다.
- 입문자에게는 "SQLAlchemy 모델은 DB 표"와 "Pydantic 모델은 API 스키마"가 따로 있다는 분리를 처음부터 이해하는 게 장기적으로 유리합니다.

### 그래도 써보고 싶다면

```python
from sqlmodel import Field, SQLModel, create_engine

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: int | None = None

engine = create_engine("sqlite:///hero.db")
SQLModel.metadata.create_all(engine)
```

소규모 프로토타입에는 깔끔하게 동작합니다. 단, 본격적으로 커지면 SQLAlchemy + Pydantic 분리로 갈아타야 할 가능성이 높습니다.

---

## E. 인증·보안

## 12.16 PyJWT

> **한 줄**: JWT(JSON Web Token)를 만들고 검증하는 Python 라이브러리.
> **버전 (2026-04 기준)**: 2.8.x 이상
> **설치**: `uv add pyjwt`
> **공식**: https://pyjwt.readthedocs.io/

### 왜 쓰는가

로그인 후 클라이언트에 발급하는 토큰을 만들고 검증할 때 사실상 표준입니다. 08장에서 직접 사용했습니다.

### 최소 코드

```python
from datetime import datetime, timedelta, timezone
import jwt

SECRET = "change-me-in-production"
ALGO = "HS256"

# 발급
payload = {
    "sub": "42",                                              # subject = user_id
    "exp": datetime.now(timezone.utc) + timedelta(hours=1),   # 만료
    "iat": datetime.now(timezone.utc),                        # 발급 시각
}
token = jwt.encode(payload, SECRET, algorithm=ALGO)

# 검증
try:
    decoded = jwt.decode(
        token, SECRET, algorithms=[ALGO],
        options={"require": ["exp", "sub", "iat"]},   # 필수 클레임 강제
    )
    # JWT 표준상 sub 는 문자열입니다. 정수가 필요하면 디코딩 후 캐스트.
    user_id = int(decoded["sub"])
except jwt.ExpiredSignatureError:
    print("만료됨")
except jwt.InvalidTokenError:
    print("위조됨")
```

### 자주 쓰는 클레임(claim)

> **클레임이란?** JWT 페이로드 안에 들어가는 키-값 쌍. 표준 키와 사용자 정의 키가 있습니다.

| 키 | 의미 |
|----|------|
| `sub` | subject — 누구의 토큰인가 (보통 user_id) |
| `exp` | expiration — 언제까지 유효한가 (UNIX 시간) |
| `iat` | issued at — 언제 발급됐는가 |
| `nbf` | not before — 언제부터 유효한가 |
| `iss` | issuer — 누가 발급했는가 |
| `aud` | audience — 누구를 위한 토큰인가 |
| `jti` | JWT ID — 고유 식별자 (블랙리스트에 활용) |

### 함정

- **HS256은 대칭 키**입니다. 검증 측도 비밀키를 알아야 합니다. 서비스 간에 키를 공유해야 한다면 RS256(비대칭) 같은 알고리즘을 검토하세요.
- `algorithms=[ALGO]`를 명시하지 않고 `decode()`를 부르면 보안 취약점입니다 — `none` 알고리즘 공격 등을 차단해야 합니다.
- 토큰 안의 정보는 **암호화되지 않고 서명만 된** 상태입니다. base64 디코딩하면 누구나 읽을 수 있으므로 비밀번호·민감정보를 넣지 마세요.

---

## 12.17 bcrypt

> **한 줄**: 비밀번호 해싱 표준 알고리즘 Bcrypt의 Python 구현.
> **버전 (2026-04 기준)**: 4.x
> **설치**: `uv add bcrypt`
> **공식**: https://github.com/pyca/bcrypt/

### 왜 쓰는가

비밀번호를 평문 저장하면 큰 사고입니다. Bcrypt는 일부러 느리게 설계되어 무차별 공격을 어렵게 합니다. salt를 자동으로 다뤄 같은 비밀번호라도 매번 다른 해시가 나옵니다.

### 최소 코드 (08장 복습)

```python
import bcrypt

# 가입 시
def hash_password(plain: str) -> str:
    salt = bcrypt.gensalt(rounds=12)             # cost factor 12
    return bcrypt.hashpw(plain.encode(), salt).decode()

# 로그인 시
def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

# 사용
hashed = hash_password("hunter2")
print(verify_password("hunter2", hashed))   # True
print(verify_password("wrong", hashed))     # False
```

### 함정 — 72바이트 제한

> **72바이트란?** Bcrypt 알고리즘 자체의 입력 제한입니다. **비밀번호의 73번째 바이트부터는 무시됩니다.**
>
> ASCII 영숫자는 1글자 = 1바이트라 72글자까지 안전하지만, **한글은 UTF-8에서 1글자 = 3바이트**입니다. 즉 한글 24글자 = 72바이트로, 그 이상은 잘립니다.
>
> 입력 단에서 비밀번호 길이를 합리적으로 제한하거나(예: Pydantic의 `max_length=72`), 미리 SHA-256으로 한 번 해싱하고 그 결과를 Bcrypt에 넣는 두 가지 패턴이 있습니다. 입문자에게는 **단순한 길이 제한**을 권장합니다.

### cost factor

`gensalt(rounds=12)`의 `12`가 cost factor입니다. 1 늘릴 때마다 시간이 약 2배 늘어납니다.

- 12: 일반적인 권장값(약 250~400ms)
- 4: 테스트에서 빠르게 (`bcrypt.gensalt(rounds=4)`)
- 14 이상: 매우 느려짐. CPU 부하 주의

---

## 12.18 passlib (왜 안 쓰는지)

`passlib`는 여러 해싱 알고리즘을 추상화한 라이브러리로 한때 표준이었습니다. 그러나:

1. 2020년 이후 사실상 유지보수가 정체되어 있습니다(2024~2025년 동안 새 릴리스가 거의 없음).
2. Bcrypt 4.x와 호환 경고가 자주 발생합니다.
3. 입문자에게 추가 추상화 층이 오히려 디버깅을 어렵게 합니다.

이 가이드는 `bcrypt`를 직접 사용합니다. 단, 이미 `passlib`를 쓰는 코드베이스에 합류했다면 그 코드를 그대로 유지해도 큰 문제는 없습니다.

---

## 12.19 itsdangerous

> **한 줄**: "단순한 토큰" — 짧은 데이터에 서명만 붙여 안전하게 주고받게 해주는 라이브러리.
> **버전 (2026-04 기준)**: 2.2.x
> **설치**: `uv add itsdangerous`
> **공식**: https://itsdangerous.palletsprojects.com/

### 왜 쓰는가

JWT는 만료·클레임·표준 알고리즘 등 묵직한 명세입니다. 그러나 "이메일 인증 링크용 일회성 토큰" 정도라면 그렇게까지 무거울 필요가 없습니다. itsdangerous는 그 가벼운 자리를 채웁니다.

### 최소 코드

```python
from itsdangerous import URLSafeTimedSerializer

s = URLSafeTimedSerializer(secret_key="change-me", salt="email-confirm")

# 발급
token = s.dumps({"user_id": 42})
print(token)

# 검증 (1시간 = 3600초 안)
try:
    data = s.loads(token, max_age=3600)
    print(data)
except Exception as e:
    print("invalid:", e)
```

### 자주 쓰는 패턴

- 이메일 인증 링크
- 비밀번호 재설정 링크
- 짧은 수명의 일회성 토큰

### 함정

- JWT의 대체가 아닙니다. 클라이언트가 들고 다니는 인증 토큰은 JWT를 쓰세요.
- `max_age` 검증을 빼먹으면 만료 검사가 안 됩니다.

---

## 12.20 secrets / hmac (표준 라이브러리)

> **한 줄**: 표준 라이브러리에 들어 있는 암호학적으로 안전한 랜덤·메시지 인증.
> **설치**: 없음 (Python 내장)
> **공식**: https://docs.python.org/ko/3/library/secrets.html

### 왜 쓰는가

`random` 모듈은 예측 가능합니다(보안용 아님). 비밀번호 재설정 토큰, API 키, CSRF 토큰처럼 **추측 불가능해야 하는 값**은 `secrets`로 만듭니다.

### 최소 코드

```python
import secrets
import hmac

# 안전한 토큰 (URL 안전 base64)
api_key = secrets.token_urlsafe(32)   # 약 43글자
print(api_key)   # f7K_z...

# 랜덤 정수
n = secrets.randbelow(1000)

# 일정 시간 비교 (타이밍 공격 방어)
def safe_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode(), b.encode())

# 절대로 ==로 토큰을 비교하지 마세요
print(safe_compare("abc", "abc"))   # True
```

### 함정

- 토큰 비교는 `hmac.compare_digest`를 쓰세요. 일반 `==`는 길이별로 응답 시간이 달라져 타이밍 공격이 가능합니다.
- `secrets.token_urlsafe(N)`의 `N`은 **바이트 수**이지 문자 수가 아닙니다. 32바이트 → 약 43글자.

---

## F. HTTP 클라이언트·API 호출

## 12.21 httpx

> **한 줄**: 동기·비동기 둘 다 지원하는 차세대 Python HTTP 클라이언트.
> **버전 (2026-04 기준)**: 0.27.x
> **설치**: `uv add httpx`
> **공식**: https://www.python-httpx.org/

### 왜 쓰는가

- 비동기(`async`) 지원이 처음부터 일급 시민입니다.
- API가 `requests`와 거의 같아 학습 곡선이 평탄.
- FastAPI 테스트(`AsyncClient`)도 httpx 기반.

### 최소 코드 (동기)

```python
import httpx

resp = httpx.get("https://api.github.com/repos/fastapi/fastapi", timeout=10)
resp.raise_for_status()
print(resp.json()["stargazers_count"])
```

### 최소 코드 (비동기)

```python
import asyncio
import httpx

async def fetch():
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get("https://api.github.com/repos/fastapi/fastapi")
        r.raise_for_status()
        return r.json()

print(asyncio.run(fetch()))
```

### 자주 쓰는 패턴: 공유 클라이언트

매 요청마다 `AsyncClient()`를 새로 만들면 TCP 연결을 매번 새로 만들게 됩니다. 앱 수명 동안 하나를 공유하세요.

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
import httpx

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(timeout=10.0)
    yield
    await app.state.http.aclose()

app = FastAPI(lifespan=lifespan)

@app.get("/joke")
async def joke():
    r = await app.state.http.get("https://api.chucknorris.io/jokes/random")
    return r.json()
```

### 함정

- 응답 본문을 읽지 않으면 연결이 풀로 안 돌아옵니다. `r.json()`이나 `r.text` 또는 `r.aclose()`를 호출하세요.
- 기본 타임아웃은 5초입니다. 필요하면 `timeout=...`을 명시.

---

## 12.22 requests (옛 표준)

> **한 줄**: 가장 유명했던 동기 HTTP 클라이언트. 비동기 미지원.
> **버전 (2026-04 기준)**: 2.32.x
> **설치**: `uv add requests`
> **공식**: https://requests.readthedocs.io/

### 왜 아직 살아있는가

- 사실상 모든 Python 튜토리얼·강의가 `requests`로 적혀 있습니다.
- 동기 코드(스크립트, 데이터 분석 노트북 등)에서는 충분.

### 새 프로젝트는 httpx 쓰세요

- requests는 **비동기를 영구히 지원하지 않을 것**으로 보입니다.
- httpx가 거의 같은 API에 비동기까지 지원합니다.

### 최소 코드

```python
import requests

r = requests.get("https://api.github.com", timeout=10)
r.raise_for_status()
print(r.json())
```

---

## 12.23 tenacity

> **한 줄**: 재시도(retry) 로직을 데코레이터 한 줄로 붙이는 라이브러리.
> **버전 (2026-04 기준)**: 9.0.x
> **설치**: `uv add tenacity`
> **공식**: https://tenacity.readthedocs.io/

### 왜 쓰는가

외부 API가 가끔 5xx를 돌려주거나 네트워크가 잠깐 끊기는 일은 흔합니다. 재시도 로직을 직접 짜면 지수 백오프·최대 시도·예외 종류 분기 등이 금세 복잡해집니다. tenacity는 그 모두를 한 데코레이터로 처리합니다.

### 최소 코드

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(httpx.HTTPError),
)
async def call_external(url: str):
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()
```

### 함정

- 재시도 자체가 외부 시스템에 부하를 더 줄 수 있습니다. **반드시 백오프**를 쓰세요(고정 0.5초 간격은 금기).
- 데이터를 변경하는 요청(POST/DELETE)에 함부로 재시도를 걸면 같은 동작이 두 번 일어날 수 있습니다(중복 결제 등). 멱등성(idempotency) 키를 같이 쓰세요.

---

## G. 비동기 / 작업

## 12.24 asyncio 패턴

> **한 줄**: Python 표준 비동기 런타임. FastAPI가 그 위에서 돈다.
> **설치**: 표준 라이브러리
> **공식**: https://docs.python.org/ko/3/library/asyncio.html

### gather — 여러 코루틴 병렬 실행

```python
import asyncio
import httpx

async def fetch(url: str):
    async with httpx.AsyncClient(timeout=5) as c:
        return (await c.get(url)).json()

async def main():
    urls = ["https://api.github.com", "https://httpbin.org/get"]
    results = await asyncio.gather(*[fetch(u) for u in urls])
    return results
```

### TaskGroup (Python 3.11+)

`gather`보다 깔끔하고 예외 처리가 더 명확합니다.

```python
async def main():
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch("https://a"))
        t2 = tg.create_task(fetch("https://b"))
    # 여기 도달하면 모든 task 완료. 하나라도 예외면 ExceptionGroup
    return t1.result(), t2.result()
```

### timeout

```python
async def main():
    async with asyncio.timeout(2.0):
        result = await slow_call()
```

### 함정

- 비동기 함수 안에서 `time.sleep(1)`을 쓰면 **이벤트 루프 전체가 멈춥니다**. `await asyncio.sleep(1)`을 쓰세요.
- 동기 함수 안에서 `await`를 쓸 수 없습니다. `asyncio.run(...)`으로 진입점을 만들거나, 이미 비동기 컨텍스트(FastAPI 라우터 등) 안에서만 사용.

---

## 12.25 anyio

> **한 줄**: asyncio와 trio 양쪽에서 동작하는 통합 비동기 API.
> **버전 (2026-04 기준)**: 4.x
> **설치**: FastAPI/Starlette가 자동 포함
> **공식**: https://anyio.readthedocs.io/

### 왜 직접 쓸 일이 있는가

FastAPI 내부에서 anyio를 쓰지만, 다음 두 가지 상황에서 직접 사용합니다.

1. **동기 함수를 비동기 컨텍스트에서 안전하게 호출**:

```python
from anyio import to_thread

async def safe_blocking():
    # 블로킹 라이브러리(예: 동기 DB 드라이버, PIL)를 별도 스레드로
    result = await to_thread.run_sync(some_blocking_function, arg1, arg2)
    return result
```

2. **세마포어·Lock·Event 같은 동기화 도구**가 필요할 때.

### 함정

- FastAPI 라우터에서 동기 `def` 함수를 정의하면 FastAPI가 자동으로 anyio의 스레드 풀로 옮겨 실행합니다. 그래서 동기 코드도 그대로 작동합니다 — 입문자가 `def` ↔ `async def`를 자유롭게 섞을 수 있는 이유.

---

## 12.26 aiocache

> **한 줄**: 메모리·Redis·Memcached를 한 API로 다루는 비동기 캐시 라이브러리.
> **버전 (2026-04 기준)**: 0.12.x
> **설치**: `uv add aiocache`
> **공식**: https://aiocache.readthedocs.io/

### 최소 코드

```python
from aiocache import Cache

cache = Cache(Cache.MEMORY)   # 또는 Cache.REDIS

await cache.set("key", "value", ttl=60)
v = await cache.get("key")
```

### 데코레이터로 함수 결과 캐싱

```python
from aiocache import cached

@cached(ttl=300, key_builder=lambda f, *args, **kw: f"user:{args[0]}")
async def get_user_profile(user_id: int):
    # 비싼 호출
    ...
```

### 함정

- 메모리 캐시는 프로세스마다 따로입니다. Gunicorn 워커가 4개면 캐시 4개로 갈라집니다 → Redis로 옮기거나, 캐시 일관성이 중요하지 않은 데이터에만 쓰세요.

---

## 12.27 arq

> **한 줄**: Redis 기반의 가벼운 비동기 작업 큐.
> **버전 (2026-04 기준)**: 0.26.x
> **설치**: `uv add arq`
> **공식**: https://arq-docs.helpmanual.io/

### 왜 쓰는가

이메일 발송, 썸네일 생성, 외부 API 호출처럼 응답 안에서 끝낼 수 없는 작업을 별도 워커로 넘깁니다. Celery보다 훨씬 가볍고, asyncio와 자연스럽게 어울립니다.

### 최소 코드

```python
# tasks.py
from arq.connections import RedisSettings

async def send_welcome_email(ctx, user_id: int, email: str):
    print(f"sending to {email}")

class WorkerSettings:
    functions = [send_welcome_email]
    redis_settings = RedisSettings(host="localhost", port=6379)

# 큐잉 (FastAPI 안에서)
from arq import create_pool

pool = await create_pool(RedisSettings())
await pool.enqueue_job("send_welcome_email", 42, "a@b.com")
```

워커 실행:

```bash
uv run arq tasks.WorkerSettings
```

### 함정

- 워커는 **별도 프로세스**여야 합니다. 웹 서버와 같은 프로세스에 넣으면 의미가 없습니다.
- 작업 함수의 첫 인자는 항상 `ctx`(워커가 주입)입니다.

---

## 12.28 Celery (전통의 강자)

> **한 줄**: Python에서 가장 오래되고 가장 큰 분산 작업 큐.
> **버전 (2026-04 기준)**: 5.4.x
> **설치**: `uv add celery redis`
> **공식**: https://docs.celeryq.dev/

### 언제 쓰는가

- 이미 Celery 인프라가 운영 중이라 학습·도입 비용이 0인 경우.
- Cron 스타일 스케줄링, 결과 백엔드, 모니터링 도구(Flower) 등 풍부한 생태계가 필요할 때.

### 언제 안 써도 되는가

- 새 프로젝트, 작업이 가벼운 경우 — `arq`나 FastAPI의 `BackgroundTasks`가 충분합니다.
- 비동기 코드와의 결합이 중요한 경우 — Celery는 본질적으로 동기 모델입니다.

### 최소 코드

```python
# celery_app.py
from celery import Celery

app = Celery("tasks", broker="redis://localhost:6379/0")

@app.task
def send_email(to: str, subject: str):
    print(f"to={to} subj={subject}")
```

```python
# 사용
from .celery_app import send_email
send_email.delay("a@b.com", "Welcome")
```

워커:

```bash
uv run celery -A celery_app worker --loglevel=info
```

### 함정

- 비동기 FastAPI 안에서 Celery 태스크를 부르는 건 가능하지만, 큐잉 자체가 동기 호출입니다. 호출 빈도가 높으면 별도 스레드로 옮기세요.
- 운영 환경에서는 결과 백엔드(Result Backend)와 브로커를 분리해 안정성을 높입니다.

---

## H. 테스트

## 12.29 pytest

> **한 줄**: Python 테스트 표준 도구. 단순한 함수 하나가 곧 테스트.
> **버전 (2026-04 기준)**: 8.3.x
> **설치**: `uv add --dev pytest`
> **공식**: https://docs.pytest.org/

### 최소 코드

```python
# tests/test_math.py
def add(x, y):
    return x + y

def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
```

실행:

```bash
uv run pytest
uv run pytest -v                 # 자세히
uv run pytest tests/test_math.py # 특정 파일
uv run pytest -k "add"           # 이름 일치 테스트만
```

### Fixture (테스트 준비물)

```python
import pytest

@pytest.fixture
def sample_user():
    return {"id": 1, "email": "a@b.com"}

def test_user(sample_user):
    assert sample_user["email"] == "a@b.com"
```

### parametrize (반복 테스트)

```python
import pytest

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (10, 20, 30),
    (-1, 1, 0),
])
def test_add(a, b, expected):
    assert a + b == expected
```

### 자주 쓰는 옵션

- `--cov=app`: 커버리지 측정 (`uv add --dev pytest-cov` 필요)
- `-x`: 첫 실패에서 즉시 종료
- `--lf`: 마지막에 실패한 것만 다시 실행
- `-s`: print 출력 보이기

### 함정

- 파일 이름은 `test_*.py` 또는 `*_test.py`여야 자동 탐지됩니다.
- 테스트 함수 이름도 `test_`로 시작해야 합니다.

---

## 12.30 pytest-asyncio

> **한 줄**: pytest로 비동기 테스트(`async def`)를 쓸 수 있게 해주는 플러그인.
> **버전 (2026-04 기준)**: 0.24.x
> **설치**: `uv add --dev pytest-asyncio`
> **공식**: https://pytest-asyncio.readthedocs.io/

### 설정

`pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"     # async def는 자동 비동기로 인식
```

### 최소 코드

```python
import pytest
import asyncio

async def fetch():
    await asyncio.sleep(0.01)
    return 42

async def test_fetch():
    result = await fetch()
    assert result == 42
```

### 함정

- `asyncio_mode = "auto"`를 안 켜면 각 테스트에 `@pytest.mark.asyncio` 데코레이터를 붙여야 합니다.
- 동기 fixture를 async 테스트에 그대로 쓸 수 있지만, async fixture를 만들 때는 `@pytest_asyncio.fixture`를 사용.

---

## 12.31 httpx.AsyncClient + ASGITransport

> **한 줄**: 진짜 HTTP 서버를 띄우지 않고도 FastAPI 앱을 비동기로 호출하는 테스트 도구.
> **설치**: `uv add --dev httpx`
> **공식**: https://www.python-httpx.org/async/

### 최소 코드

```python
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest_asyncio.fixture     # ← 비동기 fixture 는 이 데코레이터를 써야 합니다
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

async def test_root(client):
    r = await client.get("/")
    assert r.status_code == 200
```

> `@pytest.fixture` + `async def` 조합은 그대로는 동작하지 않습니다(pytest 자체는 async generator 를 안 풀어 줍니다). `@pytest_asyncio.fixture` 를 쓰거나, 12.30 의 `asyncio_mode = "auto"` 모드를 켜고 함께 사용하세요.

### 자주 쓰는 패턴: DB 의존성 오버라이드

```python
from app.deps import get_session

async def override_session():
    async with TestSessionLocal() as s:
        yield s

app.dependency_overrides[get_session] = override_session
```

### 함정

- `base_url`을 안 주면 상대 URL이 동작하지 않습니다. `base_url="http://test"`로 더미를 주세요.
- 테스트가 끝나면 `dependency_overrides`를 비우거나, 각 테스트가 격리되도록 fixture에서 처리.

---

## 12.32 fastapi.testclient.TestClient

> **한 줄**: 동기 스타일로 FastAPI 앱을 테스트하는 가장 쉬운 도구. Starlette의 `TestClient` 그대로.
> **설치**: `uv add --dev "httpx>=0.27"` (의존)
> **공식**: https://fastapi.tiangolo.com/tutorial/testing/

### 최소 코드

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello"}
```

### 언제 AsyncClient 대신 이걸?

- 입문자가 첫 테스트를 작성할 때 (가장 단순)
- 동기 코드 위주의 프로젝트
- 빠르게 한 엔드포인트만 확인할 때

### 함정

- 내부에서는 동기 코드가 비동기 라우터를 호출할 수 있도록 변환합니다. 매우 빠른 동시 요청 시뮬레이션에는 부적합.
- `with TestClient(app) as client:` 형태가 권장(앱 lifespan 이벤트가 정상 작동).

---

## 12.33 factory-boy / polyfactory

> **한 줄**: 테스트 데이터를 자동 생성하는 팩토리 라이브러리.
> **버전**:
> - factory-boy 3.3.x
> - polyfactory 2.18.x (Pydantic 친화적)
> **설치**:
> - `uv add --dev factory-boy`
> - `uv add --dev polyfactory`
> **공식**: https://factoryboy.readthedocs.io/, https://polyfactory.litestar.dev/

### 왜 쓰는가

테스트마다 사용자·게시글 더미 데이터를 손으로 만들면 코드가 지저분해집니다. 팩토리는 "사용자 만들기"를 한 줄로 처리합니다.

### factory-boy 최소 코드

```python
import factory
from app.models import User

class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    nickname = factory.Faker("name")

# 사용
user = UserFactory()
users = UserFactory.create_batch(5)
```

### polyfactory (Pydantic 친화)

```python
from polyfactory.factories.pydantic_factory import ModelFactory
from app.schemas import UserCreate

class UserCreateFactory(ModelFactory[UserCreate]):
    pass

user_data = UserCreateFactory.build()
```

### 함정

- factory-boy는 SQLAlchemy 통합(`SQLAlchemyModelFactory`)이 별도입니다. 비동기 세션과 결합하려면 약간의 설정이 필요합니다.
- 가짜 데이터를 너무 다양하게 만들면 테스트가 비결정적이 됩니다. `Faker` 시드를 고정하세요.

---

## 12.34 freezegun

> **한 줄**: 테스트에서 시간을 임의로 멈추거나 옮기는 라이브러리.
> **버전 (2026-04 기준)**: 1.5.x
> **설치**: `uv add --dev freezegun`
> **공식**: https://github.com/spulec/freezegun

### 왜 쓰는가

JWT 만료, 쿠폰 유효기간, "n일 전 가입자" 같은 시간 의존 로직은 시간을 고정하지 않고는 테스트가 불안정합니다.

### 최소 코드

```python
from datetime import datetime
from freezegun import freeze_time

@freeze_time("2026-04-25 10:00:00")
def test_now():
    assert datetime.now().year == 2026
    assert datetime.now().month == 4
```

### 컨텍스트 매니저

```python
with freeze_time("2026-12-31"):
    # 이 블록 안에서만 시간이 고정
    ...
```

### 함정

- C 라이브러리가 직접 시간을 읽으면 freezegun이 영향을 못 줍니다. 대부분의 Python 표준 라이브러리는 잘 작동합니다.

---

## I. 로깅·관측

## 12.35 logging (표준)

> **한 줄**: Python 표준 로깅 모듈.
> **설치**: 표준 라이브러리
> **공식**: https://docs.python.org/ko/3/library/logging.html

### 왜 쓰는가

`print`는 운영 환경에 부적합합니다. 로그 레벨, 포맷, 출력 대상(파일·표준출력·외부 시스템)을 분리해 관리하려면 `logging`이 필요합니다.

### 최소 코드

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logger.debug("디버그")
logger.info("정상 흐름")
logger.warning("주의")
logger.error("문제")
logger.exception("예외와 트레이스백 함께")  # except 블록 안에서
```

### 자주 쓰는 패턴: FastAPI에 통합

```python
import logging
from fastapi import FastAPI, Request

logger = logging.getLogger("api")
app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"-> {response.status_code}")
    return response
```

### 함정

- `print`로 디버깅하던 습관에서 벗어나는 데 시간이 걸립니다. 처음에는 `logger.info("...")`로만 시작하세요.
- 운영 환경에서 `DEBUG` 레벨을 켜두면 로그 폭주. 환경변수로 제어하세요.

---

## 12.36 structlog

> **한 줄**: 구조화 로그(JSON·키-값) 출력에 특화된 모던 로깅 라이브러리.
> **버전 (2026-04 기준)**: 24.x
> **설치**: `uv add structlog`
> **공식**: https://www.structlog.org/

### 왜 쓰는가

표준 `logging`의 메시지는 한 줄짜리 자유 형식 문자열입니다. 운영 환경에서 로그를 검색·분석하려면 JSON 같은 구조화된 형식이 훨씬 편합니다.

### 최소 코드

```python
import structlog

log = structlog.get_logger()

log.info("user_login", user_id=42, ip="1.2.3.4")
# {"event": "user_login", "user_id": 42, "ip": "1.2.3.4"}
```

### JSON 출력 설정

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
```

### 함정

- 표준 `logging`과의 결합 설정이 약간 복잡합니다. 처음에는 `logging`만 써도 충분.
- 컨테이너 환경(Docker, Kubernetes)에서 로그를 모아 분석한다면 거의 필수에 가깝습니다.

---

## 12.37 OpenTelemetry

> **한 줄**: 분산 시스템 전체에 걸친 추적·메트릭·로그를 수집하는 표준 도구 모음.
> **버전 (2026-04 기준)**: opentelemetry-instrumentation-fastapi 0.49.x
> **설치**: `uv add opentelemetry-distro opentelemetry-instrumentation-fastapi`
> **공식**: https://opentelemetry.io/

### 언제 쓰는가

- 서비스가 여러 개로 갈라져 한 요청이 어떤 경로를 거쳤는지 추적이 필요할 때.
- Datadog·New Relic·Honeycomb·Jaeger 같은 관측 시스템과 연동해야 할 때.

### 최소 코드 (자동 계측)

```bash
opentelemetry-instrument \
    --traces_exporter console \
    --service_name my-api \
    uv run uvicorn app.main:app
```

### 함정

- 본격적으로 도입하려면 백엔드(Jaeger, Tempo, Datadog 등)의 설정이 필요합니다. 입문자에게는 부담.
- 단일 모놀리식 앱이라면 Sentry나 Prometheus만으로도 충분할 때가 많습니다.

---

## 12.38 Sentry

> **한 줄**: 에러를 자동으로 수집해 대시보드로 보여주는 외부 서비스 + Python SDK.
> **버전 (2026-04 기준)**: sentry-sdk 2.18.x
> **설치**: `uv add "sentry-sdk[fastapi]"`
> **공식**: https://docs.sentry.io/platforms/python/integrations/fastapi/

### 왜 쓰는가

운영 환경에서 일어난 예외는 사용자가 알려주기 전에는 모릅니다. Sentry는 예외와 관련 컨텍스트(스택, 요청 정보, 사용자)를 자동으로 모아 대시보드로 띄워줍니다.

### 최소 코드

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://xxx@sentry.io/yyy",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,   # 10%만 추적 샘플링
    environment="production",
    release="my-api@1.2.3",
)

from fastapi import FastAPI
app = FastAPI()
```

이게 끝입니다. 이후 잡히지 않은 예외가 나면 자동으로 Sentry에 보고됩니다.

### 자주 쓰는 패턴: 사용자 정보 태깅

```python
import sentry_sdk

sentry_sdk.set_user({"id": user.id, "email": user.email})
sentry_sdk.set_tag("organization", org_id)
```

### 함정

- 무료 플랜은 한 달 이벤트 수가 제한됩니다. `traces_sample_rate`를 낮게 시작하세요.
- 민감 정보(비밀번호·토큰)가 컨텍스트에 섞여 들어갈 수 있습니다. `before_send` 훅으로 필터링.

---

## 12.39 Prometheus + prometheus-fastapi-instrumentator

> **한 줄**: 시계열 메트릭을 표준 형식으로 수집·노출하는 도구 + FastAPI 통합 라이브러리.
> **버전 (2026-04 기준)**: prometheus-fastapi-instrumentator 7.0.x
> **설치**: `uv add prometheus-fastapi-instrumentator`
> **공식**: https://github.com/trallnag/prometheus-fastapi-instrumentator, https://prometheus.io/

### 최소 코드

```python
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)
# /metrics 엔드포인트가 자동으로 만들어짐
```

이후 Prometheus 서버를 띄우고 이 엔드포인트를 스크레이프하게 설정하면 응답 시간·요청 수·상태 코드 분포가 모두 수집됩니다.

### 자주 쓰는 패턴: 사용자 정의 메트릭

```python
from prometheus_client import Counter

login_attempts = Counter("login_attempts_total", "로그인 시도 수", ["status"])

@app.post("/login")
async def login(...):
    if ok:
        login_attempts.labels(status="ok").inc()
    else:
        login_attempts.labels(status="fail").inc()
```

### 함정

- `/metrics` 엔드포인트는 외부에 그대로 노출하지 마세요. 내부 네트워크나 인증 미들웨어 뒤에 두세요(메트릭으로 시스템 정보가 새어나갈 수 있습니다).
- Grafana로 시각화하면 더 강력합니다.

---

## J. 설정·환경

## 12.40 pydantic-settings (재방문)

12.10에서 다뤘습니다. 이 가이드의 표준 선택입니다.

## 12.41 dynaconf (옵션)

> **한 줄**: 환경별 설정 파일·환경변수·Vault·Redis 등 여러 출처를 통합 관리하는 설정 라이브러리.
> **버전 (2026-04 기준)**: 3.2.x
> **설치**: `uv add dynaconf`
> **공식**: https://www.dynaconf.com/

### 언제 쓰는가

- 개발/스테이징/운영 환경에 따라 설정 파일을 분리·계승하고 싶을 때.
- TOML/YAML/INI 파일을 함께 쓰고 싶을 때.
- 비밀 관리(Vault, AWS Secrets Manager)를 통합하고 싶을 때.

### 이 가이드에서 안 쓰는 이유

- 입문자가 다루기에는 개념이 많습니다(`settings.toml`, `.secrets.toml`, `dynaconf_merge` 등).
- 대부분의 작은 프로젝트는 pydantic-settings로 충분합니다.

### 최소 코드

```python
from dynaconf import Dynaconf

settings = Dynaconf(
    settings_files=["settings.toml", ".secrets.toml"],
    environments=True,    # [development], [production] 섹션 인식
    envvar_prefix="MYAPP",
)

print(settings.DATABASE_URL)
```

---

## K. 캐시·큐

## 12.42 Redis (redis-py)

> **한 줄**: 가장 널리 쓰이는 인메모리 키-값 저장소 + Python 비동기 클라이언트.
> **버전 (2026-04 기준)**: redis 5.2.x
> **설치**: `uv add redis`
> **공식**: https://redis.io/, https://redis.readthedocs.io/

### 왜 쓰는가

- 캐시: DB 부하를 줄임.
- 세션 저장: 여러 서버 인스턴스가 같은 세션 정보를 공유.
- 큐 브로커: arq, Celery의 백엔드.
- Pub/Sub, 분산 잠금, Rate Limiting.

### 최소 코드 (비동기)

```python
import redis.asyncio as redis

r = redis.from_url("redis://localhost:6379/0")

await r.set("key", "value", ex=60)   # 60초 TTL
v = await r.get("key")
print(v)                              # b'value'

await r.aclose()
```

### Docker로 띄우기

```bash
docker run --name dev-redis -p 6379:6379 -d redis:7-alpine
```

### 자주 쓰는 패턴: Rate Limit (간단)

```python
async def rate_limit(user_id: int, max_per_min: int = 60) -> bool:
    key = f"rl:{user_id}:{int(time.time() // 60)}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    return count <= max_per_min
```

### 함정

- Redis는 기본적으로 메모리 위에 있습니다. 정전·재시작에 데이터가 사라질 수 있습니다(설정으로 영속화 가능).
- 키 네임스페이스를 합의하지 않으면 여러 기능이 같은 키를 덮어씁니다. `app:cache:user:42` 같이 접두사 규칙을 정하세요.

---

## 12.43 Memcached (짧게)

> **한 줄**: Redis보다 더 가벼운 인메모리 캐시. 데이터 구조가 단순(문자열 키-값만).
> **설치**: `uv add pymemcache`
> **공식**: https://memcached.org/

### Redis와의 차이

- Redis: 자료구조 풍부(List, Set, Hash, Sorted Set), 영속화 가능, Pub/Sub.
- Memcached: 단순 키-값, 메모리 전용.

대부분의 새 프로젝트는 Redis를 씁니다. 기존 Memcached 인프라를 유지해야 할 때만 고려.

---

## L. 메일·파일·기타

## 12.44 fastapi-mail

> **한 줄**: FastAPI에서 SMTP·HTML 템플릿 메일을 비동기로 보내는 라이브러리.
> **버전 (2026-04 기준)**: 1.4.x
> **설치**: `uv add fastapi-mail`
> **공식**: https://sabuhish.github.io/fastapi-mail/

### 최소 코드

```python
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

conf = ConnectionConfig(
    MAIL_USERNAME="user",
    MAIL_PASSWORD="pass",
    MAIL_FROM="noreply@modapl.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.example.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

fm = FastMail(conf)

async def send_welcome(email: str):
    message = MessageSchema(
        subject="환영합니다",
        recipients=[email],
        body="<h1>환영합니다!</h1>",
        subtype=MessageType.html,
    )
    await fm.send_message(message)
```

### 함정

- SMTP 서버를 직접 운영하기보다 SendGrid·Mailgun·AWS SES 같은 서비스의 SMTP 게이트웨이를 쓰는 게 안정적입니다(스팸 차단·DKIM·SPF 자동 처리).

---

## 12.45 python-multipart

> **한 줄**: 폼 데이터·파일 업로드 파싱 라이브러리. FastAPI 내부 의존성.
> **버전 (2026-04 기준)**: 0.0.20
> **설치**: `uv add python-multipart` (FastAPI에서 `Form`/`File` 사용 시 자동 요구)
> **공식**: https://github.com/Kludex/python-multipart

### 왜 쓰는가

FastAPI에서 `Form(...)`, `UploadFile`을 쓰면 이 라이브러리가 필요합니다. 직접 임포트할 일은 거의 없고 그냥 깔려 있어야 합니다.

### 사용 예 (FastAPI에서)

```python
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()

@app.post("/upload")
async def upload(note: str = Form(""), file: UploadFile = File(...)):
    contents = await file.read()
    return {"filename": file.filename, "size": len(contents), "note": note}
```

---

## 12.46 aiofiles

> **한 줄**: 비동기 파일 IO 라이브러리. 비동기 컨텍스트에서 파일을 안전하게 읽고 쓴다.
> **버전 (2026-04 기준)**: 24.1.x
> **설치**: `uv add aiofiles`
> **공식**: https://github.com/Tinche/aiofiles

### 왜 쓰는가

비동기 함수 안에서 일반 `open()`을 쓰면 디스크 IO가 이벤트 루프를 막습니다. aiofiles는 그 부분을 비동기로 만듭니다.

### 최소 코드

```python
import aiofiles

async def save(path: str, data: bytes):
    async with aiofiles.open(path, "wb") as f:
        await f.write(data)

async def load(path: str) -> str:
    async with aiofiles.open(path, "r") as f:
        return await f.read()
```

### 함정

- 작은 텍스트 파일을 한 번 읽는 정도라면 일반 `open()`도 큰 문제 없습니다. **반복적이거나 큰 파일**일 때 차이가 납니다.

---

## 12.47 boto3 / aioboto3

> **한 줄**: AWS Python SDK. boto3는 동기, aioboto3는 비동기.
> **버전 (2026-04 기준)**: boto3 1.35.x, aioboto3 13.x
> **설치**:
> - `uv add boto3`
> - `uv add aioboto3`
> **공식**: https://boto3.amazonaws.com/v1/documentation/api/latest/index.html

### 최소 코드 (S3 업로드, 비동기)

```python
import aioboto3

session = aioboto3.Session()

async def upload(file_bytes: bytes, key: str):
    async with session.client("s3", region_name="ap-northeast-2") as s3:
        await s3.put_object(Bucket="my-bucket", Key=key, Body=file_bytes)
```

### 자주 쓰는 패턴: Presigned URL

직접 업로드를 받지 말고, 클라이언트가 S3로 바로 올리도록 서명된 URL만 발급:

```python
async with session.client("s3") as s3:
    url = await s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": "my-bucket", "Key": "uploads/abc.png"},
        ExpiresIn=600,
    )
```

### 함정

- 자격 증명: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` 환경 변수 또는 IAM 역할.
- 동기 boto3와 비동기 aioboto3를 한 코드베이스에 섞으면 혼란스럽습니다. 가능하면 한쪽으로 통일.
- aioboto3는 boto3 위에 비동기 래퍼라 boto3 버전과 호환성을 맞춰야 합니다.

---

## 12.48 Pillow

> **한 줄**: 가장 널리 쓰이는 Python 이미지 처리 라이브러리.
> **버전 (2026-04 기준)**: 11.0.x
> **설치**: `uv add Pillow`
> **공식**: https://pillow.readthedocs.io/

### 최소 코드 — 썸네일 만들기

```python
from PIL import Image
from io import BytesIO

def make_thumbnail(image_bytes: bytes, size=(200, 200)) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail(size)
    out = BytesIO()
    img.save(out, format="JPEG", quality=85)
    return out.getvalue()
```

### 함정

- Pillow는 동기·CPU 바운드입니다. 큰 이미지를 비동기 라우터에서 직접 처리하면 이벤트 루프가 막힙니다 → `anyio.to_thread.run_sync` 또는 백그라운드 작업(arq)으로 옮기세요.
- 일부 포맷(WebP, AVIF)은 시스템 라이브러리(`libwebp` 등)가 있어야 동작합니다.

---

## 12.49 uuid (표준) / ulid-py

> **한 줄**: 분산 환경에서 충돌하지 않는 식별자를 만드는 도구.
> **공식**: https://docs.python.org/ko/3/library/uuid.html, https://github.com/ahawker/ulid

### uuid (표준 라이브러리)

```python
import uuid

# 가장 흔한 v4 (랜덤)
uid = uuid.uuid4()
print(uid)            # UUID('e58ed763-928c-4155-bee9-fdbaaadc15f3')
print(str(uid))       # 문자열로

# v7 (Python 3.14에서 추가, 시간순 정렬 가능)
uid7 = uuid.uuid7()
```

### ulid

```python
import ulid

uid = ulid.new()
print(str(uid))      # 26자, 시간 + 랜덤. 정렬 가능.
```

### 무엇을 쓸 것인가

- DB 기본 키로 정수 자동 증가가 부담스러우면 UUID v7 또는 ULID(둘 다 시간순 정렬 가능).
- 외부에 노출하는 ID에 정수를 쓰면 "총 사용자 수"가 추측됩니다 → UUID 권장.
- 단순 토큰·임시 식별자라면 v4로 충분.

### 함정

- UUID v4는 **시간 정렬이 안 됩니다**. DB 인덱스에 부담을 줄 수 있습니다 → v7 또는 ULID.
- ulid-py는 외부 라이브러리이고, Python 3.14에 `uuid.uuid7()`이 추가됐으므로 3.14 이상 새 프로젝트는 v7을 검토(3.13 이하는 ULID 또는 외부 라이브러리 사용).

---

## 12.50 python-slugify

> **한 줄**: 한글·기타 문자를 URL-safe한 영문 슬러그로 변환.
> **버전 (2026-04 기준)**: 8.0.x
> **설치**: `uv add python-slugify`
> **공식**: https://github.com/un33k/python-slugify

### 최소 코드

```python
from slugify import slugify

print(slugify("FastAPI 가이드 — Hello World"))
# fastapi-gaideu-hello-world

print(slugify("Café & Bar"))
# cafe-bar
```

### 자주 쓰는 패턴

블로그 글 URL을 만들 때:

```python
slug = slugify(post.title)
existing = await db.execute(select(Post).where(Post.slug == slug))
if existing.scalar_one_or_none():
    slug = f"{slug}-{post.id}"
```

### 함정

- 한글 트랜슬리터레이션은 완벽하지 않습니다. 한국어 SEO가 중요하다면 그냥 한글 + 퍼센트 인코딩이 더 자연스러울 때도 있습니다.

---

## M. WebSocket·SSE

## 12.51 FastAPI WebSocket

> **한 줄**: FastAPI에 내장된 WebSocket 라우팅. 별도 설치 불필요.
> **공식**: https://fastapi.tiangolo.com/advanced/websockets/

### 최소 코드

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        print("client disconnected")
```

### 함정

- 기본 ws 라우터는 단일 프로세스 메모리에 연결 정보를 유지합니다. 워커가 여러 개면 메시지 브로드캐스트가 갈라집니다 → `broadcaster` 또는 Redis Pub/Sub 필요.
- 인증은 첫 메시지로 토큰을 받거나, 쿠키·헤더로 검증.

---

## 12.52 broadcaster

> **한 줄**: 여러 워커 사이에서 WebSocket 메시지를 브로드캐스트하는 라이브러리.
> **버전 (2026-04 기준)**: 0.3.x
> **설치**: `uv add "broadcaster[redis]"`
> **공식**: https://github.com/encode/broadcaster

### 짧은 사용 예

```python
from broadcaster import Broadcast

broadcast = Broadcast("redis://localhost:6379")

async def chat_room(ws):
    async with broadcast.subscribe(channel="chatroom") as subscriber:
        async for event in subscriber:
            await ws.send_text(event.message)
```

이 가이드의 범위 밖. 실시간 기능이 필요하면 별도 학습.

---

## N. CLI·관리 도구

## 12.53 typer

> **한 줄**: FastAPI 작성자가 만든, 타입 힌트 기반 CLI 라이브러리.
> **버전 (2026-04 기준)**: 0.13.x
> **설치**: `uv add typer`
> **공식**: https://typer.tiangolo.com/

### 왜 쓰는가

데이터 임포트, 마이그레이션 보조, 일회성 관리 명령을 위한 작은 CLI를 만들 때 매우 편합니다. FastAPI와 사고방식이 같습니다(타입 힌트 → 자동).

### 최소 코드

```python
import typer

app = typer.Typer()

@app.command()
def hello(name: str, count: int = 1):
    """이름을 count번 출력합니다."""
    for _ in range(count):
        typer.echo(f"안녕, {name}!")

if __name__ == "__main__":
    app()
```

실행:

```bash
uv run python cli.py hello Alice --count 3
uv run python cli.py hello --help
```

### 자주 쓰는 패턴: DB 시드 스크립트

```python
import asyncio
import typer
from app.db import SessionLocal
from app.models import User

cli = typer.Typer()

@cli.command()
def seed_users(n: int = 10):
    """샘플 사용자 n명을 만듭니다."""
    async def _run():
        async with SessionLocal() as s:
            for i in range(n):
                s.add(User(email=f"user{i}@a.com"))
            await s.commit()
    asyncio.run(_run())

if __name__ == "__main__":
    cli()
```

### 함정

- 비동기 명령을 직접 정의하기보다 `asyncio.run()`으로 감싸는 패턴이 안전합니다.

---

## 12.54 fastapi-cli

> **한 줄**: FastAPI 공식 CLI. `fastapi dev` 한 줄로 개발 서버를 띄운다.
> **버전 (2026-04 기준)**: 0.0.7+
> **설치**: FastAPI 0.111+에서 자동 포함
> **공식**: https://fastapi.tiangolo.com/fastapi-cli/

### 사용 예

```bash
# 개발 서버 (자동 재시작)
uv run fastapi dev app/main.py

# 운영 서버 (재시작 없음)
uv run fastapi run app/main.py
```

내부적으로 `uvicorn`을 호출합니다. 직접 `uvicorn ...`을 치는 것과 결과는 같지만, FastAPI 친화적인 기본값이 적용됩니다.

### 함정

- 운영 환경에서는 워커를 여러 개 띄웁니다 — 이 가이드의 표준은 **Uvicorn 자체 멀티워커**(`uvicorn ... --workers N --proxy-headers`) 입니다(09 배포 가이드 참고). `gunicorn -k uvicorn.workers.UvicornWorker` 패턴은 deprecated 되어 별도 패키지(`uvicorn-worker`)로 분리되었습니다.

---

## O. 운영 라이브러리

## 12.55 Uvicorn 멀티워커 / Gunicorn (선택)

> **한 줄**: 비동기 FastAPI 앱은 **Uvicorn 자체 멀티워커**(0.30+ 내장)가 표준. Gunicorn 의 운영 기능(graceful reload, preload)이 필요하면 별도 패키지 `uvicorn-worker` 로 분리해 사용.
> **버전 (2026-04 기준)**: Uvicorn 0.30+, Gunicorn 23.x, uvicorn-worker (PyPI 별도 패키지)
> **설치**: 표준 — `uv add "uvicorn[standard]>=0.30"`. Gunicorn 경로를 쓰려면 `uv add "gunicorn>=23" uvicorn-worker`.
> **공식**: https://www.uvicorn.org/ , https://gunicorn.org/

### 왜 멀티워커?

Uvicorn 한 프로세스로는 단일 CPU만 활용합니다. 워커를 여러 개 띄우면 GIL 한계를 우회해 멀티코어를 사용합니다. 비동기 앱에서는 한 워커 안에서도 동시 처리량이 크므로 **워커 수 = CPU 코어 수** 정도가 출발점입니다(`(2 * CPU) + 1` 공식은 동기 WSGI 시절 가이드).

### 표준: Uvicorn 한 줄

```bash
uv run uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 \
    --workers 4 \
    --proxy-headers --forwarded-allow-ips='*'
```

- `--workers 4`: 워커 4개. 비동기 앱은 보통 CPU 코어 수 정도가 시작점.
- `--proxy-headers --forwarded-allow-ips`: nginx/리버스 프록시 뒤에서 `X-Forwarded-Proto`/`X-Forwarded-For` 신뢰. 없으면 scheme/IP 가 잘못 잡힙니다.

### Gunicorn 을 쓰고 싶다면 (선택)

`uv add uvicorn-worker` 후:

```bash
uv run gunicorn app.main:app \
    -k uvicorn_worker.UvicornWorker \
    -w 4 -b 0.0.0.0:8000 \
    --timeout 60 \
    --forwarded-allow-ips='127.0.0.1' \
    --access-logfile - --error-logfile -
```

> **주의**: 옛 `gunicorn -k uvicorn.workers.UvicornWorker` 는 Uvicorn 0.30 부터 deprecated, 0.31 에서 별도 패키지(`uvicorn-worker`)로 분리되었습니다. 위처럼 `uvicorn_worker.UvicornWorker` 를 쓰세요.

### 자주 쓰는 패턴: 컨테이너화

Dockerfile 의 CMD 한 줄:

```dockerfile
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
```

### 함정

- 워커 수는 메모리·CPU에 따라 정합니다. 무작정 늘리면 메모리 사용량이 비례해서 증가.
- 비동기 코드의 GIL 우회 효과를 보려면 워커 수가 의미 있게 1보다 커야 합니다.
- Windows에서는 Gunicorn이 동작하지 않습니다. Hypercorn을 검토하거나, Linux/WSL에서 작업.

---

## 12.56 uvloop

> **한 줄**: 표준 asyncio 이벤트 루프를 더 빠른 C 구현으로 교체.
> **버전 (2026-04 기준)**: 0.21.x
> **설치**: `uv add uvloop` (또는 `uvicorn[standard]`에 포함)
> **공식**: https://github.com/MagicStack/uvloop

### 왜 쓰는가

같은 코드의 처리량을 보통 2~4배 향상합니다. Uvicorn은 uvloop이 깔려 있으면 자동으로 사용.

### 함정

- Windows에서는 동작하지 않습니다(Linux/macOS만).
- 대부분의 경우 명시적으로 임포트할 일이 없습니다 — `uvicorn[standard]`을 쓰면 자동.

---

## 12.57 httptools

> **한 줄**: Node.js의 `http-parser` 기반 C HTTP 파서. Uvicorn의 빠른 HTTP 파싱.
> **버전 (2026-04 기준)**: 0.6.x
> **설치**: `uvicorn[standard]`에 포함
> **공식**: https://github.com/MagicStack/httptools

### 함정

- 직접 임포트할 일은 거의 없습니다. `uvicorn[standard]`을 쓰면 자동.

---

## 12.58 uvicorn[standard]가 무엇을 묶는가

> **`uv add "uvicorn[standard]"` 한 줄로 따라오는 것**:
> - **uvloop**: 빠른 이벤트 루프 (Linux/macOS만)
> - **httptools**: 빠른 HTTP 파서
> - **websockets** 또는 **wsproto**: WebSocket 지원
> - **watchfiles**: `--reload` 시 파일 변경 감지
> - **PyYAML**: 설정 파일 로딩
> - **python-dotenv**: `.env` 파일 자동 로드
>
> 그냥 `uv add uvicorn`만 쓰면 위 부가 기능 없이 가장 가벼운 형태가 깔립니다. **개발/운영 모두 `[standard]`를 권장**합니다.

---

## 12.59 watchfiles

> **한 줄**: 파일 변경을 감지해 서버를 자동 재시작.
> **버전 (2026-04 기준)**: 0.24.x
> **설치**: `uvicorn[standard]`에 포함
> **공식**: https://watchfiles.helpmanual.io/

### 사용

`uv run uvicorn app.main:app --reload`의 `--reload`가 watchfiles를 씁니다. 직접 임포트할 일은 거의 없습니다.

### 함정

- `--reload`는 개발용입니다. 운영 환경에서 켜면 안 됩니다(매번 코드 변경 감시 비용 + 안전성 문제).

---

## 12.60 자주 묻는 질문

**Q. 이 라이브러리들을 모두 한 프로젝트에 넣어야 하나요?**
**아닙니다.** 새 프로젝트의 시작 묶음(스타터 셋)은 다음 정도면 충분합니다.

```bash
uv add fastapi "uvicorn[standard]" pydantic-settings
uv add "sqlalchemy[asyncio]>=2.0" alembic asyncpg
uv add pyjwt bcrypt
uv add --dev pytest pytest-asyncio httpx
uv add --dev ruff mypy
```

이후 **그 기능이 진짜 필요해질 때** 하나씩 추가하세요. Sentry는 운영 시작 직전, Redis는 캐시·rate limit이 필요할 때, Celery/arq는 무거운 백그라운드 작업이 생길 때.

**Q. 버전을 언제 업그레이드해야 하나요?**
- 보안 패치(patch 버전): 즉시.
- 마이너 버전: 릴리스 노트 확인 후 월 단위.
- 메이저 버전: 별도 브랜치에서 검증 후. SQLAlchemy 1.x → 2.x, Pydantic v1 → v2 같은 큰 변화는 시간을 잡고 진행.

**Q. 어떤 라이브러리를 믿어도 되나요?**
- GitHub star 수와 최근 커밋 시점
- PyPI의 다운로드 통계
- 공식 FastAPI 문서·커뮤니티에서 추천되는지
- 라이선스(MIT/BSD가 안전)

**Q. 라이브러리 충돌이 나면?**
`uv lock`이 자동으로 호환 버전을 찾습니다. 그래도 안 풀리면 `uv lock --upgrade-package <이름>`으로 단일 패키지를 갱신하거나, `pyproject.toml`의 버전 범위를 조정하세요.

**Q. 의존성이 너무 많아지면 문제 있나요?**
빌드·이미지 크기·보안 관리 부담이 커집니다. `uv tree`로 의존성 트리를 가끔 확인하고, GitHub의 Dependabot이나 `renovate`로 자동 PR을 받으세요.

---

## 12.61 이 챕터 요약

- 이 가이드의 표준 스택 = **FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic + PyJWT + bcrypt + uv + uvicorn[standard]**.
- 그 외 라이브러리는 **필요할 때** 사전(이 챕터)에서 펼쳐 보고 도입.
- 코드 품질: **ruff + mypy + pre-commit**가 입문 직후 도입할 만한 1순위.
- 비동기 작업: 가벼우면 **arq**, 무겁고 큰 생태계가 필요하면 **Celery**.
- 관측: 작은 팀의 시작점은 **Sentry** 하나로 충분.
- 운영: **Gunicorn + UvicornWorker**가 표준 패턴. `uvicorn[standard]`만 깔아도 uvloop/httptools 같은 성능 부품이 자동 포함.
- 모든 도구는 자기 자리에 있을 때 가장 빛납니다. **무엇을 쓰지 않을지** 결정하는 것이 무엇을 쓸지 결정하는 것만큼 중요합니다.

---

← [11. 종합 예제 2 — Blog API](11-project-blog-api.md) | [README로 돌아가기](../README.md)
