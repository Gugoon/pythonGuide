# 05. 라우팅과 Pydantic (JSON 요청/응답)

> **이 챕터의 목표**
> - FastAPI에서 라우트(URL → 함수 매핑)를 만드는 모든 기본 방법을 익힌다.
> - 경로 매개변수·쿼리 매개변수·요청 본문을 Python의 타입 힌트로 자동 검증한다.
> - **Pydantic** 모델로 JSON 요청과 응답의 모양을 선언하고, FastAPI가 알아서 검증·문서화하게 한다.
> - `response_model`, `status_code`, `responses=`로 응답 명세를 또렷하게 적는다.
> - `HTTPException`으로 에러를 적절한 상태 코드로 내보낸다.
> - `APIRouter`로 라우트를 도메인 단위 모듈로 쪼갠다.
> - `Header`, `Cookie`, 폼·파일 등 자주 만나는 입력을 받는다.
> - `Depends`(의존성 주입)의 맛을 살짝 본다(본격은 08장).
> - `/docs`(Swagger UI)에서 직접 호출하고, `TestClient`로 통합 테스트를 쓴다.
> - 챕터 마무리에 **메모리 기반 명언(Quote) API** 한 개를 처음부터 끝까지 만든다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 3~4시간 (실습 포함)

---

## 5.1 시작하기 전에 — 이 챕터의 큰 그림

이 챕터에서 우리가 답하는 질문은 다음과 같습니다.

1. URL과 HTTP 메서드를 함수에 어떻게 묶나? → **라우팅**
2. URL 안의 `{id}`나 `?limit=10` 같은 값은 어떻게 받나? → **경로 매개변수 / 쿼리 매개변수**
3. JSON 본문은 어떤 모양으로 받고 어떻게 검증하나? → **Pydantic 모델**
4. 응답의 모양과 상태 코드는 어떻게 명시하나? → **`response_model`, `status_code`**
5. 에러는 어떻게 내려보내나? → **`HTTPException`**
6. 라우트가 많아지면 어떻게 나누나? → **`APIRouter`**
7. 만든 API를 어떻게 테스트하나? → **`TestClient` + pytest**

이 챕터의 코드 조각들은 머릿속에서 한 번씩 따라 쳐 보시면 가장 좋습니다. 마지막 절(5.18)에서 **명언(Quote) API**라는 작은 프로젝트로 모든 조각을 하나로 묶어 보겠습니다.

> **이번 챕터의 약속**: 데이터베이스는 아직 등장하지 않습니다. 모든 자료는 메모리(파이썬 `dict`) 위에 잠깐 올려두고 끝납니다. DB는 06장에서 처음부터 다룹니다. 메모리에 둔 자료는 서버를 끄면 사라집니다 — 학습 단계에서는 그게 오히려 편합니다.

---

## 5.2 라우팅 기본

### 5.2.1 가장 단순한 라우트

`app.py` 한 파일을 만들고 다음 코드를 붙여 봅니다.

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
def hello():
    return {"message": "Hello, world!"}
```

- `app = FastAPI()` — 애플리케이션 인스턴스를 하나 만든다.
- `@app.get("/hello")` — "GET /hello 요청이 오면 바로 아래 함수가 처리한다"는 등록.
- 함수 반환 `dict` — FastAPI가 자동으로 JSON으로 직렬화하고, `Content-Type: application/json` 헤더를 붙여 200 OK로 응답.

> **데코레이터(decorator)란?** 함수 위에 `@`로 붙는 표시입니다. "이 바로 아래 함수에 추가 동작을 입혀라"는 뜻입니다. `@app.get(...)`은 "이 함수를 GET 요청 처리기로 등록해라"는 명령입니다. 자세한 내용은 [용어 사전 — 데코레이터](glossary.md#데코레이터-decorator)를 참고하세요.

띄우기:

```bash
uv run uvicorn app:app --reload
```

`http://127.0.0.1:8000/hello`를 열어 JSON이 보이면 끝입니다.

### 5.2.2 HTTP 메서드별 데코레이터

| 메서드 | FastAPI 데코레이터 | 보통 쓰는 용도 |
|--------|--------------------|----------------|
| GET | `@app.get(...)` | 자료 가져오기 (조회) |
| POST | `@app.post(...)` | 자료 새로 만들기 (생성) |
| PUT | `@app.put(...)` | 자료를 통째로 덮어쓰기 (전체 수정) |
| PATCH | `@app.patch(...)` | 자료의 일부만 바꾸기 (부분 수정) |
| DELETE | `@app.delete(...)` | 자료 지우기 (삭제) |
| HEAD | `@app.head(...)` | 본문 없이 헤더만 받기 (드물게) |
| OPTIONS | `@app.options(...)` | CORS 사전 요청 등 (드물게) |
| 임의 메서드 | `@app.api_route("/", methods=[...])` | 특수한 경우 |

