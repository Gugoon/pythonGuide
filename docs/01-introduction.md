# 01. FastAPI 소개 — Python 개발자를 위한 안내

> **이 챕터의 목표**
> - FastAPI가 무엇인지, 어떤 위치의 프레임워크인지 이해한다.
> - Python 문법 지식이 어떻게 FastAPI 백엔드 개발로 그대로 이어지는지 파악한다.
> - 왜 Python으로 백엔드를 만드는가에 대한 관점을 잡는다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

---

## 1.1 FastAPI란 무엇인가

**FastAPI**는 Python 언어로 작성된 **오픈소스 비동기 웹 프레임워크**입니다. 간단히 말해, Python으로 HTTP 서버, REST API, 웹 애플리케이션 백엔드를 만들 수 있게 해주는 도구입니다.

> **프레임워크(framework)**: 어떤 종류의 프로그램을 만들 때 자주 쓰는 코드 패턴(서버 시작, 요청 받기, 응답 보내기 등)을 미리 만들어 둔 "뼈대" 같은 도구 모음입니다. 우리는 그 뼈대 위에 우리만의 살(=비즈니스 로직)을 붙이기만 하면 됩니다.

- 공식 사이트: https://fastapi.tiangolo.com/
- GitHub: https://github.com/fastapi/fastapi
- 최초 공개: 2018년 12월 (Sebastián Ramírez)
- 현재 사용 중인 안정 버전: 0.x 계열 (집필 시점 0.115.x 이상)
- 라이선스: MIT

FastAPI의 위치를 다른 언어의 프레임워크와 대응시키면 아래와 같습니다. 옆에 적힌 도구들을 모를 수 있는데 괜찮습니다 — "다른 언어에도 비슷한 게 있다는 거구나" 정도만 받아들이면 됩니다.

| 언어 / 런타임 | 대표 프레임워크 | FastAPI와의 유사점 |
|---------------|-----------------|--------------------|
| JavaScript / Node.js | Express, Hono, Fastify | 경량, 라우팅 중심, 미들웨어 구조 |
| Ruby | Sinatra | 블록 기반 DSL 스타일 라우트 선언 |
| Go | Echo, Gin, Fiber | 고성능 HTTP 서버, 간결한 문법 |
| Java/Kotlin | Spring Boot, Ktor | 의존성 주입, 자동 검증 |
| Python (다른 선택지) | Django, Flask, Litestar | 같은 생태계, 다른 철학 |

"Node.js의 Express에 자동 데이터 검증과 자동 API 문서를 더한 것에 가깝다"는 직관이 비교적 잘 들어맞습니다. 다만 FastAPI는 Express보다 타입 검증이 훨씬 더 강력하고, Spring Boot보다는 훨씬 가볍습니다.

## 1.2 FastAPI가 제공하는 것 (범위)

FastAPI 본체와, 함께 자주 쓰이는 기본 라이브러리 묶음으로 다음이 모두 가능합니다.

- **HTTP 서버**: Starlette + Uvicorn 기반의 비동기 논블로킹 서버
- **라우팅**: `@app.get("/path")` 식의 데코레이터 기반 선언적 라우팅
- **요청/응답 처리**: JSON, form-data, 쿼리 파라미터를 Python 타입으로 자동 변환
- **데이터 검증**: **Pydantic**으로 요청·응답 스키마 자동 검증 (틀린 타입의 데이터가 들어오면 자동으로 422 에러)
- **자동 API 문서**: 코드만 작성하면 Swagger UI(`/docs`)와 ReDoc(`/redoc`)이 자동 생성됨 — **FastAPI의 가장 큰 차별점**
- **의존성 주입**: 인증·DB 세션·설정 등을 함수 인자로 주입받는 깔끔한 구조
- **미들웨어 시스템**: 인증, 로깅, CORS, 에러 핸들링 등 파이프라인
- **인증 도우미**: OAuth2, Bearer 토큰, API 키 등 표준 패턴을 한 줄로 선언
- **WebSocket**: 실시간 통신 지원 (이 가이드의 범위 밖)
- **백그라운드 작업**: 응답을 보낸 뒤 가벼운 후속 작업 실행
- **테스팅 유틸리티**: `TestClient` 한 줄로 통합 테스트 작성

