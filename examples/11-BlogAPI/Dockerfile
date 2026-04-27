# 11-BlogAPI 운영용 컨테이너 이미지.
# 단계 1) 의존성 빌드 단계 — uv로 lock 파일 기준으로 정확히 같은 버전을 받는다.
# 단계 2) 실행 단계 — 가벼운 슬림 이미지에 빌드 결과만 복사한다.

FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

# uv 설치 (Astral 공식 이미지에서 바이너리만 가져온다)
COPY --from=ghcr.io/astral-sh/uv:0.5.18 /uv /uvx /usr/local/bin/

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

# 운영에서는 gunicorn + uvicorn worker.
# 개발에서는 docker-compose의 command를 uvicorn --reload 로 덮어쓴다.
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "-w", "2", "-b", "0.0.0.0:8000"]
