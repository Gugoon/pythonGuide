# 15-BackgroundTasks — FastAPI 백그라운드 작업 예제

FastAPI 가이드 [15장 백그라운드 작업](../../docs/15-background-tasks.md)의 완성본입니다. 응답을 **먼저** 클라이언트에게 보내고, 환영 알림·감사 로그·보너스 포인트 지급 같은 부수 작업을 **응답 전송 후** 백그라운드로 처리하는 `BackgroundTasks` 패턴을 보여 줍니다.

## 사용 기술

- Python 3.13
- FastAPI 0.115.x (`BackgroundTasks`)
- Pydantic 2.x
- pytest + pytest-asyncio + httpx (테스트)
- uv (패키지/가상환경 매니저)

DB 는 쓰지 않습니다. 백그라운드 작업의 결과는 학습용 인메모리 상태(`app/state.py`)에 기록하고, 조회 엔드포인트로 확인합니다.

## 실행 방법

```bash
# 1) 의존성 설치 (가상환경은 uv가 자동으로 만듭니다)
uv sync

# 2) 서버 실행
uv run uvicorn app.main:app --reload
```

서버가 뜨면 다음 주소에서 확인할 수 있습니다.

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- 헬스 체크: http://127.0.0.1:8000/health

## 직접 호출해 보기

```bash
# 가입 — 즉시 201 응답이 오고, 알림/감사로그/포인트는 백그라운드로 처리된다.
curl -X POST http://127.0.0.1:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "alice"}'

# 잠시 후 백그라운드 작업의 결과를 조회.
curl http://127.0.0.1:8000/notifications
curl http://127.0.0.1:8000/audit-log
```

## 테스트 실행

```bash
uv run pytest -v
```

> **테스트 타이밍 메모**: httpx 의 `ASGITransport` 로 보낸 요청은 `await client.post(...)` 가 반환될 시점에 응답 전송이 끝나 있고, 그 직후 백그라운드 작업도 모두 실행된 상태가 됩니다. 그래서 요청을 보낸 뒤 `/notifications`·`/audit-log` 를 조회해 작업 수행 여부를 검증합니다. 진짜 uvicorn 서버와 실제 네트워크로 호출할 때도 동작은 같지만, 응답 수신과 백그라운드 실행 완료 사이에 약간의 시간차가 있을 수 있습니다.

## 폴더 구조

```
15-BackgroundTasks/
├── pyproject.toml
├── uv.lock                   (uv sync 후 생성)
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 앱 + 엔드포인트 + BackgroundTasks 등록
│   ├── state.py              # 학습용 인메모리 상태(+ reset)
│   └── tasks.py              # 백그라운드에서 실행될 작업 함수들
└── tests/
    ├── __init__.py
    ├── conftest.py           # AsyncClient 픽스처 + 매 테스트 상태 초기화
    └── test_background_tasks.py
```

## 엔드포인트

| 메서드 | 경로 | 설명 | 성공 상태 |
|--------|------|------|-----------|
| `POST` | `/signup` | 가입 응답 즉시 반환 + 백그라운드 작업 3개 등록 | 201 |
| `POST` | `/signup-via-dependency` | `BackgroundTasks` 를 의존성으로 주입받는 패턴 | 201 |
| `POST` | `/signup-with-risky-task` | 실패할 수 있는 부수 작업 + 안전한 작업 함께 등록 | 201 |
| `GET` | `/notifications` | 백그라운드로 기록된 환영 알림 조회(검증용) | 200 |
| `GET` | `/audit-log` | 백그라운드로 기록된 감사 로그 조회(검증용) | 200 |
| `GET` | `/health` | 헬스 체크 | 200 |

## 한계와 다음 단계

`BackgroundTasks` 는 **같은 프로세스·같은 요청 수명**에 묶입니다. 작업이 무겁거나(이미지 처리 등), 재시도·스케줄링·여러 워커 분산이 필요하면 Celery·RQ·arq 같은 **외부 작업 큐**로 옮겨야 합니다. 외부 큐는 12장(유용한 라이브러리)에서 다룹니다.