데이터베이스(ORM), JWT 토큰 발급, 비밀번호 해싱은 FastAPI 본체에 포함되지는 않지만, **이 가이드에서 사용하는 라이브러리(SQLAlchemy 2.0, PyJWT, bcrypt)와의 통합이 매우 자연스럽습니다.** 각 챕터에서 함께 익혀나갑니다.

> **REST API란?** "REST"는 Representational State Transfer의 약자로, 웹에서 데이터를 주고받는 가장 흔한 약속 방식입니다. URL로 자원을 가리키고(예: `/users/42`), HTTP 메서드(GET·POST·PUT·DELETE)로 동작을 표현하며, 데이터는 보통 JSON으로 주고받습니다. 자세한 내용은 02장에서 다룹니다.

> **HTTP 메서드란?** "이 요청이 무엇을 하려는지" 알려주는 동사입니다. **GET**(자료 가져오기), **POST**(자료 새로 만들기), **PUT/PATCH**(자료 수정하기), **DELETE**(자료 지우기) 다섯 가지를 가장 자주 씁니다. 예를 들어 `GET /users/42`는 "42번 사용자 정보를 보여달라", `DELETE /users/42`는 "42번 사용자를 지워달라"가 됩니다.

> **JSON이란?** 데이터를 글자로 표현하는 가장 흔한 형식입니다. 파이썬의 `dict`와 거의 같은 모양입니다: `{"id": 42, "name": "Alice"}`. 백엔드와 프론트엔드는 이 JSON을 주고받습니다.

> **HTTP 상태 코드란?** 응답이 어떻게 됐는지 알려주는 세 자리 숫자입니다. **200**(잘 됐음), **201**(새로 만들어짐), **400**(요청이 잘못됨), **401**(로그인 필요), **404**(없음), **422**(검증 실패), **500**(서버 에러) 정도가 가장 자주 등장합니다.

## 1.3 왜 Python 입문자에게 FastAPI가 유리한가

### 1.3.1 익숙한 Python 문법, 익숙한 도구

Python에서 쓰던 것을 그대로 씁니다.

- **언어**: Python 3.13 (이미 알고 있는 그것)
- **에디터**: VS Code, PyCharm — 평소 쓰던 도구 그대로
- **패키지 매니저**: `uv` (또는 `pip`)
- **실행**: `uvicorn app.main:app --reload` 한 줄

`Node.js`, `npm`, `gradle`, Maven 같은 새로운 도구를 배울 필요가 없습니다. `pyproject.toml` 또는 `requirements.txt` 하나로 모든 의존성이 관리됩니다.

### 1.3.2 타입 힌트가 그대로 통한다

Python 3.5부터 표준화된 **타입 힌트**(PEP 484, `def add(x: int, y: int) -> int:`)를 평소에 사용해 왔다면, FastAPI에서는 그 타입 힌트가 **자동 검증·자동 변환·자동 문서화**로 곧장 이어집니다(함수 어노테이션 문법 자체는 PEP 3107 로 Python 3.0 부터 존재했지만, `typing` 모듈로 표준화된 것은 3.5 입니다).

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    email: str
    name: str

@app.post("/users")
async def create_user(user: User) -> User:
    # user는 이미 검증된 User 인스턴스
    # 클라이언트가 잘못된 타입(예: id에 문자열)을 보내면 자동으로 422 에러
    return user
```

이 짧은 코드만으로 FastAPI는:
1. 들어오는 JSON을 파이썬의 `User` 객체로 자동 변환
2. 타입이 안 맞으면 자동으로 422 에러 + 오류 위치 표시
3. `/docs` 페이지에 이 엔드포인트 사양을 자동 등록

타입 힌트를 안 써본 분도 걱정하지 마세요. 05장에서 처음부터 자세히 다룹니다.

### 1.3.3 async/await가 일급 시민

FastAPI는 Python의 비동기(async/await) 문법을 자연스럽게 지원합니다.

> **비동기(async/await)**: 한 가지 일이 끝나기를 기다리는 동안 다른 일을 처리할 수 있게 하는 문법입니다. 백엔드는 "DB에서 자료 꺼내기", "외부 API 호출" 같은 기다림이 많아서, 비동기를 쓰면 한 서버가 동시에 훨씬 많은 요청을 처리할 수 있습니다.

```python
# 핵심만 발췌한 의사코드 — 실제 코드에서는 `db` 도 의존성 주입을 거쳐 받습니다.
# (예: `db: AsyncSession = Depends(get_db)`. 06장에서 다룹니다.)
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