> **HTTP 메서드란?** 이 요청이 무엇을 하려는지를 표현하는 동사입니다. **GET**(가져오기), **POST**(만들기), **PUT/PATCH**(수정하기), **DELETE**(지우기). 자세한 내용은 02장과 [용어 사전 — HTTP 메서드](glossary.md#http-메서드-http-method)에 있습니다.

다음과 같이 같은 경로에 메서드만 다르게 등록할 수 있습니다.

```python
@app.get("/users")
def list_users():
    return [{"id": 1, "name": "Alice"}]


@app.post("/users")
def create_user():
    return {"id": 2, "name": "Bob"}
```

`GET /users`와 `POST /users`는 서로 **다른 라우트**입니다. URL은 같지만 메서드가 다르므로 FastAPI는 두 함수를 따로 등록합니다.

### 5.2.3 함수 이름은 자유, 경로 문자열만이 진실

라우트 함수의 이름(`list_users`, `create_user`)은 자유롭게 지어도 됩니다. **요청을 어디로 보낼지 결정하는 건 데코레이터에 적힌 경로 문자열**입니다. 함수 이름은 자동 문서의 `operationId` 같은 보조 정보로 쓰입니다.

### 5.2.4 `def` vs `async def`

```python
@app.get("/sync")
def sync_handler():
    return {"kind": "sync"}


@app.get("/async")
async def async_handler():
    return {"kind": "async"}
```

FastAPI는 두 형태를 **모두 받아들입니다.**

- `async def`로 쓰면 비동기 함수가 되어, 안에서 `await`를 쓸 수 있다(예: 비동기 DB 호출).
- 그냥 `def`로 쓰면 동기 함수가 되어, FastAPI가 알아서 별도 스레드 풀에서 실행한다(블로킹 호출이 있어도 다른 요청을 막지 않게).

> **이 가이드의 약속**: 입문 단계에서는 **`def`(동기) 함수**로 시작합니다. DB와 외부 호출을 다루는 06~08장부터 `async def`를 본격적으로 도입합니다. 5장의 예제는 메모리만 만지므로 동기든 비동기든 차이가 없습니다.

> **비동기(async/await)**: 한 가지 일이 끝나기를 기다리는 동안 다른 일을 처리할 수 있게 하는 문법입니다. 자세한 내용은 [용어 사전 — 비동기](glossary.md#비동기--동기-async--sync)에 있습니다.

---

## 5.3 경로 매개변수 (Path Parameters)

URL 안에 변하는 부분을 끼워 넣어 한 함수가 여러 ID를 처리하게 만드는 패턴입니다.

### 5.3.1 가장 단순한 형태

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}
```

- `{user_id}`: 경로 안의 동적 부분.
- 함수의 인자 `user_id: int`: **타입 힌트가 곧 검증·변환**입니다. URL의 그 자리에 들어온 문자열을 FastAPI가 자동으로 `int`로 바꿔서 함수에 넘깁니다.

호출 예:

| 요청 | 응답 |
|------|------|
| `GET /users/42` | `{"user_id": 42}` |
| `GET /users/abc` | `422 Unprocessable Entity` (정수가 아님) |

> **타입 힌트(Type Hint)란?** 함수 인자나 반환값의 타입을 적어두는 표기입니다(예: `def f(x: int) -> str`). Python 자체는 런타임에 이걸 강제하지 않지만, **FastAPI/Pydantic은 이 힌트를 읽어서 자동으로 검증**합니다. [용어 사전 — 타입 힌트](glossary.md#타입-힌트-type-hint)도 참고.

> **HTTP 422란?** "Unprocessable Entity"의 약자. "요청 형식은 알아들었는데 값이 검증에 실패했다"는 뜻입니다. FastAPI가 잘못된 타입의 입력을 만났을 때 자주 돌려주는 응답 코드입니다.

### 5.3.2 다양한 타입

`int`, `float`, `str`, `bool`, `UUID` 등 거의 모든 표준 타입을 그대로 쓸 수 있습니다.

```python
from uuid import UUID

@app.get("/posts/{post_id}")
def get_post(post_id: UUID):
    return {"post_id": str(post_id)}
```

| 요청 | 결과 |
|------|------|
| `GET /posts/550e8400-e29b-41d4-a716-446655440000` | 200, UUID 파싱 성공 |
| `GET /posts/abc` | 422 |

`bool` 도 자연스럽게 동작합니다 — `true`, `false`, `1`, `0`, `yes`, `no` 등을 모두 받습니다.

### 5.3.3 여러 개의 경로 매개변수

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

요청: `GET /users/1/posts/42` → `{"user_id": 1, "post_id": 42}`

함수 인자의 **이름이 곧 경로 매개변수의 이름**입니다. 순서는 중요하지 않고 이름이 일치하면 됩니다.

### 5.3.4 추가 검증 — `Path(...)`

타입만으로는 부족할 때(예: "1 이상 1000 이하의 정수만"), FastAPI의 `Path`를 씁니다.

```python
from fastapi import FastAPI, Path

app = FastAPI()


@app.get("/users/{user_id}")
def get_user(
    user_id: int = Path(..., ge=1, le=1_000_000, description="사용자 PK"),
):
    return {"user_id": user_id}
```

- `...` (말줄임표): "이 값은 필수다"라는 표시(파이썬에서 `Ellipsis` 객체).
- `ge=1`: greater than or equal to 1 (1 이상)
- `le=1_000_000`: less than or equal to 1,000,000 (1백만 이하)
- `description=...`: 자동 문서에 나타날 설명

`GET /users/0`은 422가 됩니다.

> **`Path`, `Query`, `Body` 같은 함수가 자꾸 등장합니다.** 이 함수들은 단순히 "이 인자는 이런 종류의 입력이다"라고 FastAPI에 힌트를 주는 표시입니다. 우리가 직접 호출해서 만든 객체가 인자의 기본값처럼 들어가는 모양새인데, FastAPI는 이 자리에 진짜 기본값이 아니라 "메타 정보"를 두고 검증·문서화에 사용합니다. 처음에는 약간 어색하지만 곧 익숙해집니다.

### 5.3.5 경로의 슬래시(`/`) 안 허용

기본적으로 경로 매개변수는 슬래시를 포함하지 못합니다. 즉 `/files/{path}`로 선언했을 때 `path`에 `a/b/c.txt`는 들어가지 않습니다. 파일 경로처럼 슬래시를 그대로 받고 싶다면 다음과 같이 `path:`를 명시합니다.

```python
@app.get("/files/{file_path:path}")
def read_file(file_path: str):
    return {"file_path": file_path}
```

`GET /files/img/2026/hello.png` → `{"file_path": "img/2026/hello.png"}`

---

## 5.4 쿼리 매개변수 (Query Parameters)

URL의 `?key=value&key2=value2` 부분입니다. FastAPI는 **함수 인자 중에서 경로 매개변수에 해당하지 않는 것**들을 자동으로 쿼리 매개변수로 인식합니다.

### 5.4.1 기본형

```python
@app.get("/items")
def list_items(limit: int = 10, offset: int = 0):
    return {"limit": limit, "offset": offset}
```

| 요청 | 결과 |
|------|------|
| `GET /items` | `{"limit": 10, "offset": 0}` (기본값) |
| `GET /items?limit=20` | `{"limit": 20, "offset": 0}` |
| `GET /items?limit=20&offset=40` | `{"limit": 20, "offset": 40}` |
| `GET /items?limit=abc` | 422 |

규칙은 단순합니다.

- 함수 인자에 **기본값이 있으면** 그 값은 쿼리 매개변수의 **선택값**이 된다.
- **기본값이 없으면** 그 값은 **필수**가 된다(없으면 422).

### 5.4.2 선택값(`Optional`) — 기본값을 `None`으로

```python
from typing import Optional

@app.get("/search")
def search(q: Optional[str] = None, limit: int = 10):
    return {"q": q, "limit": limit}
```

`q`가 없으면 `None`, 있으면 그 문자열이 들어옵니다. Python 3.10+에서는 다음과 같이 짧게 적어도 됩니다.

```python
@app.get("/search")
def search(q: str | None = None, limit: int = 10):
    return {"q": q, "limit": limit}
```

> **`Optional[str]`과 `str | None`의 관계**: 같습니다. Python 3.10에서 더 간결한 `|` 표기가 도입되었습니다. 이 가이드는 Python 3.13을 쓰므로 **`str | None` 표기를 1순위**로 씁니다.

### 5.4.3 추가 검증 — `Query(...)`

```python
from fastapi import Query

@app.get("/search")
def search(
    q: str | None = Query(default=None, min_length=2, max_length=50, description="검색어"),
    limit: int = Query(default=10, ge=1, le=100),
):
    return {"q": q, "limit": limit}
```

- `min_length`, `max_length`: 문자열 길이 제한
- `pattern`: 정규식 패턴 매칭 (옛 이름 `regex`, 더 이상 권장 안 함)
- `ge`, `le`, `gt`, `lt`: 숫자 범위
- `default=...`: 기본값 (말줄임표 `...`을 넣으면 필수)

### 5.4.4 같은 이름의 쿼리를 여러 번 받기 — 리스트

```python
@app.get("/posts")
def list_posts(tag: list[str] | None = Query(default=None)):
    return {"tags": tag}
```

`GET /posts?tag=python&tag=fastapi&tag=web` → `{"tags": ["python", "fastapi", "web"]}`

### 5.4.5 `bool` 쿼리 매개변수

```python
@app.get("/items")
def list_items(active: bool = True):
    return {"active": active}
```

`?active=false`, `?active=0`, `?active=no`는 모두 `False`로 인식됩니다.

### 5.4.6 자주 헷갈리는 점 — 경로 매개변수와 쿼리 매개변수의 구분

FastAPI의 규칙은 단순합니다.

1. 함수 인자의 이름이 **데코레이터 경로의 `{...}`에 들어 있으면** → 경로 매개변수
2. 그 외에는 → 쿼리 매개변수
3. (단, Pydantic 모델 인자는 → 요청 본문, 곧 5.5에서)

```python
@app.get("/users/{user_id}/posts")
def list_user_posts(
    user_id: int,                    # 경로 매개변수 ({user_id}에 매칭)
    limit: int = 10,                  # 쿼리 매개변수
    tag: str | None = None,           # 쿼리 매개변수
):
    return {"user_id": user_id, "limit": limit, "tag": tag}
```

`GET /users/1/posts?limit=5&tag=python` → `{"user_id": 1, "limit": 5, "tag": "python"}`

---

## 5.5 요청 본문 — Pydantic 모델

POST나 PUT처럼 큰 자료를 받을 때는 보통 **JSON 본문**으로 전달합니다. FastAPI는 이 본문을 받기 위해 **Pydantic 모델**을 씁니다.

### 5.5.1 Pydantic 모델이란

> **Pydantic이란?** 파이썬에서 데이터의 모양(스키마)을 클래스로 선언하면, 자동으로 **타입 검증·JSON 변환·문서화**까지 해주는 라이브러리입니다. FastAPI의 데이터 처리는 거의 다 Pydantic이 담당합니다. 현재 v2.x. 자세한 내용은 [공식 문서](https://docs.pydantic.dev/)를 참고하세요.

`BaseModel`을 상속하면 그 클래스의 인스턴스는 자동 검증되고 JSON과 자유롭게 오갑니다.

```python
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    name: str
    age: int = 0
```

이 클래스는 다음을 의미합니다.

- `email`, `name` — 필수 문자열
- `age` — 기본값 0인 정수

### 5.5.2 본문 받기

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserCreate(BaseModel):
    email: str
    name: str


@app.post("/users")
def create_user(user: UserCreate):
    # user는 이미 검증된 UserCreate 인스턴스
    return {"created": user}
```

요청:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","name":"Alice"}'
```

응답: `{"created": {"email":"a@b.com","name":"Alice"}}`

빈 본문이거나, 필수 필드가 빠지거나, 타입이 안 맞으면 자동으로 **422**가 돌아갑니다. **에러 본문에는 어느 필드가 왜 틀렸는지가 함께 들어갑니다.**

```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {"name": "Alice"}
    }
  ]
}
```

### 5.5.3 필드별 검증 — `Field(...)`

`Field`는 Pydantic 모델 안에서 각 필드에 검증·메타정보를 붙이는 도구입니다(`Path`/`Query`의 모델 버전이라고 보면 됩니다).

```python
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=100, description="사용자 이메일")
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(default=0, ge=0, le=150)
```

- `...`: 필수
- `default=...`: 기본값(있으면 선택값)
- `min_length`, `max_length`: 문자열·리스트 길이
- `ge`, `le`, `gt`, `lt`: 숫자 범위
- `pattern=r"..."`: 정규식
- `description=...`: 자동 문서에 나오는 설명

### 5.5.4 더 정밀한 타입 — `EmailStr`, `HttpUrl` 등

기본 `str`보다 의미가 분명한 타입을 쓰면 검증이 더 엄격해집니다.

```python
from pydantic import BaseModel, EmailStr, HttpUrl


