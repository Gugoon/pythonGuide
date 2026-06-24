# 13-TestingDeep — pytest 테스트 심화 예제

FastAPI 가이드 [13장 테스트 작성 심화](../../docs/13-testing-deep.md)의 예제입니다. 작은 대상 앱 하나에 **픽스처 설계·파라미터화·에러 케이스·외부 HTTP 호출 모킹**을 보여주는 테스트 30개를 붙였습니다.

## 사용 기술

- Python 3.13
- FastAPI 0.115.x
- Pydantic 2.x
- pytest + pytest-asyncio (`asyncio_mode = "auto"`) + httpx.AsyncClient(ASGITransport)
- uv (패키지/가상환경 매니저)

## 무엇을 담고 있나

대상 앱(`app/`)은 DB 없이 인메모리 dict 하나만 쓰는 작은 API 입니다.

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/health` | 헬스 체크 |
| `POST` | `/quotes` | 명언 생성(검증 포함) |
| `GET` | `/quotes/{id}` | 단건 조회(없으면 404) |
| `GET` | `/quotes` | 전체 목록 |
| `GET` | `/rate/{code}` | **외부 환율 API 호출** — `app/services.py` 의 `fetch_rate` 로 격리 |

테스트(`tests/`)는 세 파일로 나뉩니다.

- `test_health_and_quotes.py` — 픽스처(`client`, `sample_quote`), 기본 CRUD, 404/422, 상태 격리.
- `test_parametrize.py` — `@pytest.mark.parametrize`, `pytest.raises`.
- `test_rate_mock.py` — 외부 호출 모킹 3종(`monkeypatch`, `dependency_overrides`, `httpx.MockTransport`).

## 실행 방법

```bash
# 1) 의존성 설치 (가상환경은 uv가 자동으로 만듭니다)
uv sync

# 2) 테스트 실행
uv run pytest -v

# 3) (선택) 서버 실행 — 직접 눌러보고 싶을 때
uv run uvicorn app.main:app --reload
```

서버가 뜨면 Swagger UI 는 http://127.0.0.1:8000/docs 에서 확인할 수 있습니다.

> `GET /rate/{code}` 는 실제 외부 API(`https://api.example.com/rates`)를 부르도록 되어 있어, 서버에서 직접 호출하면 외부에 닿지 못해 503 이 납니다. 이 엔드포인트의 정상 동작은 **테스트에서 모킹으로** 확인하는 것이 이 예제의 핵심입니다.

## 폴더 구조

```
13-TestingDeep/
├── pyproject.toml
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   ├── main.py               # FastAPI 앱 (health / quotes / rate)
│   └── services.py           # 외부 HTTP 호출 격리 (fetch_rate)
└── tests/
    ├── __init__.py
    ├── conftest.py           # AsyncClient 픽스처 + 상태 초기화(autouse)
    ├── test_health_and_quotes.py
    ├── test_parametrize.py
    └── test_rate_mock.py
```

## 커버리지(선택)

순수 pytest 로 모든 테스트가 돕니다. 커버리지까지 보고 싶다면 `pytest-cov` 를 추가로 깔면 됩니다.

```bash
uv add --dev pytest-cov
uv run pytest --cov=app --cov-report=term-missing
```
