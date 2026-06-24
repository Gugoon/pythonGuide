# 11-BlogAPI — FastAPI 가이드 11장 종합 예제

다중 사용자 블로그 REST API. User · Post · Comment · Tag 모델과 1:N · N:M 관계,
JWT 인증, MySQL 연동, 페이지네이션·검색·태그 필터까지 한 프로젝트에 모았습니다.
본문 가이드는 [docs/11-project-blog-api.md](../../docs/11-project-blog-api.md)를 참고하세요.

## 핵심 기능

- `POST /auth/signup` — 회원가입 (Bcrypt 해싱)
- `POST /auth/login` — JWT 액세스 토큰 발급
- `GET /auth/me` — 내 정보 (보호됨)
- `GET /posts` — 목록 (페이지네이션 `?page=1&size=20`, 검색 `?q=...`, 태그 필터 `?tag=python`, 정렬 `?sort=-created_at`)
- `GET /posts/{id}` — 단건 조회. 공개 글은 비로그인도, 비공개 글은 작성자만.
- `POST /posts` — 글 작성. `tags: ["python","fastapi"]`로 태그 자동 생성·연결.
- `PATCH /posts/{id}` — 부분 수정 (작성자만)
- `DELETE /posts/{id}` — 삭제 (작성자만)
- `POST /posts/{id}/publish`, `POST /posts/{id}/unpublish` — 게시 상태 토글
- `GET /posts/{id}/comments` — 댓글 목록
- `POST /posts/{id}/comments` — 댓글 작성 (보호됨)
- `PATCH /comments/{id}`, `DELETE /comments/{id}` — 댓글 수정·삭제 (작성자만)
- `GET /tags` — 태그 목록
- `GET /health` — 헬스체크

## 사용한 도구 / 라이브러리

| 도구 | 버전 | 역할 |
|------|------|------|
| Python | 3.13 | 언어 |
| FastAPI | 0.115+ | 웹 프레임워크 |
| Pydantic | 2.x | 요청·응답 검증 |
| SQLAlchemy | 2.0 (async) | ORM |
| Alembic | 1.13+ | 마이그레이션 |
| asyncmy | 0.2+ | MySQL 비동기 드라이버 |
| aiosqlite | 0.20+ | 테스트용 SQLite 드라이버 |
| PyJWT | 2.8+ | JWT 발급·검증 |
| bcrypt | 5.x | 비밀번호 해싱 (직접 사용) |
| python-slugify | 8.x | 제목 → slug 변환 |
| Uvicorn | 0.30+ | ASGI 개발 서버 |
| Gunicorn | 23.x (선택) | graceful reload 등이 필요할 때만 (기본은 Uvicorn 멀티워커) |
| Docker | latest | 컨테이너화 |
| MySQL | 8.4 LTS | 데이터베이스 |
| uv | 0.4+ | 패키지/가상환경 관리 |

## 빠른 실행 (Docker Compose 권장)

가장 빠른 길은 `docker compose`로 MySQL과 앱을 함께 띄우는 것입니다.

```bash
# 1) 환경 변수 준비
cp .env.example .env
# .env 의 SECRET_KEY 를 다음으로 교체:
# python -c "import secrets; print(secrets.token_urlsafe(48))"

# 2) MySQL 띄우기
docker compose up -d db

# 3) 마이그레이션 적용
docker compose run --rm migrate

# 4) 앱 띄우기 (개발 모드: --reload 활성)
docker compose up app
```

`http://127.0.0.1:8000/docs` 에서 자동 생성된 Swagger UI로 모든 엔드포인트를
바로 시험해 볼 수 있습니다.

## 로컬에서 직접 실행 (Docker 없이)

```bash
# 1) Python 의존성
uv sync

# 2) MySQL 컨테이너만 별도로 띄우기
docker run --name blog-mysql \
  -e MYSQL_DATABASE=blog_api \
  -e MYSQL_USER=blog_user \
  -e MYSQL_PASSWORD=blog_pass \
  -e MYSQL_ROOT_PASSWORD=root_pass \
  -p 3306:3306 -d mysql:8.4

# 3) 환경 변수 + 마이그레이션
cp .env.example .env
uv run alembic upgrade head

# 4) 개발 서버
uv run uvicorn app.main:app --reload
```

## 자주 쓰는 흐름 — curl

### 회원가입 + 로그인

```bash
curl -X POST http://127.0.0.1:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"hunter22hunter","name":"Alice"}'

TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice@example.com&password=hunter22hunter" | jq -r .access_token)
```

### 글 작성 (태그 자동 연결)

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

### 목록 조회 (검색 + 태그)

```bash
curl "http://127.0.0.1:8000/posts?q=FastAPI&tag=python&page=1&size=10"
```

### 댓글

```bash
POST_ID=1
curl -X POST "http://127.0.0.1:8000/posts/$POST_ID/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"body":"좋은 글이네요"}'
```

## 테스트 실행

```bash
uv run pytest -v
```

테스트는 인메모리 SQLite로 빠르게 돕니다(같은 ORM 코드가 두 DB에서 모두 동작).

## 폴더 구조

```
11-BlogAPI/
├── pyproject.toml
├── uv.lock                # 첫 `uv sync` 시 생성됨 — 저장소에 커밋 권장
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
│       └── 0001_initial.py
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 앱 조립
│   ├── config.py           # 설정 (환경 변수)
│   ├── db.py               # 비동기 엔진·세션
│   ├── models.py           # User · Post · Comment · Tag · PostTag
│   ├── schemas.py          # Pydantic 입출력 스키마
│   ├── security.py         # bcrypt + JWT
│   ├── deps.py             # get_current_user / get_optional_user
│   ├── crud.py             # slug, 태그 자동 생성, 검색·페이지 필터
│   └── routers/
│       ├── __init__.py
│       ├── auth.py         # /auth/signup, /auth/login, /auth/me
│       ├── posts.py        # /posts CRUD + publish toggle
│       ├── comments.py     # /posts/{id}/comments + /comments/{id}
│       └── tags.py         # /tags
└── tests/
    ├── __init__.py
    ├── conftest.py         # 인메모리 DB + 앱 의존성 override + 토큰 픽스처
    └── test_blog.py        # 10개의 통합 케이스
```

## 운영 체크리스트

- [ ] `.env`는 git에 커밋하지 않는다(`.gitignore`에 등록됨)
- [ ] `SECRET_KEY`를 `python -c "import secrets; print(secrets.token_urlsafe(48))"` 결과로 교체
- [ ] MySQL 비밀번호를 운영용으로 강하게 변경(`docker-compose.yml`의 기본값은 개발용)
- [ ] HTTPS — Let's Encrypt + nginx (또는 Render·Fly.io 자동 TLS)
- [ ] CORS `allow_origins`를 실제 프런트엔드 도메인 목록으로 명시
- [ ] DB 정기 백업 (`mysqldump` 크론)
- [ ] 로그 회전·모니터링
