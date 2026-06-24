# 09. 배포 가이드 — Docker, Render/Fly.io, AWS, Ubuntu

> **이 챕터의 목표**
> - 개발 서버(`uvicorn --reload`)와 운영 서버의 차이를 이해하고, 왜 운영에서는 **Uvicorn 멀티워커**(`--workers N`)를 쓰는지를 한 줄로 설명할 수 있다.
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
| 서버 | `uvicorn --reload` 한 프로세스 | `uvicorn ... --workers N` 이 여러 워커 프로세스를 띄움 |
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

이 모든 단점을 한 번에 해결하는 가장 단순한 길은 **Uvicorn 자체의 멀티워커 모드**다(0.30 부터 자체 워커 매니저 내장). 운영의 다음 단계로는 Gunicorn + 별도 패키지 `uvicorn-worker` 를 둘 수 있지만, 입문 단계에서는 Uvicorn 한 줄이면 충분하다.

> **2026 시점 메모 — `uvicorn.workers.UvicornWorker` 는 deprecated**: Uvicorn 0.30(2024-06)부터 자체 멀티워커가 내장되며 `uvicorn.workers.UvicornWorker` 는 deprecated 되었고, 권장 경로가 별도 패키지(`uvicorn-worker`)로 옮겨졌다(레거시 import 는 경고와 함께 아직 동작). 이 가이드는 **Uvicorn 자체 워커**를 표준으로 쓴다. Gunicorn 의 운영 기능(graceful reload, preload 등)이 꼭 필요하면 `uv add uvicorn-worker` 후 `-k uvicorn_worker.UvicornWorker` 를 사용한다.

### 9.1.3 운영 명령 한 줄 — 이 가이드의 표준

이 챕터에서 어디든 동일하게 쓰는 운영 실행 명령은 다음과 같다. **이 한 줄을 외워 두면 모든 배포 경로에서 다시 마주친다.**

```bash
uvicorn app.main:app \
    --host 0.0.0.0 --port 8000 \
    --workers 4 \
    --proxy-headers --forwarded-allow-ips='127.0.0.1'
```

각 옵션의 의미를 한 번 풀어 적는다.

| 옵션 | 의미 |
|------|------|
| `app.main:app` | "`app/main.py` 파일 안의 `app` 객체를 띄워라" |
| `--host 0.0.0.0 --port 8000` | 외부 모든 IP 의 8000 포트로 들어오는 요청을 받음. (`127.0.0.1` 로 두면 같은 컴퓨터 안에서만 접근 가능) |
| `--workers 4` | 워커 프로세스 수. 비동기 앱은 보통 **`코어 수`** 정도가 출발점(다음 절 참고). |
| `--proxy-headers` | nginx/리버스 프록시 뒤에서 받은 `X-Forwarded-Proto`, `X-Forwarded-For` 를 신뢰. 없으면 `request.url.scheme` 가 항상 `http`, `client.host` 가 항상 프록시 IP 로 잡힌다. |
| `--forwarded-allow-ips='127.0.0.1'` | 위 헤더를 신뢰할 발신지. 같은 호스트의 프록시(nginx 등) 뒤라면 `127.0.0.1` 이 기본이자 안전한 값. `'*'` 는 아무 발신지의 위조 헤더도 믿게 되므로 피한다. **여러 프록시/오케스트레이터(로드밸런서·k8s 등) 뒤에서는** 신뢰 대역으로 넓혀라(예: 프록시 서브넷). |

> **Gunicorn 을 쓰고 싶다면** — `uv add uvicorn-worker` 후 다음:
> ```bash
> gunicorn app.main:app \
>     -k uvicorn_worker.UvicornWorker \
>     -b 0.0.0.0:8000 \
>     --workers 4 \
>     --timeout 60 \
>     --forwarded-allow-ips='127.0.0.1' \
>     --access-logfile - --error-logfile -
> ```
> graceful reload, preload, 더 정교한 워커 관리가 필요한 운영 환경에 적합하다. 입문 학습 흐름에서는 위 Uvicorn 한 줄로 충분하다.

### 9.1.4 워커 수는 어떻게 정하나

