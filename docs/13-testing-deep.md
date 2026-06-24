# 13. 테스트 작성 심화 — pytest로 더 깊게

> **이 챕터의 목표**
> - 07·08장에서 한 번 써본 `pytest` + `httpx.AsyncClient` 통합 테스트를, **재사용 가능한 픽스처 설계**로 한 단계 끌어올린다.
> - 픽스처의 **스코프**(function / module / session)와 `autouse` 의 의미를 손에 익히고, 의존성 오버라이드를 복습한다.
> - `@pytest.mark.parametrize` 로 **한 테스트 함수를 여러 입력으로** 반복 실행해, 표 하나로 수십 개의 케이스를 덮는 법을 배운다.
> - 에러·예외 케이스를 의도적으로 테스트한다 — `pytest.raises` 로 "예외가 나는 게 정상" 인 경우를, 상태 코드(404 / 422 / 503)로 HTTP 에러를 검증한다.
> - **외부 HTTP 호출을 모킹**한다. 진짜 네트워크 없이 `monkeypatch` 로 외부 함수를 가짜로 바꿔치워, 우리 코드만 격리해서 빠르고 안정적으로 검증한다.
> - 테스트 파일을 어떻게 나눌지(**조직화**)와 커버리지 측정(`pytest-cov`) 의 존재를 익힌다.

> **소요 시간**: 2~4시간

> **전제**: 07·08장을 따라 pytest 통합 테스트를 한 번 써봤다. `async def test_...`, `httpx.AsyncClient`, `ASGITransport`, `app.dependency_overrides` 라는 단어를 한 번씩 만나봤다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 보세요. 처음 보는 용어는 한두 줄만 읽고 본문으로 돌아오면 됩니다.

---

## 13.1 왜 테스트를 "더 깊게" 배우는가

07장에서 우리는 통합 테스트 17개를 썼다. 그때의 패턴은 단순했다.

- `conftest.py` 에 `client` 픽스처 하나를 두고,
- 테스트마다 `await client.post(...)` 로 요청을 보내고,
- `assert res.status_code == ...` 로 응답을 확인했다.

이 패턴은 강력하다. 하지만 프로젝트가 자라면 다음 질문들이 차례로 찾아온다.

- "비슷한 검증을 입력만 바꿔 열 번 반복하고 있다. 복사-붙여넣기 말고 더 좋은 방법이 없을까?"
- "이 엔드포인트는 외부 결제 API 를 부른다. 테스트할 때마다 진짜 결제가 일어나면 안 되는데?"
- "예외가 **나야 정상** 인 경우는 어떻게 테스트하지?"
- "픽스처를 매 테스트마다 새로 만들면 느리다. 한 번만 만들어 공유할 순 없나?"

이 챕터는 그 질문들에 하나씩 답한다. 핵심 도구는 다섯 가지다.

1. **픽스처 설계와 스코프** — 무엇을, 얼마나 자주 만들고 정리할지.
2. **파라미터화**(`@pytest.mark.parametrize`) — 한 함수로 여러 입력을 덮기.
3. **예외/에러 케이스** — `pytest.raises` 와 상태 코드 단언.
4. **외부 호출 모킹**(`monkeypatch`) — 네트워크 없이 빠르고 안정적으로.
5. **조직화와 커버리지** — 파일을 나누는 법, 빠진 줄을 찾는 법.

> **이 챕터의 대상 앱은 일부러 작다.** 07장처럼 DB·Alembic 까지 끌고 오면 "테스트 기법" 이 그 무게에 묻힌다. 그래서 이번에는 **DB 없이 인메모리 dict 하나만 쓰는 작은 API** 를 대상으로, 오롯이 테스트 기법에만 집중한다.

---

## 13.2 큰 그림 — 무엇을 테스트할 것인가

대상 앱은 세 종류의 엔드포인트를 가진다. 각각이 **다른 테스트 기법** 을 끌어내도록 골랐다.

| 메서드 | 경로 | 설명 | 이 엔드포인트로 배우는 것 |
|--------|------|------|---------------------------|
| `GET` | `/health` | 헬스 체크 | 가장 단순한 테스트 |
| `POST` | `/quotes` | 명언 생성(검증) | 파라미터화·에러 케이스(422) |
| `GET` | `/quotes/{id}` | 단건 조회 | 404 케이스 |
| `GET` | `/quotes` | 전체 목록 | 상태 격리(픽스처) |
| `GET` | `/rate/{code}` | **외부 환율 API 호출** | 외부 호출 모킹 |

폴더 구조는 다음과 같다. 07장보다 훨씬 가볍다.

```
13-TestingDeep/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py            ← FastAPI 앱 (health / quotes / rate)
│   └── services.py        ← 외부 HTTP 호출 격리 (fetch_rate)
└── tests/
    ├── __init__.py
    ├── conftest.py        ← AsyncClient 픽스처 + 상태 초기화(autouse)
    ├── test_health_and_quotes.py
    ├── test_parametrize.py
    └── test_rate_mock.py
```

각 파일의 한 줄 정의:

| 파일 | 책임 한 줄 |
|------|------------|
| `app/main.py` | FastAPI 앱·스키마·엔드포인트. 인메모리 저장소 하나를 둔다 |
| `app/services.py` | 외부 세계와 통신하는 함수(`fetch_rate`)만 격리해 둔다 |
| `tests/conftest.py` | 공통 픽스처(`client`, `sample_quote`, 상태 초기화)를 정의한다 |
| `tests/test_health_and_quotes.py` | 픽스처·기본 CRUD·404/422·상태 격리 |
| `tests/test_parametrize.py` | 파라미터화·`pytest.raises` |
| `tests/test_rate_mock.py` | 외부 호출 모킹 3종 |

---

## 13.3 프로젝트 만들기

```bash
mkdir 13-TestingDeep
cd 13-TestingDeep

uv init --bare
rm -f hello.py main.py

uv add fastapi "uvicorn[standard]" httpx
uv add --dev pytest pytest-asyncio httpx

mkdir -p app tests
touch app/__init__.py tests/__init__.py
```