class UserCreate(BaseModel):
    email: EmailStr           # 이메일 형식 검증
    homepage: HttpUrl | None = None  # URL 형식 검증
```

`EmailStr`을 쓰려면 추가 설치가 필요합니다.

```bash
uv add "pydantic[email]"
```

### 5.5.5 모델 안에 모델 — 중첩

```python
class Address(BaseModel):
    city: str
    zipcode: str


class UserCreate(BaseModel):
    email: str
    name: str
    address: Address | None = None
```

요청 본문 예시:

```json
{
  "email": "a@b.com",
  "name": "Alice",
  "address": {"city": "Seoul", "zipcode": "06000"}
}
```

### 5.5.6 본문 + 경로 매개변수 + 쿼리 매개변수 한꺼번에

세 가지를 한 함수에서 동시에 받을 수 있습니다. **타입을 보고 FastAPI가 알아서 분류**해 줍니다.

```python
@app.put("/users/{user_id}")
def update_user(
    user_id: int,                 # 경로 매개변수 ({user_id})
    user: UserCreate,             # 본문 (Pydantic 모델)
    notify: bool = False,         # 쿼리 매개변수
):
    return {"id": user_id, "user": user, "notify": notify}
```

호출:

```bash
curl -X PUT "http://127.0.0.1:8000/users/1?notify=true" \
  -H "Content-Type: application/json" \
  -d '{"email":"a@b.com","name":"Alice"}'
```

---

## 5.6 응답 모델 (`response_model`)

요청을 받는 모델은 위에서 다뤘으니, 이번엔 **응답 모델**입니다. "이 엔드포인트는 이런 모양으로 답한다"고 미리 선언해 두면 다음 세 가지 이점이 한꺼번에 옵니다.

1. **자동 문서**가 응답 스키마를 정확히 보여준다.
2. **응답이 검증**된다(우리 코드가 실수로 다른 모양을 돌려주면 알려준다).
3. **필터링**된다 — 모델에 없는 필드는 응답에서 자동으로 제거된다(예: 비밀번호 해시).

### 5.6.1 가장 단순한 사용

```python
from pydantic import BaseModel


class UserOut(BaseModel):
    id: int
    email: str
    name: str


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    # 우리가 만든 dict에 모델에 없는 필드가 있어도, 응답에서는 자동으로 빠진다
    return {"id": user_id, "email": "a@b.com", "name": "Alice", "password_hash": "secret"}
```

응답: `{"id": 1, "email": "a@b.com", "name": "Alice"}` — `password_hash`는 자동으로 빠집니다.

### 5.6.2 입력 모델과 출력 모델 분리하기

거의 항상 **입력과 출력은 모양이 다릅니다.** 비밀번호는 입력에는 있고 출력에는 없어야 하고, 반대로 `id`나 `created_at`은 출력에만 있죠. 이 가이드의 권장 패턴은 다음과 같습니다.

```python
from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    """입력·출력에 공통으로 들어가는 필드들"""
    email: str
    name: str


class UserCreate(UserBase):
    """클라이언트가 만들 때 보내는 입력"""
    password: str


class UserUpdate(BaseModel):
    """수정 시 보내는 입력 — 모두 선택값"""
    email: str | None = None
    name: str | None = None
    password: str | None = None


class UserRead(UserBase):
    """서버가 돌려주는 출력"""
    id: int
    created_at: datetime
```

이 패턴은 06장 이후 본격적으로 쓰는 SQLAlchemy 모델과의 분리에도 그대로 이어집니다.

### 5.6.3 함수의 반환 타입으로 대체

`response_model=...`을 데코레이터에 적는 대신, 함수의 **반환 타입 어노테이션**으로 적어도 같은 효과가 납니다.

```python
@app.get("/users/{user_id}")
def get_user(user_id: int) -> UserRead:
    ...
```

> **권장**: 둘 중 하나만 일관되게 씁니다. `response_model`을 데코레이터에 두면 "이 엔드포인트의 명세"가 한 줄에 모이고, 반환 타입에 두면 함수의 시그니처에서 바로 보입니다. 본 가이드는 **반환 타입 어노테이션**을 1순위로 씁니다 — 타입 체커(Pylance/mypy)가 함수 본문도 함께 검사해 주기 때문입니다.

### 5.6.4 응답에서 `None` 필드 빼기

기본적으로 응답에는 `null` 값을 가진 필드도 그대로 들어갑니다.

```json
{"id": 1, "email": "a@b.com", "name": "Alice", "homepage": null}
```

`null`을 통째로 빼고 싶으면 `response_model_exclude_none=True`를 씁니다.

```python
@app.get("/users/{user_id}", response_model=UserRead, response_model_exclude_none=True)
def get_user(user_id: int):
    ...
```

응답: `{"id": 1, "email": "a@b.com", "name": "Alice"}`

### 5.6.5 응답에서 일부 필드만 골라 보내기

```python
@app.get(
    "/users/{user_id}",
    response_model=UserRead,
    response_model_include={"id", "name"},          # 이 필드만 보냄
    # 또는 response_model_exclude={"email"} — 이 필드는 빼고 보냄
)
def get_user(user_id: int):
    ...
