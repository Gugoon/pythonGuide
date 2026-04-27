# 10-NoteAPI — FastAPI 가이드 10장 종합 예제

회원가입·로그인·개인 메모 CRUD가 동작하는 작은 백엔드. PostgreSQL + Docker
Compose 환경을 함께 제공한다. 본문은 [docs/10-project-note-api.md](../../docs/10-project-note-api.md)를 참고하세요.

## 핵심 기능

- `POST /auth/signup` — 이메일+비밀번호로 회원가입 (Bcrypt 해싱 저장)
- `POST /auth/login` — 로그인 후 JWT 액세스 토큰 발급 (form-encoded)
- `POST /notes` — 새 메모 작성 (Bearer 토큰 필요)
- `GET /notes` — **내 메모만** 페이지네이션·태그/검색 필터로 조회
- `GET /notes/{id}` — 단건 조회 (본인 소유만)
- `PATCH /notes/{id}` — 부분 수정 (본인 소유만)
- `DELETE /notes/{id}` — 삭제 (본인 소유만)
- `GET /health` — 헬스체크

## 사용 스택

| 도구 | 버전 | 역할 |
|------|------|------|
| Python | 3.13 | 언어 |
| FastAPI | 0.115+ | 웹 프레임워크 |
| Pydantic | 2.x | 요청·응답 검증 |
| SQLAlchemy | 2.0 (async) | ORM |
| Alembic | 1.13+ | 마이그레이션 |
| asyncpg | 0.29+ | PostgreSQL 비동기 드라이버 |
| aiosqlite | 0.20+ | 테스트용 SQLite 비동기 드라이버 |
| PyJWT | 2.8+ | JWT 발급·검증 |
| bcrypt | 4.x | 비밀번호 해싱 (직접 사용) |
| Uvicorn | 0.30+ | 개발 ASGI 서버 |
| Gunicorn | 22+ | 운영 프로세스 매니저 |
| uv | 0.4+ | 패키지/가상환경 관리 |

## 빠른 실행

### 1) 의존성 설치

```bash
uv sync
```

### 2) PostgreSQL 띄우기 (Docker Compose)

```bash
docker compose up -d db
docker compose ps
# db 가 healthy 상태가 될 때까지 5~15초 대기
```

### 3) 환경 변수 준비

```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(48))"
# 출력값을 .env의 SECRET_KEY 자리에 붙여 넣으세요.
```

### 4) DB 마이그레이션 적용

```bash
uv run alembic upgrade head
```

`users`, `notes` 두 테이블이 생긴다.

### 5) 개발 서버 띄우기

```bash
uv run uvicorn app.main:app --reload
```

- `http://127.0.0.1:8000/docs` — 자동 문서 (Swagger UI)
- `http://127.0.0.1:8000/redoc` — ReDoc

## curl 따라하기

### 회원가입 → 로그인 → 토큰 보관

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"alicepass1234"}'

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=alicepass1234" | jq -r .access_token)
echo "$TOKEN"
```

### 메모 만들기

```bash
curl -X POST http://127.0.0.1:8000/notes \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"첫 메모","body":"FastAPI 시작!","tag":"diary"}'
```

### 목록·검색·페이지네이션

```bash
curl "http://127.0.0.1:8000/notes?skip=0&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 태그 필터
curl "http://127.0.0.1:8000/notes?tag=diary" \
  -H "Authorization: Bearer $TOKEN"

# 키워드 검색(제목·본문 부분 일치, 대소문자 무시)
curl "http://127.0.0.1:8000/notes?search=시작" \
  -H "Authorization: Bearer $TOKEN"
```

### 부분 수정 / 삭제

```bash
curl -X PATCH http://127.0.0.1:8000/notes/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"제목만 살짝"}'

curl -X DELETE -i http://127.0.0.1:8000/notes/1 \
  -H "Authorization: Bearer $TOKEN"
# HTTP/1.1 204 No Content
```

### 본인 소유 검사 시연

다른 사용자의 메모 ID로 GET을 시도하면 **404**가 떨어진다(403이 아니다).
"권한 없음"으로 응답하면 다른 사람 메모의 존재 자체가 노출되기 때문이다.

```bash
# Bob 가입·로그인 (생략) → Bob의 토큰을 $T2 에 보관했다고 가정
curl -i http://127.0.0.1:8000/notes/1 \
  -H "Authorization: Bearer $T2"
# HTTP/1.1 404 Not Found
```

## 통째로 컨테이너로 실행

운영과 비슷한 모양으로 띄우려면 `app + db`를 한 번에 올린다.

```bash
docker compose --env-file .env up --build
```

`http://localhost:8000/health` → `{"status":"ok"}` 면 OK.

## 테스트

```bash
uv run pytest -v
```

테스트는 인메모리 SQLite 위에서 도므로 PostgreSQL이 떠 있지 않아도 통과한다.
운영의 동작은 Docker Compose로 별도로 검증한다.

## 폴더 구조

```
10-NoteAPI/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial.py
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── deps.py
│   ├── crud.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       └── notes.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── test_notes.py
```

## 주의사항

- `.env`는 절대 git에 커밋하지 말 것 (`.gitignore`에 막혀 있음).
- 운영 환경은 반드시 HTTPS — JWT가 평문으로 헤더에 실리기 때문.
- `SECRET_KEY`는 운영 배포 전 반드시 강한 난수로 교체.
- Bcrypt는 입력의 첫 72바이트만 사용한다. 한국어는 글자당 3바이트로 계산되어
  24글자 근처에서 잘리기 시작 — `app/security.py`가 사전에 `ValueError`를 낸다.
- 본인 소유 검사: 모든 Note 핸들러는 `note.user_id == current_user.id`를 쿼리
  조건으로 함께 건다. 남의 메모를 만지는 사고는 구조적으로 불가능.