`pyproject.toml` 의 핵심은 다음과 같다(07장과 같은 모양).

```toml
[project]
name = "testing-deep"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "httpx>=0.27",
]

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

> **`httpx` 가 두 군데 적힌 이유** : 대상 앱이 런타임에 외부 API 를 부를 때도 `httpx` 를 쓰고(`dependencies`), 테스트에서 `AsyncClient` 로 앱을 호출할 때도 `httpx` 를 쓴다(`dev`). 둘 다 같은 패키지지만 "런타임 의존성" 과 "개발 의존성" 양쪽에서 필요하다는 뜻을 명시해 둔 것이다.

> **`asyncio_mode = "auto"` 복습** : 이 한 줄이 있으면 `async def test_...` 모양의 테스트가 `@pytest.mark.asyncio` 데코레이터 없이도 자동으로 비동기로 실행된다. 07장에서 이미 켜 둔 옵션이다.

---

## 13.4 대상 앱 — `app/services.py` (외부 호출을 한곳에 가둔다)

모킹을 쉽게 하려면, 외부 세계와 통신하는 코드를 **한 함수에 가둬 두는 설계** 가 먼저다. 그래서 환율 API 호출을 `app/services.py` 의 `fetch_rate` 하나로 모은다.

```python
# app/services.py
import httpx

RATES_API_BASE = "https://api.example.com/rates"
HTTP_TIMEOUT = 5.0


class RateUnavailableError(Exception):
    """환율 정보를 가져오지 못했을 때 던지는 우리 도메인 예외."""


async def fetch_rate(code: str) -> float:
    """통화 코드(예: "USD")에 대한 원화 환율을 외부 API 에서 가져온다."""
    url = f"{RATES_API_BASE}/{code.upper()}"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as http:
            res = await http.get(url)
            res.raise_for_status()
            data = res.json()
            return float(data["rate"])
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        raise RateUnavailableError(str(exc)) from exc
```

이 작은 모듈에 두 가지 설계 결정이 들어 있다.

### 13.4.1 외부 호출의 "입구" 를 하나로 좁힌다

라우터가 `httpx.AsyncClient(...).get(...)` 을 **직접** 부르면, 테스트할 때 그 라우터 안의 네트워크 호출을 가로채기가 까다롭다. 대신 모든 외부 호출이 `fetch_rate` 한 함수를 **반드시 거치게** 해 두면, 테스트는 이 함수 하나만 가짜로 바꾸면 된다.

> **이것이 "모킹 가능한 설계" 다.** 모킹은 테스트 기법이기 전에 **설계 습관**이다. "외부와 통신하는 코드를 얇은 함수 하나로 격리" 해 두면, 나중에 그 함수만 갈아끼우거나 가짜로 만들 수 있다. 07장에서 "라우터는 HTTP 만, crud 는 DB 만" 이라고 한 것과 같은 정신이다.

### 13.4.2 저수준 예외를 도메인 예외로 정규화한다

`httpx` 는 상황에 따라 여러 종류의 예외를 던진다(타임아웃, 연결 실패, 4xx/5xx 등). 응답 형식이 깨지면 `KeyError`·`ValueError` 도 날 수 있다. 이걸 라우터까지 그대로 흘려보내면 라우터가 너무 많은 예외를 알아야 한다.

그래서 `fetch_rate` 는 이 모두를 잡아 **우리 도메인 예외 하나**(`RateUnavailableError`)로 감싼다. 라우터는 이 예외 하나만 알면 된다(13.5 에서 503 으로 변환한다).

> **`raise ... from exc` 가 뭔가요?** "이 예외는 저 예외(`exc`)가 원인이었다" 를 파이썬에 알려주는 문법이다. 로그·트레이스백에 원래 원인이 함께 남아 디버깅이 쉬워진다.

---

## 13.5 대상 앱 — `app/main.py`

이제 앱 본체다. 인메모리 저장소 하나, 스키마 셋, 엔드포인트 다섯이 전부다.

```python
# app/main.py
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, Field

from app import services

app = FastAPI(
    title="Testing Deep",
    version="0.1.0",
    description="13장 테스트 작성 심화 예제 — 픽스처, 파라미터화, 에러 케이스, 외부 호출 모킹.",
)


# --- 인메모리 저장소 ---
_quotes: dict[int, "QuoteRead"] = {}
_next_id = 1


def reset_state() -> None:
    """인메모리 저장소를 초기 상태로 되돌린다(테스트 픽스처가 호출)."""
    global _next_id
    _quotes.clear()
    _next_id = 1


# --- 스키마 ---
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


# --- 의존성: 외부 호출 함수를 주입 가능한 모양으로 ---
def get_rate_fetcher():
    return services.fetch_rate