```

---

## 5.7 상태 코드와 응답 명세

### 5.7.1 `status_code=...`

기본 응답 상태 코드를 200(또는 응답 본문이 없으면 204)이 아닌 다른 값으로 두려면 다음과 같이 적습니다.

```python
from fastapi import status


@app.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate) -> UserRead:
    ...
```

`status_code=201`처럼 정수를 직접 적어도 동작합니다. **`fastapi.status` 안의 상수를 쓰면 코드가 더 또렷합니다.**

자주 쓰는 상태 코드:

| 상수 | 숫자 | 용도 |
|------|------|------|
| `status.HTTP_200_OK` | 200 | 성공 (기본값) |
| `status.HTTP_201_CREATED` | 201 | 생성 완료 (POST의 일반적 성공) |
| `status.HTTP_204_NO_CONTENT` | 204 | 성공, 응답 본문 없음 (DELETE의 일반적 성공) |
| `status.HTTP_400_BAD_REQUEST` | 400 | 클라이언트 요청 오류 |
| `status.HTTP_401_UNAUTHORIZED` | 401 | 인증 필요 |
| `status.HTTP_403_FORBIDDEN` | 403 | 권한 없음 |
| `status.HTTP_404_NOT_FOUND` | 404 | 자원 없음 |
| `status.HTTP_409_CONFLICT` | 409 | 충돌(중복 등) |
| `status.HTTP_422_UNPROCESSABLE_ENTITY` | 422 | 검증 실패 (FastAPI가 자동으로 돌려줌) |
| `status.HTTP_500_INTERNAL_SERVER_ERROR` | 500 | 서버 내부 오류 |

### 5.7.2 204 No Content — 본문 없는 응답

```python
@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int):
    # 아무것도 반환하지 않거나, None을 반환
    return None
```

204는 **본문이 비어 있어야 하는 약속**이라, `response_model`을 함께 두지 않습니다.

### 5.7.3 `responses=...`로 여러 응답 명세

자동 문서에 "이 엔드포인트는 200 외에도 404, 409 같은 응답이 있을 수 있다"고 적어두려면 `responses=`를 씁니다.

```python
@app.get(
    "/users/{user_id}",
    response_model=UserRead,
    responses={
        404: {"description": "사용자를 찾을 수 없음"},
        500: {"description": "서버 내부 오류"},
    },
)
def get_user(user_id: int) -> UserRead:
    ...
```

`/docs`를 열어 보면 가능한 응답 코드들이 표로 정리됩니다.

---

## 5.8 에러 처리 — `HTTPException`

검증 외의 비즈니스 에러(자원 없음, 권한 없음, 충돌 등)는 우리가 직접 적절한 상태 코드로 응답해야 합니다. FastAPI에서는 **`HTTPException`을 `raise`** 하면 됩니다.

### 5.8.1 기본 사용

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

USERS = {1: {"id": 1, "name": "Alice"}}


@app.get("/users/{user_id}")
def get_user(user_id: int):
    user = USERS.get(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 사용자를 찾을 수 없습니다",
        )
    return user
```

응답 (사용자가 없을 때):

```json
{
  "detail": "해당 사용자를 찾을 수 없습니다"
}
```

`detail`은 문자열뿐 아니라 dict, list도 들어갑니다.

```python
raise HTTPException(
    status_code=409,
    detail={"code": "EMAIL_TAKEN", "message": "이미 가입된 이메일입니다"},
)
```

### 5.8.2 `headers=...` 추가

응답 헤더를 같이 붙일 수 있습니다.

```python
raise HTTPException(
    status_code=401,
    detail="로그인이 필요합니다",
    headers={"WWW-Authenticate": "Bearer"},
)
```

### 5.8.3 일반 `Exception`은 500이 된다

`HTTPException`이 아닌 일반 파이썬 예외는 잡히지 않으면 **500 Internal Server Error**로 응답되고, 콘솔에는 트레이스백이 찍힙니다. 우리가 의도한 4xx 에러를 일반 `Exception`으로 던지면 안 됩니다 — 항상 `HTTPException`을 사용하세요.

### 5.8.4 사용자 정의 예외를 핸들러로 매핑

특정 도메인 예외(예: `UserNotFound`)를 정의해 두고, 한 곳에서 통째로 401/404로 매핑하고 싶을 때:

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class UserNotFound(Exception):
    def __init__(self, user_id: int):
        self.user_id = user_id


app = FastAPI()


@app.exception_handler(UserNotFound)
def handle_user_not_found(request: Request, exc: UserNotFound):
    return JSONResponse(
        status_code=404,
        content={"detail": f"사용자 {exc.user_id} 없음"},
    )


@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id not in USERS:
        raise UserNotFound(user_id)
    return USERS[user_id]
```

이 패턴은 코드가 커졌을 때 진가를 발휘합니다. 5.x에서는 `HTTPException` 하나로 충분합니다.

---

## 5.9 자동 문서에 메타 정보 채우기 — `tags`, `summary`, `description`

FastAPI가 만들어 주는 `/docs`(Swagger UI)와 `/redoc`은 코드만으로도 충분히 유용하지만, 약간의 메타 정보를 더해 주면 클라이언트 개발자(또는 미래의 나)가 훨씬 편합니다.

### 5.9.1 `tags` — 그룹핑

`/docs`에서 같은 `tags`를 가진 엔드포인트끼리 한 묶음으로 묶입니다.

```python
@app.get("/users", tags=["users"])
def list_users():
    ...


@app.get("/posts", tags=["posts"])
def list_posts():
    ...
```

### 5.9.2 `summary`, `description`

```python
@app.get(
    "/users/{user_id}",
    summary="사용자 한 명 조회",
    description="기본 키로 사용자 한 명을 조회합니다. 없으면 404를 돌려줍니다.",
)
def get_user(user_id: int):
    ...
```

`summary`는 한 줄 요약, `description`은 더 긴 설명입니다. **함수의 docstring을 자동 description으로 가져갑니다** — 그래서 보통은 docstring으로 적습니다.

```python
@app.get("/users/{user_id}", summary="사용자 한 명 조회")
def get_user(user_id: int):
    """
    기본 키로 사용자 한 명을 조회합니다.

    - **user_id**: 사용자 PK (1 이상의 정수)
    - 없으면 404, 있으면 200으로 사용자 정보를 돌려줍니다.
    """
    ...
```

마크다운이 그대로 렌더링됩니다.

### 5.9.3 엔드포인트 숨기기 — `include_in_schema=False`

내부용 헬스체크 같은 엔드포인트는 자동 문서에서 빼는 게 깔끔합니다.

```python
@app.get("/health", include_in_schema=False)
def healthcheck():
    return {"status": "ok"}
```

---

## 5.10 `APIRouter` — 라우트를 모듈로 쪼개기

라우트가 늘어나면 `app.py` 한 파일에 다 두기 부담스러워집니다. **도메인 단위로 모듈을 쪼개고 한 곳에서 합치는** 패턴이 표준입니다.

### 5.10.1 기본 사용

```python
# app/routers/users.py
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
def list_users():
    return [{"id": 1, "name": "Alice"}]


@router.get("/{user_id}")
def get_user(user_id: int):
    return {"id": user_id, "name": "Alice"}
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import users

