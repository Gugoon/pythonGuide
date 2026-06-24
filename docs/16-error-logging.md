# 16. 에러 핸들링·로깅 심화

> **이 챕터의 목표**
> - 05장에서 한 줄로 만났던 `HTTPException` 과 `@app.exception_handler` 를 한 단계 끌어올려, **커스텀 예외 클래스**와 **전역 예외 핸들러**로 에러 처리를 한 곳에 모은다.
> - 모든 에러가 같은 모양으로 나가도록 **일관된 에러 응답 스키마**(`code` / `message` / `detail`) 를 설계한다.
> - `RequestValidationError`(422) 핸들러를 커스터마이징해 검증 실패도 같은 스키마로 통일한다.
> - **요청 ID 미들웨어**(`X-Request-ID`) 로 요청 하나하나에 고유 ID 를 붙이고, 그 ID 를 응답 헤더와 로그에 함께 실어 **로그 상관관계(log correlation)** 를 만든다.
> - 표준 라이브러리 `logging` 을 포매터·레벨·핸들러·필터로 제대로 설정하고, 예외를 트레이스백과 함께 로그에 남긴다.

> **소요 시간**: 2~4시간

> **전제**: 05·08장(HTTPException, 의존성, 미들웨어)

> **모르는 단어가 나오면** 먼저 [용어 사전(glossary.md)](glossary.md) 을 펼쳐 한두 줄만 읽고 돌아오면 된다.

---

## 16.1 왜 에러 처리와 로깅을 따로 한 장으로 다루나

지금까지 우리는 에러가 나면 그때그때 `HTTPException` 을 던졌다(05·07·08장). 작은 앱에서는 그걸로 충분하다. 그런데 코드가 자라면 같은 질문이 반복된다.

- 404 를 던지는 코드가 라우터마다 흩어져 있다. **에러 메시지 형식이 제각각**이다.
- 어떤 라우트는 `{"detail": "..."}`, 어떤 라우트는 `{"message": "..."}` 를 돌려준다. **클라이언트가 에러를 일관되게 처리할 수 없다**.
- 검증 실패(422)는 또 다른 모양(`{"detail": [...]}`) 이라 형식이 셋으로 갈린다.
- 운영에서 "그 사용자의 그 요청이 왜 실패했는지" 를 로그에서 **찾을 수가 없다**. 어떤 로그가 어떤 요청에 속하는지 표시가 없기 때문이다.
- 예상 못 한 예외가 나면 **트레이스백이 클라이언트에게 그대로 노출**되거나(보안 문제), 반대로 아무 데도 안 남아 디버깅이 불가능하다.

이 장은 이 다섯 가지를 한 번에 정리한다. 핵심 도구는 네 가지다.

1. **커스텀 예외 클래스** — 도메인 상황(자원 없음, 규칙 위반)을 예외 타입으로 표현한다.
2. **전역 예외 핸들러** — 그 예외들을 한 곳에서 일관된 JSON 으로 변환한다.
3. **요청 ID 미들웨어** — 요청마다 ID 를 붙여 로그와 응답을 잇는다.
4. **표준 logging 설정** — 포매터·레벨·핸들러·필터를 제대로 구성한다.

> **이 장은 DB 가 없다.** 주제(에러·로깅)에 집중하기 위해 데이터는 인메모리 `dict` 로 둔다. 실제 앱이라면 06~07장처럼 SQLAlchemy 가 들어오지만, 에러·로깅 패턴은 DB 유무와 무관하게 똑같이 적용된다.

---

## 16.2 큰 그림 — 무엇을 만들 것인가

만들 것은 작은 시연용 API 다. **기능보다 "에러가 났을 때 무슨 일이 일어나는가"** 를 보여주는 데 집중한다.

| 메서드 | 경로 | 설명 | 결과 |
|--------|------|------|------|
| `GET` | `/health` | 헬스 체크 | 200 |
| `GET` | `/items/{item_id}` | 단건 조회 | 200 / 404(커스텀 예외) |
| `POST` | `/orders` | 주문 | 200 / 404 / 409 / 422 |
| `GET` | `/boom` | 예상 못 한 예외 시연 | 500 |

이 네 엔드포인트로 다음 다섯 가지 에러 경로를 전부 시연한다.

1. **정상 응답**(200) — 핸들러가 정상 흐름을 망가뜨리지 않는다.
2. **커스텀 예외 → 404** — `ResourceNotFound("item", 9999)`.
3. **비즈니스 규칙 위반 → 409** — `BusinessRuleError("재고가 부족합니다")`.
4. **검증 실패 → 422** — Pydantic 검증을 커스텀 핸들러로 다듬는다.
5. **예상 못 한 예외 → 500** — 트레이스백은 로그에만, 클라이언트에는 일반 메시지만.

그리고 이 모든 응답에 **`X-Request-ID` 헤더**가 붙고, 서버 로그의 모든 줄에 같은 ID 가 찍힌다.

### 16.2.1 패키지 구조 한 그림

```
16-ErrorLogging/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
└── app/
    ├── __init__.py
    ├── main.py                ← 앱 조립 + 시연 엔드포인트
    ├── errors.py              ← 커스텀 예외 + 에러 스키마 + 전역 핸들러
    ├── middleware.py          ← 요청 ID(X-Request-ID) 미들웨어
    ├── request_context.py     ← 요청 ID 를 담는 ContextVar
    └── logging_config.py      ← 표준 logging 설정(포매터·핸들러·필터)
```

각 파일의 한 줄 정의:

| 파일 | 책임 한 줄 |
|------|------------|
| `app/main.py` | 로깅·미들웨어·핸들러를 조립하고, 시연 엔드포인트를 둔다 |
| `app/errors.py` | 커스텀 예외, 에러 응답 스키마, 전역 예외 핸들러를 모두 모은다 |
| `app/middleware.py` | 요청마다 `X-Request-ID` 를 부여·전파하는 미들웨어 |
| `app/request_context.py` | 요청 ID 를 어디서나 읽을 수 있게 `ContextVar` 로 보관한다 |
| `app/logging_config.py` | 표준 `logging` 의 포매터·핸들러·필터를 한 함수로 설정한다 |

이 표가 곧 우리의 작업 순서다. 다만 "왜" 부터 차근히 보기 위해 `HTTPException` 복습부터 시작한다.

---

## 16.3 출발점 — `HTTPException` 복습

05장에서 배운 표준은 이랬다. 에러가 필요하면 `HTTPException` 을 `raise` 한다.

```python
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


@router.get("/items/{item_id}")
async def get_item(item_id: int):
    item = ITEMS.get(item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {item_id} 를 찾을 수 없습니다",
        )
    return item
```

`HTTPException(status_code=404, detail="...")` 는 자동으로 다음 JSON 으로 직렬화된다.

```json
{ "detail": "Item 9999 를 찾을 수 없습니다" }
```

이 방식의 장점은 분명하다. 짧고, `/docs` 에도 잘 표시된다. **작은 앱에서는 이게 정답이다.** 그런데 두 가지 한계가 있다.