- **`(2 × CPU 코어) + 1`** 공식은 **동기 워커(WSGI) 시절**의 가이드라인이다. Gunicorn 공식 문서가 옛날부터 적어둔 식이며, 동기 워커를 쓰는 환경에서는 여전히 합리적인 출발점이다.
- **FastAPI(비동기) 워커는 다르다.** 한 워커 안에서 수천 건의 요청을 동시에 처리할 수 있으므로, **`워커 수 = CPU 코어 수`** (또는 그 이하)로 시작하는 편이 메모리 측면에서 효율적이다.

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

- [ ] **환경 변수**: `DATABASE_URL`, `SECRET_KEY`, `CORS_ALLOW_ORIGINS` 등이 코드/저장소에 박혀 있지 않다. `.env.example` 에 변수 이름과 의미만 적혀 있다.
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
# 버전은 작성 시점 안정 태그. 새 마이너가 나오면 직접 핀 갱신 권장.
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/

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

# tini 가 PID 1 을 받고, 그 아래에서 uvicorn 이 동작한다
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", "--forwarded-allow-ips=127.0.0.1"]
```

내용이 길어 보이지만, 본질은 **두 단계뿐**이다.

1. **빌더**: `pyproject.toml` + `uv.lock` 만 먼저 복사 → `uv sync --frozen --no-dev` 로 의존성 설치 → 소스 복사 → 프로젝트 설치.
2. **런타임**: 빌더에서 만든 `/app` 폴더(가상환경 포함) 를 통째로 가져와 `uvicorn` 실행.

각 줄에 적은 주석을 그대로 따라 읽으면 충분하다. 핵심 포인트만 다섯 가지 다시 짚자.

#### 1) `python:3.13-slim` 을 베이스로

- `python:3.13` 풀 이미지: Debian + 빌드 도구까지 포함 (~1GB). 너무 무겁다.
- `python:3.13-slim` 이미지: Debian slim + Python 만 (압축 약 50MB / 풀어서 약 150MB). **이 가이드의 기본**.
- `python:3.13-alpine` 이미지: Alpine Linux 기반 (압축 약 25MB). 가벼우나 일부 라이브러리(asyncpg, bcrypt, greenlet 등 C 확장) 빌드가 까다롭다. 입문자에겐 비권장.

> **베이스 이미지의 버전을 못 박는 이유**: `python:3.13` 만 쓰면 새 마이너 버전이 나올 때 조용히 바뀐다. 이 가이드는 학습용이니 `python:3.13-slim` 정도면 충분하지만, **운영에서는 `python:3.13.1-slim-bookworm`** 처럼 더 정확히 못 박는 편이 좋다.

#### 2) `uv` 를 한 줄로 가져온다

```dockerfile
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /bin/
```

`uv` 의 공식 이미지에서 실행 파일만 잘라내 우리 빌더에 옮긴다. `pip install uv` 같은 단계가 필요 없다 — 이게 가장 빠르고 깔끔한 패턴이다.

> **버전 고정**: `:0.7` 처럼 정확히 못 박아라. `:latest` 로 두면 빌드가 어느 날 갑자기 깨질 수 있다. 작성 시점 이후 새 마이너가 나오면 그때그때 직접 갱신.

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

PID 1 프로세스는 좀비 자식 프로세스를 거두고, 신호(SIGTERM 등) 를 잘 다뤄야 하는 책임이 있다. Python/Uvicorn 이 이 역할을 직접 해도 잘 동작하는 경우가 많지만, 가끔 좀비 프로세스가 남는 등의 미묘한 문제가 생긴다. **`tini` 라는 작은 init 을 한 줄 끼워 두면** 이 문제가 깔끔히 사라진다.

```dockerfile
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
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
| `app` | 우리의 FastAPI 앱 (Uvicorn 멀티워커, 포트 8000) |
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
SECRET_KEY=local-dev-secret-do-not-use-in-prod
CORS_ALLOW_ORIGINS=http://localhost:3000
APP_NAME=Todo API (local)
```

협업용으로 git 에 두는 `.env.example`:

```
DATABASE_URL=
SECRET_KEY=
APP_ENV=production
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