비동기를 처음 본다고 해도 괜찮습니다. **FastAPI는 일반(`def`) 함수도 그대로 받아들입니다.** 입문 단계에서는 동기 함수로 시작하고, 익숙해지면 점진적으로 `async def`로 바꿔도 됩니다.

### 1.3.4 자동 생성되는 API 문서 — FastAPI 최대 강점

FastAPI 앱을 띄우면, **아무 추가 설정 없이** 다음 두 페이지가 자동으로 만들어집니다.

- `http://localhost:8000/docs` — Swagger UI (인터랙티브 API 테스트 페이지)
- `http://localhost:8000/redoc` — ReDoc (읽기 좋은 API 문서)

각 엔드포인트의 입력 타입, 출력 타입, 가능한 에러 코드, 예시 데이터가 모두 자동으로 표시됩니다. 클라이언트 개발자(프론트엔드, 모바일)에게 별도 문서를 작성해 줄 필요가 없어, **혼자 또는 작은 팀에서 일하는 백엔드 개발자에게 엄청난 시간 절약**이 됩니다.

다른 프레임워크에서는 이 기능을 얻으려면 별도의 라이브러리(Django의 `drf-spectacular`, Express의 `swagger-jsdoc` 등)를 추가하고 직접 설정해야 합니다.

### 1.3.5 Starlette/Uvicorn 기반의 고성능

FastAPI는 내부적으로 **Starlette**(가벼운 ASGI 프레임워크)와 **Uvicorn**(고속 ASGI 서버) 위에 구축되어 있습니다.

> **ASGI(Asynchronous Server Gateway Interface)**: 비동기 Python 웹 앱과 서버 사이의 표준 약속입니다. 옛날 Django/Flask가 쓰던 WSGI의 비동기 버전이라고 생각하면 됩니다.

이 덕분에 FastAPI는 Python 웹 프레임워크 중에서도 가장 빠른 축에 속합니다. TechEmpower 같은 벤치마크에서 Node.js·Go와 비교해도 큰 차이가 나지 않을 만큼 효율적입니다(완벽하게 같지는 않지만, 대부분의 실무 트래픽에서는 충분합니다).

## 1.4 왜 Python 백엔드인가 — 현실적인 관점

### 1.4.1 장점

1. **러닝 커브가 가장 완만한 언어 중 하나**: 같은 분량의 백엔드 기능을 가르칠 때, Python이 Java/Kotlin/Go보다 빠르게 익힐 수 있다는 점은 거의 모든 비교에서 일치합니다.
2. **압도적인 라이브러리 생태계**: 거의 모든 외부 서비스(AWS, Stripe, 카카오·네이버 API 등)가 Python SDK를 1순위로 제공합니다.
3. **데이터·머신러닝과의 결합**: 백엔드 안에서 numpy, pandas, scikit-learn, PyTorch를 그대로 가져다 씁니다. AI 기능을 곁들인 서비스를 만들기에 가장 자연스럽습니다.
4. **인력 시장**: Python 백엔드 채용 수요가 매우 큽니다. (특히 스타트업, AI 관련 회사)
5. **빠른 프로토타이핑**: 같은 기능을 1/3~1/2 분량의 코드로 만듭니다.

### 1.4.2 단점과 현실

정직하게 말하자면 Python 백엔드에도 한계가 있습니다.

- **순수 계산 성능은 컴파일 언어(Go, Rust, Java)보다 느립니다.** 다만 백엔드 작업 대부분이 "DB 호출/외부 API 호출 대기"라서 실무에서는 큰 문제가 안 되는 경우가 많습니다.
- **GIL(Global Interpreter Lock)**: Python의 한 프로세스 안에서 진짜 병렬로 CPU를 쓰는 데 제약이 있습니다. 대신 비동기(async)나 여러 프로세스 띄우기로 해결합니다.
- **타입 시스템이 컴파일 타임에 강제되지 않음**: 타입 힌트는 어디까지나 "안내"이며, 런타임에 강제로 검사하지 않습니다(우리는 Pydantic으로 이 부분을 메꿉니다).
- **버전 호환성 이슈**: 옛날 라이브러리 일부는 최신 Python을 따라가지 못합니다. 새 프로젝트는 가능하면 Python 3.13 이상 권장.