1. **응답 모양이 `{"detail": ...}` 로 고정**이라, 기계가 분기할 에러 코드(`resource_not_found` 같은)를 같이 싣기 어렵다. `detail` 에 dict 를 넣을 수는 있지만, 그러면 라우트마다 모양이 또 제각각이 된다.
2. **같은 404 를 던지는 코드가 여기저기 흩어진다.** "Todo 404", "User 404", "Item 404" 가 각자 다른 메시지 형식으로 자란다.

해법은 05장 5.8.4 에서 살짝 맛본 **커스텀 예외 + 핸들러** 다. 거기서는 "코드가 커졌을 때 진가를 발휘한다" 고만 했는데, 이 장이 바로 그 "커졌을 때" 다.

> **`HTTPException` 을 버리는 게 아니다.** 뒤에서 보겠지만, `HTTPException` 도 우리의 일관된 에러 스키마로 흡수한다. 직접 `raise HTTPException(...)` 한 곳, 그리고 프레임워크가 자동으로 내는 404·405 까지 전부 같은 모양으로 통일하는 게 목표다.

---

## 16.4 일관된 에러 응답 스키마 설계

코드를 짜기 전에 **"에러는 어떤 모양으로 나갈 것인가"** 를 먼저 정한다. 이게 이 장의 뼈대다.

우리가 쓸 모양은 다음과 같다.

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "item 9999 를 찾을 수 없습니다",
    "detail": { "resource": "item", "id": 9999 },
    "request_id": "ae510f2727354c37a1bdecbca61e2033"
  }
}
```

네 필드의 역할:

| 필드 | 타입 | 역할 |
|------|------|------|
| `code` | `str` | **기계**가 분기할 짧은 식별자. 프런트엔드가 `if code == "resource_not_found"` 처럼 쓴다. |
| `message` | `str` | **사람**이 읽는 한 줄 설명. 화면에 그대로 띄울 수 있다. |
| `detail` | `any \| null` | 부가 정보. 검증 에러 목록, 어떤 자원이 없었는지 등. 없으면 `null`. |
| `request_id` | `str` | 이 에러가 난 요청의 ID. 사용자가 이 값을 알려주면 운영자가 로그에서 정확히 찾는다. |

> **왜 `code` 와 `message` 를 나누나?** `message` 는 사람이 읽으라고 있는 거라 언제든 바뀔 수 있다("Item 없음" → "상품을 찾을 수 없습니다"). 그런데 프런트엔드 코드가 메시지 **문자열**로 분기하면, 메시지를 다듬는 순간 클라이언트가 깨진다. 그래서 **변하지 않는 기계용 식별자(`code`)** 와 **언제든 바뀌어도 되는 사람용 문장(`message`)** 을 분리한다. 이건 거의 모든 잘 설계된 API(Stripe, GitHub 등)가 쓰는 패턴이다.

이 모양을 Pydantic 스키마로 못 박는다. `app/errors.py` 의 맨 위에 둔다.

```python
# app/errors.py (윗부분)
from pydantic import BaseModel


class ErrorBody(BaseModel):
    """에러 응답의 `error` 안쪽 본문."""

    code: str  # 기계가 분기할 수 있는 짧은 식별자 (예: "resource_not_found")
    message: str  # 사람이 읽는 한 줄 설명
    detail: object | None = None  # 부가 정보(검증 에러 목록 등). 없으면 null.
    request_id: str  # 이 에러가 발생한 요청의 ID. 로그와 대조할 수 있다.


class ErrorResponse(BaseModel):
    """최상위 에러 응답. 모든 에러가 이 모양으로 나간다."""

    error: ErrorBody
```

> **왜 `error` 로 한 겹 감싸나?** 최상위에 `error` 키를 두면, 정상 응답과 에러 응답을 클라이언트가 한눈에 구분할 수 있다. `"error" in body` 한 줄이면 끝이다. (취향에 따라 감싸지 않기도 한다. 중요한 건 "**프로젝트 안에서 하나로 통일**" 이다.)

---

## 16.5 요청 ID 를 어디서나 읽기 — `ContextVar`

에러 응답에 `request_id` 를 넣으려면, 핸들러가 "지금 처리 중인 요청의 ID" 를 알아야 한다. 그런데 예외 핸들러 함수는 `request_id` 를 인자로 받지 않는다. 또 로그를 찍는 `crud` 함수도, 서비스 함수도 ID 를 알아야 하는데 매번 인자로 넘기는 건 번거롭다.

해법은 표준 라이브러리 `contextvars.ContextVar` 다.

```python
# app/request_context.py
from contextvars import ContextVar

# 기본값 "-" : 아직 미들웨어를 거치지 않은(요청 밖) 로그에도 안전하게 찍힌다.
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


def set_request_id(request_id: str) -> None:
    """현재 요청의 ID 를 컨텍스트에 저장한다(미들웨어가 호출)."""
    _request_id_ctx.set(request_id)


def get_request_id() -> str:
    """현재 요청의 ID 를 읽는다. 요청 밖이면 '-' 를 돌려준다."""
    return _request_id_ctx.get()
```

미들웨어가 요청 시작 시점에 `set_request_id(...)` 로 ID 를 심으면, 같은 요청을 처리하는 **모든 코드**가 `get_request_id()` 한 줄로 같은 값을 읽는다. 인자로 들고 다닐 필요가 없다.

> **그냥 전역 변수(`REQUEST_ID = "..."`) 면 안 되나?** 안 된다. 비동기 서버는 여러 요청을 **동시에(번갈아)** 처리한다. 평범한 전역 변수는 요청 A 가 심은 값을 요청 B 가 덮어써서, 로그가 뒤섞인다. `ContextVar` 는 각 실행 흐름(async task)마다 **독립된 값**을 보관하므로 안전하다. 이게 `ContextVar` 가 존재하는 이유다.

> **`default="-"` 의 의미** : 미들웨어를 아직 안 거친 상황(앱 시작 로그, 백그라운드 작업 등)에서 `get_request_id()` 를 불러도 에러 없이 `"-"` 가 나온다. 로그 포맷이 깨지지 않는다.

---

## 16.6 표준 `logging` 설정 — 포매터·핸들러·필터

`print` 는 운영에 부적합하다(12장 12.35 절). 레벨·형식·출력 대상을 분리해 관리하려면 `logging` 을 제대로 설정해야 한다. 우리가 쓸 최소 구성을 한 함수에 모은다.

```python
# app/logging_config.py
import logging
import sys

