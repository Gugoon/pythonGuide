# 16-ErrorLogging — 에러 핸들링·로깅 심화 예제

FastAPI 가이드 [16장 에러 핸들링·로깅 심화](../../docs/16-error-logging.md)의 완성본입니다. 커스텀 예외 클래스, 일관된 에러 응답 스키마, 요청 ID 미들웨어(X-Request-ID), 표준 라이브러리 `logging` 설정을 한 프로젝트에 담았습니다. 데이터베이스는 등장하지 않습니다(주제에 집중하기 위해 인메모리 dict 사용).

## 사용 기술

- Python 3.13
- FastAPI 0.115+
- 표준 라이브러리 `logging` (structlog 는 12장 참고)
- pytest + pytest-asyncio + httpx (테스트)
- uv (패키지/가상환경 매니저)

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

## 테스트 실행

```bash
uv run pytest -v
```

## 폴더 구조

```
16-ErrorLogging/
├── pyproject.toml
├── uv.lock                    (uv sync 후 생성)
├── .python-version
├── .gitignore
├── README.md
└── app/
│   ├── __init__.py
│   ├── main.py                # 앱 조립 + 시연 엔드포인트
│   ├── errors.py              # 커스텀 예외 + 에러 스키마 + 전역 핸들러
│   ├── middleware.py          # 요청 ID(X-Request-ID) 미들웨어
│   ├── request_context.py     # 요청 ID 를 담는 ContextVar
│   └── logging_config.py      # 표준 logging 설정(포매터·핸들러·필터)
└── tests/
    ├── __init__.py
    ├── conftest.py            # AsyncClient 픽스처
    └── test_errors.py         # 정상·에러·요청 ID 통합 테스트
```

## 엔드포인트

| 메서드 | 경로 | 설명 | 결과 |
|--------|------|------|------|
| `GET` | `/health` | 헬스 체크 | 200 |
| `GET` | `/items/{item_id}` | 단건 조회 | 200 / 404(커스텀 예외) |
| `POST` | `/orders` | 주문 | 200 / 404 / 409 / 422 |
| `GET` | `/boom` | 예상 못 한 예외 시연 | 500 |

## 일관된 에러 응답 모양

모든 에러는 같은 JSON 스키마로 나갑니다.

```json
{
  "error": {
    "code": "resource_not_found",
    "message": "item 9999 를 찾을 수 없습니다",
    "detail": { "resource": "item", "id": 9999 },
    "request_id": "ae510f2727354c37a1bdecbca61e2033"
  }
}
```

- `code` — 기계가 분기할 짧은 식별자
- `message` — 사람이 읽는 한 줄 설명
- `detail` — 부가 정보(검증 에러 목록 등). 없으면 `null`
- `request_id` — 이 에러가 난 요청의 ID. 응답 헤더 `X-Request-ID` 와 같으며, 서버 로그와 대조할 수 있습니다.

## 직접 호출해 보기

```bash
# 정상
curl -i http://127.0.0.1:8000/items/1

# 커스텀 404
curl -i http://127.0.0.1:8000/items/9999

# 검증 실패(422)
curl -i -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "quantity": 999}'

# 비즈니스 규칙 위반(409, 2번 상품은 재고 0)
curl -i -X POST http://127.0.0.1:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"item_id": 2, "quantity": 1}'

# 내부 오류(500) — 응답 본문에 내부 구현은 안 새고 request_id 만
curl -i http://127.0.0.1:8000/boom

# 요청 ID 전파 — 보낸 X-Request-ID 가 그대로 응답 헤더로 돌아온다
curl -i http://127.0.0.1:8000/health -H "X-Request-ID: my-trace-1"
```
