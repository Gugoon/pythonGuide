---
title: "FastAPI 한국어 가이드 — Python 입문자를 위한 비동기 웹 백엔드"
author: "FastAPI 한국어 가이드"
date: "2026-04-26"
lang: ko
---

# FastAPI 한국어 가이드

**Python 입문자를 위한 비동기 웹 프레임워크 FastAPI 완벽 가이드**

- **대상 독자**: Python 기본 문법(함수·클래스·타입 힌트)에 익숙하고, 백엔드는 처음인 분
- **학습 방식**: 이론 → 개별 요소 실습 → 종합 프로젝트 2개
- **집필 기준**: 2026년 4월 시점의 최신 공식 문서 (Python 3.13, FastAPI 0.115.x 이상)

## 사용 기술 스택 (2026-04 기준)

| 구성요소 | 사용 버전 |
|----------|-----------|
| Python | 3.13 이상 |
| FastAPI | 0.115.x 이상 |
| Pydantic | 2.x |
| SQLAlchemy | 2.0.x (`[asyncio]` extras) |
| Alembic | 1.13.x 이상 |
| DB 드라이버 | `aiosqlite` / `asyncmy` / `asyncpg` |
| PyJWT | 2.8.x 이상 |
| bcrypt | 4.x (직접 사용) |
| Uvicorn | 0.30.x 이상 |
| Gunicorn | 23.x (운영) |
| uv | 0.4.x 이상 |

## 학습 목표

- 백엔드 핵심 개념 이해 (HTTP, REST, DB, 인증, 배포)
- FastAPI 프로젝트 처음부터 구성
- SQLAlchemy 2.0(async) 으로 SQLite·MySQL·PostgreSQL 어디든
- JWT 회원가입·로그인·인증 흐름
- Docker / Render / Fly.io / AWS / Ubuntu 배포
- Note API · Blog API 종합 프로젝트 완성

> 이 가이드는 7개의 실 검증을 거친 예제 프로젝트(`examples/`)와 모든 핵심 흐름의 회귀 테스트를 포함합니다.

# 목차

## 1부. 기초

- [1장. FastAPI 소개](#ch01)
- [2장. 백엔드 기본 용어 정리](#ch02)
- [3장. 설치 가이드 (macOS / Linux)](#ch03)
- [4장. 첫 프로젝트 — Hello FastAPI](#ch04)

## 2부. 실습 요소

- [5장. 라우팅과 Pydantic (JSON 요청/응답)](#ch05)
- [6장. SQLAlchemy 2.0과 데이터베이스 연동](#ch06)
- [7장. CRUD 예제 — Todo API](#ch07)
- [8장. 사용자 인증 — JWT와 Bcrypt](#ch08)

## 3부. 배포

- [9장. 배포 가이드 — Docker, Render/Fly.io, AWS, Ubuntu](#ch09)

## 4부. 종합 예제

- [10장. 종합 예제 1 — Note API](#ch10)
- [11장. 종합 예제 2 — Blog API](#ch11)

## 5부. 레퍼런스

- [12장. 유틸리티 및 라이브러리](#ch12)
- [부록. 용어 사전](#glossary)


<a id="ch01"></a>

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
| Ruby | Sinatra | 데코레이터/DSL 스타일 라우트 선언 |
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

Python 3.5부터 도입된 **타입 힌트**(`def add(x: int, y: int) -> int:`)를 평소에 사용해 왔다면, FastAPI에서는 그 타입 힌트가 **자동 검증·자동 변환·자동 문서화**로 곧장 이어집니다.

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
from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

@app.get("/users/{user_id}")
async def get_user(user_id: int, db: AsyncSession) -> User:
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

집필 시점(2026년 4월) FastAPI의 최신 안정 버전은 **0.115.x 이상**입니다. "0.x"라고 하니 미완성 같지만, 실제로는 다음과 같습니다.

- FastAPI는 [SemVer 약속](https://semver.org/lang/ko/)을 따르되, 1.0 출시를 매우 보수적으로 미루고 있습니다.
- 2025년 3월에 0.115를 거치며 사실상 안정 단계에 진입했고, **수많은 회사가 운영 환경에서 그대로 쓰고 있습니다.**
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
네. Microsoft, Uber, Netflix 등 대형 기업의 일부 내부 서비스에서 FastAPI가 사용된다는 사실이 [공식 사이트의 회사 사용 사례 페이지](https://fastapi.tiangolo.com/#opinions)에 정리되어 있습니다. 한국에서도 다수의 스타트업과 ML/데이터 회사가 백엔드의 1순위로 FastAPI를 채택하고 있습니다.

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

<a id="ch02"></a>

# 02. 백엔드 기본 용어 정리

> **이 챕터의 목표**
> - 백엔드 개발에서 반복 등장하는 핵심 용어를 한 번에 정리한다.
> - HTTP가 어떻게 흘러가는지, 요청과 응답이 어떻게 생겼는지 손에 잡힐 정도로 이해한다.
> - 이후 챕터(05~11장)에서 별도 설명 없이 사용될 용어들의 레퍼런스 역할을 한다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **읽는 방법**
> 처음부터 끝까지 죽 읽어도 좋고, 이후 챕터에서 모르는 용어가 나올 때 해당 절만 찾아 펼쳐 읽는 사전처럼 써도 좋습니다. 굵은 글씨와 표를 위주로 빠르게 훑은 다음, 본문에서 자세히 풀어 쓴 부분을 다시 읽는 방식도 효과적입니다.

---

## 2.1 가장 기본: 클라이언트와 서버

### 2.1.1 클라이언트 / 서버

- **클라이언트(Client)**: 요청을 보내는 쪽. 웹 브라우저, 모바일 앱, 또 다른 서버, 또는 우리가 터미널에서 실행하는 `curl` 명령어도 클라이언트입니다.
- **서버(Server)**: 요청을 받아 처리하고 응답을 돌려주는 프로그램. 그 프로그램이 동작하는 컴퓨터(장비) 자체도 "서버"라고 부릅니다.

> **헷갈림 주의**: "서버"라는 말은 두 가지를 동시에 가리킵니다. (1) 우리가 만들 FastAPI **프로그램**, (2) 그 프로그램이 도는 **하드웨어 또는 가상 머신**. 문맥에 따라 자연스럽게 구분합니다.

가장 단순한 그림은 이렇습니다.

```
[클라이언트] ──요청(Request)──▶ [서버]
[클라이언트] ◀──응답(Response)── [서버]
```

우리가 작성할 FastAPI 코드는 이 그림의 오른쪽, 즉 "서버" 역할을 맡습니다. 클라이언트가 무엇이든(브라우저, 모바일 앱, 다른 서버) 백엔드 입장에서는 "HTTP로 들어온 요청"으로만 보입니다.

### 2.1.2 백엔드 / 프론트엔드

- **프론트엔드(Frontend)**: 사용자가 직접 보는 화면. 웹 페이지(HTML/CSS/JavaScript), 모바일 앱(Android, 그 외 모바일 플랫폼), 데스크톱 앱 등.
- **백엔드(Backend)**: 화면 뒤에서 동작하는 서버 측 로직, 데이터베이스, 인증, 비즈니스 규칙 등.

FastAPI는 **백엔드 프레임워크**이며, 이 가이드의 관심사입니다. 화면을 그리는 일(프론트엔드)은 별도 프로젝트가 맡는다고 가정합니다.

> **풀스택(full-stack)이란?** 한 사람이 프론트엔드와 백엔드를 모두 담당하는 것을 가리키는 말입니다. 이 가이드는 백엔드만 다루지만, 프론트엔드(예: React)와 어떻게 연결되는지에 대한 감각은 곳곳에서 함께 익힙니다.

### 2.1.3 API

**API**는 Application Programming Interface의 약자로, 서로 다른 소프트웨어가 통신하기 위한 규약입니다. 백엔드 문맥에서 "API"는 거의 항상 **HTTP 기반 웹 API**를 의미합니다(이 가이드에서도 마찬가지).

> **API를 쉽게 비유하면** 식당의 메뉴판 + 주문서와 같습니다. "이런 URL로 이런 데이터를 보내면, 이런 형식의 응답이 온다"는 약속을 적어둔 계약서입니다.

이 가이드에서 우리가 만드는 것은 **REST API**입니다. REST가 무엇인지는 2.6에서 자세히 다루지만, "URL과 HTTP 메서드를 약속에 따라 사용하는 웹 API"라고 우선 받아들이면 됩니다.

### 2.1.4 프로토콜

**프로토콜(protocol)**: 통신 규약. 서로 다른 컴퓨터가 같은 약속에 따라 데이터를 주고받기 위한 규칙입니다.

- **HTTP / HTTPS**: 우리가 다루는 주된 프로토콜. 웹 통신의 기본.
- **WebSocket**: 클라이언트와 서버가 양방향으로 메시지를 주고받는 실시간 통신용. 이 가이드의 범위 밖.
- **TCP / UDP**: HTTP보다 한 단계 아래의 전송 계층 프로토콜. 우리가 직접 다룰 일은 거의 없습니다.
- **gRPC**: HTTP/2 위에서 동작하는 효율적 RPC 프로토콜. 이 가이드의 범위 밖.

이 가이드는 **HTTP(S)** 만 깊이 다룹니다.

---

## 2.2 HTTP — 웹의 통신 규약

### 2.2.1 HTTP란

**HTTP(HyperText Transfer Protocol)**: 클라이언트와 서버가 텍스트 기반으로 주고받는 약속의 묶음입니다. HTTP는 **요청(Request)** 과 **응답(Response)** 이 한 쌍으로 오가는 단순한 모델로 동작합니다.

```
클라이언트 ──요청(Request)──▶ 서버
클라이언트 ◀──응답(Response)── 서버
```

요청 하나에 응답 하나. 이 단순함이 HTTP의 강점입니다. **서버는 한 요청을 끝내고 나면 그 요청에 대한 기억이 없습니다(stateless).** 다음 요청이 와도 누구였는지 알 수 없으므로, 토큰이나 쿠키로 매번 자기를 밝혀야 합니다(2.12 인증 절에서 다룹니다).

> **stateless(상태 없음)란?** 서버가 이전 요청을 기억하지 않는다는 뜻입니다. 같은 사용자가 두 번 요청해도, 두 번째 요청 입장에서는 첫 요청이 있었는지 모릅니다. 이게 불편해 보이지만, 서버를 여러 대로 늘리기 쉬워지는 결정적 장점이 있습니다(어느 서버에 요청이 가도 똑같이 처리 가능).

### 2.2.2 HTTP vs HTTPS

- **HTTP**: 평문 통신. 중간 네트워크 장비에서 내용을 볼 수 있음.
- **HTTPS**: TLS로 암호화된 HTTP. 도청·변조가 어려움. 현재 웹에서는 사실상 필수.

> **TLS(Transport Layer Security)란?** HTTP 위에 씌우는 암호화 층입니다. "TLS 인증서"는 이 암호화에 쓰이는 작은 파일이며, 도메인을 가지고 있으면 무료(Let's Encrypt)로도 발급받을 수 있습니다. 09장 배포에서 다룹니다.

FastAPI는 기본적으로 평문 HTTP로 동작하고, 운영 환경에서는 앞단에 둔 **Nginx 같은 리버스 프록시**나 클라우드 로드 밸런서가 HTTPS 처리를 담당하는 구조가 일반적입니다(09장에서 다룸).

### 2.2.3 HTTP 메시지 구조

모든 HTTP 요청과 응답은 동일한 구조를 갖습니다.

**요청(Request):**
```
POST /users HTTP/1.1               ← 시작줄 (메서드, 경로, 버전)
Host: api.example.com              ← 헤더 (여러 줄)
Content-Type: application/json
Authorization: Bearer eyJhbGc...
Content-Length: 52
                                   ← 빈 줄 (헤더 끝 표시)
{"email":"a@b.com","name":"Alice"} ← 바디(body)
```

**응답(Response):**
```
HTTP/1.1 201 Created               ← 시작줄 (버전, 상태 코드, 상태 텍스트)
Content-Type: application/json     ← 헤더
Content-Length: 68
                                   ← 빈 줄
{"id":42,"email":"a@b.com","name":"Alice","created_at":"..."}  ← 바디
```

구조는 양쪽 모두 **시작줄 → 헤더 → 빈 줄 → 바디** 순서입니다. 이 순서를 알아두면 나중에 디버깅 도구(브라우저 개발자 도구의 Network 탭, `curl -v`)가 토해내는 출력을 읽기가 한결 쉬워집니다.

### 2.2.4 헤더(Header)

요청·응답의 **메타데이터**(부가 정보)입니다. 키-값 쌍으로 표현됩니다. 자주 만나는 헤더들:

| 헤더 | 의미 | 예시 |
|------|------|------|
| `Content-Type` | 바디의 형식 | `application/json`, `multipart/form-data` |
| `Content-Length` | 바디의 바이트 수 | `512` |
| `Authorization` | 인증 정보 | `Bearer eyJhbGc...` |
| `Accept` | 응답으로 받고 싶은 형식 | `application/json` |
| `User-Agent` | 요청 보낸 클라이언트 정보 | `Mozilla/5.0 ...`, `MyMobileApp/1.0` |
| `Cookie` | 쿠키 값 (요청 시) | `session=abc123` |
| `Set-Cookie` | 쿠키 설정 (응답 시) | `session=abc123; HttpOnly` |
| `Cache-Control` | 캐싱 정책 | `no-cache`, `max-age=3600` |
| `Access-Control-Allow-Origin` | CORS 허용 출처 | `*`, `https://example.com` |

FastAPI에서는 핸들러 함수가 `Request` 객체를 인자로 받아 `request.headers["authorization"]` 식으로 헤더에 접근할 수 있습니다. 다만 인증·CORS처럼 자주 쓰는 헤더 처리는 거의 대부분 FastAPI의 의존성(`Depends`)·미들웨어가 알아서 해주므로, 직접 헤더를 만질 일은 의외로 적습니다.

### 2.2.5 바디(Body)

실제 데이터가 들어가는 부분입니다. 우리가 다룰 REST API에서는 거의 항상 **JSON**이 들어갑니다(2.7 절 참고).

- **요청 바디**: 클라이언트가 서버로 보내는 데이터(예: 회원가입 시 이메일·비밀번호).
- **응답 바디**: 서버가 클라이언트로 돌려주는 데이터(예: 조회한 사용자 정보 목록).

`GET`, `DELETE` 같은 메서드는 보통 요청 바디가 없습니다. `POST`, `PUT`, `PATCH`는 거의 항상 바디가 있습니다.

### 2.2.6 요청-응답 사이클을 한 번 따라가 보기

`POST /users`로 회원가입 요청이 들어왔을 때 FastAPI 내부에서 일어나는 흐름은 대략 이렇습니다.

1. **클라이언트**가 JSON 바디(`{"email":"a@b.com","password":"..."}`)와 함께 `POST` 요청을 보냄.
2. **Uvicorn**(ASGI 서버)이 TCP 연결로 들어온 바이트를 읽어 HTTP 메시지로 파싱.
3. **FastAPI**가 요청 URL과 메서드를 보고 `@app.post("/users")` 데코레이터가 붙은 함수를 찾음(라우팅).
4. FastAPI가 바디의 JSON을 **Pydantic 모델**(예: `UserCreate`)로 자동 변환·검증. 타입이 안 맞으면 즉시 422 응답.
5. 의존성(`Depends`)으로 선언된 값(예: DB 세션)을 만들어 함수 인자에 주입.
6. 함수가 실행되어 DB에 저장하고, 결과 객체를 반환.
7. 반환된 객체를 다시 JSON으로 직렬화. 응답 모델이 정의되어 있으면 그 모양만 남김.
8. **Uvicorn**이 그 JSON과 상태 코드(201)를 HTTP 응답 메시지로 만들어 클라이언트에 전송.

이 일련의 흐름을 우리가 직접 코딩하지 않아도 된다는 점이 FastAPI의 가장 큰 매력입니다. 우리는 **6번(함수 본문)** 만 작성하면 되고, 나머지는 데코레이터·타입 힌트·의존성 시스템이 알아서 처리합니다.

---

## 2.3 HTTP 메서드

### 2.3.1 자주 쓰는 메서드

메서드는 "이 요청이 자원에 대해 무엇을 하고 싶은가"를 나타내는 동사입니다.

| 메서드 | 의미 | 관례적 용도 | 바디 |
|--------|------|--------------|------|
| `GET` | 조회 | 자원 읽기 | 보통 없음 |
| `POST` | 생성 | 새 자원 만들기, 일반 데이터 제출 | 있음 |
| `PUT` | 전체 교체 | 자원을 통째로 새 값으로 교체 | 있음 |
| `PATCH` | 부분 수정 | 자원의 일부 필드만 수정 | 있음 |
| `DELETE` | 삭제 | 자원 제거 | 보통 없음 |
| `HEAD` | 헤더만 받기 | 자원 존재 확인 | 없음 |
| `OPTIONS` | 허용 메서드 조회 | CORS preflight 등 자동 처리 | 없음 |

CRUD 연산과의 매핑은 다음이 관례입니다.

| CRUD | HTTP 메서드 |
|------|-------------|
| **C**reate (생성) | POST |
| **R**ead (조회) | GET |
| **U**pdate (수정) | PUT 또는 PATCH |
| **D**elete (삭제) | DELETE |

### 2.3.2 PUT vs PATCH

- **PUT**: 자원을 통째로 보낸 데이터로 **교체**. 빠진 필드는 기본값/`null`이 됩니다.
- **PATCH**: 보낸 필드만 **부분 수정**. 빠진 필드는 그대로 둡니다.

```
# PUT (전체 교체)
PUT /users/42
{"email": "a@b.com", "name": "Alice"}
→ 42번 사용자의 모든 필드를 위 값으로 덮어쓴다.

# PATCH (부분 수정)
PATCH /users/42
{"name": "Alice"}
→ 42번 사용자의 name만 수정. email은 건드리지 않는다.
```

처음 배우는 단계에서는 **수정에 PATCH만 써도 충분합니다.** 부분 수정이 더 자연스럽고 실수 위험이 낮기 때문입니다. 전체 교체가 정말 필요할 때만 PUT을 씁니다.

### 2.3.3 멱등성(Idempotency)

같은 요청을 여러 번 보내도 **서버 상태**가 한 번 보낸 것과 동일하게 유지되는가? 를 묻는 속성입니다.

(주의: "응답 자체가 매번 동일하다"는 뜻이 아닙니다. 예: 첫 번째 `DELETE /users/42`는 200을 돌려주고 두 번째는 404를 돌려줄 수 있지만, 결과적으로 "42번 사용자가 없는 상태"는 동일합니다.)

- `GET`, `PUT`, `DELETE`, `HEAD`, `OPTIONS`는 **멱등(idempotent)**
- `GET`, `HEAD`, `OPTIONS`는 **safe**이기도 함(서버 상태를 전혀 바꾸지 않음)
- `POST`, `PATCH`는 **비멱등**(매 호출마다 새 자원이 만들어지거나 상태가 달라질 수 있음)

이 구분은 **재시도(retry) 설계**에서 중요합니다. 네트워크 타임아웃이 났을 때 멱등 메서드는 안전하게 다시 보낼 수 있지만, 비멱등 메서드(`POST`)는 두 번 처리되어 같은 글이 두 개 만들어지는 사고가 날 수 있습니다.

---

## 2.4 URL과 URI의 구조

### 2.4.1 URL 구성

```
https://api.example.com:8080/users/42?include=posts&limit=10#section
   │              │       │     │            │                    │
   │              │       │     │            │                    └── 프래그먼트(fragment)
   │              │       │     │            └── 쿼리 스트링(query string)
   │              │       │     └── 경로(path)
   │              │       └── 포트(port)
   │              └── 호스트(host) — 도메인 이름 또는 IP
   └── 스킴(scheme)
```

FastAPI 라우팅에서 자주 다루는 세 요소:

- **경로(path)**: `/users/42` — 라우트 매칭에 쓰임. `@app.get("/users/{user_id}")`
- **경로 파라미터(path parameter)**: 경로의 일부가 변수. 예: `/users/{user_id}` → `user_id = 42`
- **쿼리 파라미터(query parameter)**: `?include=posts&limit=10` — 선택적·필터·정렬·페이지네이션용

> **경로 파라미터 vs 쿼리 파라미터, 어떻게 구분하나?** 어떤 자원을 가리키느냐(`/users/42`)는 **경로**에, 그 자원을 어떻게 보여줄까에 대한 부가 옵션(`?limit=10&sort=name`)은 **쿼리**에 둡니다. "이 자원을 식별하기 위해 반드시 필요한가?"가 기준입니다.

```python
# FastAPI에서의 사용 예
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int, include: str | None = None):
    # user_id는 경로 파라미터 (반드시 필요)
    # include는 쿼리 파라미터 (없으면 None)
    return {"user_id": user_id, "include": include}
```

### 2.4.2 URI vs URL

- **URI(Uniform Resource Identifier)**: 자원 식별자의 총칭.
- **URL(Uniform Resource Locator)**: 위치(어디서 받을 수 있는지)까지 포함한 URI.

실무에서는 거의 구분 없이 씁니다. 그냥 **"URL"** 이라 말하면 통합니다. 이 가이드도 그렇게 씁니다.

### 2.4.3 슬래시(Trailing Slash) 관례

`/users`와 `/users/`는 사실 다른 URL입니다. FastAPI는 둘 다 매칭되도록 옵션을 줄 수 있지만, **하나로 통일하는 것**이 좋습니다. 이 가이드는 **슬래시를 끝에 붙이지 않는** 쪽으로 통일합니다(`/users`, `/users/42`). 이유는 단순합니다 — 모바일 앱이나 프론트엔드와 협업할 때 한 가지로 통일하면 사고가 줄어듭니다.

---

## 2.5 HTTP 상태 코드

서버가 응답에 붙이는 3자리 숫자입니다. 앞자리가 응답의 큰 분류를 나타냅니다.

| 범위 | 의미 |
|------|------|
| 1xx | 정보 (직접 다룰 일 거의 없음) |
| 2xx | 성공 |
| 3xx | 리다이렉트 |
| 4xx | 클라이언트 오류 |
| 5xx | 서버 오류 |

자주 쓰는 것만 외워두면 됩니다.

| 코드 | 이름 | 언제 쓰나 |
|------|------|-----------|
| 200 | OK | 일반적인 성공 |
| 201 | Created | POST로 자원 생성 성공 |
| 204 | No Content | 성공했지만 돌려줄 바디가 없음(DELETE 등) |
| 301 | Moved Permanently | 영구 이동 |
| 302 | Found | 임시 이동 |
| 400 | Bad Request | 잘못된 요청(JSON 형식이 깨짐 등) |
| 401 | Unauthorized | 인증되지 않음(로그인 필요) |
| 403 | Forbidden | 인증은 됐지만 권한이 없음 |
| 404 | Not Found | 자원이 존재하지 않음 |
| 405 | Method Not Allowed | 해당 경로가 그 메서드를 허용하지 않음 |
| 409 | Conflict | 충돌(이미 가입된 이메일로 또 가입 시도 등) |
| 422 | Unprocessable Entity | 형식은 맞지만 검증을 통과 못 함 — **FastAPI가 자주 돌려줌** |
| 429 | Too Many Requests | 너무 많이 요청함(레이트 리밋 초과) |
| 500 | Internal Server Error | 서버 내부에서 처리되지 않은 예외 |
| 502 | Bad Gateway | 프록시 뒤의 서버가 응답 못 함 |
| 503 | Service Unavailable | 일시적 서버 불가(점검·과부하) |

> **400과 422의 차이**가 자주 헷갈립니다.
> - 400: "요청 자체가 깨졌어." — 예를 들어 JSON 문법이 틀렸을 때.
> - 422: "JSON 모양은 맞는데 값이 검증을 통과 못 했어." — 예를 들어 `email` 필드에 숫자가 왔거나, 필수 필드가 빠졌을 때. **FastAPI/Pydantic이 자동으로 돌려줍니다.**

> **401과 403의 차이**도 자주 헷갈립니다.
> - 401: "너 누구야? 로그인부터 해."
> - 403: "네가 누군지 아는데, 이 동작은 너에게 허용되지 않아."

---

## 2.6 REST와 RESTful API

### 2.6.1 REST란

**REST**(Representational State Transfer)는 Roy Fielding이 2000년 박사 학위 논문에서 제안한 웹 아키텍처 스타일입니다. 핵심은 **자원(Resource)** 을 URL로 식별하고, **HTTP 메서드**로 그 자원에 대한 행위를 표현하는 것입니다.

쉽게 풀면 "URL은 자원을 가리키는 명사, 메서드는 동사"라는 약속입니다.

### 2.6.2 RESTful한 API 설계 관례

"RESTful"이란 REST의 원칙을 따르는 API를 말합니다. 다음 관례가 흔합니다.

- **자원은 명사로 표현**: `/users`, `/posts` (동사 아님 — `/getUsers` 같은 건 RESTful 하지 않음)
- **계층 구조 URL**: `/users/42/posts` ("42번 유저의 글들")
- **HTTP 메서드로 행위 표현**:
  - `GET /users` — 목록 조회
  - `GET /users/42` — 단건 조회
  - `POST /users` — 생성
  - `PUT /users/42` — 전체 교체
  - `PATCH /users/42` — 부분 수정
  - `DELETE /users/42` — 삭제
- **복수형 사용**: `/user`보다 `/users`로 통일(일관성)
- **쿼리로 필터·정렬·페이지네이션**: `/users?age_gte=20&sort=name&page=2`
- **의미 있는 상태 코드**: 201 Created(생성), 404 Not Found(없음), 409 Conflict(충돌) 등

### 2.6.3 좋은 REST 설계 예시 vs 나쁜 예시

| 의도 | 나쁜 예 | 좋은 예 |
|------|---------|---------|
| 사용자 목록 조회 | `GET /getUsers` | `GET /users` |
| 사용자 상세 조회 | `GET /user?id=42` | `GET /users/42` |
| 사용자 생성 | `POST /createUser` | `POST /users` |
| 사용자 삭제 | `POST /users/42/delete` | `DELETE /users/42` |
| 글 검색 | `GET /searchPosts?q=hi` | `GET /posts?search=hi` |
| 글에 좋아요 | `GET /likePost?id=10` | `POST /posts/10/likes` |

좋은 예의 공통점은 **URL은 명사, 메서드는 동사**라는 원칙을 지킨다는 점입니다.

### 2.6.4 주의: "REST"라는 단어의 현실

학술적 REST의 완전한 정의(특히 HATEOAS — 응답 안에 다음 가능한 동작 링크를 포함하는 것)를 엄격히 따르는 API는 드뭅니다. 현업에서 말하는 "REST API"는 거의 **"HTTP + JSON으로 CRUD를 표현하는 API"** 정도의 의미입니다. 이 가이드도 그 실용적 의미로 씁니다 — HATEOAS는 다루지 않습니다.

---

## 2.7 JSON과 데이터 형식

### 2.7.1 JSON

**JavaScript Object Notation**. 키-값 쌍과 배열로 이루어진 텍스트 형식. API 데이터 교환의 사실상 표준입니다.

```json
{
  "id": 42,
  "email": "dev@modapl.com",
  "active": true,
  "tags": ["python", "fastapi"],
  "profile": {
    "name": "Alice",
    "age": 30
  },
  "created_at": "2026-04-25T09:00:00Z"
}
```

JSON에서 표현할 수 있는 타입은 다음 여섯 가지뿐입니다.

| JSON 타입 | 예 | Python 대응 |
|-----------|----|-----|
| string | `"hello"` | `str` |
| number | `42`, `3.14` | `int`, `float` |
| boolean | `true`, `false` | `bool` |
| null | `null` | `None` |
| array | `[1, 2, 3]` | `list` |
| object | `{"k": "v"}` | `dict` |

JSON 자체에는 날짜·시간 타입이 없습니다. 그래서 보통 **ISO 8601 문자열**(`"2026-04-25T09:00:00Z"`) 또는 **Unix timestamp 정수**(`1777107600`)로 표현합니다. 이 가이드는 ISO 8601을 기본으로 씁니다 — 사람이 읽기 좋고, Pydantic이 알아서 `datetime` 객체로 변환해 줍니다.

### 2.7.2 직렬화(Serialization) / 역직렬화(Deserialization)

- **직렬화(serialize)**: Python 객체 → JSON 문자열. 응답을 보낼 때.
- **역직렬화(deserialize)**: JSON 문자열 → Python 객체. 요청을 받을 때.

> **이 단어들이 어렵게 느껴진다면** "객체 → 문자열" / "문자열 → 객체"로만 기억해도 충분합니다. FastAPI에서는 Pydantic이 자동으로 양방향을 처리하므로, 우리가 `json.loads()`나 `json.dumps()`를 직접 부르는 일은 드뭅니다.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    email: str

# 역직렬화: 클라이언트가 보낸 JSON → User 객체
# (FastAPI가 자동으로 처리하므로, 함수는 이미 만들어진 User를 받기만 함)
@app.post("/users")
async def create_user(user: User) -> User:
    # 직렬화: 반환한 User 객체 → JSON 응답
    # (이것도 FastAPI가 자동으로 처리)
    return user
```

### 2.7.3 다른 데이터 형식들 (참고)

- **XML**: JSON 이전에 널리 쓰이던 형식. 현재는 구형 시스템·SOAP API에서만 만나게 됩니다.
- **YAML**: 설정 파일(`.yml`, `.yaml`)에 주로 씁니다. API 데이터 교환에는 거의 안 씁니다.
- **Protobuf**: Google이 만든 바이너리 형식. gRPC에서 씁니다. 매우 효율적이지만 사람이 직접 읽기 어렵습니다.
- **MessagePack**: JSON과 거의 같은 모델인데 바이너리로 압축한 형식.

이 가이드는 **JSON만** 사용합니다. 처음 백엔드를 만들 때 다른 형식을 섞으면 디버깅이 매우 어려워집니다.

---

## 2.8 쿼리 파라미터, 경로 파라미터, 바디

데이터를 어디에 담을지에 대한 정리입니다.

| 위치 | 언제 쓰나 | 예시 |
|------|-----------|------|
| **경로 파라미터** | 자원 식별자(id 등) | `GET /users/42` → `42` |
| **쿼리 파라미터** | 선택적 필터·정렬·페이지 | `GET /users?age=20&sort=name&page=2` |
| **요청 바디 (JSON)** | 생성/수정할 데이터 | `POST /users` + `{"name":"Alice"}` |
| **헤더** | 메타데이터·인증 | `Authorization: Bearer xxx` |

규칙:

- **민감한 데이터는 쿼리에 절대 넣지 않습니다.** URL은 서버·중간 프록시·브라우저 히스토리에 그대로 로그로 남습니다. 비밀번호·토큰은 헤더 또는 바디에 넣어야 합니다.
- **경로 파라미터는 필수**, **쿼리는 선택** 이 관례입니다. "이 자원을 가리키려면 반드시 필요한가?" 기준으로 결정합니다.
- **GET 요청의 바디는 쓰지 않습니다.** HTTP 표준으로 금지된 건 아니지만, 중간 프록시·캐시·라이브러리들이 종종 무시하므로 신뢰할 수 없습니다.

```python
# FastAPI에서의 종합 예
from fastapi import FastAPI, Request

app = FastAPI()

@app.get("/users/{user_id}/posts")
async def list_user_posts(
    user_id: int,                          # 경로 파라미터
    request: Request,                      # Request 객체로 헤더 등 접근
    page: int = 1,                         # 쿼리 (기본값 1)
    sort: str = "created_at",              # 쿼리
):
    # request.headers 등으로 헤더에 접근 가능
    return {"user_id": user_id, "page": page, "sort": sort}
```

---

## 2.9 미들웨어

### 2.9.1 개념

**미들웨어(Middleware)**: 요청과 응답 사이에 끼어드는 코드 블록입니다. 여러 미들웨어가 파이프라인처럼 줄지어 있고, 모든 요청은 그 줄을 한 번씩 통과하며 처리됩니다.

```
요청 → [로깅 MW] → [인증 MW] → [CORS MW] → [라우트 핸들러] → 응답
        │            │            │
        └ 시간 기록   └ 토큰 검증   └ 헤더 추가
```

### 2.9.2 미들웨어로 구현하기 좋은 일

- **로깅**: 모든 요청의 메서드·경로·소요 시간 기록
- **인증·인가 체크**: 토큰 헤더가 있는지, 유효한지 검사
- **CORS 헤더 추가**: 응답에 `Access-Control-Allow-Origin` 같은 헤더 자동 삽입
- **요청 바디 파싱**: 거의 항상 프레임워크가 자동으로 처리
- **에러 핸들링**: 처리되지 않은 예외를 잡아 일관된 JSON 에러 응답으로 변환
- **레이트 리밋(Rate Limit)**: 일정 시간 동안 같은 IP에서 너무 많이 요청하면 차단

> **횡단 관심사(Cross-cutting Concern)란?** 모든 요청에 대해 똑같이 해야 하는 일(로깅·인증·CORS)을 가리키는 말입니다. 이런 일은 라우트 함수마다 반복하지 않고 미들웨어에 모아둡니다.

FastAPI에서는 `app.add_middleware(...)` 또는 `@app.middleware("http")` 데코레이터로 등록합니다. 04장 이후에서 실제 코드를 작성합니다.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://my-frontend.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 2.10 라우팅과 엔드포인트

### 2.10.1 라우팅

요청의 **메서드 + 경로**를 특정 핸들러 함수에 연결하는 작업입니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")    # GET /users/42 매칭
async def get_user(user_id: int): ...

@app.post("/users")              # POST /users 매칭
async def create_user(...): ...
```

`@app.get`, `@app.post` 같은 데코레이터가 "이 함수를 그 메서드+경로의 처리기로 등록해라"는 의미를 갖습니다.

### 2.10.2 엔드포인트

클라이언트가 호출하는 하나의 API 단위입니다. 보통 **URL + HTTP 메서드 한 쌍**을 가리킵니다. 예: "`POST /users` 엔드포인트", "`GET /users/{user_id}` 엔드포인트". "라우트(route)"와 거의 동의어로 쓰입니다.

### 2.10.3 라우트 / 핸들러 / 라우터

- **라우트(Route)**: 메서드 + 경로의 등록 정보 한 건.
- **핸들러(Handler)**: 그 라우트가 매칭됐을 때 실행되는 함수. FastAPI에서는 그냥 일반 함수(`def` 또는 `async def`).
- **라우터(Router)**: 여러 라우트를 한 모듈로 묶는 객체. FastAPI에서는 `APIRouter`. 큰 앱에서 도메인별로 파일을 나눌 때 씁니다.

```python
# users 도메인 라우터 모듈
from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

@router.get("")
async def list_users(): ...

@router.get("/{user_id}")
async def get_user(user_id: int): ...

# 메인 앱에서 등록
app.include_router(router)
```

이 구조는 11장 Blog API에서 본격적으로 사용됩니다.

---

## 2.11 데이터베이스

### 2.11.1 DB의 분류

| 분류 | 예시 | 특징 |
|------|------|------|
| 관계형 DB (RDBMS) | PostgreSQL, MySQL, SQLite, MariaDB | 표(테이블), SQL, ACID 강함 |
| NoSQL — 문서 | MongoDB, Couchbase | 스키마 유연, JSON 유사 |
| NoSQL — 키밸류 | Redis, DynamoDB | 초고속 단순 조회 |
| NoSQL — 컬럼 | Cassandra, ScyllaDB | 대규모 쓰기에 강함 |
| 그래프 DB | Neo4j | 관계가 핵심인 데이터(소셜 그래프 등) |
| 시계열 | InfluxDB, TimescaleDB | 로그·메트릭 |

이 가이드는 **관계형 DB(SQLite, MySQL, PostgreSQL)** 만 다룹니다. 백엔드 입문자가 가장 먼저 배워야 할 것이며, 거의 모든 일반 서비스에 충분합니다.

> **어떤 DB로 시작할까?** 이 가이드는 **개발 단계에서 SQLite** → **운영 단계에서 PostgreSQL** 흐름을 권장합니다. SQLite는 파일 하나로 동작해서 설치가 필요 없고, PostgreSQL은 운영에서 가장 안정적인 선택지입니다. 06장에서 어떤 DB든 같은 SQLAlchemy 코드로 다룰 수 있다는 점을 보여줍니다.

### 2.11.2 테이블, 행, 열

관계형 DB는 자료를 표(테이블) 형태로 저장합니다.

- **테이블(table)**: 자료를 모은 표 한 장. 예: `users` 테이블.
- **행(row, record)**: 표의 가로줄 하나. 한 사용자에 해당.
- **열(column, field)**: 표의 세로줄 하나. `email`, `name` 같은 속성.

```
users 테이블
┌────┬─────────────────┬──────────┬─────────────────────┐
│ id │ email           │ name     │ created_at          │
├────┼─────────────────┼──────────┼─────────────────────┤
│  1 │ a@example.com   │ Alice    │ 2026-04-25 09:00:00 │
│  2 │ b@example.com   │ Bob      │ 2026-04-25 09:05:00 │
│  3 │ c@example.com   │ Carol    │ 2026-04-25 10:00:00 │
└────┴─────────────────┴──────────┴─────────────────────┘
```

### 2.11.3 스키마(Schema)

테이블의 구조 — 어떤 열이 있고, 어떤 타입이며, 어떤 제약조건(NOT NULL, UNIQUE 등)이 있는가를 가리킵니다.

```
users 테이블 스키마
┌──────────────┬──────────────┬──────────┬────────────┐
│ 열 이름      │ 타입         │ NULL?    │ 기본값     │
├──────────────┼──────────────┼──────────┼────────────┤
│ id           │ INTEGER      │ NOT NULL │ AUTO       │
│ email        │ VARCHAR(255) │ NOT NULL │            │
│ name         │ VARCHAR(100) │ NOT NULL │            │
│ created_at   │ TIMESTAMP    │ NOT NULL │ now()      │
└──────────────┴──────────────┴──────────┴────────────┘

제약: email은 UNIQUE
```

### 2.11.4 기본 키 / 외래 키

- **기본 키(Primary Key, PK)**: 각 행을 고유하게 가리키는 열. 보통 `id`라는 정수 자동 증가 열을 씁니다.
- **외래 키(Foreign Key, FK)**: 다른 테이블의 PK를 가리키는 열. "이 글의 작성자(`user_id`)는 사용자 테이블의 그 사람"이라는 연결을 표현합니다.

```
posts 테이블
┌────┬──────────┬─────────────┬──────────┐
│ id │ title    │ content     │ user_id  │  ← user_id가 FK
├────┼──────────┼─────────────┼──────────┤
│  1 │ Hello    │ Hi there!   │  1       │  ← Alice가 쓴 글
│  2 │ World    │ Yo.         │  2       │  ← Bob이 쓴 글
└────┴──────────┴─────────────┴──────────┘
                                  │
                                  └─ users 테이블의 id를 가리킴
```

### 2.11.5 SQL 기본

ORM을 써도 SQL의 기초는 알아둬야 합니다 — 결국 ORM이 SQL을 만들어 보내고 있기 때문입니다.

- **`SELECT`**: 조회 (`SELECT * FROM users WHERE id = 42`)
- **`INSERT`**: 삽입
- **`UPDATE`**: 수정
- **`DELETE`**: 삭제
- **`JOIN`**: 두 테이블을 합쳐서 보기
- **`WHERE`**: 조건 필터
- **`ORDER BY`**: 정렬
- **`LIMIT / OFFSET`**: 페이지네이션
- **`GROUP BY / HAVING`**: 집계
- **`TRANSACTION`**: 묶음으로 처리

### 2.11.6 관계 (1:1, 1:N, N:M)

테이블 사이의 연결입니다.

- **1:1 (one-to-one)**: 한 사용자 ↔ 한 프로필. 자주 안 쓰임.
- **1:N (one-to-many)**: 한 사용자 ↔ 여러 글. **가장 흔함.** 예: `posts.user_id`.
- **N:M (many-to-many)**: 여러 글 ↔ 여러 태그. 중간 테이블(연결 테이블)이 필요. 예: `posts`, `tags`, `posts_tags`.

11장 Blog API에서 1:N과 N:M을 모두 직접 구현해 봅니다.

### 2.11.7 인덱스

자주 검색하는 열에 미리 만들어 두는 "찾아보기" 자료구조입니다. `SELECT * FROM users WHERE email = ?` 같은 쿼리를 빠르게 합니다.

- **장점**: 조회가 매우 빨라짐 (테이블 전체를 훑지 않고 인덱스로 곧장 도달).
- **단점**: 디스크 공간을 더 씀, 그리고 그 열에 INSERT/UPDATE 할 때마다 인덱스도 갱신해야 해서 쓰기가 살짝 느려짐.

규칙: **자주 검색하는 열, 외래 키 열, UNIQUE로 만들어야 하는 열에는 인덱스를 건다.** 일단 모든 열에 인덱스를 거는 건 좋지 않습니다.

### 2.11.8 트랜잭션

여러 DB 작업을 **하나의 원자 단위**로 묶는 것입니다. 전부 성공하거나 전부 실패하거나 둘 중 하나입니다.

대표적 예: **계좌 이체**. A의 잔액에서 1만 원을 빼고, B의 잔액에 1만 원을 더하는 두 SQL이 있습니다. 첫 SQL만 성공하고 두 번째가 실패하면 돈이 사라집니다. 트랜잭션으로 묶으면 둘 중 하나라도 실패할 경우 첫 SQL도 자동으로 되돌려집니다(롤백).

```sql
BEGIN;
UPDATE accounts SET balance = balance - 10000 WHERE id = 1;  -- A
UPDATE accounts SET balance = balance + 10000 WHERE id = 2;  -- B
COMMIT;  -- 둘 다 성공이면 확정. 실패면 ROLLBACK으로 되돌림.
```

**ACID** 속성:
- **A**tomicity (원자성): 전부 또는 전무.
- **C**onsistency (일관성): 트랜잭션 전후로 DB가 항상 유효한 상태.
- **I**solation (격리성): 동시에 일어나는 트랜잭션끼리 서로 영향을 주지 않음.
- **D**urability (지속성): 커밋된 변경은 시스템이 죽어도 살아남음.

SQLAlchemy 세션은 자동으로 트랜잭션을 시작하고, `commit()`이나 `rollback()`을 부르는 시점에 끝냅니다. 06장에서 자세히 다룹니다.

### 2.11.9 마이그레이션 (Migration)

DB 스키마 변경(열 추가, 새 표 만들기 등)을 **코드로 기록**하는 작업입니다. 팀 전체가 같은 스키마를 쓰게 하고, 운영 배포 시 자동으로 적용할 수 있습니다.

이 가이드는 **Alembic**을 씁니다(SQLAlchemy와 짝지어 쓰는 표준 도구). 06장에서 처음부터 다룹니다.

```
# 마이그레이션의 흐름 (개념만)
1. 모델(Python 클래스)을 수정한다 → users 테이블에 nickname 열을 추가하고 싶다.
2. Alembic이 자동으로 마이그레이션 파일을 만든다 → "users에 nickname 추가" 라는 변경 기록.
3. 그 파일을 git에 커밋한다 → 팀원이 같이 받는다.
4. 각자 alembic upgrade head 명령으로 자신의 DB에 적용한다.
5. 배포 시에도 같은 명령으로 운영 DB에 적용한다.
```

### 2.11.10 ORM

**ORM(Object Relational Mapper)**: DB의 테이블과 프로그래밍 언어의 객체(클래스)를 연결해 주는 라이브러리입니다. 직접 SQL을 쓰지 않고도 쿼리를 작성할 수 있게 합니다.

이 가이드는 **SQLAlchemy 2.0**을 씁니다 — Python에서 가장 널리 쓰이는 ORM이며, 동기와 비동기 API를 모두 제공합니다. 우리는 비동기(async) API를 씁니다.

```python
# SQL을 직접 쓴 경우
SELECT * FROM users WHERE email = 'a@example.com' LIMIT 1;

# SQLAlchemy로 표현한 같은 쿼리
from sqlalchemy import select
stmt = select(User).where(User.email == "a@example.com").limit(1)
result = await session.execute(stmt)
user = result.scalar_one_or_none()
```

ORM의 장점은 **타입 안전성과 가독성**입니다. 오타를 미리 잡을 수 있고, IDE 자동완성이 잘 동작합니다. 단점은 복잡한 쿼리에서 SQL이 비효율적으로 생성될 수 있다는 점인데, 이는 06장에서 흔한 함정과 함께 다룹니다.

### 2.11.11 N+1 문제

ORM을 쓸 때 입문자가 가장 자주 만나는 성능 함정입니다. 목록을 가져온 다음(N개), 각 항목마다 또 쿼리를 1번씩 더 날려서 총 N+1번 쿼리가 나가는 비효율 패턴입니다.

```python
# 안 좋은 예 (N+1)
posts = await session.execute(select(Post))
for post in posts.scalars():
    print(post.author.name)   # ← 매 글마다 author를 가져오기 위해 SQL 한 번씩 더!

# 좋은 예 (한 번에 JOIN)
from sqlalchemy.orm import selectinload
stmt = select(Post).options(selectinload(Post.author))
posts = await session.execute(stmt)
```

11장 Blog API에서 이 문제와 해결법(`selectinload`, `joinedload`)을 본격적으로 다룹니다.

---

## 2.12 인증과 인가

### 2.12.1 Authentication vs Authorization

- **인증(Authentication, AuthN)**: "너 누구야?" — 신원 확인. 로그인.
- **인가(Authorization, AuthZ)**: "너 이걸 해도 돼?" — 권한 확인.

**인증 → 인가** 순서로 이뤄집니다. 상태 코드도 각각 401(인증 실패), 403(인가 실패)입니다.

> **헷갈림 주의**: 영어 단어가 비슷해서 짧게 줄여 **AuthN**(인증)과 **AuthZ**(인가)로 구분해서 부르기도 합니다.

### 2.12.2 인증 방식들

| 방식 | 설명 | 용례 |
|------|------|------|
| Basic Auth | 헤더에 `user:pass`를 Base64로 인코딩해 전송 | 단순 API, 개발용 |
| Bearer Token (예: JWT) | 헤더에 토큰을 붙여 전송 | 모바일 앱, SPA |
| Session Cookie | 서버가 세션을 유지하고 쿠키로 ID 전달 | 전통적 웹 |
| API Key | 고정된 키를 헤더 또는 쿼리로 전달 | 서비스 간 통신 |
| OAuth 2.0 | 제3자(구글, 깃허브 등)에게 인증 위임 | 소셜 로그인 |

이 가이드는 **Bearer Token + JWT** 조합을 씁니다. 모바일 앱·SPA 백엔드에서 가장 보편적이며, 서버를 여러 대로 늘리기에도 유리합니다.

### 2.12.3 세션(서버 저장) vs 토큰(클라이언트 저장)

| 항목 | 세션(Session) | JWT |
|------|------|-----|
| 저장 위치 | 서버 메모리 또는 DB | 클라이언트 |
| 확장성 | 세션 스토어를 모든 서버가 공유해야 함 | 스테이트리스라 쉬움 |
| 즉시 무효화 | 쉽다 (서버에서 삭제) | 어렵다 (블랙리스트 별도 필요) |
| 모바일 친화성 | 쿠키 관리 필요 | 헤더에 넣기 간편 |
| 데이터 노출 | 서버에만 있음 | 페이로드는 누구나 디코딩 가능(서명만 검증) |

> **세션을 안 쓰는 이유**: 세션은 서버 메모리에 사용자 상태를 저장합니다. 서버가 한 대일 때는 괜찮지만, 운영에서 여러 대로 늘리면 "어느 서버가 그 세션을 갖고 있나?"를 매번 확인해야 합니다(=공유 세션 스토어 필요). 모바일·SPA·MSA 시대에는 부담입니다. JWT는 서버에 아무것도 저장하지 않으므로 이런 문제가 없습니다.

### 2.12.4 JWT (JSON Web Token)

JWT는 서버가 사용자 정보를 담아 **서명한 작은 문자열**입니다. 클라이언트는 이 문자열을 들고 다니다가 요청마다 헤더에 실어 보냅니다.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiIsImV4cCI6MTc2MDAwMDAwMH0.SflKxwRJSMeKKF2...
```

**Base64URL 인코딩된 세 부분**이 점(`.`)으로 연결된 구조입니다.

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiIsImV4cCI6MTc2MDAwMDAwMH0.SflKxwRJSMeKKF2...
└──── Header ─────┘ └─────── Payload ───────────────────────┘ └── Signature ──┘
```

- **Header**: 서명 알고리즘 정보 (예: `{"alg": "HS256"}`)
- **Payload**: 데이터(클레임). 예: 사용자 ID, 만료 시간
- **Signature**: Header + Payload를 서버의 비밀 키(secret)로 서명한 값

검증은 다음 순서로 이뤄집니다.

1. **먼저 Signature로 위변조 검증** — 서명이 맞아야 Payload를 신뢰할 수 있습니다.
2. 서명이 유효하면 Payload 안의 클레임으로 사용자를 식별합니다.
3. `exp`(만료) 같은 시간 클레임도 함께 검증합니다.

특징:

- **Stateless**: 서버가 토큰을 따로 저장하지 않습니다 → 서버 여러 대로 늘리기 쉽습니다.
- **만료 시간(`exp`)** 을 반드시 설정해야 합니다 — 없으면 영원히 유효한 토큰이 만들어집니다.
- 서명 덕분에 **위조는 거의 불가능**하지만, **훔치면 그대로 통과**되므로 HTTPS가 필수입니다.
- **페이로드는 암호화가 아니라 서명**입니다. 누구나 Base64 디코딩만으로 내용을 볼 수 있으니, 비밀번호·민감정보를 넣지 마세요.

### 2.12.5 표준 JWT 클레임

| 클레임 | 뜻 |
|--------|----|
| `iss` | Issuer, 발급자 |
| `sub` | Subject, 대상 — 보통 사용자 ID |
| `aud` | Audience, 대상 수신자 |
| `exp` | Expiration, 만료 시각 (Unix timestamp) |
| `nbf` | Not Before, 이 시각 이전엔 무효 |
| `iat` | Issued At, 발급 시각 |
| `jti` | JWT ID, 토큰 고유 ID |

이 가이드의 08장에서 PyJWT로 직접 토큰을 만들고 검증해 봅니다.

### 2.12.6 비밀번호 해싱과 Bcrypt

비밀번호는 **절대** 평문으로 DB에 저장하지 않습니다. **단방향 해시 함수**(되돌릴 수 없는 변환)로 바꿔서 저장하고, 로그인 시 입력값을 같은 방식으로 해시해 저장된 값과 비교합니다.

- 단순 해시(SHA-256 등)는 너무 빨라서 무차별 대입 공격(brute-force)에 약합니다.
- **Bcrypt**는 의도적으로 **느리게** 설계되어 무차별 공격을 어렵게 만듭니다. "느린 게 장점"이라는 점이 직관과 반대인데, 공격자가 한 번 시도하는 데 걸리는 시간을 늘려야 안전하기 때문입니다.
- **Salt**(임의 값)를 함께 섞어 같은 비밀번호여도 사용자마다 결과 해시가 다르게 만듭니다. 이는 미리 계산된 해시 표(레인보우 테이블)를 무력화합니다.

```python
import bcrypt

# 회원가입: 평문 → 해시
plain = "my-password"
hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt())
# DB에 hashed를 저장

# 로그인: 입력값을 같은 방식으로 해시해서 비교
ok = bcrypt.checkpw(plain.encode(), hashed)
```

08장에서 회원가입·로그인 흐름을 처음부터 직접 구현합니다.

---

## 2.13 CORS

### 2.13.1 동일 출처 정책 (Same-Origin Policy)

브라우저는 보안상 **현재 페이지가 떠 있는 출처(스킴+호스트+포트)와 다른 곳의 리소스**를 스크립트로 마음대로 가져오지 못하게 막아둡니다. 이게 동일 출처 정책입니다.

> **출처(origin)란?** 스킴(`https`) + 호스트(`example.com`) + 포트(`:443`)의 조합입니다. 셋 중 하나라도 다르면 다른 출처입니다. `https://a.com`과 `https://b.com`은 호스트가 달라서 다른 출처, `https://a.com`과 `http://a.com`도 스킴이 달라서 다른 출처입니다.

이 정책은 모르는 사이트가 우리가 로그인된 다른 사이트의 정보를 빼가는 공격을 막아줍니다. 하지만 **개발 중에는 제약**이 됩니다 — 프론트엔드(`http://localhost:5173`)와 백엔드(`http://localhost:8000`)가 다른 포트에서 도니 다른 출처가 되어 차단됩니다.

### 2.13.2 CORS

**CORS(Cross-Origin Resource Sharing)**: 서버가 "이 출처는 허용한다"고 응답 헤더로 알려주면 브라우저가 그 차단을 풀어주는 약속입니다.

서버가 응답에 붙이는 헤더(예시):

```
Access-Control-Allow-Origin: https://my-frontend.example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

FastAPI에서는 `CORSMiddleware`로 한 줄에 처리할 수 있습니다.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://my-frontend.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

### 2.13.3 CORS는 브라우저의 일이다

CORS는 **브라우저가 강제하는 정책**입니다. 따라서:

- 브라우저(웹 페이지·SPA)에서 호출하는 경우 → CORS가 동작.
- **모바일 앱이나 서버에서 직접 호출**하는 경우 → CORS는 적용되지 않음. 모바일 앱 백엔드만 만든다면 사실상 CORS를 신경 쓸 필요가 없습니다.
- 다만 관리자 페이지·웹 클라이언트가 같이 붙는 경우는 반드시 설정해야 합니다.

> **자주 만나는 함정**: `allow_origins=["*"]`로 두면 모든 출처를 허용해 편하지만, **`allow_credentials=True`와 함께 쓸 수 없습니다**(CORS 표준 제약). 쿠키·인증을 동반하는 프론트엔드와 붙일 때는 와일드카드 대신 실제 출처를 명시해야 합니다.

---

## 2.14 환경 변수

### 2.14.1 왜 필요한가

DB 비밀번호, JWT 시크릿 같은 **민감한 값**을 코드에 박으면 유출 위험이 커집니다(특히 코드를 GitHub에 올릴 때). 또한 환경마다(개발·스테이징·운영) 값이 달라야 하는 경우가 많습니다 — 개발 DB와 운영 DB는 분리되어야 합니다.

**환경 변수**는 운영체제 수준에서 프로세스에 주입되는 값입니다. 코드 변경 없이 환경마다 다르게 설정할 수 있습니다.

### 2.14.2 `.env` 파일

개발 편의를 위해 `.env`라는 파일에 환경 변수를 모아둡니다.

```
# .env
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/mydb
JWT_SECRET=very-long-random-string-please
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
LOG_LEVEL=DEBUG
```

> **반드시 지킬 약속**: `.env`는 **절대 git에 커밋하지 않습니다.** `.gitignore`에 등록해 두세요. 팀원과는 `.env.example` 같은 키만 적힌 샘플 파일을 공유합니다.

```
# .env.example (이건 커밋해도 OK — 값이 비어 있음)
DATABASE_URL=
JWT_SECRET=
JWT_ALGORITHM=HS256
JWT_EXPIRES_MINUTES=60
LOG_LEVEL=INFO
```

### 2.14.3 FastAPI에서의 사용

이 가이드에서는 **`pydantic-settings`** 라이브러리로 `.env` 파일을 읽어 설정 객체에 채웁니다. 직접 `os.environ`을 읽는 것보다 훨씬 안전합니다 — 빠진 값이 있으면 시작 시점에 즉시 에러를 내고, 타입 검증도 자동입니다.

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    jwt_secret: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    jwt_expires_minutes: int = 60

settings = Settings()
```

이렇게 해 두면 앱이 시작될 때 `.env`(또는 OS 환경 변수)에서 값이 자동으로 읽혀 `settings.jwt_secret`처럼 타입 안전하게 접근할 수 있습니다. 04장 이후에서 본격적으로 쓰입니다.

---

## 2.15 포트, IP, DNS

### 2.15.1 IP 주소

네트워크상의 장비 식별자입니다.

- **IPv4**: `192.168.1.10`처럼 0~255 숫자 4개로 표현. 자주 만남.
- **IPv6**: `2001:db8::1` 같은 더 긴 주소 형식. 점차 도입 중.

개발 중에 자주 보는 주소들:

- **`127.0.0.1`** 또는 **`localhost`**: "이 컴퓨터 자신". 개발 서버를 띄우면 보통 여기서 동작.
- **`0.0.0.0`**: "모든 네트워크 인터페이스에서 받기". 서버를 외부에서도 접근 가능하게 만들 때 사용.
- **`::1`**: IPv6 형식의 localhost.

### 2.15.2 포트

한 IP 안에서 여러 프로그램을 구분하는 번호입니다. 0~65535 범위.

- **80**: HTTP 기본
- **443**: HTTPS 기본
- **8000**: 개발용 HTTP에 흔히 쓰는 번호 (FastAPI 기본)
- **8080**: 또 다른 개발용 HTTP 흔한 번호
- **5432**: PostgreSQL 기본
- **3306**: MySQL 기본
- **6379**: Redis 기본

FastAPI/Uvicorn은 기본적으로 `http://127.0.0.1:8000`에서 시작합니다. 04장에서 첫 서버를 띄울 때 직접 보게 됩니다.

### 2.15.3 DNS

사람이 기억하기 어려운 IP(`172.217.14.238`)를 `google.com` 같은 이름으로 매핑하는 시스템입니다. 도메인을 구매한 뒤 DNS 레코드를 설정해서 우리 서버 IP와 연결합니다.

- **A 레코드**: 도메인 → IPv4 주소 매핑
- **AAAA 레코드**: 도메인 → IPv6 주소 매핑
- **CNAME 레코드**: 도메인 → 다른 도메인 매핑(별칭)

09장 배포 절에서 도메인을 우리 서버에 연결하는 절차를 다룹니다.

---

## 2.16 컨테이너와 Docker

### 2.16.1 배경 — "내 컴퓨터에선 되는데"

개발 장비와 운영 서버 사이의 환경 차이 때문에 생기는 고전적 문제가 있습니다. Linux 버전, Python 버전, 시스템 라이브러리, 경로 설정이 미묘하게 달라 동작이 갈립니다. 이를 해결하기 위해 **컨테이너** 기술이 등장했습니다.

### 2.16.2 컨테이너

**컨테이너(Container)**: 애플리케이션과 그 실행 환경(OS 라이브러리, 의존성, 환경 변수 등)을 함께 패키징한 **경량 실행 단위**입니다. 가상 머신(VM)과 달리 호스트의 커널을 공유하므로 훨씬 가볍습니다.

핵심 효과: **개발 PC에서 돌리던 앱이 운영 서버에서도 똑같이 돈다.** "내 컴퓨터에선 되는데" 문제가 거의 사라집니다.

### 2.16.3 Docker

가장 널리 쓰이는 컨테이너 플랫폼입니다.

- **이미지(Image)**: 컨테이너를 만드는 **청사진**. 정적 파일. 배포 단위.
- **컨테이너(Container)**: 이미지로 만든 **실행 인스턴스**.
- **Dockerfile**: 이미지를 만드는 **레시피 텍스트 파일**. (`FROM python:3.13-slim` 으로 시작.)
- **docker-compose.yml**: 여러 컨테이너(앱 + DB + Redis 등)의 관계를 정의하는 파일. 개발 환경에서 매우 유용.
- **레지스트리(Registry)**: 이미지 저장소(Docker Hub, GitHub Container Registry, AWS ECR 등).

> **이미지와 컨테이너의 관계**는 "클래스와 인스턴스"의 관계와 비슷합니다. 한 이미지로 컨테이너를 여러 개 만들 수 있고, 컨테이너를 지워도 이미지는 그대로 남아 있습니다.

09장에서 FastAPI 앱을 Docker로 컨테이너화하고, Docker Compose로 PostgreSQL과 함께 띄우는 방법을 다룹니다.

---

## 2.17 리버스 프록시와 로드 밸런서

### 2.17.1 리버스 프록시

클라이언트의 요청을 받아 **뒤에 있는 진짜 앱 서버**로 전달하는 중계 서버입니다. 대표적으로 **Nginx**.

리버스 프록시가 맡는 일:

- **HTTPS 종단(TLS termination)**: 외부와는 HTTPS, 내부 앱과는 평문 HTTP로 통신. TLS 인증서 관리를 한 곳에 모음.
- **정적 파일 서빙**: 이미지·CSS·JS 같은 파일을 앱 대신 빠르게 응답.
- **캐싱**: 자주 요청되는 응답을 잠시 보관해 빠르게 돌려줌.
- **보안**: 잘못된 요청 차단, 민감한 헤더 삭제 등.
- **여러 앱에 경로 기반 분기**: `/api`는 FastAPI로, `/static`은 파일 서버로.

### 2.17.2 로드 밸런서

여러 서버 인스턴스에 트래픽을 골고루 나눠주는 중계자입니다. AWS의 ALB(Application Load Balancer), GCP의 Cloud Load Balancing, 또는 Nginx 자체로도 가능합니다.

수평 확장(서버 대수 늘리기)을 위해 FastAPI 앱을 여러 프로세스·여러 서버로 띄우고, 그 앞에 로드 밸런서를 두는 것이 운영의 기본 패턴입니다.

```
                  ┌──→ FastAPI 워커 1
[클라이언트]──▶ Nginx ──┼──→ FastAPI 워커 2
                  └──→ FastAPI 워커 3
```

09장 운영 배포 절에서 직접 설정해 봅니다.

---

## 2.18 CI / CD

- **CI(Continuous Integration)**: 코드를 저장소에 푸시할 때마다 자동으로 빌드·테스트를 돌리는 흐름.
- **CD(Continuous Deployment / Delivery)**: 그 결과물을 자동으로 스테이징 또는 운영 환경에 배포하는 흐름.

도구로는 **GitHub Actions**(이 가이드의 기본), GitLab CI, CircleCI, Jenkins 등이 있습니다. 09장 배포 절에서 GitHub Actions로 Docker 이미지를 빌드해 푸시하는 짧은 예제를 다룹니다.

CI/CD가 잘 갖춰지면 **`git push` 한 번으로 운영까지 반영**되는 흐름이 만들어집니다 — 운영 사고를 줄이고, 회복도 빨라집니다.

---

## 2.19 로깅과 모니터링

### 2.19.1 로그

서버가 남기는 실행 기록입니다. **레벨로 중요도를 구분**합니다.

| 레벨 | 용도 |
|------|------|
| DEBUG | 개발 중 디버깅 (운영에서는 보통 끔) |
| INFO | 일반 동작 기록 (요청 처리, 사용자 가입 등) |
| WARNING | 주의가 필요한 상황 (재시도 발생 등) |
| ERROR | 처리 가능한 오류 발생 |
| CRITICAL | 심각한 오류 (서비스가 위태로움) |

> **`print()` 대신 `logging`을 쓰는 이유**: 로그 레벨로 운영/개발 환경에서 출력량을 조절할 수 있고, 시간·모듈명 같은 메타정보가 자동으로 붙으며, 외부 모니터링 도구(Datadog, Sentry 등)와 쉽게 연동됩니다. FastAPI는 표준 `logging`을 그대로 씁니다.

이 가이드에서는 처음에는 표준 `logging` 모듈로 시작하고, 12장에서 더 보기 좋은 `structlog`도 짧게 소개합니다.

### 2.19.2 모니터링

운영 중인 서버의 상태(CPU 사용률, 메모리, 응답 시간, 에러율 등)를 관찰하는 작업입니다. 대표 도구:

- **Prometheus + Grafana**: 오픈소스 기본 조합. 메트릭 수집 + 시각화.
- **Sentry**: 에러를 실시간으로 모아 알려줌. 입문자에게도 매우 유용 — 무료 플랜 충분.
- **Datadog, New Relic**: 상용 통합 모니터링.

이 가이드는 모니터링 자체를 깊이 다루지는 않지만, 09장에서 **헬스 체크 엔드포인트**(`GET /health`)를 만드는 것까지는 진행합니다.

---

## 2.20 에러 처리 관례

REST API에서 에러를 어떻게 표현할지에 대한 흔한 관례입니다.

### 2.20.1 상태 코드 + JSON 본문

성공이든 실패든 **상태 코드와 JSON 본문**으로 표현합니다. 실패 응답에도 일관된 모양을 유지하는 것이 좋습니다.

```json
// 성공 (200 OK)
{
  "id": 42,
  "email": "a@b.com"
}

// 실패 (404 Not Found)
{
  "detail": "User not found"
}

// 검증 실패 (422 Unprocessable Entity) — FastAPI 기본 형식
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

FastAPI는 처리되지 않은 예외에 대해 500을 자동으로 돌려주고, 검증 실패에 대해서는 422를 자동으로 돌려줍니다. 우리는 비즈니스 로직에서 발생하는 의도된 에러(예: 이메일 중복 → 409, 자원 없음 → 404)만 명시적으로 던지면 됩니다.

```python
from fastapi import HTTPException

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 2.20.2 자주 쓰는 에러 매핑

| 상황 | 상태 코드 |
|------|-----------|
| 클라이언트가 보낸 JSON 형식이 깨짐 | 400 Bad Request |
| 토큰 없거나 만료됨 | 401 Unauthorized |
| 토큰은 있지만 권한 없음 | 403 Forbidden |
| 자원이 존재하지 않음 | 404 Not Found |
| 이미 존재하는 자원을 다시 생성 (이메일 중복) | 409 Conflict |
| 필드 검증 실패 | 422 Unprocessable Entity |
| 너무 많은 요청 | 429 Too Many Requests |
| 처리되지 않은 서버 예외 | 500 Internal Server Error |

08장에서 인증 흐름과 함께 이 매핑을 실제로 적용해 봅니다.

---

## 2.21 API 버전 관리

API를 한 번 공개하면, 사용 중인 클라이언트(앱·다른 서비스)가 갑자기 깨지지 않도록 신경 써야 합니다. 그래서 **하위 호환을 깨는 변경**이 생길 때 버전을 새로 매깁니다.

### 2.21.1 버전 표기 위치

흔히 쓰는 세 가지 방식이 있습니다.

- **URL 경로**: `https://api.example.com/v1/users`, `/v2/users` ← **가장 흔하며 입문자에게 권장**
- **헤더**: `Accept: application/vnd.example.v1+json`
- **쿼리 스트링**: `/users?api-version=1`

이 가이드는 **URL 경로 방식**을 씁니다. 가장 간단하고, 브라우저 주소창·`curl` 명령으로도 명확히 보이며, FastAPI에서 `APIRouter(prefix="/v1")`로 깔끔하게 표현됩니다.

### 2.21.2 언제 버전을 올리는가

- **올린다(major bump)**: 기존 응답 모양이 바뀌어 옛 클라이언트가 깨질 때. 필드 이름 변경, 타입 변경, 필수 입력 추가 등.
- **그대로 둔다**: 새 필드를 응답에 **추가만** 하는 경우, 새 엔드포인트를 추가하는 경우, 선택 입력을 추가하는 경우. 옛 클라이언트가 무시하면 그만이므로 버전을 올릴 필요가 없습니다.

> **호환을 잘 지키는 작은 팁**: 응답에서 **필드를 절대 지우지 말고**, 새로운 필드만 추가합니다. 옛 클라이언트가 모르는 새 필드는 알아서 무시해 주는 게 보통입니다.

### 2.21.3 폐기(deprecation) 흐름

큰 변경이 필요하면 보통 다음 흐름을 거칩니다.

1. 새 버전(`/v2`)을 추가로 공개.
2. 기존(`/v1`) 응답에 `Deprecation` / `Sunset` 헤더를 붙여 클라이언트들에게 알림.
3. 사용량을 모니터링하면서 충분한 마이그레이션 기간을 줌.
4. 모든 클라이언트가 옮겨왔을 때 `/v1`을 제거.

10·11장 종합 예제는 단일 버전(`/v1`)으로 출발하지만, 라우터 prefix를 분리해 두므로 나중에 v2를 붙이기 쉬운 구조입니다.

---

## 2.22 테스트 용어

| 용어 | 설명 |
|------|------|
| **단위 테스트(Unit Test)** | 한 함수·클래스 단위로 검증 |
| **통합 테스트(Integration Test)** | 여러 컴포넌트 결합 검증 (예: DB 포함) |
| **E2E (End-to-End)** | 실제 API를 HTTP로 호출해 검증 |
| **픽스처(Fixture)** | 테스트용으로 미리 준비해 두는 데이터·환경 |
| **모킹(Mock)** | 실제 의존성을 가짜로 대체 |
| **테스트 커버리지(Coverage)** | 코드의 어느 비율이 테스트로 실행되는지 |

이 가이드는 Python 표준 테스트 도구인 **`pytest`** 와 FastAPI의 **`TestClient`**(또는 비동기 `httpx.AsyncClient`)를 함께 씁니다. 메모리 안에서 앱을 띄워 실제 HTTP처럼 호출할 수 있어, 별도 서버 실행 없이도 통합 테스트가 가능합니다.

```python
from fastapi.testclient import TestClient
from app.main import app

def test_create_user():
    client = TestClient(app)
    response = client.post("/users", json={"email": "a@b.com"})
    assert response.status_code == 201
    assert response.json()["email"] == "a@b.com"
```

본격적인 테스트 작성은 10·11장 종합 예제에서 다룹니다.

---

## 2.23 자주 혼동되는 용어 짝

| 쌍 | 구분 |
|----|------|
| **URI** vs **URL** | URI가 상위 개념. 실무에선 URL로 통일 |
| **인증(AuthN)** vs **인가(AuthZ)** | "너 누구야?" vs "이거 해도 돼?" |
| **PUT** vs **PATCH** | 전체 교체 vs 부분 수정 |
| **동기** vs **비동기** | 호출 즉시 결과 vs 기다리는 동안 다른 일 처리 |
| **프로세스** vs **스레드** | 메모리 독립 vs 메모리 공유 |
| **세션** vs **쿠키** vs **토큰** | 서버 저장 / 브라우저 저장 / 보통 JWT |
| **401** vs **403** | 로그인 필요 vs 권한 없음 |
| **400** vs **422** | 요청 자체 깨짐 vs 검증 실패 |
| **이미지** vs **컨테이너** | 청사진 vs 실행 인스턴스 |
| **ORM 세션** vs **인증 세션** | DB 작업 묶음 vs 로그인 상태 |
| **동시성** vs **병렬성** | 번갈아 처리 vs 정말 동시에 처리 |

---

## 2.24 이 챕터 요약

- 백엔드는 HTTP 요청을 받아 처리하고 응답을 돌려주는 프로그램이다. HTTP는 stateless이며 요청-응답 한 쌍으로 동작한다.
- HTTP 메시지는 메서드 + 경로 + 헤더 + 바디로 구성되며, 응답은 상태 코드로 결과를 알린다. 401/403/422의 의미를 정확히 구분해 두면 좋다.
- REST API는 URL을 자원(명사), HTTP 메서드를 동작(동사)으로 쓰는 설계 스타일이다. 우리가 만들 것이 그것이다.
- 데이터베이스는 관계형(이 가이드의 대상)과 NoSQL로 나뉘며, ORM(SQLAlchemy 2.0)을 통해 타입 안전하게 다룬다. 트랜잭션·인덱스·N+1 문제는 입문자도 알아둬야 할 핵심 개념이다.
- 인증(누구?)과 인가(권한?)는 별개다. 이 가이드는 JWT 기반 Bearer 토큰으로 인증하고, 비밀번호는 Bcrypt로 해싱한다.
- 환경 변수와 `.env` 파일로 비밀과 환경별 설정을 코드 밖에 둔다. `.env`는 절대 커밋하지 않는다.
- Docker 컨테이너는 개발과 운영 환경의 일관성을 보장한다. 운영에서는 리버스 프록시(Nginx) 뒤에 여러 워커로 띄우는 것이 기본 패턴이다.
- 이 챕터의 용어는 이후 챕터에서 반복 등장하므로, 막히면 이 챕터로 돌아와 찾아보자. 더 짧은 한 줄 정의가 필요하면 [용어 사전](glossary.md)을 펼친다.

<a id="ch03"></a>

# 03. 설치 가이드 (macOS / Linux)

> **이 챕터의 목표**
> - macOS 또는 Linux에 **Python 3.13**과 **uv**를 설치한다.
> - 코드 에디터(VS Code)를 FastAPI 개발에 맞게 세팅한다.
> - 가상환경을 만들고 FastAPI 라이브러리를 설치한 뒤, 가장 짧은 "Hello FastAPI" 한 줄을 띄워 환경이 정상인지 검증한다.
> - Windows에서 따라할 때의 권장 경로(WSL2)를 짧게 안내한다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 30분 ~ 1시간 (Python·VS Code 미설치 시 다운로드 시간 포함)

---

## 3.1 이 챕터에서 깔 도구 한눈에

본격적으로 명령어를 치기 전에, 이 챕터에서 어떤 도구를 어떤 순서로 깔지 큰 그림부터 잡고 가겠습니다.

| 순서 | 도구 | 역할 | 한 줄 설명 |
|------|------|------|------------|
| 1 | **Python 3.13** | 언어 + 표준 런타임 | 우리가 짤 모든 코드를 실행하는 인터프리터 |
| 2 | **uv** | 패키지/가상환경 매니저 | "어떤 라이브러리를 어느 버전으로 깔지"를 빠르게 관리 |
| 3 | **VS Code** | 코드 에디터 | 코드를 짜고 디버깅하는 작업 환경 |
| 4 | (검증용) **FastAPI + Uvicorn** | 1번 검증 | 환경이 잘 깔렸는지 한 줄짜리 앱으로 확인 |

순서가 곧 의존 관계입니다. **Python이 있어야 → uv가 의미가 있고 → 그 위에 FastAPI가 동작합니다.** VS Code는 어느 단계에서 깔든 상관없지만, 이 챕터에서는 마지막에 다룹니다.

> **인터프리터(interpreter)란?** 우리가 작성한 Python 코드(텍스트 파일)를 한 줄씩 읽어 실제로 실행해 주는 프로그램입니다. 우리가 깔 "Python 3.13"이 사실은 이 인터프리터 프로그램입니다. 터미널에서 `python3` 명령을 치면 깔려 있는 인터프리터가 실행되는 것입니다.

> **패키지 매니저(package manager)란?** 외부 라이브러리(예: `fastapi`, `sqlalchemy`)를 인터넷에서 받아 우리 프로젝트에 설치·업그레이드·삭제해 주는 도구입니다. Python에는 표준 도구로 `pip`가, 차세대 도구로 `uv`가 있습니다. 이 가이드는 **uv를 1순위**로 씁니다.

> **에디터(editor)란?** 코드를 작성·편집하는 텍스트 편집기입니다. 메모장도 에디터지만, 개발자가 쓰는 에디터는 코드 자동 완성·문법 색칠·디버깅 같은 기능이 더 많습니다. 이 가이드는 **VS Code**를 권장합니다.

### 3.1.1 왜 이 조합인가

- **Python 3.13**: 2024년 10월 정식 출시된 가장 최신 안정 버전. 새 프로젝트는 가능하면 가장 최신을 쓰는 게 미래 호환에 유리합니다(라이브러리들도 새 버전을 계속 지원하기 때문).
- **uv**: `pip`/`venv`/`pip-tools`가 따로 하던 일을 한 도구로 묶었고, 같은 일을 10~100배 빠르게 합니다. 명령 체계도 일관됩니다.
- **VS Code**: 무료, 가볍고, Python 확장 생태계가 가장 풍부합니다. PyCharm Community도 좋지만, 이 가이드는 VS Code 기준으로 스크린샷·설명을 통일합니다.

> **선택지 안내**: PyCharm Community도 무료이고 충분히 좋습니다. 이미 익숙하면 그대로 써도 됩니다. 본문은 VS Code 기준으로만 적습니다.

---

## 3.2 시스템 요구사항 (2026-04 기준)

| 항목 | 요구사항 |
|------|----------|
| Python | **3.13 이상** (3.12도 동작은 하지만 이 가이드는 3.13 기준) |
| OS | macOS 13 Ventura 이상 / 최신 Ubuntu 22.04, 24.04 LTS 권장 |
| 디스크 여유 공간 | 최소 **5GB** (Python + 가상환경 + 라이브러리들) |
| 메모리 | 4GB 이상 권장 (8GB 이상이면 쾌적) |
| 인터넷 연결 | 라이브러리 다운로드 시 필요 |

### 3.2.1 OS별 권장 경로 한눈에

- **macOS**: Homebrew → Python 3.13 → uv → VS Code 순서
- **Linux (Ubuntu/Debian)**: apt 또는 deadsnakes PPA → Python 3.13 → uv → VS Code 순서
- **Windows**: **가능하면 WSL2(Ubuntu)에서 위 Linux 절차를 따르는 것을 강력 권장.** 순수 Windows 직접 설치도 가능하지만 배포 환경이 거의 다 Linux이므로 처음부터 같은 환경에서 익히는 것이 편합니다.

> **WSL2(Windows Subsystem for Linux 2)란?** Windows 안에서 진짜 Linux(Ubuntu 등)를 거의 그대로 돌릴 수 있게 해 주는 마이크로소프트의 공식 기능입니다. Windows를 쓰면서도 Linux 명령어가 그대로 통하므로, 백엔드 학습에는 거의 항상 WSL2 쪽이 편합니다. 설치는 [공식 안내](https://learn.microsoft.com/ko-kr/windows/wsl/install)를 참고하세요. (PowerShell 관리자에서 `wsl --install` 한 줄로 보통 됩니다.)

---

## 3.3 macOS — Python 3.13 설치

### 3.3.1 단계 1 — Homebrew 확인 또는 설치

**Homebrew**는 macOS에서 명령어 한 줄로 외부 프로그램을 설치해 주는 패키지 매니저입니다. 우리는 Python을 깔 때 Homebrew를 사용합니다.

> **Homebrew란?** macOS·Linux용 패키지 매니저. `brew install <이름>` 한 줄로 외부 소프트웨어를 설치할 수 있게 해 줍니다. 이 가이드는 macOS 사용자에게 Homebrew를 전제로 합니다.

이미 깔려 있는지 먼저 확인합니다.

```bash
brew --version
```

`Homebrew 4.x.x` 또는 `Homebrew 5.x.x` 같은 출력이 나오면 다음 단계로. `command not found: brew`가 나오면 아래 한 줄로 설치합니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 후 Apple Silicon(M1/M2/M3 등) Mac에서는 PATH 설정을 한 번 해 줘야 `brew` 명령이 잡힙니다.

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

> **PATH란?** 터미널이 명령을 받았을 때 "이 이름의 실행 파일을 어느 폴더에서 찾아야 하지?"를 정해주는 환경 변수입니다. PATH에 등록된 폴더 순서대로 뒤져서 찾습니다. PATH에 안 들어 있는 폴더의 명령어는 `command not found`가 됩니다.

> **`~/.zshrc`란?** macOS 기본 셸인 zsh이 시작될 때마다 자동으로 읽는 설정 파일입니다. 여기에 환경 변수, 별칭(alias) 등을 적어두면 셸을 새로 켤 때마다 적용됩니다. `~`는 홈 디렉터리(예: `/Users/yourname`)를 뜻합니다.

다시 확인해서 버전이 출력되면 OK.

```bash
brew --version
```

### 3.3.2 단계 2 — Python 3.13 설치

```bash
brew install python@3.13
```

설치가 끝나면 다음 명령으로 확인합니다.

```bash
python3.13 --version
```

다음과 같이 나오면 성공입니다(마이너 버전 숫자는 시점에 따라 다릅니다).

```
Python 3.13.x
```

### 3.3.3 단계 3 — `python` / `python3` / `python3.13` 정리

Python 입문자를 가장 자주 헷갈리게 하는 부분입니다. **macOS의 시스템에는 옛날 Python 3가 이미 깔려 있을 수 있고**, 우리가 새로 깐 3.13이 그 위에 별도로 추가된 상태가 됩니다.

확인해 보겠습니다.

```bash
which python3.13
# 예상: /opt/homebrew/bin/python3.13  (Apple Silicon)
# 또는: /usr/local/bin/python3.13     (Intel Mac)

which python3
# 위와 같을 수도, /usr/bin/python3 (시스템 기본)일 수도

which python
# command not found 가 가장 흔합니다
```

이 가이드의 약속은 다음과 같습니다.

- **`python3.13`** : 우리가 깐 새 인터프리터를 명확히 가리킬 때
- **`python3`** : 가상환경을 켠 뒤(=`.venv` 활성화 후)에는 그 안의 Python을 가리키는 별칭이 되므로 안전
- **`python`** : 가상환경 안에서만 가끔 통함. 시스템 전역에서는 보통 안 통함

**가상환경을 켠 상태에서는 `python`/`python3`/`python3.13`이 모두 같은 것을 가리킵니다.** 그래서 가상환경에 들어간 뒤에는 그냥 `python`만 써도 안전합니다. 가상환경 밖에서 명시적으로 3.13을 쓸 때는 `python3.13`을 쓰는 게 가장 명확합니다.

> **가상환경(virtual environment)이란?** 프로젝트마다 라이브러리를 격리해 두는 작은 "독립된 Python 공간"입니다. 시스템 Python을 더럽히지 않고 프로젝트별로 다른 라이브러리·버전을 쓸 수 있게 해 줍니다. 자세한 내용은 [용어 사전](glossary.md#가상환경-virtual-environment)에 있습니다.

### 3.3.4 (대안) pyenv로 여러 Python 버전을 갈아끼우고 싶다면

여러 프로젝트가 다른 Python 버전을 요구할 때 쓰는 도구가 **pyenv**입니다. Node.js의 nvm, Ruby의 rbenv와 비슷합니다. 본 가이드의 권장 경로는 아니지만 짧게 적어 둡니다.

```bash
brew install pyenv
pyenv install 3.13
pyenv global 3.13
```

`~/.zshrc`에 다음을 추가해야 셸이 pyenv의 Python을 우선 찾습니다.

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
```

> **참고**: 이 가이드는 Homebrew로 깐 Python 3.13 하나를 그대로 씁니다. pyenv는 "여러 버전을 자주 갈아끼울 일이 생기면 그때" 도입해도 늦지 않습니다.

---

## 3.4 Linux (Ubuntu/Debian) — Python 3.13 설치

Ubuntu·Debian 계열을 기준으로 설명합니다. 다른 배포판(Fedora·Arch 등)은 패키지 매니저 명령(`dnf`, `pacman`)만 다르고 흐름은 같습니다.

### 3.4.1 단계 1 — apt로 시도

먼저 OS의 기본 패키지 매니저인 `apt`로 3.13이 바로 깔리는지 시도합니다.

```bash
sudo apt update
sudo apt install -y python3.13 python3.13-venv
```

설치 후 확인:

```bash
python3.13 --version
```

`Python 3.13.x`가 나오면 3.6 절(uv 설치)로 넘어가도 됩니다. **`E: Unable to locate package python3.13`이 나오면** OS의 기본 저장소에 아직 3.13이 없다는 뜻입니다(특히 Ubuntu 22.04 LTS나 Debian 12에서 그럴 수 있습니다). 이때는 다음 단계로.

### 3.4.2 단계 2 — deadsnakes PPA 추가 (Ubuntu)

**deadsnakes**는 Ubuntu 사용자들이 가장 많이 쓰는 "최신 Python을 제공하는 비공식 저장소"입니다. 한 번 등록해 두면 `apt`로 새 Python 버전을 깔 수 있습니다.

> **PPA(Personal Package Archive)란?** Ubuntu에서 사용자·단체가 직접 만드는 작은 패키지 저장소입니다. 공식 저장소에는 없는 새 버전이나 도구를 PPA를 통해 추가로 받을 수 있습니다. deadsnakes는 그중에서 Python 전용으로 잘 관리되는 PPA입니다.

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

확인:

```bash
python3.13 --version
```

### 3.4.3 (대안) pyenv로 직접 컴파일

Debian이거나 어떤 사정으로 PPA를 못 쓰는 환경이라면 pyenv가 가장 확실합니다.

```bash
# 빌드에 필요한 시스템 의존성 (Ubuntu/Debian)
sudo apt install -y \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# pyenv 설치
curl https://pyenv.run | bash
```

`pyenv.run` 스크립트가 알려주는 대로 셸 설정 파일(`~/.bashrc` 또는 `~/.zshrc`)에 두세 줄을 추가하고 셸을 다시 켭니다. 그 다음:

```bash
pyenv install 3.13
pyenv global 3.13
python3.13 --version
```

> **빌드가 오래 걸려요**: pyenv는 Python을 소스에서 직접 컴파일하므로 5~15분 걸립니다. 한 번만 하면 됩니다.

---

## 3.5 Windows — WSL2 한 단락 안내

이 가이드는 macOS/Linux 전제이므로, Windows는 **WSL2(Ubuntu)**를 강하게 권장합니다.

1. **WSL2 설치** — 관리자 권한 PowerShell에서 한 줄.
   ```powershell
   wsl --install
   ```
   설치가 끝나면 재부팅 후 Ubuntu 셸이 한 번 자동으로 뜹니다. 사용자 이름·비밀번호를 만들면 준비 완료.

2. **그 다음**부터는 위 **3.4 Linux 절차**를 그대로 따라 하면 됩니다.

3. (선택) **VS Code의 "WSL" 확장**을 설치하면, Windows의 VS Code에서 WSL 안의 Linux 파일을 직접 열고 편집·디버깅할 수 있습니다. 거의 모든 Windows + Python 백엔드 개발자가 이렇게 씁니다.

> **순수 Windows에 직접 설치해도 되나요?** 됩니다. [python.org](https://www.python.org/downloads/windows/)에서 공식 인스톨러를 받아 설치하고, 설치 화면에서 **"Add python.exe to PATH"**를 반드시 체크하세요. uv도 Windows용 설치 명령이 있습니다(공식 문서 참고). 다만 이 가이드의 명령어 예시(`source .venv/bin/activate` 등)는 macOS/Linux 셸 기준이라 Windows PowerShell에서는 일부 명령이 다릅니다(예: `.venv\Scripts\activate`). 학습 단계에서 그런 차이까지 신경 쓰는 것은 부담스러우므로 WSL2를 권합니다.

---

## 3.6 uv 설치

이제 본격적으로 패키지 매니저 **uv**를 깝니다.

### 3.6.1 왜 uv인가 (다시 한 번)

`pip`도 충분히 잘 동작합니다. 하지만 백엔드 프로젝트가 커지면 다음과 같은 작업이 자주 일어납니다.

1. 가상환경 만들기 (`python -m venv .venv`)
2. 가상환경 켜기 (`source .venv/bin/activate`)
3. 라이브러리 설치 (`pip install fastapi`)
4. 설치된 라이브러리 목록 잠그기 (`pip freeze > requirements.txt`)
5. 다른 컴퓨터에서 똑같이 복원 (`pip install -r requirements.txt`)

`uv`는 이 다섯 단계를 **한 도구로 일관되게**, 그리고 **압도적으로 빠르게** 처리합니다. 명령 체계도 더 간결합니다(`uv add fastapi` 한 줄).

> **uv와 pip의 관계는?** 같은 일을 하는 두 도구입니다. uv는 안에서 pip이 하던 일을 직접 다시 짠 것에 가깝습니다. `uv pip install ...`처럼 pip의 명령을 그대로 흉내낼 수도 있고, `uv add ...`처럼 더 현대적인 명령도 제공합니다. 자세한 비교는 [용어 사전의 pip와 uv 표](glossary.md#pip-와-uv-의-관계)를 참고하세요.

### 3.6.2 설치 — macOS / Linux 공통

[공식 문서](https://docs.astral.sh/uv/getting-started/installation/)가 권장하는 한 줄 설치 명령입니다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 스크립트가 셸 설정 파일(`~/.zshenv`, `~/.bashrc` 등)에 PATH를 자동으로 추가해 주지만, **현재 켜져 있는 터미널에는 자동 적용되지 않습니다.** **터미널을 한 번 닫았다 다시 열거나** 다음 한 줄을 실행해 주세요.

```bash
# macOS (zsh): 보통 ~/.zshenv 에 추가됩니다
source ~/.zshenv

# 위가 안 되면 ~/.zshrc 도 시도해 봅니다
source ~/.zshrc

# Linux (bash): ~/.bashrc 에 추가됩니다
source ~/.bashrc
```

> **그래도 `uv: command not found`가 뜨면** 새 터미널을 여는 게 가장 확실합니다. uv의 기본 설치 경로는 `~/.local/bin/uv`이며, 3.11.4 절의 트러블슈팅을 참고하세요.

> **위 명령이 인터넷에서 스크립트를 받아 바로 실행하는 게 안전한가요?** 일반적으로 신뢰할 수 있는 도메인(`astral.sh`)의 공식 설치 방법입니다. 더 보수적인 환경(회사·학교 정책)에서는 [GitHub 릴리스](https://github.com/astral-sh/uv/releases)에서 바이너리를 직접 받아 PATH에 두는 방식, 또는 `pipx install uv`도 가능합니다.

### 3.6.3 설치 확인

```bash
uv --version
```

`uv 0.x.x` 같은 출력이 나오면 성공입니다.

```bash
uv python list
```

이 명령은 uv가 인식한 Python 인터프리터 목록을 보여줍니다. 우리가 위에서 깐 3.13이 보이면 환경이 깔끔하게 잡힌 겁니다.

---

## 3.7 uv로 처음 가상환경 만들고 FastAPI 설치하기

이번 절에서는 **테스트용 폴더**를 하나 만들고, uv로 가상환경 + 라이브러리 설치까지 진행합니다. 04장에서 본격적인 첫 프로젝트를 다시 만들 것이므로 여기서는 **환경이 잘 동작하는지 확인**하는 데 의의가 있습니다.

### 3.7.1 폴더 만들기

```bash
mkdir hello-fastapi
cd hello-fastapi
```

홈 디렉터리든 데스크톱이든 어디에 만들든 상관없습니다. 이 가이드에서는 보통 홈(`~`) 아래에 `projects/` 같은 작업 폴더를 두고 그 안에 둡니다.

### 3.7.2 uv 프로젝트 초기화

```bash
uv init
```

이 명령은 현재 폴더를 uv 프로젝트로 만듭니다. 실행 직후 폴더에 다음 파일들이 생깁니다.

- **`pyproject.toml`** — 프로젝트 메타데이터(이름·Python 버전·의존성 라이브러리 목록)를 적는 표준 파일.
- **`.python-version`** — 이 프로젝트가 쓸 Python 버전을 적어둔 작은 텍스트 파일.
- **`README.md`** — 빈 README. 지금은 신경 안 써도 됨.
- **`hello.py`** 또는 **`main.py`** (uv 버전에 따라 이름이 다를 수 있음) — 짧은 예시 스크립트.

> **`pyproject.toml`이란?** 현대 Python 프로젝트의 **표준 설정 파일**입니다. 옛날에는 `setup.py`, `requirements.txt`가 따로 했던 일을 한 파일로 모았습니다. 이름·버전·의존성·빌드 설정 등이 다 여기 들어갑니다. uv뿐 아니라 pip·poetry·ruff 등 거의 모든 현대 Python 도구가 이 파일을 읽습니다.

`pyproject.toml`을 한 번 열어 보면 대략 이렇게 생겼을 겁니다(uv 버전에 따라 약간 다를 수 있음).

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

`requires-python = ">=3.13"` 줄이 보입니다. uv는 이 줄을 읽고 "이 프로젝트는 Python 3.13 이상이 필요하구나"를 압니다.

### 3.7.3 FastAPI와 Uvicorn 추가

이제 라이브러리를 추가합니다. `uv add` 명령은 **자동으로 가상환경을 만들고**(없으면) **거기에 라이브러리를 깔고** **잠금 파일을 만듭니다.** 한 번에 다 합니다.

```bash
uv add fastapi "uvicorn[standard]"
```

> **`uvicorn[standard]`의 대괄호는 뭔가요?** "추가 옵션 묶음"을 뜻하는 표기입니다. `uvicorn` 자체만 받으면 핵심 기능만 들어오고, `uvicorn[standard]`로 받으면 자주 쓰는 부가 라이브러리(예: 자동 리로드를 위한 `watchfiles`, 빠른 HTTP 파서 `httptools`, 더 빠른 이벤트 루프 `uvloop` 등)가 함께 깔립니다. 우리는 자동 리로드를 쓸 거라서 `[standard]`를 붙입니다. 따옴표는 일부 셸이 대괄호를 잘못 해석하지 않게 막아주는 안전장치입니다.

명령이 끝나면 폴더 구성은 다음처럼 확장됩니다.

```
hello-fastapi/
├── .venv/                ← 새로 생긴 "가상환경 폴더"
├── .python-version
├── pyproject.toml        ← dependencies 항목이 갱신됨
├── uv.lock               ← 새로 생긴 "잠금 파일"
├── README.md
└── hello.py (또는 main.py)
```

각 파일·폴더가 무엇을 의미하는지 정리합니다.

- **`.venv/`** — 이 프로젝트만의 격리된 Python 공간. 안에 Python 인터프리터의 복사본과 깔린 라이브러리들이 들어 있습니다. **이 폴더는 git에 올리지 않습니다.**(자동 생성되므로 다시 만들면 됨)
- **`uv.lock`** — 이번에 깔린 라이브러리들의 **정확한 버전과 해시값**을 기록한 잠금 파일. 다른 컴퓨터에서 `uv sync`를 돌리면 정확히 같은 버전들이 다시 깔립니다. 이 파일은 git에 올립니다.
- **`pyproject.toml`의 `dependencies`** — 위 명령으로 우리가 의도한 의존성 목록(`fastapi`, `uvicorn[standard]`)이 적힙니다. 사람이 읽고 편집하는 파일입니다.

> **잠금 파일(lock file)이란?** "이 프로젝트는 정확히 이 버전들로 동작한다"고 못 박아 두는 파일입니다. 협업 시 "내 컴퓨터에선 되는데"를 막아 줍니다. uv는 `uv.lock`, npm은 `package-lock.json`, Cargo는 `Cargo.lock` 등 비슷한 개념입니다.

### 3.7.4 가상환경 켜기 / 안 켜기

`uv add` 자체는 가상환경을 켤 필요가 없습니다. uv가 알아서 `.venv/`를 보고 거기에 깝니다. 하지만 **앞으로 `python` 명령을 직접 칠 일이 있다면 가상환경을 켜야** 그 안의 Python이 호출됩니다.

```bash
source .venv/bin/activate
```

켜지면 프롬프트 앞에 `(hello-fastapi)` 같은 표시가 붙습니다. 이 상태에서 `python --version`을 치면 프로젝트의 3.13이 나옵니다.

끄고 싶으면 그냥 `deactivate`.

> **uv를 쓰면 거의 가상환경을 직접 켤 일이 없습니다.** `uv run python ...`, `uv run uvicorn ...`, `uv add ...`처럼 **`uv run` 접두사**를 붙이면 uv가 알아서 가상환경 안에서 명령을 실행해 줍니다. 본 가이드의 표준 패턴은 `uv run`입니다.

### 3.7.5 깔린 것 확인

```bash
uv pip list
```

이 명령은 현재 가상환경에 깔린 라이브러리 목록을 보여줍니다. 다음 같은 출력이 나오면 성공입니다(버전 숫자는 시점에 따라 다름).

```
Package           Version
----------------- --------
annotated-types   0.7.0
anyio             4.x.x
fastapi           0.115.x
pydantic          2.x.x
pydantic_core     2.x.x
sniffio           1.3.x
starlette         0.x.x
typing_extensions 4.x.x
uvicorn           0.30.x
...
```

`fastapi`와 `uvicorn`이 보이면 환경 구축은 끝입니다.

---

## 3.8 (대체 절차) pip + venv로 똑같이 하기

회사·학교 PC 정책으로 외부 설치 스크립트를 못 돌리는 등 **uv를 쓸 수 없는 환경**을 위한 대체 절차입니다. 그 외의 경우라면 위의 uv 절차를 그대로 따르는 것을 권장합니다.

```bash
# 1) 폴더 만들기
mkdir hello-fastapi-pip
cd hello-fastapi-pip

# 2) 가상환경 만들기 (.venv 폴더가 생김)
python3.13 -m venv .venv

# 3) 가상환경 켜기
source .venv/bin/activate
# 켜진 뒤로는 python, pip이 모두 .venv 안의 것을 가리킵니다

# 4) FastAPI 설치
pip install --upgrade pip
pip install fastapi "uvicorn[standard]"

# 5) 깔린 라이브러리를 텍스트로 잠그기
pip freeze > requirements.txt
```

`requirements.txt`는 `uv.lock`보다 **간단하지만 정밀도가 떨어집니다**(예: 해시 검증이 없음). 작은 학습 프로젝트에선 충분합니다.

다른 사람이 같은 프로젝트를 받아서 환경을 복원할 때:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **언제 uv 대신 pip + venv를 써야 하나요?**
> - 회사·학교 보안 정책이 외부 설치 스크립트(curl | sh) 실행을 막을 때
> - 이미 운영 중인 프로젝트가 `requirements.txt`/`pip` 흐름으로 굳어져 있을 때
> - **그 외**: 거의 모든 새 프로젝트에서 uv를 권장.

---

## 3.9 VS Code 환경 세팅

### 3.9.1 VS Code 설치

[code.visualstudio.com](https://code.visualstudio.com/)에서 OS에 맞는 빌드를 받아 설치합니다.

- **macOS**: `.zip`을 받아 압축을 풀고 `Visual Studio Code.app`을 `/Applications`로 끌어다 둡니다. (또는 `brew install --cask visual-studio-code`)
- **Linux (Ubuntu/Debian)**: `.deb` 파일을 받아 `sudo apt install ./code_*.deb`로 설치하거나, `snap install code --classic`.
- **WSL2**: Windows에서 VS Code를 설치하면 WSL 확장을 통해 Linux 파일에 그대로 접근할 수 있습니다.

설치 후 터미널에서 `code` 명령이 통하는지 확인해 둡니다(없으면 VS Code의 명령 팔레트에서 "Shell Command: Install 'code' command in PATH"를 한 번 실행).

```bash
code --version
```

### 3.9.2 추천 확장 (Extensions)

VS Code의 좌측 막대에서 사각형 4개 모양의 **Extensions** 아이콘을 누르고, 다음 세 개를 검색해 설치합니다. **확장 이름과 발행자(Publisher)를 정확히** 맞춰 설치하세요(비슷한 이름의 다른 확장이 많습니다).

| 확장 이름 | 발행자 (Publisher) | 역할 |
|-----------|--------------------|------|
| **Python** | **Microsoft** | 파이썬 언어의 핵심 지원(인터프리터 선택, 디버깅, 실행) |
| **Pylance** | **Microsoft** | 빠른 자동 완성·타입 분석 (Python 확장과 함께 동작) |
| **Ruff** | **Astral Software** | 매우 빠른 린터·포매터(코드 스타일 자동 정리) |

> **린터(linter)란?** 코드의 잠재적 문제(쓰지 않는 변수, 잘못된 들여쓰기, 위험한 패턴 등)를 자동으로 잡아주는 도구입니다.
>
> **포매터(formatter)란?** 코드의 스타일(들여쓰기·줄바꿈 위치·따옴표 종류 등)을 약속한 규칙대로 자동 정렬해 주는 도구입니다. ruff는 두 역할을 한 번에 합니다.

추가로 **선택적**으로 다음도 자주 깝니다.

- **GitLens** (eamodio) — git 히스토리를 코드 옆에 보여줌
- **Docker** (Microsoft) — 09장 배포에서 유용
- **Even Better TOML** (tamasfe) — `pyproject.toml` 편집 시 자동 완성

### 3.9.3 가상환경 인터프리터 선택

위에서 만든 `hello-fastapi/` 폴더를 VS Code로 엽니다.

```bash
cd hello-fastapi
code .
```

**중요한 한 단계**: VS Code 우측 하단(또는 명령 팔레트 `Cmd+Shift+P` / `Ctrl+Shift+P` → `Python: Select Interpreter`)에서 **인터프리터를 `.venv`로 지정**해 줍니다. 보통 자동으로 `.venv` 안의 Python이 후보로 뜹니다. 거기를 골라 주면 VS Code가 다음을 그 가상환경 기준으로 동작시킵니다.

- 자동 완성·타입 검사(Pylance)
- 통합 터미널을 열 때 자동으로 가상환경 활성화
- "Run Python File" 시 그 인터프리터로 실행

> **이 단계를 빠뜨리면** Pylance가 `import fastapi`를 빨간 줄로 표시할 수 있습니다. "라이브러리는 깔렸는데 VS Code가 다른 Python을 보고 있는" 상태입니다.

### 3.9.4 권장 settings.json

프로젝트 루트에 `.vscode/settings.json`을 두면 그 프로젝트에만 적용되는 VS Code 설정을 만들 수 있습니다. 다음 정도면 충분합니다.

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.fixAll": true
}
```

이 설정은 다음을 의미합니다.

- 이 프로젝트에서는 `.venv` 안의 Python을 인터프리터로 쓴다.
- 새 터미널을 열 때 가상환경을 자동 활성화한다.
- `.py` 파일을 저장할 때 ruff로 자동 포매팅 + import 정리 + 자동 수정 가능한 린트 오류 정리.

> **WSL2 사용자**: `python.defaultInterpreterPath`의 경로 구분자는 그대로 `/`를 씁니다(WSL 안은 Linux이므로). Windows 경로 표기(`\`)를 쓰지 마세요.

### 3.9.5 PyCharm Community도 무난

VS Code가 부담스럽다면 [PyCharm Community](https://www.jetbrains.com/pycharm/download/)도 무료이고, Python 프로젝트 인식이 자동입니다. 가상환경도 대체로 알아서 잡아 줍니다. 이 가이드의 본문 캡처와 단축키는 VS Code 기준으로만 적습니다.

---

## 3.10 새너티 체크 — 한 줄 FastAPI 앱 띄워보기

이제 환경이 정말 잘 깔렸는지 **가장 짧은 FastAPI 앱**으로 검증합니다. 04장에서 본격적으로 같은 작업을 다시 하므로 여기서는 가볍게.

> **새너티 체크(sanity check)란?** 본격적인 작업 전에 "기본적인 것이 제대로 돌아가는가?"를 빠르게 확인하는 절차입니다. 의학·공학에서 두루 쓰는 표현이며, 우리는 "환경이 깨지지 않았는지"를 1분 안에 확인하려는 것입니다.

### 3.10.1 `app.py` 작성

`hello-fastapi/` 폴더 안에 `app.py` 파일을 **새로** 만들어 다음 내용을 넣습니다. (uv가 자동으로 만들어 둔 `hello.py` / `main.py`는 그대로 두어도 됩니다 — 우리는 새로 만든 `app.py`만 사용합니다.)

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}
```

겨우 다섯 줄입니다. 이 코드는 다음을 합니다.

1. `FastAPI` 클래스를 가져온다.
2. `app`이라는 이름으로 FastAPI 앱을 하나 만든다.
3. **`/` 경로로 GET 요청이 들어오면** `hello()` 함수가 처리하도록 등록한다.
4. 응답으로 `{"message": "Hello, FastAPI!"}` 라는 JSON을 돌려준다.

> **`@app.get("/")` 이 줄은 뭔가요?** **데코레이터**라고 부르는 표기로, "이 바로 아래의 함수를 GET / 요청 처리기로 등록해라"는 명령입니다. FastAPI 라우팅의 기본 단위입니다. [용어 사전 — 데코레이터](glossary.md#데코레이터-decorator)도 참고.

### 3.10.2 서버 띄우기

다음 명령으로 띄웁니다(uv 권장 경로 / pip 경로 둘 다 적습니다).

**uv 경로 (권장):**

```bash
uv run uvicorn app:app --reload
```

**pip + venv 경로:**

```bash
# 가상환경이 켜져 있어야 함
source .venv/bin/activate
uvicorn app:app --reload
```

`uvicorn app:app` 부분은 "**`app.py` 파일 안의 `app` 객체**를 띄우라"는 뜻입니다. 콜론 앞이 파일명, 뒤가 변수명입니다. `--reload`는 코드를 수정하면 서버가 자동으로 재시작되게 해 주는 개발용 옵션입니다.

성공하면 다음 비슷한 로그가 출력됩니다.

```
INFO:     Will watch for changes in these directories: ['/Users/.../hello-fastapi']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...] using WatchFiles
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.10.3 브라우저에서 확인

다음 두 주소를 열어 봅니다.

1. http://127.0.0.1:8000/ — `{"message":"Hello, FastAPI!"}` JSON이 보입니다.
2. http://127.0.0.1:8000/docs — **자동 생성된 Swagger UI**가 보입니다. `GET /` 엔드포인트가 등록돼 있고, 펼치면 "Try it out" 버튼으로 직접 호출도 됩니다.

또는 다른 터미널에서 `curl`로 확인해도 좋습니다.

```bash
curl http://127.0.0.1:8000/
# 응답: {"message":"Hello, FastAPI!"}
```

확인이 끝나면 첫 터미널에서 `Ctrl+C`로 서버를 종료합니다. 테스트 폴더는 04장에서 다시 만들 거라 지워도 되고, 그대로 둬도 됩니다.

```bash
# 만약 지우고 싶으면
cd ..
rm -rf hello-fastapi
```

> **04장 예고**: 다음 챕터에서 같은 흐름을 처음부터 다시 만들면서 이번엔 라우트를 더 추가하고, 폴더 구조를 잡고, 자동 문서를 자세히 살펴봅니다.

---

## 3.11 OS·환경별 자주 발생하는 문제와 해결

### 3.11.1 macOS — `command not found: brew`

Homebrew가 설치되지 않았거나, 설치는 됐는데 PATH가 안 잡힌 상태입니다.

- 설치 자체가 안 된 경우: 3.3.1의 설치 한 줄을 다시.
- 설치는 됐는데 PATH가 안 잡힌 경우(Apple Silicon Mac에서 흔함):
  ```bash
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
  source ~/.zshrc
  ```

### 3.11.2 macOS / Linux — `command not found: python3.13`

Python 3.13이 깔리지 않았거나, 깔린 곳이 PATH에 없는 상태입니다.

```bash
# 어디 있는지 직접 찾아보기
ls /opt/homebrew/bin/python3.13   # macOS Apple Silicon
ls /usr/local/bin/python3.13      # macOS Intel
ls /usr/bin/python3.13            # 일부 Linux
which python3                     # 다른 버전이라도 잡히는지
```

대부분은 위 3.3 / 3.4 절을 다시 따라 하면 해결됩니다. 시스템에 옛날 Python(예: 3.10)만 있고 3.13이 정말 없을 수도 있으니 버전 확인을 명확히 합니다.

### 3.11.3 Linux — `python3.13: not found` (Ubuntu LTS의 기본 Python 버전)

Ubuntu 22.04 LTS의 기본 저장소에는 보통 Python 3.10이, 24.04 LTS에는 보통 3.12가 들어 있습니다. 그래서 `apt install python3.13`이 곧장 안 통할 때가 있습니다. 해결책은 두 가지.

1. **deadsnakes PPA 추가** (3.4.2 절차)
2. **pyenv 사용** (3.4.3 절차)

> **시스템 Python을 함부로 바꾸지 마세요**: Ubuntu 시스템 자체가 기본 Python 3.x에 의존하는 부분이 있어서, 시스템 Python 자체를 갈아끼우면 OS가 망가질 수 있습니다. 우리는 항상 **시스템 Python과 별개로 새 Python을 추가**해 쓰는 방식을 씁니다. (위 두 방법 모두 그렇게 동작합니다.)

### 3.11.4 `uv: command not found` (uv 설치 후에)

설치 스크립트는 PATH 라인을 셸 설정 파일에 추가하지만, **현재 켜진 셸에는 자동 적용되지 않습니다.** 새 터미널을 열거나, 다음 한 줄을 시도합니다.

```bash
source ~/.zshenv     # macOS (zsh): uv 설치 스크립트가 보통 이 파일을 갱신
source ~/.zshrc      # macOS 보조
source ~/.bashrc     # 대부분의 Linux
```

여전히 안 통하면 직접 PATH를 확인합니다(uv의 기본 설치 경로는 `~/.local/bin/uv`).

```bash
ls ~/.local/bin/uv
echo $PATH | tr ':' '\n' | grep local
```

### 3.11.5 가상환경에서 `pip install`이 시스템에 깔리는 것 같음

가상환경을 켜는 걸 깜빡한 경우가 압도적으로 많습니다. 프롬프트 앞에 `(hello-fastapi)` 같은 표시가 있는지 다시 확인하세요. uv 사용자라면 그냥 `uv add ...`나 `uv run ...`을 쓰면 이 문제가 안 생깁니다.

### 3.11.6 8000번 포트가 이미 사용 중

```
ERROR: [Errno 48] Address already in use
```

다른 프로세스(또는 이전에 띄워두고 안 끈 uvicorn)가 8000을 잡고 있는 경우입니다.

```bash
# 8000 사용 중인 프로세스 찾기 (macOS / Linux)
lsof -i :8000
# 또는
sudo lsof -i :8000
```

원인 프로세스를 찾아 종료하거나, 다른 포트로 띄웁니다.

```bash
uv run uvicorn app:app --reload --port 8001
```

### 3.11.7 VS Code가 `import fastapi`를 빨간 줄로 표시함

라이브러리는 깔렸는데 VS Code가 다른 인터프리터(예: 시스템 Python)를 보고 있는 상태입니다. **`Cmd/Ctrl+Shift+P → Python: Select Interpreter`**에서 `.venv` 안의 Python을 골라 주면 해결됩니다. 그래도 안 되면 VS Code 창을 한 번 닫았다가 다시 열어 보세요.

### 3.11.8 Windows에서 `source .venv/bin/activate`가 안 통함

WSL2를 쓰지 않고 PowerShell·CMD에서 직접 작업 중이라면 활성화 명령이 다릅니다.

```powershell
.venv\Scripts\Activate.ps1   # PowerShell
.venv\Scripts\activate.bat   # CMD
```

이 가이드의 명령 표기는 macOS/Linux 기준이므로, Windows는 가능하면 **WSL2(Ubuntu)**에서 작업하길 다시 한 번 권장합니다.

---

## 3.12 설치 완료 체크리스트

다음이 모두 성공하면 다음 챕터로 넘어갈 준비가 끝난 것입니다.

- [ ] `python3.13 --version` → `Python 3.13.x` 출력
- [ ] `uv --version` → 버전 출력 (uv를 못 쓰는 환경이면 `pip --version` 출력으로 대체)
- [ ] `code --version` → VS Code 설치 확인
- [ ] VS Code에 **Python**, **Pylance**, **Ruff** 확장이 깔려 있다
- [ ] `mkdir hello-fastapi && cd hello-fastapi && uv init && uv add fastapi "uvicorn[standard]"` 가 에러 없이 끝남
- [ ] `app.py`에 5줄짜리 FastAPI 앱을 작성하고 `uv run uvicorn app:app --reload`로 띄움
- [ ] 브라우저에서 `http://127.0.0.1:8000/`이 JSON을 돌려줌
- [ ] 브라우저에서 `http://127.0.0.1:8000/docs`가 Swagger UI를 보여줌

위가 다 통과하면 환경 구축은 완료입니다. **다음 챕터에서 같은 흐름을 더 단단하게 다시 만들면서 라우트와 폴더 구조까지 정리합니다.**

---

## 3.13 이 챕터 요약

- Python 3.13 + uv + VS Code, 이 세 가지가 이 가이드의 표준 스택이다.
- macOS는 Homebrew로(`brew install python@3.13`), Ubuntu는 `apt`나 deadsnakes PPA로 Python 3.13을 깐다. Windows는 WSL2(Ubuntu)에서 위 Linux 절차를 따른다.
- uv는 한 줄(`curl -LsSf https://astral.sh/uv/install.sh | sh`)로 설치하고, 가상환경·라이브러리·잠금 파일을 한 도구로 관리한다.
- 권장 흐름은 `uv init` → `uv add fastapi "uvicorn[standard]"` → `uv run uvicorn app:app --reload`. 회사·학교 정책 등으로 uv를 못 쓰면 `python3.13 -m venv .venv` + `pip install`이 대체 절차다.
- VS Code에 **Python(Microsoft)**, **Pylance(Microsoft)**, **Ruff(Astral Software)** 확장을 깔고, `Python: Select Interpreter`로 `.venv`를 가리키게 한다.
- `app.py`에 다섯 줄짜리 FastAPI 앱을 만들고 `/`와 `/docs`가 모두 응답하면, 환경 구축은 끝난 것이다.

<a id="ch04"></a>

# 04. 첫 프로젝트 — Hello FastAPI

> **이 챕터의 목표**
> - 03장에서 5줄짜리 새너티 체크로 띄웠던 앱을, 본격적인 **첫 프로젝트** 형태로 다시 만든다.
> - `uv init`으로 표준 폴더 구조를 갖춘 프로젝트를 생성한다.
> - `pyproject.toml`이 무엇이고 어떤 정보가 들어 있는지 한 줄씩 읽어낼 수 있다.
> - `app/main.py`를 만들고, FastAPI 앱의 가장 작은 코드를 한 줄 한 줄 풀어 이해한다.
> - `uv run uvicorn app.main:app --reload` 명령의 각 부분이 무엇을 하는지 안다.
> - 자동 생성되는 `/docs`, `/redoc`, `/openapi.json` 세 페이지의 차이를 안다.
> - 경로 매개변수(`GET /hello/{name}`)와 Pydantic 모델 응답을 살짝 맛본다.
> - 동기 함수(`def`)와 비동기 함수(`async def`)의 차이를 입문자 수준에서 짚는다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 1~2시간 (직접 타이핑하며 따라할 때 기준)

> **전제**: 03장의 설치가 끝나 있어야 합니다. 즉, 다음 세 가지가 통하는 상태:
> - `python3.13 --version` → `Python 3.13.x`
> - `uv --version` → `uv 0.x.x`
> - `code --version` → VS Code 버전 출력

---

## 4.1 이 챕터의 큰 그림 — 우리가 만들 것

03장 마지막에서 우리는 다음 다섯 줄짜리 코드를 띄워봤습니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}
```

이 다섯 줄은 환경이 잘 깔렸는지 확인하기 위한 **최소 검증**이었습니다. 한 파일에 모든 게 들어 있었고, 폴더 구조도 단순했죠.

이번 챕터에서는 같은 흐름을 **본격적인 프로젝트의 모양으로** 다시 만듭니다. 구체적으로 다음을 더합니다.

1. **표준 폴더 구조**: 모든 코드를 한 파일에 넣지 않고, `app/` 폴더 안에 `main.py`를 둡니다. 앞으로 라우터·모델·DB 코드가 늘어나면 `app/routers/`, `app/models/`처럼 자연스럽게 가지를 칠 수 있는 형태입니다.
2. **`pyproject.toml` 이해**: 03장에서 `uv init`으로 자동 생성된 이 파일을 한 줄씩 읽어보고, 의존성·메타데이터가 어떻게 기록되는지 살펴봅니다.
3. **추가 라우트**: 경로 매개변수(`/hello/{name}`)를 받는 라우트를 하나 더 만듭니다. 이 작은 변형이 "정적인 응답"에서 "사용자 입력에 반응하는 응답"으로 가는 첫걸음입니다.
4. **자동 문서 자세히 보기**: `/docs`, `/redoc`, `/openapi.json` 세 페이지의 정체와 쓰임을 정리합니다.
5. **Pydantic 모델 맛보기**: 응답을 그냥 `dict`로 돌려주지 않고, 작은 데이터 클래스로 감싸봅니다. 본격적인 Pydantic은 05장에서 다루지만, 미리 한 번 보고 넘어가면 다음 장이 훨씬 부드럽습니다.

이번 챕터를 마치면, 앞으로 모든 챕터에서 등장하는 "프로젝트를 새로 만들고 → 라우트 한두 개를 추가하고 → 띄워서 확인한다"는 사이클을 자기 손으로 반복할 수 있게 됩니다.

> **앞으로의 챕터와의 관계**: 05장(라우팅·Pydantic)·06장(DB)·07장(CRUD)에서는 모두 이 구조를 그대로 늘려 나갑니다. `app/main.py`에 직접 라우트를 추가하다가, 라우트가 많아지면 `app/routers/` 폴더로 나누고, DB가 들어오면 `app/db.py`·`app/models/`가 추가됩니다. 즉, **이 챕터의 골격이 끝까지 이어지는 뼈대**가 됩니다.

---

## 4.2 우리가 만들 프로젝트의 최종 모습

이번 챕터를 다 마치면 폴더는 다음과 같이 됩니다. 지금은 **이름만** 봐 두세요.

```
04-HelloFastAPI/
├── pyproject.toml         # uv가 만드는 프로젝트 설정 파일 (의존성·메타데이터)
├── uv.lock                # 의존성 잠금 파일 (정확한 버전·해시 기록)
├── .python-version        # 이 프로젝트가 쓸 Python 버전 ("3.13")
├── .gitignore             # git에 올리지 않을 파일·폴더 목록
├── README.md              # 프로젝트 설명·실행 방법
└── app/
    ├── __init__.py        # 빈 파일 (또는 한 줄 docstring) — "이 폴더는 패키지" 표시
    └── main.py            # FastAPI 앱 본체. 우리가 가장 자주 만질 파일.
```

각 항목을 한 줄로 정리하면:

| 파일/폴더 | 누가 만드는가 | 무엇인가 |
|-----------|---------------|----------|
| `pyproject.toml` | `uv init` | 프로젝트 메타데이터·의존성 목록 (사람이 읽는 표준 파일) |
| `uv.lock` | `uv add`·`uv sync` | 의존성의 정확한 버전·해시 잠금 (자동 관리) |
| `.python-version` | `uv init` | 이 프로젝트가 쓸 Python 버전을 적어둔 작은 텍스트 |
| `.gitignore` | 우리(또는 `uv init`) | git이 무시할 파일 목록 |
| `README.md` | 우리(또는 `uv init`) | 프로젝트 개요·실행법 |
| `app/__init__.py` | 우리 | "이 폴더를 Python 패키지로 취급하라"는 표시. 보통 비어 있음 |
| `app/main.py` | 우리 | FastAPI 앱 본체. 라우트와 `app` 객체가 여기 들어감 |

> **이 구조의 의도**: `app/` 안에 모든 코드가 들어 있으므로, 나중에 테스트 폴더(`tests/`)나 마이그레이션 폴더(`alembic/`)가 추가돼도 **앱 코드와 다른 코드가 섞이지 않습니다.** "코드 = `app/`" "프로젝트 메타 = 그 바깥"이라는 분리가 가독성과 배포의 단순함을 모두 가져옵니다.

---

## 4.3 프로젝트 폴더 만들기 — `uv init` 흐름

03장에서 이미 `uv init`을 한 번 해봤습니다. 이번에는 **실전 프로젝트**라는 마음으로 다시, 단계마다 출력 결과를 확인하며 진행합니다.

### 4.3.1 작업 위치 정하기

이 가이드는 홈 디렉터리 아래 `projects/`라는 작업 폴더를 두는 관례를 씁니다(없으면 만드세요). 다른 위치를 써도 무방합니다.

```bash
mkdir -p ~/projects
cd ~/projects
```

> **`mkdir -p`의 `-p`란?** 부모 폴더가 없어도 함께 만들고, 폴더가 이미 있어도 에러를 내지 않습니다. 안전한 표준 옵션입니다.

### 4.3.2 프로젝트 폴더 만들기

```bash
mkdir 04-HelloFastAPI
cd 04-HelloFastAPI
```

폴더 이름은 자유지만, 가이드의 예제 폴더 이름에 맞춰 `04-HelloFastAPI`를 권장합니다.

> **폴더 이름에 대시(`-`)가 있어도 되나요?** 됩니다. **폴더 이름**과 **Python 패키지 이름**은 별개입니다. 우리가 import할 패키지는 `app/`이라서 어떤 이름이든 상관없습니다. 단, 만약 `pyproject.toml`의 `name = "..."` 항목에 대시가 들어가면 자동으로 `_`로 바꿔 import하므로 그 정도만 알아두세요.

### 4.3.3 `uv init` 실행

이제 이 폴더를 uv 프로젝트로 초기화합니다.

```bash
uv init
```

실행 직후 출력은 대략 다음과 같습니다(uv 버전에 따라 약간 다를 수 있음).

```
Initialized project `04-hellofastapi`
```

폴더에는 다음 파일들이 생겨 있습니다.

```bash
ls -a
```

```
.        ..       .git/    .gitignore   .python-version   README.md   pyproject.toml   main.py
```

각 항목의 의미:

- **`.git/`**: uv가 자동으로 git 저장소를 초기화해 둡니다. 우리가 바로 git을 쓸 수 있도록 준비된 상태입니다.
- **`.gitignore`**: `__pycache__/`, `.venv/` 등 Python 프로젝트의 표준 제외 항목이 미리 들어 있습니다.
- **`.python-version`**: 이 프로젝트가 쓸 Python 버전이 적힌 작은 텍스트 파일.
- **`README.md`**: 빈 README 한 장.
- **`pyproject.toml`**: 프로젝트 설정 표준 파일. 다음 절에서 자세히 봅니다.
- **`main.py`**: uv가 만든 한 줄짜리 예시 스크립트. **우리는 이 파일을 곧 지웁니다** — FastAPI 앱은 `app/main.py`라는 다른 위치에 새로 만들 거라서요.

> **uv 버전에 따라 `main.py` 대신 `hello.py`가 생기기도 합니다.** 어느 쪽이든 우리가 안 쓸 파일이므로 다음 절에서 함께 정리합니다.

### 4.3.4 자동 생성된 예시 스크립트 지우기

루트의 `main.py`(또는 `hello.py`)는 우리가 만들 `app/main.py`와 이름이 헷갈릴 수 있으니 **지웁니다**.

```bash
rm -f main.py hello.py
```

> **`rm -f`의 `-f`란?** "force"의 줄임으로, 파일이 없어도 에러를 내지 않습니다. 둘 중 하나만 있어도 깔끔히 지워집니다.

### 4.3.5 `.python-version` 확인

```bash
cat .python-version
```

다음과 비슷한 한 줄이 보입니다.

```
3.13
```

이 한 줄이 의미하는 바: "이 폴더에 들어오면 uv는 Python 3.13으로 동작한다." `uv run` 계열 명령은 이 파일을 보고 어떤 Python을 써야 할지 결정합니다.

> **만약 다른 버전이 적혀 있다면** 03장의 Python 설치를 점검하세요. uv가 시스템에서 인식한 Python 중 가장 적합한 것을 골라 적기 때문에, 3.13이 깔려 있는데 3.12가 적혀 있다면 인식 문제일 수 있습니다. 그럴 땐 텍스트 에디터로 직접 `3.13`으로 수정해도 됩니다.

---

## 4.4 `pyproject.toml` 한 줄씩 읽기

이제 가장 중요한 파일을 살펴볼 차례입니다. 텍스트 에디터나 VS Code로 `pyproject.toml`을 열어 보세요.

```bash
code pyproject.toml
```

내용은 대략 이렇습니다(uv 버전에 따라 미세 차이가 있을 수 있음).

```toml
[project]
name = "04-hellofastapi"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

### 4.4.1 `pyproject.toml`이란

> **`pyproject.toml`이란?** 현대 Python 프로젝트의 **표준 설정 파일**입니다. 옛날에는 `setup.py`(빌드)·`requirements.txt`(의존성)·`setup.cfg`(메타데이터)·`MANIFEST.in`(파일 포함 규칙) 등이 따로 했던 일을 한 파일에 모은 것입니다. uv·pip·poetry·ruff·pytest 등 거의 모든 현대 Python 도구가 이 파일을 읽습니다.

> **TOML이란?** "Tom's Obvious Minimal Language"의 줄임. JSON·YAML과 비슷한 역할을 하지만, **사람이 읽고 쓰기 가장 편하게** 설계된 설정 형식입니다. `[섹션이름]`으로 묶고, `키 = 값` 형태로 적습니다. 따옴표·괄호 같은 세부 문법이 단순합니다.

### 4.4.2 항목별 의미

| 항목 | 의미 | 우리가 자주 만지는가 |
|------|------|-----------------------|
| `[project]` | 이 아래는 프로젝트 메타데이터 섹션이라는 표시 | 섹션 헤더 자체는 안 만짐 |
| `name = "04-hellofastapi"` | 패키지 이름. 외부에 배포할 때 쓰임 | 처음 한 번 |
| `version = "0.1.0"` | 프로젝트 버전. SemVer 권장 | 가끔 |
| `description = "..."` | 한 줄 설명 | 처음 한 번 |
| `readme = "README.md"` | 어떤 파일이 README인지 | 거의 안 만짐 |
| `requires-python = ">=3.13"` | 이 프로젝트가 요구하는 최소 Python 버전 | 거의 안 만짐 |
| `dependencies = []` | 이 프로젝트가 쓰는 외부 라이브러리 목록 | **자주 — 다만 직접 손대기보다 `uv add` 명령으로 자동 갱신됨** |

### 4.4.3 `name`을 읽기 좋게 다듬기

기본값으로 `04-hellofastapi`처럼 폴더 이름을 그대로 가져오는 경우가 많은데, **숫자로 시작**하거나 **대시가 들어간 이름**은 일부 도구에서 어색할 수 있습니다. 학습용 가이드 폴더라면 그대로 둬도 무방하지만, 깔끔하게 다듬고 싶다면 `name`을 바꿔 줍니다.

`pyproject.toml`을 열어 다음처럼 수정합니다.

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 입문 — 04장 Hello FastAPI 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

> **이름은 어떻게 정해야 하나요?** 영어 소문자 + 대시(`-`)가 가장 안전합니다. PyPI(공식 패키지 저장소)에 올릴 게 아니라면 어떤 이름이든 상관없습니다. 학습용으로는 `hello-fastapi`, `notes-api`, `blog-api` 정도가 무난합니다.

### 4.4.4 `requires-python`을 본격 이해하기

`requires-python = ">=3.13"`은 "이 프로젝트는 Python 3.13 이상에서 동작한다"는 선언입니다. uv는 이 줄을 읽고 다음을 합니다.

1. 가상환경을 만들 때 3.13 이상의 인터프리터를 골라 씁니다.
2. 의존성을 풀 때 3.13 이상에서만 동작하는 라이브러리도 후보로 포함합니다.

> **`>=3.13`과 `~=3.13` 같은 표기는 뭐가 다른가요?**
> - `>=3.13` — 3.13 이상 (3.14, 4.0도 OK)
> - `~=3.13` — 3.13 이상, 3.14 미만 (마이너 잠금)
> - `==3.13.*` — 3.13.x만
>
> 라이브러리를 PyPI에 배포한다면 신중히 정해야 하지만, 우리는 학습용이니 `>=3.13`이면 충분합니다.

### 4.4.5 다른 도구의 설정도 들어옵니다

지금은 `[project]` 섹션밖에 없지만, 프로젝트가 자라면 같은 파일에 다음 같은 섹션이 추가됩니다.

```toml
[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
addopts = "-q"

[tool.uv]
# uv 자체에 대한 설정
```

이 가이드의 후반부 챕터에서 하나씩 등장합니다. 지금은 "한 파일에 여러 도구 설정이 다 모인다"는 사실만 기억하세요.

---

## 4.5 FastAPI와 Uvicorn 의존성 추가하기

이제 FastAPI와 Uvicorn을 이 프로젝트에 추가합니다.

```bash
uv add fastapi "uvicorn[standard]"
```

### 4.5.1 `uv add`가 한 번에 하는 일

이 명령은 **네 가지를 동시에** 처리합니다.

1. **가상환경 만들기**: 처음이면 `.venv/` 폴더를 자동 생성. (이미 있으면 그대로 사용)
2. **라이브러리 설치**: `fastapi`, `uvicorn[standard]`, 그리고 그 의존성들(`pydantic`, `starlette`, `anyio` 등)을 받아서 `.venv/`에 깝니다.
3. **`pyproject.toml` 갱신**: `[project]`의 `dependencies` 항목에 우리가 의도한 두 줄(`fastapi`, `uvicorn[standard]`)을 추가합니다.
4. **`uv.lock` 작성**: 깔린 모든 라이브러리의 정확한 버전·해시를 잠금 파일에 기록합니다.

명령이 끝난 뒤 `pyproject.toml`을 다시 열면 다음처럼 바뀝니다.

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 입문 — 04장 Hello FastAPI 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
```

(정확한 버전 숫자는 시점에 따라 다릅니다.)

### 4.5.2 `uvicorn[standard]`의 대괄호

> **`uvicorn[standard]`의 대괄호는 뭐죠?** "추가 옵션 묶음"을 뜻하는 표기입니다. 그냥 `uvicorn`만 받으면 핵심만 들어오고, `uvicorn[standard]`로 받으면 자주 쓰는 부가 라이브러리가 함께 깔립니다. 대표적으로 자동 리로드를 위한 `watchfiles`, 빠른 HTTP 파서인 `httptools` 등이 포함됩니다. 우리는 개발 중 `--reload`를 쓸 거라서 `[standard]`가 필요합니다. 따옴표(`"..."`)는 일부 셸이 대괄호를 잘못 해석하지 않게 막아주는 안전장치입니다.

### 4.5.3 깔린 것 확인

```bash
uv pip list
```

다음 같은 출력이 나오면 OK입니다(버전 숫자는 다를 수 있음).

```
Package           Version
----------------- --------
annotated-types   0.7.0
anyio             4.x.x
click             8.x.x
fastapi           0.115.x
h11               0.14.x
httptools         0.6.x
idna              3.x
pydantic          2.x.x
pydantic_core     2.x.x
python-dotenv     1.x.x
sniffio           1.3.x
starlette         0.x.x
typing_extensions 4.x.x
uvicorn           0.30.x
uvloop            0.x.x
watchfiles        0.x.x
websockets        13.x.x
```

`fastapi`와 `uvicorn`이 보이면 의존성 설치는 성공입니다. (다른 이름이 같이 보이는 것은 정상 — 그것들은 FastAPI/Uvicorn이 내부적으로 의존하는 라이브러리들입니다.)

### 4.5.4 `uv.lock`은 어떤 모양인가

`uv.lock` 파일은 사람이 직접 편집하지 않는 **자동 생성 파일**이지만, 어떻게 생겼는지 한 번 봐 두면 좋습니다.

```bash
head -n 30 uv.lock
```

다음과 비슷한 TOML이 보입니다.

```toml
version = 1
requires-python = ">=3.13"

[[package]]
name = "annotated-types"
version = "0.7.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "sha256:..." }
wheels = [
    { url = "...", hash = "sha256:..." },
]

[[package]]
name = "fastapi"
version = "0.115.x"
...
```

각 라이브러리마다 **정확한 버전과 다운로드 URL, 해시값**이 적혀 있습니다. 다른 컴퓨터에서 `uv sync`를 돌리면 이 파일을 보고 **정확히 같은 것**들이 다시 깔립니다. 협업 시 "내 컴퓨터에선 됐는데"를 막아주는 핵심 파일입니다.

> **`uv.lock`은 git에 올려야 하나요?** 네. 애플리케이션(실행 파일) 프로젝트에서는 항상 커밋합니다. 우리가 만들 모든 프로젝트는 애플리케이션이므로, 의심하지 말고 커밋하세요. (라이브러리를 만드는 경우엔 토론의 여지가 있지만, 이 가이드의 범위 밖입니다.)

### 4.5.5 다른 컴퓨터에서 같은 환경 복원하기

만약 친구가 우리 프로젝트를 받아 자기 컴퓨터에서 띄우려 한다면, `git clone` 한 뒤 다음 한 줄이면 됩니다.

```bash
uv sync
```

이 명령은 **`uv.lock`을 그대로 복원**합니다. 즉, 가상환경을 만들고, 잠긴 정확한 버전으로 모든 라이브러리를 깝니다. **`uv add`와의 차이**는, `uv add`는 "새 의존성 추가 + 잠금 갱신"이고 `uv sync`는 "이미 잠금된 그대로 복원"이라는 점입니다.

| 명령 | 언제 쓰나 |
|------|-----------|
| `uv add <라이브러리>` | 새 라이브러리를 처음 추가할 때 |
| `uv sync` | 다른 컴퓨터·새 클론에서 잠금 그대로 복원할 때 |
| `uv lock` | 잠금 파일만 새로 만들 때 (의존성 변경 후 명시적으로 잠그고 싶을 때) |

지금은 첫 번째만 알면 됩니다.

---

## 4.6 `app/` 폴더와 `app/main.py` 만들기

이제 본격적인 코드 작성입니다.

### 4.6.1 왜 코드를 폴더에 모으나 (왜 `main.py` 한 파일이 아닌가)

03장에서는 모든 코드가 `app.py` 한 파일에 들어 있었습니다. 학습 1단계로는 충분하지만, 라우트가 늘고 DB가 들어오면 한 파일이 곧 수백 줄이 됩니다. 그 시점에 폴더로 나누려면 **import 경로가 모두 바뀌어** 수정이 번거롭습니다. 그래서 처음부터 작은 폴더 구조로 시작하는 게 안전합니다.

이 가이드의 표준 구조는 **`app/` 패키지 안에 코드가 들어가고**, 진입점 모듈은 `app/main.py`라는 약속입니다. 다음과 같은 장점이 있습니다.

1. **늘어날 자리가 마련돼 있음**: 라우터가 많아지면 `app/routers/`, 모델이 추가되면 `app/models/`, DB는 `app/db.py`처럼 같은 폴더 안에 자연스럽게 가지가 칩니다.
2. **import 경로가 일관됨**: 어디에서든 `from app.something import ...` 형식으로 부르게 됩니다. 한 파일짜리 구조에서 갈아탈 때 발생하는 import 깨짐이 없습니다.
3. **테스트와 분리됨**: 나중에 `tests/` 폴더가 추가돼도 `app/`과 깨끗하게 분리됩니다.
4. **Uvicorn 명령이 표준 형태가 됨**: `uvicorn app.main:app`이 어떤 프로젝트에서나 같은 의미를 갖게 됩니다.

### 4.6.2 폴더와 파일 만들기

다음 명령으로 한 번에 만듭니다.

```bash
mkdir app
touch app/__init__.py app/main.py
```

> **`touch`란?** 빈 파일을 만드는 명령(또는 이미 있는 파일의 수정 시각만 갱신). 여기서는 두 빈 파일을 만들기 위해 씁니다.

확인해 보면 폴더는 다음 모양이 됩니다.

```
04-HelloFastAPI/
├── app/
│   ├── __init__.py
│   └── main.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

### 4.6.3 `__init__.py`란

> **`__init__.py`란?** "이 폴더를 Python 패키지로 취급해라"라고 표시하는 특수 파일입니다. 보통은 **비워 두지만**, 패키지가 import될 때 자동 실행되는 코드를 적기도 합니다.

> **꼭 있어야 하나요?** Python 3에서는 "namespace package"라는 개념이 생겨서, `__init__.py` 없이도 폴더를 패키지처럼 쓸 수 있습니다. 하지만 IDE의 자동 완성·정적 분석 도구가 더 깔끔하게 인식하려면 빈 `__init__.py`를 두는 게 안전합니다. **이 가이드에서는 항상 빈 `__init__.py`를 둡니다.**

지금은 비어 있는 채로 두거나, 가독성을 위해 한 줄짜리 docstring만 적어 둡니다.

```python
"""hello-fastapi 앱 패키지."""
```

### 4.6.4 `app/main.py`에 가장 작은 FastAPI 앱 작성

이제 `app/main.py`에 다음 코드를 적습니다. **한 줄씩** 따라 적으면서, 다음 절(4.7)의 해설을 참고하세요.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI

# FastAPI 인스턴스 — 우리 앱 전체의 루트 객체.
# 이 객체에 라우트, 미들웨어, 의존성 등을 등록한다.
app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리.

    매우 단순한 환영 메시지를 JSON으로 돌려준다.
    """
    return {"message": "Hello, FastAPI!"}
```

저장합니다. 다음 절에서 한 줄씩 풀어 보겠습니다.

---

## 4.7 가장 작은 FastAPI 앱, 한 줄씩 풀이

위 코드는 짧지만 FastAPI의 가장 기본 패턴이 모두 들어 있습니다. 한 줄씩 보겠습니다.

### 4.7.1 `from fastapi import FastAPI`

`fastapi` 패키지에서 `FastAPI`라는 클래스를 가져옵니다. `FastAPI`가 우리 앱의 루트 객체를 만드는 클래스입니다.

> **import 한 줄이 무겁지 않나요?** `fastapi` 패키지 자체는 가볍습니다. 무거운 건 그 안에서 다시 import하는 `pydantic`·`starlette` 등인데, 그것들은 우리가 직접 import하지 않더라도 FastAPI가 동작할 때 자연스럽게 로드됩니다.

### 4.7.2 `app = FastAPI(...)`

`FastAPI()` 클래스를 호출해 인스턴스 하나를 만듭니다. 이 변수 이름은 관례상 **`app`**으로 짓습니다(다른 이름도 가능하지만, 모든 FastAPI 자료가 `app`을 가정합니다).

생성자에 넘긴 `title`, `description`, `version` 인자는 자동 생성될 API 문서(`/docs`, `/redoc`)에 그대로 노출됩니다. 즉, 다음 절에서 브라우저로 확인할 페이지 상단에 우리가 적은 제목·설명·버전이 보입니다.

> **인자를 안 넘기고 `FastAPI()`만 해도 되나요?** 됩니다. 다 기본값으로 채워집니다. 다만 자동 문서 페이지의 제목이 `FastAPI`라는 무미건조한 이름이 됩니다. 학습용이라도 한두 줄 채워두면 보기 좋고, 나중에 운영 환경에서 어떤 앱인지 식별에 도움이 됩니다.

### 4.7.3 `@app.get("/")` — 데코레이터

이 한 줄이 FastAPI 라우팅의 **핵심**입니다. 의미는 다음과 같습니다.

- `@`로 시작하는 표기를 **데코레이터**라고 부릅니다.
- `app.get(...)`은 "GET 메서드의 라우트를 만드는 함수"입니다.
- 인자 `"/"`는 "어느 URL 경로에서 동작할지" 지정합니다. 슬래시 하나는 루트 경로.
- 이 데코레이터는 **그 바로 아래의 함수**(`read_root`)를 "GET `/` 요청 처리기"로 등록합니다.

> **데코레이터(decorator)란?** 함수 위에 `@`로 붙는 표시입니다. "이 함수에 추가 기능을 입혀라"는 뜻입니다. 우리가 데코레이터를 직접 만들 일은 거의 없고, 이미 만들어진 데코레이터(여기서는 `@app.get`)를 갖다 쓰기만 합니다. [용어 사전 — 데코레이터](glossary.md#데코레이터-decorator)에 한 줄 더 자세한 설명이 있습니다.

같은 패턴으로 다른 HTTP 메서드도 등록합니다.

| 데코레이터 | 의미 |
|------------|------|
| `@app.get("/path")` | GET 요청 처리 (자료 가져오기) |
| `@app.post("/path")` | POST 요청 처리 (자료 새로 만들기) |
| `@app.put("/path")` | PUT 요청 처리 (자료 통째로 수정) |
| `@app.patch("/path")` | PATCH 요청 처리 (자료 일부 수정) |
| `@app.delete("/path")` | DELETE 요청 처리 (자료 삭제) |

> **HTTP 메서드 복습**: GET = 자료 가져오기, POST = 만들기, PUT/PATCH = 수정, DELETE = 삭제. 02장에서 설명한 그것입니다. 다섯 가지를 거의 다 쓰는 챕터는 07장 CRUD입니다.

### 4.7.4 `def read_root() -> dict[str, str]:`

처리기 함수의 본체입니다.

- **함수 이름 `read_root`**: 자유. FastAPI는 함수 이름 자체로 라우팅을 결정하지 않습니다(데코레이터의 `"/"`로 결정). 다만 자동 문서의 endpoint 이름으로 쓰이기 때문에, 의미가 잘 드러나는 이름을 짓는 게 좋습니다.
- **인자가 없음**: 이 라우트는 어떤 입력도 받지 않습니다. 곧 추가할 `/hello/{name}` 라우트는 인자가 있습니다.
- **반환 타입 힌트 `-> dict[str, str]`**: "이 함수는 문자열 키와 문자열 값을 가진 dict를 돌려준다"는 표시입니다. FastAPI는 이 타입 힌트를 읽어 자동 문서에 응답 형식을 적습니다.

> **타입 힌트 복습**: Python 3.5부터 도입된 표기로, 변수와 함수의 인자·반환에 "이건 이런 타입"이라고 적어두는 것입니다. 런타임에 강제하지는 않지만, FastAPI/Pydantic은 이 힌트를 읽어 자동 검증·문서화를 합니다.

> **`dict[str, str]`이 어색하다면**: Python 3.8까지는 `Dict[str, str]`(대문자, `from typing import Dict`)이었지만, 3.9부터 소문자 `dict[...]`를 그대로 쓸 수 있게 됐습니다. 우리는 3.13을 쓰므로 항상 소문자 형태를 씁니다.

### 4.7.5 `return {"message": "Hello, FastAPI!"}`

`dict`를 반환합니다. FastAPI는 이 dict를 **자동으로 JSON으로 직렬화해** 응답 본문(body)에 담습니다. 응답 헤더도 자동으로 `Content-Type: application/json`이 붙습니다.

> **dict가 어떻게 JSON이 되나요?** FastAPI 내부에서 `pydantic`을 통해 `json.dumps` 비슷한 변환이 일어납니다. dict뿐 아니라 list, Pydantic 모델, dataclass 등 거의 모든 기본 자료형이 JSON으로 자동 변환됩니다. 변환 못 하는 타입(예: 임의의 클래스 인스턴스)을 그대로 반환하면 에러가 납니다.

응답의 HTTP 상태 코드는 명시하지 않으면 **200 OK**가 기본값입니다.

---

## 4.8 서버 실행 — `uv run uvicorn app.main:app --reload`

이제 띄워볼 시간입니다. 프로젝트 루트(`04-HelloFastAPI/`)에서 다음을 실행합니다.

```bash
uv run uvicorn app.main:app --reload
```

성공하면 다음 비슷한 로그가 출력됩니다.

```
INFO:     Will watch for changes in these directories: ['/Users/.../04-HelloFastAPI']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

이 로그가 보이면 서버가 떠 있는 상태입니다. 이대로 두고 다음 절(4.9)에서 브라우저로 확인합니다.

### 4.8.1 명령의 각 부분 풀이

이 한 줄을 처음부터 끝까지 읽어 봅시다.

| 부분 | 의미 |
|------|------|
| `uv run` | "uv가 가상환경 안에서 다음 명령을 실행해" |
| `uvicorn` | 실제로 실행할 프로그램 (Uvicorn 서버) |
| `app.main:app` | "어떤 앱을 띄울지" — `app/main.py` 파일의 `app` 변수 |
| `--reload` | 코드를 수정하면 서버를 자동으로 다시 시작 |

각각을 좀 더 자세히.

### 4.8.2 `uv run`

> **`uv run <명령>`이란?** "이 명령을 가상환경 안에서 실행해 줘"라는 뜻의 uv 표준 접두사입니다. `uv run` 없이 그냥 `uvicorn ...`을 치면 시스템에 깔린 다른 uvicorn(있다면)을 부르거나, 없다면 `command not found`가 됩니다. uv 사용자는 거의 모든 실행 명령 앞에 `uv run`을 붙입니다.

뒤에 오는 명령이 무엇이든 상관없습니다.

```bash
uv run python --version
uv run pytest
uv run ruff check .
```

모두 같은 패턴입니다.

### 4.8.3 `uvicorn`

Uvicorn은 ASGI 서버, 즉 우리가 만든 FastAPI 앱을 실제로 띄워 HTTP 요청을 받아주는 프로그램입니다. FastAPI 자체는 "라우트 정의 + 처리 로직"이고, 그것을 8000번 포트에서 듣게 만드는 일은 Uvicorn이 합니다.

> **ASGI(Asynchronous Server Gateway Interface)란?** 비동기 Python 웹 앱과 서버 사이의 표준 약속입니다. FastAPI는 ASGI 앱이고, Uvicorn은 ASGI 서버입니다. 이 둘은 ASGI 약속을 통해 대화합니다. [용어 사전](glossary.md#asgi-asynchronous-server-gateway-interface) 참고.

### 4.8.4 `app.main:app` — 모듈 경로 형식

이 부분이 가장 헷갈리는 부분입니다. 형식은 **`폴더.파일이름:변수이름`**입니다.

- `app` — 폴더(=Python 패키지) 이름. 우리가 만든 `app/` 폴더입니다.
- `.main` — 그 안의 `main.py` 파일. 점(`.`)으로 폴더와 파일을 잇습니다.
- `:app` — 콜론 뒤는 그 파일 안의 **변수 이름**. 우리가 만든 `app = FastAPI(...)`의 `app`입니다.

따라서 전체 의미는 "**`app/main.py`라는 모듈 안의 `app`이라는 변수**(즉, FastAPI 인스턴스)를 띄워라"입니다.

> **헷갈리는 이유**: 폴더 이름과 변수 이름이 둘 다 `app`이라서 두 번 등장합니다. 만약 폴더가 `myapi/`였다면 명령은 `myapi.main:app`이 됩니다. **앞쪽 `app`은 폴더, 뒤쪽 `app`은 변수**라는 점을 한 번만 이해하면 헷갈리지 않습니다.

> **다른 예시**:
> - 단일 파일 `app.py` 안의 `app` 변수 → `app:app`
> - `myapp/server.py` 안의 `application` 변수 → `myapp.server:application`
> - `src/api/main.py` 안의 `app` → `src.api.main:app` (단, `src/`도 `__init__.py`가 있어야 패키지로 인식됨)

### 4.8.5 `--reload`

`--reload`는 **개발용 옵션**으로, 코드 파일이 바뀌면 서버를 자동으로 다시 시작합니다. 이게 없으면 코드를 고칠 때마다 직접 `Ctrl+C`로 끄고 다시 띄워야 해서 매우 번거롭습니다.

> **운영 환경에서도 쓰나요?** 절대 안 됩니다. `--reload`는 파일 시스템을 끊임없이 감시하므로 CPU 낭비가 있고, 안전하지도 않습니다. **개발 중에만 씁니다.** 운영 배포는 09장에서 Gunicorn + Uvicorn으로 다시 다룹니다.

### 4.8.6 `--host`와 `--port`

기본값은 `127.0.0.1:8000`입니다. 이를 바꾸고 싶다면:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

- `--host 127.0.0.1` (기본): 같은 컴퓨터에서만 접근 가능 (localhost).
- `--host 0.0.0.0`: 모든 네트워크 인터페이스에서 접근 가능. **다른 기기(예: 같은 와이파이의 휴대폰)에서 접속하고 싶을 때.**
- `--port 8000` (기본): 8000번 포트.

> **`localhost`와 `127.0.0.1`이 같은 건가요?** 사실상 같습니다. `127.0.0.1`은 "내 컴퓨터 자신"을 가리키는 IPv4 주소이고, `localhost`는 그 별칭입니다. 브라우저 주소창에 둘 중 어느 것을 쳐도 똑같이 동작합니다.

---

## 4.9 자동 문서 보기 — `/docs`, `/redoc`, `/openapi.json`

서버가 떠 있는 동안 브라우저에서 다음 세 주소를 차례로 열어 봅시다. **FastAPI의 가장 큰 매력**을 직접 보는 시간입니다.

### 4.9.1 첫 라우트 직접 호출 — `/`

브라우저 주소창에 다음을 칩니다.

```
http://127.0.0.1:8000/
```

화면에 다음 JSON이 보입니다.

```json
{"message":"Hello, FastAPI!"}
```

또는 다른 터미널에서 `curl`로 직접 호출해도 됩니다.

```bash
curl http://127.0.0.1:8000/
# 응답: {"message":"Hello, FastAPI!"}
```

### 4.9.2 `/docs` — Swagger UI

이게 FastAPI의 핵심 기능입니다. 다음 주소를 엽니다.

```
http://127.0.0.1:8000/docs
```

다음과 같은 페이지가 보입니다.

- 상단에 우리가 적은 **`Hello FastAPI` (제목)**, **0.1.0 (버전)**, **설명**이 표시됩니다.
- 아래에 등록된 모든 엔드포인트가 카드 형태로 나열됩니다. 지금은 `GET /`만 있습니다.
- 카드를 클릭해서 펼치면 입력 형식·응답 형식·예시가 자동으로 보입니다.
- **"Try it out" 버튼**을 누르면 브라우저에서 직접 API를 호출해 보고, 응답을 받아볼 수 있습니다.

> **Swagger UI란?** OpenAPI 명세를 보고 인터랙티브하게 테스트할 수 있는 웹 페이지입니다. 별도 앱(Postman 등) 없이 브라우저만으로 API 테스트가 가능합니다. FastAPI는 우리 코드를 분석해 OpenAPI 명세를 만들고, 그 명세를 보여주는 Swagger UI를 자동으로 `/docs`에 띄워줍니다.

이 한 페이지가 나오기까지 우리가 별도로 설정한 게 **하나도 없다**는 점에 주목하세요. 코드만 적었고, 나머지는 FastAPI가 합니다.

### 4.9.3 `/redoc` — ReDoc

같은 정보를 다른 디자인으로 보여주는 페이지입니다.

```
http://127.0.0.1:8000/redoc
```

- 좌측에 엔드포인트 목록, 우측에 자세한 설명·예시가 나옵니다.
- "Try it out" 같은 인터랙티브 요소는 없고, **읽기 좋은 정적 문서**에 가깝습니다.

> **`/docs`와 `/redoc` 중 뭘 쓰나요?** 개발 중에는 거의 항상 `/docs`(Swagger UI)를 씁니다. 직접 호출해 볼 수 있어서 편합니다. `/redoc`은 외부에 API 문서를 공개할 때 더 깔끔해 보여서 종종 쓰입니다. **두 페이지 모두 별도 설정 없이 그냥 같이 만들어집니다.** 한쪽이 부담스러우면 끌 수 있는 옵션도 있습니다(`FastAPI(redoc_url=None)`).

### 4.9.4 `/openapi.json` — OpenAPI 명세 자체

진짜 흥미로운 페이지는 이것입니다.

```
http://127.0.0.1:8000/openapi.json
```

브라우저에 긴 JSON 한 덩어리가 보입니다. 다음과 같이 생긴 무언가입니다.

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Hello FastAPI",
    "description": "FastAPI 가이드 04장 — 첫 프로젝트 예제",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "get": {
        "summary": "Read Root",
        "operationId": "read_root__get",
        "responses": { ... }
      }
    }
  },
  ...
}
```

> **OpenAPI란?** REST API의 명세를 JSON/YAML로 적는 표준 형식입니다. 옛 이름은 Swagger. 이 명세 한 장만 있으면 다른 도구가 자동으로 클라이언트 코드를 만들거나, 위에서 본 Swagger UI 같은 문서 페이지를 그릴 수 있습니다. **FastAPI의 `/openapi.json`은 모든 자동 문서의 원천**입니다. `/docs`와 `/redoc`은 결국 이 JSON을 가져와 그리는 페이지입니다.

이 명세는 외부 도구와 통합할 때 매우 유용합니다.

- **클라이언트 SDK 자동 생성**: `openapi-generator`로 TypeScript·Swift·Kotlin 등 다양한 언어의 클라이언트 코드를 자동 생성할 수 있습니다.
- **API 변경 추적**: 매 배포마다 `/openapi.json`을 저장하면, API가 어떻게 변했는지 자동으로 비교 가능합니다.
- **모의 서버**: Postman 등에서 OpenAPI 명세를 import해 응답을 흉내 내는 mock 서버를 만들 수 있습니다.

지금은 **존재만 알아두고**, 실전에서 필요해질 때 다시 펼쳐보면 됩니다.

---

## 4.10 작은 변형 — 경로 매개변수 추가하기

지금까지의 라우트는 입력이 없습니다. 한 단계 더 나가서 **사용자 입력**을 받아 응답을 바꾸는 라우트를 만들어 봅시다.

### 4.10.1 코드 추가

`app/main.py`를 다음처럼 수정합니다(기존 코드 아래에 새 라우트를 추가).

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def hello_name(name: str) -> dict[str, str]:
    """경로 매개변수 `name`을 받아 인사말을 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!"}`
    """
    return {"message": f"안녕하세요, {name}님!"}
```

저장합니다. `--reload` 옵션을 켜뒀다면 서버가 자동으로 재시작됩니다.

### 4.10.2 동작 확인

브라우저에서:

```
http://127.0.0.1:8000/hello/Alice
```

응답:

```json
{"message":"안녕하세요, Alice님!"}
```

다른 이름도 시도해 보세요.

```bash
curl http://127.0.0.1:8000/hello/보성
# 응답: {"message":"안녕하세요, 보성님!"}
```

### 4.10.3 한 줄씩 풀이

```python
@app.get("/hello/{name}")
def hello_name(name: str) -> dict[str, str]:
    return {"message": f"안녕하세요, {name}님!"}
```

핵심 두 가지:

1. **경로의 `{name}` (중괄호)** — "이 자리는 변수다"라는 표시입니다. 클라이언트가 `/hello/Alice`로 요청하면 FastAPI가 `Alice`를 추출해서 함수 인자로 넘겨줍니다.
2. **함수 인자 `name: str`** — 경로의 `{name}`과 **이름이 일치**해야 합니다. 타입은 `str`로 지정. 다른 이름이면 매핑이 안 돼 에러가 납니다.

> **이름이 일치해야 한다고요?** 네. 경로의 `{name}`과 함수 인자 `name`이 같은 단어여야 FastAPI가 자동으로 연결해 줍니다. `{user_name}`이라고 적으면 함수 인자도 `user_name: str`이어야 합니다.

> **타입을 `int`로 하면?** `@app.get("/items/{item_id}")` + `def get_item(item_id: int)` 식으로 적으면, FastAPI는 URL의 `{item_id}` 부분을 자동으로 정수로 변환해 줍니다. 변환 실패(예: `/items/abc`)면 자동으로 422 에러를 돌려줍니다. **이게 FastAPI의 자동 검증입니다.**

### 4.10.4 자동 문서 다시 확인

`http://127.0.0.1:8000/docs`를 다시 열어 봅니다. 이제 두 엔드포인트가 보입니다.

- `GET /` — Read Root
- `GET /hello/{name}` — Hello Name

새 라우트의 카드를 펼치면 **"Parameters"** 섹션에 `name` 항목이 자동으로 나타납니다. "Try it out" → `name`에 값 입력 → "Execute"로 직접 호출도 됩니다. **우리가 별도로 적은 문서가 하나도 없는데** 이게 자동으로 만들어진다는 점을 기억하세요.

### 4.10.5 경로 매개변수가 여러 개일 때 (맛보기)

다음 챕터에서 본격적으로 다루지만, 경로 매개변수는 여러 개를 둘 수 있습니다.

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int) -> dict[str, int]:
    return {"user_id": user_id, "post_id": post_id}
```

순서·이름이 일치하기만 하면 됩니다. 자세한 내용은 05장에서 라우팅을 깊이 다룰 때.

---

## 4.11 응답을 dict 대신 Pydantic 모델로 (맛보기)

지금까지 우리는 응답을 **`dict`**로 만들어 돌려줬습니다. 이 방식은 짧은 예제엔 편하지만, 응답의 형태가 코드 어디에서 결정되는지 한눈에 보기 어렵고, 자동 문서의 응답 스키마도 빈약하게 그려집니다(`{"message": "string"}` 정도).

해결책은 **Pydantic 모델**로 응답 형태를 명시하는 것입니다. 본격적인 Pydantic은 05장에서 다루지만, 한 번 맛만 보고 갑니다.

### 4.11.1 코드 수정

`app/main.py`를 다음처럼 한 번 더 확장합니다.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI
from pydantic import BaseModel


# 응답 데이터의 모양을 클래스로 명시한다.
# `BaseModel`을 상속한 클래스의 인스턴스는 FastAPI가 자동으로 JSON으로 직렬화한다.
class HelloResponse(BaseModel):
    """`/hello/{name}` 라우트의 응답 본문 형식."""

    message: str
    name: str


app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    """경로 매개변수 `name`을 받아 `HelloResponse`를 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!", "name": "Alice"}`
    """
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

저장합니다.

### 4.11.2 한 줄씩 풀이

```python
from pydantic import BaseModel


class HelloResponse(BaseModel):
    message: str
    name: str
```

- `BaseModel`은 Pydantic이 제공하는 **데이터 모델 베이스 클래스**입니다.
- 상속한 클래스의 **클래스 변수**(여기서는 `message`, `name`)를 **필드**로 봅니다.
- 각 필드에 타입 힌트(`: str`)가 있어, "어떤 타입의 값을 가질 수 있는지" Pydantic이 압니다.
- 이렇게 정의된 클래스는 다음 같은 일을 자동으로 해 줍니다.
  1. 인스턴스를 만들 때 인자 검증 (`HelloResponse(message=123, name="A")` → 에러)
  2. JSON으로 직렬화 (FastAPI가 자동으로 호출)
  3. 자동 문서의 응답 스키마에 정확한 모양 표시

```python
@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

- `response_model=HelloResponse` — 데코레이터에 추가된 인자. "이 라우트의 응답은 `HelloResponse` 형태다"라고 FastAPI에 알려줍니다.
- 함수 반환은 그 모델의 인스턴스를 만들어 돌려줍니다.

> **`response_model` 인자가 꼭 필요한가요?** 함수의 반환 타입 힌트(`-> HelloResponse`)만으로도 FastAPI는 자동 문서를 그립니다. 다만 **`response_model`을 명시하면 추가 안전망**이 생깁니다 — FastAPI가 응답을 그 모델로 한 번 더 검증·필터링합니다(예: 모델에 없는 필드는 잘라내기). 학습 단계에서는 둘 다 적어두는 걸 권장합니다. 자세한 차이는 05장에서.

### 4.11.3 자동 문서 다시 확인

`http://127.0.0.1:8000/docs`를 다시 열고 `GET /hello/{name}` 카드를 펼치면, **응답 스키마**(Responses 섹션)가 다음처럼 정확해집니다.

```
{
  "message": "string",
  "name": "string"
}
```

이전엔 `additionalProperties` 같은 모호한 표현이 들어갔지만, 이제는 **정확한 두 필드**가 명시됩니다. **클라이언트(프론트엔드·모바일) 개발자가 이 문서만 보고도 응답 형식을 정확히 알 수 있다**는 게 핵심 가치입니다.

> **본격적인 Pydantic은 05장에서**: 요청 본문 검증(`POST /users` 같은 곳), 필드 제약(`min_length=3` 등), 복합 모델, 옵셔널 필드, 모델 중첩 등 풍부한 주제가 있습니다. 이 챕터에서는 "응답에도 모델을 쓸 수 있다"는 사실만 가지고 넘어갑니다.

---

## 4.12 동기 함수(`def`) vs 비동기 함수(`async def`)

여기서 잠깐 옆길로 새서, FastAPI 입문자가 가장 자주 헷갈리는 주제 하나를 짚고 갑니다.

### 4.12.1 두 모양 다 지원된다

지금까지 우리는 **동기** 함수(`def`)로 라우트를 만들었습니다.

```python
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}
```

FastAPI는 **`async def`**도 똑같이 지원합니다.

```python
@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}
```

겉보기 차이는 `async` 한 단어뿐. 동작도 거의 같습니다 — 위 단순한 라우트에서는 **차이를 체감할 일이 없습니다.**

### 4.12.2 차이는 어디서 나오나

`async def`의 진가는 **함수 안에 `await`가 등장할 때** 나옵니다.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_user(user_id)   # ← DB가 응답을 줄 때까지 잠깐 비킨다
    return user
```

`await`이 걸린 줄에서 **이 함수는 잠깐 멈추고**, **그 시간에 다른 요청이 처리됩니다.** 한 서버가 동시에 많은 요청을 다룰 수 있는 비결이 이 비동기입니다.

> **비동기(async/await) 짧게 다시**:
> - **동기**: 한 줄을 끝내야 다음 줄로 간다. DB가 0.5초 걸리면 그동안 다른 일을 못 한다.
> - **비동기**: `await`이 걸린 곳에서 잠깐 비키고 다른 요청을 처리한다. 기다리는 시간이 많은 백엔드에서 큰 효과.
>
> 자세한 정의는 [용어 사전](glossary.md#비동기--동기-async--sync)에 있습니다.

### 4.12.3 그럼 우리는 뭘 써야 하나

**입문 단계의 결론**: 함수 안에 `await`를 쓸 일이 있으면 `async def`, 아니면 `def`로 써도 됩니다. FastAPI는 둘 다 잘 처리합니다.

다만 이 가이드의 약속은 다음과 같습니다.

- **DB·외부 API·파일 I/O를 호출하는 라우트는 `async def`로 작성한다** (06장부터 SQLAlchemy 비동기를 쓰면서 본격화).
- **순수 계산만 하는 작은 라우트는 `def`로 적어도 무방하다** (이 챕터의 라우트들이 그 예).
- **일관성을 위해 한 프로젝트 안에서는 거의 다 `async def`로 통일하는 패턴**도 흔하다 (실무 권장).

### 4.12.4 한 가지 함정

**`async def` 함수 안에서 `time.sleep()` 같은 동기 블로킹 호출을 쓰면 큰일납니다.** 그 시간 동안 서버 전체가 멈춥니다(이벤트 루프가 블로킹). 비동기에서는 항상 `await asyncio.sleep(...)`처럼 비동기 짝을 써야 합니다.

이 주제는 06장에서 비동기 DB를 다룰 때 다시 나옵니다. 지금은 "**async 함수에서 동기 블로킹 함수를 부르면 안 된다**"는 한 줄만 기억하세요.

> **이 챕터에서 굳이 `async def`로 안 쓴 이유**: 라우트 안에서 `await`을 쓸 일이 없으므로 둘 다 동작이 같습니다. 입문자에게는 처음 보는 키워드를 줄이는 쪽이 낫다고 판단했습니다. 06장부터는 자연스럽게 `async def`가 등장합니다.

---

## 4.13 서버 멈추기 / 다시 켜기

### 4.13.1 멈추기 — `Ctrl+C`

서버가 떠 있는 터미널에서 **`Ctrl+C`** 한 번을 누릅니다(`Cmd+C`가 아닙니다 — macOS에서도 터미널 종료 신호는 `Ctrl+C`).

```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [12346]
INFO:     Stopping reloader process [12345]
```

이런 메시지가 나오면 정상 종료입니다.

> **`Ctrl+C`를 두 번 누르면?** 거의 똑같이 종료되지만, 이미 종료 절차가 진행 중일 때 두 번 누르면 강제 종료가 될 수 있습니다(SIGINT 신호가 두 번 가서). 한 번만 누르고 잠깐 기다리는 게 안전합니다.

### 4.13.2 다시 켜기

같은 명령을 다시 실행합니다.

```bash
uv run uvicorn app.main:app --reload
```

코드가 그대로 보존돼 있다면 1~2초 안에 다시 떠 있습니다.

### 4.13.3 새 터미널에서 작업하기

서버가 떠 있는 터미널은 그 자체로 점유 상태입니다. 그 안에서 다른 명령을 치려면 일단 서버를 끄거나, **새 터미널을 하나 더 엽니다.**

- VS Code: 우상단의 `+` 아이콘 또는 `Ctrl+\`` 단축키로 통합 터미널을 추가.
- macOS Terminal: `Cmd+T`로 새 탭.
- iTerm2: `Cmd+T`로 새 탭, `Cmd+D`로 분할.

새 터미널에서 `cd`로 같은 프로젝트 폴더에 들어간 뒤 `curl`이나 `git` 같은 다른 명령을 칠 수 있습니다.

### 4.13.4 백그라운드 실행은?

`&`로 백그라운드 실행할 수도 있지만, 학습 단계에서는 **추천하지 않습니다.** 로그가 어느 터미널에서 나오는지 추적하기 어려워지고, 종료할 때도 PID를 찾아 `kill`해야 합니다. 그냥 한 터미널 = 한 서버 흐름을 유지하는 게 깔끔합니다.

---

## 4.14 트러블슈팅 — 자주 만나는 에러

### 4.14.1 `Error loading ASGI app. Could not import module "app.main".`

```
ERROR:    Error loading ASGI app. Could not import module "app.main".
```

가장 흔한 원인은 **현재 디렉터리**입니다. `uvicorn app.main:app` 명령은 "현재 폴더에 `app/` 폴더가 있고, 그 안에 `main.py`가 있다"고 가정합니다. 다른 폴더에서 명령을 치면 `app` 모듈을 못 찾습니다.

해결:

```bash
cd 04-HelloFastAPI    # 프로젝트 루트로 이동
uv run uvicorn app.main:app --reload
```

또 다른 원인은 **`app/__init__.py`가 없는 경우**입니다. 빈 파일이라도 반드시 있어야 `app/`이 패키지로 인식됩니다.

```bash
touch app/__init__.py
```

### 4.14.2 `Attribute "app" not found in module "app.main".`

```
ERROR:    Attribute "app" not found in module "app.main".
```

`app/main.py` 안에 `app = FastAPI(...)` 줄이 빠져 있거나, 변수 이름이 다른 경우입니다. 명령의 콜론 뒤(`:app`)와 코드의 변수 이름이 일치해야 합니다. `app`이 아니라 `application`으로 적었다면 명령을 `app.main:application`으로 바꾸거나, 코드를 `app`으로 통일하세요.

### 4.14.3 `[Errno 48] Address already in use` 또는 `[Errno 98] Address already in use`

```
ERROR:    [Errno 48] Address already in use
```

8000번 포트를 다른 프로세스(거의 항상 이전에 띄워두고 안 끈 uvicorn)가 쓰고 있습니다.

해결 방법 두 가지:

```bash
# 1) 8000을 쓰는 프로세스 찾아서 종료
lsof -i :8000
# PID를 확인해 kill (예: kill 12345)

# 2) 다른 포트로 띄우기
uv run uvicorn app.main:app --reload --port 8001
```

### 4.14.4 `ModuleNotFoundError: No module named 'fastapi'`

가상환경 안에 FastAPI가 깔리지 않았거나, 다른 Python을 쓰고 있을 때 납니다.

해결:

```bash
# 프로젝트 폴더에서
uv add fastapi "uvicorn[standard]"
# 그래도 안 되면
uv sync
```

또는 명령을 `uv run` 없이 쳤을 가능성. **항상 `uv run` 접두사를 잊지 마세요.**

```bash
# 잘못된 호출 (시스템 Python을 봄)
uvicorn app.main:app --reload
# 올바른 호출
uv run uvicorn app.main:app --reload
```

### 4.14.5 `--reload`인데 코드를 고쳐도 반영이 안 됨

대부분 두 가지 원인 중 하나입니다.

1. **저장(Save)을 안 한 경우**. VS Code에서 파일 탭에 점(●)이 보이면 미저장 상태. `Cmd+S`(macOS) 또는 `Ctrl+S`(Linux)로 저장.
2. **`uvicorn[standard]`가 아니라 그냥 `uvicorn`만 깔린 경우**. `--reload`에는 `watchfiles`가 필요한데, `[standard]` 묶음에 들어 있습니다.
   ```bash
   uv add "uvicorn[standard]"
   ```

### 4.14.6 `/docs`가 404로 나옴

```
{"detail":"Not Found"}
```

거의 100% **주소 오타**입니다. 정확히 `/docs`(슬래시 포함)인지 확인하세요. 또 다른 가능성으로, `FastAPI(docs_url=None)`처럼 docs를 일부러 끈 코드일 수도 있습니다. 우리 코드에는 그런 옵션이 없으니 보통 오타입니다.

### 4.14.7 한글이 응답에서 깨져 보임

이 가이드의 코드대로라면 한글이 그대로 출력돼야 합니다. 만약 깨져 보인다면:

- **터미널 인코딩**: macOS·최신 Linux는 UTF-8 기본. Windows CMD는 인코딩 문제가 잦으니 WSL2 권장.
- **브라우저**: 거의 모든 모던 브라우저는 UTF-8 기본. 의심되면 페이지 인코딩을 UTF-8로 바꿔 보세요.

### 4.14.8 VS Code가 `import fastapi`를 빨간 줄로 표시함

라이브러리는 깔렸는데 VS Code가 다른 인터프리터(예: 시스템 Python)를 보고 있는 상태입니다.

해결:

1. `Cmd+Shift+P`(macOS) / `Ctrl+Shift+P`(Linux) → **`Python: Select Interpreter`**.
2. 후보 중 `.venv` 안의 Python을 고릅니다 (`./.venv/bin/python` 같은 경로).
3. VS Code 창을 한 번 닫았다가 다시 열면 더 확실히 적용됩니다.

03장에서 이미 다뤘지만, 새 프로젝트마다 한 번씩 해줘야 합니다.

---

## 4.15 이 챕터의 변경 내역과 최종 코드

이번 챕터의 마지막 시점에서 `app/main.py`는 다음 모양이어야 합니다.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI
from pydantic import BaseModel


# 응답 데이터의 모양을 클래스로 명시한다.
# `BaseModel`을 상속한 클래스의 인스턴스는 FastAPI가 자동으로 JSON으로 직렬화한다.
class HelloResponse(BaseModel):
    """`/hello/{name}` 라우트의 응답 본문 형식."""

    message: str
    name: str


app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리.

    매우 단순한 환영 메시지를 JSON으로 돌려준다.
    """
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    """경로 매개변수 `name`을 받아 `HelloResponse`를 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!", "name": "Alice"}`
    """
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

`pyproject.toml`은 다음 모양이어야 합니다(버전 숫자는 시점에 따라 다름).

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 가이드 04장 — 첫 프로젝트 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
```

이 두 파일이 위 모양이고, `uv run uvicorn app.main:app --reload`가 에러 없이 떠서 `/`, `/hello/Alice`, `/docs`가 모두 응답한다면 이 챕터는 완성입니다.

> **완성된 예제 폴더**: 본 가이드 저장소의 `examples/04-HelloFastAPI/`에 같은 모양으로 정리되어 있습니다. 직접 친 코드가 동작하지 않으면 그쪽과 비교해 보세요.

---

## 4.16 이 챕터 체크리스트

다음을 모두 통과하면 다음 챕터로 넘어갈 준비가 된 것입니다.

- [ ] `~/projects/04-HelloFastAPI` 폴더를 만들고 `uv init`을 실행했다.
- [ ] `pyproject.toml`이 무엇인지, 어떤 항목이 들어 있는지 한 줄로 설명할 수 있다.
- [ ] `uv add fastapi "uvicorn[standard]"`로 의존성을 추가하고 `uv.lock`이 생긴 것을 확인했다.
- [ ] `app/__init__.py`가 빈 파일로 존재한다.
- [ ] `app/main.py`에 `FastAPI` 인스턴스 생성 + 두 개의 라우트(`/`, `/hello/{name}`) + Pydantic `HelloResponse` 모델이 들어 있다.
- [ ] `uv run uvicorn app.main:app --reload`로 서버가 8000번 포트에 떴다.
- [ ] 브라우저에서 `http://127.0.0.1:8000/`이 JSON을 돌려준다.
- [ ] 브라우저에서 `http://127.0.0.1:8000/hello/Alice`가 한국어 인사를 돌려준다.
- [ ] `http://127.0.0.1:8000/docs`(Swagger UI), `/redoc`(ReDoc), `/openapi.json` 세 페이지가 모두 보인다.
- [ ] `Ctrl+C`로 서버를 정상 종료할 수 있다.
- [ ] `app.main:app` 명령의 의미("`app/main.py` 파일의 `app` 변수")를 자기 말로 설명할 수 있다.

위가 모두 통과하면 **이 챕터의 본문은 완료**입니다. 다음 챕터(05)에서는 같은 골격 위에 라우팅과 Pydantic을 본격적으로 다룹니다.

---

## 4.17 이 챕터 요약

- 03장의 5줄 새너티 체크에서 출발해, **표준 폴더 구조**(`app/main.py`)를 갖춘 첫 프로젝트로 확장했다.
- `uv init`으로 `pyproject.toml`·`.python-version`·`.gitignore` 등이 자동 생성되며, 이 파일들이 프로젝트의 표준 메타데이터다.
- `uv add fastapi "uvicorn[standard]"` 한 줄로 가상환경·라이브러리 설치·잠금 파일 작성이 동시에 처리된다.
- FastAPI 앱의 핵심 패턴은 **`app = FastAPI(...)` + 데코레이터(`@app.get(...)`) + 처리기 함수**의 세 박자다.
- `uv run uvicorn app.main:app --reload`의 의미: "uv 환경 안에서 Uvicorn으로 `app/main.py`의 `app` 변수를 띄우고, 코드 변경 시 자동 재시작."
- FastAPI는 `/docs`(Swagger UI), `/redoc`(ReDoc), `/openapi.json`(원천 명세) 세 페이지를 자동 생성한다. 이게 FastAPI의 핵심 차별점이다.
- 경로 매개변수는 `@app.get("/hello/{name}")` + `def hello_name(name: str)`처럼 **이름 일치**로 자동 매핑된다.
- 응답을 `dict` 대신 `BaseModel` 모델로 돌려주면 자동 문서의 응답 스키마가 정확해지고, 이후 챕터의 검증·필터링 기능과 자연스럽게 이어진다.
- `def`와 `async def`는 둘 다 라우트로 쓸 수 있다. 입문 단계에서는 `await`이 필요할 때만 `async def`를 쓰는 게 단순하다.
- `Ctrl+C`로 서버를 끄고, 같은 명령으로 다시 띄운다.

다음 챕터에서는 같은 골격 위에 **여러 종류의 요청 입력**(쿼리 스트링, 본문)과 **본격적인 Pydantic 모델**(요청 검증, 필드 제약, 모델 중첩)을 다룹니다.

<a id="ch05"></a>

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

<a id="ch06"></a>

# 06. SQLAlchemy 2.0과 데이터베이스 연동 (SQLite / MySQL / PostgreSQL)

> **이 챕터의 목표**
> - 데이터베이스의 핵심 개념(테이블·행·열·기본 키·외래 키·트랜잭션)을 자기 말로 설명할 수 있다.
> - **ORM**이 무엇이고 왜 직접 SQL을 쓰는 것보다 입문자에게 유리한지 이해한다.
> - **SQLAlchemy 2.0의 비동기 API** (`AsyncEngine`, `AsyncSession`, `select(...)`)로 FastAPI 안에서 데이터를 읽고 쓸 수 있다.
> - SQLAlchemy 2.0의 새 표기법(`Mapped[...]`, `mapped_column(...)`)으로 모델을 선언한다.
> - **Pydantic 스키마**와 **ORM 모델**의 역할을 분리하고 `from_attributes=True`로 연결한다.
> - **Alembic**으로 마이그레이션을 만들고(`autogenerate`) 적용한다(`upgrade head`).
> - 같은 코드를 SQLite ↔ PostgreSQL ↔ MySQL 사이에서 **`DATABASE_URL`만 바꿔** 옮길 수 있다.
> - N+1 문제를 인식하고 `selectinload`로 첫 대응을 할 수 있다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터는 새 용어가 많아서 가장 자주 펼치게 될 챕터입니다.

> **소요 시간**: 4 ~ 6시간 (개념 → 실습 → 마이그레이션 → DB 전환 시도)

> **이 챕터의 위치**: 04장에서 첫 FastAPI 앱을 띄웠고, 05장에서 라우팅과 Pydantic으로 JSON을 주고받는 법을 배웠습니다. 이제 데이터를 **메모리에 두지 않고 디스크의 데이터베이스**에 저장하는 단계입니다. 여기서 만든 토대 위에 07장(Todo CRUD), 08장(인증), 10·11장(종합 예제)이 모두 올라갑니다.

---

## 6.1 왜 데이터베이스가 필요한가

지금까지 우리가 짠 코드는 모두 **메모리**에 데이터를 둔 상태였습니다. 04·05장에서 만든 작은 라우트들은 함수가 끝나면 변수도 사라지고, 서버를 끄면 모든 자료가 증발합니다. 그래도 학습 단계에서는 충분했습니다.

하지만 실제 백엔드는 **요청과 요청 사이에 자료가 살아 있어야** 합니다. 사용자가 회원가입한 정보, 작성한 글, 올린 사진의 위치 — 이 모든 것을 어딘가 안전한 곳에 적어 두고, 다음 요청 때 다시 꺼내야 합니다. 그 "어딘가 안전한 곳"이 바로 **데이터베이스**입니다.

> **데이터베이스(database, DB)란?** 자료를 표(table) 형태로 모아 두고, 빠르게 검색하고 수정할 수 있게 해주는 저장소 프로그램입니다. 우리는 흔히 "DB에 저장한다"는 말을 씁니다.

> **DBMS(Database Management System)란?** 데이터베이스를 다루는 프로그램 본체입니다. **PostgreSQL, MySQL, SQLite** 등이 모두 DBMS입니다. 흔히 "DB"라고 줄여 말하면 둘 중 어느 쪽을 가리키는지 문맥으로 구분합니다.

### 6.1.1 메모리 저장 vs 데이터베이스 저장

| 비교 | 메모리(파이썬 dict / list) | 데이터베이스 |
|------|--------------------------|--------------|
| 서버 재시작 후 | 모두 사라짐 | 그대로 남아 있음 |
| 여러 프로세스가 공유 | 안 됨 | 됨 |
| 검색 속도 | 자료가 적으면 빠름, 많으면 느려짐 | 인덱스로 매우 빠름 |
| 동시 수정 안전성 | 별도 락이 필요 | 트랜잭션으로 안전 |
| 디스크에 저장 | 안 됨 | 기본 |
| 다른 도구로 읽기 | 어려움 | SQL/도구로 누구나 |

서버가 한 번이라도 다시 실행되거나, 여러 사람이 동시에 자료를 만지거나, 자료가 많아지는 순간 **메모리만으로는 더 못 버팁니다.** 그래서 거의 모든 백엔드는 데이터베이스를 끼고 동작합니다.

### 6.1.2 이 가이드가 다루는 DB의 종류

| DBMS | 한 줄 소개 | 이 가이드의 위치 |
|------|----------|------------------|
| **SQLite** | 파일 하나로 동작하는 가벼운 DB | **개발·학습용 기본** — 별도 서버 불필요 |
| **PostgreSQL** | 가장 표준적인 오픈소스 DB | 운영 환경 권장 — 10·11장 배포에서 사용 |
| **MySQL** | 가장 널리 쓰이는 오픈소스 DB | 회사·기존 코드와 통합할 때 사용 |

이 챕터에서는 **SQLite로 시작합니다.** 별도 DB 서버를 깔 필요가 없어서 환경 구축이 가장 빠르고, SQLAlchemy로 작성한 코드는 나중에 **DB URL만 바꾸면 PostgreSQL/MySQL에서도 그대로 동작**합니다. 이 점이 ORM의 가장 큰 실용적 장점입니다.

---

## 6.2 데이터베이스 개념 빠른 복습

여기까지 한 번도 SQL을 본 적 없어도 따라올 수 있도록 핵심 용어만 짧게 정리합니다. 이미 익숙하다면 6.3으로 건너뛰어도 됩니다.

### 6.2.1 테이블·행·열

자료는 **표(table)** 형태로 저장됩니다. 표의 가로줄 한 개가 자료 한 건이고, 세로줄 한 개가 속성 한 가지입니다.

```
┌──────────────────────  todos 테이블  ──────────────────────┐
│  id  │ title          │ is_done │ created_at              │
├──────┼────────────────┼─────────┼─────────────────────────┤
│  1   │ 우유 사기      │ false   │ 2026-04-25 10:00:00      │   ← 행(row) 하나
│  2   │ 빨래 돌리기   │ true    │ 2026-04-25 11:30:00      │
│  3   │ 보고서 쓰기   │ false   │ 2026-04-25 12:00:00      │
└──────┴────────────────┴─────────┴─────────────────────────┘
   ↑          ↑              ↑              ↑
   열(column)이 4개
```

> **테이블(table)이란?** 자료를 표 형태로 모은 단위입니다. 흔히 "엑셀 시트 한 장"으로 비유합니다. 위 예시에서 `todos`는 테이블 이름입니다.

> **행(row, record)이란?** 표의 가로줄 한 개입니다. 자료 한 건을 의미합니다. "1번 할 일"은 한 행입니다.

> **열(column, field)이란?** 표의 세로줄 한 개입니다. 속성 하나를 나타냅니다. `title`, `is_done`은 열입니다. 각 열은 미리 정해진 **타입**(문자열·정수·날짜 등)을 가집니다.

### 6.2.2 기본 키 (Primary Key)

표 안에서 **각 행을 유일하게 가리키는 열**입니다. 보통 `id`라는 이름의 정수 자동 증가 열을 씁니다.

> **기본 키(Primary Key, PK)란?** 행 하나를 다른 행과 구별해 주는 열입니다. 두 행이 같은 PK 값을 가질 수 없습니다(중복 금지). 우리는 보통 정수 `id`를 PK로 두고 1, 2, 3, ... 자동으로 번호를 매깁니다.

PK 덕분에 "3번 todo 가져와", "5번 user 지워"처럼 **하나를 콕 집어 가리킬** 수 있습니다.

### 6.2.3 외래 키 (Foreign Key)

다른 표의 PK를 가리키는 열입니다. 표 사이의 **연결**을 표현합니다.

```
users 테이블                       posts 테이블
┌────┬───────┐                    ┌────┬─────────┬──────────┐
│ id │ email │                    │ id │ title   │ user_id  │
├────┼───────┤                    ├────┼─────────┼──────────┤
│ 1  │ a@... │ ◄──────────────┐  │ 11 │ 첫 글  │   1      │
│ 2  │ b@... │                  │  │ 12 │ 두번째 │   1      │
└────┴───────┘                  │  │ 13 │ 다른 글│   2      │
                                  │  └────┴─────────┴──────────┘
                                  │              ↑
                                  └─── 이 user_id가 외래 키. users.id를 가리킴
```

> **외래 키(Foreign Key, FK)란?** 다른 테이블의 PK를 참조하는 열입니다. "이 글의 작성자(=`user_id`)는 users 테이블의 그 사용자"라는 연결을 표현합니다. DB는 잘못된 FK 값(예: 존재하지 않는 user를 가리키는 값)이 들어오는 것을 자동으로 막을 수 있습니다.

이 챕터의 예제는 표가 하나(Todo)뿐이라 외래 키가 등장하지 않습니다. 11장 Blog API에서 본격적으로 다룹니다.

### 6.2.4 인덱스

자주 검색하는 열에 미리 만들어 두는 "찾아보기" 자료구조입니다.

> **인덱스(index)란?** 책의 색인처럼 "이 값이 어느 행에 있는지"를 미리 정리해 둔 표입니다. `WHERE email = 'a@b.com'` 같은 검색을 매우 빠르게 합니다. 단점은 디스크 공간을 더 쓰고, INSERT/UPDATE 시 인덱스도 함께 갱신해야 해 살짝 느려진다는 점입니다. 자주 검색하는 열에만 만드는 게 원칙입니다.

### 6.2.5 SQL — 데이터베이스에게 말하는 언어

데이터베이스에 "이런 자료를 가져와줘", "이 자료를 새로 넣어줘"라고 지시할 때 쓰는 언어가 **SQL**입니다.

> **SQL(Structured Query Language)이란?** 관계형 DB를 다루는 표준 언어입니다. "구조화된 질의 언어"라는 뜻이고, 보통 "씨퀄" 또는 "에스큐엘"로 읽습니다.

가장 자주 보는 네 가지:

```sql
-- SELECT: 자료 가져오기
SELECT * FROM todos WHERE is_done = false;

-- INSERT: 새 자료 만들기
INSERT INTO todos (title, is_done) VALUES ('우유 사기', false);

-- UPDATE: 자료 수정
UPDATE todos SET is_done = true WHERE id = 1;

-- DELETE: 자료 지우기
DELETE FROM todos WHERE id = 1;
```

이 가이드는 **직접 SQL을 쓰지 않습니다.** 대신 SQLAlchemy(ORM)를 통해 파이썬 코드로 같은 일을 합니다. 다만 ORM이 내부에서 만들어 보내는 SQL이 이런 모양이라는 점은 알고 있어야, 문제가 생겼을 때 디버깅이 가능합니다.

### 6.2.6 트랜잭션

여러 SQL을 **한 묶음으로 실행**하고, 도중에 어느 하나라도 실패하면 전체를 되돌리는 단위입니다.

> **트랜잭션(transaction)이란?** "이 SQL 묶음은 전부 성공하거나 전부 취소되어야 한다"는 안전장치입니다. 송금이 대표적입니다 — A 통장에서 1만원 빼고 B 통장에 1만원 넣는 두 SQL이 둘 다 성공하거나 둘 다 취소되어야지, 한쪽만 성공하면 큰일이 납니다. SQLAlchemy 세션이 트랜잭션을 자동으로 시작/커밋/롤백합니다.

세 가지 핵심 동작:

- **commit** — "여기까지 한 작업을 진짜 디스크에 반영해 줘"
- **rollback** — "지금까지 한 작업을 모두 취소해 줘"
- **자동 시작** — 세션을 만들면 트랜잭션이 자동으로 열립니다

이 챕터에서 우리가 직접 부를 일은 거의 `await session.commit()` 하나뿐입니다. 나머지는 SQLAlchemy/FastAPI가 알아서 합니다.

---

## 6.3 ORM이란 무엇이고 왜 쓰는가

### 6.3.1 정의

> **ORM(Object Relational Mapper)이란?** 데이터베이스의 표(테이블)와 프로그래밍 언어의 객체(클래스)를 자동으로 연결해 주는 도구입니다. SQL을 직접 쓰지 않고도 파이썬 객체를 다루듯 DB를 다룰 수 있습니다.

이름이 어렵게 느껴질 수 있습니다. 풀어 쓰면 다음 비교가 거의 전부입니다.

### 6.3.2 같은 일, 두 가지 방법

"3번 할 일을 가져와서 완료 표시하기"를 두 방식으로 비교해 봅니다.

**SQL을 직접 쓸 때:**

```python
# 1) DB 연결을 가져온다
conn = some_db_lib.connect(url)
cur = conn.cursor()

# 2) SELECT 쿼리를 문자열로 만들어 보낸다
cur.execute("SELECT id, title, is_done FROM todos WHERE id = ?", (3,))
row = cur.fetchone()

if row is None:
    raise HTTPException(404)

# 3) 튜플에서 직접 위치로 값을 꺼낸다 — 어느 위치가 어느 열인지 외워야 함
todo_id, title, is_done = row

# 4) UPDATE 쿼리도 문자열로
cur.execute("UPDATE todos SET is_done = ? WHERE id = ?", (True, 3))
conn.commit()
```

**SQLAlchemy ORM을 쓸 때:**

```python
# 1) 세션 의존성으로 받아오면 됨 (FastAPI가 자동 주입)
todo = await session.get(Todo, 3)

if todo is None:
    raise HTTPException(404)

# 2) 그냥 파이썬 객체의 속성을 바꾼다
todo.is_done = True

# 3) commit만 부르면 ORM이 알아서 UPDATE를 만들어 보낸다
await session.commit()
```

같은 일을 다른 방식으로 표현했을 뿐이지만, 두 번째 코드의 장점이 분명합니다.

### 6.3.3 ORM이 주는 이득

1. **SQL 인젝션 자동 방지** — `WHERE id = ?` 자리에 사용자 입력을 직접 끼워 넣지 않으므로, 악의적인 입력으로 DB를 망가뜨리는 공격을 막아 줍니다.
2. **타입 안전과 자동 완성** — `todo.title`, `todo.is_done`을 IDE가 인식해 자동 완성과 오타 검출을 해 줍니다. SQL 문자열 안의 오타는 IDE가 잡아 주지 않습니다.
3. **DB 종류에 덜 의존적** — SQLite로 짠 ORM 코드는 PostgreSQL/MySQL에서도 거의 그대로 동작합니다. SQL은 종류별로 미묘한 차이(예: `LIMIT` 표기)가 있어 그대로 옮기기 어렵습니다.
4. **모델 = 단일 진실 공급원** — 표 구조를 파이썬 클래스에 한 번만 적으면, 그 정의가 마이그레이션·쿼리·응답 구조에 모두 재사용됩니다.
5. **관계를 객체처럼 다룸** — `user.posts`처럼 자연스러운 표기로 1:N 관계의 자료를 가져올 수 있습니다.

### 6.3.4 ORM의 단점과 현실

ORM은 만능이 아닙니다. 단점도 정직하게 짚고 갑니다.

- **느린 학습** — 새 도구의 API와 약속을 익혀야 합니다. 본 챕터에서 압축해 다룹니다.
- **복잡한 쿼리에서는 SQL이 더 깔끔** — 통계·집계 쿼리(예: 월별 주문 합계, 윈도우 함수)는 SQL이 더 직관적입니다. SQLAlchemy는 필요할 때 raw SQL을 섞어 쓸 수도 있습니다.
- **N+1 문제** — ORM 표기로 무심코 짜면 쿼리가 N+1번 나가는 비효율이 잘 생깁니다(6.16에서 다룸).
- **추상화의 누수** — 결국 어느 시점에는 "ORM이 뒤에서 무슨 SQL을 만드는지" 봐야 합니다. SQLAlchemy는 `echo=True` 옵션으로 SQL을 다 찍어 줍니다.

> **결론**: 입문 단계와 일반 CRUD에서는 ORM이 압도적으로 편하고 안전합니다. 통계 분석이 핵심인 코드만 부분적으로 SQL로 내려가면 됩니다. 이 가이드는 그 입문 단계에 집중합니다.

### 6.3.5 왜 SQLAlchemy인가

파이썬 ORM 후보는 여러 개가 있습니다.

- **SQLAlchemy 2.0** ← 이 가이드의 선택
- **Django ORM** — Django 프레임워크와 묶여 있음. FastAPI와 결합 어려움
- **SQLModel** — FastAPI 저자가 만든 라이브러리. 사실상 SQLAlchemy의 얇은 래퍼
- **Tortoise ORM** — 비동기 전용. 사용자 풀이 작음

이 가이드가 SQLAlchemy 2.0을 못 박은 이유:

1. **가장 널리 쓰이는 파이썬 ORM** — 회사에서 만나는 백엔드 코드의 대다수가 SQLAlchemy를 씁니다.
2. **FastAPI 공식 튜토리얼이 SQLAlchemy 사용** — 표준 경로입니다.
3. **2.0에서 비동기와 타입 표기가 매우 깔끔해짐** — `Mapped[...]` 표기가 IDE의 도움을 가장 많이 받습니다.
4. **Alembic이 거의 표준 마이그레이션 도구** — SQLAlchemy 2.0 + Alembic 한 쌍이 사실상 정답입니다.

---

## 6.4 비동기 ORM과 `AsyncSession`

### 6.4.1 왜 비동기 DB가 중요한가

FastAPI는 비동기(async) 프레임워크라고 1·5장에서 짧게 언급했습니다. 비동기의 가장 큰 효과는 **DB·외부 API처럼 "기다리는" 작업**에서 나타납니다.

> **비동기 I/O란?** "디스크/네트워크 응답이 올 때까지 기다리는 동안, 같은 워커가 다른 요청을 처리할 수 있게 하는" 방식입니다. DB 쿼리가 0.05초 걸린다면, 그 0.05초 동안 다른 요청이 처리됩니다. 동기 방식은 그 시간 동안 멍하니 막혀 있습니다.

```python
# 동기 (옛날 방식)
def get_todos():
    rows = db.execute("SELECT * FROM todos")   # 여기서 실제로 멈춰 기다림
    return rows

# 비동기 (FastAPI + SQLAlchemy 2.0)
async def get_todos(session):
    result = await session.execute(select(Todo))   # 기다리는 동안 다른 요청 처리 가능
    return result.scalars().all()
```

차이는 코드 두 글자(`async`, `await`)뿐이지만, 동시 처리량이 크게 달라집니다. 특히 트래픽이 많은 서비스에서 비용 절감 효과가 큽니다.

### 6.4.2 SQLAlchemy 2.0의 비동기 API

SQLAlchemy 2.0은 다음 한 쌍이 비동기의 핵심입니다.

| 이름 | 역할 |
|------|------|
| **`AsyncEngine`** | DB와의 연결 풀(여러 연결의 묶음). 앱 시작 시 한 개 만들어 두고 끝까지 재사용 |
| **`AsyncSession`** | 한 묶음의 DB 작업(보통 한 요청에 한 개)을 처리하는 객체. 트랜잭션 단위 |

이 두 개의 관계는 다음과 같습니다.

```
   AsyncEngine (연결 풀, 앱 전체에 1개)
        │
        ├── 요청 A → AsyncSession A → 한 트랜잭션
        ├── 요청 B → AsyncSession B → 한 트랜잭션
        ├── 요청 C → AsyncSession C → 한 트랜잭션
        ...
```

**FastAPI 안에서의 흐름**은 이렇게 됩니다.

1. 앱 시작 시: `AsyncEngine`을 한 번 만든다.
2. 요청 들어옴: 의존성 함수 `get_session()`이 새 `AsyncSession`을 만들어 라우트에 주입한다.
3. 라우트가 동작: `await session.execute(...)`, `session.add(...)` 등으로 DB 작업.
4. 라우트 종료: 의존성 함수가 `commit` 또는 `rollback`을 처리하고 세션을 닫는다.

자세한 구현은 6.6에서 코드로 보여 드립니다.

### 6.4.3 비동기 드라이버 — DB 종류별로 별도

SQLAlchemy 2.0의 비동기 API를 쓰려면 DB 종류에 맞는 **비동기 드라이버 라이브러리**도 같이 깔아야 합니다.

> **DB 드라이버(driver)란?** 파이썬 코드와 실제 DB 사이를 통역하는 작은 라이브러리입니다. SQLAlchemy 자체는 "어느 DB든 다룰 수 있는 공통 인터페이스"이고, 실제로 PostgreSQL과 통신하려면 PostgreSQL용 드라이버가 추가로 필요합니다.

이 가이드의 표준은 다음과 같습니다.

| DB | 비동기 드라이버 | 설치 명령 |
|----|------------------|-----------|
| **SQLite** | `aiosqlite` | `uv add aiosqlite` |
| **PostgreSQL** | `asyncpg` | `uv add asyncpg` |
| **MySQL** | `asyncmy` | `uv add asyncmy` |

이 챕터는 SQLite로 시작하므로 `aiosqlite`만 깝니다. 다른 DB로 옮길 때 추가로 깔면 됩니다.

> **왜 같은 DB에 동기/비동기 드라이버가 따로 있나요?** 비동기 함수는 안에서 진짜로 비동기로 동작해야 합니다. 옛날 동기 드라이버를 그대로 쓰면 "기다리는 동안 멈춰 있는" 동기 동작이 되어 비동기의 의미가 사라집니다. 그래서 `aiosqlite`/`asyncpg`/`asyncmy` 같은 비동기 전용 드라이버가 필요합니다.

---

## 6.5 SQLAlchemy 2.0의 새 표기법

SQLAlchemy 2.0은 1.x에 비해 모델 정의 표기가 크게 바뀌었습니다. 옛 코드와 새 코드가 인터넷에 섞여 있어 혼란스러울 수 있어, 새 표기법(2.0 스타일)을 짧게 미리 보여드립니다.

### 6.5.1 새 표기법: `Mapped[...]`와 `mapped_column(...)`

```python
from datetime import datetime, timezone
from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """모든 모델의 부모 클래스."""
    pass

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )
```

각 줄이 무엇을 의미하는지 풀어 봅니다.

- **`__tablename__ = "todos"`** — DB의 테이블 이름. 관례는 복수형 snake_case.
- **`Mapped[int]`** — "이 속성은 파이썬에서 `int` 타입이고, DB의 어떤 정수 열에 매핑된다"는 표시. IDE가 이 정보를 읽고 자동 완성과 타입 검사를 해 줍니다.
- **`mapped_column(...)`** — DB 열의 세부 옵션(타입·길이·기본값·PK 여부 등)을 지정. 인자가 없으면 SQLAlchemy가 `Mapped[...]`의 타입을 보고 적당한 기본값을 씁니다.
- **`primary_key=True`** — 이 열이 PK(기본 키)임을 표시. 정수 PK는 자동 증가가 기본.
- **`String(200)`** — VARCHAR(200) 타입. 길이를 명시하면 DB 측에서 길이 제한을 강제합니다.
- **`default=False`** — 새 행을 만들 때 값이 안 들어오면 이 기본값.

### 6.5.2 옛 표기법(1.x)과의 비교

옛 코드는 이런 식이었습니다.

```python
# 옛날 (SQLAlchemy 1.4 스타일) — 이 가이드는 안 씁니다
from sqlalchemy import Column, Integer, String, Boolean

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    is_done = Column(Boolean, default=False)
```

옛 표기법은 IDE가 `todo.title`의 타입을 모릅니다(`Column[str]`까지밖에 못 따라감). 새 표기법(`Mapped[str]`)은 IDE가 정확히 `str`로 추론합니다. **새 프로젝트는 항상 2.0 표기법을 쓰세요.**

### 6.5.3 `Mapped[...]`의 흔한 타입

| Mapped 타입 | DB 타입 (기본 매핑) | 설명 |
|-------------|---------------------|------|
| `Mapped[int]` | INTEGER | 정수. PK로 자주 사용 |
| `Mapped[str]` | VARCHAR | 문자열. `String(200)`처럼 길이 지정 권장 |
| `Mapped[bool]` | BOOLEAN | 참/거짓 |
| `Mapped[float]` | FLOAT | 실수 |
| `Mapped[datetime]` | TIMESTAMP / DATETIME | 날짜+시간 |
| `Mapped[date]` | DATE | 날짜만 |
| `Mapped[bytes]` | BLOB / BYTEA | 바이너리 데이터 |
| `Mapped[Optional[str]]` 또는 `Mapped[str \| None]` | NULL 허용 VARCHAR | nullable 열 |

> **NULL 허용을 표기하는 두 방식**: `Mapped[Optional[str]]`(파이썬 3.9 이전 호환)과 `Mapped[str | None]`(파이썬 3.10+). 이 가이드는 3.13을 쓰므로 후자를 권장합니다. 둘 다 동작합니다.

---

## 6.6 `db.py` 작성 — Engine, Session, 의존성

이제 손을 움직입니다. **표준 프로젝트 구조**(README의 약속과 동일)는 다음과 같습니다.

```
06-SQLAlchemyTodo/
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
└── app/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── db.py            ← 이 절에서 만드는 파일
    ├── models.py
    └── schemas.py
```

### 6.6.1 새 프로젝트 만들기

03장에서 익힌 흐름과 같습니다.

```bash
mkdir 06-SQLAlchemyTodo
cd 06-SQLAlchemyTodo

uv init
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite
```

`uv add` 한 줄로 다음이 한꺼번에 들어옵니다.

- **`fastapi`** — 웹 프레임워크 본체
- **`uvicorn[standard]`** — ASGI 서버
- **`sqlalchemy`** — ORM 본체 (2.x를 자동으로 가져옵니다)
- **`alembic`** — 마이그레이션 도구
- **`aiosqlite`** — SQLite용 비동기 드라이버

설치가 끝나면 `app/` 폴더와 빈 `__init__.py`를 만듭니다.

```bash
mkdir -p app
touch app/__init__.py
```

### 6.6.2 `app/config.py` — DATABASE_URL 설정

DB 접속 주소(=`DATABASE_URL`)는 코드에 직접 박지 않고 **환경 변수**로 분리합니다. 환경마다(개발·테스트·운영) 다른 DB를 가리키도록 하기 위함입니다.

> **환경 변수(environment variable)란?** 운영체제가 프로세스에 전달하는 키-값 쌍입니다. 비밀번호·접속 주소처럼 "코드에 박으면 안 되는 값"을 운영체제 쪽에서 주입할 수 있게 합니다. 개발 중에는 `.env` 파일에 적어 두고 라이브러리가 그걸 읽어들입니다.

```python
# app/config.py
import os

# 개발 기본값: 현재 폴더에 todo.db 라는 SQLite 파일을 사용한다.
# 실제 운영에서는 환경 변수 DATABASE_URL 을 PostgreSQL 등의 주소로 바꾼다.
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo.db",
)
```

> **`sqlite+aiosqlite:///./todo.db`의 형식**: `드라이버명+비동기드라이버명:///경로`. 콜론과 슬래시 개수에 주의(`:///`로 슬래시 세 개). `./todo.db`는 "현재 작업 폴더의 todo.db 파일"이라는 뜻입니다. 메모리 SQLite를 쓰려면 `sqlite+aiosqlite:///:memory:`.

다른 DB의 URL 형식도 미리 표로 정리합니다(이 챕터 끝의 6.17에서 다시).

| DB | DATABASE_URL 예시 |
|----|---------------------|
| SQLite (파일) | `sqlite+aiosqlite:///./todo.db` |
| SQLite (메모리, 테스트용) | `sqlite+aiosqlite:///:memory:` |
| PostgreSQL | `postgresql+asyncpg://user:pass@localhost:5432/mydb` |
| MySQL | `mysql+asyncmy://user:pass@localhost:3306/mydb` |

### 6.6.3 `app/db.py` — Engine과 Session 만들기

이 가이드의 가장 중요한 인프라 파일입니다. 한 번 잘 만들어 두면 이후 챕터들이 모두 이걸 그대로 씁니다.

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

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    """모든 ORM 모델이 상속할 부모 클래스.

    이 클래스를 상속받은 클래스들이 모이면 SQLAlchemy 가
    "어떤 테이블들이 존재해야 하는가"를 알 수 있게 된다.
    """
    pass


# 1) 비동기 엔진 — 앱 전체에서 한 개만 만든다.
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,           # True 로 두면 모든 SQL 문이 콘솔에 찍힌다(디버깅용)
    future=True,
)

# 2) 세션 팩토리 — 요청마다 새 AsyncSession 을 만들어 주는 함수.
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,   # commit 후에도 객체 속성에 접근 가능하게 한다
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성 함수.

    한 요청마다 한 개의 세션을 만들고, 라우트가 끝나면
    자동으로 commit (성공 시) 또는 rollback (예외 시) 하고 닫는다.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            # 라우트 안에서 예외가 발생하면 트랜잭션을 되돌린다
            await session.rollback()
            raise
        else:
            # 라우트가 정상 종료되면 commit
            await session.commit()
```

각 부분을 풀어 설명합니다.

- **`Base`**: 모든 모델 클래스의 부모. 06.5에서 본 그것입니다. ORM 모델들이 다 이걸 상속합니다.
- **`create_async_engine(DATABASE_URL, ...)`**: 비동기 엔진을 만듭니다.
  - `echo=False`: SQL 로그를 안 찍습니다. 디버깅 시에만 `True`.
  - `future=True`: 2.0 스타일을 사용한다는 명시(2.0에서는 사실 기본).
- **`async_sessionmaker(bind=engine, ...)`**: "이 엔진에 연결된 세션을 만들어 주는 공장"입니다. 호출하면 새 `AsyncSession`을 반환합니다.
  - `expire_on_commit=False`: commit 후에도 ORM 객체의 속성에 접근할 수 있게 합니다(기본 `True`이면 commit 직후 객체가 "유효 기한 만료" 상태가 되어 다시 로드해야 함). FastAPI에서는 거의 항상 `False`로 둡니다.
  - `autoflush=False`: 자동 flush를 끕니다(취향). 입문 단계에서는 이게 더 이해하기 쉽습니다.
- **`get_session()`**: FastAPI의 **의존성 함수**입니다. `Depends(get_session)`으로 라우트가 받게 됩니다. 한 요청에 한 세션이 만들어지고, 끝나면 자동으로 commit·close 됩니다.

> **`async with SessionLocal() as session:`이란?** 비동기 컨텍스트 매니저입니다. 블록을 벗어나면 자동으로 `await session.close()`가 호출됩니다. 우리는 명시적으로 close를 호출할 필요가 없습니다.

> **`yield session`은 왜 쓰나요?** FastAPI의 의존성 함수에서 `yield`는 "여기까지가 사전 처리, 라우트가 끝나면 다시 돌아오라"는 뜻입니다. 위 코드에서 라우트 함수가 모두 끝난 뒤에야 `else: await session.commit()` 또는 `except`가 실행됩니다.

### 6.6.4 의존성 함수의 동작 흐름 정리

`get_session`이 한 요청 동안 어떤 순서로 도는지 그림으로 정리합니다.

```
요청 들어옴
   │
   ▼
get_session() 호출
   ├─ SessionLocal() 로 새 AsyncSession 생성 (← async with __aenter__)
   ├─ try 블록 진입
   │
   ▼ (yield)  ←── 라우트 함수 실행 (예: create_todo, get_todo, ...)
   │              ─ 라우트가 session.add, session.execute 등을 호출
   │              ─ 라우트가 정상 종료 또는 예외 발생
   ▼
case 정상 종료:  await session.commit()    ← else 블록
case 예외 발생:  await session.rollback()  ← except 블록 + raise
   │
   ▼
async with 블록 종료 (← async with __aexit__)
   └─ session 이 자동으로 close 된다
   │
   ▼
요청 종료
```

이 한 함수만 한 번 잘 짜 두면, 라우트들은 단지 `session: AsyncSession = Depends(get_session)`을 인자로 받기만 하면 끝입니다. **commit이나 rollback을 직접 부를 일이 거의 없어집니다.**

---

## 6.7 모델 정의 — `Todo`

`app/models.py`에 첫 ORM 모델을 만듭니다.

```python
# app/models.py
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Todo(Base):
    """할 일 한 건을 표현하는 ORM 모델 (todos 테이블에 매핑)."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Todo id={self.id} title={self.title!r} is_done={self.is_done}>"
```

설명:

- **`__tablename__ = "todos"`**: DB에 만들어질 테이블 이름.
- **`id`**: PK. `primary_key=True`만 주면 정수 자동 증가가 기본입니다.
- **`title`**: VARCHAR(200). 200자 제한. 200자가 너무 작거나 큰 것 같다면 프로젝트 요구사항에 맞춰 조정.
- **`is_done`**: BOOLEAN. 기본값 `False` — 새로 만든 할 일은 미완료.
- **`created_at`**: 만든 시각. `default=lambda: datetime.now(timezone.utc)`로 자동 채움. **UTC 시각을 저장하는 것이 표준입니다.** 지역 시간대는 응답 시점에 변환합니다.

> **왜 `datetime.utcnow`를 안 쓰나요?** Python 3.12부터 `datetime.utcnow()`는 **deprecated** 입니다(naive datetime을 돌려줘서 timezone 정보가 없습니다). 대신 명시적으로 `datetime.now(timezone.utc)`를 써서 UTC임을 분명히 합니다. `from datetime import datetime, timezone` 한 줄로 둘 다 import 합니다.

> **왜 함수를 호출하지 않고 `lambda`로 감싸 넘기나요?** `default=datetime.now(timezone.utc)`처럼 호출 결과를 넘기면 **모듈이 import되는 시점**의 시간이 박혀버립니다. 우리가 원하는 건 "행이 만들어질 때마다 그때의 시간"이므로, 함수 객체(여기서는 `lambda`)를 넘겨 SQLAlchemy가 INSERT 직전에 호출하도록 합니다.

> **`__repr__`은 꼭 필요하나요?** 디버깅용입니다. `print(todo)` 했을 때 보기 좋게 출력됩니다. 운영에 영향은 없습니다.

### 6.7.1 모델은 어디서 import되어야 하는가

마이그레이션이 모델을 발견하려면 어딘가에서 **이 클래스가 한 번은 import되어야** 합니다. 안 그러면 `Base.metadata`에 등록되지 않아 Alembic이 모릅니다. 이 가이드는 `app/main.py`에서 `from app.models import Todo`로 import하므로 자동으로 등록됩니다.

큰 프로젝트에서는 `app/models/__init__.py`에서 모든 모델을 한꺼번에 import해 두는 패턴이 흔합니다(11장 Blog API에서 다룸).

---

## 6.8 Pydantic 스키마와 ORM 모델의 분리

5장에서 Pydantic으로 요청·응답을 검증하는 법을 배웠습니다. 이제 그 Pydantic 스키마와 6.7에서 만든 ORM 모델을 어떻게 함께 쓸지 정리합니다.

### 6.8.1 왜 두 종류의 클래스가 필요한가

같은 "Todo"를 표현하는 클래스가 두 개 있는 게 처음에는 이상하게 느껴집니다. 이유를 정리합니다.

| | ORM 모델 (`models.py::Todo`) | Pydantic 스키마 (`schemas.py::TodoRead` 등) |
|--|------------------------------|---------------------------------------------|
| 역할 | DB 테이블에 매핑된 객체 | 요청·응답의 JSON 모양 |
| 가지는 정보 | DB의 모든 열 (PK, FK, 내부 플래그까지) | 외부에 보일/받을 필드만 |
| 사용처 | 라우트 안에서 DB 작업 | 라우트의 인자(요청)와 반환값(응답) |
| 변경 영향 | DB 마이그레이션이 따라옴 | 외부 API 호환성에 영향 |

**핵심**: ORM 모델과 외부 API의 모양은 자주 다릅니다. 예를 들어:

- **회원가입 요청**에는 `password`(평문)가 들어 있지만, **DB**에는 `password_hash`만 저장합니다. **응답**에는 어느 쪽도 안 나갑니다.
- **DB**에는 `is_deleted` 같은 내부 플래그가 있을 수 있지만, **외부**에는 노출하지 않습니다.

이 분리 덕분에 DB 구조가 바뀌어도 외부 API 모양은 그대로 유지할 수 있고, 반대로 외부 응답 형태가 변해도 DB는 멀쩡할 수 있습니다.

### 6.8.2 `app/schemas.py` 작성

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """POST /todos 의 요청 본문."""

    title: str = Field(min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 의 요청 본문 — 부분 수정."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_done: bool | None = None


class TodoRead(BaseModel):
    """GET 응답에 사용하는 스키마."""

    id: int
    title: str
    is_done: bool
    created_at: datetime

    # ORM 객체(Todo 인스턴스)에서 직접 값을 읽어들일 수 있게 한다.
    model_config = ConfigDict(from_attributes=True)
```

세 가지 스키마의 역할:

- **`TodoCreate`**: 새 todo를 만들 때의 요청. `title`만 받습니다. `id`나 `created_at`은 서버가 정합니다.
- **`TodoUpdate`**: 부분 수정. 모든 필드가 선택적입니다(둘 다 None이면 아무것도 안 바꾸는 결과).
- **`TodoRead`**: 응답. PK·생성 시각까지 포함합니다.

가장 중요한 한 줄은 **`model_config = ConfigDict(from_attributes=True)`** 입니다.

> **`from_attributes=True`란?** Pydantic이 "이 스키마는 dict뿐 아니라 일반 객체의 속성에서도 값을 읽어 만들 수 있다"는 표시입니다. 우리가 ORM에서 받아온 `Todo` 인스턴스를 그대로 `TodoRead.model_validate(todo)`로 변환하거나, FastAPI의 `response_model=TodoRead`에 그대로 넘길 수 있게 됩니다.

> **옛날 이름은 `orm_mode = True`**: Pydantic v1까지는 같은 옵션이 `class Config: orm_mode = True`였습니다. v2에서 `from_attributes=True`로 이름이 바뀌었습니다. 인터넷의 옛 코드와 비교할 때 헷갈리지 마세요.

### 6.8.3 ORM 객체 → Pydantic 스키마로 변환

라우트가 ORM의 `Todo` 인스턴스를 받아 `TodoRead`로 응답하는 흐름은 두 가지입니다.

**방법 A — `response_model`을 라우트에 지정 (권장)**

```python
@app.get("/todos/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)) -> Todo:
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(404, "Not Found")
    return todo   # FastAPI 가 알아서 TodoRead 로 변환
```

`response_model=TodoRead`만 적어두면, FastAPI는 함수가 어떤 타입을 반환하든 그것을 `TodoRead`로 자동 변환·검증해서 응답합니다. **이 방식이 가장 깔끔하고, 자동 문서에도 잘 반영됩니다.**

**방법 B — 함수 안에서 명시적으로 변환**

```python
@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)) -> TodoRead:
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(404, "Not Found")
    return TodoRead.model_validate(todo)   # 명시적
```

둘 다 동작하지만, 본 가이드는 **방법 A를 표준**으로 합니다.

---

## 6.9 CRUD 구현 — 라우트로 직접

이제 모든 조각이 갖춰졌으니 실제 CRUD 라우트를 만듭니다. **이 챕터까지는 라우터 분리 없이** `app/main.py`에 모든 라우트를 모읍니다(07장에서 라우터 분리 패턴을 다룸).

### 6.9.1 `app/main.py` — 전체 코드

```python
# app/main.py
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

app = FastAPI(title="SQLAlchemy Todo")


@app.get("/health")
async def health() -> dict[str, str]:
    """앱이 살아 있는지 확인하는 헬스체크."""
    return {"status": "ok"}


@app.post(
    "/todos",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """새 할 일 한 건을 만든다."""
    todo = Todo(title=payload.title)
    session.add(todo)
    # commit 은 get_session 의존성이 라우트 종료 후 알아서 한다.
    # flush 만 해 두면 id, created_at 같은 자동 생성 값이 todo 객체에 채워진다.
    await session.flush()
    await session.refresh(todo)
    return todo


@app.get("/todos", response_model=list[TodoRead])
async def list_todos(
    session: AsyncSession = Depends(get_session),
) -> list[Todo]:
    """전체 할 일 목록을 최신순으로 돌려준다."""
    stmt = select(Todo).order_by(Todo.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@app.get("/todos/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """id 로 할 일 한 건 조회. 없으면 404."""
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """할 일을 부분 수정한다.

    payload 에 들어 있는 필드만 갱신하고, 나머지는 그대로 둔다.
    """
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    # exclude_unset=True : 클라이언트가 명시적으로 보낸 필드만 가져온다.
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(todo, key, value)

    await session.flush()
    await session.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """할 일을 영구 삭제한다."""
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    await session.delete(todo)
    # 커밋은 get_session 이 알아서 한다
    return None
```

여섯 개의 라우트를 표로 다시 정리합니다.

| HTTP | 경로 | 함수 | 역할 |
|------|------|------|------|
| GET | `/health` | `health` | 헬스 체크 |
| POST | `/todos` | `create_todo` | 새 todo 만들기 |
| GET | `/todos` | `list_todos` | 전체 목록 |
| GET | `/todos/{id}` | `get_todo` | 한 건 조회 |
| PATCH | `/todos/{id}` | `update_todo` | 부분 수정 |
| DELETE | `/todos/{id}` | `delete_todo` | 삭제 |

### 6.9.2 라우트 한 줄 한 줄 풀어보기 — INSERT

POST `/todos`의 흐름을 자세히 봅니다.

```python
todo = Todo(title=payload.title)   # 1) 파이썬 객체 생성. 아직 DB에 안 들어감
session.add(todo)                  # 2) "이 객체를 INSERT 대기열에 넣어"
await session.flush()              # 3) 대기 중인 작업을 DB로 보냄(트랜잭션은 아직 안 닫힘)
await session.refresh(todo)        # 4) DB가 정한 id, created_at 값을 todo에 다시 가져옴
return todo                        # 5) 함수 종료
                                   # 6) get_session 의존성이 commit
```

> **`add`와 `commit`의 차이**: `add`는 메모리상 세션의 "대기열"에만 추가하는 것이고, 실제로 DB에 INSERT가 나가는 것은 `flush`(또는 `commit`이 자동으로 부르는 flush)입니다. `commit`은 "지금까지 한 작업을 트랜잭션째 디스크에 영구 반영하라"는 더 강한 동작입니다.

> **`flush`와 `refresh`가 왜 둘 다 필요?** `flush`만 하면 INSERT는 나가지만, DB가 자동 생성한 값(예: 자동 증가 id, default로 들어간 created_at)이 우리 손에 든 `todo` 인스턴스에는 반영되지 않을 수도 있습니다. `refresh`는 "DB에 가서 이 행의 값들을 다시 읽어와 인스턴스를 갱신하라"는 의미입니다. 이 한 줄을 빼면 응답 JSON의 `id`가 `null`로 나가는 상황이 생길 수 있습니다.

### 6.9.3 SELECT — `select()`와 `session.execute()`

목록 조회를 봅니다.

```python
stmt = select(Todo).order_by(Todo.created_at.desc())
result = await session.execute(stmt)
return list(result.scalars().all())
```

- **`select(Todo)`**: SQL의 `SELECT * FROM todos`에 해당하는 SQLAlchemy 표현입니다. SQLAlchemy 2.0의 표준 표기법.
- **`.order_by(Todo.created_at.desc())`**: 정렬. `desc()`는 내림차순.
- **`await session.execute(stmt)`**: 만든 SELECT 문을 실제로 실행합니다. 비동기이므로 `await`.
- **`result.scalars()`**: `execute`의 반환값은 행 단위의 결과인데, 우리는 단일 모델(Todo) 객체로 받고 싶으므로 `scalars()`로 변환합니다.
- **`.all()`**: 전부를 리스트로. (한 건만 원하면 `.first()`, `.one()`, `.one_or_none()`)

> **`scalars()`는 왜 필요한가?** `session.execute(select(Todo))`의 반환은 "각 행이 한 칸짜리 튜플인 결과 집합"입니다(`(<Todo>,)`, `(<Todo>,)`, ...). 우리는 그 첫 칸만 원하므로 `scalars()`로 풀어 평평한 모양(`<Todo>`, `<Todo>`, ...)으로 만듭니다.

### 6.9.4 단건 조회 — `session.get()` 단축

`session.get(Todo, todo_id)` 한 줄로 PK 조회를 끝낼 수 있습니다. 같은 일을 풀어 쓰면 다음과 같습니다.

```python
# 같은 일, 풀어 쓴 버전
stmt = select(Todo).where(Todo.id == todo_id)
result = await session.execute(stmt)
todo = result.scalars().one_or_none()
```

`session.get(Model, pk)`는 캐시까지 활용하므로 **PK 조회는 항상 `get`을 우선 고려**하세요.

### 6.9.5 UPDATE — 객체 속성 변경 + 자동 INSERT

UPDATE 라우트의 핵심은 다음 패턴입니다.

```python
todo = await session.get(Todo, todo_id)
data = payload.model_dump(exclude_unset=True)
for key, value in data.items():
    setattr(todo, key, value)
await session.flush()
```

- 가져온 ORM 객체의 속성을 그냥 파이썬 코드로 바꾸기만 하면 됩니다.
- `flush`(또는 `commit`) 시점에 SQLAlchemy가 "이 객체가 어떤 속성이 바뀌었는지" 추적해 둔 정보를 바탕으로 UPDATE 문을 만들어 보냅니다.
- **변경한 속성이 하나도 없으면 UPDATE 자체가 안 나갑니다.**

> **`exclude_unset=True`의 의미**: 클라이언트가 PATCH 요청에서 명시적으로 보낸 필드만 dict에 담습니다. `title`만 보낸 요청이면 `is_done`은 dict에 안 들어옵니다. 만약 `True`로 안 두면 보내지 않은 필드가 모두 `None`으로 들어와 멀쩡한 데이터를 NULL로 덮어쓸 수 있습니다.

### 6.9.6 DELETE — `await session.delete(obj)`

```python
todo = await session.get(Todo, todo_id)
await session.delete(todo)
```

`session.delete(obj)`는 "다음 flush 때 이 행을 DELETE해 달라"는 표시입니다. 실제 DELETE는 flush/commit 시 나갑니다.

이 챕터는 **하드 삭제(hard delete)**만 다룹니다. 즉, 행 자체를 지웁니다. 일부 서비스는 `is_deleted` 플래그만 켜는 **소프트 삭제(soft delete)**를 쓰는데, 11장에서 다룹니다.

### 6.9.7 응답 코드 정리

본 라우트들이 돌려주는 HTTP 상태 코드는 다음과 같습니다.

| 라우트 | 정상 상태 코드 | 비정상 |
|--------|----------------|--------|
| POST `/todos` | **201 Created** | 422 (검증 실패) |
| GET `/todos` | 200 | (드뭄) |
| GET `/todos/{id}` | 200 | 404 |
| PATCH `/todos/{id}` | 200 | 404, 422 |
| DELETE `/todos/{id}` | **204 No Content** | 404 |

> **204 No Content란?** "잘 처리됐고 응답 본문은 없다"는 의미. DELETE의 표준 성공 코드입니다. 본 코드에서 `status_code=status.HTTP_204_NO_CONTENT`로 지정하고 함수가 `None`을 반환하게 했습니다.

---

## 6.10 트랜잭션과 세션 라이프사이클

이 챕터에서 트랜잭션은 6.6의 `get_session` 의존성이 거의 모든 일을 알아서 합니다. 하지만 안에서 무슨 일이 벌어지는지 짧게 점검하고 갑니다.

### 6.10.1 한 요청 = 한 트랜잭션

```
요청 시작
  └─ AsyncSession 생성
       └─ 트랜잭션 시작 (자동)
             ├─ session.add / select / delete ...
             ├─ ...
             ├─ ...
             └─ (라우트 종료)
       ├─ 정상: commit
       └─ 예외: rollback
  └─ AsyncSession close
요청 끝
```

이 한 단위가 우리의 표준입니다. **두 라우트 호출이 같은 트랜잭션을 공유하지 않습니다.** 한 요청 안에서 일어난 일들만 하나의 트랜잭션으로 묶입니다.

### 6.10.2 commit을 직접 부르고 싶을 때

대부분의 경우 의존성이 commit을 처리하므로 라우트 안에서 `await session.commit()`을 직접 부를 일이 없습니다. 다만 한 라우트 안에서 **여러 번 commit을 나누고 싶을 때**(예: 큰 배치 작업)는 직접 호출할 수 있습니다.

```python
for chunk in chunks_of_data:
    for item in chunk:
        session.add(Item(...))
    await session.commit()   # 청크 단위로 끊어서 커밋
```

이런 시나리오는 일반 CRUD에서는 잘 안 나옵니다. 본 챕터에서는 **무시하고, commit은 의존성에 맡깁니다.**

### 6.10.3 예외와 자동 rollback

라우트 안에서 `HTTPException`이나 다른 예외가 발생하면, 6.6의 `get_session`은 `except Exception:` 블록에서 `await session.rollback()`을 부른 뒤 예외를 다시 던집니다. 그래서 **DB가 어중간한 상태로 남는 일이 없습니다.**

### 6.10.4 세션의 수명: "요청 1개 = 세션 1개"

이 약속을 어기면 흔한 버그가 생깁니다. 이 챕터의 코드 예시는 모두 그 약속을 지키게 짜여 있고, 7장 이후 라우터 분리 패턴에서도 같은 약속이 유지됩니다.

> **세션을 라우트 함수 밖에 전역 변수로 두지 마세요.** 동시 요청들이 같은 세션을 건드리면 트랜잭션이 엉키고 알 수 없는 에러가 납니다. 항상 의존성으로 받아 함수 안에서만 씁니다.

---

## 6.11 마이그레이션이란 — 그리고 왜 필요한가

### 6.11.1 코드와 DB는 동시에 진화한다

새 기능을 추가하면 보통 이런 일이 함께 일어납니다.

1. ORM 모델에 새 필드를 추가했다 (`models.py`).
2. **DB 테이블에도 그 새 열이 생겨야 한다.**
3. 코드는 이미 그 새 열을 읽고 쓰는데, DB에 열이 없으면 런타임 에러.

이 "DB 구조 변경"을 **마이그레이션**이라고 부릅니다. 그냥 즉석에서 SQL로 ALTER TABLE을 날려도 동작은 합니다. 하지만 다음 문제가 생깁니다.

- **팀원이 한 일을 알 수 없다.** "어제 어떤 ALTER를 날렸지?" 기억이 안 나면 끝납니다.
- **다른 환경에 다시 적용할 수 없다.** 운영, 스테이징, 다른 개발자의 로컬 DB에 같은 변경이 똑같이 들어가야 하는데, 즉석 SQL은 재현이 어렵습니다.
- **롤백이 어렵다.** 잘못 날린 ALTER를 되돌리려면 그 반대 SQL을 직접 짜야 합니다.

마이그레이션 도구(=Alembic)는 이 문제를 다음으로 해결합니다.

- **각 변경을 파일 한 개로 기록**(`versions/abc123_add_email.py`).
- **순서대로 적용/되돌림 가능** (`upgrade head`, `downgrade -1`).
- **모델 변경을 자동으로 비교해 변경 파일 초안을 생성**(`autogenerate`).

> **마이그레이션(migration)이란?** DB의 스키마(표 구조) 변경을 코드 파일로 기록·실행하는 작업입니다. 변경 이력이 git에 함께 들어가, 어느 시점·어느 환경의 DB든 같은 순서로 같은 구조에 도달할 수 있습니다.

### 6.11.2 Alembic — SQLAlchemy의 짝 도구

> **Alembic이란?** SQLAlchemy의 작성자가 같이 만든 마이그레이션 도구입니다. SQLAlchemy 모델을 읽어 DB와 비교한 뒤 차이를 파일로 만들어 줍니다(`autogenerate`). 그리고 그 파일을 적용·되돌릴 수 있는 CLI를 제공합니다.

Alembic의 핵심 명령은 세 개뿐입니다.

| 명령 | 용도 |
|------|------|
| `alembic init alembic` | 처음 한 번 — Alembic 폴더 골격 생성 |
| `alembic revision --autogenerate -m "..."` | 새 마이그레이션 파일 만들기 |
| `alembic upgrade head` | 미적용 마이그레이션을 모두 적용 |

> **head 란?** "최신 마이그레이션"을 가리키는 별칭입니다. 마이그레이션 파일들이 사슬처럼 이어진 그래프의 끝입니다. `upgrade head`는 "끝까지 다 적용해라"는 뜻.

추가로 자주 쓰는 명령:

| 명령 | 용도 |
|------|------|
| `alembic downgrade -1` | 가장 최근 한 단계만 되돌림 |
| `alembic downgrade base` | 모든 마이그레이션을 되돌림(빈 상태로) |
| `alembic history` | 마이그레이션 그래프를 보여줌 |
| `alembic current` | 지금 DB가 어느 마이그레이션까지 적용됐는지 |

---

## 6.12 Alembic 설치와 초기화

### 6.12.1 Alembic 설치 (이미 완료)

6.6.1에서 `uv add ... alembic`으로 함께 깔았습니다. 다음 한 줄로 확인.

```bash
uv run alembic --version
```

`alembic 1.x.x` 같은 출력이 나오면 OK.

### 6.12.2 폴더 골격 생성

프로젝트 루트(`pyproject.toml`이 있는 폴더)에서 한 번만 실행합니다.

```bash
uv run alembic init alembic
```

> **`alembic init alembic`의 두 번째 `alembic`은?** "마이그레이션 폴더의 이름"입니다. 관례적으로 `alembic`이라는 이름을 쓰지만, `migrations`, `db/migrations` 등으로 바꿔도 됩니다. 이 가이드는 표준대로 `alembic`을 씁니다.

실행 후 폴더 구조가 다음처럼 됩니다.

```
06-SQLAlchemyTodo/
├── alembic.ini              ← 새로 생김 (Alembic 전체 설정)
├── alembic/
│   ├── env.py               ← 새로 생김 (실행 시 호출되는 스크립트)
│   ├── script.py.mako       ← 새로 생김 (revision 파일 템플릿)
│   ├── README
│   └── versions/            ← 새로 생김 (마이그레이션 파일이 들어갈 폴더)
└── ...
```

각 파일의 역할:

- **`alembic.ini`** — Alembic의 메인 설정 파일. DB URL, 로깅, 스크립트 경로 등.
- **`alembic/env.py`** — 마이그레이션 명령이 실행될 때 호출되는 부트스트랩 코드. **여기를 우리 프로젝트에 맞게 수정해야 합니다.**
- **`alembic/script.py.mako`** — `alembic revision`으로 새 파일을 만들 때 쓰는 템플릿.
- **`alembic/versions/`** — 실제 마이그레이션 파일들이 들어갈 폴더. 처음에는 비어 있습니다.

### 6.12.3 `alembic.ini` 살짝 수정

`alembic.ini`를 열고 `sqlalchemy.url` 줄을 찾으면 다음처럼 들어 있을 겁니다.

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

이 줄을 **비워 두거나 그대로 둡니다.** 우리는 `env.py`에서 `DATABASE_URL`을 읽어서 덮어쓸 것이므로 여기 값은 무시됩니다.

```ini
sqlalchemy.url =
```

> **왜 ini 파일에 박아두지 않나요?** 환경별로 DB가 다를 수 있고(개발 SQLite, 운영 Postgres), `.env` 파일을 통해 주입하는 흐름이 더 안전합니다. ini 파일에 비밀번호를 박으면 git에 노출됩니다.

### 6.12.4 `alembic/env.py`를 비동기용으로 수정

이 부분이 본 챕터에서 가장 까다로운 한 단계입니다. Alembic은 기본적으로 동기 SQL 실행을 가정하고 만들어졌습니다. 우리 프로젝트는 **비동기 엔진(`AsyncEngine`)**을 쓰므로 약간의 수정이 필요합니다.

`alembic/env.py`를 통째로 다음 내용으로 교체합니다.

```python
# alembic/env.py
"""Alembic 환경 — 비동기 엔진(AsyncEngine)으로 마이그레이션을 실행한다."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ─────────────────────────────────────────────────────────
# 우리 앱의 모델과 DATABASE_URL 을 가져오기 위한 import
# (alembic 폴더가 프로젝트 루트의 자식이므로, 같은 sys.path 에 있다고 가정)
# ─────────────────────────────────────────────────────────
from app.config import DATABASE_URL
from app.db import Base
from app import models  # noqa: F401  - Base.metadata 에 모델이 등록되도록 import

# Alembic Config 객체
config = context.config

# alembic.ini 의 sqlalchemy.url 을 우리의 DATABASE_URL 로 덮어쓴다
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 가 비교할 메타데이터 (= 우리의 Base.metadata)
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
    """실제 마이그레이션 실행 본체. 동기 connection 위에서 돈다."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,            # 열의 타입 변경도 감지
        render_as_batch=True,         # SQLite 의 ALTER TABLE 제약을 우회
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진을 만들고 동기 컨텍스트로 변환해 마이그레이션을 실행."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드 — 실제 DB 에 연결해 마이그레이션 실행."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

핵심 포인트만 짚습니다.

- **`from app.config import DATABASE_URL`, `from app.db import Base`**: 우리가 만든 설정과 베이스 클래스를 그대로 가져옵니다.
- **`from app import models`**: 모델을 import해야 `Base.metadata`에 등록됩니다. **이 한 줄을 빼면 autogenerate가 빈 마이그레이션을 만듭니다.**
- **`config.set_main_option("sqlalchemy.url", DATABASE_URL)`**: ini 파일의 URL을 우리의 환경 변수로 덮어씁니다.
- **`async_engine_from_config(...)`**: 비동기 엔진을 만듭니다. `poolclass=pool.NullPool`은 마이그레이션은 일회성이라 풀이 필요 없어서 끄는 옵션.
- **`await connection.run_sync(do_run_migrations)`**: Alembic 본체는 동기 함수만 받으므로, 비동기 connection 안에서 동기 함수를 실행시키는 다리 역할입니다.
- **`compare_type=True`**: autogenerate가 열의 타입 변경(예: VARCHAR(100)→VARCHAR(200))도 감지하게 합니다.
- **`render_as_batch=True`**: SQLite 가 일부 `ALTER TABLE` 형식만 지원하므로 batch 모드를 켜둡니다. 이 옵션이 있어야 컬럼 변경 같은 마이그레이션이 SQLite 에서도 호환되게 처리됩니다(다른 DB 에는 영향 없음).

> **이 한 파일이 이 챕터에서 가장 손이 많이 가는 부분입니다.** 하지만 한 번 만들어 두면 이후 챕터에서 그대로 재사용합니다. 사실상 "FastAPI + SQLAlchemy async + Alembic" 표준 템플릿입니다.

---

## 6.13 첫 마이그레이션 — `autogenerate`와 `upgrade head`

### 6.13.1 새 마이그레이션 파일 만들기

이제 `app/models.py`의 `Todo` 모델을 보고 마이그레이션 파일을 자동 생성합니다.

```bash
uv run alembic revision --autogenerate -m "create todos table"
```

성공하면 다음 비슷한 출력이 나옵니다.

```
INFO  [alembic.autogenerate.compare] Detected added table 'todos'
  Generating .../alembic/versions/xxxxxxxxxxxx_create_todos_table.py ...  done
```

`alembic/versions/` 안에 파일이 한 개 생겼습니다. 열어보면 다음과 같은 내용입니다(파일명의 해시는 매번 다름).

```python
"""create todos table

Revision ID: 1234567890ab
Revises:
Create Date: 2026-04-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1234567890ab"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("todos")
```

각 부분:

- **`upgrade()`**: 적용할 변경. "todos 테이블을 만들어라."
- **`downgrade()`**: 되돌릴 때 할 변경. "todos 테이블을 지워라."
- **`revision`, `down_revision`**: 마이그레이션 사슬의 ID. `down_revision = None`이면 첫 번째라는 뜻.

> **autogenerate가 자동으로 만들어 준 파일은 항상 한 번 읽어보세요.** 100% 정확하지 않습니다. 인덱스, 제약조건 이름, 데이터 마이그레이션(예: 기존 행을 변환) 같은 부분은 손으로 보강해야 할 때가 있습니다. 하지만 본 챕터처럼 단순한 표 한 개 추가는 거의 항상 그대로 동작합니다.

### 6.13.2 마이그레이션 적용

```bash
uv run alembic upgrade head
```

성공 출력:

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 1234567890ab, create todos table
```

이제 프로젝트 루트에 **`todo.db`라는 SQLite 파일**이 새로 생겼습니다. 그 안에 `todos` 테이블과 Alembic이 자기가 쓰는 `alembic_version` 테이블이 들어 있습니다.

### 6.13.3 적용 확인 — `sqlite3`로 들여다보기

`sqlite3` CLI가 깔려 있으면 다음으로 들어가 봅니다.

```bash
sqlite3 todo.db
```

```
sqlite> .tables
alembic_version  todos

sqlite> .schema todos
CREATE TABLE todos (
        id INTEGER NOT NULL,
        title VARCHAR(200) NOT NULL,
        is_done BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        PRIMARY KEY (id)
);

sqlite> select * from alembic_version;
1234567890ab

sqlite> .quit
```

`alembic_version` 테이블이 우리 DB가 어느 마이그레이션까지 적용됐는지 기억합니다. **이 테이블을 함부로 지우거나 손대지 마세요.**

### 6.13.4 두 번째 마이그레이션을 만드는 흐름 (예시)

만약 나중에 `Todo` 모델에 `priority: Mapped[int] = mapped_column(default=0)`라는 새 열을 추가했다면, 같은 명령을 다시 부르기만 하면 됩니다.

```bash
# 1) models.py 에 priority 추가
# 2) 새 마이그레이션 파일 자동 생성
uv run alembic revision --autogenerate -m "add priority to todos"

# 3) 적용
uv run alembic upgrade head
```

Alembic은 두 번째 파일에서 `down_revision = "1234567890ab"`(첫 번째의 ID)를 자동으로 채워 사슬을 잇습니다.

### 6.13.5 되돌리기

```bash
uv run alembic downgrade -1     # 가장 최근 한 단계 되돌림
uv run alembic downgrade base   # 모든 마이그레이션 되돌림
uv run alembic upgrade head     # 다시 끝까지
```

개발 중에 마이그레이션을 잘못 만들었으면 `downgrade -1`로 되돌리고, 파일을 수정한 뒤 `upgrade head`로 다시 적용합니다.

> **운영 환경에서 downgrade는 신중하게**: 한 번 운영에 적용된 마이그레이션은 데이터 손실이 따를 수 있으므로 함부로 되돌리지 않습니다. 본 가이드는 개발 중 흐름만 다룹니다.

---

## 6.14 실행하기 — 서버를 띄우고 curl로 검증

### 6.14.1 서버 띄우기

```bash
uv run uvicorn app.main:app --reload
```

다음 비슷한 로그가 나오면 성공.

```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)를 열면 Swagger UI가 자동 생성된 모습이 보입니다.

### 6.14.2 curl로 CRUD 한 바퀴 돌리기

다른 터미널에서 다음을 차례대로 실행해 봅니다.

```bash
# 1) 헬스 체크
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}

# 2) 새 todo 만들기
curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"우유 사기"}'
# {"id":1,"title":"우유 사기","is_done":false,"created_at":"2026-04-25T..."}

curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"빨래 돌리기"}'

# 3) 목록 조회
curl -s http://127.0.0.1:8000/todos
# [{"id":2,...},{"id":1,...}]

# 4) 한 건 조회
curl -s http://127.0.0.1:8000/todos/1
# {"id":1,"title":"우유 사기","is_done":false,...}

# 5) 부분 수정 (완료 표시)
curl -s -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done":true}'
# {"id":1,"title":"우유 사기","is_done":true,...}

# 6) 삭제
curl -s -X DELETE http://127.0.0.1:8000/todos/2 -w "%{http_code}\n"
# (응답 본문 없음) 204

# 7) 없는 todo 조회 → 404
curl -s -i http://127.0.0.1:8000/todos/9999
# HTTP/1.1 404 Not Found
# ...
```

이 한 라운드가 모두 통과하면 **6장의 핵심 내용이 모두 동작하는 것입니다.** 축하합니다.

### 6.14.3 검증 실패는 어떻게 보이나

빈 title을 보내보면 422가 떨어집니다.

```bash
curl -s -i -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":""}'

# HTTP/1.1 422 Unprocessable Entity
# Content-Type: application/json
# ...
# {"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character",...}]}
```

`TodoCreate.title`에 `min_length=1`을 줬기 때문입니다. **이 검증은 ORM이 아니라 Pydantic이 한 일**이며, DB에 도달하기 전에 막혔습니다.

---

## 6.15 SQLite에서 PostgreSQL로 옮기기 — `DATABASE_URL`만 바꾸면 됨

ORM의 가장 큰 실용적 가치 중 하나가 이것입니다. 우리가 짠 모델·라우트 코드 한 줄도 바꾸지 않고 DB 종류만 바꿀 수 있습니다.

### 6.15.1 PostgreSQL 준비 (Docker로)

가장 간단한 방법은 Docker로 띄우는 것입니다.

```bash
docker run --name fastapi-pg \
  -e POSTGRES_DB=tododb \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass \
  -p 5432:5432 \
  -d postgres:17
```

PostgreSQL이 5432 포트에서 떴습니다.

> **Docker가 없거나 설치가 부담스러우면** 이 절은 읽기만 하고 넘어가도 됩니다. 09장 배포에서 Docker를 본격적으로 다루며, 그때 다시 시도해 볼 수 있습니다.

### 6.15.2 비동기 PostgreSQL 드라이버 설치

```bash
uv add asyncpg
```

> **`asyncpg`란?** PostgreSQL용 비동기 파이썬 드라이버. SQLAlchemy 2.0이 PostgreSQL과 비동기로 대화할 때 가장 빠르고 표준입니다.

### 6.15.3 `DATABASE_URL` 한 줄 바꾸기

`.env` 파일을 만들고:

```
DATABASE_URL=postgresql+asyncpg://todouser:todopass@localhost:5432/tododb
```

그리고 셸에 적용해 주거나, 터미널에서 직접 export.

```bash
export DATABASE_URL="postgresql+asyncpg://todouser:todopass@localhost:5432/tododb"
```

> **`.env` 파일은 자동으로 읽히나요?** Pydantic Settings(추후 챕터)나 `python-dotenv` 같은 라이브러리가 있어야 자동으로 읽힙니다. 본 챕터는 단순화를 위해 `os.environ.get`만 씁니다. 다음 명령들은 셸에서 export한 환경 변수를 읽습니다.

### 6.15.4 마이그레이션 적용 + 서버 재시작

```bash
uv run alembic upgrade head     # PG에 todos 테이블이 새로 만들어진다
uv run uvicorn app.main:app --reload
```

이제 같은 코드가 SQLite가 아닌 PostgreSQL을 쓰고 있습니다. 6.14의 curl을 그대로 다시 실행해도 모두 동작합니다.

> **모델 코드는 한 줄도 안 바뀌었습니다.** 이게 ORM의 본질적인 가치입니다. SQLite로 빠르게 개발해서 검증하고, 운영 시 PostgreSQL로 옮기는 흐름이 흔합니다.

### 6.15.5 MySQL로 가려면

같은 식입니다.

```bash
uv add asyncmy
export DATABASE_URL="mysql+asyncmy://user:pass@localhost:3306/tododb"
uv run alembic upgrade head
```

> **드라이버 차이로 동작이 달라지는 경우**: 99% 똑같이 동작합니다. 다만 PostgreSQL의 JSONB·배열, MySQL의 utf8mb4 콜레이션, SQLite의 빈약한 ALTER TABLE 같은 DB별 특성을 쓰는 모델은 옮겼을 때 작은 차이가 날 수 있습니다. 본 챕터의 Todo 같은 단순한 모델은 차이가 없습니다.

---

## 6.16 N+1 문제와 `selectinload` 맛보기

### 6.16.1 무엇이 문제인가

이 챕터는 모델이 하나(Todo)뿐이라 N+1 문제가 등장하지 않습니다. 하지만 11장에서 `User`와 `Post`처럼 관계가 있는 모델을 다루면 곧 만나게 됩니다. 미리 한 번 보고 갑니다.

상상해 봅시다. 사용자가 100명, 각 사용자가 글을 5개씩 가지고 있고, "모든 사용자와 그들의 글을 함께 보여라"는 라우트가 있습니다.

**잘못된 구현 (N+1 쿼리):**

```python
# ⚠️ 안티패턴
users = (await session.execute(select(User))).scalars().all()  # 1번 쿼리
for user in users:
    posts = (await session.execute(
        select(Post).where(Post.user_id == user.id)
    )).scalars().all()                                          # 사용자마다 1번 = 100번 쿼리
    # 총 1 + 100 = 101 번 쿼리!
```

이게 **N+1 문제**입니다. 사용자 수(N)가 늘어날수록 쿼리가 선형으로 늘어 성능이 무너집니다.

> **N+1 문제란?** "목록을 가져오는 1번 쿼리"와 "그 목록의 각 항목마다 추가 1번씩 N번 쿼리"가 합쳐져 총 N+1번 쿼리가 나가는 비효율 패턴입니다. ORM 사용자가 가장 자주 만드는 성능 문제이며, eager loading으로 해결합니다.

### 6.16.2 `selectinload`로 해결

같은 일을 한 번의 SELECT(또는 두 번이지만 N에 무관하게 일정한 횟수)로 끝낼 수 있습니다.

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.posts))
users = (await session.execute(stmt)).scalars().all()

for user in users:
    # user.posts 는 이미 로드되어 있음 — 추가 쿼리 없음
    print(user.email, len(user.posts))
```

`selectinload(User.posts)`는 SQLAlchemy에게 "User를 가져올 때, 관련 Post들도 한 번에 같이 가져와라"고 지시합니다. 내부적으로 두 번의 SELECT(`SELECT * FROM users`, `SELECT * FROM posts WHERE user_id IN (...)`)로 끝납니다. 사용자가 100명이든 10000명이든 두 번뿐입니다.

이외에도 `joinedload`(JOIN 한 번으로 처리), `subqueryload` 등 여러 옵션이 있지만, **본 가이드의 권장 1순위는 `selectinload`** 입니다. 거의 모든 1:N에서 무난히 동작하고 직관적입니다.

> **본 챕터에서는 깊이 안 들어갑니다.** 자세한 내용과 실전 사용은 11장 Blog API에서 1:N·N:M 관계를 만들 때 본격적으로 다룹니다. 지금은 "이런 함정과 도구가 있다"는 것만 기억해 두면 됩니다.

---

## 6.17 다른 DB로 옮길 때 — 정리

이 챕터에서 익힌 내용 중 **DB 전환에 관한 핵심**만 표로 모읍니다.

### 6.17.1 DATABASE_URL 형식

| DB | 형식 | 비고 |
|----|------|------|
| SQLite (파일) | `sqlite+aiosqlite:///./todo.db` | 슬래시 3개. 상대 경로 |
| SQLite (절대 경로) | `sqlite+aiosqlite:////absolute/path/db.sqlite` | 슬래시 4개에 주의 |
| SQLite (메모리) | `sqlite+aiosqlite:///:memory:` | 테스트용 |
| PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/dbname` | 표준 포트 5432 |
| PostgreSQL (TLS) | `postgresql+asyncpg://user:pass@host:5432/db?ssl=true` | 운영 권장 |
| MySQL | `mysql+asyncmy://user:pass@host:3306/dbname` | 표준 포트 3306 |
| MariaDB | `mysql+asyncmy://user:pass@host:3306/dbname` | MySQL과 동일 드라이버 |

### 6.17.2 옮기는 절차 한 장 요약

1. 새 비동기 드라이버 설치 (`uv add asyncpg` 등)
2. `DATABASE_URL` 환경 변수를 새 형식으로 변경
3. `uv run alembic upgrade head`로 새 DB에 스키마 생성
4. 서버 재시작 (`uv run uvicorn app.main:app --reload`)
5. 끝

코드 변경: **0줄**. (단, DB별 특수 타입을 쓴 경우는 별도 검토 필요)

---

## 6.18 흔한 함정과 해결법

이 챕터에서 입문자가 가장 자주 만나는 문제들을 모았습니다.

### 6.18.1 commit 잊기

```python
# ⚠️ 안티패턴
@app.post("/todos")
async def create_todo(payload, session=Depends(get_session)):
    todo = Todo(title=payload.title)
    session.add(todo)
    return todo   # commit 을 안 했는데 어쩌지?
```

**우리 가이드의 패턴에서는 문제가 안 됩니다.** `get_session` 의존성이 라우트 종료 후 자동으로 commit하기 때문입니다. 다만 6.6의 `get_session`을 안 쓰고 의존성 함수에서 `yield session` 뒤에 commit을 안 적은 경우라면, 정말로 commit이 안 나가서 데이터가 사라집니다.

> **체크포인트**: 본 가이드의 `get_session`을 그대로 복사해 쓰면 안전합니다. 직접 변형하지 마세요.

### 6.18.2 async/sync 혼용

```python
# ⚠️ 안티패턴
@app.get("/todos")
async def list_todos(session=Depends(get_session)):
    rows = session.execute(select(Todo))   # await 빠뜨림!
    return rows
```

`session.execute`는 코루틴을 반환합니다. `await` 없이 그냥 변수에 담으면 실제 SQL은 실행되지 않고, 그 코루틴 객체가 반환됩니다. **에러 메시지가 어색해서 디버깅이 어렵습니다.** 항상 `await`를 잊지 마세요.

> **반대로 sync 함수에서 비동기 메서드를 부르면**: `await`를 못 써서 다음과 같은 경고가 뜹니다 — `RuntimeWarning: coroutine ... was never awaited`. 함수에 `async def`를 안 쓴 게 원인입니다.

### 6.18.3 세션을 함수 밖에서 쓰기

```python
# ⚠️ 안티패턴
session = SessionLocal()    # 모듈 전역에 한 번만!
@app.get("/todos")
async def list_todos():
    return await session.execute(select(Todo))   # 모든 요청이 같은 session 공유
```

이렇게 하면 **모든 요청이 같은 세션을 쓰기 시작**합니다. 트랜잭션이 엉키고, 한 요청의 rollback이 다른 요청에 영향을 주고, 알 수 없는 에러가 뜹니다.

> **항상 의존성으로 받아 함수 안에서만 쓰세요.** `Depends(get_session)`이 한 요청 한 세션을 보장합니다.

### 6.18.4 `id`가 `None`인 채로 응답

```python
todo = Todo(title="x")
session.add(todo)
return todo   # ⚠️ id 가 아직 채워지지 않았을 수 있음
```

`add`만 한 시점에는 `todo.id`가 `None`입니다(아직 INSERT 전이므로). 응답으로 나가기 전에 `await session.flush()` 또는 `await session.commit()`이 한 번 일어나야 자동 생성된 PK가 객체에 채워집니다. 6.9의 `create_todo`처럼 명시적으로 `await session.flush()`와 `await session.refresh(todo)`를 부르는 것이 가장 안전합니다.

### 6.18.5 `expire_on_commit=True`로 commit 후 속성 접근 시 에러

기본값(`True`)이면 commit 직후 객체의 모든 속성이 "만료" 상태가 되어, 다시 접근하려면 `refresh`가 필요합니다. FastAPI 라우트에서 응답 직전에 commit이 일어나는 흐름과는 잘 맞지 않습니다. **6.6의 `expire_on_commit=False` 설정을 그대로 쓰세요.**

### 6.18.6 마이그레이션이 빈 파일로 만들어짐

`alembic revision --autogenerate`를 돌렸는데 `upgrade()`/`downgrade()`가 비어 있는 경우, `env.py`에서 모델을 import하지 않아서 `Base.metadata`가 비어 있는 상태입니다. 6.12.4의 `from app import models  # noqa: F401` 한 줄을 빠뜨렸는지 확인하세요.

### 6.18.7 `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: todos`

마이그레이션을 적용하지 않은 채로 라우트를 호출한 경우입니다. `uv run alembic upgrade head`를 한 번 실행하면 해결됩니다.

### 6.18.8 SQLite에서 `Boolean`이 `0/1`로 나옴

SQLite는 진짜 BOOLEAN 타입이 없고 INTEGER로 저장합니다. 그래서 외부 도구(예: `sqlite3` CLI)로 직접 보면 `is_done`이 `0`이나 `1`로 보입니다. **이는 정상입니다.** SQLAlchemy/Pydantic이 응답할 때는 `true`/`false`로 변환해 줍니다. PostgreSQL/MySQL은 진짜 BOOLEAN이라 그대로 `true`/`false`입니다.

### 6.18.9 PostgreSQL 연결 시 `password authentication failed`

비밀번호가 틀렸거나 사용자가 없습니다. Docker로 띄웠다면 `docker logs fastapi-pg`로 초기화 로그를 보고, 환경 변수가 우리가 지정한 것과 일치하는지 확인합니다.

### 6.18.10 `RuntimeWarning: coroutine 'AsyncSession.execute' was never awaited`

위 6.18.2의 `await` 누락이 원인입니다.

---

## 6.19 더 깊이 보기 — 이 챕터에서 의도적으로 미룬 것

이 챕터는 입문 분량을 지키기 위해 다음을 미뤘습니다.

- **관계(1:N, N:M) 모델링** — 11장 Blog API.
- **`selectinload`/`joinedload`의 자세한 비교** — 11장.
- **트랜잭션 중첩과 SAVEPOINT** — 본 가이드 범위 외(필요해지면 SQLAlchemy 공식 문서로).
- **Alembic의 분기·병합·라벨** — 본 가이드 범위 외.
- **수동(autogenerate 안 쓰는) 마이그레이션 작성** — 11장에서 데이터 마이그레이션 예시.
- **PostgreSQL 특화 기능(JSONB, 배열, 풀텍스트 검색)** — 12장 레퍼런스.
- **SQLAlchemy의 `Session.scalars(...)` 단축 표기** — 같은 일을 더 짧게 쓰는 형태가 있지만(`await session.scalars(select(Todo))`), 본 가이드는 표준적인 `execute() → scalars()` 흐름을 일관되게 사용했습니다.

---

## 6.20 이 챕터 요약

- 데이터베이스는 **요청 사이에 자료가 살아 있어야 하는** 모든 백엔드의 기본이다.
- **ORM**은 DB의 표를 파이썬 클래스에 매핑해, SQL을 직접 쓰지 않고도 객체처럼 데이터를 다룰 수 있게 한다.
- 이 가이드는 **SQLAlchemy 2.0 (async)** + **Alembic**을 표준으로 못 박는다.
- DB 드라이버는 비동기 전용을 쓴다: SQLite=`aiosqlite`, PostgreSQL=`asyncpg`, MySQL=`asyncmy`.
- 모델은 새 표기법(`Mapped[...]`, `mapped_column(...)`)으로 작성한다 — IDE 지원이 가장 좋다.
- **Pydantic 스키마**(요청·응답 모양)와 **ORM 모델**(DB 매핑)은 분리하고, `from_attributes=True`로 잇는다.
- `app/db.py`의 `get_session()` 의존성이 한 요청 = 한 세션 = 한 트랜잭션을 보장한다. 라우트는 `Depends(get_session)`만 받으면 끝.
- CRUD는 `select(...)`/`session.add(...)`/`session.get(...)`/`session.delete(...)` 그리고 객체 속성 변경 + 자동 UPDATE.
- **Alembic**은 모델 변경을 자동 감지(`autogenerate`)해 마이그레이션 파일을 만들고, `upgrade head`로 적용한다.
- `env.py`를 **비동기 엔진**용으로 한 번 수정해 두면, 이후 챕터들이 모두 그대로 쓴다.
- DB를 SQLite → PostgreSQL → MySQL로 옮길 때 **`DATABASE_URL`만 바꾸면 코드는 그대로**다.
- N+1 문제를 인식하고, 관계 자료를 미리 같이 가져오는 `selectinload`로 해결한다(11장에서 자세히).
- 다음 챕터(07)에서 본 챕터의 Todo 예제를 **라우터 분리 + 더 풍부한 검증·페이지네이션·테스트**로 확장한다.

---

## 부록 A. 본 챕터 예제 전체 파일 목록

`examples/06-SQLAlchemyTodo/` 폴더에 본 챕터의 코드가 모두 들어 있습니다.

```
06-SQLAlchemyTodo/
├── pyproject.toml          # uv add ... 가 만들고 갱신한 의존성 목록
├── uv.lock                 # 잠금 파일
├── .python-version         # 3.13
├── .env.example            # DATABASE_URL 의 기본값 예시
├── .gitignore              # *.sqlite, .env, __pycache__ 등 제외
├── README.md               # 실행·마이그레이션·curl 예시
├── alembic.ini             # Alembic 설정
├── alembic/
│   ├── env.py              # 비동기 엔진용으로 수정된 부트스트랩
│   ├── script.py.mako      # revision 파일 템플릿(기본)
│   └── versions/
│       └── .gitkeep
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI 앱 + 모든 CRUD 라우트
    ├── config.py           # DATABASE_URL
    ├── db.py               # AsyncEngine, async_sessionmaker, get_session
    ├── models.py           # Todo ORM 모델
    └── schemas.py          # TodoCreate, TodoRead, TodoUpdate
```

> **첫 마이그레이션 파일은 의도적으로 비워 두었습니다.** 본 가이드를 따라하는 학습자가 직접 `uv run alembic revision --autogenerate -m "create todos table"`을 실행해 자동 생성되는 흐름을 체험하기 위함입니다. `versions/.gitkeep`만 들어 있습니다.

---

## 부록 B. 자주 쓰는 명령 모음 (치트시트)

```bash
# 프로젝트 시작
uv init
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite

# Alembic 초기화 (한 번만)
uv run alembic init alembic
# → alembic/env.py 를 비동기용으로 수정

# 마이그레이션 만들기 + 적용
uv run alembic revision --autogenerate -m "create todos table"
uv run alembic upgrade head

# 마이그레이션 되돌리기
uv run alembic downgrade -1
uv run alembic downgrade base

# 히스토리 / 현재 상태 보기
uv run alembic history
uv run alembic current

# 서버 실행
uv run uvicorn app.main:app --reload

# DB 옮기기 (예: PostgreSQL)
uv add asyncpg
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"
uv run alembic upgrade head

# SQLite 파일 직접 들여다보기
sqlite3 todo.db
sqlite> .tables
sqlite> .schema todos
sqlite> select * from todos;
sqlite> .quit
```

<a id="ch07"></a>

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
uv init --no-readme           # uv 가 만드는 hello.py 는 곧 지울 거라 README 만 안 만들어둔다
rm -f hello.py main.py        # uv init 이 만든 샘플 스크립트 정리

uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite
uv add pydantic-settings
uv add --dev pytest pytest-asyncio httpx
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
    future=True,
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

전체 코드는 예제 폴더(`alembic/env.py`)에 그대로 있고, 핵심 부분만 옮긴다.

```python
import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.config import settings
from app.db import Base
from app import models  # noqa: F401  -- 모델 등록을 위해 필요

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    # ... offline 분기 (예제 코드 참고)
    ...
else:
    asyncio.run(run_migrations_online())
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
    engine = create_async_engine(TEST_DATABASE_URL, future=True)
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

<a id="ch08"></a>

# 08. 사용자 인증 — JWT와 Bcrypt

> **이 챕터의 목표**
> - **인증(Authentication)**과 **인가(Authorization)**의 차이를 자기 말로 설명할 수 있다.
> - 비밀번호를 평문으로 저장하면 왜 안 되는지, **Bcrypt**가 어떤 원리로 그것을 해결하는지 이해한다.
> - `bcrypt` 라이브러리를 직접 호출해 비밀번호를 해싱·검증한다 (`hashpw`, `checkpw`).
> - **JWT(JSON Web Token)**의 세 부분(Header / Payload / Signature)을 이해하고, 왜 이게 "DB 조회 없이도 사용자를 식별할 수 있는" 토큰이 되는지 설명할 수 있다.
> - `PyJWT`로 토큰을 발급하고 검증한다 (`jwt.encode`, `jwt.decode`).
> - FastAPI의 `OAuth2PasswordBearer`와 `Depends`를 조합해 **회원가입 → 로그인 → 보호된 라우트** 흐름을 처음부터 끝까지 만든다.
> - `is_admin` 플래그로 단순한 **인가(권한 검사)**를 의존성에 합성한다.
> - 운영 환경에서 반드시 지켜야 할 보안 수칙(HTTPS, `SECRET_KEY` 관리, 흔한 실수)을 짚는다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 4~6시간

> **전제**: 05장(라우팅·Pydantic), 06장(SQLAlchemy 비동기 DB 연동), 07장(CRUD)을 마쳤다고 가정합니다. 모델 정의·세션 의존성·라우터 분리 패턴에 익숙하다면 곧장 따라올 수 있습니다.

---

## 8.1 이 챕터에서 만들 것 — 한눈에 보기

이 챕터의 결과물은 **사용자 회원가입과 로그인이 가능한 작은 백엔드**입니다. 코드를 다 따라 치면 다음을 할 수 있는 서버가 손에 남습니다.

- `POST /auth/signup` — 이메일과 비밀번호로 회원가입. **비밀번호는 Bcrypt로 해싱해서 저장**합니다.
- `POST /auth/login` — 로그인하면 JWT 액세스 토큰을 돌려줍니다.
- `GET /users/me` — `Authorization: Bearer <토큰>` 헤더가 있어야만 자기 정보를 볼 수 있는 **보호된 엔드포인트**입니다.
- `GET /users/admin/ping` — 관리자(`is_admin=true`)만 들어갈 수 있는 엔드포인트(인가 맛보기).

전체 흐름은 다음 그림 한 장에 들어갑니다.

```
1) 회원가입
[클라이언트] ──POST /auth/signup {"email","password"}──▶ [FastAPI]
                                                               │
                                       Bcrypt로 password 해싱 │
                                                  ▼
                                              [SQLite DB]
                                                  │
[클라이언트] ◀───────── 200 {id, email, is_admin} ─┘

2) 로그인
[클라이언트] ──POST /auth/login (form: username=email, password)──▶ [FastAPI]
                                                                          │
                                                  Bcrypt로 비번 검증 →   │
                                                  JWT 서명 생성          │
                                                                          ▼
[클라이언트] ◀───── 200 {"access_token": "eyJhbGc...", "token_type": "bearer"}

3) 보호된 라우트 호출
[클라이언트] ──GET /users/me  Authorization: Bearer eyJhbGc...──▶ [FastAPI]
                                                                       │
                                          JWT 서명·만료 검증 →       │
                                          sub(=user id)로 DB 조회      │
                                                                       ▼
[클라이언트] ◀──── 200 {id, email, is_admin}  (또는 401)
```

이 가이드는 **JWT 한 가지 방식만** 끝까지 사용합니다. 세션 쿠키, OAuth2 소셜 로그인(구글·카카오), 매직 링크 등 다른 방식은 일부러 다루지 않습니다 — 입문자가 흔들리지 않도록 한 길로 마칩니다.

> **JWT(JSON Web Token)란?** 서버가 "당신이 누구인지" 정보를 담아 서명한 작은 문자열입니다. 클라이언트는 이 문자열을 들고 다니다가 요청마다 헤더에 실어 보내고, 서버는 서명만 확인하면 되어 **DB 조회 없이도 누구의 요청인지** 식별할 수 있습니다. 모바일 앱·SPA(React/Vue)·외부 API에 가장 널리 쓰입니다. 자세한 내용은 8.5에서 풀어 설명합니다.

---

## 8.2 인증 vs 인가 — 두 단어의 차이부터

> **인증(Authentication, AuthN)이란?** "당신이 진짜 그 사람이 맞는지"를 확인하는 절차입니다. 이메일·비밀번호로 로그인하는 단계가 인증입니다. 결과는 보통 "예/아니오" 둘 중 하나입니다.

> **인가(Authorization, AuthZ)란?** "이 사람이 이 동작을 할 권한이 있는지"를 확인하는 절차입니다. 로그인은 됐는데(=인증 통과), 다른 사람의 글을 지우려 한다면 인가에서 막아야 합니다.

두 단어는 영어 첫 글자(Auth)가 같아 한국어로도 자주 헷갈립니다. 다음 표가 가장 빠른 정리입니다.

| 항목 | 인증 (AuthN) | 인가 (AuthZ) |
|------|--------------|--------------|
| 묻는 질문 | "당신은 누구인가?" | "당신은 이걸 해도 되는가?" |
| 통과 기준 | 신원 확인 (비밀번호 일치, 토큰 유효) | 권한 확인 (역할/소유 관계) |
| 실패 시 응답 | **401 Unauthorized** | **403 Forbidden** |
| 시점 | 보통 한 번(로그인) | 매 요청마다 |

자주 인용되는 한 줄 비유: **인증은 "건물 출입증을 발급받는 것"**, **인가는 "그 출입증으로 어느 방에 들어갈 수 있는지 확인하는 것"** 입니다. 출입증(JWT) 자체는 신원만 증명할 뿐, 그 사람이 "사장실"이나 "서버실"에 들어갈 수 있는지는 별도의 권한 정책이 결정합니다.

이 챕터에서는 **인증 흐름을 자세히 만들고, 인가는 가장 단순한 형태(`is_admin` 플래그)로 맛보기**합니다. 본격적인 인가(역할·권한 시스템, ACL 등)는 종합 예제(10·11장)에서 더 다룹니다.

---

## 8.3 비밀번호 저장 — 왜 평문은 절대 안 되는가

### 8.3.1 비밀번호를 그대로 DB에 넣으면 생기는 일

상상해 봅시다. 우리가 회원가입 라우트를 만들면서, 사용자가 보낸 비밀번호 `"hunter2"` 를 그대로 `users` 테이블의 `password` 열에 저장했다고 칩시다. 그러면 다음 두 가지 사고가 한 번에 가능합니다.

1. **DB 유출**: 운영 서버가 해킹당하거나, 백업 파일이 잘못 공유되거나, 내부 직원이 DB를 통째로 덤프하면, 모든 사용자의 평문 비밀번호가 노출됩니다.
2. **재사용 비밀번호 피해**: 사용자들은 보통 같은 비밀번호를 여러 사이트에서 씁니다. 우리 서비스 비번이 노출되면 그 사람의 다른 서비스(은행, 메일 등)까지 위험해집니다.

이 둘은 "관리자가 신경을 더 쓰면 막을 수 있는 문제"가 아닙니다. **저장 방식 자체를 바꿔야** 막을 수 있습니다.

### 8.3.2 해결책 — 한 방향 함수(해싱)

답은 **한 방향 함수**(되돌릴 수 없는 변환)로 비밀번호를 바꿔서 저장하는 것입니다. 이걸 **해싱(hashing)**이라고 부릅니다.

> **해싱(hashing)이란?** 어떤 입력이든 정해진 길이의 출력 문자열(=해시)로 바꾸는 것입니다. 같은 입력은 항상 같은 출력을 내고, 출력만 봐서는 입력을 거꾸로 알 수 없습니다. 비유하자면 "고기를 갈면 패티가 되지만, 패티를 다시 고기로 되돌릴 수는 없다"와 같습니다.

해싱한 값을 DB에 저장하면, 설령 DB가 통째로 유출돼도 공격자는 원래 비밀번호를 직접 알 수 없습니다. 사용자가 다음에 로그인할 때는 그 사람이 보낸 평문 비밀번호를 **같은 함수로 다시 해싱해서** 저장된 해시와 비교합니다. 같으면 통과.

> **잠깐, 그러면 SHA-256 같은 일반 해시 함수를 쓰면 되는 거 아닌가요?** 안 됩니다. SHA-256은 너무 빠릅니다. 공격자가 미리 만들어 둔 거대한 사전(=레인보우 테이블)이나, 단순한 무차별 대입(brute force)으로 한 시간에 수십억 개를 시도해 볼 수 있습니다. 비밀번호용 해시는 **일부러 느려야** 합니다.

### 8.3.3 Bcrypt — 비밀번호용으로 설계된 해시

**Bcrypt**는 1999년에 Niels Provos와 David Mazières가 발표한, **비밀번호 저장을 위해 설계된 해싱 알고리즘**입니다. 핵심 특징은 두 가지입니다.

1. **느림(by design)**: 일부러 한 번 해싱하는 데 수백 밀리초가 걸리도록 설계되었습니다. **코스트 팩터(cost factor)** 라는 정수를 1씩 올릴 때마다 처리 시간이 두 배가 됩니다(보통 12를 씁니다 → 한 번에 100~400ms). 사용자 한 명의 로그인은 0.3초 정도라 별로 안 느리지만, 공격자가 1억 개를 시도하려면 1억 × 0.3초 = 1년 단위로 걸립니다.
2. **솔트(salt) 자동 처리**: 같은 비밀번호라도 사용자마다 다른 결과가 나오도록 임의의 값(=솔트)을 함께 섞어 해싱합니다. Bcrypt는 이 솔트를 자동으로 생성하고, 만들어진 해시 문자열 안에 솔트까지 함께 적어둡니다.

> **솔트(salt)란?** 비밀번호를 해싱할 때 함께 섞는 임의의 값입니다. 같은 비밀번호 `"hunter2"`도 사용자 A와 B가 쓸 때 솔트가 다르면 결과가 완전히 달라집니다. 이렇게 하면 **레인보우 테이블 공격**(미리 흔한 비밀번호의 해시를 다 계산해 둔 사전)을 무력화할 수 있습니다.

Bcrypt가 만들어낸 해시 문자열은 다음처럼 생겼습니다.

```
$2b$12$N9qo8uLOickgx2ZMRZoMye.IjPeQfZoMUd/c1mY9Td6P9kKmJ2j7C
└┬┘ └┬┘ └────────────────────────┬────────────────────────┘
 │   │                           │
 │   │                           해시 본체 (솔트 22자 + 결과 31자)
 │   코스트 팩터 (12)
 알고리즘 버전 ($2b$ = bcrypt)
```

이 한 줄에 알고리즘 버전, 코스트, 솔트, 결과가 모두 들어 있어서 **별도로 솔트를 따로 저장할 필요가 없습니다.** 검증할 때도 이 문자열만 있으면 됩니다.

### 8.3.4 이 가이드에서는 `bcrypt` 라이브러리를 직접 쓴다

파이썬 생태계에는 비밀번호 해싱을 도와주는 라이브러리가 여러 개 있습니다.

- **`bcrypt`** — Bcrypt를 그대로 노출하는 가장 단순한 라이브러리. 함수가 두 개뿐(`hashpw`, `checkpw`).
- **`passlib`** — 여러 알고리즘(bcrypt, argon2, scrypt 등)을 통일된 API로 감싼 추상화 라이브러리. 한때 표준이었으나 2020년대 후반 들어 유지보수 빈도가 줄었고, 입문자에게는 한 겹 더 있는 추상화가 오히려 디버깅을 어렵게 합니다.
- **`argon2-cffi`** — Argon2 알고리즘 라이브러리. 더 최신이지만 입문자에게는 옵션이 많아 부담이 됩니다.

**이 가이드는 `bcrypt`를 직접 사용합니다.** 함수가 두 개뿐이라 머릿속 모델이 단순해지고, 추상화 한 겹이 줄어 오류가 났을 때 추적이 쉽습니다. `passlib`이 익숙하더라도 이 가이드 안에서는 `bcrypt`만 씁니다 — 일관성을 위해서입니다.

---

## 8.4 `bcrypt` 라이브러리 사용법

### 8.4.1 설치

```bash
uv add bcrypt
```

집필 시점 기준 4.x 버전대를 받습니다.

### 8.4.2 가장 짧은 예제

```python
import bcrypt

plain = "hunter2"

# 1) 해싱
hashed: bytes = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
print(hashed)
# b'$2b$12$N9qo8uLOickgx2ZMRZoMye.IjPeQfZoMUd/c1mY9Td6P9kKmJ2j7C'

# 2) 검증
ok: bool = bcrypt.checkpw(plain.encode("utf-8"), hashed)
print(ok)  # True

ok2: bool = bcrypt.checkpw("wrongpassword".encode("utf-8"), hashed)
print(ok2)  # False
```

API는 두 함수가 전부입니다.

- **`bcrypt.hashpw(password: bytes, salt: bytes) -> bytes`** — 평문을 해싱한 결과를 돌려줍니다.
- **`bcrypt.checkpw(password: bytes, hashed: bytes) -> bool`** — 평문과 저장된 해시가 같은 비밀번호에서 나왔는지 검사합니다.

### 8.4.3 함정 1 — 입력은 **bytes**여야 한다

`bcrypt`의 모든 입력은 **`str`이 아닌 `bytes`** 입니다. 평문 문자열을 그대로 넘기면 `TypeError`가 납니다.

```python
# X 잘못된 예 — TypeError: Unicode-objects must be encoded before hashing
bcrypt.hashpw("hunter2", bcrypt.gensalt())

# O 올바른 예 — UTF-8로 인코딩
bcrypt.hashpw("hunter2".encode("utf-8"), bcrypt.gensalt())
```

`checkpw`도 똑같이 두 인자가 모두 `bytes`여야 합니다. 인코딩 방식은 **반드시 `utf-8`** 로 통일하세요. 어떤 사용자는 한국어, 다른 사용자는 영어 비밀번호일 수 있는데 인코딩이 들쑥날쑥하면 검증이 실패합니다.

### 8.4.4 함정 2 — 출력도 **bytes**여서 DB에 넣을 때는 디코딩해야 한다

`hashpw`의 결과는 `bytes`입니다. 우리 DB의 비밀번호 해시 컬럼은 보통 `String` 타입(VARCHAR)이라, `bytes`를 그대로 넣으면 ORM이 잘못 변환할 수 있습니다.

이 가이드의 표준 패턴은 **DB에 넣기 직전에 UTF-8 문자열로 디코딩**하는 것입니다.

```python
hashed_bytes = bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt())
hashed_str = hashed_bytes.decode("utf-8")   # ← DB에는 이걸 저장
```

검증할 때는 반대로, DB에서 꺼낸 `str`을 다시 `bytes`로 인코딩해 넘깁니다.

```python
db_value: str = user.hashed_password   # DB에서 꺼낸 문자열
ok = bcrypt.checkpw(plain.encode("utf-8"), db_value.encode("utf-8"))
```

> **왜 처음부터 bytes로 저장하지 않나요?** SQLAlchemy의 `String` 컬럼은 기본적으로 텍스트로 다뤄집니다. `LargeBinary`로 바꿔도 되지만, Bcrypt 해시는 **출력이 모두 ASCII 문자**라 `String`으로 저장해도 정보 손실이 없습니다. 일관성과 가독성(DB 콘솔로 들여다볼 때)을 위해 문자열로 저장하는 패턴이 가장 흔합니다.

### 8.4.5 함정 3 — Bcrypt는 **비밀번호 길이가 72바이트로 제한**된다

이 함정이 가장 잘 알려져 있지 않습니다. **Bcrypt는 입력의 첫 72바이트만 사용**합니다. 73바이트째부터는 그냥 무시됩니다. 즉, 다음 두 비밀번호는 Bcrypt 입장에서 **같은 비밀번호**입니다.

```
"a" * 72            # 72개의 a
"a" * 72 + "Z"      # 72개의 a + 추가로 Z 한 글자
```

영어 알파벳은 1글자=1바이트라 72글자까지 안전하지만, **한국어는 UTF-8 기준 한 글자가 3바이트**라서 한국어 24글자만 넘어가도 잘림이 시작됩니다. 사용자가 24글자짜리 한국어 문장으로 비밀번호를 만들었는데 25번째 글자를 바꿔도 로그인이 통과되는, 매우 헷갈리는 버그가 됩니다.

해결책은 두 가지입니다.

1. **회원가입에서 길이 제한을 명시한다** — 가장 단순한 길. 영어 기준 64자, UTF-8 바이트 기준 72바이트로 제한하고 사용자에게 알립니다.
2. **Bcrypt에 넘기기 전에 SHA-256으로 한 번 줄인다** — 입력을 SHA-256 해시(32바이트)로 먼저 줄이고, 그 32바이트를 Bcrypt에 넘기는 패턴입니다. Django가 이 방식을 씁니다. 단점은 알고리즘이 한 겹 늘고, 일부 보안 분석가가 이 합성을 "비표준"이라고 비판한다는 점입니다.

**이 가이드는 1번(길이 제한)을 채택**합니다. 입문자가 이해하기 쉽고, 표준에서 벗어나지 않기 때문입니다. 이 가이드의 `security.py`는 다음처럼 검증합니다.

```python
MAX_PASSWORD_BYTES = 72

def hash_password(plain: str) -> str:
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"비밀번호가 너무 깁니다(UTF-8 기준 {MAX_PASSWORD_BYTES}바이트 초과). "
            f"한국어는 글자당 3바이트로 계산됩니다."
        )
    return bcrypt.hashpw(encoded, bcrypt.gensalt()).decode("utf-8")
```

### 8.4.6 코스트 팩터를 직접 지정하고 싶다면

`bcrypt.gensalt()`는 기본 코스트 12를 씁니다. 더 강하게 하려면 인자로 넘깁니다.

```python
salt = bcrypt.gensalt(rounds=14)   # 12 → 14: 한 번에 4배 더 느려짐
```

**이 가이드는 기본값(12)** 을 그대로 씁니다. 2026년 시점의 일반 서버에서 12는 한 번에 약 100~300ms입니다 — 사용자 입장에서는 거의 느낌이 없고, 공격자에게는 충분히 비쌉니다. 하드웨어가 더 빨라지는 미래에는 14, 16으로 올리는 것을 고려해야 합니다.

---

## 8.5 JWT — 토큰 한 장에 신원이 담기는 방식

### 8.5.1 JWT가 필요한 이유 — 세션과의 비교

옛날 웹은 로그인 상태를 **서버 메모리에 저장**했습니다(=세션). 사용자가 로그인하면 서버가 "이 사람은 로그인 상태"라고 자기 메모리에 적어두고, 그 메모리 상의 식별자(세션 ID)를 쿠키로 클라이언트에 전달합니다. 다음 요청부터는 쿠키만 보고 누군지 알아냅니다.

이 방식은 단점이 있습니다.

- **서버를 여러 대로 늘리기 어렵다** — A 서버에서 로그인했는데 다음 요청이 B 서버로 가면, B는 그 세션을 모릅니다. 공유 저장소(Redis 등)가 추가로 필요해집니다.
- **모바일 앱·SPA와 잘 안 맞는다** — 쿠키는 브라우저용 메커니즘이라 모바일 앱에서는 직접 다루기 번거롭습니다.

**JWT는 이 문제를 "토큰 자체에 신원 정보를 다 적어두자"는 발상으로 풉니다.** 서버 메모리에 아무것도 저장하지 않아도, 토큰 안에 "이 사람은 사용자 42번이고 1시간 후 만료"라고 적혀 있으면 끝입니다. 이걸 **스테이트리스(stateless) 인증**이라고 부릅니다.

| 항목 | 세션 (전통적) | JWT (이 가이드) |
|------|---------------|-----------------|
| 신원 정보 | 서버 메모리/DB에 저장 | 토큰 자체에 들어 있음 |
| 클라이언트가 들고 다니는 것 | 세션 ID (의미 없는 식별자) | JWT (의미 있는 데이터+서명) |
| 서버 확장 | 공유 저장소 필요 | 키만 같으면 어느 서버든 검증 가능 |
| 로그아웃 | 서버에서 세션 삭제하면 즉시 | 즉시 무효화 어려움(토큰이 만료될 때까지 유효) |
| 모바일/SPA 친화도 | 보통 | 매우 좋음 |

이 가이드는 **모바일 앱·SPA 시대에 가장 흔한 패턴**인 JWT만 다룹니다.

### 8.5.2 JWT는 어떻게 생겼나 — 세 부분으로 나뉜다

> **JWT의 구조 한 페이지 정리**
>
> JWT는 **점(`.`)으로 연결된 세 덩어리** 입니다. 각 덩어리는 Base64URL로 인코딩된 텍스트입니다.
>
> ```
> Header . Payload . Signature
> ```
>
> 실제 토큰은 다음과 같이 보입니다(가독성을 위해 줄을 나눴습니다).
>
> ```
> eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
> .
> eyJzdWIiOiI0MiIsImV4cCI6MTcxNzAwMDAwMCwiaWF0IjoxNzE2OTk2NDAwfQ
> .
> SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
> ```
>
> **1) Header (헤더)** — 토큰 자체의 메타정보. 어떤 알고리즘으로 서명했는지 등을 적습니다.
>
> ```json
> {"alg": "HS256", "typ": "JWT"}
> ```
>
> **2) Payload (페이로드 / 클레임)** — 실제 데이터. "이 토큰의 주인은 누구이고, 언제 만료되는지" 같은 정보를 담습니다. JWT 표준은 자주 쓰는 클레임에 짧은 이름을 정해 두었습니다.
>
> - `sub` (subject): **주체**. 보통 사용자 ID. 이 가이드의 핵심 클레임.
> - `exp` (expiration): **만료 시각**. Unix timestamp. 이걸 지나면 토큰은 무효.
> - `iat` (issued at): **발급 시각**. Unix timestamp.
> - `nbf` (not before): 이 시각 이전에는 사용 불가.
> - `iss` (issuer): 발급자.
> - `aud` (audience): 수신자.
> - `jti` (JWT ID): 토큰의 고유 ID(블랙리스트 구현 시 유용).
>
> **3) Signature (서명)** — 위 Header와 Payload를 합쳐 서버의 비밀키로 서명한 결과. 토큰의 위변조를 막는 핵심.
>
> 서명 공식(HS256 기준):
> ```
> Signature = HMAC_SHA256(
>     Base64URL(Header) + "." + Base64URL(Payload),
>     SECRET_KEY
> )
> ```
>
> **중요: Payload는 암호화되지 않습니다.** 누구나 Base64URL로 디코딩하면 안의 내용을 그대로 읽을 수 있습니다. JWT가 보장하는 것은 "변조 불가능"(서명이 일치하면 서버가 만든 게 맞다)이지 "비밀 유지"가 아닙니다. 그래서 **비밀번호·민감 개인정보를 Payload에 넣으면 안 됩니다.** `sub`(=user id)와 `exp` 정도가 표준이고, 이 가이드도 그렇게 합니다.

### 8.5.3 토큰 검증의 흐름

서버가 클라이언트의 요청에서 받은 JWT를 검증할 때 일어나는 일은 다음과 같습니다.

1. 토큰을 점(`.`)으로 세 부분으로 나눈다.
2. Header와 Payload를 다시 합쳐, **자기가 가진 비밀키로 서명을 다시 계산**한다.
3. 그 결과가 토큰에 적힌 Signature와 같은지 비교한다. → **다르면 거부.**
4. Payload의 `exp`(만료)를 본다. 지났으면 거부.
5. Payload의 `sub`로 사용자를 식별해 라우트로 넘긴다.

핵심은 **2번과 3번**입니다. 비밀키를 모르는 사람은 Payload를 바꾼 새 Signature를 만들 수 없으므로, 토큰을 위조할 수 없습니다. **비밀키 한 개만 안전하게 지키면, 서버 메모리에 아무 상태가 없어도 인증이 됩니다.**

### 8.5.4 HS256 vs RS256 — 대칭 키 vs 비대칭 키

JWT의 서명 알고리즘은 여러 가지가 있는데, 입문 단계에서 알아둘 두 가지는 **HS256**과 **RS256**입니다.

| 항목 | HS256 (대칭) | RS256 (비대칭) |
|------|--------------|----------------|
| 키 종류 | 비밀키 1개 (서명·검증 모두에 사용) | 비밀키(서명) + 공개키(검증) 쌍 |
| 알고리즘 | HMAC-SHA256 | RSA-SHA256 |
| 검증 주체 | 서명한 서버만 가능 | 공개키를 받은 누구나 가능 |
| 키 길이 | 32바이트 이상 임의 문자열 | 2048비트 이상 RSA 키 |
| 적합한 상황 | **서버가 자기 토큰만 검증** | 여러 서비스가 한 토큰을 공유 검증 |
| 구현 난이도 | 매우 단순 | 키 페어 관리 필요 |

**이 가이드는 HS256만 사용합니다.** 우리가 만드는 백엔드는 자기가 발급한 토큰을 자기가 검증하므로, 비대칭 키의 복잡함이 필요 없습니다. 외부 서비스(다른 마이크로서비스, 모바일 앱의 검증 라이브러리 등)에게 토큰 검증을 위임해야 한다면 그때 RS256을 도입합니다.

> **HS256의 한계** — 비밀키 하나가 모든 검증을 책임지므로, 그 키가 유출되면 누구나 토큰을 위조할 수 있습니다. 그래서 비밀키 관리(다음 절)가 핵심입니다.

### 8.5.5 `SECRET_KEY` 관리 — 절대 코드에 넣지 말 것

비밀키를 코드 파일에 직접 적으면 안 됩니다. 이유는 자명합니다.

- **Git에 그대로 커밋된다.** 공개 저장소든 비공개 저장소든, 한 번 들어간 비밀키는 git 히스토리에 영구히 남습니다.
- **개발·테스트·운영의 키가 같아진다.** 개발 환경의 키가 실수로 노출되면 운영도 위험해집니다.

이 가이드의 약속은 다음과 같습니다.

1. 비밀키는 **환경 변수 `SECRET_KEY`** 에서 읽는다.
2. 개발 중에는 프로젝트 루트의 `.env` 파일에 적어두고, **`.env`는 git에 절대 커밋하지 않는다**(`.gitignore`로 제외).
3. **`.env.example`** 이라는 예시 파일은 커밋한다 — 안에는 진짜 키가 아닌 샘플 값(`SECRET_KEY=please-change-this`)만 넣는다.
4. 운영 환경에서는 클라우드 비밀 관리자(AWS Secrets Manager, GCP Secret Manager 등)나 컨테이너 오케스트레이터의 비밀 기능을 통해 환경 변수로 주입한다.

비밀키 만들기는 한 줄이면 됩니다.

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
# 예시 출력: jGv-x7qPq2Z...길고 임의로 보이는 문자열
```

`secrets.token_urlsafe(n)`은 보안용으로 충분히 강한 난수를 만듭니다. **48바이트 이상**(=URL-safe Base64 64자 정도)을 권장합니다.

### 8.5.6 만료 시간 — 짧을수록 안전, 길수록 편함

`exp` 클레임은 토큰의 만료 시각입니다. 이 가이드는 다음 기본값을 씁니다.

- **액세스 토큰: 60분** (1시간)
- **갱신 토큰(refresh token): 도입은 8.13절에서 짧게 언급. 이 가이드의 기본 흐름에서는 단순화를 위해 다루지 않음.**

만료가 짧으면 토큰이 유출돼도 피해 시간이 짧아 안전하지만, 사용자가 자주 다시 로그인해야 합니다. 모바일 앱에서는 보통 **짧은 액세스 토큰 + 긴 갱신 토큰**의 조합으로 둘의 단점을 상쇄합니다(이 가이드는 단순화).

---

## 8.6 PyJWT — 토큰 만들고 검증하기

### 8.6.1 설치

```bash
uv add pyjwt
```

집필 시점 기준 2.8.x 이상이 받아집니다.

> **이름이 헷갈리는 점** — 패키지 이름은 `pyjwt`이지만, 코드에서 `import`할 때는 `import jwt`입니다. PyPI 검색이나 README에서는 "PyJWT"로 통칭합니다. `python-jose`라는 비슷한 라이브러리도 있는데, 그건 별도이고 이 가이드는 PyJWT만 씁니다.

### 8.6.2 가장 짧은 예제 — `encode` / `decode`

```python
import jwt
from datetime import datetime, timezone, timedelta

SECRET = "my-very-secret-key"
ALG = "HS256"

# 1) 토큰 만들기
now = datetime.now(timezone.utc)
payload = {
    "sub": "42",                                      # 사용자 ID
    "iat": now,                                       # 발급 시각
    "exp": now + timedelta(minutes=60),               # 만료 시각
}
token: str = jwt.encode(payload, SECRET, algorithm=ALG)
print(token)
# eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0M...

# 2) 토큰 검증하기
decoded: dict = jwt.decode(token, SECRET, algorithms=[ALG])
print(decoded)
# {'sub': '42', 'iat': 1717000000, 'exp': 1717003600}
```

API는 핵심이 두 함수입니다.

- **`jwt.encode(payload: dict, key: str, algorithm: str) -> str`**
- **`jwt.decode(token: str, key: str, algorithms: list[str]) -> dict`**

### 8.6.3 함정 1 — `algorithms`는 **리스트**다

`encode`는 단수(`algorithm=`)인데 `decode`는 복수(`algorithms=`)에 **리스트**를 받습니다. 헷갈리면 안 됩니다.

```python
jwt.encode(payload, SECRET, algorithm="HS256")        # 단수, 문자열
jwt.decode(token, SECRET, algorithms=["HS256"])       # 복수, 리스트
```

**왜 리스트인가?** "허용할 알고리즘 목록"을 명시하라는 뜻입니다. 옛날 PyJWT 버전에서 `algorithms` 인자를 비워두면 기본적으로 모든 알고리즘을 허용했고, 이게 `alg=none`(서명 없음) 공격을 가능하게 한 보안 사고가 있었습니다. 그래서 지금은 **반드시 명시**해야 합니다.

### 8.6.4 함정 2 — `datetime`을 그대로 넣을 수 있지만, **반드시 timezone-aware**

`exp`와 `iat`는 Unix timestamp(정수)여야 하지만, PyJWT는 `datetime` 객체를 자동으로 정수로 변환해 줍니다. 단, **timezone 정보가 있는(=aware)** `datetime`이어야 합니다.

```python
# X 위험 — naive datetime은 시스템 타임존에 따라 결과가 달라짐
exp = datetime.now() + timedelta(minutes=60)

# O 안전 — UTC 명시
exp = datetime.now(timezone.utc) + timedelta(minutes=60)
```

서버가 UTC 기준이 아닌 곳(예: 한국 시간)에서 도는데 naive datetime을 넣으면, 토큰의 만료가 한국 시간으로 해석되어 9시간이 어긋날 수 있습니다. 항상 `timezone.utc`로 통일하세요.

### 8.6.5 만료된 토큰의 처리

`jwt.decode`는 만료가 지난 토큰을 발견하면 **`jwt.ExpiredSignatureError`** 예외를 던집니다. 위변조된 토큰은 **`jwt.InvalidTokenError`**(또는 그 하위 예외) 입니다.

```python
import jwt

try:
    payload = jwt.decode(token, SECRET, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    # "토큰이 만료되었습니다"
    raise
except jwt.InvalidTokenError:
    # "토큰이 유효하지 않습니다" (서명 불일치, 형식 오류 등)
    raise
```

`InvalidTokenError`가 모든 오류의 부모이므로, 한 번에 잡고 싶으면 그것만 잡아도 됩니다. 이 가이드의 `security.py`는 두 가지를 구분해 처리합니다.

### 8.6.6 토큰 만들기 / 검증을 함수로 묶기

매 라우트에서 직접 `jwt.encode`/`jwt.decode`를 호출하면 코드가 흩어집니다. 이 가이드는 `app/security.py`에 **두 함수**를 두고 그 안에서 모든 토큰 처리를 합니다.

```python
def create_access_token(subject: str, expires_minutes: int = 60) -> str: ...
def decode_access_token(token: str) -> TokenPayload: ...
```

자세한 구현은 8.10절(예제 코드)에서 다룹니다.

---

## 8.7 FastAPI의 `OAuth2PasswordBearer` — 어디까지가 OAuth2인가

### 8.7.1 첫인상이 헷갈리는 클래스

FastAPI 공식 튜토리얼을 보면 `OAuth2PasswordBearer`라는 이름이 등장합니다. 이름이 길고 무서워 보이지만, 실제로 하는 일은 단순합니다.

```python
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
```

이 한 줄이 만드는 것은 **"`Authorization: Bearer <토큰>` 헤더에서 토큰 문자열을 꺼내주는 의존성"** 입니다. 그게 전부입니다.

### 8.7.2 그럼 OAuth2는 뭐가 OAuth2인가?

엄밀히 말하면 OAuth2는 **다른 서비스의 일부 권한을 빌려오는 표준 흐름**입니다. "구글 계정으로 로그인", "카카오 로그인" 같은 것의 뼈대입니다. 우리가 만드는 회원가입+로그인은 **OAuth2의 일부 모양만 빌려온 것**이고, 진짜 OAuth2 흐름(authorization code, client_id/secret 등)은 따라가지 않습니다.

`OAuth2PasswordBearer`가 빌려오는 것은 다음 두 가지뿐입니다.

1. **Bearer 토큰 헤더 형식** — `Authorization: Bearer <토큰>` 표준.
2. **`tokenUrl` 명시** — Swagger UI가 "Authorize" 버튼에서 어디로 로그인 요청을 보낼지 알아내는 메타데이터.

이게 다입니다. 우리 서버는 진짜 OAuth2 서버가 아닙니다. **이름에 너무 겁먹지 말고, "Bearer 헤더에서 토큰 꺼내기" 도구라고 받아들이세요.**

### 8.7.3 `OAuth2PasswordRequestForm` — 로그인 입력 폼

비슷하게 이상한 이름이 한 번 더 나옵니다. **`OAuth2PasswordRequestForm`**.

```python
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    # form.username, form.password 가 들어옴
    ...
```

이것은 "로그인 요청을 **JSON이 아닌 `application/x-www-form-urlencoded` 폼**으로 받게 한다"는 의존성입니다. 필드는 `username`, `password` 두 개로 고정입니다(OAuth2 표준이 그렇게 정해두었습니다).

> **왜 JSON이 아니라 form인가?** OAuth2 표준이 그렇기 때문입니다. 그리고 Swagger UI의 "Authorize" 버튼이 이 형식을 자동으로 인식해 로그인 폼을 띄워줍니다. 이 가이드는 표준에 맞추기 위해 form으로 받습니다.

이 가이드의 약속은 **`username` 필드에 사용자의 이메일을 받는다**는 것입니다. 즉:

- 사용자에게 보이는 라벨: "이메일"
- 실제 HTTP 요청의 필드 이름: `username`

이게 헷갈리지만 OAuth2 표준 호환을 위한 어쩔 수 없는 타협입니다. 라우트 안에서 `form.username`을 받아 이메일로 처리하면 됩니다.

### 8.7.4 자동 문서(`/docs`)에서 토큰을 어떻게 넣는가

`OAuth2PasswordBearer(tokenUrl="/auth/login")`을 등록해 두면 Swagger UI(`/docs`)에 **"Authorize" 버튼**이 자동으로 생깁니다. 클릭하면 username/password 폼이 뜨고, 이 폼이 `tokenUrl`로 지정한 엔드포인트(`/auth/login`)에 form-encoded 요청을 보냅니다. 응답에서 받은 `access_token`이 자동으로 모든 보호된 엔드포인트의 `Authorization` 헤더에 채워집니다.

**즉, 코드를 한 줄도 안 바꾸고도 Swagger에서 로그인 → 토큰 받기 → 보호된 라우트 호출이 한 번에 됩니다.** 이게 FastAPI 인증 시스템의 가장 매력적인 부분입니다.

---

## 8.8 `Depends`로 `get_current_user` 만들기

### 8.8.1 의존성 사슬 한 그림

`/users/me` 같은 보호된 라우트는 다음 의존성 사슬을 거칩니다.

```
요청 헤더의 Authorization
        │
        ▼
oauth2_scheme  (OAuth2PasswordBearer 인스턴스)
        │  → "Bearer ..." 에서 토큰 문자열만 꺼냄
        ▼
get_current_user  (우리가 만드는 의존성 함수)
        │  → 토큰 검증 + DB에서 사용자 조회
        ▼
라우트 함수의 인자: current_user: User
```

각 단계를 함수로 만들고, 다음 단계에서 `Depends(...)`로 주입받습니다.

### 8.8.2 `get_current_user`의 본문 흐름

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    # 1) 토큰 검증 → payload (TokenPayload 모델)
    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="토큰이 만료되었습니다")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다")

    # 2) sub(=user id) 확인
    user_id = int(payload.sub)
    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다")

    return user
```

이 함수가 라우트의 의존성으로 들어가는 모양은 다음과 같습니다.

```python
@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return current_user
```

**라우트 함수 본문은 단 한 줄**입니다. 토큰 파싱, 서명 검증, 만료 체크, DB 조회는 모두 의존성에서 끝났습니다. 이게 FastAPI 의존성 주입의 힘입니다.

### 8.8.3 인가 의존성 합성하기 — `get_current_admin`

`is_admin=True` 인 사용자만 접근할 수 있는 라우트가 필요하다면, **이미 만든 `get_current_user`를 의존성으로 받아 그 위에 권한 검사를 얹으면 됩니다.**

```python
async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="관리자 권한이 필요합니다")
    return current_user
```

라우트에서는 똑같이 `Depends(get_current_admin)`만 쓰면 끝입니다.

```python
@router.get("/admin/ping")
async def admin_ping(admin: User = Depends(get_current_admin)):
    return {"message": "Hello, admin!"}
```

**의존성을 의존성으로 합성하는 패턴은 FastAPI의 핵심**입니다. 권한이 더 복잡해져도(역할 배열, 자원 소유 검사 등) 같은 패턴으로 확장됩니다.

> **401 vs 403의 구분** — "토큰이 없거나 잘못됨" → **401 Unauthorized**(인증 실패). "토큰은 맞는데 권한이 부족함" → **403 Forbidden**(인가 실패). 위 코드의 두 예외가 정확히 이렇게 분기되어 있는지 확인하세요.

---

## 8.9 프로젝트 구조와 의존성

이제 챕터 본문의 코드를 본격적으로 만들 차례입니다. 결과 폴더는 다음과 같이 생기게 됩니다.

```
08-AuthExample/
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
│       └── 0001_create_user.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py            # SECRET_KEY 등 환경 설정
│   ├── db.py                # 비동기 엔진·세션
│   ├── models.py            # User
│   ├── schemas.py           # UserCreate / UserRead / Token / TokenPayload
│   ├── security.py          # 비번 해싱·검증, JWT 생성·검증
│   ├── deps.py              # get_current_user, get_current_admin
│   └── routers/
│       ├── __init__.py
│       ├── auth.py          # /auth/signup, /auth/login
│       └── users.py         # /users/me, /users/admin/ping
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_auth.py
```

각 파일이 무엇을 담는지는 주석에 짧게 적었습니다. 다음 절부터 이 모든 파일을 차례로 만들어 나갑니다.

### 8.9.1 의존성 추가

```bash
uv init 08-AuthExample
cd 08-AuthExample
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite pyjwt bcrypt pydantic-settings "pydantic[email]" python-multipart
uv add --dev pytest httpx pytest-asyncio
```

각 라이브러리의 역할은 [README의 스택 표](../README.md)와 [용어 사전의 도구 절](glossary.md#6-이-가이드에서-쓰는-도구라이브러리)에 정리되어 있습니다. 여기서 새로 등장한 두 가지만 다시 짚습니다.

- **`pyjwt`** — JWT 토큰을 만들고 검증하는 라이브러리. `import jwt`로 씁니다.
- **`bcrypt`** — Bcrypt 해싱 라이브러리. `import bcrypt`로 씁니다.

### 8.9.2 환경 변수 파일 — `.env.example`

프로젝트 루트에 `.env.example` 파일을 만들고 다음을 적습니다.

```bash
DATABASE_URL=sqlite+aiosqlite:///./auth.db
# 실제 운영에서는 아래의 secrets.token_urlsafe(48) 출력으로 교체할 것.
# PyJWT 2.x는 32바이트 미만의 HS256 키를 InsecureKeyLengthWarning으로 경고합니다.
SECRET_KEY=please-change-this-to-32-bytes-or-longer-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

실제 사용할 때는 이 파일을 복사해 `.env`를 만들고 `SECRET_KEY`를 진짜 키로 바꿉니다.

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
# 출력값을 .env의 SECRET_KEY 자리에 붙여넣기
```

`.gitignore`에 `.env`가 들어 있는지 다시 한 번 확인합니다(이 가이드의 표준 `.gitignore`에 이미 들어 있습니다).

---

## 8.10 코드 작성 — 한 파일씩

### 8.10.1 `app/config.py` — 설정 로딩

`Pydantic`의 `BaseSettings`를 써서 환경 변수를 한 번에 읽습니다.

```python
# app/config.py
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """애플리케이션 환경 설정.

    .env 파일과 OS 환경 변수에서 값을 읽어 들입니다.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # 데이터베이스 URL (SQLite + aiosqlite 기본)
    database_url: str = "sqlite+aiosqlite:///./auth.db"

    # JWT 서명용 비밀키 — 운영 환경에서는 반드시 환경 변수로 주입.
    # 기본값은 PyJWT 2.x의 InsecureKeyLengthWarning(<32바이트)을 피하기 위해
    # 32바이트 이상의 더미 문자열로 둔다. 실제 키는 .env에서 덮어쓴다.
    secret_key: str = "please-change-this-to-32-bytes-or-longer-random-string"

    # JWT 알고리즘 — 이 가이드는 HS256 고정
    algorithm: str = "HS256"

    # 액세스 토큰 만료 시간(분)
    access_token_expire_minutes: int = 60


@lru_cache
def get_settings() -> Settings:
    """설정을 한 번만 읽고 캐시한다."""
    return Settings()
```

> **`pydantic-settings`는 별도 패키지** — Pydantic 2.x부터 환경 변수 로딩 기능은 `pydantic_settings`로 분리되었습니다. 위 import가 통하지 않으면 `uv add pydantic-settings`로 추가하세요.

### 8.10.2 `app/db.py` — 비동기 엔진과 세션

06장에서 다룬 패턴과 같습니다. 라우트 의존성으로 사용할 `get_session`이 핵심입니다.

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

# 비동기 엔진 — SQLite + aiosqlite
engine = create_async_engine(settings.database_url, echo=False)

# 세션 팩토리 — 한 요청당 한 세션을 만들기 위한 도장
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """모든 모델 클래스의 부모."""


async def get_session() -> AsyncIterator[AsyncSession]:
    """라우트에서 Depends(get_session)으로 주입받는 비동기 세션."""
    async with AsyncSessionLocal() as session:
        yield session
```

### 8.10.3 `app/models.py` — User 테이블

```python
# app/models.py
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    """회원가입한 사용자 한 명을 표현한다."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
```

> **이메일에 `unique=True`** — DB 레벨에서 같은 이메일을 두 개 못 만들게 잠그는 안전장치입니다. 라우트에서도 회원가입 전에 중복을 체크하지만, 동시에 두 요청이 들어오면 라우트 검사만으로는 막을 수 없습니다. 데이터베이스의 unique 제약이 마지막 방어선입니다.

### 8.10.4 `app/schemas.py` — 입력·출력 스키마와 토큰 모델

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """회원가입 요청 본문."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserRead(BaseModel):
    """회원 정보 응답 — 비밀번호 해시는 절대 포함하지 않는다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    """로그인 응답 — OAuth2 표준 형식."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """디코딩된 JWT 페이로드의 타입화된 표현."""

    sub: str
    exp: int
    iat: int
```

- **`EmailStr`** 은 Pydantic이 제공하는 이메일 검증 타입입니다. 사용하려면 `uv add "pydantic[email]"`로 부가 의존성을 깔아야 합니다(`email-validator`).
- **`UserRead`에 `hashed_password`가 없음** — 이게 핵심 안전장치입니다. 응답 모델에 비밀번호 해시를 절대 포함시키지 않습니다.

### 8.10.5 `app/security.py` — 해싱·JWT의 모든 함수

이 파일이 이 챕터의 두뇌입니다. 비밀번호 해싱, 검증, 토큰 생성, 토큰 검증의 네 함수가 모두 여기 있습니다.

```python
# app/security.py
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import get_settings
from app.schemas import TokenPayload

settings = get_settings()

# Bcrypt는 입력 첫 72바이트만 사용하므로, 그 이상은 사전에 거른다.
MAX_PASSWORD_BYTES = 72


def hash_password(plain: str) -> str:
    """평문 비밀번호를 Bcrypt로 해싱하고, DB에 저장하기 좋은 문자열로 돌려준다."""
    encoded = plain.encode("utf-8")
    if len(encoded) > MAX_PASSWORD_BYTES:
        raise ValueError(
            f"비밀번호가 너무 깁니다(UTF-8 기준 {MAX_PASSWORD_BYTES}바이트 초과). "
            "한국어는 글자당 3바이트로 계산됩니다."
        )
    hashed_bytes = bcrypt.hashpw(encoded, bcrypt.gensalt())
    return hashed_bytes.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """평문이 저장된 해시와 일치하는지 검사한다."""
    encoded_plain = plain.encode("utf-8")
    encoded_hash = hashed.encode("utf-8")
    if len(encoded_plain) > MAX_PASSWORD_BYTES:
        # 해싱 단계에서 막혔어야 정상이지만, 안전을 위해 비교도 거부.
        return False
    try:
        return bcrypt.checkpw(encoded_plain, encoded_hash)
    except ValueError:
        # 잘못된 해시 문자열이 DB에 있을 때(예: 평문 저장 후 마이그레이션 사고)
        return False


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """sub(=사용자 ID)를 담은 JWT 액세스 토큰을 만든다."""
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
    """JWT를 검증하고 TokenPayload로 돌려준다.

    - 서명 불일치/형식 오류: jwt.InvalidTokenError 또는 그 하위 예외
    - 만료된 경우: jwt.ExpiredSignatureError (InvalidTokenError의 자식)
    """
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

### 8.10.6 `app/deps.py` — 의존성 함수들

```python
# app/deps.py
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import decode_access_token

# tokenUrl은 Swagger UI의 Authorize 버튼이 사용할 로그인 엔드포인트 경로
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """헤더의 Bearer 토큰을 검증하고 현재 사용자를 돌려준다."""
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
    if user is None or not user.is_active:
        raise credentials_exc

    return user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """관리자 권한 확인 — 인증은 끝났고 인가만 검사한다."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자 권한이 필요합니다",
        )
    return current_user
```

> **`WWW-Authenticate: Bearer` 헤더** — 401을 돌려줄 때 이 헤더를 함께 보내는 것이 OAuth2/HTTP 표준입니다. 클라이언트가 "어떤 인증 방식을 써야 하는지" 알 수 있게 해줍니다. 빠뜨려도 동작은 하지만 표준에 맞춰 두는 것이 좋습니다.

### 8.10.7 `app/routers/auth.py` — 회원가입과 로그인

```python
# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, hash_password, verify_password

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
    """이메일+비밀번호로 회원가입.

    - 이메일 중복 체크
    - 비밀번호는 Bcrypt로 해싱해서 저장
    """
    # 이메일 정규화 — 대소문자 무시 일관성
    email = payload.email.lower()

    result = await session.execute(select(User).where(User.email == email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다",
        )

    try:
        hashed = hash_password(payload.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    user = User(email=email, hashed_password=hashed)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post("/login", response_model=Token)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    """form 필드 username(=이메일), password를 받아 액세스 토큰을 돌려준다."""
    email = form.username.lower()

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # 사용자 없음 / 비밀번호 불일치 — 메시지를 같게 해 정보 누설 방지
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

핵심은 두 가지입니다.

1. **회원가입에서 비밀번호 길이 검증을 두 단계로 한다** — Pydantic 스키마(`min_length=8`, `max_length=64`)에서 한 번, `hash_password` 안의 72바이트 검사에서 한 번.
2. **로그인 실패 메시지를 통일한다** — "사용자 없음"과 "비밀번호 틀림"을 구분해서 알려주면 공격자에게 "이 이메일은 가입돼 있다"는 정보를 줍니다. 항상 같은 메시지("이메일 또는 비밀번호가 올바르지 않습니다")로 답합니다.

### 8.10.8 `app/routers/users.py` — 보호된 라우트

```python
# app/routers/users.py
from fastapi import APIRouter, Depends

from app.deps import get_current_admin, get_current_user
from app.models import User
from app.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)) -> User:
    """로그인된 사용자의 정보를 돌려준다."""
    return current_user


@router.get("/admin/ping")
async def admin_ping(admin: User = Depends(get_current_admin)) -> dict[str, str]:
    """관리자만 접근 가능한 라우트(인가 데모)."""
    return {"message": f"Hello, admin {admin.email}!"}
```

라우트 본문이 한 줄~두 줄입니다. 모든 검증·인증·인가가 의존성에서 끝났기 때문입니다.

### 8.10.9 `app/main.py` — 앱 조립

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth as auth_router
from app.routers import users as users_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Auth Example",
        description="08장 — 회원가입·로그인·보호된 라우트 예제",
        version="0.1.0",
    )

    # CORS — 프론트가 다른 도메인일 때 흐름. 개발 단계에서는 * 도 가능.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.include_router(auth_router.router)
    app.include_router(users_router.router)

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
```

`app.routers` 모듈 두 개를 한 줄씩 등록하면 끝입니다. 라우트 안에서 도메인별로 깔끔하게 분리되어 있어, 큰 프로젝트로 자라나도 같은 패턴이 통합니다.

---

## 8.11 Alembic — 첫 마이그레이션

06·07장에서 다룬 흐름을 그대로 따라갑니다. 여기서는 핵심만 빠르게.

### 8.11.1 초기화

```bash
uv run alembic init alembic
```

`alembic/` 폴더와 `alembic.ini`가 생깁니다.

### 8.11.2 `alembic/env.py` 수정

`alembic/env.py`의 일부를 우리 모델과 비동기 환경에 맞게 바꿉니다(생성된 파일에서 다음 부분만 교체).

```python
# alembic/env.py 의 일부
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from app.config import get_settings
from app.db import Base
import app.models  # noqa: F401  (모델을 import 해야 metadata에 등록됨)


config = context.config
settings = get_settings()

# alembic.ini의 sqlalchemy.url 대신 우리 설정값을 쓰도록 덮어쓴다
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
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


run_migrations_online()
```

### 8.11.3 첫 리비전 자동 생성

```bash
uv run alembic revision --autogenerate -m "create_user"
```

`alembic/versions/` 아래에 새 파일이 하나 생깁니다.

### 8.11.4 적용

```bash
uv run alembic upgrade head
```

`auth.db` 파일이 생기고 `users` 테이블이 만들어집니다. SQL 클라이언트(예: DBeaver)로 열어봐도 좋습니다.

---

## 8.12 직접 호출해보기 — curl로 손에 익히기

서버를 띄웁니다.

```bash
uv run uvicorn app.main:app --reload
```

### 8.12.1 회원가입

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "hunter22hunter"}'
```

응답(201):

```json
{
  "id": 1,
  "email": "alice@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-04-25T10:00:00+00:00"
}
```

### 8.12.2 로그인

`-d` 형식이 form-encoded라는 점에 주의하세요(JSON이 아닙니다).

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=hunter22hunter"
```

응답(200):

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 8.12.3 보호된 라우트 호출

토큰을 변수에 넣고 `/users/me`를 호출합니다.

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=hunter22hunter" | jq -r .access_token)

curl http://127.0.0.1:8000/users/me \
  -H "Authorization: Bearer $TOKEN"
```

응답(200):

```json
{
  "id": 1,
  "email": "alice@example.com",
  "is_active": true,
  "is_admin": false,
  "created_at": "2026-04-25T10:00:00+00:00"
}
```

토큰 없이 부르면 401:

```bash
curl -i http://127.0.0.1:8000/users/me
# HTTP/1.1 401 Unauthorized
# {"detail":"Not authenticated"}
```

### 8.12.4 자동 문서에서 테스트

`http://127.0.0.1:8000/docs`를 열어 봅니다. 우측 상단에 **"Authorize"** 버튼이 보입니다.

1. **Authorize** 클릭 → 작은 폼이 뜸
2. `username`에 이메일, `password`에 비밀번호 입력 → **Authorize**
3. 이제 모든 보호된 라우트가 자물쇠 풀린 표시로 바뀜
4. `GET /users/me` 펼치고 **Try it out → Execute** 클릭 → 200 응답

이 흐름은 `OAuth2PasswordBearer(tokenUrl="/auth/login")` 한 줄 등록만으로 자동으로 동작합니다. 입문자에게는 "마법" 같지만, 실제로는 OpenAPI 명세를 Swagger UI가 읽어 자동 처리하는 것입니다.

### 8.12.5 관리자 만들기

기본 가입자는 `is_admin=False`입니다. 관리자 라우트를 테스트하려면 DB에서 직접 한 줄을 바꿔야 합니다(혹은 별도의 부트스트랩 스크립트). 가장 빠른 방법은 SQLite CLI:

```bash
sqlite3 auth.db "UPDATE users SET is_admin=1 WHERE email='alice@example.com';"
```

다시 로그인해 새 토큰을 받고(`is_admin`은 토큰에 들어 있지 않지만, DB에서 매번 조회하므로 새로 발급할 필요는 없습니다 — 다음 요청부터 즉시 반영) `GET /users/admin/ping`을 호출하면 200이 나옵니다.

---

## 8.13 토큰 만료와 갱신 토큰 — 짧게

이 가이드는 **단일 액세스 토큰**으로 단순하게 끝냅니다. 하지만 실무에서는 **짧은 액세스 + 긴 갱신(refresh)** 조합이 표준이라 핵심만 짚습니다.

- **액세스 토큰(access token)**: 매 요청에 사용. 만료 짧음(예: 15분~1시간). 유출 시 피해 최소.
- **갱신 토큰(refresh token)**: 액세스 토큰이 만료되면 이걸로 새 액세스 토큰을 받음. 만료 김(예: 30일). DB에 보관해 즉시 무효화 가능.

전형적인 흐름:

```
1. 로그인 → access(15분) + refresh(30일) 둘 다 발급
2. access로 보호된 라우트 호출 → 200
3. 15분 후 access가 만료 → 401
4. 클라이언트가 refresh로 /auth/refresh 호출 → 새 access 받음
5. 다시 보호된 라우트 호출 → 200
```

이 가이드의 단순화 버전에서는 **사용자가 1시간마다 다시 로그인**해야 합니다. 종합 예제(10·11장)에서 갱신 토큰 패턴을 도입할지는 선택입니다.

> **즉시 로그아웃 / 토큰 무효화** — JWT의 가장 큰 약점입니다. 한 번 발급된 토큰은 만료될 때까지 유효합니다. 즉시 무효화하려면 (1) DB에 "블랙리스트" 테이블을 두거나, (2) Redis 같은 빠른 저장소에 무효화 토큰 ID를 캐시하는 방식이 있습니다. 둘 다 "JWT의 스테이트리스" 장점을 일부 포기하는 것이라 트레이드오프가 있습니다.

---

## 8.14 CORS — 프론트가 다른 도메인일 때

### 8.14.1 CORS가 왜 등장하는가

브라우저는 보안상 "현재 페이지가 떠 있는 도메인"과 다른 도메인의 API를 마음대로 부르지 못하게 막아둡니다. 이걸 **Same-Origin Policy**라고 합니다. 우리가 백엔드를 `api.example.com`에 띄우고, 프론트엔드는 `app.example.com`에 띄우면 둘은 다른 도메인이라 브라우저가 요청을 막아 버립니다.

> **CORS(Cross-Origin Resource Sharing)란?** Same-Origin Policy의 차단을 풀어주는 약속입니다. 백엔드가 응답에 `Access-Control-Allow-Origin: app.example.com` 같은 헤더를 붙여 "이 도메인에서 오는 요청은 허용한다"고 명시합니다.

### 8.14.2 FastAPI에서 한 줄 등록

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

위 예제에서는 `["*"]`로 모든 도메인을 허용했지만, **운영 환경에서는 반드시 명시적인 도메인 목록**을 주세요. `*`로 두면 어떤 사이트에서든 우리 API를 부를 수 있어 토큰 탈취 시나리오가 생길 수 있습니다.

### 8.14.3 `allow_credentials=True`와 `*`의 조합 주의

CORS 사양 상 **`allow_credentials=True`이면 `allow_origins=["*"]`을 쓸 수 없습니다.** (토큰을 헤더로 보내는 우리 흐름에서는 보통 영향이 없지만, 쿠키 기반 인증을 같이 쓰는 경우엔 명시적인 도메인을 적어야 합니다.) 운영 단계에서는 둘 다 명시적 도메인 목록으로 통일하세요.

---

## 8.15 HTTPS — 운영에서는 반드시

JWT는 헤더로 평문 전송됩니다. HTTP(암호화 없음)로 토큰을 주고받으면, 같은 와이파이의 다른 사람이 패킷 캡처로 토큰을 그대로 가져갈 수 있습니다. **토큰 한 번 탈취되면 만료 시각까지는 그 사람이 곧 나입니다.**

그래서 **운영 환경의 모든 백엔드는 HTTPS**를 써야 합니다. 개발 단계에서는 `http://localhost:8000`로 충분하지만, 인터넷에 노출되는 순간 HTTPS가 필수입니다.

09장 배포 가이드에서 다음 두 가지 방법으로 HTTPS를 다룹니다.

- **리버스 프록시 + Let's Encrypt** (nginx/Caddy + 무료 자동 인증서)
- **PaaS 자동 TLS** (Render, Fly.io 등이 도메인에 자동으로 인증서를 붙임)

운영용 환경 변수에서 추가로 신경 쓸 것:

- 쿠키를 쓴다면 `Secure`, `HttpOnly`, `SameSite=Lax` 또는 `Strict`.
- 헤더에 `Strict-Transport-Security`(HSTS)를 추가해 HTTPS를 강제.

---

## 8.16 흔한 실수와 함정

### 8.16.1 비밀번호를 `==`로 비교하기

평문 비밀번호를 그대로 비교하는 건 당연히 잘못입니다. 그런데 **해시도 `==`로 비교하면 안 되는** 미묘한 함정이 있습니다.

```python
# X 위험 — 타이밍 공격에 노출 가능
def verify(plain, hashed):
    return hash_password(plain) == hashed

# O 안전 — bcrypt가 상수시간 비교를 내부에서 처리
def verify(plain, hashed):
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

(현실적으로 Bcrypt 해시 자체가 매번 솔트가 달라 단순 `==` 비교는 작동하지 않지만, 일반 해시(SHA-256 등)를 쓸 때 같은 함정에 빠지기 쉽습니다. **항상 라이브러리가 제공하는 검증 함수를 쓰세요.**)

### 8.16.2 비밀키를 코드에 박기

```python
# X 절대 금지
SECRET_KEY = "my-real-production-secret-key-abc123"
```

git 히스토리에 한 번 들어가면 영영 거기 남습니다. 노출됐다면 새 키를 만들어 즉시 회전하고, 모든 발급된 토큰을 무효화해야 합니다. 처음부터 환경 변수로 다루는 것이 비교할 수 없이 쉽습니다.

### 8.16.3 응답에 `hashed_password`를 포함시키기

```python
# X 절대 금지
@router.get("/me")
async def me(user = Depends(get_current_user)):
    return user   # ← User 모델 그대로 직렬화하면 hashed_password가 노출될 수 있음
```

이 가이드는 **Pydantic의 `UserRead` 응답 모델**을 통해서만 직렬화합니다. `UserRead`에는 `hashed_password`가 없으므로 자동으로 차단됩니다.

### 8.16.4 만료 시간을 안 넣기

`exp` 클레임이 없는 토큰은 영원히 유효합니다. 한 번 만들면 회수가 사실상 불가능합니다. **`exp`는 절대 빠뜨리지 마세요.**

### 8.16.5 `algorithms`에 알고리즘을 안 명시하거나 너무 많이 적기

`jwt.decode(token, SECRET, algorithms=[])`처럼 비워두거나, 허용 목록에 `"none"`(서명 없음)이 들어가면 위조 토큰이 통과될 수 있습니다. **HS256만 쓴다면 `algorithms=["HS256"]`** 만 적습니다.

### 8.16.6 `username`과 `email`을 헷갈리기

`OAuth2PasswordRequestForm`은 필드 이름이 `username`으로 고정입니다. 이 가이드에서는 그 자리에 이메일을 받습니다. 라우트 안에서 `form.username`으로 받아 처리한다는 점을 잊지 마세요.

### 8.16.7 한국어 비밀번호의 길이 함정

24글자짜리 한국어 비밀번호와 25글자짜리가 Bcrypt에서 같게 취급될 수 있습니다(72바이트 제한). 8.4.5에서 다룬 길이 검증을 반드시 적용하세요.

### 8.16.8 시간대 안 맞춤

`datetime.now()` (naive) 대신 항상 `datetime.now(timezone.utc)`. 토큰의 `exp`/`iat`는 UTC 기준이어야 모든 환경에서 일관됩니다.

### 8.16.9 `.env`를 git에 커밋

`.gitignore`에 `.env`가 반드시 들어 있어야 합니다. 처음 푸시하기 전에 `git status`로 한 번 확인하는 습관을 들이세요.

### 8.16.10 로그에 평문 비밀번호 흘리기

`print(payload)` 같은 줄을 무심코 남기면 사용자의 평문 비밀번호가 로그 파일에 남습니다. 회원가입·로그인 라우트에서 입력 객체를 절대 통째로 로깅하지 마세요. 필요하면 비번을 마스킹한 별도 로깅 함수를 만듭니다.

---

## 8.17 트러블슈팅 — 자주 헷갈리는 포인트

### 8.17.1 401이 계속 뜨는데 토큰은 맞아 보인다

- 헤더 형식 확인: `Authorization: Bearer <토큰>` (Bearer 뒤에 띄어쓰기 한 번, 그 뒤 토큰)
- 토큰을 [jwt.io](https://jwt.io/)에 붙여넣어 Payload를 확인. `exp`가 지났는지, `sub`가 정수 변환 가능한지.
- 비밀키 확인: 발급한 서버와 검증하는 서버의 `SECRET_KEY`가 같아야 함. 환경 변수 오타 흔함.

### 8.17.2 `ImportError: cannot import name 'BaseSettings' from 'pydantic'`

Pydantic 2.x부터 `BaseSettings`는 별도 패키지로 분리되었습니다.

```bash
uv add pydantic-settings
```

`from pydantic_settings import BaseSettings`로 임포트.

### 8.17.3 `ValueError: password cannot be longer than 72 bytes`

`bcrypt` 라이브러리 4.x부터 72바이트 초과 시 자동으로 에러를 냅니다. 이 가이드의 `hash_password`는 사전에 검사하지만, 다른 코드 경로에서 직접 호출했다면 같은 함정입니다. 사용자 입력은 항상 길이 검증 후 해싱.

### 8.17.4 `jwt.exceptions.PyJWTError`로 시작하는 예외

PyJWT 2.x의 모든 에러는 `jwt.exceptions.PyJWTError`의 자식입니다. `InvalidTokenError`도 그 하위입니다. 좁게 잡고 싶으면 `ExpiredSignatureError`, `InvalidSignatureError` 등을 개별로 잡으세요.

### 8.17.5 Swagger의 Authorize 후에도 401

- `tokenUrl`이 실제 로그인 엔드포인트와 일치하는지 확인 (`OAuth2PasswordBearer(tokenUrl="/auth/login")`).
- 로그인 응답이 `{"access_token": ..., "token_type": "bearer"}` 형식인지 확인 (필드 이름 정확).
- 보호된 엔드포인트가 실제로 `Depends(get_current_user)`를 받고 있는지 확인.

### 8.17.6 비동기 SQLite의 동시성 문제

SQLite는 파일 한 개에 쓰기 락이 걸려 동시성이 약합니다. 가벼운 학습용 / 단일 서버 데모에는 충분하지만, 실제 운영에서는 PostgreSQL을 권장합니다(09장 배포 참조).

### 8.17.7 테스트에서 DB가 공유돼서 케이스가 서로 영향을 줌

`tests/conftest.py`에서 매 테스트마다 임시 DB(예: 인메모리 SQLite)를 다시 만들어야 합니다. 이 가이드의 `conftest.py`(8.18)가 그 패턴을 보여줍니다.

---

## 8.18 테스트 — 흐름을 자동으로 검증

`tests/conftest.py`에서 매 테스트마다 새로운 인메모리 SQLite를 띄우고, FastAPI 앱의 `get_session` 의존성을 그것으로 덮어씁니다.

```python
# tests/conftest.py — 핵심 골자
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db import Base, get_session
from app.main import app


@pytest_asyncio.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    # 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async def override_get_session():
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()
```

테스트 케이스는 다음과 같이 합니다(예시 한 개).

```python
# tests/test_auth.py — 한 케이스 예
async def test_signup_login_me(client):
    # 회원가입
    r = await client.post("/auth/signup", json={
        "email": "alice@example.com",
        "password": "hunter22hunter",
    })
    assert r.status_code == 201

    # 로그인
    r = await client.post("/auth/login", data={
        "username": "alice@example.com",
        "password": "hunter22hunter",
    })
    assert r.status_code == 200
    token = r.json()["access_token"]

    # 보호된 라우트
    r = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["email"] == "alice@example.com"
```

전체 테스트 파일은 예제 폴더의 `tests/test_auth.py`에 있습니다(회원가입 성공, 중복 가입 409, 잘못된 비번 401, 토큰 없이 401, 만료 토큰 401, 변조 토큰 401, 비밀번호 길이 초과 422, 인가 403 등 여러 케이스).

```bash
uv run pytest -v
```

---

## 8.19 다음 단계로 가기 전에 — 체크리스트

- [ ] `uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite pyjwt bcrypt pydantic-settings "pydantic[email]" python-multipart` 가 모두 끝났다
- [ ] `app/security.py`의 네 함수(`hash_password`, `verify_password`, `create_access_token`, `decode_access_token`)가 작성되었다
- [ ] `OAuth2PasswordBearer(tokenUrl="/auth/login")`이 `app/deps.py`에 한 번만 등록되어 있다
- [ ] `get_current_user`와 `get_current_admin`이 작성되어 401과 403을 정확히 구분한다
- [ ] `/auth/signup`, `/auth/login`, `/users/me`, `/users/admin/ping` 네 라우트가 모두 동작한다
- [ ] 자동 문서(`/docs`)의 **Authorize** 버튼으로 로그인 후 보호된 라우트를 호출할 수 있다
- [ ] `.env.example`은 커밋되고, `.env`는 `.gitignore`에 들어 있다
- [ ] `SECRET_KEY`가 코드에 하드코딩되어 있지 않고 환경 변수에서 읽힌다
- [ ] `tests/test_auth.py`가 통과한다(`uv run pytest -v`)

위가 다 통과하면 다음 챕터로 넘어갈 준비가 끝난 것입니다.

---

## 8.20 이 챕터 요약

- **인증(AuthN)**은 "누구냐"를 확인하고, **인가(AuthZ)**는 "이걸 해도 되느냐"를 확인한다. 실패 시 코드는 각각 401, 403.
- 비밀번호는 절대 평문으로 저장하지 않는다. **Bcrypt**는 일부러 느린 비밀번호 전용 해시이며, 솔트를 자동으로 처리한다.
- `bcrypt` 라이브러리는 입력·출력이 모두 **bytes**다. DB 저장 시 `.decode("utf-8")`. **72바이트 제한**을 길이 검증으로 다룬다.
- **JWT**는 Header.Payload.Signature 세 부분이며, Payload는 암호화되지 않으므로 비밀 정보를 넣지 않는다. `sub`, `exp`, `iat` 정도가 표준.
- 이 가이드는 단일 서버이므로 **HS256(대칭 키)** 만 쓰고, `SECRET_KEY`는 환경 변수에서 읽는다.
- **PyJWT**의 `jwt.encode` / `jwt.decode` 두 함수가 핵심. `algorithms=["HS256"]` 같은 리스트 명시를 빠뜨리지 않는다.
- FastAPI의 **`OAuth2PasswordBearer`**는 "Bearer 헤더에서 토큰 꺼내기" 도구일 뿐, 진짜 OAuth2 흐름은 아니다. **`OAuth2PasswordRequestForm`**은 표준 form 필드(`username`, `password`)를 받는다.
- `Depends(get_current_user)` 한 줄로 보호된 라우트가 만들어지고, `get_current_admin`처럼 의존성 위에 의존성을 합성하면 인가가 된다.
- 운영에서는 **HTTPS 필수**, `SECRET_KEY` 절대 코드에 박지 말 것, `.env`는 git에 커밋 금지.
- 흔한 실수: 비번 직접 비교, 응답에 `hashed_password` 노출, `algorithms` 누락, `exp` 누락, 한국어 비번 길이 함정.
- 갱신 토큰(refresh token)은 짧게 언급만. 이 가이드는 단일 액세스 토큰으로 단순화.

<a id="ch09"></a>

# 09. 배포 가이드 — Docker, Render/Fly.io, AWS, Ubuntu

> **이 챕터의 목표**
> - 개발 서버(`uvicorn --reload`)와 운영 서버의 차이를 이해하고, 왜 운영에서는 **Gunicorn + UvicornWorker** 를 쓰는지를 한 줄로 설명할 수 있다.
> - **Docker** 로 우리 FastAPI 앱을 컨테이너로 만들고, **`docker-compose`** 로 앱 + PostgreSQL 을 한 번에 띄울 수 있다.
> - **Render** 또는 **Fly.io** 같은 관리형 플랫폼에 GitHub 저장소 한 번 연결로 배포할 수 있다.
> - **AWS EC2(t3.small)** 에 Docker 만 깔아 가장 단순하게 띄울 수 있다.
> - **Ubuntu 서버**에 systemd + nginx + Let's Encrypt 조합으로 직접 띄울 수 있다.
> - 어느 경로를 택하든 "환경 변수, 마이그레이션, 헬스 체크, HTTPS, 로그" 다섯 가지를 빠뜨리지 않는다.

> **소요 시간**: 4~8시간 (선택하는 경로에 따라 다름. Docker 절은 누구나 본다.)

> **전제**: 03~08장을 한 번씩 따라했다. 가상환경(`uv sync`), 비동기 SQLAlchemy, Alembic 마이그레이션, JWT 인증의 흐름을 한 번씩 만나봤다. 이 챕터는 07장의 Todo API 또는 그와 비슷한 구조의 앱(`app/main.py` 안에 `app: FastAPI`, `app/db.py`, `alembic/` 폴더)이 있다고 가정한다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

---

## 9.1 운영 배포의 큰 그림

### 9.1.1 "내 컴퓨터에서는 되는데" 를 끝내는 것이 배포다

여기까지의 챕터에서 우리는 항상 한 가지 명령으로 서버를 띄웠다.

```bash
uv run uvicorn app.main:app --reload
```

이 명령이 잘 돌아간다면, **이미 절반은 한 셈이다.** 배포는 결국 "이 한 줄을 다른 컴퓨터에서, 코드 수정 없이, 안정적으로 24시간 돌리는 일"이다. 다만 다음 일곱 가지가 달라진다.

| 항목 | 개발(내 컴퓨터) | 운영(서버) |
|------|------|------|
| 서버 | `uvicorn --reload` 한 프로세스 | `gunicorn` 이 여러 `uvicorn` 워커를 띄움 |
| 코드 자동 재로드 | 켬 (`--reload`) | **끔** (재시작은 배포 파이프라인의 일) |
| DB | SQLite 파일 또는 로컬 Postgres | 외부 관리형 Postgres (RDS, Render Postgres 등) |
| 비밀값 | `.env` 파일 | 플랫폼의 환경 변수 UI / 시크릿 매니저 |
| 마이그레이션 | `alembic upgrade head` 를 손으로 가끔 | **배포 단계에서 자동 또는 1단계 명시 실행** |
| 로그 | 터미널에 그냥 흐름 | 표준출력 → 플랫폼이 수집/저장 |
| 외부 노출 | `127.0.0.1:8000` 만 | `0.0.0.0` + 도메인 + HTTPS |

이 표를 한 장 안에 옮겨 적은 것이 이 챕터의 본문이다.

> **배포(deployment)란?** 개발한 앱을 사용자가 실제로 쓰는 환경(서버)에 올려 동작하게 만드는 모든 과정. 코드 푸시 → 빌드 → 환경 변수 주입 → DB 마이그레이션 → 서비스 시작 → HTTPS 연결까지가 한 묶음이다.

### 9.1.2 왜 `uvicorn --reload` 만으로는 부족한가

개발용 명령 `uvicorn app.main:app --reload` 는 다음과 같은 단점을 가진다.

1. **단 하나의 프로세스만 띄운다.** Python 의 GIL 때문에 한 프로세스 안에서는 CPU 작업이 동시에 진행되지 못한다. 코어가 4개 있어도 1개만 쓴다.
2. **프로세스가 죽으면 그걸로 끝.** 어떤 이유로든 `uvicorn` 이 종료되면 서비스가 멈춘다.
3. **`--reload` 가 켜져 있다.** 파일을 감시하느라 CPU·메모리를 더 쓰고, 운영에서는 위험한 동작이다(코드가 외부 디스크에서 갱신되면 그 순간 재시작이 일어나기 때문).
4. **요청 처리 통계·죽은 워커 재시작·헬스 체크** 같은 운영 기능이 없다.

이 모든 단점을 한 번에 해결하는 표준 조합이 **Gunicorn + UvicornWorker** 다.

> **Gunicorn 이란?** "Green Unicorn" 의 약자. 파이썬 웹 앱을 운영 환경에서 띄우는 **프로세스 매니저**다. 워커 프로세스를 N 개 띄워 부하를 분산하고, 죽은 워커를 자동으로 재시작하며, 표준 출력에 정형화된 로그를 찍어 준다. 옛날에는 Gunicorn 이 WSGI(동기) 서버였지만, **워커 클래스만 ASGI 용으로 바꿔주면**(`-k uvicorn.workers.UvicornWorker`) 비동기 FastAPI 앱도 그대로 운영할 수 있다.

> **UvicornWorker 란?** Uvicorn 이 제공하는, "Gunicorn 이 띄우는 워커 프로세스 안에서 ASGI 앱을 실행해 주는" 클래스. Gunicorn 의 운영 기능(워커 관리·로그·신호 처리)과 Uvicorn 의 비동기 처리(asyncio + httptools) 를 동시에 얻을 수 있다.

### 9.1.3 운영 명령 한 줄 — 이 가이드의 표준

이 챕터에서 어디든 동일하게 쓰는 운영 실행 명령은 다음과 같다. **이 한 줄을 외워 두면 모든 배포 경로에서 다시 마주친다.**

```bash
gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -b 0.0.0.0:8000 \
    --workers 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
```

각 옵션의 의미를 한 번 풀어 적는다.

| 옵션 | 의미 |
|------|------|
| `app.main:app` | "`app/main.py` 파일 안의 `app` 객체를 띄워라" — uvicorn 명령과 같은 표기 |
| `-k uvicorn.workers.UvicornWorker` | 워커 클래스로 UvicornWorker 사용 — ASGI(비동기) 앱을 굴리겠다는 선언 |
| `-b 0.0.0.0:8000` | 외부 모든 IP 의 8000 포트로 들어오는 요청을 받음. (`127.0.0.1` 로 두면 같은 컴퓨터 안에서만 접근 가능) |
| `--workers 4` | 워커 프로세스 수. 보통 `(코어 수 × 2) + 1` 이 시작점이지만, 비동기 앱은 더 적게 둬도 충분하다 (다음 절 참고) |
| `--timeout 60` | 워커가 60초 안에 응답하지 못하면 죽이고 재시작. 무한 대기 방지 |
| `--access-logfile -`, `--error-logfile -` | 로그를 표준출력/표준에러로. 컨테이너 환경의 정석 |

### 9.1.4 워커 수는 어떻게 정하나

가장 흔한 가이드 두 가지를 둘 다 적어 둔다.

- **공식적인 시작점**: `워커 수 = (CPU 코어 수 × 2) + 1`. 동기 워커(WSGI) 시절의 가이드라인으로, Gunicorn 공식 문서가 지금도 권장한다.
- **FastAPI(비동기) 의 현실**: 이미 한 워커 안에서 수천 건의 요청을 동시에 처리할 수 있으므로, **`코어 수` 또는 `코어 수 × 2`** 로 시작해도 충분한 경우가 많다.

작은 서버(예: 1 코어, 1GB RAM)에서는 **2~4 워커**가 보통이다. 큰 서버(예: 4 코어, 8GB RAM)에서는 **4~8 워커**. **메모리가 부족해 워커가 OOM 으로 죽는다면, 워커 수를 줄이는 것이 정답**이다 — 워커가 많을수록 같은 모델/엔진/캐시가 N 배 만큼 메모리에 올라가기 때문.

> **시작 권장값**: 학습용 작은 서버라면 `--workers 2` 로 시작해 측정 후 늘려라. "2 → 4 → 8" 순으로 부하 테스트하면서 응답 시간 / 메모리를 보면 자기 서비스의 적정값이 보인다.

### 9.1.5 환경 변수 분리의 의미

운영에서 가장 자주 사고 나는 부분이다.

- **개발**: 비밀값(DB 비번, JWT 시크릿)을 `.env` 파일에 적어 두고 `pydantic-settings` 가 자동으로 읽는다.
- **운영**: **`.env` 파일을 서버에 올리지 않는다.** 대신 **운영체제 환경 변수**(또는 플랫폼의 시크릿 매니저)에 같은 이름의 값을 주입한다.

`pydantic-settings` 의 `BaseSettings` 는 이 둘을 똑같이 읽는다. 즉, 코드 한 줄도 안 고쳐도 `.env` 와 환경 변수 사이를 자유롭게 오갈 수 있다.

```python
# app/config.py — 07장과 동일
class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    cors_allow_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
```

이 `Settings` 객체는 다음 두 환경에서 모두 동작한다.

- 로컬: `.env` 파일에 `DATABASE_URL=...` 이 있으면 그걸 읽음.
- 서버: OS 환경 변수에 `DATABASE_URL=...` 이 있으면 그걸 읽음. (`.env` 가 없어도 됨)

> **`.env` 는 절대 git 에 올리지 않는다.** `.gitignore` 에 등록하고, 협업용으로는 **변수 이름과 의미만 적은 `.env.example`** 을 git 에 둔다. 이 가이드의 모든 예제 프로젝트가 이 약속을 따른다.

### 9.1.6 이 챕터에서 다룰 다섯 가지 배포 경로

| 경로 | 누가 쓰나 | 난이도 | 비용 |
|------|-----------|--------|------|
| **Render** | 1인 개발, 빠른 데모 | ★ | 무료(슬립) ~ 월 $7 |
| **Fly.io** | 1인~소규모 팀, 글로벌 배포 | ★★ | 무료 한도 + 사용량 과금 |
| **AWS EC2(t3.small) + Docker** | AWS 인프라 학습 | ★★★ | 월 $20 내외 |
| **Ubuntu 서버에 직접** | 시스템 운영을 손에 익히고 싶을 때 | ★★★★ | VPS 월 $5~10 |
| **Docker / Compose 만 로컬에서** | 위 모든 경로의 공통 기반 | ★★ | 무료 |

**Heroku 는 다루지 않는다.** 무료 요금제가 2022년 11월 28일 폐지된 이후 입문자 기준의 매력이 줄었고, Render·Fly.io 가 같은 사용 경험을 제공한다.

이 챕터는 **Docker → Render → Fly.io → AWS EC2 → Ubuntu 직접 배포** 순으로 다룬다. **Docker 는 공통 기반**이니 가장 먼저 본다. 그 다음은 어느 절에서 시작해도 자기완결적으로 따라갈 수 있도록 적었다.

---

## 9.2 배포 전 공통 체크리스트

어떤 경로든 시작 전에 다음을 확인하면 사고가 절반 이상 줄어든다. 본문에서 다시 자세히 다루지만, 첫 한 번은 위에서 한 번 훑어 두자.

- [ ] **환경 변수**: `DATABASE_URL`, `JWT_SECRET`, `CORS_ALLOW_ORIGINS` 등이 코드/저장소에 박혀 있지 않다. `.env.example` 에 변수 이름과 의미만 적혀 있다.
- [ ] **`.env` 가 `.gitignore` 에 들어 있다.**
- [ ] **마이그레이션**: `app/main.py` 안에서 부팅 시 자동으로 `Base.metadata.create_all(...)` 같은 코드를 부르지 **않는다**(개발 편의용 코드를 운영에 남겨두면 위험하다). Alembic 으로 명시적으로 마이그레이션한다.
- [ ] **`/health` 엔드포인트**가 존재한다.
- [ ] **로그 레벨**: 운영은 `INFO` 또는 `WARNING`. 개발의 `DEBUG` 그대로 가지 않는다.
- [ ] **포트 바인딩**: `0.0.0.0` 으로 바인딩한다 (`127.0.0.1` 은 외부 접근 불가).
- [ ] **테스트 통과**: `uv run pytest` 가 깔끔하다.
- [ ] **HTTPS 계획**: 어떤 경로로 TLS 를 받을지 미리 정한다 (플랫폼 자동 / nginx + Let's Encrypt / ALB + ACM 등).
- [ ] **CORS 화이트리스트**: 운영에선 `*` 대신 실제 프론트 도메인 목록을 적는다.

> **헬스 체크(health check)란?** "서버가 살아 있나요?" 를 묻는 작은 엔드포인트. 보통 `GET /health` 를 두고 200 만 돌려준다. 로드 밸런서·플랫폼·모니터링 툴이 주기적으로 호출해 죽은 인스턴스를 자동으로 빼낸다. 이 가이드의 표준은 다음 한 줄이다.

```python
# app/main.py 어딘가
@app.get("/health")
def health():
    return {"status": "ok"}
```

DB 까지 살아 있는지 확인하려면 작은 SELECT 한 번을 더 해도 된다. 다만 헬스 체크는 **싸고 빠른 게 미덕**이라, 보통은 위처럼 단순하게 둔다.

---

## 9.3 Docker 기초 — 모든 배포의 공통 토대

배포 경로를 어디로 가든 Docker 한 번을 먼저 정리하면 그 뒤가 모두 쉬워진다. **Render·Fly.io·AWS·Ubuntu 모두 우리의 Dockerfile 을 그대로 쓰기** 때문이다.

### 9.3.1 컨테이너·이미지·레이어 — 한 단락 정리

세 단어를 빠르게 풀어 본다.

> **컨테이너(container)란?** 앱과 그 앱이 의존하는 OS 환경(파이썬, 라이브러리, 시스템 패키지) 까지를 한 묶음으로 잘라낸 격리된 실행 단위다. 호스트 OS 의 커널은 공유하지만, 파일 시스템·프로세스 공간은 따로 갖는다. "내 노트북, 동료 노트북, 운영 서버에서 똑같이 돌아간다" 가 컨테이너의 약속이다.

> **이미지(image)란?** 컨테이너의 "설계도"다. 정적인 파일 묶음이며, 실행되면 컨테이너가 된다. 한 이미지에서 여러 컨테이너를 동시에 띄울 수 있다.

> **레이어(layer)란?** 이미지는 여러 층(layer) 으로 쌓여 만들어진다. `FROM python:3.13-slim` 이 한 층, `RUN apt-get install ...` 이 그 위 층, `COPY . .` 이 또 그 위 층. **위 층이 바뀌어도 아래 층이 같으면 캐시를 그대로 재사용**한다. 이 캐시 동작을 잘 활용하는 것이 빠른 빌드의 비결이다.

> **레지스트리(registry)란?** 이미지를 보관·배포하는 저장소. Docker Hub(공개), GitHub Container Registry(GHCR), AWS ECR 등이 있다.

### 9.3.2 Docker Desktop 설치 (개발용)

배포 대상 서버에는 Docker 만 있으면 되지만, **로컬 개발 시에 빌드와 테스트를 같이 하려면 Docker Desktop** 이 가장 편하다.

- **macOS / Windows**: [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop) 에서 다운로드. 설치 후 자동 실행.
- **Ubuntu**: Docker Desktop 도 있지만, 보통은 엔진(`docker-ce`) 만 깐다. 9.7 절(Ubuntu 직접 배포) 에서 다시 다룬다.

설치 확인.

```bash
docker --version
docker compose version
```

각각 버전이 출력되면 OK.

### 9.3.3 자주 쓰는 Docker 명령어 한눈에

본격 빌드에 들어가기 전에 자주 만나는 명령을 정리한다. 천천히 외우면 된다.

```bash
# 이미지 빌드
docker build -t myapp:1.0 .

# 이미지 목록
docker images

# 컨테이너 실행 (-p 호스트포트:컨테이너포트)
docker run -p 8000:8000 myapp:1.0

# 백그라운드(-d), 이름 지정(--name)
docker run -d --name myapp -p 8000:8000 myapp:1.0

# 환경 변수 주입
docker run -e DATABASE_URL="postgresql+asyncpg://..." myapp:1.0

# 실행 중 컨테이너 목록
docker ps

# 로그 확인 (-f: 실시간 추적)
docker logs -f myapp

# 컨테이너 안의 셸 들어가기
docker exec -it myapp bash

# 정지 / 제거
docker stop myapp
docker rm myapp

# 이미지 제거
docker rmi myapp:1.0

# Compose
docker compose up -d
docker compose down
docker compose logs -f
docker compose run --rm migrate alembic upgrade head
```

> **`-it` 는 뭔가요?** `-i`(interactive: 표준입력 유지) + `-t`(TTY 할당). 셸을 직접 두드릴 때 쓴다. 명령 한 번을 자동으로 돌리는 경우엔 빼도 된다.

### 9.3.4 이 가이드의 표준 `Dockerfile` (멀티스테이지)

이 챕터의 핵심 자산이다. 처음부터 끝까지 천천히 읽는다. 여러분 프로젝트의 루트(예: `07-TodoAPI/`) 에 `Dockerfile` 이라는 이름으로 둔다.

```dockerfile
# syntax=docker/dockerfile:1.7

# ============================================================
# 1단계: 빌드 단계 — uv 로 의존성을 풀어 가상환경(.venv)을 만든다
# ============================================================
FROM python:3.13-slim AS builder

# uv 본체만 빌더 단계에 가져온다 (가벼움, 한 줄)
COPY --from=ghcr.io/astral-sh/uv:0.5.7 /uv /uvx /bin/

# 빌드/링크 시 byte-compile 활성화 → 첫 요청이 빨라짐
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/app/.venv

WORKDIR /app

# 의존성 정의 파일만 먼저 복사 → 라이브러리 캐시 분리
# (소스 코드가 바뀌어도 의존성이 그대로면 이 단계 캐시가 재사용됨)
COPY pyproject.toml uv.lock ./

# 의존성만 먼저 설치 (개발 의존성 제외, lock 파일을 그대로 사용)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

# 이제 진짜 소스 코드 복사
COPY . .

# 프로젝트 자체도 .venv 에 설치
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ============================================================
# 2단계: 런타임 단계 — 빌더에서 만든 .venv 만 들고 와서 실행
# ============================================================
FROM python:3.13-slim AS runtime

# 운영 단계에 필요한 최소 시스템 패키지만 설치
# - libpq5: asyncpg 가 동적으로 호출하는 PostgreSQL 클라이언트 라이브러리
# - ca-certificates: HTTPS 외부 호출 시 인증서 검증
# - tini: PID 1 을 안전하게 처리해주는 작은 init
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        ca-certificates \
        tini \
    && rm -rf /var/lib/apt/lists/*

# 비루트 유저 생성 (보안의 기본)
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app

WORKDIR /app

# 빌더에서 만든 가상환경과 소스만 복사
COPY --from=builder --chown=app:app /app /app

# .venv 의 실행 파일을 PATH 앞쪽에 끼워 넣음 → `uvicorn`, `alembic`, `gunicorn` 이 그냥 통한다
ENV PATH="/app/.venv/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

USER app

EXPOSE 8000

# tini 가 PID 1 을 받고, 그 아래에서 gunicorn 이 동작한다
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--workers", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

내용이 길어 보이지만, 본질은 **두 단계뿐**이다.

1. **빌더**: `pyproject.toml` + `uv.lock` 만 먼저 복사 → `uv sync --frozen --no-dev` 로 의존성 설치 → 소스 복사 → 프로젝트 설치.
2. **런타임**: 빌더에서 만든 `/app` 폴더(가상환경 포함) 를 통째로 가져와 `gunicorn` 실행.

각 줄에 적은 주석을 그대로 따라 읽으면 충분하다. 핵심 포인트만 다섯 가지 다시 짚자.

#### 1) `python:3.13-slim` 을 베이스로

- `python:3.13` 풀 이미지: Debian + 빌드 도구까지 포함 (~1GB). 너무 무겁다.
- `python:3.13-slim` 이미지: Debian slim + Python 만 (~120MB). **이 가이드의 기본**.
- `python:3.13-alpine` 이미지: Alpine Linux 기반 (~60MB). 가벼우나 일부 라이브러리(asyncpg, bcrypt 등 C 확장) 빌드가 까다롭다. 입문자에겐 비권장.

> **베이스 이미지의 버전을 못 박는 이유**: `python:3.13` 만 쓰면 새 마이너 버전이 나올 때 조용히 바뀐다. 이 가이드는 학습용이니 `python:3.13-slim` 정도면 충분하지만, **운영에서는 `python:3.13.1-slim-bookworm`** 처럼 더 정확히 못 박는 편이 좋다.

#### 2) `uv` 를 한 줄로 가져온다

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.5.7 /uv /uvx /bin/
```

`uv` 의 공식 이미지에서 실행 파일만 잘라내 우리 빌더에 옮긴다. `pip install uv` 같은 단계가 필요 없다 — 이게 가장 빠르고 깔끔한 패턴이다.

> **버전 고정**: `:0.5.7` 처럼 정확히 못 박아라. `:latest` 로 두면 빌드가 어느 날 갑자기 깨질 수 있다.

#### 3) 의존성 설치를 캐시 가능하게 분리

```dockerfile
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev
```

이 네 단계 순서가 **빠른 재빌드의 핵심**이다.

- 소스 코드만 한 줄 고친 경우: `pyproject.toml`/`uv.lock` 은 그대로 → `uv sync --no-install-project` 단계는 캐시 히트. 의존성 다운로드 0초.
- 라이브러리를 추가한 경우: `pyproject.toml`/`uv.lock` 이 바뀜 → 그 줄부터 다시 시작. 그래도 다음 빌드부터는 또 캐시.

`--mount=type=cache,target=/root/.cache/uv` 는 **BuildKit 의 캐시 마운트** 기능이다. 빌드 사이에 uv 의 다운로드 캐시를 보존해, 같은 라이브러리를 두 번 받지 않게 해 준다.

> **`--frozen` 의 의미**: "lock 파일을 절대 갱신하지 말고 정확히 그 버전들만 깔아라". 운영 빌드에서는 항상 `--frozen` 을 쓴다. lock 파일이 빌드마다 바뀌면 재현 가능성이 깨진다.

> **`--no-dev` 의 의미**: pytest/ruff 같은 개발 의존성을 빼고 깐다. 이미지 크기가 줄고 운영에서 안 쓸 코드가 안 들어간다.

> **`--no-install-project` 의 의미**: "라이브러리만 깔고, 우리 프로젝트 자체(`app/`) 는 아직 설치하지 마". 소스가 아직 복사되지 않은 상태이므로 이 단계가 따로 필요하다.

#### 4) 비루트 유저(`app`) 로 실행

- 컨테이너가 root 로 동작하면 호스트의 보안 위험이 커진다(드물지만 컨테이너 탈출 공격이 있을 때 root 권한이 그대로 위험).
- 운영의 표준 패턴은 **비루트 유저를 만들어 그 권한으로 앱을 실행**하는 것.

```dockerfile
RUN groupadd --system app && useradd --system --gid app --create-home --home-dir /home/app app
USER app
```

#### 5) `tini` 로 PID 1 을 안전하게

PID 1 프로세스는 좀비 자식 프로세스를 거두고, 신호(SIGTERM 등) 를 잘 다뤄야 하는 책임이 있다. Python/Gunicorn 이 이 역할을 직접 해도 잘 동작하는 경우가 많지만, 가끔 좀비 프로세스가 남는 등의 미묘한 문제가 생긴다. **`tini` 라는 작은 init 을 한 줄 끼워 두면** 이 문제가 깔끔히 사라진다.

```dockerfile
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["gunicorn", "app.main:app", ...]
```

> **tini 가 꼭 필요한가?** 학습 단계에서는 없어도 거의 문제가 안 보인다. 다만 한 줄 추가로 미래의 잠재 문제를 미리 막아두는 것이라 이 가이드의 표준에 포함했다. 의존성도 가볍다(수십 KB).

### 9.3.5 `.dockerignore` — 비밀 유출을 막는 한 파일

`Dockerfile` 옆에 **반드시** 다음 파일을 둔다.

```
# .dockerignore

# 가상환경
.venv/
__pycache__/
*.py[cod]
*.so

# 환경 변수와 비밀
.env
.env.*

# 테스트·린트 캐시
.pytest_cache/
.ruff_cache/
.mypy_cache/
.coverage
htmlcov/

# git / IDE 메타
.git/
.github/
.gitignore
.vscode/
.idea/
.DS_Store

# 로그·임시
*.log
*.pid
*.tmp

# 로컬 DB 파일
*.db
*.sqlite
*.sqlite3

# 문서 / 빌드 산출물
docs/
build/
dist/
*.egg-info/
```

`.dockerignore` 의 효과는 두 가지.

1. **빌드 컨텍스트가 작아져서 빌드가 빨라진다.** Docker 는 `docker build .` 시 현재 폴더 전체를 데몬에 보낸다. `.venv/` 가 안 빠지면 수백 MB 가 매번 전송된다.
2. **비밀이 이미지에 딸려 들어가지 않는다.** `.env` 파일이 그대로 이미지에 구워지면, 그 이미지를 레지스트리에 푸시하는 순간 누구나 비밀번호를 본다. **이 한 항목이 가장 중요하다.**

> **`.gitignore` 와 같은 내용 아닌가?** 비슷하지만 같지 않다. `.gitignore` 가 git 에만 적용되듯, `.dockerignore` 는 Docker 빌드에만 적용된다. 둘 다 따로 만들어 둔다. 보통은 `.gitignore` 의 내용을 거의 다 옮긴 뒤 도커 특화 항목(예: `.git/` 자체를 빼는 등) 만 추가한다.

### 9.3.6 빌드 / 실행 — 로컬에서 한 번 띄워보기

`07-TodoAPI/` (또는 비슷한 구조의 앱 폴더) 안에서 다음을 차례로 친다.

```bash
# 1. 이미지 빌드
docker build -t todo-api:dev .

# 2. 컨테이너 실행 (테스트용 SQLite 모드)
#    환경 변수는 -e 로 직접 주입
docker run --rm -p 8000:8000 \
    -e DATABASE_URL="sqlite+aiosqlite:///./todo.db" \
    -e CORS_ALLOW_ORIGINS="*" \
    todo-api:dev

# 3. 다른 터미널에서 헬스 체크
curl http://localhost:8000/health
# {"status":"ok"}

# 4. 자동 문서
open http://localhost:8000/docs   # macOS
xdg-open http://localhost:8000/docs # Linux
```

이 흐름이 통과하면, **여러분의 앱은 어디든 배포될 수 있다.** Docker 가 표준이고, 다음 절부터의 모든 플랫폼은 이 이미지를 그대로 쓴다.

> **포트 충돌 시**: 8000 이 이미 쓰이고 있다면 `-p 18000:8000` 같이 호스트 쪽 포트만 바꿔서 띄우자. 컨테이너 내부의 8000 은 그대로 둬야 `Dockerfile` 의 `CMD` 가 바뀌지 않는다.

### 9.3.7 첫 빌드 결과 점검 — 이미지 크기 줄이는 작은 팁

빌드가 끝나고 `docker images` 를 쳐 보면 대략 다음 같은 크기가 나온다(소수의 추가 라이브러리 제외).

```
todo-api    dev    abcd1234    2 minutes ago    220MB
```

200~300MB 면 합격이다. 1GB 가 넘는다면 다음을 의심한다.

- 베이스 이미지를 `python:3.13`(slim 아님) 으로 잡았다.
- `.dockerignore` 가 없거나 부실해서 `.venv/` / `node_modules/` / 데이터 파일이 통째로 들어갔다.
- 멀티스테이지가 아니어서 빌드 도구가 최종 이미지에 남아 있다.

각각 위 9.3.4 ~ 9.3.5 절을 다시 보면 된다.

---

## 9.4 `docker-compose.yml` — 앱 + PostgreSQL 한 번에

로컬 개발에서 **앱과 DB 를 한 번에 띄우는 가장 표준적인 방법**이 Docker Compose 다. 7장의 Todo API 가 SQLite 였다면, 이번에는 같은 코드를 **운영급에 가까운 PostgreSQL** 위에서 돌려본다.

> **Docker Compose 란?** 여러 컨테이너(앱 + DB + Redis 등) 의 관계와 환경을 한 YAML 파일에 적어두면 `docker compose up` 한 줄로 한 번에 띄우게 해 주는 도구. 운영에서 단일 서버에 같이 돌리는 용도와, 개발에서 외부 서비스를 흉내 내는 용도 모두 자주 쓴다.

### 9.4.1 표준 `docker-compose.yml`

프로젝트 루트에 다음 파일을 둔다.

```yaml
# docker-compose.yml
services:
  app:
    build:
      context: .
    image: todo-api:dev
    env_file:
      - .env
    environment:
      # .env 의 값을 덮거나 보강할 때 사용
      DATABASE_URL: postgresql+asyncpg://todo:todo@db:5432/todo
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "8000:8000"
    restart: unless-stopped

  migrate:
    image: todo-api:dev
    build:
      context: .
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://todo:todo@db:5432/todo
    depends_on:
      db:
        condition: service_healthy
    # 일회성 작업: `docker compose run --rm migrate` 로 명시 실행
    command: ["alembic", "upgrade", "head"]
    profiles:
      - tools

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: todo
      POSTGRES_PASSWORD: todo
      POSTGRES_DB: todo
    volumes:
      - db_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U todo -d todo"]
      interval: 5s
      timeout: 5s
      retries: 10
    restart: unless-stopped

volumes:
  db_data:
```

각 서비스의 책임을 한 줄로 정리한다.

| 서비스 | 역할 |
|--------|------|
| `app` | 우리의 FastAPI 앱 (Gunicorn + UvicornWorker, 포트 8000) |
| `migrate` | 일회성으로 `alembic upgrade head` 만 돌리는 컨테이너. 평소엔 안 뜸(`profiles: tools`) |
| `db` | PostgreSQL 16. 데이터는 `db_data` 볼륨에 영속 |

> **`profiles: [tools]` 은 뭔가요?** 이 서비스는 일반 `docker compose up` 시 띄우지 않고, 명시적으로 부를 때만 실행. `docker compose --profile tools up migrate` 또는 `docker compose run --rm migrate` 로 실행한다. 마이그레이션·시드·일회성 백업 같은 작업에 쓴다.

### 9.4.2 `depends_on` 만으로는 부족하다 — `service_healthy`

`depends_on: [db]` 만 적으면 "db 컨테이너가 시작된 직후" 에 app 이 뜨는데, **PostgreSQL 은 시작 직후 몇 초 동안 아직 접속을 받지 않는다.** 이 사이에 app 이 부팅하면서 DB 연결을 시도하다 실패하는 일이 자주 생긴다.

해결책이 두 가지.

1. **헬스 체크 + 조건부 의존성**(권장): 위 예시처럼 `db` 에 `healthcheck` 를 달고, `app` 의 `depends_on` 을 `condition: service_healthy` 로 바꾼다. Compose 가 `pg_isready` 가 OK 가 될 때까지 기다린다.
2. **앱 안에 재시도 로직**: 부팅 시 DB 연결을 N 번 재시도. 학습용으로는 1번이 더 깔끔하다.

### 9.4.3 환경 변수 분리 — `.env` 파일

위 yaml 의 `env_file: [.env]` 가 **로컬 개발용 `.env`** 를 컨테이너에 주입한다. `.env` 예시:

```
# .env  — 절대 git 에 올리지 않는다
DATABASE_URL=postgresql+asyncpg://todo:todo@db:5432/todo
JWT_SECRET=local-dev-secret-do-not-use-in-prod
CORS_ALLOW_ORIGINS=http://localhost:3000
APP_NAME=Todo API (local)
```

협업용으로 git 에 두는 `.env.example`:

```
DATABASE_URL=
JWT_SECRET=
CORS_ALLOW_ORIGINS=
APP_NAME=Todo API
```

> **운영에서는 `.env` 파일을 안 쓴다.** Render·Fly.io 의 환경 변수 UI 또는 시스템 환경 변수로 같은 이름을 주입한다. Compose 의 `.env` 는 **로컬 개발 전용**.

### 9.4.4 사용 흐름

```bash
# 1) 처음 한 번: 이미지 빌드
docker compose build

# 2) DB 먼저 띄움 (헬스 체크가 OK 될 때까지 기다림)
docker compose up -d db

# 3) 마이그레이션 한 번 (alembic upgrade head)
docker compose run --rm migrate

# 4) 앱 띄우기 (포그라운드, Ctrl+C 로 종료)
docker compose up app

# 또는 백그라운드
docker compose up -d app
docker compose logs -f app

# 5) 정지
docker compose down

# 6) 데이터까지 모두 초기화하고 싶을 때
docker compose down -v
```

이 다섯~여섯 명령이 익숙해지면, **여러분의 컴퓨터에는 운영과 거의 같은 환경**이 돈다는 사실을 손으로 체감할 수 있다. 다음 절부터는 이 같은 그림을 클라우드 서버에 그대로 옮기는 작업이다.

---

## 9.5 Render 배포 — GitHub 연결로 5분 안에

Render 는 "GitHub 저장소를 연결하면 알아서 빌드·배포·HTTPS 까지 해 주는" 관리형 PaaS 다. **Heroku 의 빈 자리를 가장 자연스럽게 채운 서비스**로, 입문자에게 가장 추천한다.

- 공식: https://render.com/
- 가격: 무료 티어(Web Service 슬립 모드 포함) ~ 월 $7 부터 항상 켜짐
- 강점: GitHub 연동 + Dockerfile 자동 인식 + HTTPS 자동 + 관리형 PostgreSQL 포함

### 9.5.1 준비물

- [ ] GitHub 계정과 우리 앱 코드가 올라간 저장소 (`Dockerfile`, `pyproject.toml`, `uv.lock` 포함)
- [ ] Render 계정 (`https://render.com/` 에서 GitHub 로 가입)

> **저장소가 비공개여도 되나?** 된다. Render 는 GitHub OAuth 로 권한을 받아 비공개 저장소도 빌드한다. 단, 무료 플랜에서도 가능.

### 9.5.2 PostgreSQL 먼저 만든다

배포 순서는 보통 **DB → 앱** 이다. 앱이 시작되자마자 DB 연결 정보를 필요로 하기 때문.

1. Render 대시보드 → **New +** → **PostgreSQL**.
2. 정보 입력:
   - **Name**: `todo-db`
   - **Region**: 가까운 곳(예: `Singapore`).
   - **Plan**: Free 또는 Starter($7).
3. **Create Database** 클릭.
4. 1~2분 후 페이지 하단의 **Connections** 섹션에서 두 가지를 복사해 둔다.
   - **Internal Database URL** — 같은 Render 프로젝트의 다른 서비스가 쓰는 내부 주소.
   - **External Database URL** — 외부에서 접속할 때 (로컬 DBeaver 등).

값은 다음과 같이 생겼다.

```
postgresql://todo_db_user:secret@dpg-xxx-a:5432/todo_db
```

> **`postgresql://` 를 `postgresql+asyncpg://` 로 바꿔라.** SQLAlchemy 의 비동기 드라이버를 쓰려면 스킴이 필요하다. 환경 변수에 넣을 때 다음처럼 직접 변환:
> ```
> postgresql+asyncpg://todo_db_user:secret@dpg-xxx-a:5432/todo_db
> ```

### 9.5.3 Web Service 생성

1. Render 대시보드 → **New +** → **Web Service**.
2. **Connect a Git provider** 단계에서 GitHub 와 연결되어 있지 않다면 **Connect GitHub** 를 누르고 권한을 부여.
3. 우리 저장소(예: `gubosung/07-TodoAPI`) 를 선택.
4. 다음 정보를 입력한다.
   - **Name**: `todo-api`
   - **Region**: PostgreSQL 과 같은 지역(같지 않으면 네트워크 비용·지연이 커진다).
   - **Branch**: `main`
   - **Runtime**: **Docker** 를 선택. (저장소 루트에 `Dockerfile` 이 있으면 자동 감지된다.)
   - **Instance Type**: Free($0/mo, 슬립) 또는 Starter($7/mo, 항상 켜짐).
5. **Environment Variables** 섹션에서 비밀값을 입력한다.
   - `DATABASE_URL` = 위에서 복사한 **Internal** URL을 `postgresql+asyncpg://...` 로 변환한 값.
   - `JWT_SECRET` = 길고 무작위한 문자열. 터미널에서 `openssl rand -base64 48` 로 만들어 붙여넣기.
   - `CORS_ALLOW_ORIGINS` = 운영 프론트 도메인 (예: `https://app.example.com`). 없으면 일단 `*`.
   - 그 외 본인 앱이 요구하는 변수.
6. **Health Check Path**: `/health`.
7. **Auto-Deploy**: `Yes` (기본값). main 브랜치 푸시 시 자동 재배포.
8. **Create Web Service** 클릭.

이후 Render 가 다음 순서로 자동 진행한다.

```
Cloning repo
  → docker build (Dockerfile 인식)
  → docker push to internal registry
  → starting service (curl /health)
  → live at https://todo-api-xxx.onrender.com
```

처음 빌드는 3~6분 정도 걸린다. 두 번째부터는 캐시 덕분에 1~2분.

### 9.5.4 마이그레이션을 어디에 끼워 넣나

Render 자체는 "배포 시 마이그레이션을 자동으로 돌려라" 같은 단일 옵션을 제공하지 않는다. 입문자에게 가장 단순한 두 가지 패턴을 적는다.

**패턴 A — 시작 명령에 한 줄 더 (가장 간단, 학습용 OK)**

`Dockerfile` 의 `CMD` 를 다음처럼 바꿔, 컨테이너가 뜰 때마다 마이그레이션을 한 번 돌리고 곧장 서버를 띄운다.

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && exec gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 --workers 4 --timeout 60 --access-logfile - --error-logfile -"]
```

`alembic upgrade head` 는 **변경사항이 없으면 빠르게 끝나기 때문에**, 매 배포마다 부르는 비용이 매우 작다. 단, 워커가 여러 개라서 동시에 부팅할 때 마이그레이션이 충돌할 위험이 이론적으로 있다 — Alembic 이 자체적으로 락을 걸어 안전한 편이지만, 트래픽이 큰 운영에서는 다음 패턴 B 로 넘어간다.

**패턴 B — Render Job 으로 분리 (권장 운영)**

Render 대시보드의 **New +** → **Cron Job** 또는 **Pre-Deploy Command**(Render 의 "Build & Deploy" 설정에 있는 항목) 에 다음을 적어둔다.

```
alembic upgrade head
```

Pre-Deploy Command 는 **새 인스턴스가 트래픽을 받기 전에 한 번 실행**된다. 마이그레이션이 실패하면 배포가 자동으로 롤백된다.

> **주의**: Pre-Deploy Command 는 **유료 플랜(Standard 이상)에서만** 제공된다. 무료(Free)·Starter 플랜에서는 패턴 A(시작 직전 컨테이너 안에서 실행)를 쓰거나, 별도의 Cron Job 으로 분리해야 한다.

> **`autoMigrate` 같은 코드는 운영에 두지 마라.** `app/main.py` 안에 `Base.metadata.create_all(...)` 같은 호출이 들어 있다면 운영에서는 반드시 빼라. 마이그레이션은 **배포 단계의 명시적 작업**으로 분리해야 데이터 사고가 줄어든다.

### 9.5.5 HTTPS 와 도메인

- Render 는 모든 Web Service 에 **`*.onrender.com` 서브도메인 + 무료 HTTPS** 를 자동 제공한다.
- 자기 도메인을 쓰려면 **Settings → Custom Domains** 에서 도메인을 추가하고, 안내된 CNAME / A 레코드를 DNS 에 등록한다. 그 후 Render 가 Let's Encrypt 인증서를 자동 발급·갱신한다.

### 9.5.6 배포 후 확인 — 헬스 체크와 Swagger

```bash
curl https://todo-api-xxx.onrender.com/health
# {"status":"ok"}

# 자동 문서
open https://todo-api-xxx.onrender.com/docs
```

500 이 나오면 Render 의 **Logs** 탭을 열어 에러 메시지를 확인한다. 가장 흔한 원인 두 개:

1. `DATABASE_URL` 의 스킴을 `postgresql+asyncpg://` 로 안 바꿔 SQLAlchemy 가 동기 드라이버(`psycopg`) 를 찾다 실패.
2. PostgreSQL 의 **Internal** URL 이 아니라 **External** URL 을 넣어, 같은 지역 안에서도 외부 망을 한 번 도느라 타임아웃.

### 9.5.7 Render 의 한계 (정직하게)

- 무료 플랜은 15분 사용이 없으면 슬립 → 첫 요청에 ~30초 콜드 스타트.
- DB 무료 플랜도 30일 사용 후 만료(데이터 삭제). 학습 후 끄거나 유료 전환.
- 한국·일본 리전은 없다 (가까운 Singapore 사용).

> **그럼에도 입문자에게 추천하는 이유**: GitHub 푸시 → 자동 빌드 → HTTPS 까지의 흐름을 한 시간 안에 손에 익힐 수 있는 가장 짧은 길이기 때문이다. 한 번 익혀두면 다른 모든 PaaS 의 흐름이 비슷하게 보인다.

---

## 9.6 Fly.io 배포 — 글로벌 엣지에 가까운 PaaS

Fly.io 는 "전 세계 30+ 리전에 우리 앱 컨테이너를 가깝게 띄워주는" PaaS 다. CLI(`flyctl`) 가 매우 잘 만들어져 있어, **터미널에서만 모든 작업이 끝나는** 흐름을 좋아한다면 Render 보다 더 잘 맞는다.

- 공식: https://fly.io/
- 가격: 사용한 만큼(시간×CPU 메모리) 과금 + 매월 $5 의 무료 사용량.
- 강점: `flyctl` 의 자동 Dockerfile 인식, 글로벌 멀티 리전, 관리형 Postgres.

### 9.6.1 준비물

- [ ] Fly.io 계정 (`https://fly.io/app/sign-up`)
- [ ] 결제 수단 등록 (소액 사용량 과금 모델 — 신용카드 인증 필요)
- [ ] `flyctl` (a.k.a. `fly`) 설치

```bash
# macOS
brew install flyctl

# Linux / WSL2
curl -L https://fly.io/install.sh | sh

# 로그인
fly auth login
```

### 9.6.2 `fly launch` — Dockerfile 자동 인식

프로젝트 루트(예: `07-TodoAPI/`) 에서:

```bash
fly launch --no-deploy
```

`flyctl` 이 다음을 자동 처리한다.

1. 폴더에 `Dockerfile` 이 있는지 확인 → 있으면 그대로 사용.
2. 앱 이름(예: `todo-api-yourname`), 리전(예: `nrt` = 도쿄, `sin` = 싱가포르) 을 묻는다.
3. Postgres 를 같이 만들 거냐고 묻는다 — **`y` 누르고 Development(작은 인스턴스) 선택**.
4. 루트에 **`fly.toml`** 파일을 생성. 이게 우리 앱의 배포 설정이다.

생성된 `fly.toml` 은 대략 이렇게 생겼다(일부 자동 생성 항목 생략).

```toml
app = "todo-api-yourname"
primary_region = "nrt"

[build]
  # Dockerfile 자동 인식 (이 부분이 비어 있으면 같은 폴더의 Dockerfile 사용)

[env]
  PORT = "8000"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"      # 트래픽 없으면 자동 정지(요금 절약)
  auto_start_machines = true        # 요청이 오면 자동 시작
  min_machines_running = 0
  processes = ["app"]

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 512
```

> **`auto_stop_machines = "stop"`**: 트래픽이 없으면 머신을 자동으로 정지해 시간당 요금을 아낀다. 첫 요청 시에 0.5~2초 콜드 스타트가 있다. 학습용에 적합. 항상 켜두려면 `min_machines_running = 1`.

### 9.6.3 비밀값 주입 — `fly secrets set`

Render 의 환경 변수 UI 에 해당하는 작업을 CLI 로 한다.

```bash
fly secrets set \
    JWT_SECRET="$(openssl rand -base64 48)" \
    CORS_ALLOW_ORIGINS="*"
```

`DATABASE_URL` 은 위 9.6.2 단계에서 Postgres 를 같이 만들었다면 **이미 자동 주입**돼 있다. 다음 명령으로 확인.

```bash
fly secrets list
```

다음 같은 출력이 나오면 OK.

```
NAME                    DIGEST        CREATED AT
DATABASE_URL            abc...         5m ago
JWT_SECRET              def...         1m ago
CORS_ALLOW_ORIGINS      ghi...         1m ago
```

> **여전히 스킴은 직접 바꿔야**: `fly` 가 만든 `DATABASE_URL` 은 `postgres://...` 로 시작한다. 코드에서는 `postgresql+asyncpg://` 가 필요하므로, `app/config.py` 또는 `app/db.py` 안에서 한 줄 변환을 해 두는 편이 안전하다.
>
> ```python
> # app/db.py 안의 한 줄
> raw = settings.database_url
> if raw.startswith("postgres://"):
>     raw = raw.replace("postgres://", "postgresql+asyncpg://", 1)
> elif raw.startswith("postgresql://") and "+asyncpg" not in raw:
>     raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
> engine = create_async_engine(raw, ...)
> ```

### 9.6.4 `fly deploy` — 빌드 + 배포 한 줄

```bash
fly deploy
```

`flyctl` 이 다음을 차례로 한다.

1. 로컬 또는 Fly 의 빌더에서 `Dockerfile` 로 이미지를 빌드.
2. Fly 의 컨테이너 레지스트리에 푸시.
3. 새 머신을 띄우고 헬스 체크가 통과하면 트래픽을 새 머신으로 옮김(롤링 배포).
4. 옛 머신을 종료.

전 과정이 보통 1~3분.

### 9.6.5 마이그레이션 — `fly ssh console` 또는 `release_command`

**가장 간단한 방법**: 배포 직후 한 번 SSH 로 들어가 손으로 돌린다.

```bash
fly ssh console
# 컨테이너 안 셸이 열림
$ alembic upgrade head
$ exit
```

**자동화 방법**: `fly.toml` 에 다음을 추가하면 매 배포마다 새 머신이 트래픽을 받기 전에 한 번 실행된다.

```toml
[deploy]
  release_command = "alembic upgrade head"
```

이 한 줄이 Render 의 "Pre-Deploy Command" 와 같은 역할을 한다.

### 9.6.6 PostgreSQL — `fly postgres create` (필요 시)

`fly launch` 단계에서 Postgres 만들기를 건너뛰었다면 다음으로 만들 수 있다.

```bash
fly postgres create --name todo-db --region nrt --vm-size shared-cpu-1x --initial-cluster-size 1

# 우리 앱과 연결 (DATABASE_URL 자동 주입)
fly postgres attach --app todo-api-yourname todo-db
```

> **주의**: Fly Postgres 는 "관리형" 이긴 하지만, 백업·점검 책임은 사용자에게 있다. 운영 트래픽이 큰 서비스라면 RDS 같은 더 본격 관리형 DB 를 쓰는 게 안전하다. 학습·소규모 서비스라면 충분히 좋다.

### 9.6.7 도메인과 HTTPS

`fly launch` 직후 자동으로 `https://todo-api-yourname.fly.dev` 가 발급된다 (HTTPS 포함). 자기 도메인을 쓰려면:

```bash
fly certs add api.example.com
```

이후 안내되는 CNAME 또는 A 레코드를 DNS 에 등록하면, Fly 가 Let's Encrypt 인증서를 발급·갱신한다.

### 9.6.8 자주 쓰는 fly 명령

```bash
fly status                  # 머신 상태
fly logs                    # 실시간 로그
fly logs --tail 200         # 최근 200줄
fly ssh console             # 컨테이너 안 셸
fly deploy                  # 다시 배포
fly scale count 2           # 머신 N개로 늘리기
fly scale memory 1024       # 메모리 1GB 로
fly secrets unset JWT_SECRET  # 비밀 제거
fly machines list           # 머신 목록 (멀티 리전 시 유용)
```

---

## 9.7 AWS EC2(t3.small) — Docker 만으로 가장 단순하게

이 절은 **AWS 의 가장 기초인 EC2 한 대를 빌려, Docker 컨테이너 한 개를 띄우는** 학습 목적의 경로다. ECS·ECR·Fargate 같은 본격 서비스는 운영 채택의 선택지로 두고, 입문 단계에선 **"리눅스 한 대 빌려서 직접 띄우기"** 가 가장 손에 잘 잡힌다.

> **t3.small 이 적당한 이유**: t3.micro(1 vCPU, 1GB RAM) 는 Python 컨테이너 + Postgres 클라이언트 라이브러리가 OOM 으로 가끔 죽는다. **t3.small(2 vCPU, 2GB RAM)** 이면 학습용 트래픽에 여유롭다. 월 $20 내외 (서울 리전 기준).

### 9.7.1 준비물

- [ ] AWS 계정과 결제 수단
- [ ] AWS 콘솔에 로그인할 수 있는 사용자
- [ ] 로컬에 SSH 클라이언트 (macOS/Linux 의 기본 `ssh`, Windows 의 PowerShell `ssh`)

### 9.7.2 EC2 인스턴스 생성

1. AWS 콘솔 → **EC2** → **인스턴스 시작**(Launch instance).
2. **이름**: `todo-api-server`.
3. **AMI**: Ubuntu Server **24.04 LTS** (또는 22.04 LTS) — x86_64. ARM(Graviton) 도 가능하지만 처음엔 x86 이 생태계가 가장 두텁다.
4. **인스턴스 유형**: `t3.small`.
5. **키 페어**: 새로 만들거나 기존 것을 선택. **`.pem` 파일을 안전하게 보관한다.**
6. **네트워크 설정** → **보안 그룹**:
   - SSH(22) — **내 IP** 만 허용 (0.0.0.0/0 으로 열어두면 위험).
   - HTTP(80) — 0.0.0.0/0
   - HTTPS(443) — 0.0.0.0/0
   - 사용자 정의 TCP(8000) — 학습 단계에서만 0.0.0.0/0 으로 열어두고, **나중엔 닫는다** (nginx 가 80/443 → 8000 으로 프록시할 거라서 외부에 8000 을 열어둘 필요가 없다).
7. **스토리지**: 20GB 정도면 학습용에 충분.
8. **시작**.

생성된 인스턴스의 **퍼블릭 IPv4 주소**(또는 DNS) 를 메모해 둔다.

### 9.7.3 SSH 로 접속

```bash
chmod 400 ~/Downloads/todo-key.pem   # 처음 한 번만
ssh -i ~/Downloads/todo-key.pem ubuntu@<퍼블릭IP>
```

> **`ubuntu` 사용자**: AWS Ubuntu AMI 의 기본 SSH 유저는 `ubuntu` 다 (Amazon Linux 는 `ec2-user`). 키 파일 권한이 너무 열려 있으면 `Permissions are too open` 에러로 거부되니 `chmod 400` 을 잊지 말자.

### 9.7.4 Docker 설치

서버 안에서:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Docker 공식 한 줄 설치 스크립트 (입문에 가장 쉬움)
curl -fsSL https://get.docker.com | sh

# ubuntu 사용자가 sudo 없이 docker 를 쓸 수 있게
sudo usermod -aG docker $USER

# 그룹 변경을 즉시 반영 (또는 ssh 로그아웃 후 재접속)
newgrp docker

# 확인
docker --version
docker compose version
```

### 9.7.5 코드 가져오기 — git 또는 scp

**git 사용(권장)**:

```bash
git clone https://github.com/yourname/07-TodoAPI.git
cd 07-TodoAPI
```

비공개 저장소라면 [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) 을 만들어 HTTPS URL 의 사용자 이름/비밀번호로 쓰거나, EC2 안에서 SSH 키를 만들어 GitHub 에 등록한다.

**scp 사용**: 로컬 폴더를 통째로 보내는 방식.

```bash
# 로컬에서 (.venv, .git 등을 빼고 보냄)
rsync -avz --exclude '.venv' --exclude '.git' --exclude '*.db' \
    -e "ssh -i ~/Downloads/todo-key.pem" \
    ./ ubuntu@<퍼블릭IP>:/home/ubuntu/07-TodoAPI/
```

### 9.7.6 `.env` 파일 작성

```bash
nano /home/ubuntu/07-TodoAPI/.env
```

```
DATABASE_URL=postgresql+asyncpg://todo:todo@db:5432/todo
JWT_SECRET=서버에서_생성한_긴_랜덤_문자열
CORS_ALLOW_ORIGINS=*
APP_NAME=Todo API (prod)
```

> **랜덤 시크릿 한 줄 생성**: 서버에서 `openssl rand -base64 48` 한 번 친 결과를 그대로 붙여넣는다.

### 9.7.7 빌드 + 띄우기

```bash
cd /home/ubuntu/07-TodoAPI
docker compose build
docker compose up -d db          # DB 먼저
docker compose run --rm migrate  # 마이그레이션
docker compose up -d app         # 앱 백그라운드
docker compose logs -f app       # 로그 확인
```

브라우저에서 `http://<퍼블릭IP>:8000/health` → `{"status":"ok"}` 가 보이면 성공.

### 9.7.8 nginx + HTTPS — 다음 절(9.8)로 그대로 이어진다

여기까지가 "EC2 에 Docker 만 깐" 단계다. 도메인을 붙이고 HTTPS 를 발급하려면 다음 절(9.8 Ubuntu 직접 배포) 의 **9.8.5 nginx 리버스 프록시** 와 **9.8.6 Let's Encrypt** 절차를 그대로 따라하면 된다 — Ubuntu 절차가 EC2 안에서 그대로 동작한다.

### 9.7.9 EC2 의 한계와 다음 단계

- 인스턴스 한 대가 죽으면 서비스가 멈춘다(가용 영역 한 대 의존). 학습용엔 OK, 운영 SLA 가 필요하면 ECS / Auto Scaling Group / 다중 가용 영역 으로 확장.
- 인스턴스 안에 Postgres 를 같이 띄우면 데이터가 인스턴스 디스크에 묶인다. 운영에선 **RDS for PostgreSQL** 등 관리형으로 분리 권장.
- 보안 그룹의 8000 포트는 nginx 가 동작하기 시작하면 닫는다 (외부에서 80/443 으로만 들어오게).

> **이 가이드는 EC2 까지만 다룬다.** ECR/ECS/Fargate/ALB/ACM 의 본격 운영 경로는 분량이 한 챕터 더 필요해 12장 레퍼런스에 포인터만 남긴다.

---

## 9.8 Ubuntu 서버에 직접 띄우기 — systemd + nginx + Let's Encrypt

가장 손이 많이 가는 경로지만, **시스템 운영을 한 번 손에 익히면 다른 모든 배포 경로가 쉽게 보인다.** Docker 를 쓰지 않고 Python 자체를 시스템에 깔아 systemd 서비스로 등록하는 흐름이다.

이 절은 위 9.7(EC2) 또는 다른 VPS(DigitalOcean, Linode, Vultr 등) 에서 **Ubuntu 22.04/24.04 LTS** 인스턴스 한 대가 준비된 상태를 가정한다.

### 9.8.1 시스템 준비

서버에 SSH 로 들어간 뒤 기본 보안·편의 도구 설치.

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
    build-essential curl git \
    libpq5 \
    nginx \
    certbot python3-certbot-nginx
```

### 9.8.2 Python 3.13 + uv 설치

03장의 Linux 절차와 동일.

```bash
# Python 3.13 (Ubuntu 24.04 의 기본 저장소에 없으면 deadsnakes PPA)
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev

# uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
uv --version
```

### 9.8.3 앱 디렉터리 배치 — `/srv/myapp/`

리눅스 관례상, 운영용 앱은 `/srv/<앱이름>/` 또는 `/opt/<앱이름>/` 아래에 둔다. 사용자 홈(`/home/ubuntu/`) 도 가능하지만, **여러 사람이 운영을 다룰 가능성이 있다면 `/srv/` 가 깔끔**하다.

```bash
sudo mkdir -p /srv/myapp
sudo chown $USER:$USER /srv/myapp

cd /srv/myapp
git clone https://github.com/yourname/07-TodoAPI.git .

# 의존성 설치
uv sync --frozen --no-dev
```

`/srv/myapp/.venv/` 가 만들어진다.

### 9.8.4 systemd 서비스 파일 작성

systemd 는 리눅스에서 백그라운드 프로세스(데몬) 를 관리하는 표준 도구다. 우리 앱을 systemd 서비스로 등록하면, **재부팅 후 자동 시작**과 **죽었을 때 자동 재시작**을 운영체제가 책임진다.

`/etc/systemd/system/myapp.service`:

```bash
sudo nano /etc/systemd/system/myapp.service
```

```ini
[Unit]
Description=Todo API (FastAPI + Gunicorn + UvicornWorker)
After=network.target

[Service]
Type=simple

# 어떤 사용자/그룹으로 돌릴지 (절대 root 금지)
User=ubuntu
Group=ubuntu

# 작업 디렉터리 — 앱 코드의 루트
WorkingDirectory=/srv/myapp

# 환경 변수 파일 — 비밀값을 코드에 박지 않고 여기에서만 읽는다
EnvironmentFile=/srv/myapp/.env

# 실행 명령 — .venv 안의 gunicorn 을 절대 경로로 부른다
ExecStart=/srv/myapp/.venv/bin/gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -b 127.0.0.1:8000 \
    --workers 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -

# 재시작 정책 — 죽으면 5초 뒤에 자동 재시작
Restart=on-failure
RestartSec=5

# 표준 출력/에러를 journald 로 (journalctl 로 모아 볼 수 있음)
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

핵심 포인트.

| 항목 | 의미 |
|------|------|
| `User=ubuntu` | root 가 아닌 ubuntu 권한으로 실행 (보안) |
| `WorkingDirectory=/srv/myapp` | 상대 경로 import 가 이 폴더 기준으로 동작 |
| `EnvironmentFile=/srv/myapp/.env` | `.env` 의 KEY=VALUE 들이 환경 변수로 주입됨 |
| `ExecStart=...` | **절대 경로**로 `gunicorn` 을 지정. systemd 는 PATH 가 비어 있는 상태로 동작하므로 항상 절대 경로. |
| `-b 127.0.0.1:8000` | nginx 가 같은 머신에서 프록시할 거라 외부에 직접 노출하지 않음 |
| `Restart=on-failure` | 비정상 종료 시 자동 재시작 |

`.env` 파일은 다음처럼 둔다.

```bash
sudo nano /srv/myapp/.env
```

```
DATABASE_URL=postgresql+asyncpg://todo:todo@127.0.0.1:5432/todo
JWT_SECRET=긴_랜덤_문자열
CORS_ALLOW_ORIGINS=https://app.example.com
```

> **`.env` 의 권한 좁히기**: `chmod 600 /srv/myapp/.env` 로 다른 사용자가 못 읽게 한다. 보안의 작은 한 단계.

서비스 등록·시작:

```bash
sudo systemctl daemon-reload      # 새 service 파일 인식
sudo systemctl enable myapp       # 부팅 시 자동 시작 등록
sudo systemctl start myapp        # 즉시 시작
sudo systemctl status myapp       # 상태 확인
```

`Active: active (running)` 이 보이면 성공. 만약 실패하면 다음으로 원인을 본다.

```bash
sudo journalctl -u myapp -n 200 --no-pager
```

### 9.8.5 nginx 리버스 프록시 설정

이제 외부의 80/443 으로 들어오는 HTTP 요청을 nginx 가 받아 내부의 8000 으로 넘긴다. **이 한 단계가 HTTPS 와 추후 정적 파일 서빙·캐시·로드 분산의 모든 발판**이다.

> **리버스 프록시(reverse proxy)란?** 클라이언트가 보낸 요청을 일단 받아 뒤쪽의 진짜 앱 서버에 넘기는 중계자. 클라이언트 입장에서는 nginx 가 전체 백엔드처럼 보이고, 실제 우리 앱은 그 뒤에 숨어 있다.

`/etc/nginx/sites-available/myapp`:

```bash
sudo nano /etc/nginx/sites-available/myapp
```

```nginx
# 처음엔 80만. 다음 단계에서 certbot 이 443 블록을 자동으로 추가한다.
server {
    listen 80;
    listen [::]:80;
    server_name api.example.com;

    # 큰 본문 업로드 허용량 (필요 시 조정)
    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;

        # 클라이언트의 진짜 정보를 우리 앱에 전달 (FastAPI 가 IP·도메인을 정확히 알 수 있게)
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket / Server-Sent Events 를 쓸 가능성이 있다면 둔다
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 비동기 응답 대기 시간 — 일반 REST API 라면 60s 면 넉넉
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }
}
```

활성화 후 문법 검사·리로드.

```bash
sudo ln -s /etc/nginx/sites-available/myapp /etc/nginx/sites-enabled/

# 기본 default 사이트는 비활성 (선택)
sudo rm -f /etc/nginx/sites-enabled/default

sudo nginx -t          # 문법 OK 확인
sudo systemctl reload nginx
```

이 시점에서 도메인이 이 서버 IP 를 가리키도록 DNS 를 등록해 둔다.

- `api.example.com` 의 **A 레코드** → 서버의 퍼블릭 IPv4
- (선택) **AAAA 레코드** → IPv6

브라우저에서 `http://api.example.com/health` 를 열어 200 이 나오면 nginx 까지 OK.

### 9.8.6 Let's Encrypt 로 HTTPS 발급/갱신

`certbot` 한 줄이면 끝난다.

```bash
sudo certbot --nginx -d api.example.com
```

certbot 이 다음을 자동으로 처리한다.

1. Let's Encrypt 에 도메인 소유 증명(80 포트로 임시 토큰 검증).
2. 인증서 파일 발급(`/etc/letsencrypt/live/api.example.com/`).
3. **nginx 설정에 443 리스너 + 인증서 경로 + HTTP→HTTPS 리다이렉트를 자동 추가**.
4. systemd 타이머에 **자동 갱신**(`certbot.timer`) 등록 — 90일 만료 전에 알아서 갱신.

이후 다음이 모두 동작한다.

- `https://api.example.com/health` → 200, 자물쇠 아이콘.
- `http://api.example.com/health` → 자동으로 https 로 리다이렉트.

자동 갱신이 잘 등록되었는지 확인.

```bash
sudo systemctl list-timers | grep certbot
sudo certbot renew --dry-run
```

`Congratulations, all simulated renewals succeeded` 가 보이면 안전.

> **HTTPS 가 왜 필수인가?** 운영에서 비밀번호·JWT·개인정보가 브라우저와 서버 사이를 평문으로 오가는 상황은 곧 사고로 이어진다. HTTPS 는 그 모든 통신을 암호화한다. **Let's Encrypt 는 무료**이니 망설일 이유가 없다.

### 9.8.7 로그 보기 — `journalctl`

systemd 서비스의 표준출력/표준에러는 자동으로 `journald` 가 모은다.

```bash
# 우리 앱의 최근 로그
sudo journalctl -u myapp -n 200 --no-pager

# 실시간 추적 (Ctrl+C 로 종료)
sudo journalctl -u myapp -f

# 시간 범위
sudo journalctl -u myapp --since "1 hour ago"
sudo journalctl -u myapp --since "2026-04-25 10:00"

# 모든 단위(앱, nginx 등) 의 에러만
sudo journalctl -p err -b
```

nginx 액세스 로그는 따로.

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 9.8.8 마이그레이션 — 배포 시점에 한 줄

systemd 서비스 자체는 마이그레이션을 부르지 않는다(부팅 시 자동으로 부르면 위험). 배포 절차는 다음 같은 단순한 셸 스크립트로 묶는다.

`/srv/myapp/deploy.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /srv/myapp

git pull origin main

# 의존성 동기화 (lock 그대로)
uv sync --frozen --no-dev

# DB 마이그레이션
uv run alembic upgrade head

# systemd 서비스 재시작
sudo systemctl restart myapp

echo "Deployed at $(date)"
```

```bash
chmod +x /srv/myapp/deploy.sh
```

이후 배포는 한 줄.

```bash
/srv/myapp/deploy.sh
```

### 9.8.9 Postgres 도 같은 서버에 둘 거라면

학습용으로 같은 서버에 Postgres 를 두려면.

```bash
sudo apt install -y postgresql postgresql-contrib

# 사용자/DB 만들기
sudo -u postgres psql <<'SQL'
CREATE USER todo WITH PASSWORD 'todo';
CREATE DATABASE todo OWNER todo;
GRANT ALL PRIVILEGES ON DATABASE todo TO todo;
SQL
```

`.env` 의 `DATABASE_URL` 은 `postgresql+asyncpg://todo:todo@127.0.0.1:5432/todo`. 같은 서버 안에서만 접근하므로 Postgres 의 외부 포트는 닫아둔다(기본). UFW 가 켜져 있다면 그 자체로 보호된다.

> **운영 권장**: Postgres 는 별도 관리형 서비스(RDS, Render Postgres, Supabase 등) 로 분리. 한 머신에 함께 두면 백업·업그레이드·OOM 위험이 한꺼번에 묶인다.

---

## 9.9 운영 체크리스트 — 어떤 경로든 이 다섯 묶음

배포 경로별 절차를 모두 한 묶음으로 다시 묶는다. **이 체크리스트가 통과하면, 어디에 띄웠든 합격선**이다.

### 9.9.1 비밀값과 환경 변수

- [ ] `.env` 가 git 에 올라가 있지 않다(`.gitignore` 등록).
- [ ] `.dockerignore` 에 `.env`, `.env.*` 가 들어 있다.
- [ ] 모든 비밀값(`JWT_SECRET`, `DATABASE_URL` 의 비밀번호 부분)이 코드/저장소에서 검색해도 안 나온다.
- [ ] 운영의 비밀값 주입 방법이 명확하다 (Render 의 Env UI / Fly secrets / EC2 의 systemd EnvironmentFile / k8s Secret 등).
- [ ] 같은 비밀이 여러 환경(개발/스테이지/운영) 에 다른 값으로 분리되어 있다.

### 9.9.2 데이터베이스 마이그레이션

- [ ] `app/main.py` 안에 `Base.metadata.create_all(...)` 같은 부팅 시 스키마 생성 호출이 **없다**.
- [ ] 배포 파이프라인의 어느 단계에서 `alembic upgrade head` 가 실행되는지 한 줄로 답할 수 있다(예: "Render 의 Pre-Deploy Command", "Fly 의 release_command", "Ubuntu 의 deploy.sh 안").
- [ ] 마이그레이션 실패 시 배포가 자동으로 롤백되거나, 적어도 알람이 뜨도록 되어 있다.
- [ ] 운영 DB 의 스키마 수정은 항상 Alembic 리비전을 통해서만 한다 (psql 직접 ALTER 금지).

### 9.9.3 헬스 체크 엔드포인트 `/health`

- [ ] `GET /health` 가 200 을 돌려준다.
- [ ] 인증 미들웨어가 `/health` 를 통과시킨다 (자기도 모르게 `Depends(get_current_user)` 의 영향을 받지 않게).
- [ ] 플랫폼/로드 밸런서가 이 경로를 헬스 체크 대상으로 등록되어 있다.
- [ ] (선택) `/health/db` 같이 DB 한 번 SELECT 해 보는 더 깊은 헬스 체크도 별도로 둔다.

```python
# app/main.py
@app.get("/health")
def health():
    return {"status": "ok"}
```

### 9.9.4 로그와 로그 레벨

- [ ] 운영 로그 레벨이 `INFO` 또는 `WARNING`. `DEBUG` 가 아니다.
- [ ] 로그가 **표준 출력/표준 에러**로 흐른다 (파일에 직접 쓰지 않음). 컨테이너/플랫폼이 로그를 수집할 수 있어야 한다.
- [ ] `print(...)` 로 운영 로그를 찍지 않는다 — `logging` 모듈 또는 `structlog` 를 쓴다.

```python
# app/main.py 위쪽 한 번
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
```

> **structlog 짧은 안내**: 운영의 모든 로그를 JSON 한 줄로 만들어 ELK/Datadog/Loki 같은 수집기와 잘 어울리게 만드는 라이브러리. 12장 레퍼런스에서 짧게 다룬다. 학습 단계에서는 표준 `logging` 으로 충분.

### 9.9.5 CORS

- [ ] 운영에서 `CORS_ALLOW_ORIGINS=*` 이 아니다. 실제 프론트 도메인 목록만 적혀 있다.
- [ ] `allow_credentials=True` 를 쓰는 경우 `*` 와 함께 쓸 수 없음을 알고 있다 (구체적인 도메인 목록이 필수).

```python
# app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,   # 예: ["https://app.example.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 9.9.6 보안 헤더 (간단 요약)

브라우저에서 직접 호출되는 API 라면 다음이 도움 된다.

- **HSTS(`Strict-Transport-Security`)**: 한 번 HTTPS 로 들어온 클라이언트에게 "다음부터는 항상 HTTPS 로 와라" 를 강제. nginx 라면 `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;`.
- **secure cookies**: 인증을 쿠키로 한다면(이 가이드는 JWT 헤더지만, 만약 둔다면) `Secure`, `HttpOnly`, `SameSite=Lax` 또는 `Strict` 를 켠다.
- **`X-Content-Type-Options: nosniff`**, **`X-Frame-Options: DENY`** 같은 헤더는 nginx 측에서 한 번에 추가하는 게 깔끔하다.

```nginx
# /etc/nginx/sites-available/myapp 의 server 블록 안
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### 9.9.7 백업과 모니터링 (한 단락)

학습 단계에서 깊이 들어가지 않더라도 다음만큼은 의식해 둔다.

- **백업**: 관리형 DB(RDS, Render Postgres) 는 자동 일일 스냅샷이 기본 옵션. 직접 운영 Postgres 라면 `pg_dump` 를 cron 으로 돌리고, 결과물을 S3 같은 외부 스토리지에 둔다.
- **모니터링**: 작은 프로젝트라면 [UptimeRobot](https://uptimerobot.com/) 같은 무료 외부 핑 서비스가 가장 가성비가 좋다. `/health` 를 5분마다 핑하고 다운 시 메일·슬랙 알림.
- **에러 알림**: Sentry 무료 플랜이 입문 단계의 모든 사용 사례를 덮는다. `pip install sentry-sdk` + `sentry_sdk.init(dsn=...)` 한 번이면 모든 처리되지 않은 예외가 대시보드에 뜬다.

> **모니터링은 "있으면 좋은" 게 아니다.** 운영 첫날부터 `/health` 외부 핑과 에러 알림을 켜 두는 편이, 한 달 후의 디버깅 시간을 절반으로 줄인다.

---

## 9.10 GitHub Actions 로 가벼운 CI

배포 자체는 위 절차로 충분하지만, **푸시할 때마다 테스트와 린트를 자동으로 돌리는 작은 안전장치**를 한 번 깔아두면 큰 사고가 줄어든다.

`.github/workflows/ci.yml` 한 파일이면 끝.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6
        with:
          version: "0.5.7"

      - name: Set up Python
        run: uv python install 3.13

      - name: Sync dependencies
        run: uv sync --frozen

      - name: Lint with ruff
        run: uv run ruff check .

      - name: Run tests
        run: uv run pytest -q
        env:
          # 테스트는 in-memory SQLite 로
          DATABASE_URL: "sqlite+aiosqlite:///./test.db"
          JWT_SECRET: "ci-test-secret"
```

이 워크플로가 하는 일은 단순하다.

1. `main` 브랜치 푸시 또는 PR 시 트리거.
2. uv 설치 → Python 3.13 설치 → `uv sync --frozen`.
3. `ruff check` 로 린트.
4. `pytest -q` 로 테스트.

**5분 안에 결과가 나온다.** 실패하면 깃허브의 PR 화면에 빨간 X 가 뜨고, 머지 전에 고칠 기회가 생긴다.

> **CD(자동 배포) 는 어떻게?** Render·Fly.io 라면 그쪽이 이미 main 푸시 자동 배포를 해 주므로 CD 워크플로는 필요 없다. EC2/Ubuntu 라면 `appleboy/ssh-action` 같은 액션으로 SSH 후 `deploy.sh` 를 부르는 단계를 더 추가하면 된다. 이 가이드의 범위는 CI 까지.

> **CI 가 통과한 SHA 의 이미지에만 배포하기**: 더 본격 운영에서는 CI 단계에서 Docker 이미지를 빌드해 GHCR 같은 레지스트리에 푸시하고, 그 태그(예: `:sha-abc1234`) 를 **수동으로** 운영에 적용한다. 자동 배포보다 안전한 패턴이다.

---

## 9.11 트러블슈팅 — 자주 만나는 8가지

배포에서 자주 마주치는 문제와 해결법을 모았다. 한 번씩 쓱 읽고 머릿속 한 구석에 두면, 진짜로 마주쳤을 때 회복이 빠르다.

### 9.11.1 Docker 빌드가 `uv sync --frozen` 단계에서 실패한다

증상:

```
error: lockfile is missing or out of date
```

원인 두 가지 중 하나.

1. **`uv.lock` 이 git 에 안 올라가 있다.** `uv.lock` 은 빌드 재현성의 핵심이라 반드시 커밋해야 한다.
2. **`pyproject.toml` 을 손으로 고쳤는데 `uv lock` 을 안 돌려 lock 이 옛날 그대로다.** 로컬에서 `uv lock` 한 번 → 커밋 → 다시 푸시.

> **확인**: `git ls-files | grep uv.lock` 로 lock 이 git 에 들어 있는지 확인. `.gitignore` 에 실수로 `uv.lock` 을 넣어두지 않았는지도 본다.

### 9.11.2 컨테이너가 띄워졌는데 `curl /health` 가 응답이 없다

증상: `Empty reply from server` 또는 타임아웃.

자주 보는 원인.

- `Dockerfile` 의 `CMD` 에서 `-b 127.0.0.1:8000` 으로 바인딩했다. **컨테이너 안의 127.0.0.1 은 호스트에서 접근 불가**. 반드시 `-b 0.0.0.0:8000`.
- `EXPOSE 8000` 만 있고 `docker run -p 8000:8000` 의 `-p` 를 빠뜨렸다.
- `Dockerfile` 의 `app.main:app` 모듈 경로가 실제 파일과 다르다. 컨테이너 안에서 `python -c "from app.main import app"` 으로 임포트가 되는지 확인.

### 9.11.3 Gunicorn 워커가 부팅하자마자 죽는다

증상: 로그에 `[CRITICAL] WORKER TIMEOUT (pid:N)` 또는 `Worker (pid:N) was sent SIGKILL!` 이 반복.

흔한 원인.

- **워커 부팅 중에 import 가 너무 오래 걸린다.** 큰 ML 모델·외부 자원 초기화가 모듈 import 시점에 일어나면 `--timeout 60` 안에 부팅을 못 끝낸다. **부팅 부분을 `lifespan` 으로 옮기거나** `--timeout 120` 같이 일시적으로 늘린다.
- **메모리 부족(OOM).** 워커 수 × 워커당 메모리가 인스턴스 RAM 을 초과. 워커 수를 줄이거나 인스턴스를 키운다.
- **DB 연결 실패가 부팅 시 예외로 발생.** `lifespan` 에서 DB 핑이 실패하면 워커가 부팅을 포기한다. DB 가 떴는지부터 확인.

### 9.11.4 nginx 502 Bad Gateway

증상: 브라우저/`curl` 이 502 를 받음. nginx 의 에러 로그(`/var/log/nginx/error.log`) 에 `connect() failed (111: Connection refused)`.

원인은 거의 항상 **뒤쪽 앱이 안 떠 있는 것**이다.

```bash
sudo systemctl status myapp
sudo journalctl -u myapp -n 100 --no-pager

# 직접 8000 으로 응답이 오는지
curl -v http://127.0.0.1:8000/health
```

- 앱이 죽었으면 `systemctl restart myapp`.
- 떴는데도 502 면 **nginx 의 `proxy_pass` 포트와 앱의 바인드 포트가 다른 경우**. systemd 의 `ExecStart` 가 `-b 127.0.0.1:8001` 인데 nginx 가 `proxy_pass http://127.0.0.1:8000;` 면 안 만난다.

### 9.11.5 certbot 갱신이 실패한다

증상: `certbot renew --dry-run` 이 `Failed authorization procedure` 로 끝남.

흔한 원인.

- **80 포트가 막혀 있다.** Let's Encrypt 의 도메인 검증은 80 포트로 들어온다. 보안 그룹/방화벽에서 80 을 다시 열고 (또는 nginx 의 80 블록을 살려두고) 다시 시도.
- **DNS 가 다른 서버를 가리킨다.** A 레코드가 이 서버 IP 를 가리키는지 `dig api.example.com +short` 로 확인.
- **이미 인증서를 너무 자주 발급해서 rate limit 에 걸렸다.** 같은 도메인에 대해 1주에 5건, 60일에 50건 등의 한도가 있다. `--dry-run` 으로만 시험하다 정작 실제 발급에서 실패하면 며칠 기다려야 한다.

### 9.11.6 `psycopg` / `asyncpg` 관련 ImportError

증상: 컨테이너 안에서 `ImportError: no pq driver` 또는 `ModuleNotFoundError: asyncpg`.

원인 두 가지.

1. **드라이버를 의존성으로 추가하지 않았다.** `pyproject.toml` 의 dependencies 에 `asyncpg` 가 있는지 확인.
2. **시스템 패키지 `libpq5` 가 런타임 단계에 없다.** `Dockerfile` 의 런타임 단계에서 `apt-get install -y libpq5` 가 빠졌으면 추가.

### 9.11.7 `DATABASE_URL` 이 비어 있다 / 설정이 안 읽힌다

증상: 부팅 시 `pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings ... database_url Field required`.

원인.

- 환경 변수 이름의 대소문자 불일치. `pydantic-settings` 의 `case_sensitive=False` 가 안 켜져 있으면 `database_url` 만 인식하고 `DATABASE_URL` 은 무시할 수 있다.
- 플랫폼 UI 에 변수를 넣고 **재배포를 안 했다.** Render·Fly 모두 환경 변수 변경 후 새 배포가 필요하다.
- systemd 의 `EnvironmentFile=` 경로가 잘못됐다. `sudo systemctl status myapp` 로 활성 환경 변수를 확인.

### 9.11.8 Apple Silicon 맥에서 빌드한 이미지가 Linux 서버에서 `exec format error`

증상: ECS·EC2 의 amd64 환경에서 컨테이너가 부팅 직후 죽고, 로그에 `exec format error`.

원인: Apple Silicon(arm64) 에서 빌드한 이미지를 amd64 머신에 그대로 올린 것.

해결: 빌드 시 플랫폼을 명시.

```bash
docker buildx build --platform linux/amd64 -t todo-api:1.0 . --load
```

또는 **레지스트리에 push 할 때만** 멀티 아키텍처로:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/me/todo-api:1.0 . --push
```

> **간단한 회피**: Render·Fly 는 자체 빌더로 이미지를 빌드하므로 이 문제가 거의 안 보인다. 직접 푸시해서 운영에 띄우는 경로(EC2 / 자체 서버) 에서만 의식하면 된다.

---

## 9.12 이 챕터 요약

- 운영 서버는 `uvicorn --reload` 가 아니라 **Gunicorn + UvicornWorker** 한 줄로 띄운다. 워커 수는 코어 × (1~2) 에서 시작해 측정 후 조정한다.
- 어떤 배포 경로든 토대는 같다: **표준 멀티스테이지 `Dockerfile`** 하나(`python:3.13-slim` 베이스, uv 로 의존성 깐 뒤 비루트 유저로 gunicorn 실행) 와 **`.dockerignore`** 한 파일.
- 로컬 개발에서는 **`docker-compose.yml`** 로 앱 + PostgreSQL 을 한 번에 띄우고, `service_healthy` 로 부팅 순서를 안전하게 묶는다. 마이그레이션은 별도 일회성 컨테이너(`profile: tools`).
- **Render** 는 GitHub 연결만으로 5분 안에 배포 + HTTPS + 관리형 Postgres 까지 받을 수 있다. 마이그레이션은 Pre-Deploy Command 에 `alembic upgrade head` 한 줄.
- **Fly.io** 는 `flyctl` 로 모든 작업이 끝난다. `fly launch` → `fly secrets set` → `fly deploy`. 마이그레이션은 `release_command` 에 한 줄.
- **AWS EC2(t3.small)** 에 우분투를 깔고 Docker 만 설치한 뒤 `docker compose up -d` 로 띄우는 것이 입문에 가장 단순한 AWS 경로다. ECS·Fargate 는 학습 후 단계.
- **Ubuntu 직접 배포**는 `/srv/myapp/` 에 코드를 두고, **systemd 서비스 + nginx 리버스 프록시 + Let's Encrypt 자동 갱신**의 조합. 시스템 운영을 손에 익히는 가장 좋은 학습 경로.
- 어디든 빠뜨리면 안 되는 다섯 가지: **환경 변수 분리, 마이그레이션의 명시적 위치, `/health`, 표준 출력 기반 로그 + 적절한 레벨, HTTPS**. 이 다섯이 확보되면 나머지는 점진적으로 채워가도 안전하다.
- GitHub Actions 한 파일(`uv sync` + `ruff check` + `pytest`) 로 가벼운 CI 부터 깔아두면 사고 비율이 눈에 띄게 줄어든다.

<a id="ch10"></a>

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
SECRET_KEY=please-change-this

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
    secret_key: str = "please-change-this"
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

본 가이드의 예제 폴더는 보기 좋게 파일명을 **`0001_initial.py`**로 바꿔 두었습니다. 직접 따라하실 때도 이름을 바꾸셔도 됩니다(파일 안의 `revision = "..."` 식별자만 헷갈리지 않게).

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

전체 코드는 예제 폴더에 있습니다. 여기서는 **본인 소유 검사** 테스트를 발췌해 봅니다.

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

COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /usr/local/bin/

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
    PIP_DISABLE_PIP_VERSION_CHECK=1

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

CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", \
     "-b", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
```

각 부분을 풀어 봅니다.

- **`FROM python:3.13-slim AS builder`** — 빌드 단계. slim은 Debian 베이스에서 일부 도구를 제외한 가벼운 이미지.
- **`COPY --from=ghcr.io/astral-sh/uv:0.4.30 /uv /uvx /usr/local/bin/`** — uv 바이너리를 공식 이미지에서 가져옵니다. 버전을 박아두면 재현성이 좋아집니다.
- **`UV_SYSTEM_PYTHON=1`** — uv가 `.venv` 대신 컨테이너의 시스템 site-packages에 곧장 설치하도록. 컨테이너 안은 격리가 이미 충분해서 `.venv`를 또 만들 이유가 없습니다.
- **의존성 메타데이터를 먼저 복사**(`pyproject.toml`, `uv.lock`)한 뒤 의존성을 설치하고, **그 다음에 앱 소스를 복사**합니다. 이 순서가 Docker의 레이어 캐시를 가장 잘 활용합니다 — 코드만 바뀌면 의존성 설치 단계는 캐시되어 다시 안 돌아갑니다.
- **런타임 단계**는 더 깨끗합니다. uv도 빌드 결과물도 그대로 가져오지만 빌드 도구는 가져오지 않습니다.
- **`useradd ... app`** + **`USER app`** — 비루트 사용자를 만들고 그 사용자로 실행합니다. 컨테이너 안에서 root로 도는 프로세스는 컨테이너 탈출 취약점이 발견되면 호스트 root와 가까워지므로, 일반 사용자로 두는 게 표준입니다.
- **`CMD ["gunicorn", ...]`** — 운영용 실행. **Gunicorn으로 Uvicorn 워커 4개**를 띄웁니다. 개발 시에는 docker-compose에서 명령을 덮어씁니다.

> **왜 Gunicorn + Uvicorn 워커?** Uvicorn 단독으로는 한 프로세스로 동작합니다. 운영에서는 CPU 코어를 다 활용하기 위해 여러 워커를 띄우고, 워커 한 명이 죽으면 자동으로 재시작하는 매니저가 필요합니다. Gunicorn이 그 매니저 역할을 하고, 각 워커는 비동기 처리를 위해 `UvicornWorker` 클래스를 씁니다.

> **워커 수는 어떻게 정하나?** 일반적인 권장은 `(2 × CPU 코어) + 1`입니다. 1코어 환경이면 3, 2코어면 5. 위 Dockerfile은 4로 박아두었지만, 실제 배포 시 CPU 환경에 맞춰 조정하세요.

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
      SECRET_KEY: ${SECRET_KEY:-please-change-this}
      ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: "60"
      CORS_ALLOW_ORIGINS: "*"
    ports:
      - "8000:8000"
    command: >
      sh -c "alembic upgrade head && \
             gunicorn app.main:app \
               -k uvicorn.workers.UvicornWorker \
               -w 4 \
               -b 0.0.0.0:8000 \
               --access-logfile - --error-logfile -"

volumes:
  postgres-data:
```

새로운 부분만 짚습니다.

- **`app.build: .`** — 같은 폴더의 `Dockerfile`로 이미지를 빌드.
- **`depends_on: db: condition: service_healthy`** — db가 healthy가 된 뒤에야 app이 시작됩니다. `pg_isready`로 검증되므로 "DB가 아직 안 뜬 상태에서 마이그레이션이 실패하는" 사고를 막아 줍니다.
- **`environment.DATABASE_URL`** — 호스트가 `localhost`가 아니라 **`db`(서비스 이름)** 입니다. 같은 docker network 안에서는 서비스 이름이 곧 호스트입니다.
- **`environment.SECRET_KEY: ${SECRET_KEY:-...}`** — 셸의 `SECRET_KEY` 환경 변수가 있으면 그것을, 없으면 기본값을 쓴다는 뜻. 운영에서는 반드시 셸 또는 외부 비밀 관리자에서 주입.
- **`command: sh -c "alembic upgrade head && gunicorn ..."`** — 컨테이너 시작 시 마이그레이션을 한 번 적용한 뒤 Gunicorn을 실행. 운영에서는 마이그레이션을 별도 단계로 분리하는 것이 일반적이지만, 학습용으로는 한 줄로 묶어 두면 편합니다.

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
note-api-app  | [INFO] Listening at: http://0.0.0.0:8000 (1)
note-api-app  | [INFO] Using worker: uvicorn.workers.UvicornWorker
note-api-app  | [INFO] Booting worker with pid: 8
note-api-app  | [INFO] Booting worker with pid: 9
note-api-app  | [INFO] Booting worker with pid: 10
note-api-app  | [INFO] Booting worker with pid: 11
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
- [ ] **`SECRET_KEY`를 `please-change-this`로 두고 운영에 띄우지 않았는지** — `secrets.token_urlsafe(48)`로 만든 값으로.
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

- [ ] **운영에서는 `--reload` 플래그 사용 금지** — 파일 와처가 무겁고 불안정. Gunicorn + UvicornWorker만 사용.
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

<a id="ch11"></a>

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
uv add fastapi "uvicorn[standard]" gunicorn \
       sqlalchemy alembic asyncmy aiosqlite \
       pyjwt bcrypt python-slugify \
       pydantic-settings "pydantic[email]"

uv add --dev pytest pytest-asyncio httpx
```

각 라이브러리의 역할:

- **fastapi / uvicorn / gunicorn** — 웹 프레임워크와 ASGI 서버, 운영용 프로세스 매니저.
- **sqlalchemy / alembic / asyncmy** — ORM, 마이그레이션, MySQL 비동기 드라이버.
- **aiosqlite** — 테스트에서 인메모리 SQLite를 띄울 때 사용. 운영 코드는 MySQL.
- **pyjwt / bcrypt** — 08장에서 깐 그대로. JWT 발급·검증, 비밀번호 해싱.
- **python-slugify** — `"FastAPI 시작하기"` 같은 제목을 `"fastapi"` 같은 URL-safe 문자열로 바꿔 줍니다(11.7에서 사용).
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
SECRET_KEY=please-change-this
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
    secret_key: str = "please-change-this"
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

COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /usr/local/bin/

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

WORKDIR /app
COPY --from=builder /app /app

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "2", "-b", "0.0.0.0:8000"]
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
- 앱은 **Web Service**로 배포. 빌드 명령은 `uv sync --frozen --no-dev`, 시작 명령은 `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT -w 2`.
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

- [ ] `uv add fastapi "uvicorn[standard]" gunicorn "sqlalchemy[asyncio]" alembic asyncmy aiosqlite pyjwt bcrypt python-slugify pydantic-settings "pydantic[email]"` 설치 완료
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

<a id="ch12"></a>

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

[[tool.mypy.overrides]]
module = ["fastapi.*", "starlette.*"]
ignore_missing_imports = false
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
    password_hash: Mapped[str] = mapped_column(String(60))
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

`alembic/env.py`에서 비동기 엔진을 쓰려면:

```python
from sqlalchemy.ext.asyncio import async_engine_from_config

def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
    )
    async def do_run():
        async with connectable.connect() as conn:
            await conn.run_sync(do_run_migrations)
    asyncio.run(do_run())
```

자세한 템플릿은 06장과 10장 종합 예제에서 다뤘습니다.

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
    decoded = jwt.decode(token, SECRET, algorithms=[ALGO])
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
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.fixture
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

- 운영 환경에서는 `gunicorn -k uvicorn.workers.UvicornWorker`처럼 워커를 여러 개 띄우는 게 일반적입니다(12.55 참고).

---

## O. 운영 라이브러리

## 12.55 Gunicorn (UvicornWorker)

> **한 줄**: Uvicorn 워커를 여러 프로세스로 띄워 부하를 분산하는 운영용 프로세스 매니저.
> **버전 (2026-04 기준)**: 23.x
> **설치**: `uv add gunicorn`
> **공식**: https://gunicorn.org/

### 왜 쓰는가

Uvicorn 한 프로세스로는 단일 CPU만 활용합니다. Gunicorn으로 여러 프로세스를 띄우면 GIL 한계를 우회해 멀티코어를 사용합니다.

### 명령

```bash
uv run gunicorn app.main:app \
    -k uvicorn.workers.UvicornWorker \
    -w 4 \
    -b 0.0.0.0:8000 \
    --access-logfile - \
    --error-logfile -
```

- `-k`: 워커 클래스. UvicornWorker가 ASGI 앱을 처리.
- `-w 4`: 워커 4개. 보통 `(2 * CPU 코어) + 1`이 출발점.
- `-b`: 바인드 주소.
- `--access-logfile -`: 표준 출력으로 액세스 로그 (Docker 친화적).

### 자주 쓰는 패턴: 컨테이너화

Dockerfile에서:

```dockerfile
CMD ["gunicorn", "app.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "4", "-b", "0.0.0.0:8000"]
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

<a id="glossary"></a>

# 부록 A — 용어 사전 (Glossary)

> **이 문서의 목적**
> 가이드 전체에서 등장하는 백엔드·웹·Python 용어를 한 곳에 모아 빠르게 찾아볼 수 있게 했습니다. 처음부터 다 외울 필요는 없습니다 — 모르는 단어가 나오면 이 페이지를 펼쳐 한두 줄만 읽고 본문으로 돌아오시면 됩니다.

용어는 **주제별**로 묶었습니다. 알파벳순이 아닙니다. 같은 주제 안에서는 자주 쓰이는 순서로 배치했습니다.

- [1. 웹과 HTTP 기본](#1-웹과-http-기본)
- [2. Python 언어와 실행 환경](#2-python-언어와-실행-환경)
- [3. 프레임워크와 아키텍처](#3-프레임워크와-아키텍처)
- [4. 데이터베이스](#4-데이터베이스)
- [5. 인증과 보안](#5-인증과-보안)
- [6. 이 가이드에서 쓰는 도구·라이브러리](#6-이-가이드에서-쓰는-도구라이브러리)
- [7. 운영과 배포](#7-운영과-배포)

---

## 1. 웹과 HTTP 기본

### HTTP (HyperText Transfer Protocol)

웹에서 클라이언트(브라우저, 모바일 앱)와 서버가 데이터를 주고받기 위해 합의한 약속(프로토콜)입니다. "이런 형식으로 요청을 보내면, 이런 형식으로 응답을 돌려준다"는 규칙의 묶음입니다. 우리가 만드는 백엔드는 거의 다 이 HTTP 위에서 동작합니다.

### HTTP 메서드 (HTTP Method)

요청이 무엇을 하려고 하는지 표현하는 동사입니다. 자주 쓰는 다섯 가지:

- **GET** — 자료를 가져옴 (예: 사용자 목록 조회)
- **POST** — 새 자료를 만듦 (예: 회원가입)
- **PUT** — 자료를 통째로 덮어씀 (예: 글 전체 수정)
- **PATCH** — 자료의 일부만 바꿈 (예: 글의 제목만 수정)
- **DELETE** — 자료를 지움 (예: 회원 탈퇴)

### HTTP 상태 코드 (HTTP Status Code)

응답이 어떻게 됐는지 알려주는 세 자리 숫자입니다.

- **200 OK** — 잘 처리됨
- **201 Created** — 새로 만들어짐 (POST의 성공)
- **204 No Content** — 잘 처리됐는데 돌려줄 본문이 없음 (DELETE의 성공)
- **400 Bad Request** — 클라이언트가 보낸 요청이 잘못됨
- **401 Unauthorized** — 로그인이 필요함
- **403 Forbidden** — 로그인은 했는데 권한이 없음
- **404 Not Found** — 자료가 없음
- **422 Unprocessable Entity** — 요청 형식은 맞는데 값이 검증을 통과 못 함 (FastAPI가 자주 돌려줌)
- **500 Internal Server Error** — 서버에 문제가 생김

### URL과 경로 / 쿼리 스트링

`https://api.example.com/users/42?format=json` 같은 주소에서:
- `https://` — 통신 방식(스킴)
- `api.example.com` — 호스트(도메인)
- `/users/42` — **경로(path)**: 어떤 자원을 가리키는지
- `?format=json` — **쿼리 스트링(query string)**: 추가 옵션. `key=value` 형태로 여러 개를 `&`로 이음

### 요청 헤더 / 응답 헤더 (Headers)

본문(body)과 별개로 붙는 메타 정보입니다. `Content-Type: application/json`(본문은 JSON이다), `Authorization: Bearer xxx`(이게 내 인증 토큰이다) 같은 것들이 헤더입니다.

### 쿠키 (Cookie)

서버가 브라우저에 저장해 두라고 보낸 작은 문자열입니다. 다음 요청부터 브라우저가 자동으로 쿠키를 함께 보내줍니다. 옛날 웹에서 로그인 상태 유지에 주로 썼습니다. 이 가이드의 인증은 쿠키 대신 JWT를 씁니다.

### JSON (JavaScript Object Notation)

자료를 글자로 표현하는 가장 흔한 형식입니다. Python의 dict와 거의 비슷하게 생겼습니다.

```json
{
  "id": 42,
  "name": "Alice",
  "roles": ["user", "admin"]
}
```

### REST / RESTful

웹 API를 설계할 때 자주 따르는 약속의 이름입니다. 핵심 원칙은 두 가지입니다.
1. **자원을 URL로 가리킨다** (예: 게시글 42번 = `/posts/42`)
2. **동작은 HTTP 메서드로 표현한다** (조회는 GET, 만들기는 POST 등)

이 약속을 잘 지킨 API를 "RESTful 하다"고 말합니다. FastAPI는 RESTful API를 만들기에 매우 적합합니다.

### CORS (Cross-Origin Resource Sharing)

브라우저는 보안상 "현재 페이지가 떠 있는 도메인"과 다른 도메인의 API를 마음대로 부르지 못하게 막아둡니다. 그 차단을 풀어주는 약속이 CORS입니다. 백엔드에서 "이 도메인은 허용한다"는 헤더를 응답에 붙여줍니다. FastAPI는 `CORSMiddleware`로 한 줄에 처리합니다.

### 클라이언트 / 서버 / 프론트엔드 / 백엔드

- **클라이언트(client)**: 데이터를 요청하는 쪽. 브라우저, 모바일 앱, 또 다른 서버.
- **서버(server)**: 요청을 받고 응답을 돌려주는 쪽.
- **프론트엔드(frontend)**: 사용자에게 직접 보이는 화면을 그리는 부분 (HTML, React, 모바일 앱 등).
- **백엔드(backend)**: 화면 뒤에서 동작하는 서버 프로그램. **이 가이드가 만드는 그것.**

---

## 2. Python 언어와 실행 환경

### 가상환경 (Virtual Environment)

프로젝트마다 라이브러리를 격리해 두는 작은 "독립된 Python 공간"입니다. A 프로젝트는 SQLAlchemy 1.4를, B 프로젝트는 SQLAlchemy 2.0을 써야 할 때, 가상환경 없이 시스템 Python에 둘 다 깔면 충돌합니다. `uv venv`나 `python -m venv .venv`로 만들고, `.venv/bin/activate`로 켭니다.

### 패키지 매니저 (Package Manager)

라이브러리를 받아 설치·삭제·잠금(lock)해 주는 도구입니다. Python에는 두 가지를 알면 됩니다:
- **`pip`** — 표준 도구. 모든 환경에 깔려 있음.
- **`uv`** — 같은 일을 10~100배 빠르게 하는 차세대 도구. 이 가이드의 권장 도구.

### `pip` 와 `uv` 의 관계

같은 일을 하는 두 도구입니다. 명령어가 거의 1:1로 대응됩니다.

| 작업 | `pip`/`venv` | `uv` |
|------|-------------|------|
| 가상환경 만들기 | `python -m venv .venv` | `uv venv` |
| 라이브러리 설치 | `pip install fastapi` | `uv pip install fastapi` (또는 `uv add fastapi`) |
| 잠금 파일 | `requirements.txt` | `uv.lock` (자동) |
| 속도 | 느림 | 매우 빠름 |

### 데코레이터 (Decorator)

함수 위에 `@`로 붙는 표시입니다. "이 함수에 추가 기능을 입혀라"는 의미입니다.

```python
@app.get("/hello")        # ← 이게 데코레이터
def hello():
    return "Hi"
```

위 코드는 "`hello` 함수를 GET `/hello` 요청 처리기로 등록해라"는 뜻입니다. FastAPI 라우팅의 기본 단위입니다.

### 타입 힌트 (Type Hint)

변수와 함수 인자·반환값에 "이건 이런 타입이다"라고 적어주는 표기입니다.

```python
def add(x: int, y: int) -> int:
    return x + y
```

Python은 런타임에 이 타입을 강제하지 않지만, FastAPI/Pydantic은 타입 힌트를 읽어서 **자동으로 검증**합니다.

### 비동기 / 동기 (async / sync)

- **동기(sync)**: 한 줄을 끝내야 다음 줄로 갑니다. DB 호출이 0.5초 걸리면, 그 0.5초 동안 다른 일을 못 합니다.
- **비동기(async)**: 기다림이 생기면 잠시 비키고 다른 일을 처리합니다. `await` 키워드로 "여기서 기다린다"고 표시합니다.

```python
# 동기
def get_user(id):
    user = db.find(id)   # 여기서 0.5초 멈춤
    return user

# 비동기
async def get_user(id):
    user = await db.find(id)  # 기다리는 동안 다른 요청 처리 가능
    return user
```

백엔드는 기다리는 일이 많아서 비동기가 큰 효과를 냅니다.

### 동시성 (Concurrency) / 병렬성 (Parallelism)

- **동시성**: 여러 일을 "번갈아가며" 처리. CPU 코어가 한 개여도 가능. (비동기로 달성)
- **병렬성**: 여러 일을 "정말 동시에" 처리. CPU 코어가 여러 개여야 가능. (멀티프로세스로 달성)

### GIL (Global Interpreter Lock)

CPython 구현의 특성상, **한 프로세스 안의 여러 스레드가 동시에 Python 코드를 실행할 수 없습니다.** 이게 GIL입니다. 백엔드에서는 보통 비동기(I/O가 많으면 효과적) 또는 여러 프로세스(Gunicorn 워커) 띄우기로 해결합니다.

### ASGI (Asynchronous Server Gateway Interface)

비동기 Python 웹 앱과 서버 사이의 표준 약속입니다. FastAPI는 ASGI 앱이고, Uvicorn은 ASGI 서버입니다. 이 둘은 ASGI 약속을 통해 대화합니다.

### WSGI (Web Server Gateway Interface)

ASGI의 옛 버전(동기). 옛날 Django와 Flask가 썼습니다. 이 가이드에서는 거의 등장하지 않습니다.

### 코루틴 (Coroutine)

`async def`로 정의된 함수를 부르면 곧장 실행되지 않고, 일단 "곧 실행될 약속" 객체가 만들어집니다. 이 객체가 코루틴입니다. `await`로 그 코루틴이 끝날 때까지 기다리거나, 이벤트 루프가 알아서 처리합니다.

---

## 3. 프레임워크와 아키텍처

### 프레임워크 / 라이브러리

- **라이브러리(library)**: 우리가 부르는 도구. 우리가 흐름을 통제함.
- **프레임워크(framework)**: 흐름을 정해두고, 우리는 빈 칸을 채우는 형태. "Don't call us, we'll call you."

FastAPI는 프레임워크입니다. SQLAlchemy는 라이브러리입니다.

### 라우팅 / 라우트 / 엔드포인트

- **라우팅(routing)**: 요청 URL을 어느 함수가 처리할지 결정하는 과정.
- **라우트(route)**: "이 URL은 이 함수가 처리한다"는 등록 정보 한 건.
- **엔드포인트(endpoint)**: 한 라우트가 노출하는 외부 접점. 보통 `URL + HTTP 메서드` 한 쌍을 가리킵니다(예: `GET /users`).

### 미들웨어 (Middleware)

요청과 응답 사이에 "끼어드는" 코드입니다. 모든 요청이 들어오기 전에·나가기 전에 한 번씩 거치는 검문소 같은 것. 로깅, 인증 검사, CORS 헤더 추가, 요청 시간 측정 등이 미들웨어로 구현됩니다.

### 의존성 주입 (Dependency Injection, DI)

함수가 "동작하려면 이게 필요하다"고 인자로 선언만 하면, 프레임워크가 알아서 그 값을 만들어 넣어주는 패턴입니다. FastAPI에서는 `Depends(...)`로 표현합니다.

```python
@app.get("/me")
def me(user: User = Depends(get_current_user)):
    # user는 FastAPI가 알아서 주입
    return user
```

### 컨트롤러 / APIRouter / 서비스 레이어

- **APIRouter (FastAPI 용어)**: 여러 라우트를 한 모듈로 묶는 객체. 다른 프레임워크의 "컨트롤러"에 해당.
- **서비스 레이어 (Service Layer)**: 실제 비즈니스 로직을 담는 함수·클래스. 라우터가 너무 두꺼워지면 서비스로 분리하는 게 관례입니다.

### MVC / MVT

웹 백엔드 코드를 "데이터(M) / 화면(V) / 흐름 제어(C)" 세 부분으로 나누자는 옛 패턴. Django는 MVT(Model-View-Template)라고 부르지만 비슷한 개념입니다. **이 가이드의 FastAPI는 화면(V)이 없는 REST API라서 MVC 용어를 거의 쓰지 않습니다** — 대신 라우터/서비스/모델로 부릅니다.

### REPL

"Read-Eval-Print Loop"의 약자. 한 줄씩 입력하면 곧장 결과가 나오는 대화형 환경. 터미널에 `python` 또는 `ipython`을 치면 들어갑니다.

---

## 4. 데이터베이스

### 데이터베이스 / DBMS

- **데이터베이스(DB)**: 자료를 모아둔 저장소.
- **DBMS(Database Management System)**: 그 저장소를 다루는 프로그램. PostgreSQL, MySQL, SQLite 등이 DBMS입니다.

### 관계형 DB / NoSQL

- **관계형 DB (RDBMS)**: 자료를 표(테이블) 형태로 저장. SQL로 다룹니다. PostgreSQL, MySQL, SQLite, Oracle.
- **NoSQL**: 표가 아닌 다른 형태(문서, 키-값, 그래프 등). MongoDB, Redis, DynamoDB.

이 가이드는 관계형 DB만 다룹니다.

### SQL (Structured Query Language)

관계형 DB를 다루는 표준 언어입니다.

```sql
SELECT * FROM users WHERE email = 'a@b.com';
```

### 테이블 / 행(Row) / 열(Column)

- **테이블(table)**: 자료를 표 형태로 모은 단위. 예: `users` 테이블.
- **행(row, record)**: 표의 가로줄 하나. 한 사용자에 해당.
- **열(column, field)**: 표의 세로줄 하나. `email`, `password_hash` 같은 속성.

### 기본 키 (Primary Key, PK)

각 행을 고유하게 가리키는 열. 보통 `id`라는 정수 자동 증가 열을 씁니다.

### 외래 키 (Foreign Key, FK)

다른 테이블의 PK를 가리키는 열. "이 글의 작성자(`user_id`)는 사용자 테이블의 그 사람"이라는 연결을 표현합니다.

### 인덱스 (Index)

자주 검색하는 열에 미리 만들어 두는 "찾아보기" 자료구조입니다. `SELECT ... WHERE email = ?` 같은 쿼리를 빠르게 합니다. 만들면 빨라지지만 디스크와 쓰기 비용이 듭니다.

### 트랜잭션 (Transaction)

"여러 SQL을 한 묶음으로 실행하고, 도중에 실패하면 모두 되돌린다"는 단위입니다. 송금이 대표적: A에서 빼고 B에 더하는 두 SQL이 둘 다 성공하거나 둘 다 취소되어야 합니다. SQLAlchemy 세션이 트랜잭션을 자동으로 관리합니다.

### 마이그레이션 (Migration)

DB의 표 구조 변경(열 추가, 표 새로 만들기 등)을 코드로 기록·실행하는 작업입니다. Alembic이 그 도구입니다. 변경 이력이 파일로 남아 팀원이 같은 순서로 적용할 수 있습니다.

### ORM (Object Relational Mapper)

DB 표와 Python 클래스를 자동 연결해 주는 도구입니다. SQL을 직접 쓰지 않고 `await session.get(User, 1)` 같은 Python 코드로 DB를 다룹니다. 이 가이드는 SQLAlchemy 2.0을 씁니다.

### 세션 (Session) — DB 세션

ORM이 한 묶음의 DB 작업을 처리하는 단위입니다. 한 요청 안에서 세션 하나를 만들고, 끝날 때 닫습니다. (인증의 "세션"과는 다른 단어입니다.)

### 커넥션 풀 (Connection Pool)

DB 연결을 매번 새로 만드는 건 비싸기 때문에, 미리 N개를 만들어두고 재사용하는 방식입니다. SQLAlchemy가 자동으로 관리합니다.

### 1:N / N:M 관계

- **1:N (one-to-many)**: 한 사용자가 여러 글을 쓴다(`user.posts`).
- **N:M (many-to-many)**: 한 글에 여러 태그, 한 태그가 여러 글에 붙는다(`post.tags`).

11장 Blog API에서 본격적으로 다룹니다.

### N+1 문제

목록을 가져온 다음(N개), 각 항목마다 또 쿼리를 1번씩 더 날려서 총 N+1번 쿼리가 나가는 비효율 패턴입니다. SQLAlchemy의 `selectinload`/`joinedload`로 해결합니다.

---

## 5. 인증과 보안

### 인증 (Authentication, AuthN)

"당신이 누구인지 확인하는 절차"입니다. 보통 이메일+비밀번호로 로그인하는 단계.

### 인가 (Authorization, AuthZ)

"이 사람이 이 동작을 할 권한이 있는지 확인하는 절차"입니다. 로그인은 했는데 다른 사람의 글을 지우려 하면 인가 단계에서 막아야 합니다.

### 세션 (Session) — 인증의 세션

서버가 "이 사용자는 로그인 상태다"라는 사실을 자기 메모리/DB에 기록해 두고, 그 식별자(세션 ID)를 쿠키로 클라이언트에 전달하는 방식입니다. (DB의 세션과 단어는 같지만 의미가 다릅니다.) 옛날 웹에서 흔했고, 지금도 콘텐츠 관리 사이트에서 자주 씁니다.

### JWT (JSON Web Token)

서버가 "당신이 누구인지" 정보를 담아 서명한 작은 문자열입니다. 클라이언트는 이 문자열을 들고 다니다가 요청마다 헤더(`Authorization: Bearer xxx`)에 실어 보냅니다. 서버는 서명만 검증하면 되어, **DB 조회 없이도 누가 보낸 요청인지 알 수 있습니다.** 모바일 앱·SPA·외부 API 인증에 자주 씁니다. 08장에서 자세히 다룹니다.

### Bearer 토큰

`Authorization: Bearer <토큰>` 형태로 보내는, "이 토큰을 들고 있는 사람을 일단 그 사용자로 인정한다"는 표준 패턴입니다. JWT가 가장 흔한 Bearer 토큰입니다.

### OAuth2

"내가 직접 비밀번호를 넘기지 않고도, A 서비스가 B 서비스의 일부 권한을 빌릴 수 있게 하는" 표준 흐름입니다. "구글 로그인", "카카오 로그인"의 뼈대입니다. 이 가이드는 OAuth2의 "Password Flow" 변형(=서버가 직접 비번을 받아 토큰 발급)만 사용합니다 — 진짜 OAuth2 외부 로그인은 다루지 않습니다.

### 비밀번호 해싱 / Bcrypt / Salt

비밀번호를 평문 그대로 저장하면 DB가 털릴 때 큰 사고입니다. 그래서 **한 방향 함수**(되돌릴 수 없는 변환)로 바꿔서 저장합니다.

- **해싱(hashing)**: 평문 → 고정 길이 문자열로 변환. 같은 입력에는 항상 같은 출력.
- **Bcrypt**: 비밀번호용으로 설계된 해싱 알고리즘. 일부러 느리게 만들어 무차별 공격을 어렵게 합니다.
- **Salt**: 같은 비밀번호라도 사용자마다 다른 결과가 나오도록 함께 섞는 임의의 값. Bcrypt는 이 salt를 자동으로 다룹니다.

### HTTPS / TLS

HTTP 위에 암호화 층(TLS)을 씌운 것이 HTTPS입니다. 클라이언트와 서버 사이가 도청·변조 당하지 않습니다. **운영 환경의 모든 백엔드는 HTTPS를 써야 합니다.** 09장 배포에서 다룹니다.

### CSRF / XSS

- **CSRF(Cross-Site Request Forgery)**: 로그인된 사용자의 브라우저를 속여 의도하지 않은 요청을 보내게 하는 공격. 쿠키 기반 세션이 주요 표적이며, JWT/헤더 기반 인증은 비교적 안전합니다.
- **XSS(Cross-Site Scripting)**: 화면에 악성 스크립트를 삽입해 다른 사용자의 브라우저에서 실행시키는 공격. 주로 프론트엔드 영역. 우리 백엔드에서는 자료를 그대로 받아 그대로 돌려주지 말고 검증·이스케이프해야 합니다.

---

## 6. 이 가이드에서 쓰는 도구·라이브러리

### FastAPI

이 가이드의 주인공인 비동기 Python 웹 프레임워크. 타입 힌트를 적극 활용해 자동 검증·자동 API 문서를 제공합니다.

### Pydantic

요청·응답 스키마(데이터 모양)를 클래스로 정의하면 자동으로 타입 검증·JSON 변환·문서 생성까지 해주는 라이브러리입니다. FastAPI의 데이터 처리는 거의 다 Pydantic이 담당합니다. 현재 v2.x.

```python
from pydantic import BaseModel
class UserCreate(BaseModel):
    email: str
    password: str
```

### SQLAlchemy

Python에서 가장 널리 쓰이는 ORM입니다. 이 가이드는 v2.0의 비동기(async) API를 씁니다. 표를 클래스로 매핑하고, 쿼리도 Python 코드로 작성합니다.

### Alembic

SQLAlchemy와 짝지어 쓰는 마이그레이션 도구. "DB 표 구조를 이렇게 바꿔라"라는 변경 사항을 파일로 만들어 관리·실행합니다.

### Uvicorn

FastAPI 앱을 실제로 실행해 주는 ASGI 서버. 개발용으로는 `uvicorn app.main:app --reload` 한 줄로 충분합니다.

### Gunicorn

운영 환경에서 Uvicorn을 여러 개 띄워 부하를 분산해 주는 프로세스 매니저. 보통 `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4` 식으로 씁니다.

### uv

Astral 사가 만든 Python 패키지 매니저 + 가상환경 도구. `pip` + `venv` + `pip-tools`를 한 번에 대체합니다. 매우 빠릅니다. 이 가이드의 권장 도구.

### PyJWT

JWT 토큰을 만들고 검증하는 Python 라이브러리. 08장에서 직접 사용합니다.

### bcrypt (라이브러리)

위에서 설명한 Bcrypt 해싱 알고리즘의 Python 구현 라이브러리. `bcrypt.hashpw()`, `bcrypt.checkpw()` 두 함수가 핵심입니다.

### OpenAPI / Swagger UI / ReDoc

- **OpenAPI**: REST API의 명세를 JSON/YAML로 적는 표준 형식. 옛 이름은 Swagger.
- **Swagger UI**: OpenAPI 명세를 보고 인터랙티브하게 테스트할 수 있는 웹 페이지. FastAPI는 자동으로 `/docs`에 띄워줍니다.
- **ReDoc**: 같은 명세를 더 깔끔한 읽기 전용 문서로 보여주는 웹 페이지. FastAPI는 자동으로 `/redoc`에 띄워줍니다.

### httpx / pytest

- **httpx**: 비동기 HTTP 클라이언트. 외부 API 호출이나 테스트에서 사용.
- **pytest**: Python 테스트 표준 도구. FastAPI의 `TestClient`와 함께 씁니다.

### ruff / mypy

- **ruff**: Astral의 매우 빠른 린터·포매터. (옛 `flake8` + `black` + `isort`를 한 번에)
- **mypy**: 타입 힌트를 정적으로 검사하는 도구.

12장 레퍼런스에서 더 다룹니다.

---

## 7. 운영과 배포

### 환경 변수 / `.env` 파일

비밀번호·DB 접속 정보 같이 코드에 박으면 안 되는 값을 운영체제 환경 변수로 둡니다. 개발 중에는 `.env` 파일에 적고, `pydantic-settings` 같은 도구가 그 파일을 읽어 앱에 주입합니다. **`.env` 파일은 절대 git에 커밋하지 않습니다.**

### 컨테이너 / Docker / 이미지

- **컨테이너(container)**: 앱을 OS 환경째 잘라내 어디서나 똑같이 실행할 수 있게 묶은 단위.
- **이미지(image)**: 컨테이너의 "설계도". 정적 파일.
- **Docker**: 가장 널리 쓰는 컨테이너 도구.

09장 배포에서 본격적으로 다룹니다.

### Docker Compose

여러 컨테이너(앱 + DB + Redis 등)를 한 YAML 파일로 묶어 함께 띄우는 도구입니다. 개발 환경에서 매우 유용합니다.

### 헬스 체크 (Health Check)

운영 환경의 로드밸런서·오케스트레이터가 "이 앱이 살아있나?"를 주기적으로 확인하는 용도의 단순 엔드포인트입니다. 보통 `GET /health`로 만들고, OK 상태면 200을 돌려줍니다.

### 로그 (Log)

앱이 뱉는 운영용 메시지. 어떤 요청이 언제 들어왔는지, 어떤 에러가 났는지가 로그로 남아야 디버깅이 가능합니다. `print` 대신 `logging` 모듈 또는 `structlog`를 씁니다(12장).

### systemd / nginx / 리버스 프록시

- **systemd**: 리눅스에서 백그라운드 프로세스(데몬)를 관리하는 표준 도구. 우리 FastAPI 앱을 systemd 서비스로 등록하면 서버가 부팅될 때 자동 실행됩니다.
- **nginx**: 가장 많이 쓰이는 웹 서버. 우리 앱 앞에 두고 HTTPS 처리·정적 파일 서빙·로드 분산을 맡깁니다.
- **리버스 프록시(reverse proxy)**: 클라이언트의 요청을 일단 받아서 뒤쪽 진짜 앱 서버에 전달하는 중계자. 위의 nginx 역할이 그것.

09장 Ubuntu 배포 절에서 직접 설정해 봅니다.

### 도메인 / DNS

- **도메인(domain)**: 사람이 읽기 좋은 서버 주소. 예: `api.example.com`.
- **DNS**: 도메인을 실제 IP 주소로 바꿔주는 시스템.

### TLS / SSL 인증서

HTTPS를 쓰려면 도메인에 대해 발급받는 작은 파일이 필요합니다. 보통 무료인 Let's Encrypt를 써서 `certbot` 명령으로 자동 갱신합니다. 09장에서 다룹니다.

### CI / CD

- **CI(Continuous Integration)**: 코드를 푸시할 때마다 테스트·린트를 자동으로 돌리는 흐름.
- **CD(Continuous Deployment)**: 그 결과가 통과하면 자동으로 배포까지 하는 흐름.

이 가이드에서는 GitHub Actions를 활용한 매우 짧은 예시만 다룹니다.