from app.request_context import get_request_id

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [req=%(request_id)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    """모든 로그 레코드에 현재 요청 ID 를 붙여주는 필터.

    포매터가 `%(request_id)s` 를 쓰려면 모든 레코드에 `request_id` 속성이 있어야 한다.
    이 필터가 레코드마다 그 속성을 채워 넣는다. (요청 밖에서 찍힌 로그는 '-' 가 된다.)
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True  # True 를 돌려줘야 레코드가 통과한다(필터링 탈락이 아님).


def setup_logging(level: int = logging.INFO) -> None:
    """애플리케이션 로깅을 한 번 설정한다.

    앱이 뜰 때 한 번만 부르면 된다. 여러 번 불려도 기존 핸들러를 정리하고
    다시 붙이므로 핸들러가 중복되지 않는다(중복되면 로그가 두 번씩 찍힌다).
    """
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(level)

    # 핸들러 중복 방지: 이미 붙어 있던 것을 떼고 우리 핸들러 하나만 둔다.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
```

`logging` 의 네 부품을 정확히 짚자.

### 16.6.1 로거 / 핸들러 / 포매터 / 필터

`logging` 은 네 종류의 부품으로 이루어진다. 처음엔 헷갈리지만 역할이 또렷하다.

| 부품 | 한 줄 역할 | 우리 코드에서 |
|------|-----------|---------------|
| **Logger** | 로그를 "발생" 시키는 입구. `logging.getLogger("app.errors")` | 각 모듈이 자기 이름의 로거를 쓴다 |
| **Handler** | 로그를 **어디로** 보낼지. 파일·표준출력·외부 시스템 | `StreamHandler(sys.stdout)` 하나 |
| **Formatter** | 로그 한 줄의 **모양**(시각·레벨·메시지) | `LOG_FORMAT` 문자열 |
| **Filter** | 레코드를 거르거나 **속성을 추가** | `RequestIdFilter` 가 `request_id` 주입 |

> **로거는 이름으로 계층을 이룬다.** `logging.getLogger("app.errors")` 와 `logging.getLogger("app.request")` 는 모두 루트 로거(`logging.getLogger()`)의 자식이다. 루트에 핸들러 하나만 붙이면, 자식 로거들이 발생시킨 로그가 자동으로 그 핸들러로 흘러 올라간다(propagation). 그래서 우리는 **루트에 핸들러 하나, 포매터 하나, 필터 하나** 만 둔다.

### 16.6.2 포매터 문자열 뜯어보기

```
%(asctime)s [%(levelname)s] %(name)s [req=%(request_id)s] %(message)s
```

| 토큰 | 뜻 | 예시 |
|------|-----|------|
| `%(asctime)s` | 시각 | `2026-06-24 11:55:57` |
| `%(levelname)s` | 레벨 | `INFO`, `WARNING`, `ERROR` |
| `%(name)s` | 로거 이름 | `app.errors` |
| `%(request_id)s` | **우리가 추가한** 요청 ID | `ae510f...` |
| `%(message)s` | 실제 메시지 | `요청 시작 GET /items/1` |

실제 출력은 이렇게 나온다.

```
2026-06-24 11:55:57 [WARNING] app.errors [req=ae510f27...] 도메인 예외: item 9999 를 찾을 수 없습니다 (code=resource_not_found)
```

`[req=...]` 한 토막이 이 장의 핵심이다. **로그 한 줄만 봐도 어느 요청에서 났는지** 알 수 있다.

### 16.6.3 `Filter` 로 모든 레코드에 요청 ID 주입

포매터에 `%(request_id)s` 를 쓰면, `logging` 은 모든 로그 레코드에 `request_id` 라는 속성이 있다고 가정한다. 그런데 기본 레코드에는 그런 속성이 없다 → `KeyError` 로 로그가 깨진다.

`RequestIdFilter` 가 이 구멍을 메운다. 필터의 `filter()` 메서드는 레코드가 통과할 때마다 불리는데, 우리는 거기서 거르는 대신 **속성을 추가**한다.

```python
def filter(self, record: logging.LogRecord) -> bool:
    record.request_id = get_request_id()
    return True
```

- `record.request_id = get_request_id()` — 현재 요청 ID(없으면 `"-"`)를 레코드에 단다.
- `return True` — "이 레코드를 버리지 말고 통과시켜라". 필터는 원래 "거르는" 용도지만, 이렇게 **속성 주입 훅**으로도 쓰는 게 표준 관용구다.

> **왜 `LoggerAdapter` 나 `extra=` 가 아니라 필터인가?** `logger.info("...", extra={"request_id": ...})` 처럼 매번 `extra` 를 넘기는 방법도 있다. 하지만 그러면 **모든 로그 호출**에 `extra` 를 붙여야 하고, 한 군데라도 빠뜨리면 `KeyError` 다. 게다가 우리가 직접 부르지 않는 라이브러리(`uvicorn`, `httpx`)의 로그에는 `extra` 를 넣을 수조차 없다. 필터를 핸들러에 붙이면 **그 핸들러를 거치는 모든 로그**(우리 것 + 라이브러리 것)에 자동으로 ID 가 붙는다. 훨씬 견고하다.

### 16.6.4 핸들러 중복 방지

`setup_logging` 끝부분을 보자.

```python
for existing in list(root.handlers):
    root.removeHandler(existing)
root.addHandler(handler)
```

`--reload` 로 개발하거나 테스트에서 앱을 여러 번 import 하면 `setup_logging` 이 두 번 불릴 수 있다. 그때마다 핸들러를 그냥 `addHandler` 하면 핸들러가 쌓여서 **같은 로그가 2번, 3번씩 찍힌다.** 기존 핸들러를 먼저 떼고 하나만 붙이면 이 함정을 피한다.

> **`logging.basicConfig()` 면 충분하지 않나?** `basicConfig` 는 "이미 핸들러가 있으면 아무 것도 안 함" 이라 두 번째 호출이 무시된다. 편하지만 **필터를 핸들러에 붙이기**가 번거롭고, 재설정도 까다롭다. 명시적으로 핸들러를 만들어 두면 필터 부착·중복 제거를 우리가 통제할 수 있다.

---

## 16.7 커스텀 예외 클래스

이제 도메인 상황을 **예외 타입**으로 표현한다. `app/errors.py` 에 이어서 적는다.

```python
# app/errors.py (이어서)
from fastapi import status


class AppError(Exception):
    """이 앱의 모든 도메인 예외의 부모.

    공통 속성을 정의해 두면, 핸들러 하나로 자식 예외 전부를 처리할 수 있다.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "internal_error"

    def __init__(self, message: str, *, detail: object | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class ResourceNotFound(AppError):
    """요청한 자원이 없을 때. 404 로 매핑된다."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "resource_not_found"

    def __init__(self, resource: str, resource_id: object) -> None:
        super().__init__(
            message=f"{resource} {resource_id!r} 를 찾을 수 없습니다",
            detail={"resource": resource, "id": resource_id},
        )


class BusinessRuleError(AppError):
    """비즈니스 규칙 위반(예: 잔액 부족, 중복 신청). 409 로 매핑된다."""

    status_code = status.HTTP_409_CONFLICT
    code = "business_rule_violation"
```

설계의 핵심은 **부모 클래스 `AppError`** 다.

- `status_code` 와 `code` 를 **클래스 속성**으로 둔다. 자식이 이 둘만 바꾸면 새 예외 타입이 완성된다.
- `ResourceNotFound` 는 `status_code = 404`, `code = "resource_not_found"`.
- `BusinessRuleError` 는 `status_code = 409`, `code = "business_rule_violation"`.

이렇게 부모를 두면, 핸들러를 **`AppError` 하나에만** 등록해도 모든 자식 예외가 잡힌다(파이썬의 `except AppError` 가 자식까지 잡는 것과 같은 원리). 새 예외 타입을 추가해도 핸들러는 그대로다.

> **`raise HTTPException(404, ...)` 와 뭐가 다른가?** 두 가지가 다르다. ① **의미가 코드에 드러난다.** `raise ResourceNotFound("item", id)` 는 "자원이 없다" 는 도메인 사실을 말한다. HTTP 상태 코드(404)는 그 사실의 _번역_ 일 뿐이고, 번역은 핸들러가 한 곳에서 맡는다. ② **재사용·일관성.** "item 없음" 메시지 형식이 `ResourceNotFound` 안에 한 번만 정의된다. 모든 라우터가 같은 형식을 공유한다.

> **`resource_id!r` 의 `!r`** 은 f-string 에서 `repr()` 을 쓰라는 표시다. 문자열이면 따옴표가 붙어(`'abc'`) 숫자(`9999`)와 구분이 또렷해진다. 디버깅 메시지에서 유용하다.

---

## 16.8 전역 예외 핸들러

예외를 정의했으니, 이제 그것을 **일관된 JSON 으로 변환**하는 핸들러를 만든다. `app/errors.py` 에 이어서 적는다. 먼저 모든 핸들러가 공유할 **렌더 함수** 부터.

```python
# app/errors.py (이어서)
import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.request_context import get_request_id

logger = logging.getLogger("app.errors")


def _render(
    *,
    status_code: int,
    code: str,
    message: str,
    detail: object | None = None,
) -> JSONResponse:
    """일관된 에러 JSON 응답을 만든다. 모든 핸들러가 이 함수를 거친다."""
    body = ErrorResponse(
        error=ErrorBody(
            code=code,
            message=message,
            detail=detail,
            request_id=get_request_id(),
        )
    )
    return JSONResponse(
        status_code=status_code,
        # model_dump() 만으로는 datetime 등 일부 타입이 JSON 으로 안 바뀔 수 있어
        # jsonable_encoder 로 한 번 더 감싸 안전하게 직렬화한다.
        content=jsonable_encoder(body.model_dump()),
    )
```

`_render` 한 함수가 **모든 에러의 단일 출구**다. `request_id` 를 여기서 한 번만 채우므로, 각 핸들러는 `code`/`message`/`detail` 만 신경 쓰면 된다.

> **`jsonable_encoder` 는 왜 쓰나?** `JSONResponse` 에 dict 를 넘기면 표준 `json` 모듈로 직렬화하는데, `datetime`·`UUID`·`Decimal` 같은 타입은 그대로는 직렬화가 안 돼 에러가 난다. `jsonable_encoder` 는 FastAPI 가 평소 응답에 쓰는 변환기로, 이런 타입들을 JSON 이 이해하는 형태(문자열 등)로 미리 바꿔준다. 에러 응답에도 같은 변환기를 쓰면 안전하다.

### 16.8.1 커스텀 예외 핸들러

```python
# app/errors.py (이어서)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """우리가 정의한 도메인 예외를 일관된 JSON 으로 변환한다."""
    # 4xx(클라이언트 잘못)는 WARNING, 5xx(서버 잘못)는 ERROR 로 레벨을 나눈다.
    if exc.status_code >= 500:
        logger.error("도메인 예외(5xx): %s", exc.message, exc_info=exc)
    else:
        logger.warning("도메인 예외: %s (code=%s)", exc.message, exc.code)
    return _render(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        detail=exc.detail,
    )
```

핸들러 함수의 시그니처는 `(request: Request, exc: <예외타입>)` 으로 고정이다. FastAPI 가 매칭되는 예외를 잡아 이 함수에 넘긴다.

- **`AppError` 에 등록** → 자식인 `ResourceNotFound`·`BusinessRuleError` 도 모두 이 핸들러가 처리한다.
- `exc.status_code`, `exc.code`, `exc.message`, `exc.detail` 을 그대로 `_render` 에 넘긴다.
- **로그 레벨을 상태 코드로 나눈다.** 4xx 는 "클라이언트가 잘못 보낸 것" 이라 `WARNING`, 5xx 는 "서버가 잘못한 것" 이라 `ERROR`. 운영에서 알림(alert)을 거는 기준이 보통 `ERROR` 이상이라, 이 구분이 중요하다.

### 16.8.2 `HTTPException` 도 같은 모양으로 흡수

직접 `raise HTTPException(...)` 한 곳, 그리고 존재하지 않는 경로(404)·잘못된 메서드(405)처럼 **프레임워크가 자동으로 내는 에러**도 같은 스키마로 통일한다.

```python
# app/errors.py (이어서)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """`HTTPException`(과 Starlette 의 404 등)도 같은 에러 모양으로 통일한다.

    이렇게 해두면 직접 `raise HTTPException(...)` 한 곳, 존재하지 않는 경로(404),
    405 등 프레임워크가 자동으로 내는 에러까지 모두 같은 JSON 스키마로 나간다.
    """
    logger.warning("HTTP 예외: %s (status=%s)", exc.detail, exc.status_code)
    return _render(
        status_code=exc.status_code,
        code=f"http_{exc.status_code}",
        message=str(exc.detail),
    )
```

> **왜 `starlette.exceptions.HTTPException` 을 import 하나?** FastAPI 의 `HTTPException` 은 Starlette 의 것을 상속한 것이고, **존재하지 않는 경로(404) 같은 자동 에러는 Starlette 쪽 `HTTPException` 으로 발생**한다. Starlette 의 것에 핸들러를 등록하면 FastAPI 의 것(자식)까지 함께 잡힌다. 그래서 더 넓게 잡는 부모 쪽에 등록한다.

- `code` 는 `http_404`, `http_405` 처럼 상태 코드에서 자동 생성한다.
- 이제 우리 앱은 **없는 경로로 요청해도** `{"detail": "Not Found"}` 가 아니라 우리의 `{"error": {...}}` 모양으로 응답한다.

### 16.8.3 `RequestValidationError`(422) 커스터마이징

Pydantic 검증이 실패하면 FastAPI 는 기본적으로 `{"detail": [...]}` 모양의 422 를 돌려준다(07장 7.14.4 에서 봤다). 이 모양만 다른 에러와 형태가 다르다. 같은 스키마로 흡수한다.

```python
# app/errors.py (이어서)
from fastapi import status


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """요청 검증 실패(422)를 우리 스키마에 맞게 다듬는다.

    FastAPI 기본 422 응답은 `{"detail": [...]}` 모양이라 다른 에러와 형태가 다르다.
    여기서 같은 `{"error": {...}}` 스키마로 감싸고, Pydantic 이 준 상세 목록을
    `detail` 에 그대로 담아 클라이언트가 어느 필드가 틀렸는지 알 수 있게 한다.
    """
    logger.warning("검증 실패: %d 건", len(exc.errors()))
    return _render(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="validation_error",
        message="요청 본문 검증에 실패했습니다",
        # errors() 안에는 예외 객체 등 JSON 으로 못 바꾸는 값이 섞일 수 있어
        # jsonable_encoder 로 안전하게 변환한다.
        detail=jsonable_encoder(exc.errors()),
    )
```

- `exc.errors()` 는 Pydantic 이 만든 상세 목록이다. 각 항목에 `loc`(어느 필드), `type`(어떤 검증), `msg`(메시지)가 들어 있다.
- 그걸 통째로 `detail` 에 담는다. 클라이언트는 `detail[0]["loc"]` 로 어느 필드가 틀렸는지 안다.
- 바깥 모양(`code`/`message`/`request_id`)은 다른 에러와 똑같다.

이제 422 응답은 이렇게 나간다.

```json
{
  "error": {
    "code": "validation_error",
    "message": "요청 본문 검증에 실패했습니다",
    "detail": [
      {
        "type": "less_than_equal",
        "loc": ["body", "quantity"],
        "msg": "Input should be less than or equal to 100",
        "input": 999,
        "ctx": { "le": 100 }
      }
    ],
    "request_id": "e00e8bedf8c64804ac40c5c4c917cb59"
  }
}
```

### 16.8.4 예상 못 한 예외 → 500 (안전하게)

마지막은 우리가 미처 다루지 못한 모든 예외다. `ValueError`, `KeyError`, DB 끊김 등 무엇이든.

```python
# app/errors.py (이어서)
async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """그 외 예상 못 한 모든 예외 → 500.

    트레이스백은 서버 로그에만 남기고, 클라이언트에게는 내부 구현을 노출하지
    않는 일반 메시지만 돌려준다(보안). 대신 `request_id` 를 함께 주므로,
    사용자가 그 ID 를 알려주면 운영자가 로그에서 정확한 트레이스백을 찾을 수 있다.
    """
    logger.error("처리되지 않은 예외", exc_info=exc)
    return _render(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_error",
        message="서버 내부 오류가 발생했습니다",
    )
```

이 핸들러가 **보안의 핵심**이다.

- **`logger.error(..., exc_info=exc)`** — 트레이스백 전체를 **서버 로그에만** 남긴다. `exc_info=exc` 가 트레이스백을 함께 찍는 마법이다(`logger.exception(...)` 과 같은 효과).
- **클라이언트에게는 일반 메시지만.** `"서버 내부 오류가 발생했습니다"` 만 돌려주고, `ValueError("의도적으로...")` 같은 원문이나 트레이스백은 **절대 노출하지 않는다.** 내부 구현·파일 경로·변수명이 새면 공격자에게 힌트가 된다.
- **대신 `request_id` 를 준다.** 사용자가 "request_id `1ca4ae...` 에서 에러가 났어요" 라고 알려주면, 운영자는 로그에서 그 ID 로 정확한 트레이스백을 찾는다. 보안과 디버깅 가능성을 동시에 잡는다.

### 16.8.5 핸들러 등록

핸들러들을 앱에 다는 함수다.

```python
# app/errors.py (맨 끝)
def register_exception_handlers(app: FastAPI) -> None:
    """위 핸들러들을 앱에 한꺼번에 등록한다(main.py 에서 한 줄 호출)."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
```

> **등록 순서가 중요한가?** FastAPI 는 예외 타입의 **구체성** 으로 매칭한다(가장 잘 맞는 타입). `ResourceNotFound` 가 나면 `AppError` 핸들러가, `RequestValidationError` 가 나면 그 전용 핸들러가, 그 외 전부는 `Exception` 핸들러가 잡는다. `Exception` 은 모든 예외의 부모라 "최후의 그물" 역할을 한다. 등록 순서 자체보다 **타입 계층**이 매칭을 결정한다.

---

## 16.9 요청 ID 미들웨어

이제 요청마다 ID 를 부여하는 미들웨어를 만든다. 이게 로그 상관관계의 출발점이다.

```python
# app/middleware.py
import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.request_context import set_request_id

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1) 클라이언트가 보낸 ID 를 쓰거나, 없으면 새로 만든다.
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming or uuid.uuid4().hex

        # 2) 컨텍스트에 심는다. 이제 이 요청을 처리하는 모든 로그가 이 ID 를 단다.
        set_request_id(request_id)
        # 라우터 등에서 request.state.request_id 로도 꺼내 쓸 수 있게 둔다.
        request.state.request_id = request_id

        logger.info("요청 시작 %s %s", request.method, request.url.path)

        # 3) 다음 단계(다른 미들웨어 → 라우터)를 호출한다.
        #    예외가 나도 응답 헤더에 ID 를 넣어주기 위해 try/finally 로 감쌀 수도 있지만,
        #    예외는 예외 핸들러가 만든 JSONResponse 로 변환되어 이 자리로 돌아오므로
        #    아래 한 줄로 충분하다.
        response = await call_next(request)

        # 4) 응답 헤더에 같은 ID 를 실어 돌려준다.
        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info("요청 종료 -> %s", response.status_code)
        return response
```

### 16.9.1 미들웨어가 하는 네 가지

번호 주석 그대로다.

1. **ID 결정** — 클라이언트가 `X-Request-ID` 를 보냈으면 그걸 쓰고, 없으면 `uuid.uuid4().hex` 로 새로 만든다.
2. **컨텍스트에 심기** — `set_request_id(request_id)`. 이 순간부터 이 요청을 처리하는 모든 로그가 이 ID 를 단다(16.5·16.6 의 `ContextVar` + `Filter` 조합 덕분).
3. **다음 단계 호출** — `await call_next(request)`. 이게 라우터까지 내려갔다 응답을 들고 돌아온다.
4. **응답 헤더에 ID 반영** — `response.headers[REQUEST_ID_HEADER] = request_id`. 클라이언트도 자기 요청의 ID 를 받는다.

> **왜 클라이언트가 보낸 ID 를 존중하나?** 마이크로서비스 환경에서는 한 사용자 요청이 여러 서비스를 거친다(게이트웨이 → 주문 서비스 → 결제 서비스). 첫 서비스가 만든 ID 를 뒤 서비스들이 **그대로 이어받으면**, 서비스 경계를 넘어도 같은 ID 로 로그를 추적할 수 있다. 이걸 분산 추적(distributed tracing)의 기초라고 한다. 단일 서비스라면 그냥 새로 만들어도 된다.

### 16.9.2 미들웨어와 예외 핸들러의 협력

여기서 한 가지 의문이 든다. **라우터에서 예외가 나면 `call_next` 가 던져서, 4번(헤더 반영)이 실행 안 되는 것 아닌가?**

답은 "아니다". FastAPI/Starlette 에서 **예외 핸들러는 미들웨어보다 안쪽에서 동작**한다. 즉 라우터에서 예외가 나면:

```
라우터 예외 발생
  → 예외 핸들러가 잡아 JSONResponse(500/404/...) 로 변환
  → 그 JSONResponse 가 call_next 의 반환값으로 미들웨어에 올라옴
  → 미들웨어 4번이 그 응답 헤더에 X-Request-ID 를 붙임
```

그래서 **에러 응답에도 `X-Request-ID` 가 정상적으로 붙는다.** 본문의 `request_id` 와 헤더의 `X-Request-ID` 가 항상 일치한다. (이건 뒤 16.11 테스트에서 직접 검증한다.)

> **`@app.middleware("http")` 데코레이터 방식과 다른가?** 12장 12.35 에서 본 `@app.middleware("http")` 는 `BaseHTTPMiddleware` 를 더 짧게 쓰는 문법 설탕이다. 동작은 같다. 우리는 클래스로 분리해 `main.py` 를 깔끔하게 두는 쪽을 택했다. 둘 중 편한 것을 쓰면 된다.

---

## 16.10 `app/main.py` — 조립과 시연 엔드포인트

부품을 다 만들었으니 조립한다.

```python
# app/main.py
import logging

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.errors import BusinessRuleError, ResourceNotFound, register_exception_handlers
from app.logging_config import setup_logging
from app.middleware import RequestIdMiddleware

# 앱이 import 되는 시점에 로깅을 한 번 설정한다.
setup_logging(level=logging.INFO)
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Error Logging Example",
    version="0.1.0",
    description="16장 — 커스텀 예외, 일관된 에러 응답, 요청 ID 미들웨어, 표준 logging.",
)

