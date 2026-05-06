# 11-BlogAPI 운영용 컨테이너 이미지.
# 단계 1) 의존성 빌드 단계 — uv로 lock 파일 기준으로 정확히 같은 버전을 받는다.
# 단계 2) 실행 단계 — 가벼운 슬림 이미지에 빌드 결과만 복사한다.

FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# uv 설치 (Astral 공식 이미지에서 바이너리만 가져온다 — 새 마이너 출시 시 직접 갱신)
COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /uvx /usr/local/bin/

WORKDIR /app

# 락 파일 기준으로 의존성을 먼저 설치 (소스 변경에도 캐시 활용)
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

# 앱 소스 복사
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./

# ─────────────────────────────────────────────────────────
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# 비루트 사용자로 실행해 권한 사고를 줄인다.
RUN groupadd --system app && \
    useradd --system --gid app --no-create-home --shell /usr/sbin/nologin app

WORKDIR /app

# 빌더에서 설치한 가상환경과 소스 그대로 복사
COPY --from=builder /app /app

# 앱 디렉터리 소유자를 app 으로
RUN chown -R app:app /app

USER app

EXPOSE 8000

# 운영에서는 Uvicorn 자체 멀티워커(0.30+ 내장) + proxy-headers.
# 옛 `gunicorn -k uvicorn.workers.UvicornWorker` 패턴은 deprecated 되어 별도
# 패키지(`uvicorn-worker`)로 분리됐습니다. Gunicorn 의 graceful reload 가 꼭
# 필요하면 `uv add uvicorn-worker` 후 `-k uvicorn_worker.UvicornWorker` 로.
# 개발에서는 docker-compose의 command를 uvicorn --reload 로 덮어쓴다.
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "2", \
     "--proxy-headers", "--forwarded-allow-ips=*"]
