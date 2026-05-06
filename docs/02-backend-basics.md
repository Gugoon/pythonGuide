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
| `OPTIONS` | 허용 메서드 조회 | `CORSMiddleware` 등록 시 CORS preflight 자동 처리(미들웨어 없으면 일반 라우트엔 405) | 없음 |

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
> - 403: "이 동작은 허용되지 않아." (엄밀히는 인증 여부와 무관하게 서버가 거부하는 상태이며, 흔히 "인증은 됐지만 권한 없음" 케이스로 쓰입니다)

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
- 서명 덕분에 **위조는 거의 불가능**하지만, **훔치면 그대로 통과**되므로 HTTPS가 필수입니다. 단, 라이브러리 사용 시 알고리즘을 명시적으로 고정(`algorithms=["HS256"]`)하지 않으면 `alg: none` 우회 같은 잘 알려진 함정에 노출될 수 있습니다(08장 참고).
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

> **bcrypt 의 72바이트 함정**: bcrypt 는 입력을 72바이트로 잘라 처리합니다. 한국어는 UTF-8 기준 글자당 3바이트라 24글자 근처에서 잘리기 시작하고, 그 이후 글자를 바꿔도 같은 해시가 나옵니다. 더 모던한 대안으로 **Argon2id**(2015 PHC 우승)가 있으며, OWASP 도 새 시스템에는 Argon2id 를 권장합니다. 본 가이드는 학습 단순성을 위해 bcrypt 4.x 직접 사용을 표준으로 두고, 08장에서 길이 사전 검증으로 함정을 막습니다.

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

> **출처(origin)란?** 스킴(`https`) + 호스트(`example.com`) + 포트(생략 시 기본 포트로 간주: http=80, https=443)의 조합입니다. 셋 중 하나라도 다르면 다른 출처입니다. `https://a.com`과 `https://b.com`은 호스트가 달라서 다른 출처, `https://a.com`과 `http://a.com`도 스킴이 달라서 다른 출처입니다.

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

---

← [01. FastAPI 소개](01-introduction.md) | 다음 문서로 이동: **[03. 설치 가이드 →](03-installation.md)**