# 미들웨어 등록. add_middleware 로 붙인 것은 "가장 나중에 추가한 것이 가장 바깥"이다.
# 요청 ID 는 모든 처리의 가장 바깥에서 부여돼야 하므로 여기 한 줄이면 충분하다.
app.add_middleware(RequestIdMiddleware)

# 전역 예외 핸들러 등록(errors.py 의 핸들러 묶음).
register_exception_handlers(app)


# 학습용 인메모리 "DB". 실제 앱이라면 06~07장처럼 SQLAlchemy 가 들어온다.
ITEMS: dict[int, dict] = {
    1: {"id": 1, "name": "노트북", "stock": 3},
    2: {"id": 2, "name": "키보드", "stock": 0},
}


class OrderRequest(BaseModel):
    """주문 요청 본문. 검증 에러를 시연하기 위해 제약을 건다."""

    item_id: int = Field(ge=1, description="주문할 상품 ID (1 이상)")
    quantity: int = Field(ge=1, le=100, description="수량 (1~100)")


@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    """살아 있는지 확인하는 정상 응답 엔드포인트."""
    return {"status": "ok"}


@app.get("/items/{item_id}", tags=["items"], summary="단건 조회(정상/404 시연)")
async def get_item(item_id: int) -> dict:
    """있으면 정상 200, 없으면 커스텀 예외 `ResourceNotFound` → 일관된 404 JSON."""
    item = ITEMS.get(item_id)
    if item is None:
        # HTTPException 대신 도메인 예외를 던진다. 변환은 전역 핸들러가 맡는다.
        raise ResourceNotFound("item", item_id)
    return item