# --- 엔드포인트 ---
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
```

테스트 관점에서 짚을 점 세 가지.

### 13.5.1 `reset_state()` — 테스트가 비울 수 있는 상태

DB 가 없으니 데이터는 모듈 수준 `_quotes` dict 에 산다. 모듈 수준 변수는 **프로세스가 사는 동안 계속 남는다**. 테스트 A 가 만든 명언이 테스트 B 에 그대로 보이면, 테스트가 서로 간섭해 깨진다.

그래서 "저장소를 초기 상태로 되돌리는" `reset_state()` 함수를 노출해 둔다. 테스트는 매번 시작 전에 이 함수를 불러 **빈 저장소** 라는 같은 출발선을 보장한다(13.7 의 `reset_store` 픽스처).

> **07장은 왜 이게 필요 없었나?** 07장은 매 테스트마다 새 in-memory SQLite 엔진을 `engine` 픽스처가 새로 만들었다. 즉 "상태를 새로 만드는" 일을 DB 계층이 해 줬다. 이번엔 DB 가 없으니 우리가 직접 비워야 한다. 본질은 같다 — **테스트 격리**.

### 13.5.2 `get_rate_fetcher` — 외부 호출을 의존성으로

`/rate/{code}` 는 `services.fetch_rate` 를 직접 부르지 않고, `Depends(get_rate_fetcher)` 로 **함수를 주입**받아 부른다. 왜 이렇게 한 단계 우회할까? 테스트에서 `app.dependency_overrides[get_rate_fetcher]` 로 이 함수를 통째로 갈아끼우는 길이 열리기 때문이다(13.9 의 방법 2). `monkeypatch` 방식과 함께, **모킹의 두 갈래**를 모두 보여주기 위한 설계다.

### 13.5.3 에러를 상태 코드로 일관 변환

- 통화 코드 형식이 틀리면 → **422**(외부 호출 전에 막는다).
- 외부가 실패해 `RateUnavailableError` 가 올라오면 → **503 Service Unavailable**.

"내 잘못(클라이언트 입력)" 은 4xx, "남의 잘못(외부 서비스)" 은 5xx 로 가른다. 이 구분을 테스트로 못박을 것이다.

> **`status.HTTP_422_...` 대신 그냥 `422` 를 쓴 이유** : FastAPI/Starlette 버전에 따라 422 상수의 이름이 달라지는 시기가 있었다(`UNPROCESSABLE_ENTITY` ↔ `UNPROCESSABLE_CONTENT`). 숫자 `422` 로 직접 쓰면 버전과 무관하게 안전하다. 다른 코드(201/404/503)는 이름이 안정적이라 `status.` 상수를 그대로 쓴다.

---

## 13.6 픽스처 설계와 스코프

이제 테스트의 토대인 **픽스처**를 본격적으로 들여다본다.

### 13.6.1 픽스처 다시 보기

픽스처는 "테스트가 시작될 때 미리 준비하고, 끝날 때 정리할 자원" 을 함수로 묶은 것이다. 테스트(또는 다른 픽스처)가 **인자로 그 이름을 적으면**, pytest 가 알아서 값을 만들어 넣어 준다.

```python
@pytest.fixture
def sample_quote() -> dict:
    return {"text": "...", "author": "..."}


async def test_무언가(client, sample_quote):  # ← 이름만 적으면 주입된다
    ...
```

`yield` 를 쓰면 "준비 → (테스트 실행) → 정리" 를 한 함수로 표현할 수 있다.

```python
@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac          # ← 여기서 테스트로 값이 넘어간다
    # 테스트가 끝나면 async with 블록을 빠져나오며 자동 정리
```

### 13.6.2 스코프 — 얼마나 자주 만들고 버릴까

픽스처에는 **스코프**가 있다. "이 자원을 얼마나 오래 살려둘 것인가" 를 정한다.

| 스코프 | 의미 | 언제 쓰나 |
|--------|------|-----------|
| `function`(기본) | 테스트 함수마다 새로 만들고 정리 | 격리가 중요한 대부분의 경우 |
| `class` | 한 테스트 클래스 안에서 공유 | 클래스 단위로 묶인 셋업 |
| `module` | 한 파일 안에서 공유 | 파일 내 모든 테스트가 같은 무거운 자원을 써도 될 때 |
| `session` | 테스트 전체 실행에서 단 한 번 | 아주 무거운 1회성 준비(예: 컨테이너 기동) |

스코프는 데코레이터에 적는다.

```python
@pytest.fixture(scope="session")
def expensive_resource():
    ...
```

> **스코프는 "속도 ↔ 격리" 의 트레이드오프다.** 넓은 스코프(session)는 한 번만 만들어 **빠르지만**, 여러 테스트가 같은 객체를 공유하므로 **상태가 새기 쉽다**. 좁은 스코프(function)는 매번 새로 만들어 **느리지만 격리가 확실하다**. 입문 단계의 안전한 기본값은 **function 스코프**다. 우리 예제의 `client` 도 function 스코프(기본값)다.

> **흔한 함정** : 무거운 자원을 빠르게 하려고 스코프를 `module` 로 넓혔다가, 한 테스트가 만든 데이터가 다음 테스트에 새서 "어떤 건 통과하고 어떤 건 실패" 하는 현상을 만난다. 07장 트러블슈팅에서도 같은 함정을 다뤘다. 넓힐 거면 "상태를 비우는 장치" 를 반드시 함께 둔다.

### 13.6.3 `autouse` — 적지 않아도 켜지는 픽스처

보통 픽스처는 테스트가 **인자로 이름을 적어야** 동작한다. 그런데 "모든 테스트에 무조건 적용하고 싶은" 셋업도 있다. 그럴 때 `autouse=True` 를 쓴다.

```python
@pytest.fixture(autouse=True)
def reset_store():
    reset_state()
