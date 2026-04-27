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

---

← [07. CRUD 예제](07-crud-example.md) | 다음 문서로 이동: **[09. 배포 가이드 →](09-deployment.md)**