app = FastAPI()
app.include_router(users.router)
```

`prefix="/users"`를 라우터에 두면 안에 적힌 `@router.get("/")`이 `GET /users/`가, `@router.get("/{user_id}")`가 `GET /users/{user_id}`가 됩니다.

### 5.10.2 `APIRouter`도 `app`처럼 쓴다

`APIRouter`의 데코레이터는 `app`의 데코레이터와 거의 똑같이 생겼습니다. `@app.get(...)` 자리에 `@router.get(...)`만 넣으면 됩니다. `response_model`, `status_code`, `responses=`, `tags`, `summary`, `description`, `include_in_schema` 모두 그대로 동작합니다.

### 5.10.3 `tags`는 라우터에서 한 번에

```python
router = APIRouter(prefix="/users", tags=["users"])
```

이렇게 적으면 안의 모든 엔드포인트가 자동으로 `tags=["users"]`를 갖습니다. 개별 엔드포인트에서 `tags`를 다시 적으면 합쳐집니다.

### 5.10.4 `include_router`의 옵션

`app.include_router(router, prefix="/api/v1")`처럼 메인에서 추가 prefix를 더 붙일 수도 있습니다.

```python
app.include_router(users.router, prefix="/api/v1")
# users.py의 router에 이미 prefix="/users"가 있다면
# 최종 경로는 /api/v1/users, /api/v1/users/{user_id}
```

`tags`, `dependencies`, `responses`도 라우터 단위로 모아 줄 수 있습니다.

### 5.10.5 표준 폴더 구조

이 가이드의 표준 구조는 다음과 같습니다.

```
my-api/
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI 인스턴스 + 라우터 include
│   ├── schemas.py         # Pydantic 모델
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       ├── posts.py
│       └── auth.py
└── tests/
    ├── __init__.py
    └── test_users.py
```

이 챕터의 종합 실습(5.18절 명언 API)에서 이 구조를 그대로 만듭니다.

> **`__init__.py` 빈 파일은 왜 있나요?** Python에서 폴더를 "패키지"로 인식하게 만드는 표시 파일입니다. 빈 파일이어도 됩니다. 옛 Python에서는 필수였고, 현대 Python(3.3+)은 없어도 동작하지만 도구·에디터가 더 잘 인식하도록 두는 게 관례입니다.

---

## 5.11 헤더와 쿠키 받기

### 5.11.1 헤더 — `Header(...)`

```python
from fastapi import Header


@app.get("/items")
def list_items(
    user_agent: str | None = Header(default=None),
    x_request_id: str | None = Header(default=None),
):
    return {"user_agent": user_agent, "request_id": x_request_id}
```

함수 인자 이름의 언더스코어(`user_agent`)가 자동으로 하이픈(`User-Agent`)으로 변환됩니다. 그게 마음에 안 들면 `Header(default=None, convert_underscores=False)`로 끌 수 있습니다.

### 5.11.2 임의 헤더

`Authorization: Bearer xxx` 같은 헤더도 `Header`로 그대로 받을 수 있습니다(다만 인증은 8장에서 본격적으로 다룹니다).

```python
@app.get("/me")
def me(authorization: str | None = Header(default=None)):
    return {"authorization": authorization}
```

### 5.11.3 쿠키 — `Cookie(...)`

```python
from fastapi import Cookie


@app.get("/me")
def me(session_id: str | None = Cookie(default=None)):
    return {"session_id": session_id}
```

이 가이드의 인증은 쿠키 대신 JWT를 헤더에 실어 보냅니다. 쿠키는 가볍게 알아두는 정도면 됩니다.

### 5.11.4 응답 헤더와 쿠키 설정

응답에 헤더·쿠키를 넣고 싶으면 `Response`를 인자로 받아 쓰는 패턴이 가장 단순합니다.

```python
from fastapi import Response


@app.post("/login")
def login(response: Response):
    response.set_cookie(key="session_id", value="abc123", httponly=True, secure=True)
    response.headers["X-Custom"] = "hello"
    return {"ok": True}
```

---

## 5.12 폼과 파일 (간단히)

JSON이 아니라 **HTML 폼 데이터**(`application/x-www-form-urlencoded`)나 **파일 업로드**(`multipart/form-data`)를 받을 때 쓰는 도구입니다.

### 5.12.1 폼 필드 — `Form(...)`

`uv add python-multipart` 한 번 설치해 둡니다(폼/파일을 다룰 때 필요).

```python
from fastapi import Form


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}
```

`POST /login` 본문이 `username=alice&password=secret` 같은 모양이라고 가정합니다. 이 가이드의 **REST API 방식에서는 거의 쓰지 않습니다** — 인증조차 JSON으로 처리합니다. 하지만 OAuth2 표준의 일부 흐름에서 폼 형식을 요구해 등장할 수 있어 알아둡니다.

### 5.12.2 파일 업로드 — `UploadFile`

```python
from fastapi import File, UploadFile


@app.post("/upload")
def upload(file: UploadFile = File(...)):
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(file.file.read()),
    }
```

여러 파일을 한 번에 받을 수도 있습니다.

```python
@app.post("/upload-many")
def upload_many(files: list[UploadFile] = File(...)):
    return [{"filename": f.filename} for f in files]
```

> **이 챕터의 범위**: 폼·파일은 자주 등장하지 않으므로 깊이 다루지 않습니다. 자세한 처리(저장, 스트리밍, 크기 제한)는 [FastAPI 공식 문서의 Files 절](https://fastapi.tiangolo.com/tutorial/request-files/)을 참고하세요.

---

## 5.13 의존성 주입 (`Depends`) 맛보기

`Depends`는 FastAPI의 가장 강력한 기능 중 하나입니다. **본격은 08장에서 인증과 함께 다룹니다.** 여기서는 라우팅 흐름 안에서 한 번 보고 넘어갑니다.

### 5.13.1 무엇을 해결하나

여러 라우트에서 똑같은 전처리를 해야 할 때(예: 페이지네이션 매개변수 파싱)를 매번 함수마다 풀어쓰는 대신 **함수 하나로 떼어두고 인자로 받습니다.**

### 5.13.2 가장 단순한 예

```python
from fastapi import Depends


def common_pagination(limit: int = 10, offset: int = 0) -> dict:
    return {"limit": limit, "offset": offset}


@app.get("/items")
def list_items(pagination: dict = Depends(common_pagination)):
    return {"pagination": pagination}


@app.get("/users")
def list_users(pagination: dict = Depends(common_pagination)):
    return {"pagination": pagination}
```

`Depends(common_pagination)`이라고 적으면 FastAPI가 다음을 해 줍니다.

1. 들어온 요청에서 `limit`, `offset`을 찾아 `common_pagination`에 넣어 호출.
2. 그 반환값을 `pagination` 인자에 넣어 우리 핸들러를 호출.

### 5.13.3 `Annotated`로 더 깔끔하게

Python 3.9+의 `Annotated`를 쓰면 의존성 선언이 더 또렷합니다.

```python
from typing import Annotated


CommonPagination = Annotated[dict, Depends(common_pagination)]


@app.get("/items")
def list_items(pagination: CommonPagination):
    return {"pagination": pagination}
```

> **이 가이드의 약속**: 5장 본문에서는 `Depends(...)`가 인자 기본값에 들어가는 옛 스타일을 더 자주 보여줍니다(처음 보기에 직관적). 08장 인증부터는 `Annotated` 스타일로 전환합니다. 현재(2026-04) FastAPI 공식 문서도 `Annotated`를 권장합니다.

---

## 5.14 자동 문서로 직접 호출해 보기 — `/docs`

여기까지 왔다면 가장 좋은 학습 도구는 직접 서버를 띄우고 `/docs`를 열어 보는 것입니다.

1. `uv run uvicorn app.main:app --reload` 로 띄운다.
2. 브라우저에서 `http://127.0.0.1:8000/docs`를 연다.
3. 등록된 엔드포인트 목록이 보인다.
4. 한 엔드포인트를 펼친 뒤 **"Try it out"** → 입력 채우고 **"Execute"** → 응답 확인.