@app.post("/orders", tags=["orders"], summary="주문(검증/비즈니스 규칙 시연)")
async def create_order(payload: OrderRequest) -> dict:
    """주문을 시도한다.

    - 본문 검증 실패(item_id<1, quantity 범위 밖 등) → 422 (검증 핸들러가 처리).
    - 없는 상품 → 404 (`ResourceNotFound`).
    - 재고 부족 → 409 (`BusinessRuleError`).
    - 정상 → 201 처럼 동작(여기서는 200 으로 단순화).
    """
    item = ITEMS.get(payload.item_id)
    if item is None:
        raise ResourceNotFound("item", payload.item_id)

    if payload.quantity > item["stock"]:
        # 비즈니스 규칙 위반. detail 에 부가 정보를 실어 보낸다.
        raise BusinessRuleError(
            "재고가 부족합니다",
            detail={"requested": payload.quantity, "in_stock": item["stock"]},
        )

    logger.info("주문 성공 item_id=%s quantity=%s", payload.item_id, payload.quantity)
    return {
        "ordered": True,
        "item_id": payload.item_id,
        "quantity": payload.quantity,
    }


@app.get("/boom", tags=["demo"], summary="예상 못 한 예외 시연(500)")
async def boom() -> dict:
    """일부러 평범한 예외를 던져 500 핸들러를 시연한다.

    클라이언트에게는 일반 메시지 + request_id 만, 서버 로그에는 트레이스백이 남는다.
    """
    raise ValueError("의도적으로 발생시킨 내부 오류")