> **Render 는 Dockerfile 없이도 배포 가능**: "Native Runtime" 옵션은 `pyproject.toml` + start command 만 있으면 빌드한다. 하지만 본 가이드는 모든 배포 경로에서 같은 결과를 재현하기 위해 **Docker** 로 통일한다. Native runtime 이 더 가볍지만, "Render 에서만 동작하는 빌드 결과물" 이 되어 EC2/Fly 와 동일한 체크리스트를 못 쓴다.

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
   - `SECRET_KEY` = 길고 무작위한 문자열. 터미널에서 `openssl rand -base64 48` 로 만들어 붙여넣기.
   - `APP_ENV` = `production`. 기본 더미 키로 운영 부팅하는 사고를 막는 안전장치 활성화.
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
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers --forwarded-allow-ips='127.0.0.1'"]
```

`alembic upgrade head` 는 **변경사항이 없으면 빠르게 끝나기 때문에**, 매 배포마다 부르는 비용이 매우 작다. 단 한 가지 함정이 있다 — **Alembic 자체는 마이그레이션 락을 걸지 않는다.** 워커가 여러 개라서 동시에 부팅하거나 인스턴스 수가 둘 이상이면 두 곳에서 동시에 같은 리비전을 적용하려다 실패할 수 있다(version_table 의 unique 제약이 있어 데이터가 깨지진 않지만 한쪽이 부팅 실패). PostgreSQL 환경이라면 `pg_advisory_lock` 같은 advisory lock 을 직접 거는 패턴이 안전하고, 가장 깔끔한 해법은 **다음 패턴 B(별도 release/pre-deploy 단계로 분리)** 다.

**패턴 B — Render Job 으로 분리 (권장 운영)**

Render 대시보드의 **New +** → **Cron Job** 또는 **Pre-Deploy Command**(Render 의 "Build & Deploy" 설정에 있는 항목) 에 다음을 적어둔다.

```
alembic upgrade head
```

Pre-Deploy Command 는 **새 인스턴스가 트래픽을 받기 전에 한 번 실행**된다. 마이그레이션이 실패하면 배포가 자동으로 롤백된다.

> **주의**: Pre-Deploy Command 는 **유료 플랜에서 제공**된다(가입 시점의 플랜별 기능 표를 직접 확인하세요 — 정책이 자주 바뀝니다). 제공되지 않는 플랜에서는 패턴 A(시작 직전 컨테이너 안에서 실행)를 쓰거나, 별도의 Cron Job 으로 분리해야 한다.

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
- DB 무료 플랜은 **한정 기간만 무료**(시점에 따라 30~90일 또는 폐지될 수 있으며 정책이 자주 바뀐다 — 가입 시 약관을 직접 확인). 학습 후 끄거나 유료 전환.
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
3. Postgres 를 같이 만들 거냐고 묻는다 — 학습용이라면 `y` 후 Development 인스턴스 선택. **운영 용도라면 Fly 의 자체 Postgres 대신 Managed Postgres(MPG) 또는 Supabase 통합을 우선 고려**(아래 박스 참고).
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
    SECRET_KEY="$(openssl rand -base64 48)" \
    APP_ENV="production" \
    CORS_ALLOW_ORIGINS="*"
```

> `APP_ENV=production` 은 기본 더미 키로 운영 부팅하는 사고를 막는 안전장치를 활성화한다.

`DATABASE_URL` 은 위 9.6.2 단계에서 Postgres 를 같이 만들었다면 **이미 자동 주입**돼 있다. 다음 명령으로 확인.

```bash
fly secrets list
```

다음 같은 출력이 나오면 OK.