### 1.4.3 그럼에도 FastAPI를 쓰는 실용적 이유

- **혼자 / 소규모 팀**: 한 사람이 백엔드 + 데이터 작업 + 약간의 ML까지 할 때 언어가 하나로 통일됨
- **빠른 검증(MVP)**: 1~2주 안에 동작하는 서비스를 만들어야 하는 상황
- **데이터·AI 통합 서비스**: ChatGPT API, 추천 시스템, 이미지 분석 등을 백엔드 안에서 직접 호출
- **학습 목적**: 백엔드 개념을 가장 친숙한 언어(Python)로 빠르게 익히고, 이후 다른 언어로 확장
- **레거시 Django/Flask에서 갈아타기**: 같은 Python 안에서 더 빠른 성능과 자동 검증을 얻고 싶을 때

즉, **"빠르게 배우고 빠르게 만들면서, 데이터·AI와의 결합 가능성을 열어두고 싶은 시나리오"**에서 FastAPI의 가치가 가장 큽니다.

## 1.5 FastAPI의 핵심 구성 요소

FastAPI 애플리케이션은 다음 요소들로 이루어집니다. 이 가이드에서 하나씩 자세히 다루지만, 미리 한눈에 보고 가겠습니다. 지금은 이름만 익혀두세요.

### 1.5.1 FastAPI 인스턴스(`app`)

전체 애플리케이션의 루트 객체입니다.

```python
from fastapi import FastAPI
app = FastAPI()
```

이 `app` 위에 라우트, 미들웨어, 의존성 등을 등록합니다.

### 1.5.2 Path Operations (라우트)

URL 경로와 HTTP 메서드를 함수에 매핑합니다. **데코레이터**로 선언합니다.

> **데코레이터(decorator)란?** 함수 바로 위에 `@`로 붙는 표시입니다. "이 함수에 추가 기능을 입혀라"는 의미입니다. 우리가 직접 데코레이터를 만들 일은 거의 없고, 이미 만들어진 데코레이터(여기서는 `@app.get`)를 갖다 쓰기만 합니다.

```python
@app.get("/hello")          # ← 데코레이터: "이 함수를 GET /hello 처리기로 등록"
def hello():
    return {"message": "Hello!"}

@app.post("/users")
def create_user(...): ...
```

### 1.5.3 Request / Response

들어오는 HTTP 요청과 나가는 응답을 표현하는 객체입니다. 대부분의 경우 FastAPI가 알아서 처리하므로 직접 다룰 일이 적지만, 헤더·쿠키 등을 만질 때는 `Request` 객체를 함수 인자로 받을 수 있습니다.

### 1.5.4 Pydantic 모델

요청·응답의 데이터 형태(스키마)를 선언하는 클래스입니다. **다른 언어 프레임워크에서 직접 만들어야 했던 "데이터 검증 + 직렬화 + 문서화"를 한 번에 처리합니다.**

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str
```

### 1.5.5 Dependencies (의존성 주입)

인증된 사용자, DB 세션, 설정값 등 "함수가 동작하기 위해 필요한 것"을 함수의 인자로 자동 주입받는 구조입니다. FastAPI의 가장 강력한 기능 중 하나입니다.

> **의존성 주입(Dependency Injection, DI)이란?** "이 함수가 돌아가려면 사용자 정보가 필요해"라고 인자로만 선언해 두면, FastAPI가 알아서 그 값을 만들어 넣어주는 패턴입니다. 우리는 어떻게 만들어지는지 신경 쓰지 않고 받기만 하면 됩니다. `Depends(get_current_user)`는 "여기 들어갈 값은 `get_current_user` 함수가 만들어 줘"라는 뜻입니다.

```python
@app.get("/me")
def me(current_user: User = Depends(get_current_user)):
    # current_user는 FastAPI가 알아서 만들어 넣어 준다
    return current_user
