"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.

명령의 의미를 풀면:
    - `uv run`            : uv가 가상환경 안에서 다음 명령을 실행
    - `uvicorn`           : 실제로 띄울 ASGI 서버
    - `app.main:app`      : `app/main.py` 파일 안의 `app` 변수
    - `--reload`          : 코드 변경 시 자동 재시작 (개발용)
"""

from fastapi import FastAPI
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# 응답 모델 (Pydantic)
# ---------------------------------------------------------------------------
# 응답 본문의 "모양"을 클래스로 명시한다.
# `BaseModel`을 상속하면 다음이 자동으로 처리된다.
#   1) 인스턴스를 만들 때 인자 타입 검증
#   2) FastAPI가 응답으로 돌려줄 때 자동 JSON 직렬화
#   3) `/docs`(Swagger UI)에 정확한 응답 스키마 표시
class HelloResponse(BaseModel):
    """`/hello/{name}` 라우트의 응답 본문 형식."""

    # 사용자에게 보여줄 인사 메시지.
    message: str
    # 인사 대상 이름 — 경로 매개변수 그대로.
    name: str


# ---------------------------------------------------------------------------
# FastAPI 인스턴스
# ---------------------------------------------------------------------------
# 이 객체가 우리 앱 전체의 루트.
# 라우트, 미들웨어, 의존성 등이 모두 이 객체에 등록된다.
# 생성자에 넘긴 메타데이터(title/description/version)는
# 자동 생성되는 문서 페이지(`/docs`, `/redoc`, `/openapi.json`)에 그대로 노출된다.
app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# 라우트 1 — 루트 경로
# ---------------------------------------------------------------------------
# `@app.get("/")`는 "GET / 요청을 이 함수가 처리한다"는 등록.
# 함수가 반환한 dict는 FastAPI가 자동으로 JSON으로 변환해 응답 본문에 담는다.
@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리.

    매우 단순한 환영 메시지를 JSON으로 돌려준다.

    예: `GET /` → `{"message": "Hello, FastAPI!"}`
    """
    return {"message": "Hello, FastAPI!"}


# ---------------------------------------------------------------------------
# 라우트 2 — 경로 매개변수 + Pydantic 응답 모델
# ---------------------------------------------------------------------------
# 경로의 `{name}`(중괄호)는 "이 자리는 변수다"라는 표시.
# 함수의 인자 `name: str`과 **이름이 같아야** FastAPI가 자동으로 연결해 준다.
# `response_model=HelloResponse`로 응답 형식을 명시하면
# 자동 문서의 Responses 섹션이 정확한 두 필드(`message`, `name`)로 그려진다.
@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    """경로 매개변수 `name`을 받아 한국어 인사말을 돌려준다.

    예: `GET /hello/Alice`
        → `{"message": "안녕하세요, Alice님!", "name": "Alice"}`
    """
    return HelloResponse(
        message=f"안녕하세요, {name}님!",
        name=name,
    )