```
NAME                    DIGEST        CREATED AT
DATABASE_URL            abc...         5m ago
SECRET_KEY              def...         1m ago
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

> **주의 — Fly 자체 Postgres 는 unmanaged 옵션**: `fly postgres create` 로 만드는 Postgres 는 Fly 가 호스팅만 해 주는 **unmanaged** 인스턴스로, 백업·복구·장애 대응 책임이 사용자에게 있다. 2024 부터 Fly 는 신규 사용자에게 **Managed Postgres(MPG)** 또는 외부 파트너 **Supabase** 통합을 먼저 권한다. 운영 용도라면 다음을 검토:
>
> - **MPG**: `fly mpg create` (별도 요금, 자동 백업/HA 포함)
> - **Supabase**: `fly ext supabase create` 로 통합
> - **외부 RDS / Neon**: 일반 `DATABASE_URL` 로 연결
>
> 학습·소규모 서비스라면 위 자체 Postgres 도 충분히 쓸 만하지만, "운영" 라벨을 붙일 때는 백업 정책을 직접 챙겨야 한다는 점만 잊지 말 것.

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
fly secrets unset SECRET_KEY  # 비밀 제거
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
SECRET_KEY=서버에서_생성한_긴_랜덤_문자열
APP_ENV=production
CORS_ALLOW_ORIGINS=*
APP_NAME=Todo API (prod)
```

> `APP_ENV=production` 은 기본 더미 키로 운영 부팅하는 사고를 막는 안전장치를 활성화한다.

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

> **운영 EC2 보안**: 9.4.1 의 `docker-compose.yml` 을 그대로 가져왔다면 `db` 서비스의 `ports: "5432:5432"` 가 호스트 0.0.0.0 에 바인딩된다. EC2 보안 그룹에서 5432 가 닫혀 있으면 인터넷 노출은 막히지만, 같은 인스턴스 안의 다른 컨테이너/사용자에게는 열려 있다. 운영 EC2 에서는 `db.ports` 를 빼거나 `127.0.0.1:5432:5432` 로 바꿔 호스트 인터페이스 노출 자체를 막아라.

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
Description=Todo API (FastAPI + Uvicorn)
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

# 실행 명령 — .venv 안의 uvicorn 을 절대 경로로 부른다
# nginx 가 같은 머신에서 프록시하므로 127.0.0.1 에만 바인딩.
ExecStart=/srv/myapp/.venv/bin/uvicorn app.main:app \
    --host 127.0.0.1 --port 8000 \
    --workers 4 \
    --proxy-headers --forwarded-allow-ips=127.0.0.1

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
| `ExecStart=...` | **절대 경로**로 `uvicorn` 을 지정. systemd 는 PATH 가 비어 있는 상태로 동작하므로 항상 절대 경로. |
| `--host 127.0.0.1` | nginx 가 같은 머신에서 프록시할 거라 외부에 직접 노출하지 않음 |
| `--proxy-headers --forwarded-allow-ips=127.0.0.1` | nginx 가 보낸 `X-Forwarded-Proto`/`X-Forwarded-For` 를 신뢰. 없으면 FastAPI 가 항상 http·127.0.0.1 로 잡음. |
| `Restart=on-failure` | 비정상 종료 시 자동 재시작 |

> **`EnvironmentFile` 의 함정**: systemd 는 셸이 아니므로 `.env` 의 따옴표·공백 처리를 하지 않는다. `SECRET_KEY="abc def"` 처럼 적으면 따옴표째 변수에 들어간다. 값에 공백·특수문자가 필요하다면 따옴표 없이 그대로 적거나 base64 인코딩을 쓰자.

`.env` 파일은 다음처럼 둔다.

```bash
sudo nano /srv/myapp/.env
```

```
DATABASE_URL=postgresql+asyncpg://todo:todo@127.0.0.1:5432/todo
SECRET_KEY=긴_랜덤_문자열
APP_ENV=production
CORS_ALLOW_ORIGINS=https://app.example.com
```

> `APP_ENV=production` 은 기본 더미 키로 운영 부팅하는 사고를 막는 안전장치를 활성화한다.

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