`/docs`(Swagger UI)는 인터랙티브, `/redoc`은 깔끔한 읽기 전용 문서입니다. 둘 다 같은 OpenAPI 스펙(`/openapi.json`)을 기반으로 자동 생성됩니다. **이 자동 문서가 FastAPI의 가장 큰 차별점**임을 잊지 마세요.

> **OpenAPI / Swagger / ReDoc**:
> - **OpenAPI**: REST API 명세를 JSON/YAML로 적는 표준. 옛 이름이 Swagger.
> - **Swagger UI**: OpenAPI 명세를 보고 인터랙티브하게 테스트할 수 있는 웹 페이지. FastAPI가 `/docs`로 자동 띄움.
> - **ReDoc**: 같은 명세를 더 깔끔한 읽기 전용 문서로 보여줌. FastAPI가 `/redoc`으로 자동 띄움.
> 더 자세한 내용은 [용어 사전 — OpenAPI / Swagger UI / ReDoc](glossary.md#openapi--swagger-ui--redoc)에 있습니다.

---

## 5.15 테스트 — `TestClient`와 pytest

FastAPI 앱은 **서버를 실제로 띄우지 않고도** 테스트할 수 있습니다. `TestClient`가 우리 앱을 직접 호출해 응답을 돌려줍니다.

### 5.15.1 설치

```bash
uv add --dev pytest httpx
```

`TestClient`는 내부적으로 `httpx`를 씁니다.

> **`--dev`란?** 개발할 때만 필요한 라이브러리(예: 테스트 도구)를 표시해 두는 옵션입니다. 실제 운영 환경에는 깔리지 않게 분리할 수 있습니다.

### 5.15.2 가장 단순한 테스트

```python
# tests/test_app.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_hello():
    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, world!"}
```

실행:

```bash
uv run pytest
```

`TestClient`는 `requests`/`httpx`와 거의 같은 인터페이스를 갖습니다. `client.get(...)`, `client.post(...)`, `client.put(...)`, `client.delete(...)` 등이 모두 됩니다.

### 5.15.3 본문이 있는 요청

```python
def test_create_user():
    response = client.post(
        "/users",
        json={"email": "a@b.com", "name": "Alice"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "a@b.com"
```

`json=...`을 쓰면 자동으로 `Content-Type: application/json` 헤더가 붙고 본문이 직렬화됩니다.

### 5.15.4 검증 실패 케이스도 테스트

```python
def test_create_user_invalid_email():
    response = client.post("/users", json={"email": ""})
    assert response.status_code == 422
```

### 5.15.5 비동기 클라이언트(`httpx.AsyncClient`)

`async def` 라우트와 비동기 DB를 본격적으로 쓰기 시작하면, `httpx.AsyncClient`로 직접 비동기 테스트도 쓸 수 있습니다(고급 주제). 이 챕터에서는 `TestClient` 한 가지로 충분합니다.

---

## 5.16 CORS — 웹 프론트엔드와 연동할 때

> **CORS란?** 브라우저가 보안상 "다른 도메인의 API"를 마음대로 부르지 못하게 막는 약속입니다. 백엔드에서 "이 도메인은 허용한다"는 헤더를 응답에 붙여줘야 브라우저가 허락합니다. 자세한 내용은 [용어 사전 — CORS](glossary.md#cors-cross-origin-resource-sharing)에 있습니다.

웹 프론트엔드(React, Vue 등)가 우리 API를 부를 때만 신경 쓰면 됩니다. iOS/Android 앱만 클라이언트라면 CORS는 필요 없습니다.

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],   # 운영: 특정 도메인만
    # allow_origins=["*"],                   # 개발: 모두 허용 (운영 비추천)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 5.17 자주 헷갈리는 포인트

### 5.17.1 `{user_id}`와 함수 인자 이름이 일치해야 함

```python
@app.get("/users/{user_id}")
def get_user(userId: int):  # ❌ 이름 불일치
    return {"id": userId}
```

이렇게 적으면 FastAPI는 `userId`를 쿼리 매개변수로 인식하고 `{user_id}`를 사용하지 않은 채로 버립니다(또는 검증 에러). **꼭 함수 인자 이름이 경로의 `{...}`와 같아야** 합니다.

### 5.17.2 두 라우트 정의 순서 — 더 구체적인 쪽을 위에

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):
    ...

@app.get("/users/me")
def get_me():
    ...
```

이 코드는 `GET /users/me`가 들어왔을 때 **앞쪽 `{user_id}`에 매칭되려 시도하다가** "me는 정수가 아니다"로 422를 돌려보낼 수 있습니다. 항상 **더 구체적인 라우트(`/users/me`)를 위에** 두세요.

```python
@app.get("/users/me")
def get_me():
    ...

@app.get("/users/{user_id}")
def get_user(user_id: int):
    ...
```

### 5.17.3 `Content-Type` 헤더 누락 (curl 호출 시)

```bash
curl -X POST http://127.0.0.1:8000/users -d '{"email":"a@b.com"}'
# Content-Type 없음 → 폼 데이터로 해석 시도 → 422
```

JSON 본문을 보낼 때는 항상 `-H "Content-Type: application/json"`을 붙이세요.

### 5.17.4 응답 모델에 없는 필드는 자동으로 빠짐

`response_model=UserOut`을 두고 `password_hash`가 들어 있는 dict를 반환해도, 응답에서는 자동으로 빠집니다. 이건 **버그가 아니라 기능**입니다 — 비밀번호 해시 같은 민감한 필드를 실수로 응답에 흘릴 위험을 줄여줍니다.

### 5.17.5 같은 라우트를 두 번 등록

같은 경로 + 같은 메서드로 두 번 데코레이터를 붙이면, FastAPI는 **두 번째 정의를 무시**합니다(또는 라우터 결합 순서에 따라 첫 번째 매칭이 응답). 의도치 않은 중복은 라우트 등록을 한 곳에서 관리해서 막으세요(`APIRouter` 도입의 이유 중 하나).

### 5.17.6 `BaseModel`을 GET 요청에 쓰지 않는다

```python
# 보통 동작하지 않거나 어색하다
@app.get("/search")
def search(query: SearchQuery):  # ← FastAPI는 이걸 본문으로 인식
    ...
```

GET 요청은 본문을 거의 쓰지 않습니다. 검색 조건이 많아도 쿼리 매개변수로 받습니다. 묶어서 받고 싶으면 `Annotated`와 `Depends`를 쓰는 패턴이 있지만(고급), 5장 단계에서는 **GET은 쿼리 매개변수, POST/PUT/PATCH는 Pydantic 본문**을 그대로 따르세요.

---

## 5.18 실습 — 메모리 기반 명언(Quote) API 만들기

지금까지 배운 모든 조각(라우팅, 경로/쿼리/본문, Pydantic 모델, 응답 모델, 상태 코드, `HTTPException`, `APIRouter`, 테스트)을 **하나의 작은 프로젝트**로 묶어 봅니다. 데이터베이스는 아직 등장하지 않습니다(메모리 `dict`로 충분). 다음 챕터(06)에서 자연스럽게 같은 자료구조를 SQLAlchemy로 옮길 것입니다.

> **이 절의 코드 전체는** `examples/05-QuoteAPI/`에 동일하게 들어 있습니다. 직접 타이핑하다 막히면 그 폴더와 비교하세요.

### 5.18.1 프로젝트 구조

```
05-QuoteAPI/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 인스턴스 + 라우터 include
│   ├── schemas.py          # Pydantic 모델
│   └── routers/
│       ├── __init__.py
│       └── quotes.py       # /quotes 라우트들
└── tests/
    ├── __init__.py
    └── test_quotes.py      # TestClient 기반 통합 테스트