```

조립 순서를 한 번 더 짚자.

1. **`setup_logging(...)` 을 맨 먼저** — 앱·미들웨어가 첫 로그를 찍기 전에 로깅이 준비돼야 한다.
2. **`app.add_middleware(RequestIdMiddleware)`** — 요청 ID 미들웨어 한 줄. `add_middleware` 는 "나중에 추가한 것이 가장 바깥" 이라, 미들웨어가 여럿이면 요청 ID 를 **가장 마지막에** 추가해 가장 바깥에 둔다(가장 먼저 ID 를 부여하도록).
3. **`register_exception_handlers(app)`** — 핸들러 묶음 등록 한 줄.

> **시연 엔드포인트의 의도** : `/items/{id}` 는 정상/404 를, `/orders` 는 검증(422)/없음(404)/규칙위반(409)/정상을, `/boom` 은 500 을 각각 보여준다. 한 엔드포인트가 한 가지 에러 경로를 또렷하게 시연하도록 일부러 단순하게 짰다.

---

## 16.11 통합 테스트

라우터가 정말 일관된 에러를 내는지, 요청 ID 가 제대로 붙는지 자동으로 검증한다. 07·13장과 같은 `pytest` + `httpx.AsyncClient` 패턴이다.

### 16.11.1 `tests/conftest.py`

```python
# tests/conftest.py
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

DB 가 없으니 픽스처는 클라이언트 하나뿐이다. 한 가지만 07장과 다르다.

> **`raise_app_exceptions=False` 가 왜 필요한가?** `ASGITransport` 의 기본값(`True`)이면, 앱에서 처리되지 못한 예외를 **테스트 클라이언트가 그대로 다시 던진다.** 우리는 500 핸들러가 만든 **JSON 응답 자체**(실제 서버가 클라이언트에게 보내는 것과 같은 응답)를 검증하고 싶다. 그래서 이 옵션을 꺼서 예외 대신 500 응답을 받는다. `/boom` 테스트가 이 옵션 없이는 실패한다.

### 16.11.2 `tests/test_errors.py`

테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다. 먼저 **에러 스키마를 검증하는 헬퍼** 를 둔다(모든 에러가 같은 모양인지 한 곳에서 확인).

```python
# tests/test_errors.py (일부)
from httpx import AsyncClient

from app.middleware import REQUEST_ID_HEADER


def assert_error_shape(body: dict) -> dict:
    """에러 응답이 일관된 스키마를 따르는지 확인하고, error 본문을 돌려준다.

    모양: {"error": {"code": str, "message": str, "detail": ..., "request_id": str}}
    """
    assert set(body.keys()) == {"error"}
    err = body["error"]
    assert set(err.keys()) == {"code", "message", "detail", "request_id"}
    assert isinstance(err["code"], str) and err["code"]
    assert isinstance(err["message"], str) and err["message"]
    assert isinstance(err["request_id"], str) and err["request_id"]
    return err
```

이제 케이스들이다. 정상·커스텀 예외·검증·500·요청 ID 를 묶음별로 나눈다.

