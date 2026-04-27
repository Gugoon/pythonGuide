# 04-HelloFastAPI

FastAPI 가이드 **04장 — 첫 프로젝트** 예제 코드입니다. `uv init`으로 시작한 가장 작은 형태의 FastAPI 프로젝트로, 다음 두 라우트가 정의돼 있습니다.

- `GET /` — 환영 메시지 (`{"message": "Hello, FastAPI!"}`)
- `GET /hello/{name}` — 경로 매개변수 `name`을 받아 한국어 인사를 돌려줌. 응답은 Pydantic 모델 `HelloResponse`로 명시.

본문 설명은 [`docs/04-first-project.md`](../../docs/04-first-project.md)에 있습니다. 이 폴더는 본문 마지막 시점의 **완성본**입니다.

## 폴더 구조

```
04-HelloFastAPI/
├── pyproject.toml         # 프로젝트 메타데이터 + 의존성
├── .python-version        # 이 프로젝트가 쓸 Python 버전 (3.13)
├── .gitignore             # 표준 Python 제외 규칙
├── README.md              # 이 파일
├── requirements.txt       # uv를 못 쓰는 환경용 대체 의존성 목록
└── app/
    ├── __init__.py        # 빈 파일 (패키지 표시)
    └── main.py            # FastAPI 앱 본체
```

> `uv sync` 또는 `uv add`를 처음 실행하면 `uv.lock`(의존성 잠금 파일)이 자동으로 생성됩니다. 본 저장소에는 포함하지 않았으므로 위 트리에는 표시하지 않았습니다.

## 실행 방법 — uv (권장)

[03장 설치 가이드](../../docs/03-installation.md)대로 Python 3.13 + uv가 깔려 있다고 가정합니다.

```bash
# 의존성 설치 (uv.lock이 있으면 그대로 복원)
uv sync

# 개발 서버 실행 (코드 변경 시 자동 재시작)
uv run uvicorn app.main:app --reload
```

성공하면 다음 비슷한 로그가 보입니다.

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## 동작 확인

브라우저나 다른 터미널에서 다음 주소를 열어 보세요.

- 루트: <http://127.0.0.1:8000/>
  ```json
  {"message": "Hello, FastAPI!"}
  ```
- 인사: <http://127.0.0.1:8000/hello/Alice>
  ```json
  {"message": "안녕하세요, Alice님!", "name": "Alice"}
  ```
- 자동 문서 (Swagger UI): <http://127.0.0.1:8000/docs>
- 자동 문서 (ReDoc): <http://127.0.0.1:8000/redoc>
- OpenAPI 명세 자체: <http://127.0.0.1:8000/openapi.json>

`curl`로도 확인 가능합니다.

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/hello/보성
```

서버를 종료하려면 실행 중인 터미널에서 `Ctrl+C`.

## 실행 방법 — pip + venv (uv를 못 쓰는 환경)

회사·학교 정책 등으로 uv 설치가 막혀 있을 때의 대체 절차입니다.

```bash
# 1) 가상환경 만들기
python3.13 -m venv .venv

# 2) 가상환경 켜기
source .venv/bin/activate

# 3) requirements.txt로 라이브러리 설치
pip install --upgrade pip
pip install -r requirements.txt

# 4) 서버 실행
uvicorn app.main:app --reload
```

종료는 똑같이 `Ctrl+C`. 가상환경에서 빠져나갈 때는 `deactivate`.

## 폴더를 새 위치로 복사해서 시작하고 싶다면

이 예제 폴더를 통째로 복사해 자기 작업 위치로 옮기고 싶을 때:

```bash
cp -R examples/04-HelloFastAPI ~/projects/my-hello-fastapi
cd ~/projects/my-hello-fastapi
uv sync
uv run uvicorn app.main:app --reload
```

## 참고

- 이 예제의 챕터: [`docs/04-first-project.md`](../../docs/04-first-project.md)
- 다음 챕터: [`docs/05-routing-content.md`](../../docs/05-routing-content.md)
- 용어 사전: [`docs/glossary.md`](../../docs/glossary.md)