```

### 5.18.2 프로젝트 만들기

```bash
mkdir 05-QuoteAPI
cd 05-QuoteAPI
uv init
uv add fastapi "uvicorn[standard]"
uv add --dev pytest httpx
```

`uv init`이 만든 기본 파일(`hello.py` 또는 `main.py`)은 지워도 됩니다. 우리는 `app/` 폴더 아래에 다시 만듭니다.

```bash
mkdir -p app/routers tests
touch app/__init__.py app/routers/__init__.py tests/__init__.py
```

### 5.18.3 Pydantic 모델 — `app/schemas.py`

요청·응답에 쓸 모델을 한곳에 모읍니다.

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, Field


class QuoteBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=500, description="명언 본문")
    author: str = Field(..., min_length=1, max_length=100, description="저자")


class QuoteCreate(QuoteBase):
    """POST /quotes 요청 본문."""


class QuoteUpdate(BaseModel):
    """PATCH /quotes/{id} 요청 본문 — 모든 필드가 선택값."""
    text: str | None = Field(default=None, min_length=1, max_length=500)
    author: str | None = Field(default=None, min_length=1, max_length=100)


class QuoteRead(QuoteBase):
    """모든 응답에서 쓰는 출력 모델."""
    id: int
    created_at: datetime
```

이 분리(`Base`/`Create`/`Update`/`Read`)는 06장 이후에도 그대로 이어집니다.

### 5.18.4 라우터 — `app/routers/quotes.py`

이 파일이 이 챕터의 **하이라이트**입니다. 모든 엔드포인트를 한 라우터에 모읍니다.

```python
# app/routers/quotes.py
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import QuoteCreate, QuoteRead, QuoteUpdate

router = APIRouter(prefix="/quotes", tags=["quotes"])

# 메모리 저장소 — 학습용. 서버를 끄면 사라진다.
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
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
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
    """PUT은 전체 덮어쓰기 — 들어온 본문 그대로 반영합니다."""
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
        created_at=existing.created_at,  # 생성 시간은 그대로 유지
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
    """PATCH는 일부만 갱신 — 보내준 필드만 바꿉니다."""
    existing = _QUOTES.get(quote_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    data = existing.model_dump()
    patch = payload.model_dump(exclude_unset=True)  # 보낸 필드만 추림
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
    if quote_id not in _QUOTES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 명언을 찾을 수 없습니다",
        )
    del _QUOTES[quote_id]
    return None
```

핵심 포인트:

- `APIRouter(prefix="/quotes", tags=["quotes"])` 한 줄로 모든 엔드포인트의 prefix와 tag가 통일됩니다.
- 모든 응답에 `response_model`이 명시되어 있어 자동 문서가 또렷해집니다.
- `HTTPException`으로 404를 일관되게 내려줍니다.
- `model_dump(exclude_unset=True)`로 PATCH의 부분 갱신을 깔끔하게 처리합니다 — Pydantic이 "사용자가 실제로 보낸 필드만" 추려 줍니다.
- `_QUOTES`, `_NEXT_ID`는 모듈 전역에 둔 메모리 저장소입니다(학습용). 06장에서 SQLAlchemy로 자연스럽게 대체됩니다.

> **`global _NEXT_ID`가 필요한 이유**: 함수 안에서 모듈 전역 변수에 **다시 대입**(`_NEXT_ID += 1`)을 하려면 `global` 선언이 필요합니다. 단순 읽기는 선언이 필요 없습니다.

> **`exclude_unset=True`는 무엇이 다른가?** Pydantic 모델은 "기본값으로 둔 필드"와 "사용자가 실제로 보낸 필드"를 구분해서 기억합니다. `exclude_unset=True`는 후자만 추려 dict를 만듭니다. PATCH의 의도("보낸 것만 바꾼다")를 그대로 코드로 옮길 수 있습니다.

### 5.18.5 메인 — `app/main.py`

```python
# app/main.py
from fastapi import FastAPI

from app.routers import quotes

app = FastAPI(
    title="Quote API",
    description="메모리 기반 명언 관리 REST API (FastAPI 가이드 5장 실습)",
    version="0.1.0",
)

app.include_router(quotes.router)


@app.get("/", tags=["root"])
def root() -> dict[str, str]:
    return {"message": "Hello, Quote API!", "docs": "/docs"}
```

### 5.18.6 실행

```bash
uv run uvicorn app.main:app --reload
```

브라우저에서:

- `http://127.0.0.1:8000/` — 인사 메시지
- `http://127.0.0.1:8000/docs` — Swagger UI에서 직접 호출

`/docs`에서 `POST /quotes/`를 펼쳐 "Try it out"으로 명언 한 개를 만들고, `GET /quotes/`로 목록을 받아 보세요.

### 5.18.7 curl로 시나리오 한 번 돌려보기

```bash
# 1) 명언 생성 (201 Created)
curl -X POST http://127.0.0.1:8000/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"text":"Stay hungry, stay foolish.","author":"Steve Jobs"}'

# → {"text":"Stay hungry, stay foolish.","author":"Steve Jobs","id":1,"created_at":"..."}

# 2) 목록
curl http://127.0.0.1:8000/quotes/

# 3) 단건 조회
curl http://127.0.0.1:8000/quotes/1

# 4) 부분 수정 (저자만 바꾸기)
curl -X PATCH http://127.0.0.1:8000/quotes/1 \
  -H "Content-Type: application/json" \
  -d '{"author":"S. Jobs"}'

# 5) 검증 실패 — 빈 텍스트는 422
curl -X POST http://127.0.0.1:8000/quotes/ \
  -H "Content-Type: application/json" \
  -d '{"text":"","author":"Anon"}'

# 6) 삭제 (204 No Content)
curl -X DELETE http://127.0.0.1:8000/quotes/1 -i
```

### 5.18.8 테스트 — `tests/test_quotes.py`

```python
# tests/test_quotes.py
from fastapi.testclient import TestClient

from app.main import app
from app.routers import quotes

client = TestClient(app)


def setup_function(function):
    """각 테스트 함수 실행 전에 메모리 저장소를 깨끗이 비웁니다."""
    quotes._QUOTES.clear()
    quotes._NEXT_ID = 1


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_create_and_list_quote():
    # 생성
    response = client.post(
        "/quotes/",
        json={"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["author"] == "Steve Jobs"
    assert "created_at" in body

    # 목록
    response = client.get("/quotes/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["text"] == "Stay hungry, stay foolish."


def test_get_quote_not_found():
    response = client.get("/quotes/999")
    assert response.status_code == 404
    assert "찾을 수 없습니다" in response.json()["detail"]


def test_create_validation_error_empty_text():
    response = client.post(
        "/quotes/",
        json={"text": "", "author": "Anon"},
    )
    assert response.status_code == 422


def test_patch_partial_update():
    # 먼저 하나 만든다
    created = client.post(
        "/quotes/",
        json={"text": "원본 텍스트", "author": "원본 저자"},
    ).json()
    qid = created["id"]

    # 저자만 바꾼다
    response = client.patch(f"/quotes/{qid}", json={"author": "새 저자"})
    assert response.status_code == 200
    body = response.json()
    assert body["author"] == "새 저자"
    assert body["text"] == "원본 텍스트"  # 텍스트는 그대로


def test_delete_then_404():
    created = client.post(
        "/quotes/",
        json={"text": "지울 명언", "author": "Anon"},
    ).json()
    qid = created["id"]

    response = client.delete(f"/quotes/{qid}")
    assert response.status_code == 204

    # 다시 조회하면 404
    response = client.get(f"/quotes/{qid}")
    assert response.status_code == 404
```