```python
class TestHealthyResponses:
    async def test_헬스_체크는_정상_200(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

    async def test_존재하는_상품_조회는_200(self, client: AsyncClient) -> None:
        res = await client.get("/items/1")
        assert res.status_code == 200
        assert res.json()["name"] == "노트북"

    async def test_정상_주문은_성공_본문을_돌려준다(self, client: AsyncClient) -> None:
        res = await client.post("/orders", json={"item_id": 1, "quantity": 2})
        assert res.status_code == 200
        assert res.json()["ordered"] is True


class TestCustomException:
    async def test_없는_상품_조회는_커스텀_404와_일관된_스키마(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/items/9999")
        assert res.status_code == 404
        err = assert_error_shape(res.json())
        assert err["code"] == "resource_not_found"
        assert err["detail"]["resource"] == "item"

    async def test_재고_부족_주문은_비즈니스_규칙_409(
        self, client: AsyncClient
    ) -> None:
        # 2번 상품은 재고 0. 1개라도 주문하면 규칙 위반.
        res = await client.post("/orders", json={"item_id": 2, "quantity": 1})
        assert res.status_code == 409
        err = assert_error_shape(res.json())
        assert err["code"] == "business_rule_violation"
        assert err["detail"]["in_stock"] == 0


class TestValidationError:
    async def test_수량이_범위를_벗어나면_422_일관된_스키마(
        self, client: AsyncClient
    ) -> None:
        res = await client.post("/orders", json={"item_id": 1, "quantity": 999})
        assert res.status_code == 422
        err = assert_error_shape(res.json())
        assert err["code"] == "validation_error"
        # detail 에는 Pydantic 이 준 상세 목록이 그대로 들어 있다.
        locs = [tuple(item["loc"]) for item in err["detail"]]
        assert ("body", "quantity") in locs

    async def test_없는_경로는_404도_같은_에러_스키마(
        self, client: AsyncClient
    ) -> None:
        # 라우트가 없는 경로 → Starlette 의 404. HTTPException 핸들러가 통일한다.
        res = await client.get("/no-such-path")
        assert res.status_code == 404
        assert assert_error_shape(res.json())["code"] == "http_404"


class TestUnhandledException:
    async def test_예상_못_한_예외는_500이지만_내부를_노출하지_않는다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/boom")
        assert res.status_code == 500
        err = assert_error_shape(res.json())
        assert err["code"] == "internal_error"
        # 트레이스백·예외 메시지 원문이 그대로 새지 않아야 한다(보안).
        assert "ValueError" not in err["message"]
        assert err["request_id"] != "-"


class TestRequestId:
    async def test_에러_응답에도_X_Request_ID_헤더가_있다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/items/9999")
        assert REQUEST_ID_HEADER in res.headers
        # 헤더의 ID 와 본문의 request_id 가 같아야 한다(상관관계).
        assert res.headers[REQUEST_ID_HEADER] == res.json()["error"]["request_id"]

    async def test_클라이언트가_보낸_요청_ID가_그대로_전파된다(
        self, client: AsyncClient
    ) -> None:
        my_id = "test-correlation-id-123"
        res = await client.get("/health", headers={REQUEST_ID_HEADER: my_id})
        assert res.headers[REQUEST_ID_HEADER] == my_id

    async def test_보내지_않으면_매_요청마다_다른_ID가_생성된다(
        self, client: AsyncClient
    ) -> None:
        r1 = await client.get("/health")
        r2 = await client.get("/health")
        assert r1.headers[REQUEST_ID_HEADER] != r2.headers[REQUEST_ID_HEADER]
```

전체 파일은 예제 폴더의 `tests/test_errors.py` 에 있고, 총 14개 케이스를 포함한다(정상 3 + 커스텀 예외 3 + 검증 3 + 500 1 + 요청 ID 4).

### 16.11.3 실행

```bash
uv run pytest -q
```

성공하면 다음과 비슷한 출력이 나온다.

```
..............                                                           [100%]
14 passed in 0.03s
```

> **`X-Request-ID` 검증이 핵심** : `test_에러_응답에도_X_Request_ID_헤더가_있다` 는 16.9.2 에서 설명한 "에러가 나도 미들웨어가 헤더를 붙인다" 를 실제로 증명한다. 헤더의 ID 와 본문의 `request_id` 가 일치하는지까지 확인한다.

---

## 16.12 서버 띄우고 직접 호출해 보기

테스트를 통과했다면 실제 서버도 띄워서 눌러 보자.

```bash
uv run uvicorn app.main:app --reload
```

### 16.12.1 정상 응답

```bash
curl -i http://127.0.0.1:8000/items/1
```

응답 헤더에 `X-Request-ID` 가 보이고, 본문은 200 이다.

```
HTTP/1.1 200 OK
x-request-id: c9a52aac80324bac951b134d8c26e11e
content-type: application/json

{"id":1,"name":"노트북","stock":3}
```

### 16.12.2 커스텀 404

```bash
curl http://127.0.0.1:8000/items/9999
```

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "item 9999 를 찾을 수 없습니다",
    "detail": { "resource": "item", "id": 9999 },
    "request_id": "ae510f2727354c37a1bdecbca61e2033"
  }
}
```

### 16.12.3 검증 실패 (422)

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 999}'
```

`detail` 에 Pydantic 상세 목록이 담긴 422 가 나온다(16.8.3 의 JSON 과 동일).

### 16.12.4 비즈니스 규칙 위반 (409)

```bash
# 2번 상품은 재고 0
curl -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item_id": 2, "quantity": 1}'
```

```json
{
  "error": {
    "code": "business_rule_violation",
    "message": "재고가 부족합니다",
    "detail": { "requested": 1, "in_stock": 0 },
    "request_id": "004468d77d4b43659a16bacb17193b3c"
  }
}
```

### 16.12.5 내부 오류 (500)

```bash
curl http://127.0.0.1:8000/boom
```

클라이언트가 받는 응답에는 **내부 구현이 없다**.

```json
{
  "error": {
    "code": "internal_error",
    "message": "서버 내부 오류가 발생했습니다",
    "detail": null,
    "request_id": "1ca4ae9a08a647f4aa3dd63ebe1adade"
  }
}
```

반면 **서버 콘솔** 에는 같은 `request_id` 로 트레이스백이 통째로 남는다.

```
2026-06-24 11:55:57 [ERROR] app.errors [req=1ca4ae9a...] 처리되지 않은 예외
Traceback (most recent call last):
  ...
  File ".../app/main.py", line 112, in boom
    raise ValueError("의도적으로 발생시킨 내부 오류")
ValueError: 의도적으로 발생시킨 내부 오류
```

사용자가 `request_id` 만 알려주면 운영자가 로그에서 정확히 이 트레이스백을 찾는다. **보안(노출 안 함)과 디버깅(추적 가능)을 동시에** 잡았다.

### 16.12.6 요청 ID 전파

```bash
curl -i http://127.0.0.1:8000/health -H "X-Request-ID: my-trace-1"
```

응답 헤더의 `x-request-id` 가 보낸 값 그대로 `my-trace-1` 이다.

### 16.12.7 로그 상관관계 확인

서버 콘솔을 보면 한 요청의 모든 로그가 같은 `[req=...]` 로 묶여 있다.

```
2026-06-24 11:55:57 [INFO] app.request [req=ae510f27...] 요청 시작 GET /items/9999
2026-06-24 11:55:57 [WARNING] app.errors [req=ae510f27...] 도메인 예외: item 9999 를 찾을 수 없습니다 (code=resource_not_found)
2026-06-24 11:55:57 [INFO] app.request [req=ae510f27...] 요청 종료 -> 404
```

`app.request`(미들웨어)와 `app.errors`(핸들러)가 **서로 다른 모듈**인데도 같은 ID 로 묶인다. 16.5·16.6 의 `ContextVar` + `Filter` 조합이 만든 결과다. 운영에서 로그가 수만 줄이 쌓여도, 이 ID 하나로 한 요청의 흐름만 뽑아낼 수 있다.

---

## 16.13 구조적 로깅 개념 — structlog 는 언제

지금 우리 로그는 **한 줄짜리 자유 형식 문자열** 이다.