> **`--proxy-headers` 가 왜 중요한가**: nginx 가 `proxy_set_header X-Forwarded-Proto $scheme;` 로 원래 스킴(https)을 우리 앱에 알려도, **Uvicorn 은 기본적으로 이 헤더를 신뢰하지 않는다.** 그러면 FastAPI 의 `request.url.scheme` 가 항상 `http`, `request.client.host` 가 항상 `127.0.0.1` 로 잡혀 OAuth `redirect_uri` 가 잘못 만들어지고, HTTPS 강제 미들웨어가 무한 리다이렉트를 일으키며, IP 기반 rate-limit 가 모두 같은 IP 로 묶여 무용지물이 된다. 위 systemd `ExecStart` 의 `--proxy-headers --forwarded-allow-ips=127.0.0.1` 두 옵션이 이걸 막는다.

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
- [ ] 모든 비밀값(`SECRET_KEY`, `DATABASE_URL` 의 비밀번호 부분)이 코드/저장소에서 검색해도 안 나온다.
- [ ] 운영의 비밀값 주입 방법이 명확하다 (Render 의 Env UI / Fly secrets / EC2 의 systemd EnvironmentFile / k8s Secret 등).
- [ ] 같은 비밀이 여러 환경(개발/스테이지/운영) 에 다른 값으로 분리되어 있다.
- [ ] **`APP_ENV=production` 이 설정돼 있다** — 기본 더미 `SECRET_KEY` 로 운영 부팅하는 사고를 막는 안전장치 활성화.

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
          version: "0.7"
          enable-cache: true

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
          SECRET_KEY: "ci-test-secret"
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

> **`--load` 와 `--push` 의 차이**: `--load` 는 빌드 결과를 로컬 Docker 데몬에 적재하는데, **단일 플랫폼만 가능**하다. 멀티 아키텍처(`--platform a,b`) 빌드는 `--push` 로 레지스트리에 올려야 한다.

> **간단한 회피**: Render·Fly 는 자체 빌더로 이미지를 빌드하므로 이 문제가 거의 안 보인다. 직접 푸시해서 운영에 띄우는 경로(EC2 / 자체 서버) 에서만 의식하면 된다.

---

## 9.12 이 챕터 요약

- 운영 서버는 `uvicorn --reload` 가 아니라 **Uvicorn 멀티워커**(`--workers 4 --proxy-headers --forwarded-allow-ips`) 한 줄로 띄운다. 워커 수는 비동기 앱 기준 **CPU 코어 수** 에서 시작해 측정 후 조정. graceful reload 등 운영 기능이 더 필요하면 별도 패키지 `uvicorn-worker` + Gunicorn 으로 옮긴다(`uvicorn.workers.UvicornWorker` 는 deprecated).
- 어떤 배포 경로든 토대는 같다: **표준 멀티스테이지 `Dockerfile`** 하나(`python:3.13-slim` 베이스, uv 로 의존성 깐 뒤 비루트 유저로 uvicorn 실행) 와 **`.dockerignore`** 한 파일.
- 로컬 개발에서는 **`docker-compose.yml`** 로 앱 + PostgreSQL 을 한 번에 띄우고, `service_healthy` 로 부팅 순서를 안전하게 묶는다. 마이그레이션은 별도 일회성 컨테이너(`profile: tools`).
- **Render** 는 GitHub 연결만으로 5분 안에 배포 + HTTPS + 관리형 Postgres 까지 받을 수 있다. 마이그레이션은 Pre-Deploy Command 에 `alembic upgrade head` 한 줄.
- **Fly.io** 는 `flyctl` 로 모든 작업이 끝난다. `fly launch` → `fly secrets set` → `fly deploy`. 마이그레이션은 `release_command` 에 한 줄.
- **AWS EC2(t3.small)** 에 우분투를 깔고 Docker 만 설치한 뒤 `docker compose up -d` 로 띄우는 것이 입문에 가장 단순한 AWS 경로다. ECS·Fargate 는 학습 후 단계.
- **Ubuntu 직접 배포**는 `/srv/myapp/` 에 코드를 두고, **systemd 서비스 + nginx 리버스 프록시 + Let's Encrypt 자동 갱신**의 조합. 시스템 운영을 손에 익히는 가장 좋은 학습 경로.
- 어디든 빠뜨리면 안 되는 다섯 가지: **환경 변수 분리, 마이그레이션의 명시적 위치, `/health`, 표준 출력 기반 로그 + 적절한 레벨, HTTPS**. 이 다섯이 확보되면 나머지는 점진적으로 채워가도 안전하다.
- GitHub Actions 한 파일(`uv sync` + `ruff check` + `pytest`) 로 가벼운 CI 부터 깔아두면 사고 비율이 눈에 띄게 줄어든다.

---

← [08. 사용자 인증](08-authentication.md) | 다음 문서로 이동: **[10. 종합 예제 1 — Note API →](10-project-note-api.md)**
