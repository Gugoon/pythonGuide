# 08-AuthExample — FastAPI 가이드 08장 예제

회원가입·로그인·보호된 라우트가 동작하는 작은 FastAPI 백엔드입니다.
본문은 [docs/08-authentication.md](../../docs/08-authentication.md)를 참고하세요.

## 핵심 기능

- `POST /auth/signup` — 이메일+비밀번호로 회원가입 (Bcrypt 해싱 저장)
- `POST /auth/login` — 로그인 후 JWT 액세스 토큰 발급 (form-encoded)
- `GET /users/me` — `Authorization: Bearer <토큰>` 필요한 보호 라우트
- `GET /users/admin/ping` — `is_admin=True`인 사용자만 접근 가능 (인가 데모)
- `GET /health` — 헬스체크

## 사용한 도구 / 라이브러리

| 도구 | 버전 | 역할 |
|------|------|------|
| Python | 3.13 | 언어 |
| FastAPI | 0.115+ | 웹 프레임워크 |
| Pydantic | 2.x | 요청·응답 검증 |
| SQLAlchemy | 2.0 (async) | ORM |
| Alembic | 1.13+ | 마이그레이션 |
| aiosqlite | 0.20+ | 비동기 SQLite 드라이버 |
| PyJWT | 2.8+ | JWT 발급·검증 |
| bcrypt | 4.x | 비밀번호 해싱 (직접 사용) |
| Uvicorn | 0.30+ | ASGI 서버 |
| uv | 0.4+ | 패키지/가상환경 관리 |

## 빠른 실행

### 1) 의존성 설치

```bash
uv sync
```

### 2) 환경 변수 준비

`.env.example`을 복사해 `.env`를 만든 뒤, `SECRET_KEY`를 실제 난수로 교체합니다.

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
# 출력값을 .env의 SECRET_KEY 자리에 붙여 넣으세요.
```

### 3) DB 마이그레이션 적용

```bash
uv run alembic upgrade head
```

`auth.db` 파일이 생기고 `users` 테이블이 만들어집니다.

### 4) 개발 서버 띄우기

```bash
uv run uvicorn app.main:app --reload
```

- `http://127.0.0.1:8000/docs` — 자동 문서 (Swagger UI)
- `http://127.0.0.1:8000/redoc` — ReDoc

## curl로 따라하는 흐름

### 회원가입

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

### 로그인

`-d`는 form-encoded 입니다(JSON이 아닙니다).

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

### 보호된 라우트

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

토큰 없이 호출하면 401:

```bash
curl -i http://127.0.0.1:8000/users/me
```

### 관리자 라우트 (인가 데모)

기본 가입자는 `is_admin=False`입니다. SQLite CLI로 한 줄을 바꿔서 테스트합니다.

```bash
sqlite3 auth.db "UPDATE users SET is_admin=1 WHERE email='alice@example.com';"
```

이제 같은 토큰으로(또는 새로 발급받아) 관리자 라우트 호출:

```bash
curl http://127.0.0.1:8000/users/admin/ping \
  -H "Authorization: Bearer $TOKEN"
# {"message":"Hello, admin alice@example.com!"}
```

`is_admin=False`인 사용자가 같은 라우트를 부르면 403입니다.

## 자동 문서에서 로그인 시연

`http://127.0.0.1:8000/docs`를 열면 우측 상단에 **Authorize** 버튼이 보입니다.

1. **Authorize** 클릭 → username(이메일)과 password 입력 → **Authorize**
2. 보호된 엔드포인트(자물쇠 아이콘이 있는 라우트)가 모두 잠금 해제됨
3. `GET /users/me`를 펼치고 **Try it out → Execute** 클릭 → 200 응답

이 흐름은 `OAuth2PasswordBearer(tokenUrl="/auth/login")` 한 줄 등록만으로 자동 동작합니다.

## 테스트 실행

```bash
uv run pytest -v
```

`tests/test_auth.py`에 다음 케이스가 들어 있습니다.

- 회원가입 → 로그인 → 보호된 라우트 정상 흐름
- 이메일 중복 → 409
- 잘못된 비밀번호 → 401
- 존재하지 않는 사용자로 로그인 → 401 (메시지 동일)
- 토큰 없이 보호된 라우트 → 401
- 변조된 토큰 → 401
- 만료된 토큰 → 401
- 너무 긴 비밀번호 → 422
- 일반 사용자가 관리자 라우트 → 403
- 관리자가 관리자 라우트 → 200

## 폴더 구조

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
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── deps.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── users.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_auth.py
```

## 주의사항

- `SECRET_KEY`를 `.env.example`의 기본값 그대로 운영에 띄우면 안 됩니다.
- `.env`는 절대 git에 커밋하지 마세요(`.gitignore`로 막혀 있음).
- 운영 환경은 반드시 HTTPS를 씁니다 — JWT가 평문으로 헤더에 실리기 때문입니다.
- Bcrypt는 비밀번호 입력의 첫 72바이트만 사용합니다. 한국어는 글자당 3바이트로 계산되어 24글자 근처에서 잘립니다 — 이 예제의 `hash_password`는 사전 검증으로 막아둡니다.