실행:

```bash
uv run pytest -v
```

```
tests/test_quotes.py::test_root PASSED
tests/test_quotes.py::test_create_and_list_quote PASSED
tests/test_quotes.py::test_get_quote_not_found PASSED
tests/test_quotes.py::test_create_validation_error_empty_text PASSED
tests/test_quotes.py::test_patch_partial_update PASSED
tests/test_quotes.py::test_delete_then_404 PASSED
```

### 5.18.9 실습 체크리스트

- [ ] `POST /quotes/`로 명언을 만들고 201을 받는다.
- [ ] `GET /quotes/`로 목록을 받는다(`limit`, `offset` 동작).
- [ ] `GET /quotes/{id}`로 단건을 받고, 없으면 404가 온다.
- [ ] `PUT /quotes/{id}`로 전체를 덮어쓴다.
- [ ] `PATCH /quotes/{id}`로 일부만 바꾼다(보낸 필드만 갱신).
- [ ] `DELETE /quotes/{id}`로 지운 뒤 다시 조회하면 404다.
- [ ] 빈 텍스트나 너무 긴 저자명은 422가 온다.
- [ ] `/docs`에서 모든 엔드포인트가 `quotes` 태그로 묶여 보인다.
- [ ] `uv run pytest`가 모두 초록색이다.

---

## 5.19 트러블슈팅 — 자주 발생하는 문제

### 5.19.1 `ImportError: attempted relative import with no known parent package`

테스트나 실행을 잘못된 디렉터리에서 돌렸을 때 흔합니다. **프로젝트 루트(여러분 폴더)에서** 다음과 같이 실행하세요.

```bash
uv run uvicorn app.main:app --reload   # ← app/main.py의 app 객체
uv run pytest
```

`app:app`이 아니라 `app.main:app`입니다. 앞은 모듈 경로(`app/main.py`), 뒤는 그 모듈 안의 변수 이름.

### 5.19.2 `RuntimeError: Form data requires "python-multipart"`

폼이나 파일을 받는 코드를 추가했는데 라이브러리가 없을 때 뜹니다.

```bash
uv add python-multipart
```

### 5.19.3 `EmailStr` 사용 시 `ImportError`

`pydantic[email]` 옵션이 안 깔린 상태입니다.

```bash
uv add "pydantic[email]"
```

### 5.19.4 `/docs`가 404

`app = FastAPI(...)` 자체가 만들어지지 않았거나(import 에러), `--root-path` 같은 배포 설정이 잘못된 경우입니다. 개발 단계에서는 거의 100% **import 에러**입니다 — 콘솔의 트레이스백을 확인하세요.

### 5.19.5 응답이 `null`이거나 비어 있음

함수가 `return` 없이 끝나서 `None`이 응답되는 경우가 흔합니다. 응답 모델을 둔 엔드포인트에서는 반드시 모델에 맞는 객체나 dict를 `return`해야 합니다.

### 5.19.6 같은 라우트가 두 번 등록됨

`include_router`를 두 번 호출했거나, `app.py`와 `app/main.py` 둘 다 같은 라우터를 import하고 있을 수 있습니다. 라우터는 **한 곳에서만** include하세요.

### 5.19.7 422 에러 본문이 클라이언트에 너무 자세함

검증 실패의 상세 정보(`loc`, `type` 등)가 운영 환경에서 너무 많은 내부 정보를 흘릴까 걱정된다면 `RequestValidationError`를 잡아 응답을 다듬을 수 있습니다(고급). 학습 단계에서는 기본 응답이 가장 친절합니다.

### 5.19.8 PATCH인데 보내지 않은 필드가 `null`로 덮였다

`payload.model_dump()`만 호출하면 보내지 않은 필드도 기본값(`None`)으로 들어와 덮어씁니다. **`exclude_unset=True`** 를 꼭 함께 쓰세요(5.18.4 참고).

### 5.19.9 `--reload`가 코드 변경을 반영하지 않음

가상환경 안에 `watchfiles`가 없을 때(`uvicorn`만 깔고 `uvicorn[standard]`로 안 깔았을 때) 발생할 수 있습니다.

```bash
uv add "uvicorn[standard]"
```

### 5.19.10 라우트가 `404`인데 분명 만든 것 같음

- 데코레이터의 경로 문자열에 오타(`/qoutes/`)가 있는지
- 마지막 슬래시 — `/quotes`와 `/quotes/`가 다르게 동작할 수 있음. `APIRouter(prefix="/quotes")` + `@router.get("/")` 조합은 **`/quotes/`** 가 됩니다(슬래시 끝). `/quotes`(슬래시 없음)에 GET을 보내면 FastAPI가 자동으로 307 redirect를 시도하거나 404를 줄 수 있어요.

> **슬래시 끝 정책**: 본 가이드의 컨벤션은 라우터의 root는 `"/"`(끝 슬래시 있음), 단건 엔드포인트는 `"/{id}"`(끝 슬래시 없음)입니다. 클라이언트는 정확히 그 모양으로 호출합니다.

---

## 5.20 이 챕터 요약

- **라우팅**: `@app.get/post/put/patch/delete("/path")`. 같은 경로의 메서드별 등록은 별개의 라우트.
- **경로 매개변수**: `/users/{user_id}` + `def get_user(user_id: int)`. **타입 힌트가 곧 검증·변환.**
- **쿼리 매개변수**: 함수 인자에 기본값을 주면 선택값, 안 주면 필수. `Query(...)`로 추가 검증.
- **본문**: Pydantic `BaseModel`을 인자 타입으로 받으면 JSON 본문이 자동 디코딩·검증.
- **응답**: `response_model=...`(또는 함수 반환 타입 어노테이션)으로 검증·문서화·필터링이 한 번에.
- **상태 코드**: `status_code=...`. `responses=`로 다른 가능 응답을 문서에 표시.
- **에러**: 도메인 에러는 `raise HTTPException(status_code, detail)`. 일반 예외는 500이 되므로 그렇게 두지 않는다.
- **APIRouter**: 도메인별로 모듈을 쪼개고 `app.include_router(router)`로 합친다.
- **헤더·쿠키**: `Header`, `Cookie`로 받는다. 응답 헤더는 `Response`에 직접 적는다.
- **폼·파일**: `Form`, `File`, `UploadFile`. REST API에서는 자주 쓰지 않음(개념만 알기).
- **`Depends`**: 공통 입력·전처리를 함수로 떼어 인자로 받는 패턴. 본격은 08장.
- **자동 문서**: `/docs`(Swagger UI), `/redoc`(ReDoc). 서버를 띄우자마자 무료로 따라온다.
- **테스트**: `from fastapi.testclient import TestClient` + pytest. 서버를 띄우지 않고 바로 호출.
- **흔한 실수**: 경로 인자 이름 불일치, 더 구체적인 라우트를 아래 둠, `Content-Type` 누락, PATCH에서 `exclude_unset=True` 빼먹음.

다음 챕터(06)에서 이 메모리 저장소를 **SQLAlchemy + SQLite/MySQL/PostgreSQL**로 옮깁니다. 라우트와 Pydantic 모델은 거의 그대로 둔 채, 안쪽만 DB 호출로 바꾸게 됩니다 — 이번 챕터에서 잘 분리해 둔 보람이 그때 나타납니다.

---

← [04. 첫 프로젝트](04-first-project.md) | 다음 문서로 이동: **[06. SQLAlchemy 2.0과 데이터베이스 연동 →](06-sqlalchemy-database.md)**