```
2026-06-24 11:55:57 [WARNING] app.errors [req=ae510f27...] 도메인 예외: item 9999 를 찾을 수 없습니다 (code=resource_not_found)
```

사람이 읽기엔 좋다. 그런데 운영에서 로그를 **검색·집계** 하기 시작하면 한계가 온다. "code 가 resource_not_found 인 로그만", "req=ae510f27 인 로그만" 을 뽑으려면 문자열 파싱을 해야 한다.

**구조적 로깅(structured logging)** 은 로그를 문장이 아니라 **키-값 쌍(보통 JSON)** 으로 남기는 방식이다.

```json
{"timestamp": "2026-06-24T11:55:57", "level": "warning", "logger": "app.errors", "request_id": "ae510f27...", "event": "도메인 예외", "code": "resource_not_found"}
```

이러면 로그 수집 시스템(Elasticsearch, Loki, CloudWatch 등)이 `code` 필드로 바로 검색·집계·알림을 건다. 컨테이너(Docker·쿠버네티스) 환경에서 거의 필수에 가깝다.

이걸 가장 쉽게 해주는 라이브러리가 **structlog** 다. 설치·설정은 **12장 12.36 절**에 정리돼 있다. 핵심만 옮기면:

```python
import structlog

structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)
log = structlog.get_logger()
log.warning("도메인 예외", code="resource_not_found", request_id="...")
```

> **그럼 이 장의 표준 `logging` 은 버려야 하나?** 아니다. ① 표준 `logging` 만으로도 이 장에서 본 것처럼 **충분히 깔끔하게** 갈 수 있다. 입문·소규모에서는 이게 정답이다. ② structlog 도 결국 표준 `logging` 위에서 동작하도록 결합하는 게 일반적이라, **이 장에서 배운 핸들러·필터·포매터 개념이 그대로 쓰인다.** 표준 `logging` 을 먼저 손에 익히는 게 순서다. ③ 요청 ID 를 `ContextVar` 로 다루는 패턴은 structlog 의 `contextvars` 연동(`structlog.contextvars.bind_contextvars`)과도 거의 같은 발상이다.

요약하면, **개념은 같고 출력 형식만 다르다.** 한 줄 텍스트로 시작하고, 로그를 기계로 분석할 필요가 생기면 structlog(또는 표준 `logging` 의 JSON 포매터)로 옮기면 된다.

---

## 16.14 흔한 실수 / 트러블슈팅

### 16.14.1 로그가 두 번씩 찍힌다

`setup_logging` 이 여러 번 불려 핸들러가 쌓였다. 16.6.4 처럼 기존 핸들러를 떼고 붙이거나, `basicConfig` 를 쓴다면 한 번만 호출되도록 한다. `--reload` 개발 중에 특히 잘 생긴다.

### 16.14.2 `KeyError: 'request_id'` 로 로그가 깨진다

포매터에 `%(request_id)s` 를 썼는데 `RequestIdFilter` 를 핸들러에 안 붙였다. 필터가 모든 레코드에 `request_id` 속성을 채워줘야 포맷이 성립한다. 필터를 **핸들러** 에 붙였는지 확인(`handler.addFilter(...)`).

### 16.14.3 에러 응답이 여전히 `{"detail": ...}` 모양이다

핸들러를 등록 안 했거나, 잘못된 예외 타입에 등록했다.

- `RequestValidationError` 핸들러는 `fastapi.exceptions.RequestValidationError` 에 등록해야 한다.
- 404·405 자동 에러까지 잡으려면 `starlette.exceptions.HTTPException`(FastAPI 의 것이 아니라 **Starlette** 의 것)에 등록해야 한다.

### 16.14.4 `/boom` 테스트만 예외를 다시 던지며 실패한다

`ASGITransport(app=app)` 의 기본값이 `raise_app_exceptions=True` 라, 처리 안 된 예외를 테스트가 다시 던진다. 16.11.1 처럼 `raise_app_exceptions=False` 를 준다.

### 16.14.5 500 응답에 트레이스백/내부 메시지가 노출된다

`unhandled_exception_handler` 가 `str(exc)` 를 응답 `message` 에 넣고 있지 않은지 확인. **클라이언트 응답에는 일반 문구만**, 트레이스백은 `logger.error(..., exc_info=exc)` 로 **로그에만** 남긴다(16.8.4).

### 16.14.6 비동기에서 요청 ID 가 가끔 뒤섞인다

평범한 모듈 전역 변수에 요청 ID 를 저장하면 동시 요청끼리 덮어쓴다. 반드시 `contextvars.ContextVar` 를 쓴다(16.5). 그리고 미들웨어의 `dispatch` 안에서 `set_request_id` 를 호출해야 같은 비동기 컨텍스트에 심긴다.

### 16.14.7 `DEBUG` 레벨을 운영에서 켜둬 로그가 폭주한다

`setup_logging(level=...)` 의 레벨을 환경 변수로 제어하자(예: 개발 `DEBUG`, 운영 `INFO`). 12장 12.35 의 함정과 같은 맥락이다.

---

## 16.15 이 챕터 요약

- **커스텀 예외 + 전역 핸들러** : 도메인 상황을 예외 타입(`ResourceNotFound`, `BusinessRuleError`)으로 표현하고, 부모 `AppError` 에 핸들러 하나만 등록해 자식 전부를 일관 처리한다. "라우터는 `raise` 만, 변환은 핸들러가 한 곳에서."
- **일관된 에러 스키마** : 모든 에러가 `{"error": {code, message, detail, request_id}}` 한 모양으로 나간다. `HTTPException`·검증 에러(422)·예상 못 한 500 까지 전부 같은 스키마로 흡수한다. 기계용 `code` 와 사람용 `message` 를 분리한다.
- **`RequestValidationError` 커스터마이징** : 기본 `{"detail": [...]}` 를 우리 스키마로 감싸되, Pydantic 의 상세 목록은 `detail` 에 그대로 담아 어느 필드가 틀렸는지 알 수 있게 한다.
- **요청 ID 미들웨어** : `uuid` 로(또는 클라이언트가 보낸 값으로) `X-Request-ID` 를 부여하고, `ContextVar` 에 심어 로그에 싣고, 응답 헤더로 돌려준다. 에러 응답에도 헤더가 붙는다.
- **로그 상관관계** : `ContextVar`(요청 ID 보관) + `logging.Filter`(모든 레코드에 ID 주입) + 포매터의 `%(request_id)s` 조합으로, 서로 다른 모듈의 로그가 한 요청 ID 로 묶인다.
- **표준 logging** : 포매터·핸들러·필터·레벨을 한 함수로 설정한다. 500 의 트레이스백은 `exc_info=exc` 로 **로그에만** 남기고 클라이언트에는 노출하지 않는다(보안 + 디버깅 가능성).
- **구조적 로깅** 은 같은 개념의 다음 단계다. 로그를 기계로 검색·집계할 필요가 생기면 structlog(12장 12.36) 또는 JSON 포매터로 옮긴다. 이 장에서 배운 핸들러·필터 개념이 그대로 재사용된다.

---

← [15. 백그라운드 작업](15-background-tasks.md) | [README로 돌아가기](../README.md) | 다음 문서로 이동: **[용어 사전 →](glossary.md)**