```

이렇게 두면 테스트 함수가 `reset_store` 를 인자로 적지 않아도, 매 테스트 전에 자동으로 실행된다. 우리 예제에서는 **인메모리 저장소를 비우는 일** 을 이 방식으로 강제한다.

---

## 13.7 `tests/conftest.py`

공통 픽스처를 한곳에 모은다. **같은 폴더의 모든 테스트 파일이 import 없이** 여기 픽스처를 쓸 수 있다 — 이것이 `conftest.py` 의 핵심이다.

```python
# tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app, reset_state


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """매 테스트 시작 전에 인메모리 저장소를 초기화한다."""
    reset_state()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """ASGI 트랜스포트로 앱에 직접 요청을 보내는 비동기 클라이언트."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_quote() -> dict:
    """기본 명언 생성 페이로드. 테스트마다 살짝 바꿔 쓴다."""
    return {"text": "단순함은 신뢰성의 전제 조건이다.", "author": "Dijkstra"}
```

세 픽스처를 한 줄씩 짚자.

1. **`reset_store`** — `autouse=True`. 매 테스트 전에 `reset_state()` 를 불러 저장소를 비운다. 테스트는 이 픽스처를 인자로 적을 필요가 없다.
2. **`client`** — 07·08장과 같은 패턴. `ASGITransport(app=app)` 로 진짜 네트워크 없이 앱에 직접 요청을 보내는 비동기 클라이언트. DB 가 없으니 07장의 `engine`·`session_factory` 픽스처는 필요 없다 — 훨씬 가볍다.
3. **`sample_quote`** — 여러 테스트가 공유하는 기본 페이로드. 한 군데서 정의해 두면, 페이로드 형식이 바뀌어도 한 곳만 고치면 된다.

> **`@pytest.fixture` vs `@pytest_asyncio.fixture`** : 동기 픽스처(`reset_store`, `sample_quote`)는 일반 `@pytest.fixture` 로 충분하다. `async def` 로 만들고 `yield` 해야 하는 비동기 픽스처(`client`)는 `@pytest_asyncio.fixture` 를 쓴다. `asyncio_mode = "auto"` 가 켜져 있어도 **픽스처 데코레이터는 자동 변환되지 않으니** 비동기 픽스처에는 명시적으로 이 데코레이터를 붙인다.

---

## 13.8 기본 CRUD·에러 케이스 테스트

첫 테스트 파일이다. 픽스처를 쓰고, 정상 케이스와 **에러 케이스**(404 / 422)를 함께 다룬다.

```python
# tests/test_health_and_quotes.py
from httpx import AsyncClient


class TestHealth:
    async def test_헬스_체크는_ok_를_돌려준다(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestCreateQuote:
    async def test_정상_생성은_201_과_본문을_돌려준다(
        self, client: AsyncClient, sample_quote: dict
    ) -> None:
        res = await client.post("/quotes", json=sample_quote)
        assert res.status_code == 201

        body = res.json()
        assert body["id"] == 1
        assert body["text"] == sample_quote["text"]
        assert body["author"] == sample_quote["author"]

    async def test_빈_본문이면_422(self, client: AsyncClient) -> None:
        res = await client.post("/quotes", json={})
        assert res.status_code == 422

    async def test_text_가_280자를_넘으면_422(self, client: AsyncClient) -> None:
        too_long = "가" * 281
        res = await client.post("/quotes", json={"text": too_long, "author": "익명"})
        assert res.status_code == 422


class TestReadQuote:
    async def test_없는_id_조회는_404(self, client: AsyncClient) -> None:
        res = await client.get("/quotes/9999")
        assert res.status_code == 404
        assert "9999" in res.json()["detail"]

    async def test_생성_후_단건_조회가_가능하다(
        self, client: AsyncClient, sample_quote: dict
    ) -> None:
        created = (await client.post("/quotes", json=sample_quote)).json()

        res = await client.get(f"/quotes/{created['id']}")
        assert res.status_code == 200
        assert res.json()["author"] == sample_quote["author"]
```

### 13.8.1 에러 케이스는 "성공만큼" 중요하다

초보 단계에서는 "정상 동작이 되는지" 만 테스트하기 쉽다. 하지만 진짜 버그는 **에러 경로**에서 더 자주 산다.

- 없는 자원을 조회하면 정말 404 가 나는가? (혹시 500 으로 터지진 않나?)
- 잘못된 입력에 정말 422 가 나는가? (혹시 그냥 통과해 저장되진 않나?)
- 에러 메시지에 식별자가 들어 있는가? (`assert "9999" in res.json()["detail"]`)

이런 단언을 함께 두면, 나중에 누군가 코드를 바꾸다 에러 처리를 깨뜨려도 테스트가 즉시 잡아 준다.

### 13.8.2 상태 격리를 테스트로 증명하기

`reset_store` 픽스처가 정말로 동작하는지, 두 테스트로 직접 보여준다.

```python
class TestIsolation:
    """reset_store(autouse) 픽스처가 테스트 사이 상태를 비우는지 확인."""

    async def test_첫_테스트에서_명언을_하나_만든다(
        self, client: AsyncClient, sample_quote: dict
    ) -> None:
        await client.post("/quotes", json=sample_quote)
        res = await client.get("/quotes")
        assert len(res.json()) == 1

    async def test_두번째_테스트는_빈_저장소에서_시작한다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/quotes")
        assert res.json() == []

        created = (
            await client.post("/quotes", json={"text": "처음부터 다시", "author": "익명"})
        ).json()
        assert created["id"] == 1   # ← id 카운터까지 초기화됐다
```

첫 테스트가 명언을 하나 만들지만, 둘째 테스트는 **빈 목록** 에서 시작하고 새 id 가 다시 `1` 이다. `reset_store` 가 매번 저장소와 id 카운터를 모두 비운다는 증거다.

> **테스트는 순서에 의존하면 안 된다.** 위 두 테스트의 실행 순서가 바뀌어도, 파일 하나만 돌리든 전체를 돌리든 항상 통과해야 한다. `autouse` 초기화 픽스처가 그 독립성을 보장한다.

---

## 13.9 파라미터화 — 한 함수로 여러 입력을 덮기

같은 검증을 입력만 바꿔 반복하고 있다면, `@pytest.mark.parametrize` 가 답이다.

### 13.9.1 기본 형태

```python
# tests/test_parametrize.py
import pytest
from httpx import AsyncClient


class TestQuoteValidationParametrized:
    @pytest.mark.parametrize(
        "payload",
        [
            {},                                   # 둘 다 누락
            {"text": "본문만 있음"},               # author 누락
            {"author": "저자만 있음"},             # text 누락
            {"text": "", "author": "익명"},        # text 빈 문자열
            {"text": "정상", "author": ""},        # author 빈 문자열
            {"text": "가" * 281, "author": "익명"},  # text 너무 김
        ],
    )
    async def test_잘못된_본문은_모두_422(
        self, client: AsyncClient, payload: dict
    ) -> None:
        res = await client.post("/quotes", json=payload)
        assert res.status_code == 422
```

이 한 함수가 **6개의 독립된 테스트** 로 펼쳐진다. pytest 출력에서도 6줄로 따로 보인다.

```
test_잘못된_본문은_모두_422[payload0] PASSED
test_잘못된_본문은_모두_422[payload1] PASSED
...
```

각 케이스가 따로 실행되므로, 하나가 실패해도 **어떤 입력에서** 실패했는지 정확히 보인다. 복사-붙여넣기로 만든 6개 함수보다 훨씬 낫다.

### 13.9.2 인자가 여러 개일 때

값 묶음을 튜플로 넘기고, 첫 인자에 이름을 콤마로 나열한다.

```python
@pytest.mark.parametrize(
    ("text", "author"),
    [
        ("짧은 명언", "A"),
        ("가" * 280, "경계값 저자"),     # text 최대 길이 경계(280)
        ("이모지도 된다 🚀", "유니코드"),
    ],
)
async def test_경계값_본문은_201(
    self, client: AsyncClient, text: str, author: str
) -> None:
    res = await client.post("/quotes", json={"text": text, "author": author})
    assert res.status_code == 201
    assert res.json()["text"] == text
```

> **경계값을 꼭 넣자.** `max_length=280` 이라면 "280자(통과)" 와 "281자(실패)" 를 둘 다 테스트한다. 버그는 경계에서 가장 많이 산다. 위에서 280자는 성공 케이스에, 281자는 실패 케이스(13.9.1)에 넣어 양쪽을 덮었다.

> **`parametrize` 와 픽스처는 함께 쓴다.** 위 예에서 `client` 는 픽스처로 주입되고, `text`·`author` 는 파라미터로 주입된다. 둘은 충돌하지 않고 자연스럽게 섞인다.

---

## 13.10 예외 단언 — `pytest.raises`

지금까지는 HTTP 응답의 **상태 코드** 로 에러를 확인했다. 그런데 라우터를 거치지 않고 **함수·클래스를 직접** 테스트할 때는, "예외가 던져지는 것 자체" 를 단언해야 한다. 그게 `pytest.raises` 다.

```python
class TestPydanticRaises:
    def test_정상_입력은_검증을_통과한다(self) -> None:
        model = QuoteCreate(text="유효한 본문", author="작가")
        assert model.author == "작가"

    def test_빈_text_는_ValidationError(self) -> None:
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            QuoteCreate(text="", author="작가")

        assert exc_info.value.error_count() == 1
        assert exc_info.value.errors()[0]["loc"] == ("text",)
```

(`QuoteCreate` 는 `from app.main import QuoteCreate` 로 가져온다.)

핵심은 다음과 같다.

- **`with pytest.raises(ValidationError):`** — 이 블록 안에서 `ValidationError` 가 나면 통과, **안 나면 실패**다. "예외가 나는 게 정상" 인 케이스를 정확히 표현한다.
- **`as exc_info`** — 잡힌 예외 객체를 받아 더 들여다본다. `exc_info.value` 가 실제 예외 인스턴스다. 여기서는 "어느 필드에서(`loc == ("text",)`) 몇 개(`error_count() == 1`) 실패했는지" 까지 확인했다.

> **이 테스트들은 `async` 가 아니다.** Pydantic 모델 생성은 동기 코드라 평범한 `def test_...` 로 쓴다. 같은 파일에 `async def` 테스트(파라미터화)와 `def` 테스트(예외 단언)가 섞여 있어도 `pytest-asyncio` 가 각각 알아서 처리한다.

> **`pytest.raises` 의 `match=` 옵션** : `pytest.raises(ValueError, match="invalid")` 처럼 예외 메시지를 정규식으로 함께 확인할 수도 있다. 메시지가 사양의 일부라면 유용하다.

---

## 13.11 외부 HTTP 호출 모킹 — 이 챕터의 하이라이트

이제 가장 중요한 절이다. `/rate/{code}` 는 외부 환율 API 를 부른다. 테스트에서 진짜 네트워크를 타면 세 가지가 나빠진다.

- **느리다** — 매 테스트가 외부 응답을 기다린다.
- **불안정하다** — 외부가 잠깐 죽으면 우리 테스트가 빨개진다(우리 잘못이 아닌데도).
- **통제 불가** — "외부가 500 을 줄 때 우리가 503 으로 변환하는가" 같은 케이스를 외부에 강요할 수 없다.

그래서 외부 호출을 **가짜로 바꿔치운다(mocking)**. 핵심 도구는 pytest 내장 픽스처 `monkeypatch` 다.

### 13.11.1 `monkeypatch` 가 뭔가요

`monkeypatch` 는 "테스트 동안만 어떤 속성·함수·환경 변수를 임시로 바꿔치우고, 테스트가 끝나면 자동으로 원래대로 되돌려 주는" pytest 내장 픽스처다. 인자로 `monkeypatch` 라고 적기만 하면 쓸 수 있다.

가장 많이 쓰는 메서드는 `setattr` 이다.

```python
monkeypatch.setattr(대상모듈, "속성이름", 새값)
```

"테스트가 끝나면 자동 복원" 이 핵심이다. 직접 `services.fetch_rate = ...` 로 바꾸면 그 변경이 다음 테스트에까지 새지만, `monkeypatch` 로 바꾸면 그 테스트가 끝날 때 깔끔히 원복된다.

### 13.11.2 방법 1 — 외부 함수 자체를 교체

가장 직관적이다. `services.fetch_rate` 를 가짜 코루틴으로 바꾼다.

```python
# tests/test_rate_mock.py
import httpx
import pytest

from app import services
from app.main import app, get_rate_fetcher


class TestRateWithMonkeypatch:
    async def test_가짜_환율을_돌려주도록_교체한다(
        self, client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def fake_fetch_rate(code: str) -> float:
            return 1387.5    # 진짜 네트워크 대신 고정값

        monkeypatch.setattr(services, "fetch_rate", fake_fetch_rate)

        res = await client.get("/rate/usd")
        assert res.status_code == 200
        assert res.json() == {"code": "USD", "rate": 1387.5}
```

라우터의 의존성 `get_rate_fetcher` 가 `services.fetch_rate` 를 돌려주므로, **모듈의 그 속성을 바꾸면** 라우터가 가짜를 부르게 된다. 진짜 네트워크는 한 번도 일어나지 않는다.

> **왜 `app.main.fetch_rate` 가 아니라 `services.fetch_rate` 를 패치하나?** `get_rate_fetcher` 안이 `return services.fetch_rate` 라서, 함수가 **불릴 때** `services` 모듈에서 속성을 조회한다. 그래서 `services` 모듈의 속성을 바꾸면 충분하다. 만약 `main.py` 가 `from app.services import fetch_rate` 로 **이름을 복사해 왔다면**, `app.main.fetch_rate` 를 패치해야 했을 것이다. "어디서 그 이름을 찾는가" 를 따라가는 게 모킹의 핵심 감각이다.

### 13.11.3 실패 경로도 모킹으로 만든다

외부가 실패하는 상황을 **마음대로** 만들 수 있다는 게 모킹의 큰 장점이다.

```python
    async def test_외부가_실패하면_503_으로_변환된다(
        self, client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def failing_fetch_rate(code: str) -> float:
            raise services.RateUnavailableError("upstream 500")

        monkeypatch.setattr(services, "fetch_rate", failing_fetch_rate)

        res = await client.get("/rate/usd")
        assert res.status_code == 503
        assert "환율 정보를 가져올 수 없습니다" in res.json()["detail"]
```

진짜 외부 API 를 죽이지 않고도, "외부가 죽었을 때 우리는 503 을 준다" 는 사양을 검증했다.

### 13.11.4 가짜 함수가 받은 인자를 검증한다

가짜 함수에 기록 장치를 달면, "라우터가 우리 함수를 **올바른 인자로, 올바른 횟수** 불렀는가" 까지 확인할 수 있다.

```python
    async def test_가짜_함수가_받은_인자를_검증한다(
        self, client, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        calls: list[str] = []

        async def recording_fetch_rate(code: str) -> float:
            calls.append(code)
            return 100.0

        monkeypatch.setattr(services, "fetch_rate", recording_fetch_rate)

        await client.get("/rate/eur")
        assert calls == ["eur"]    # 정확히 한 번, "eur" 로 불렸다
```

> **이것이 "스파이(spy)" 패턴이다.** 가짜로 바꾸되, 호출 기록을 남겨 두고 나중에 검증한다. "외부를 부르긴 했나? 몇 번? 어떤 인자로?" 같은 상호작용을 확인할 때 쓴다.

### 13.11.5 외부 호출 전에 막히는 케이스

잘못된 통화 코드는 **외부 호출 전에** 422 로 막혀야 한다. 가짜 함수가 아예 안 불리는지 확인한다.

```python
    @pytest.mark.parametrize("bad_code", ["1", "U", "TOOLONG", "U$D"])
    async def test_잘못된_코드_형식은_외부_호출_전에_422(
        self, client, monkeypatch: pytest.MonkeyPatch, bad_code: str
    ) -> None:
        called = False

        async def should_not_be_called(code: str) -> float:
            nonlocal called
            called = True
            return 0.0

        monkeypatch.setattr(services, "fetch_rate", should_not_be_called)

        res = await client.get(f"/rate/{bad_code}")
        assert res.status_code == 422
        assert called is False    # 형식 검증에서 막혔으니 외부는 안 불린다
```

파라미터화와 모킹을 한 테스트에서 함께 쓴 예다. 네 가지 잘못된 코드 모두 422 이고, 외부 호출은 한 번도 일어나지 않는다.

---

## 13.12 모킹의 다른 두 갈래

`monkeypatch` 만 모킹의 길은 아니다. 상황에 맞는 다른 두 방법을 짧게 본다.

### 13.12.1 방법 2 — `dependency_overrides` 로 의존성 교체

FastAPI 의 의존성 주입을 통째로 갈아끼우는 방법이다(07·08장에서 `get_session` 에 썼던 그 패턴).

```python
class TestRateWithDependencyOverride:
    async def test_의존성_오버라이드로_가짜_fetcher_를_주입한다(
        self, client
    ) -> None:
        async def fake_fetch(code: str) -> float:
            return 9.99

        app.dependency_overrides[get_rate_fetcher] = lambda: fake_fetch
        try:
            res = await client.get("/rate/jpy")
            assert res.status_code == 200
            assert res.json() == {"code": "JPY", "rate": 9.99}
        finally:
            app.dependency_overrides.clear()    # 반드시 정리
```

`get_rate_fetcher` 가 **돌려주는 함수** 자체를 가짜로 바꾼다. `monkeypatch` 와 결과는 같지만, "FastAPI 의 의존성 경계" 에서 갈아끼운다는 점이 다르다.

> **둘 중 무엇을 쓰나?** 외부 호출이 **의존성(`Depends`)으로 주입되어 있으면** `dependency_overrides` 가 가장 깔끔하다. 그게 아니라 코드 어딘가에서 **모듈 함수를 직접 부르고 있으면** `monkeypatch` 가 답이다. 우리 앱은 둘 다 가능하도록 설계해 두어 양쪽을 보여줬다.

> **`finally` 의 `clear()` 를 잊지 말자.** `dependency_overrides` 는 앱 전역 상태다. 정리하지 않으면 그 오버라이드가 다음 테스트에까지 새서, 엉뚱한 테스트가 깨진다. (07장 conftest 의 `client` 픽스처는 이 정리를 픽스처 안에서 자동으로 했다.)

### 13.12.2 방법 3 — `httpx.MockTransport` 로 HTTP 레이어만 가짜로

지금까지는 `fetch_rate` 함수를 통째로 바꿨다. 그러면 함수 **안쪽 로직**(URL 조립, 응답 파싱, 예외 정규화)은 테스트되지 않는다. 그 안쪽까지 검증하려면, `fetch_rate` 는 진짜로 돌리되 **HTTP 레이어만** 가짜로 만든다. `httpx.MockTransport` 가 그 도구다.

```python
class TestFetchRateUnit:
    async def test_정상_응답을_파싱한다(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"rate": 1400.0})

        transport = httpx.MockTransport(handler)

        # AsyncClient 를 만들 때 우리 transport 가 끼워지도록 감싼다.
        real_async_client = httpx.AsyncClient

        def patched_async_client(*args, **kwargs):
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

        rate = await services.fetch_rate("usd")
        assert rate == 1400.0
        assert captured["url"].endswith("/USD")    # 대문자로 조립됐는지
```

여기서 일어나는 일:

- **`handler`** — 들어온 요청을 받아 가짜 `httpx.Response` 를 돌려주는 함수. 진짜 서버 대신 이 함수가 응답한다.
- **`MockTransport(handler)`** — 그 핸들러를 쓰는 가짜 트랜스포트. 07장 conftest 의 `ASGITransport` 와 사촌지간이다(트랜스포트를 바꿔 네트워크를 우회한다).
- **`patched_async_client`** — `fetch_rate` 안의 `httpx.AsyncClient(...)` 가 우리 트랜스포트를 쓰도록, `AsyncClient` 생성을 감싼다.

이 방식이면 `fetch_rate` 의 **실제 로직** 까지 검증된다. URL 이 대문자 코드로 잘 조립되는지(`/USD`), 5xx 응답이 `RateUnavailableError` 로 정규화되는지, 형식이 깨진 응답도 같은 예외가 되는지 모두 확인할 수 있다.

```python
    async def test_5xx_응답은_RateUnavailableError(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="boom")

        transport = httpx.MockTransport(handler)
        real_async_client = httpx.AsyncClient

        def patched_async_client(*args, **kwargs):
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

        with pytest.raises(services.RateUnavailableError):
            await services.fetch_rate("usd")
```

> **세 방법을 어떻게 고르나?**
> - **함수만 바꾸면 충분**하고 라우터를 검증하려면 → `monkeypatch` 로 함수 교체(방법 1).
> - **의존성으로 주입**되어 있으면 → `dependency_overrides`(방법 2).
> - **함수 안쪽 로직(파싱·예외 변환)까지** 검증하려면 → `MockTransport` 로 HTTP 레이어만(방법 3).
>
> 입문 단계에서 가장 자주 쓰는 건 방법 1이다. 방법 3은 "외부 클라이언트 코드 자체" 를 짤 때 진가를 발휘한다.

---

## 13.13 테스트 조직화

테스트가 늘어나면 "어떻게 나눌까" 가 문제가 된다. 우리 예제의 분할 기준은 단순하다.

```
tests/
├── conftest.py                  ← 공통 픽스처(모든 파일이 공유)
├── test_health_and_quotes.py    ← 기본 CRUD·에러 케이스
├── test_parametrize.py          ← 파라미터화·예외 단언
└── test_rate_mock.py            ← 외부 호출 모킹
```

권장 습관 몇 가지.

- **파일은 기능/주제 단위로 나눈다.** 라우터별(`test_quotes.py`, `test_rate.py`)로 나누는 것도 흔하고 좋다. 한 파일이 너무 길어지면(수백 줄) 쪼갠다.
- **클래스로 관련 테스트를 묶는다.** `class TestCreateQuote:` 처럼 묶으면, 출력에서도 그룹으로 보이고 공통 셋업을 클래스 픽스처로 둘 수도 있다. (테스트 클래스에는 `__init__` 을 두지 않는다.)
- **테스트 함수 이름이 곧 사양이 되게 한다.** 이 가이드는 한국어로 적는다. `test_없는_id_조회는_404` 처럼.
- **공통 픽스처는 `conftest.py` 로.** 한 파일에서만 쓰는 픽스처는 그 파일 안에 둬도 된다.

자주 쓰는 실행 명령:

```bash
uv run pytest                      # 전체
uv run pytest -v                   # 테스트 이름까지 자세히
uv run pytest tests/test_rate_mock.py          # 한 파일만
uv run pytest -k "모킹 or 422"     # 이름에 키워드가 든 것만
uv run pytest -x                   # 처음 실패에서 멈춤
uv run pytest --lf                 # 직전에 실패한(last-failed) 것만 다시
```

> **마커로 묶기** : 느린 테스트에 `@pytest.mark.slow` 를 달아 두고 `pytest -m "not slow"` 로 평소엔 건너뛰는 식의 운영도 가능하다. 커스텀 마커를 쓸 땐 `pyproject.toml` 의 `[tool.pytest.ini_options]` 에 `markers = ["slow: 느린 테스트"]` 로 등록해 경고를 없앤다. 우리 예제는 마커 없이도 충분히 빨라서 쓰지 않았다.

---

## 13.14 커버리지 측정 (`pytest-cov`)

"테스트가 코드의 어느 부분을 **실제로 실행했는지**" 를 숫자로 보여주는 게 커버리지다. 빠뜨린 분기를 찾는 데 좋다.

> **우리 예제 테스트는 순수 pytest 로만 돈다.** 커버리지는 **선택 도구**다. 보고 싶을 때만 `pytest-cov` 를 추가로 깔면 된다. 테스트 자체는 `pytest-cov` 없이도 그대로 통과한다.

설치와 실행:

```bash
uv add --dev pytest-cov
uv run pytest --cov=app --cov-report=term-missing
```

`--cov=app` 은 "`app` 패키지의 커버리지를 재라", `--cov-report=term-missing` 은 "터미널에 **실행 안 된 줄 번호까지** 보여줘" 라는 뜻이다. 출력은 대략 이렇게 생겼다.

```
Name                 Stmts   Miss  Cover   Missing
--------------------------------------------------
app/__init__.py          0      0   100%
app/main.py             48      0   100%
app/services.py         16      0   100%
--------------------------------------------------
TOTAL                   64      0   100%
```

> **커버리지 100%가 목표는 아니다.** 커버리지는 "실행된 줄" 만 본다. "그 줄이 **올바르게** 동작하는지" 는 못 본다. 즉 100% 라도 단언이 허술하면 버그를 놓친다. 커버리지는 **빠뜨린 곳을 찾는 지도**로 쓰되, 숫자 자체를 신앙하지는 말자. 의미 있는 단언이 먼저다.

> **HTML 리포트** : `--cov-report=html` 을 주면 `htmlcov/` 폴더에 색칠된 리포트가 생긴다(빨간 줄 = 실행 안 됨). 브라우저로 열어 보면 어디가 비었는지 한눈에 보인다. `.gitignore` 에 `htmlcov/`, `.coverage` 를 넣어 두자.

---

## 13.15 실행 — 전부 통과시키기

```bash
uv run pytest -v
```

성공하면 다음과 비슷한 출력이 나온다(총 30개).

```
tests/test_health_and_quotes.py::TestHealth::test_헬스_체크는_ok_를_돌려준다 PASSED
tests/test_health_and_quotes.py::TestCreateQuote::test_정상_생성은_201_과_본문을_돌려준다 PASSED
...
tests/test_parametrize.py::TestQuoteValidationParametrized::test_잘못된_본문은_모두_422[payload0] PASSED
...
tests/test_rate_mock.py::TestRateWithMonkeypatch::test_가짜_환율을_돌려주도록_교체한다 PASSED
tests/test_rate_mock.py::TestFetchRateUnit::test_정상_응답을_파싱한다 PASSED
...
============================== 30 passed in 0.04s ==============================
```

매 테스트가 `reset_store` 로 깨끗한 상태에서 시작하고, 외부 호출은 모두 모킹되므로 **순서에 의존하지 않고** **네트워크 없이** 0.1초 안에 끝난다.

> **서버를 직접 띄워 `/rate/usd` 를 누르면?** 503 이 난다. 실제 외부 주소(`https://api.example.com/rates`)는 우리 데모용 가짜라 닿지 못하기 때문이다. **이 엔드포인트의 정상 동작은 테스트의 모킹으로 확인하는 것** 이 이 예제의 핵심이다 — 바로 그래서 모킹을 배우는 것이다.

---

## 13.16 흔한 실수 / 트러블슈팅

### 13.16.1 비동기 픽스처에 `@pytest.fixture` 를 썼다

`async def` 픽스처에 일반 `@pytest.fixture` 를 붙이면, 테스트에 코루틴 객체가 그대로 주입되어 이상하게 깨진다. 비동기 픽스처는 `@pytest_asyncio.fixture` 를 써야 한다. (`asyncio_mode = "auto"` 는 **테스트 함수**만 자동 처리하지, 픽스처 데코레이터까지 바꾸진 않는다.)

### 13.16.2 모킹했는데 진짜 함수가 불린다

`monkeypatch.setattr` 의 **대상**이 틀렸을 때다. "그 이름을 실제로 어디서 찾는가" 를 따라가야 한다. `get_rate_fetcher` 가 `return services.fetch_rate` 라면 `services` 모듈을 패치한다. 만약 `main.py` 가 `from app.services import fetch_rate` 로 이름을 복사해 왔다면 `app.main.fetch_rate` 를 패치해야 한다.

### 13.16.3 한 테스트는 통과, 전체로 돌리면 깨진다

테스트 사이에 상태가 새고 있다. 우리 예제에서는 `reset_store` (autouse) 가 인메모리 저장소를 비워 막는다. `dependency_overrides` 를 쓴 테스트가 `clear()` 를 빠뜨렸을 때도 같은 증상이 난다 — `finally` 에서 반드시 정리하자.

### 13.16.4 `parametrize` 케이스가 하나도 안 보인다

데코레이터 인자 이름과 테스트 함수 인자 이름이 어긋났을 때다. `@pytest.mark.parametrize("payload", [...])` 라면 테스트 함수도 `..., payload)` 로 같은 이름을 받아야 한다.

### 13.16.5 `pytest.raises` 블록이 통과하지 않는다

블록 안에서 예외가 **안 났을 때** `pytest.raises` 는 실패한다("DID NOT RAISE"). 기대한 예외 타입이 맞는지, 정말 그 코드가 예외를 던지는지 확인한다. 너무 넓은 타입(`Exception`)보다 구체적인 타입(`ValidationError`)으로 좁히는 게 좋다.

### 13.16.6 외부 호출이 테스트에서 느리거나 빨갛다

진짜 네트워크를 타고 있다는 신호다. 모킹이 적용되지 않았을 가능성이 높다(13.16.2 참고). 테스트는 외부 세계에 닿으면 안 된다 — 그게 모킹의 존재 이유다.

### 13.16.7 `pytest-cov` 가 없다고 에러

커버리지는 선택 도구다. `--cov` 옵션은 `pytest-cov` 가 깔려 있을 때만 동작한다. `uv add --dev pytest-cov` 로 설치하거나, 옵션 없이 `uv run pytest` 로 돌리면 된다.

---

## 13.17 이 챕터 요약

- **픽스처는 스코프로 "속도 ↔ 격리" 를 조절한다.** 입문의 안전한 기본값은 function 스코프. 넓힐 거면 상태를 비우는 장치를 함께 둔다. 모두에 적용할 셋업은 `autouse=True`.
- **`conftest.py`** 에 공통 픽스처를 모으면 같은 폴더의 모든 테스트가 import 없이 공유한다. 비동기 픽스처에는 `@pytest_asyncio.fixture`.
- **`@pytest.mark.parametrize`** 로 한 함수가 여러 입력으로 펼쳐진다. 경계값(280/281)을 꼭 함께 넣는다. 실패 시 어떤 입력에서 깨졌는지 정확히 보인다.
- **에러 케이스는 성공만큼 테스트한다.** HTTP 는 상태 코드(404/422/503)로, 함수·스키마는 `pytest.raises` 로 "예외가 나는 게 정상" 임을 단언한다.
- **외부 호출은 모킹한다.** 외부 통신을 얇은 함수(`fetch_rate`)로 격리해 두는 **설계** 가 먼저다. 그 위에서 `monkeypatch`(함수 교체)·`dependency_overrides`(의존성 교체)·`httpx.MockTransport`(HTTP 레이어 교체) 셋 중 상황에 맞는 걸 고른다. 입문에서 가장 잦은 건 `monkeypatch`.
- **조직화** 는 기능/주제 단위로 파일을 나누고, 클래스로 묶고, 이름을 사양처럼 짓는 것.
- **커버리지(`pytest-cov`)** 는 빠뜨린 줄을 찾는 지도다. 선택 도구이며, 숫자 자체보다 의미 있는 단언이 먼저다.

다음 챕터에서는 **파일 업로드**를 다룬다. 멀티파트 폼, 이미지 저장, 크기·확장자 검증 같은 실무 패턴을 배우고, 업로드 엔드포인트도 이 장에서 익힌 방식으로 테스트한다.

---

← [12. 유틸리티 및 라이브러리](12-utilities.md) | [README로 돌아가기](../README.md) | 다음 문서로 이동: **[14. 파일 업로드 →](14-file-upload.md)**