```

자세한 내용은 08장(인증)에서 본격적으로 다룹니다.

### 1.5.6 Middleware

요청과 응답 사이에 개입하는 코드 블록입니다. 로깅, CORS 헤더 삽입, 응답 시간 측정 등이 미들웨어로 구현됩니다.

> **미들웨어(middleware)란?** 요청이 우리 함수에 도달하기 전·우리 함수가 응답을 돌려준 후에 한 번씩 끼어드는 "검문소" 같은 코드입니다. 예: "모든 요청에 대해 처리 시간을 로그에 남겨라", "응답에 CORS 헤더를 자동으로 붙여라" 같은 횡단 기능을 한 곳에 모아둡니다.

### 1.5.7 SQLAlchemy ORM

DB 테이블을 Python 클래스로 매핑합니다. SQL을 직접 쓰지 않고도 타입 안전하게 쿼리를 작성합니다.

> **ORM(Object Relational Mapper)**: 데이터베이스의 표(테이블)와 Python 객체(클래스)를 자동으로 연결해 주는 도구입니다. `SELECT * FROM users WHERE id = 1` 같은 SQL 대신 `await session.get(User, 1)` 같은 파이썬 코드로 데이터베이스를 다룰 수 있습니다. 06장에서 본격적으로 다룹니다.

### 1.5.8 APIRouter

여러 라우트를 모은 모듈입니다. 큰 앱에서는 `users.py`, `posts.py` 식으로 도메인별로 나눕니다.

```python
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users(): ...
```

### 1.5.9 Service Layer

비즈니스 로직을 담는 계층입니다. FastAPI가 강제하지 않지만, 규모가 커지면 `services/user_service.py`처럼 분리하는 게 관례입니다. 10·11장 종합 예제에서 도입합니다.

## 1.6 FastAPI 0.x — 버전 표기에 대한 안내

집필 시점(2026년 4월) FastAPI의 최신 안정 버전은 **0.115.x 이상**입니다(이후로도 마이너 버전은 꾸준히 올라갑니다 — 2026년 6월 기준 0.13x대. `uv`가 lock·`>=` 제약 안에서 늘 호환되는 최신을 받으므로 정확한 숫자를 외울 필요는 없습니다). "0.x"라고 하니 미완성 같지만, 실제로는 다음과 같습니다.

- FastAPI는 [SemVer 약속](https://semver.org/lang/ko/)을 따르되, 1.0 출시를 매우 보수적으로 미루고 있습니다.
- 2024년 하반기 0.115 라인 이후 사실상 안정 단계에 진입했고, **수많은 회사가 운영 환경에서 그대로 쓰고 있습니다.**
- 마이너 버전 사이의 호환성은 잘 지켜집니다. 0.110 → 0.115 사이에 작은 변경은 있어도 큰 코드 재작성은 필요 없습니다.

**이 가이드는 FastAPI 0.115.x 이상을 기준으로 작성되었습니다.** 향후 1.0 또는 그 이상으로 올라가도 본 가이드의 핵심 코드 대부분이 그대로 동작할 것으로 예상합니다(이주가 필요한 경우, FastAPI 공식 마이그레이션 가이드를 참고).

## 1.7 다른 백엔드 프레임워크와의 비교

### 1.7.1 FastAPI vs Django + DRF (Python)

| 항목 | FastAPI | Django + DRF |
|------|---------|--------------|
| 무게감 | 경량, REST API 특화 | 풀스택(Admin/ORM/Auth 내장) |
| 학습 곡선 | 완만 | 상대적으로 가파름 |
| 비동기 | 처음부터 async 일급 | 부분적 async (점진 도입 중) |
| 자동 API 문서 | 기본 제공 | 별도 라이브러리(`drf-spectacular`) |
| ORM | 별도(SQLAlchemy 권장) | Django ORM 내장 |
| 어드민 페이지 | 없음 | 강력한 자동 어드민 |

**언제 FastAPI가 유리한가**: REST API만 깔끔하게 만들고 싶을 때, 자동 문서화가 필요할 때.
**언제 Django + DRF가 유리한가**: 콘텐츠 관리·어드민 화면이 핵심인 서비스(블로그, 쇼핑몰 백오피스 등).

### 1.7.2 FastAPI vs Flask (Python)

| 항목 | FastAPI | Flask |
|------|---------|-------|
| 첫 등장 | 2018 | 2010 |
| 데이터 검증 | 자동(Pydantic) | 수동(또는 marshmallow 등 별도) |
| 비동기 | 일급 시민 | 2.x부터 부분 지원 |
| 자동 API 문서 | 기본 제공 | 별도 설치 |
| 타입 힌트 | 핵심에 통합 | 보조 |
| 성능 | 더 빠름 | 충분히 빠름 |

**언제 FastAPI가 유리한가**: 거의 모든 새 프로젝트.
**언제 Flask가 유리한가**: 단순 동기 스크립트 수준의 미니멀 서비스, 또는 기존 Flask 코드베이스 유지·보수.

### 1.7.3 FastAPI vs Express (Node.js)

| 항목 | FastAPI | Express |
|------|---------|---------|
| 언어 | Python | JavaScript / TypeScript |
| 타입 검증 | Pydantic 자동 | 기본 동적, 별도 라이브러리(zod 등) |
| 비동기 모델 | async/await (asyncio) | async/await (libuv) |
| 자동 API 문서 | 기본 제공 | 별도 설치 |
| 생태계 크기 | 큼 | 매우 큼 |

**언제 FastAPI가 유리한가**: 같은 코드베이스에서 데이터·ML과 결합할 때, 타입 검증이 강하게 필요할 때.
**언제 Express가 유리한가**: 프론트엔드와 같은 언어(JS/TS) 통일을 원할 때.

### 1.7.4 FastAPI vs Spring Boot (Java/Kotlin)

| 항목 | FastAPI | Spring Boot |
|------|---------|-------------|
| 무게감 | 경량 | 대형 프레임워크 |
| 런타임 | CPython | JVM |
| 시작 시간 | 1~2초 | 수~수십 초 |
| 메모리 사용량 | 낮음 | 높음 |
| 러닝 커브 | 완만 | 가파름 |

**언제 FastAPI가 유리한가**: 빠른 시작·저메모리·작은 팀.
**언제 Spring Boot가 유리한가**: 대규모 엔터프라이즈, 이미 JVM 인프라를 가진 조직.

## 1.8 이 가이드의 구성과 학습 흐름

앞으로 다음 순서로 배웁니다.

1. **개념**: 백엔드 기본 용어(02) — 용어의 혼란을 제거합니다.
2. **환경 구축**: 설치(03) → 첫 프로젝트(04) — 실제로 동작하는 서버를 띄워봅니다.
3. **FastAPI 핵심**: 라우팅과 Pydantic(05) → SQLAlchemy/DB(06) → CRUD(07) → 인증(08) — 각 기능을 독립 실습으로 익힙니다.
4. **운영**: 배포(09) — 실제 서버에 올립니다.
5. **종합**: Note API(10), Blog API(11) — 앞서 배운 것을 조합해 **전체 프로젝트를 처음부터** 만들어봅니다.

각 챕터에는 다음이 포함됩니다.

- **개념 설명**: 용어·원리
- **최소 예제 코드**: 해당 개념만 보여주는 짧은 스니펫
- **실습 예제**: 직접 타이핑해서 돌려볼 수 있는 코드 (`examples/` 폴더에 완성본 제공)
- **설명 주석**: 코드 안에 한국어 주석으로 이유 설명
- **참고 링크**: 공식 문서 등 1차 자료

## 1.9 전제 지식과 준비물

### 1.9.1 알고 있어야 하는 것

- **Python 3 기초**: 변수, 함수, 클래스, `if`/`for`/`while`, 예외 처리(`try/except`), 모듈 임포트
- **타입 힌트**: `def add(x: int) -> int:` 정도의 표기를 본 적 있으면 충분 (없어도 05장에서 다시 설명)
- **터미널 사용 경험**: `cd`, `ls`, 명령어 실행 정도

### 1.9.2 몰라도 괜찮은 것 (이 가이드에서 설명)

- HTTP 메서드, 상태 코드 (02장)
- REST / RESTful (02장)
- DB / ORM / 마이그레이션 (06장)
- JWT / Bcrypt / 세션 (08장)
- Docker / 컨테이너 / 배포 (09장)
- Pydantic, SQLAlchemy, Alembic 사용법 (각 챕터)

### 1.9.3 준비물

- **하드웨어**: macOS / Linux / Windows 어디든 가능 (Python이 모든 OS에서 동작)
- **운영체제 권장**: macOS 또는 Linux. Windows에서는 가능하면 [WSL2](https://learn.microsoft.com/ko-kr/windows/wsl/install)(Ubuntu)를 통해 작업하시길 권장합니다 — 배포 환경(Docker, 서버)이 거의 다 Linux이기 때문에 처음부터 같은 환경에서 익히는 것이 편합니다.
- **소프트웨어**:
  - Python 3.13 이상 (03장에서 설치 안내)
  - 터미널 (macOS의 Terminal, Ubuntu의 GNOME Terminal, Windows의 WSL2 셸)
  - 코드 에디터: [VS Code](https://code.visualstudio.com/) 권장. PyCharm Community도 가능
- **선택 도구** (사용할 때 챕터에서 안내):
  - API 테스트: 브라우저의 자동 `/docs` 페이지로 충분. 더 본격적으로는 [Bruno](https://www.usebruno.com/), [Postman](https://www.postman.com/), 또는 `curl`/`httpie`
  - DB 관리: [DBeaver](https://dbeaver.io/), [TablePlus](https://tableplus.com/)
  - Docker Desktop (배포 챕터에서 사용)

## 1.10 자주 묻는 질문

**Q. FastAPI로 만든 실제 서비스가 있나요?**
네. Microsoft, Uber, Netflix 등 대형 기업의 일부 내부 서비스에서 FastAPI 가 사용된다는 외부 공개 사례가 있습니다(예: Netflix 의 오픈소스 Dispatch — 공개 저장소·블로그로 검증). [FastAPI 공식 사이트 추천사 섹션](https://fastapi.tiangolo.com/#opinions)에서도 여러 엔지니어의 사용기를 볼 수 있습니다(다만 이 섹션은 회사 사례 모음이 아닌 개인 추천사입니다). 한국에서도 다수의 스타트업과 ML/데이터 회사가 백엔드의 1순위로 FastAPI를 채택하고 있습니다.

**Q. Python을 모르는데 이 가이드를 따라갈 수 있나요?**
권장하지 않습니다. 먼저 [Python 공식 튜토리얼(한국어)](https://docs.python.org/ko/3/tutorial/)의 1~9장 정도를 마치고 오시길 권합니다. 함수·클래스·예외처리만 익혀두면 충분합니다.

**Q. macOS가 없어도 되나요?**
괜찮습니다. FastAPI는 OS를 가리지 않습니다. 다만 배포 환경이 거의 다 Linux이므로, Windows 사용자는 WSL2(Ubuntu)에서 작업하는 것을 권장합니다.

**Q. Django/Flask를 이미 알고 있다면 따라가기 쉬운가요?**
네. 핵심 개념(라우팅, ORM, 미들웨어)이 비슷해 적응이 빠릅니다. 다만 FastAPI는 **타입 힌트를 적극적으로 쓰므로**, 타입 힌트와 Pydantic의 사고방식에 익숙해지는 데 약간의 시간이 듭니다.

**Q. 비동기(async/await)를 모르는데 따라갈 수 있나요?**
괜찮습니다. 이 가이드는 비동기 코드를 처음부터 자연스럽게 등장시키되, 비동기 자체에 대한 깊은 이해 없이도 따라갈 수 있도록 구성했습니다. 06장에서 비동기 DB 호출을 다룰 때 짧게 정리합니다.

**Q. 학습에 얼마나 걸리나요?**
하루 2~3시간 투자 기준, 01~09장 기초 학습은 2~3주, 종합 예제(10, 11장)까지 포함하면 약 4~5주 정도가 현실적인 페이스입니다. 이미 Python에 익숙한 분이라면 더 빠르게 갈 수 있습니다.

**Q. Python 3.12 또는 그 이전 버전에서도 됩니까?**
대부분 동작하지만, 이 가이드는 3.13 기준입니다. 가능하면 3.13 이상을 사용하시길 권장합니다(03장 설치 가이드 참고).

## 1.11 이 챕터 요약

- FastAPI는 Python으로 백엔드를 만드는 경량·고성능 비동기 프레임워크다.
- Python의 타입 힌트가 자동 검증·자동 변환·자동 API 문서로 그대로 이어진다.
- 가장 큰 차별점은 **무료로 따라오는 자동 API 문서(`/docs`, `/redoc`)** 와 **Pydantic 기반의 강력한 데이터 검증**이다.
- 장점은 학습 비용이 낮고 데이터·AI와 결합하기 좋다는 점. 단점은 순수 계산 성능과 GIL.
- 집필 시점 기준 FastAPI 0.115.x가 사실상 안정 버전이며, 이 가이드는 그 기준으로 작성되었다.
- 다음 챕터에서 백엔드의 기본 용어를 정리한 뒤, 환경 구축으로 넘어간다.

---

← [README로 돌아가기](../README.md) | 다음 문서로 이동: **[02. 백엔드 기본 용어 정리 →](02-backend-basics.md)**
