# syntax=docker/dockerfile:1.7
# 멀티 스테이지 빌드 — 1단계는 의존성 설치, 2단계는 실행 전용 슬림 이미지.
# uv는 빌드 단계에서만 사용하고, 실행 이미지에는 불필요한 빌드 도구가 남지 않게 한다.

# ───────────── 1) 빌더 ─────────────
FROM python:3.13-slim AS builder

# uv 설치(고정 버전을 박아두면 재현성이 좋아짐 — 새 마이너 나오면 직접 갱신)
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /usr/local/bin/

# uv가 가상환경 대신 시스템 site-packages에 직접 깔도록 둔다.
# (컨테이너 안에서는 격리가 이미 충분하므로 .venv를 따로 만들 이유가 없다.)
ENV UV_SYSTEM_PYTHON=1 \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) 의존성 메타데이터만 먼저 복사해 캐시 효율을 높임.
COPY pyproject.toml uv.lock* ./

# 2) 의존성 설치(개발 의존성은 제외).
RUN uv sync --frozen --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

# 3) 앱 소스 복사.
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini


# ───────────── 2) 런타임 ─────────────
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 비루트 사용자로 실행해 권한 사고를 줄인다.
RUN groupadd --system app && \
    useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# 빌더에서 설치된 패키지·소스를 그대로 가져온다.
COPY --from=builder /usr/local/lib/python3.13 /usr/local/lib/python3.13
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

# /app 을 sys.path 에 명시적으로 더한다 — `gunicorn`/`uvicorn`/`alembic` 등
# console_script 가 우리 패키지를 import 할 수 있도록.
ENV PYTHONPATH=/app

# 앱 폴더 소유자를 app으로
RUN chown -R app:app /app

USER app

EXPOSE 8000

# 운영용 기본 실행 — Uvicorn 자체 멀티워커 + proxy-headers.
# forwarded-allow-ips 기본은 127.0.0.1(같은 호스트의 프록시만 신뢰). Render·Fly 등
# 외부 프록시 뒤에 둘 땐 신뢰 대역(프록시 IP/서브넷, 또는 '*')으로 넓힌다.
# 개발 시에는 docker-compose에서 command를 uvicorn --reload로 덮어쓴다.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "4", \
     "--proxy-headers", "--forwarded-allow-ips=127.0.0.1"]
