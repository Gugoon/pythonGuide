# 용어 사전 (Glossary)

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

CPython 구현의 특성상, **한 프로세스 안의 여러 스레드가 동시에 Python 코드를 실행할 수 없습니다.** 이게 GIL입니다. 백엔드에서는 보통 비동기(I/O가 많으면 효과적) 또는 여러 프로세스(워커) 띄우기로 해결합니다. (Python 3.13 에 PEP 703 free-threaded 빌드가 실험적으로 도입됐지만, 일반 배포본은 여전히 GIL 이 활성입니다.)

### ASGI (Asynchronous Server Gateway Interface)

비동기 Python 웹 앱과 서버 사이의 표준 약속입니다. FastAPI는 ASGI 앱이고, Uvicorn은 ASGI 서버입니다. 이 둘은 ASGI 약속을 통해 대화합니다.

### WSGI (Web Server Gateway Interface)

동기 Python 웹 앱과 서버 사이의 표준 약속(ASGI 의 동기 버전). 지금도 Flask 와 Django 의 기본은 WSGI 이며, 비동기 처리에는 ASGI(Starlette/FastAPI/Django Channels)가 쓰입니다. 본 가이드는 ASGI 만 다룹니다.

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

"내가 직접 비밀번호를 넘기지 않고도, A 서비스가 B 서비스의 일부 권한을 빌릴 수 있게 하는" 표준 흐름입니다. "구글 로그인", "카카오 로그인"의 뼈대입니다. 이 가이드는 OAuth2의 "Password Flow"(Resource Owner Password Credentials Grant) 변형(=서버가 직접 비번을 받아 토큰 발급)만 사용합니다 — 진짜 OAuth2 외부 로그인은 다루지 않습니다.

> **Password Flow 는 표준에서 폐기 권고**: OAuth 2.1 초안에서 Resource Owner Password Credentials Grant 는 사실상 deprecated 되었습니다. FastAPI 의 `OAuth2PasswordBearer` 는 명세 차용일 뿐 진짜 OAuth2 인가가 아닙니다 — JWT 발급/검증의 형태만 빌려 쓰는 단일 서버용 패턴으로 이해하면 됩니다.

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

여러 워커 프로세스로 ASGI 앱을 굴려 주는 운영용 프로세스 매니저. 본 가이드 기준 권장은 **Uvicorn 자체 멀티워커**(`uvicorn ... --workers N --proxy-headers`)이고, Gunicorn 의 graceful reload 등이 꼭 필요할 때만 별도 패키지 `uvicorn-worker` 를 추가해 `gunicorn app.main:app -k uvicorn_worker.UvicornWorker -w 4` 형태로 씁니다(옛 `uvicorn.workers.UvicornWorker` 는 deprecated 되어 0.31 에서 분리됐습니다).

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

---

← [README로 돌아가기](../README.md)
