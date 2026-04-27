# 04. 첫 프로젝트 — Hello FastAPI

> **이 챕터의 목표**
> - 03장에서 5줄짜리 새너티 체크로 띄웠던 앱을, 본격적인 **첫 프로젝트** 형태로 다시 만든다.
> - `uv init`으로 표준 폴더 구조를 갖춘 프로젝트를 생성한다.
> - `pyproject.toml`이 무엇이고 어떤 정보가 들어 있는지 한 줄씩 읽어낼 수 있다.
> - `app/main.py`를 만들고, FastAPI 앱의 가장 작은 코드를 한 줄 한 줄 풀어 이해한다.
> - `uv run uvicorn app.main:app --reload` 명령의 각 부분이 무엇을 하는지 안다.
> - 자동 생성되는 `/docs`, `/redoc`, `/openapi.json` 세 페이지의 차이를 안다.
> - 경로 매개변수(`GET /hello/{name}`)와 Pydantic 모델 응답을 살짝 맛본다.
> - 동기 함수(`def`)와 비동기 함수(`async def`)의 차이를 입문자 수준에서 짚는다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 1~2시간 (직접 타이핑하며 따라할 때 기준)

> **전제**: 03장의 설치가 끝나 있어야 합니다. 즉, 다음 세 가지가 통하는 상태:
> - `python3.13 --version` → `Python 3.13.x`
> - `uv --version` → `uv 0.x.x`
> - `code --version` → VS Code 버전 출력

---

## 4.1 이 챕터의 큰 그림 — 우리가 만들 것

03장 마지막에서 우리는 다음 다섯 줄짜리 코드를 띄워봤습니다.

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}
```

이 다섯 줄은 환경이 잘 깔렸는지 확인하기 위한 **최소 검증**이었습니다. 한 파일에 모든 게 들어 있었고, 폴더 구조도 단순했죠.

이번 챕터에서는 같은 흐름을 **본격적인 프로젝트의 모양으로** 다시 만듭니다. 구체적으로 다음을 더합니다.

1. **표준 폴더 구조**: 모든 코드를 한 파일에 넣지 않고, `app/` 폴더 안에 `main.py`를 둡니다. 앞으로 라우터·모델·DB 코드가 늘어나면 `app/routers/`, `app/models/`처럼 자연스럽게 가지를 칠 수 있는 형태입니다.
2. **`pyproject.toml` 이해**: 03장에서 `uv init`으로 자동 생성된 이 파일을 한 줄씩 읽어보고, 의존성·메타데이터가 어떻게 기록되는지 살펴봅니다.
3. **추가 라우트**: 경로 매개변수(`/hello/{name}`)를 받는 라우트를 하나 더 만듭니다. 이 작은 변형이 "정적인 응답"에서 "사용자 입력에 반응하는 응답"으로 가는 첫걸음입니다.
4. **자동 문서 자세히 보기**: `/docs`, `/redoc`, `/openapi.json` 세 페이지의 정체와 쓰임을 정리합니다.
5. **Pydantic 모델 맛보기**: 응답을 그냥 `dict`로 돌려주지 않고, 작은 데이터 클래스로 감싸봅니다. 본격적인 Pydantic은 05장에서 다루지만, 미리 한 번 보고 넘어가면 다음 장이 훨씬 부드럽습니다.

이번 챕터를 마치면, 앞으로 모든 챕터에서 등장하는 "프로젝트를 새로 만들고 → 라우트 한두 개를 추가하고 → 띄워서 확인한다"는 사이클을 자기 손으로 반복할 수 있게 됩니다.

> **앞으로의 챕터와의 관계**: 05장(라우팅·Pydantic)·06장(DB)·07장(CRUD)에서는 모두 이 구조를 그대로 늘려 나갑니다. `app/main.py`에 직접 라우트를 추가하다가, 라우트가 많아지면 `app/routers/` 폴더로 나누고, DB가 들어오면 `app/db.py`·`app/models/`가 추가됩니다. 즉, **이 챕터의 골격이 끝까지 이어지는 뼈대**가 됩니다.

---

## 4.2 우리가 만들 프로젝트의 최종 모습

이번 챕터를 다 마치면 폴더는 다음과 같이 됩니다. 지금은 **이름만** 봐 두세요.

```
04-HelloFastAPI/
├── pyproject.toml         # uv가 만드는 프로젝트 설정 파일 (의존성·메타데이터)
├── uv.lock                # 의존성 잠금 파일 (정확한 버전·해시 기록)
├── .python-version        # 이 프로젝트가 쓸 Python 버전 ("3.13")
├── .gitignore             # git에 올리지 않을 파일·폴더 목록
├── README.md              # 프로젝트 설명·실행 방법
└── app/
    ├── __init__.py        # 빈 파일 (또는 한 줄 docstring) — "이 폴더는 패키지" 표시
    └── main.py            # FastAPI 앱 본체. 우리가 가장 자주 만질 파일.
```

각 항목을 한 줄로 정리하면:

| 파일/폴더 | 누가 만드는가 | 무엇인가 |
|-----------|---------------|----------|
| `pyproject.toml` | `uv init` | 프로젝트 메타데이터·의존성 목록 (사람이 읽는 표준 파일) |
| `uv.lock` | `uv add`·`uv sync` | 의존성의 정확한 버전·해시 잠금 (자동 관리) |
| `.python-version` | `uv init` | 이 프로젝트가 쓸 Python 버전을 적어둔 작은 텍스트 |
| `.gitignore` | 우리(또는 `uv init`) | git이 무시할 파일 목록 |
| `README.md` | 우리(또는 `uv init`) | 프로젝트 개요·실행법 |
| `app/__init__.py` | 우리 | "이 폴더를 Python 패키지로 취급하라"는 표시. 보통 비어 있음 |
| `app/main.py` | 우리 | FastAPI 앱 본체. 라우트와 `app` 객체가 여기 들어감 |

> **이 구조의 의도**: `app/` 안에 모든 코드가 들어 있으므로, 나중에 테스트 폴더(`tests/`)나 마이그레이션 폴더(`alembic/`)가 추가돼도 **앱 코드와 다른 코드가 섞이지 않습니다.** "코드 = `app/`" "프로젝트 메타 = 그 바깥"이라는 분리가 가독성과 배포의 단순함을 모두 가져옵니다.

---

## 4.3 프로젝트 폴더 만들기 — `uv init` 흐름

03장에서 이미 `uv init`을 한 번 해봤습니다. 이번에는 **실전 프로젝트**라는 마음으로 다시, 단계마다 출력 결과를 확인하며 진행합니다.

### 4.3.1 작업 위치 정하기

이 가이드는 홈 디렉터리 아래 `projects/`라는 작업 폴더를 두는 관례를 씁니다(없으면 만드세요). 다른 위치를 써도 무방합니다.

```bash
mkdir -p ~/projects
cd ~/projects
```

> **`mkdir -p`의 `-p`란?** 부모 폴더가 없어도 함께 만들고, 폴더가 이미 있어도 에러를 내지 않습니다. 안전한 표준 옵션입니다.

### 4.3.2 프로젝트 폴더 만들기

```bash
mkdir 04-HelloFastAPI
cd 04-HelloFastAPI
```

폴더 이름은 자유지만, 가이드의 예제 폴더 이름에 맞춰 `04-HelloFastAPI`를 권장합니다.

> **폴더 이름에 대시(`-`)가 있어도 되나요?** 됩니다. **폴더 이름**과 **Python 패키지 이름**은 별개입니다. 우리가 import할 패키지는 `app/`이라서 어떤 이름이든 상관없습니다. 단, 만약 `pyproject.toml`의 `name = "..."` 항목에 대시가 들어가면 자동으로 `_`로 바꿔 import하므로 그 정도만 알아두세요.

### 4.3.3 `uv init` 실행

이제 이 폴더를 uv 프로젝트로 초기화합니다.

```bash
uv init
```

실행 직후 출력은 대략 다음과 같습니다(uv 버전에 따라 약간 다를 수 있음).

```
Initialized project `04-hellofastapi`
```

폴더에는 다음 파일들이 생겨 있습니다.

```bash
ls -a
```

```
.        ..       .git/    .gitignore   .python-version   README.md   pyproject.toml   main.py
```

각 항목의 의미:

- **`.git/`**: uv가 자동으로 git 저장소를 초기화해 둡니다. 우리가 바로 git을 쓸 수 있도록 준비된 상태입니다.
- **`.gitignore`**: `__pycache__/`, `.venv/` 등 Python 프로젝트의 표준 제외 항목이 미리 들어 있습니다.
- **`.python-version`**: 이 프로젝트가 쓸 Python 버전이 적힌 작은 텍스트 파일.
- **`README.md`**: 빈 README 한 장.
- **`pyproject.toml`**: 프로젝트 설정 표준 파일. 다음 절에서 자세히 봅니다.
- **`main.py`**: uv가 만든 한 줄짜리 예시 스크립트. **우리는 이 파일을 곧 지웁니다** — FastAPI 앱은 `app/main.py`라는 다른 위치에 새로 만들 거라서요.

> **uv 버전에 따라 `main.py` 대신 `hello.py`가 생기기도 합니다.** 어느 쪽이든 우리가 안 쓸 파일이므로 다음 절에서 함께 정리합니다.

### 4.3.4 자동 생성된 예시 스크립트 지우기

루트의 `main.py`(또는 `hello.py`)는 우리가 만들 `app/main.py`와 이름이 헷갈릴 수 있으니 **지웁니다**.

```bash
rm -f main.py hello.py
```

> **`rm -f`의 `-f`란?** "force"의 줄임으로, 파일이 없어도 에러를 내지 않습니다. 둘 중 하나만 있어도 깔끔히 지워집니다.

### 4.3.5 `.python-version` 확인

```bash
cat .python-version
```

다음과 비슷한 한 줄이 보입니다.

```
3.13
```

이 한 줄이 의미하는 바: "이 폴더에 들어오면 uv는 Python 3.13으로 동작한다." `uv run` 계열 명령은 이 파일을 보고 어떤 Python을 써야 할지 결정합니다.

> **만약 다른 버전이 적혀 있다면** 03장의 Python 설치를 점검하세요. uv가 시스템에서 인식한 Python 중 가장 적합한 것을 골라 적기 때문에, 3.13이 깔려 있는데 3.12가 적혀 있다면 인식 문제일 수 있습니다. 그럴 땐 텍스트 에디터로 직접 `3.13`으로 수정해도 됩니다.

---

## 4.4 `pyproject.toml` 한 줄씩 읽기

이제 가장 중요한 파일을 살펴볼 차례입니다. 텍스트 에디터나 VS Code로 `pyproject.toml`을 열어 보세요.

```bash
code pyproject.toml
```

내용은 대략 이렇습니다(uv 버전에 따라 미세 차이가 있을 수 있음).

```toml
[project]
name = "04-hellofastapi"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

### 4.4.1 `pyproject.toml`이란

> **`pyproject.toml`이란?** 현대 Python 프로젝트의 **표준 설정 파일**입니다. 옛날에는 `setup.py`(빌드)·`requirements.txt`(의존성)·`setup.cfg`(메타데이터)·`MANIFEST.in`(파일 포함 규칙) 등이 따로 했던 일을 한 파일에 모은 것입니다. uv·pip·poetry·ruff·pytest 등 거의 모든 현대 Python 도구가 이 파일을 읽습니다.

> **TOML이란?** "Tom's Obvious Minimal Language"의 줄임. JSON·YAML과 비슷한 역할을 하지만, **사람이 읽고 쓰기 가장 편하게** 설계된 설정 형식입니다. `[섹션이름]`으로 묶고, `키 = 값` 형태로 적습니다. 따옴표·괄호 같은 세부 문법이 단순합니다.

### 4.4.2 항목별 의미

| 항목 | 의미 | 우리가 자주 만지는가 |
|------|------|-----------------------|
| `[project]` | 이 아래는 프로젝트 메타데이터 섹션이라는 표시 | 섹션 헤더 자체는 안 만짐 |
| `name = "04-hellofastapi"` | 패키지 이름. 외부에 배포할 때 쓰임 | 처음 한 번 |
| `version = "0.1.0"` | 프로젝트 버전. SemVer 권장 | 가끔 |
| `description = "..."` | 한 줄 설명 | 처음 한 번 |
| `readme = "README.md"` | 어떤 파일이 README인지 | 거의 안 만짐 |
| `requires-python = ">=3.13"` | 이 프로젝트가 요구하는 최소 Python 버전 | 거의 안 만짐 |
| `dependencies = []` | 이 프로젝트가 쓰는 외부 라이브러리 목록 | **자주 — 다만 직접 손대기보다 `uv add` 명령으로 자동 갱신됨** |

### 4.4.3 `name`을 읽기 좋게 다듬기

기본값으로 `04-hellofastapi`처럼 폴더 이름을 그대로 가져오는 경우가 많은데, **숫자로 시작**하거나 **대시가 들어간 이름**은 일부 도구에서 어색할 수 있습니다. 학습용 가이드 폴더라면 그대로 둬도 무방하지만, 깔끔하게 다듬고 싶다면 `name`을 바꿔 줍니다.

`pyproject.toml`을 열어 다음처럼 수정합니다.

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 입문 — 04장 Hello FastAPI 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

> **이름은 어떻게 정해야 하나요?** 영어 소문자 + 대시(`-`)가 가장 안전합니다. PyPI(공식 패키지 저장소)에 올릴 게 아니라면 어떤 이름이든 상관없습니다. 학습용으로는 `hello-fastapi`, `notes-api`, `blog-api` 정도가 무난합니다.

### 4.4.4 `requires-python`을 본격 이해하기

`requires-python = ">=3.13"`은 "이 프로젝트는 Python 3.13 이상에서 동작한다"는 선언입니다. uv는 이 줄을 읽고 다음을 합니다.

1. 가상환경을 만들 때 3.13 이상의 인터프리터를 골라 씁니다.
2. 의존성을 풀 때 3.13 이상에서만 동작하는 라이브러리도 후보로 포함합니다.

> **`>=3.13`과 `~=3.13` 같은 표기는 뭐가 다른가요?**
> - `>=3.13` — 3.13 이상 (3.14, 4.0도 OK)
> - `~=3.13` — 3.13 이상, 3.14 미만 (마이너 잠금)
> - `==3.13.*` — 3.13.x만
>
> 라이브러리를 PyPI에 배포한다면 신중히 정해야 하지만, 우리는 학습용이니 `>=3.13`이면 충분합니다.

### 4.4.5 다른 도구의 설정도 들어옵니다

지금은 `[project]` 섹션밖에 없지만, 프로젝트가 자라면 같은 파일에 다음 같은 섹션이 추가됩니다.

```toml
[tool.ruff]
line-length = 100

[tool.pytest.ini_options]
addopts = "-q"

[tool.uv]
# uv 자체에 대한 설정
```

이 가이드의 후반부 챕터에서 하나씩 등장합니다. 지금은 "한 파일에 여러 도구 설정이 다 모인다"는 사실만 기억하세요.

---

## 4.5 FastAPI와 Uvicorn 의존성 추가하기

이제 FastAPI와 Uvicorn을 이 프로젝트에 추가합니다.

```bash
uv add fastapi "uvicorn[standard]"
```

### 4.5.1 `uv add`가 한 번에 하는 일

이 명령은 **네 가지를 동시에** 처리합니다.

1. **가상환경 만들기**: 처음이면 `.venv/` 폴더를 자동 생성. (이미 있으면 그대로 사용)
2. **라이브러리 설치**: `fastapi`, `uvicorn[standard]`, 그리고 그 의존성들(`pydantic`, `starlette`, `anyio` 등)을 받아서 `.venv/`에 깝니다.
3. **`pyproject.toml` 갱신**: `[project]`의 `dependencies` 항목에 우리가 의도한 두 줄(`fastapi`, `uvicorn[standard]`)을 추가합니다.
4. **`uv.lock` 작성**: 깔린 모든 라이브러리의 정확한 버전·해시를 잠금 파일에 기록합니다.

명령이 끝난 뒤 `pyproject.toml`을 다시 열면 다음처럼 바뀝니다.

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 입문 — 04장 Hello FastAPI 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
```

(정확한 버전 숫자는 시점에 따라 다릅니다.)

### 4.5.2 `uvicorn[standard]`의 대괄호

> **`uvicorn[standard]`의 대괄호는 뭐죠?** "추가 옵션 묶음"을 뜻하는 표기입니다. 그냥 `uvicorn`만 받으면 핵심만 들어오고, `uvicorn[standard]`로 받으면 자주 쓰는 부가 라이브러리가 함께 깔립니다. 대표적으로 자동 리로드를 위한 `watchfiles`, 빠른 HTTP 파서인 `httptools` 등이 포함됩니다. 우리는 개발 중 `--reload`를 쓸 거라서 `[standard]`가 필요합니다. 따옴표(`"..."`)는 일부 셸이 대괄호를 잘못 해석하지 않게 막아주는 안전장치입니다.

### 4.5.3 깔린 것 확인

```bash
uv pip list
```

다음 같은 출력이 나오면 OK입니다(버전 숫자는 다를 수 있음).

```
Package           Version
----------------- --------
annotated-types   0.7.0
anyio             4.x.x
click             8.x.x
fastapi           0.115.x
h11               0.14.x
httptools         0.6.x
idna              3.x
pydantic          2.x.x
pydantic_core     2.x.x
python-dotenv     1.x.x
sniffio           1.3.x
starlette         0.x.x
typing_extensions 4.x.x
uvicorn           0.30.x
uvloop            0.x.x
watchfiles        0.x.x
websockets        13.x.x
```

`fastapi`와 `uvicorn`이 보이면 의존성 설치는 성공입니다. (다른 이름이 같이 보이는 것은 정상 — 그것들은 FastAPI/Uvicorn이 내부적으로 의존하는 라이브러리들입니다.)

### 4.5.4 `uv.lock`은 어떤 모양인가

`uv.lock` 파일은 사람이 직접 편집하지 않는 **자동 생성 파일**이지만, 어떻게 생겼는지 한 번 봐 두면 좋습니다.

```bash
head -n 30 uv.lock
```

다음과 비슷한 TOML이 보입니다.

```toml
version = 1
requires-python = ">=3.13"

[[package]]
name = "annotated-types"
version = "0.7.0"
source = { registry = "https://pypi.org/simple" }
sdist = { url = "...", hash = "sha256:..." }
wheels = [
    { url = "...", hash = "sha256:..." },
]

[[package]]
name = "fastapi"
version = "0.115.x"
...
```

각 라이브러리마다 **정확한 버전과 다운로드 URL, 해시값**이 적혀 있습니다. 다른 컴퓨터에서 `uv sync`를 돌리면 이 파일을 보고 **정확히 같은 것**들이 다시 깔립니다. 협업 시 "내 컴퓨터에선 됐는데"를 막아주는 핵심 파일입니다.

> **`uv.lock`은 git에 올려야 하나요?** 네. 애플리케이션(실행 파일) 프로젝트에서는 항상 커밋합니다. 우리가 만들 모든 프로젝트는 애플리케이션이므로, 의심하지 말고 커밋하세요. (라이브러리를 만드는 경우엔 토론의 여지가 있지만, 이 가이드의 범위 밖입니다.)

### 4.5.5 다른 컴퓨터에서 같은 환경 복원하기

만약 친구가 우리 프로젝트를 받아 자기 컴퓨터에서 띄우려 한다면, `git clone` 한 뒤 다음 한 줄이면 됩니다.

```bash
uv sync
```

이 명령은 **`uv.lock`을 그대로 복원**합니다. 즉, 가상환경을 만들고, 잠긴 정확한 버전으로 모든 라이브러리를 깝니다. **`uv add`와의 차이**는, `uv add`는 "새 의존성 추가 + 잠금 갱신"이고 `uv sync`는 "이미 잠금된 그대로 복원"이라는 점입니다.

| 명령 | 언제 쓰나 |
|------|-----------|
| `uv add <라이브러리>` | 새 라이브러리를 처음 추가할 때 |
| `uv sync` | 다른 컴퓨터·새 클론에서 잠금 그대로 복원할 때 |
| `uv lock` | 잠금 파일만 새로 만들 때 (의존성 변경 후 명시적으로 잠그고 싶을 때) |

지금은 첫 번째만 알면 됩니다.

---

## 4.6 `app/` 폴더와 `app/main.py` 만들기

이제 본격적인 코드 작성입니다.

### 4.6.1 왜 코드를 폴더에 모으나 (왜 `main.py` 한 파일이 아닌가)

03장에서는 모든 코드가 `app.py` 한 파일에 들어 있었습니다. 학습 1단계로는 충분하지만, 라우트가 늘고 DB가 들어오면 한 파일이 곧 수백 줄이 됩니다. 그 시점에 폴더로 나누려면 **import 경로가 모두 바뀌어** 수정이 번거롭습니다. 그래서 처음부터 작은 폴더 구조로 시작하는 게 안전합니다.

이 가이드의 표준 구조는 **`app/` 패키지 안에 코드가 들어가고**, 진입점 모듈은 `app/main.py`라는 약속입니다. 다음과 같은 장점이 있습니다.

1. **늘어날 자리가 마련돼 있음**: 라우터가 많아지면 `app/routers/`, 모델이 추가되면 `app/models/`, DB는 `app/db.py`처럼 같은 폴더 안에 자연스럽게 가지가 칩니다.
2. **import 경로가 일관됨**: 어디에서든 `from app.something import ...` 형식으로 부르게 됩니다. 한 파일짜리 구조에서 갈아탈 때 발생하는 import 깨짐이 없습니다.
3. **테스트와 분리됨**: 나중에 `tests/` 폴더가 추가돼도 `app/`과 깨끗하게 분리됩니다.
4. **Uvicorn 명령이 표준 형태가 됨**: `uvicorn app.main:app`이 어떤 프로젝트에서나 같은 의미를 갖게 됩니다.

### 4.6.2 폴더와 파일 만들기

다음 명령으로 한 번에 만듭니다.

```bash
mkdir app
touch app/__init__.py app/main.py
```

> **`touch`란?** 빈 파일을 만드는 명령(또는 이미 있는 파일의 수정 시각만 갱신). 여기서는 두 빈 파일을 만들기 위해 씁니다.

확인해 보면 폴더는 다음 모양이 됩니다.

```
04-HelloFastAPI/
├── app/
│   ├── __init__.py
│   └── main.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

### 4.6.3 `__init__.py`란

> **`__init__.py`란?** "이 폴더를 Python 패키지로 취급해라"라고 표시하는 특수 파일입니다. 보통은 **비워 두지만**, 패키지가 import될 때 자동 실행되는 코드를 적기도 합니다.

> **꼭 있어야 하나요?** Python 3에서는 "namespace package"라는 개념이 생겨서, `__init__.py` 없이도 폴더를 패키지처럼 쓸 수 있습니다. 하지만 IDE의 자동 완성·정적 분석 도구가 더 깔끔하게 인식하려면 빈 `__init__.py`를 두는 게 안전합니다. **이 가이드에서는 항상 빈 `__init__.py`를 둡니다.**

지금은 비어 있는 채로 두거나, 가독성을 위해 한 줄짜리 docstring만 적어 둡니다.

```python
"""hello-fastapi 앱 패키지."""
```

### 4.6.4 `app/main.py`에 가장 작은 FastAPI 앱 작성

이제 `app/main.py`에 다음 코드를 적습니다. **한 줄씩** 따라 적으면서, 다음 절(4.7)의 해설을 참고하세요.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI

# FastAPI 인스턴스 — 우리 앱 전체의 루트 객체.
# 이 객체에 라우트, 미들웨어, 의존성 등을 등록한다.
app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리.

    매우 단순한 환영 메시지를 JSON으로 돌려준다.
    """
    return {"message": "Hello, FastAPI!"}
```

저장합니다. 다음 절에서 한 줄씩 풀어 보겠습니다.

---

## 4.7 가장 작은 FastAPI 앱, 한 줄씩 풀이

위 코드는 짧지만 FastAPI의 가장 기본 패턴이 모두 들어 있습니다. 한 줄씩 보겠습니다.

### 4.7.1 `from fastapi import FastAPI`

`fastapi` 패키지에서 `FastAPI`라는 클래스를 가져옵니다. `FastAPI`가 우리 앱의 루트 객체를 만드는 클래스입니다.

> **import 한 줄이 무겁지 않나요?** `fastapi` 패키지 자체는 가볍습니다. 무거운 건 그 안에서 다시 import하는 `pydantic`·`starlette` 등인데, 그것들은 우리가 직접 import하지 않더라도 FastAPI가 동작할 때 자연스럽게 로드됩니다.

### 4.7.2 `app = FastAPI(...)`

`FastAPI()` 클래스를 호출해 인스턴스 하나를 만듭니다. 이 변수 이름은 관례상 **`app`**으로 짓습니다(다른 이름도 가능하지만, 모든 FastAPI 자료가 `app`을 가정합니다).

생성자에 넘긴 `title`, `description`, `version` 인자는 자동 생성될 API 문서(`/docs`, `/redoc`)에 그대로 노출됩니다. 즉, 다음 절에서 브라우저로 확인할 페이지 상단에 우리가 적은 제목·설명·버전이 보입니다.

> **인자를 안 넘기고 `FastAPI()`만 해도 되나요?** 됩니다. 다 기본값으로 채워집니다. 다만 자동 문서 페이지의 제목이 `FastAPI`라는 무미건조한 이름이 됩니다. 학습용이라도 한두 줄 채워두면 보기 좋고, 나중에 운영 환경에서 어떤 앱인지 식별에 도움이 됩니다.

### 4.7.3 `@app.get("/")` — 데코레이터

이 한 줄이 FastAPI 라우팅의 **핵심**입니다. 의미는 다음과 같습니다.

- `@`로 시작하는 표기를 **데코레이터**라고 부릅니다.
- `app.get(...)`은 "GET 메서드의 라우트를 만드는 함수"입니다.
- 인자 `"/"`는 "어느 URL 경로에서 동작할지" 지정합니다. 슬래시 하나는 루트 경로.
- 이 데코레이터는 **그 바로 아래의 함수**(`read_root`)를 "GET `/` 요청 처리기"로 등록합니다.

> **데코레이터(decorator)란?** 함수 위에 `@`로 붙는 표시입니다. "이 함수에 추가 기능을 입혀라"는 뜻입니다. 우리가 데코레이터를 직접 만들 일은 거의 없고, 이미 만들어진 데코레이터(여기서는 `@app.get`)를 갖다 쓰기만 합니다. [용어 사전 — 데코레이터](glossary.md#데코레이터-decorator)에 한 줄 더 자세한 설명이 있습니다.

같은 패턴으로 다른 HTTP 메서드도 등록합니다.

| 데코레이터 | 의미 |
|------------|------|
| `@app.get("/path")` | GET 요청 처리 (자료 가져오기) |
| `@app.post("/path")` | POST 요청 처리 (자료 새로 만들기) |
| `@app.put("/path")` | PUT 요청 처리 (자료 통째로 수정) |
| `@app.patch("/path")` | PATCH 요청 처리 (자료 일부 수정) |
| `@app.delete("/path")` | DELETE 요청 처리 (자료 삭제) |

> **HTTP 메서드 복습**: GET = 자료 가져오기, POST = 만들기, PUT/PATCH = 수정, DELETE = 삭제. 02장에서 설명한 그것입니다. 다섯 가지를 거의 다 쓰는 챕터는 07장 CRUD입니다.

### 4.7.4 `def read_root() -> dict[str, str]:`

처리기 함수의 본체입니다.

- **함수 이름 `read_root`**: 자유. FastAPI는 함수 이름 자체로 라우팅을 결정하지 않습니다(데코레이터의 `"/"`로 결정). 다만 자동 문서의 endpoint 이름으로 쓰이기 때문에, 의미가 잘 드러나는 이름을 짓는 게 좋습니다.
- **인자가 없음**: 이 라우트는 어떤 입력도 받지 않습니다. 곧 추가할 `/hello/{name}` 라우트는 인자가 있습니다.
- **반환 타입 힌트 `-> dict[str, str]`**: "이 함수는 문자열 키와 문자열 값을 가진 dict를 돌려준다"는 표시입니다. FastAPI는 이 타입 힌트를 읽어 자동 문서에 응답 형식을 적습니다.

> **타입 힌트 복습**: Python 3.5부터 도입된 표기로, 변수와 함수의 인자·반환에 "이건 이런 타입"이라고 적어두는 것입니다. 런타임에 강제하지는 않지만, FastAPI/Pydantic은 이 힌트를 읽어 자동 검증·문서화를 합니다.

> **`dict[str, str]`이 어색하다면**: Python 3.8까지는 `Dict[str, str]`(대문자, `from typing import Dict`)이었지만, 3.9부터 소문자 `dict[...]`를 그대로 쓸 수 있게 됐습니다. 우리는 3.13을 쓰므로 항상 소문자 형태를 씁니다.

### 4.7.5 `return {"message": "Hello, FastAPI!"}`

`dict`를 반환합니다. FastAPI는 이 dict를 **자동으로 JSON으로 직렬화해** 응답 본문(body)에 담습니다. 응답 헤더도 자동으로 `Content-Type: application/json`이 붙습니다.

> **dict가 어떻게 JSON이 되나요?** FastAPI 내부에서 `pydantic`을 통해 `json.dumps` 비슷한 변환이 일어납니다. dict뿐 아니라 list, Pydantic 모델, dataclass 등 거의 모든 기본 자료형이 JSON으로 자동 변환됩니다. 변환 못 하는 타입(예: 임의의 클래스 인스턴스)을 그대로 반환하면 에러가 납니다.

응답의 HTTP 상태 코드는 명시하지 않으면 **200 OK**가 기본값입니다.

---

## 4.8 서버 실행 — `uv run uvicorn app.main:app --reload`

이제 띄워볼 시간입니다. 프로젝트 루트(`04-HelloFastAPI/`)에서 다음을 실행합니다.

```bash
uv run uvicorn app.main:app --reload
```

성공하면 다음 비슷한 로그가 출력됩니다.

```
INFO:     Will watch for changes in these directories: ['/Users/.../04-HelloFastAPI']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

이 로그가 보이면 서버가 떠 있는 상태입니다. 이대로 두고 다음 절(4.9)에서 브라우저로 확인합니다.

### 4.8.1 명령의 각 부분 풀이

이 한 줄을 처음부터 끝까지 읽어 봅시다.

| 부분 | 의미 |
|------|------|
| `uv run` | "uv가 가상환경 안에서 다음 명령을 실행해" |
| `uvicorn` | 실제로 실행할 프로그램 (Uvicorn 서버) |
| `app.main:app` | "어떤 앱을 띄울지" — `app/main.py` 파일의 `app` 변수 |
| `--reload` | 코드를 수정하면 서버를 자동으로 다시 시작 |

각각을 좀 더 자세히.

### 4.8.2 `uv run`

> **`uv run <명령>`이란?** "이 명령을 가상환경 안에서 실행해 줘"라는 뜻의 uv 표준 접두사입니다. `uv run` 없이 그냥 `uvicorn ...`을 치면 시스템에 깔린 다른 uvicorn(있다면)을 부르거나, 없다면 `command not found`가 됩니다. uv 사용자는 거의 모든 실행 명령 앞에 `uv run`을 붙입니다.

뒤에 오는 명령이 무엇이든 상관없습니다.

```bash
uv run python --version
uv run pytest
uv run ruff check .
```

모두 같은 패턴입니다.

### 4.8.3 `uvicorn`

Uvicorn은 ASGI 서버, 즉 우리가 만든 FastAPI 앱을 실제로 띄워 HTTP 요청을 받아주는 프로그램입니다. FastAPI 자체는 "라우트 정의 + 처리 로직"이고, 그것을 8000번 포트에서 듣게 만드는 일은 Uvicorn이 합니다.

> **ASGI(Asynchronous Server Gateway Interface)란?** 비동기 Python 웹 앱과 서버 사이의 표준 약속입니다. FastAPI는 ASGI 앱이고, Uvicorn은 ASGI 서버입니다. 이 둘은 ASGI 약속을 통해 대화합니다. [용어 사전](glossary.md#asgi-asynchronous-server-gateway-interface) 참고.

### 4.8.4 `app.main:app` — 모듈 경로 형식

이 부분이 가장 헷갈리는 부분입니다. 형식은 **`폴더.파일이름:변수이름`**입니다.

- `app` — 폴더(=Python 패키지) 이름. 우리가 만든 `app/` 폴더입니다.
- `.main` — 그 안의 `main.py` 파일. 점(`.`)으로 폴더와 파일을 잇습니다.
- `:app` — 콜론 뒤는 그 파일 안의 **변수 이름**. 우리가 만든 `app = FastAPI(...)`의 `app`입니다.

따라서 전체 의미는 "**`app/main.py`라는 모듈 안의 `app`이라는 변수**(즉, FastAPI 인스턴스)를 띄워라"입니다.

> **헷갈리는 이유**: 폴더 이름과 변수 이름이 둘 다 `app`이라서 두 번 등장합니다. 만약 폴더가 `myapi/`였다면 명령은 `myapi.main:app`이 됩니다. **앞쪽 `app`은 폴더, 뒤쪽 `app`은 변수**라는 점을 한 번만 이해하면 헷갈리지 않습니다.

> **다른 예시**:
> - 단일 파일 `app.py` 안의 `app` 변수 → `app:app`
> - `myapp/server.py` 안의 `application` 변수 → `myapp.server:application`
> - `src/api/main.py` 안의 `app` → `src.api.main:app` (단, `src/`도 `__init__.py`가 있어야 패키지로 인식됨)

### 4.8.5 `--reload`

`--reload`는 **개발용 옵션**으로, 코드 파일이 바뀌면 서버를 자동으로 다시 시작합니다. 이게 없으면 코드를 고칠 때마다 직접 `Ctrl+C`로 끄고 다시 띄워야 해서 매우 번거롭습니다.

> **운영 환경에서도 쓰나요?** 절대 안 됩니다. `--reload`는 파일 시스템을 끊임없이 감시하므로 CPU 낭비가 있고, 안전하지도 않습니다. **개발 중에만 씁니다.** 운영 배포는 09장에서 Gunicorn + Uvicorn으로 다시 다룹니다.

### 4.8.6 `--host`와 `--port`

기본값은 `127.0.0.1:8000`입니다. 이를 바꾸고 싶다면:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

- `--host 127.0.0.1` (기본): 같은 컴퓨터에서만 접근 가능 (localhost).
- `--host 0.0.0.0`: 모든 네트워크 인터페이스에서 접근 가능. **다른 기기(예: 같은 와이파이의 휴대폰)에서 접속하고 싶을 때.**
- `--port 8000` (기본): 8000번 포트.

> **`localhost`와 `127.0.0.1`이 같은 건가요?** 사실상 같습니다. `127.0.0.1`은 "내 컴퓨터 자신"을 가리키는 IPv4 주소이고, `localhost`는 그 별칭입니다. 브라우저 주소창에 둘 중 어느 것을 쳐도 똑같이 동작합니다.

---

## 4.9 자동 문서 보기 — `/docs`, `/redoc`, `/openapi.json`

서버가 떠 있는 동안 브라우저에서 다음 세 주소를 차례로 열어 봅시다. **FastAPI의 가장 큰 매력**을 직접 보는 시간입니다.

### 4.9.1 첫 라우트 직접 호출 — `/`

브라우저 주소창에 다음을 칩니다.

```
http://127.0.0.1:8000/
```

화면에 다음 JSON이 보입니다.

```json
{"message":"Hello, FastAPI!"}
```

또는 다른 터미널에서 `curl`로 직접 호출해도 됩니다.

```bash
curl http://127.0.0.1:8000/
# 응답: {"message":"Hello, FastAPI!"}
```

### 4.9.2 `/docs` — Swagger UI

이게 FastAPI의 핵심 기능입니다. 다음 주소를 엽니다.

```
http://127.0.0.1:8000/docs
```

다음과 같은 페이지가 보입니다.

- 상단에 우리가 적은 **`Hello FastAPI` (제목)**, **0.1.0 (버전)**, **설명**이 표시됩니다.
- 아래에 등록된 모든 엔드포인트가 카드 형태로 나열됩니다. 지금은 `GET /`만 있습니다.
- 카드를 클릭해서 펼치면 입력 형식·응답 형식·예시가 자동으로 보입니다.
- **"Try it out" 버튼**을 누르면 브라우저에서 직접 API를 호출해 보고, 응답을 받아볼 수 있습니다.

> **Swagger UI란?** OpenAPI 명세를 보고 인터랙티브하게 테스트할 수 있는 웹 페이지입니다. 별도 앱(Postman 등) 없이 브라우저만으로 API 테스트가 가능합니다. FastAPI는 우리 코드를 분석해 OpenAPI 명세를 만들고, 그 명세를 보여주는 Swagger UI를 자동으로 `/docs`에 띄워줍니다.

이 한 페이지가 나오기까지 우리가 별도로 설정한 게 **하나도 없다**는 점에 주목하세요. 코드만 적었고, 나머지는 FastAPI가 합니다.

### 4.9.3 `/redoc` — ReDoc

같은 정보를 다른 디자인으로 보여주는 페이지입니다.

```
http://127.0.0.1:8000/redoc
```

- 좌측에 엔드포인트 목록, 우측에 자세한 설명·예시가 나옵니다.
- "Try it out" 같은 인터랙티브 요소는 없고, **읽기 좋은 정적 문서**에 가깝습니다.

> **`/docs`와 `/redoc` 중 뭘 쓰나요?** 개발 중에는 거의 항상 `/docs`(Swagger UI)를 씁니다. 직접 호출해 볼 수 있어서 편합니다. `/redoc`은 외부에 API 문서를 공개할 때 더 깔끔해 보여서 종종 쓰입니다. **두 페이지 모두 별도 설정 없이 그냥 같이 만들어집니다.** 한쪽이 부담스러우면 끌 수 있는 옵션도 있습니다(`FastAPI(redoc_url=None)`).

### 4.9.4 `/openapi.json` — OpenAPI 명세 자체

진짜 흥미로운 페이지는 이것입니다.

```
http://127.0.0.1:8000/openapi.json
```

브라우저에 긴 JSON 한 덩어리가 보입니다. 다음과 같이 생긴 무언가입니다.

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "Hello FastAPI",
    "description": "FastAPI 가이드 04장 — 첫 프로젝트 예제",
    "version": "0.1.0"
  },
  "paths": {
    "/": {
      "get": {
        "summary": "Read Root",
        "operationId": "read_root__get",
        "responses": { ... }
      }
    }
  },
  ...
}
```

> **OpenAPI란?** REST API의 명세를 JSON/YAML로 적는 표준 형식입니다. 옛 이름은 Swagger. 이 명세 한 장만 있으면 다른 도구가 자동으로 클라이언트 코드를 만들거나, 위에서 본 Swagger UI 같은 문서 페이지를 그릴 수 있습니다. **FastAPI의 `/openapi.json`은 모든 자동 문서의 원천**입니다. `/docs`와 `/redoc`은 결국 이 JSON을 가져와 그리는 페이지입니다.

이 명세는 외부 도구와 통합할 때 매우 유용합니다.

- **클라이언트 SDK 자동 생성**: `openapi-generator`로 TypeScript·Swift·Kotlin 등 다양한 언어의 클라이언트 코드를 자동 생성할 수 있습니다.
- **API 변경 추적**: 매 배포마다 `/openapi.json`을 저장하면, API가 어떻게 변했는지 자동으로 비교 가능합니다.
- **모의 서버**: Postman 등에서 OpenAPI 명세를 import해 응답을 흉내 내는 mock 서버를 만들 수 있습니다.

지금은 **존재만 알아두고**, 실전에서 필요해질 때 다시 펼쳐보면 됩니다.

---

## 4.10 작은 변형 — 경로 매개변수 추가하기

지금까지의 라우트는 입력이 없습니다. 한 단계 더 나가서 **사용자 입력**을 받아 응답을 바꾸는 라우트를 만들어 봅시다.

### 4.10.1 코드 추가

`app/main.py`를 다음처럼 수정합니다(기존 코드 아래에 새 라우트를 추가).

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}")
def hello_name(name: str) -> dict[str, str]:
    """경로 매개변수 `name`을 받아 인사말을 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!"}`
    """
    return {"message": f"안녕하세요, {name}님!"}
```

저장합니다. `--reload` 옵션을 켜뒀다면 서버가 자동으로 재시작됩니다.

### 4.10.2 동작 확인

브라우저에서:

```
http://127.0.0.1:8000/hello/Alice
```

응답:

```json
{"message":"안녕하세요, Alice님!"}
```

다른 이름도 시도해 보세요.

```bash
curl http://127.0.0.1:8000/hello/보성
# 응답: {"message":"안녕하세요, 보성님!"}
```

### 4.10.3 한 줄씩 풀이

```python
@app.get("/hello/{name}")
def hello_name(name: str) -> dict[str, str]:
    return {"message": f"안녕하세요, {name}님!"}
```

핵심 두 가지:

1. **경로의 `{name}` (중괄호)** — "이 자리는 변수다"라는 표시입니다. 클라이언트가 `/hello/Alice`로 요청하면 FastAPI가 `Alice`를 추출해서 함수 인자로 넘겨줍니다.
2. **함수 인자 `name: str`** — 경로의 `{name}`과 **이름이 일치**해야 합니다. 타입은 `str`로 지정. 다른 이름이면 매핑이 안 돼 에러가 납니다.

> **이름이 일치해야 한다고요?** 네. 경로의 `{name}`과 함수 인자 `name`이 같은 단어여야 FastAPI가 자동으로 연결해 줍니다. `{user_name}`이라고 적으면 함수 인자도 `user_name: str`이어야 합니다.

> **타입을 `int`로 하면?** `@app.get("/items/{item_id}")` + `def get_item(item_id: int)` 식으로 적으면, FastAPI는 URL의 `{item_id}` 부분을 자동으로 정수로 변환해 줍니다. 변환 실패(예: `/items/abc`)면 자동으로 422 에러를 돌려줍니다. **이게 FastAPI의 자동 검증입니다.**

### 4.10.4 자동 문서 다시 확인

`http://127.0.0.1:8000/docs`를 다시 열어 봅니다. 이제 두 엔드포인트가 보입니다.

- `GET /` — Read Root
- `GET /hello/{name}` — Hello Name

새 라우트의 카드를 펼치면 **"Parameters"** 섹션에 `name` 항목이 자동으로 나타납니다. "Try it out" → `name`에 값 입력 → "Execute"로 직접 호출도 됩니다. **우리가 별도로 적은 문서가 하나도 없는데** 이게 자동으로 만들어진다는 점을 기억하세요.

### 4.10.5 경로 매개변수가 여러 개일 때 (맛보기)

다음 챕터에서 본격적으로 다루지만, 경로 매개변수는 여러 개를 둘 수 있습니다.

```python
@app.get("/users/{user_id}/posts/{post_id}")
def get_user_post(user_id: int, post_id: int) -> dict[str, int]:
    return {"user_id": user_id, "post_id": post_id}
```

순서·이름이 일치하기만 하면 됩니다. 자세한 내용은 05장에서 라우팅을 깊이 다룰 때.

---

## 4.11 응답을 dict 대신 Pydantic 모델로 (맛보기)

지금까지 우리는 응답을 **`dict`**로 만들어 돌려줬습니다. 이 방식은 짧은 예제엔 편하지만, 응답의 형태가 코드 어디에서 결정되는지 한눈에 보기 어렵고, 자동 문서의 응답 스키마도 빈약하게 그려집니다(`{"message": "string"}` 정도).

해결책은 **Pydantic 모델**로 응답 형태를 명시하는 것입니다. 본격적인 Pydantic은 05장에서 다루지만, 한 번 맛만 보고 갑니다.

### 4.11.1 코드 수정

`app/main.py`를 다음처럼 한 번 더 확장합니다.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI
from pydantic import BaseModel


# 응답 데이터의 모양을 클래스로 명시한다.
# `BaseModel`을 상속한 클래스의 인스턴스는 FastAPI가 자동으로 JSON으로 직렬화한다.
class HelloResponse(BaseModel):
    """`/hello/{name}` 라우트의 응답 본문 형식."""

    message: str
    name: str


app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리."""
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    """경로 매개변수 `name`을 받아 `HelloResponse`를 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!", "name": "Alice"}`
    """
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

저장합니다.

### 4.11.2 한 줄씩 풀이

```python
from pydantic import BaseModel


class HelloResponse(BaseModel):
    message: str
    name: str
```

- `BaseModel`은 Pydantic이 제공하는 **데이터 모델 베이스 클래스**입니다.
- 상속한 클래스의 **클래스 변수**(여기서는 `message`, `name`)를 **필드**로 봅니다.
- 각 필드에 타입 힌트(`: str`)가 있어, "어떤 타입의 값을 가질 수 있는지" Pydantic이 압니다.
- 이렇게 정의된 클래스는 다음 같은 일을 자동으로 해 줍니다.
  1. 인스턴스를 만들 때 인자 검증 (`HelloResponse(message=123, name="A")` → 에러)
  2. JSON으로 직렬화 (FastAPI가 자동으로 호출)
  3. 자동 문서의 응답 스키마에 정확한 모양 표시

```python
@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

- `response_model=HelloResponse` — 데코레이터에 추가된 인자. "이 라우트의 응답은 `HelloResponse` 형태다"라고 FastAPI에 알려줍니다.
- 함수 반환은 그 모델의 인스턴스를 만들어 돌려줍니다.

> **`response_model` 인자가 꼭 필요한가요?** 함수의 반환 타입 힌트(`-> HelloResponse`)만으로도 FastAPI는 자동 문서를 그립니다. 다만 **`response_model`을 명시하면 추가 안전망**이 생깁니다 — FastAPI가 응답을 그 모델로 한 번 더 검증·필터링합니다(예: 모델에 없는 필드는 잘라내기). 학습 단계에서는 둘 다 적어두는 걸 권장합니다. 자세한 차이는 05장에서.

### 4.11.3 자동 문서 다시 확인

`http://127.0.0.1:8000/docs`를 다시 열고 `GET /hello/{name}` 카드를 펼치면, **응답 스키마**(Responses 섹션)가 다음처럼 정확해집니다.

```
{
  "message": "string",
  "name": "string"
}
```

이전엔 `additionalProperties` 같은 모호한 표현이 들어갔지만, 이제는 **정확한 두 필드**가 명시됩니다. **클라이언트(프론트엔드·모바일) 개발자가 이 문서만 보고도 응답 형식을 정확히 알 수 있다**는 게 핵심 가치입니다.

> **본격적인 Pydantic은 05장에서**: 요청 본문 검증(`POST /users` 같은 곳), 필드 제약(`min_length=3` 등), 복합 모델, 옵셔널 필드, 모델 중첩 등 풍부한 주제가 있습니다. 이 챕터에서는 "응답에도 모델을 쓸 수 있다"는 사실만 가지고 넘어갑니다.

---

## 4.12 동기 함수(`def`) vs 비동기 함수(`async def`)

여기서 잠깐 옆길로 새서, FastAPI 입문자가 가장 자주 헷갈리는 주제 하나를 짚고 갑니다.

### 4.12.1 두 모양 다 지원된다

지금까지 우리는 **동기** 함수(`def`)로 라우트를 만들었습니다.

```python
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}
```

FastAPI는 **`async def`**도 똑같이 지원합니다.

```python
@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Hello, FastAPI!"}
```

겉보기 차이는 `async` 한 단어뿐. 동작도 거의 같습니다 — 위 단순한 라우트에서는 **차이를 체감할 일이 없습니다.**

### 4.12.2 차이는 어디서 나오나

`async def`의 진가는 **함수 안에 `await`가 등장할 때** 나옵니다.

```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await db.fetch_user(user_id)   # ← DB가 응답을 줄 때까지 잠깐 비킨다
    return user
```

`await`이 걸린 줄에서 **이 함수는 잠깐 멈추고**, **그 시간에 다른 요청이 처리됩니다.** 한 서버가 동시에 많은 요청을 다룰 수 있는 비결이 이 비동기입니다.

> **비동기(async/await) 짧게 다시**:
> - **동기**: 한 줄을 끝내야 다음 줄로 간다. DB가 0.5초 걸리면 그동안 다른 일을 못 한다.
> - **비동기**: `await`이 걸린 곳에서 잠깐 비키고 다른 요청을 처리한다. 기다리는 시간이 많은 백엔드에서 큰 효과.
>
> 자세한 정의는 [용어 사전](glossary.md#비동기--동기-async--sync)에 있습니다.

### 4.12.3 그럼 우리는 뭘 써야 하나

**입문 단계의 결론**: 함수 안에 `await`를 쓸 일이 있으면 `async def`, 아니면 `def`로 써도 됩니다. FastAPI는 둘 다 잘 처리합니다.

다만 이 가이드의 약속은 다음과 같습니다.

- **DB·외부 API·파일 I/O를 호출하는 라우트는 `async def`로 작성한다** (06장부터 SQLAlchemy 비동기를 쓰면서 본격화).
- **순수 계산만 하는 작은 라우트는 `def`로 적어도 무방하다** (이 챕터의 라우트들이 그 예).
- **일관성을 위해 한 프로젝트 안에서는 거의 다 `async def`로 통일하는 패턴**도 흔하다 (실무 권장).

### 4.12.4 한 가지 함정

**`async def` 함수 안에서 `time.sleep()` 같은 동기 블로킹 호출을 쓰면 큰일납니다.** 그 시간 동안 서버 전체가 멈춥니다(이벤트 루프가 블로킹). 비동기에서는 항상 `await asyncio.sleep(...)`처럼 비동기 짝을 써야 합니다.

이 주제는 06장에서 비동기 DB를 다룰 때 다시 나옵니다. 지금은 "**async 함수에서 동기 블로킹 함수를 부르면 안 된다**"는 한 줄만 기억하세요.

> **이 챕터에서 굳이 `async def`로 안 쓴 이유**: 라우트 안에서 `await`을 쓸 일이 없으므로 둘 다 동작이 같습니다. 입문자에게는 처음 보는 키워드를 줄이는 쪽이 낫다고 판단했습니다. 06장부터는 자연스럽게 `async def`가 등장합니다.

---

## 4.13 서버 멈추기 / 다시 켜기

### 4.13.1 멈추기 — `Ctrl+C`

서버가 떠 있는 터미널에서 **`Ctrl+C`** 한 번을 누릅니다(`Cmd+C`가 아닙니다 — macOS에서도 터미널 종료 신호는 `Ctrl+C`).

```
^C
INFO:     Shutting down
INFO:     Waiting for application shutdown.
INFO:     Application shutdown complete.
INFO:     Finished server process [12346]
INFO:     Stopping reloader process [12345]
```

이런 메시지가 나오면 정상 종료입니다.

> **`Ctrl+C`를 두 번 누르면?** 거의 똑같이 종료되지만, 이미 종료 절차가 진행 중일 때 두 번 누르면 강제 종료가 될 수 있습니다(SIGINT 신호가 두 번 가서). 한 번만 누르고 잠깐 기다리는 게 안전합니다.

### 4.13.2 다시 켜기

같은 명령을 다시 실행합니다.

```bash
uv run uvicorn app.main:app --reload
```

코드가 그대로 보존돼 있다면 1~2초 안에 다시 떠 있습니다.

### 4.13.3 새 터미널에서 작업하기

서버가 떠 있는 터미널은 그 자체로 점유 상태입니다. 그 안에서 다른 명령을 치려면 일단 서버를 끄거나, **새 터미널을 하나 더 엽니다.**

- VS Code: 우상단의 `+` 아이콘 또는 `Ctrl+\`` 단축키로 통합 터미널을 추가.
- macOS Terminal: `Cmd+T`로 새 탭.
- iTerm2: `Cmd+T`로 새 탭, `Cmd+D`로 분할.

새 터미널에서 `cd`로 같은 프로젝트 폴더에 들어간 뒤 `curl`이나 `git` 같은 다른 명령을 칠 수 있습니다.

### 4.13.4 백그라운드 실행은?

`&`로 백그라운드 실행할 수도 있지만, 학습 단계에서는 **추천하지 않습니다.** 로그가 어느 터미널에서 나오는지 추적하기 어려워지고, 종료할 때도 PID를 찾아 `kill`해야 합니다. 그냥 한 터미널 = 한 서버 흐름을 유지하는 게 깔끔합니다.

---

## 4.14 트러블슈팅 — 자주 만나는 에러

### 4.14.1 `Error loading ASGI app. Could not import module "app.main".`

```
ERROR:    Error loading ASGI app. Could not import module "app.main".
```

가장 흔한 원인은 **현재 디렉터리**입니다. `uvicorn app.main:app` 명령은 "현재 폴더에 `app/` 폴더가 있고, 그 안에 `main.py`가 있다"고 가정합니다. 다른 폴더에서 명령을 치면 `app` 모듈을 못 찾습니다.

해결:

```bash
cd 04-HelloFastAPI    # 프로젝트 루트로 이동
uv run uvicorn app.main:app --reload
```

또 다른 원인은 **`app/__init__.py`가 없는 경우**입니다. 빈 파일이라도 반드시 있어야 `app/`이 패키지로 인식됩니다.

```bash
touch app/__init__.py
```

### 4.14.2 `Attribute "app" not found in module "app.main".`

```
ERROR:    Attribute "app" not found in module "app.main".
```

`app/main.py` 안에 `app = FastAPI(...)` 줄이 빠져 있거나, 변수 이름이 다른 경우입니다. 명령의 콜론 뒤(`:app`)와 코드의 변수 이름이 일치해야 합니다. `app`이 아니라 `application`으로 적었다면 명령을 `app.main:application`으로 바꾸거나, 코드를 `app`으로 통일하세요.

### 4.14.3 `[Errno 48] Address already in use` 또는 `[Errno 98] Address already in use`

```
ERROR:    [Errno 48] Address already in use
```

8000번 포트를 다른 프로세스(거의 항상 이전에 띄워두고 안 끈 uvicorn)가 쓰고 있습니다.

해결 방법 두 가지:

```bash
# 1) 8000을 쓰는 프로세스 찾아서 종료
lsof -i :8000
# PID를 확인해 kill (예: kill 12345)

# 2) 다른 포트로 띄우기
uv run uvicorn app.main:app --reload --port 8001
```

### 4.14.4 `ModuleNotFoundError: No module named 'fastapi'`

가상환경 안에 FastAPI가 깔리지 않았거나, 다른 Python을 쓰고 있을 때 납니다.

해결:

```bash
# 프로젝트 폴더에서
uv add fastapi "uvicorn[standard]"
# 그래도 안 되면
uv sync
```

또는 명령을 `uv run` 없이 쳤을 가능성. **항상 `uv run` 접두사를 잊지 마세요.**

```bash
# 잘못된 호출 (시스템 Python을 봄)
uvicorn app.main:app --reload
# 올바른 호출
uv run uvicorn app.main:app --reload
```

### 4.14.5 `--reload`인데 코드를 고쳐도 반영이 안 됨

대부분 두 가지 원인 중 하나입니다.

1. **저장(Save)을 안 한 경우**. VS Code에서 파일 탭에 점(●)이 보이면 미저장 상태. `Cmd+S`(macOS) 또는 `Ctrl+S`(Linux)로 저장.
2. **`uvicorn[standard]`가 아니라 그냥 `uvicorn`만 깔린 경우**. `--reload`에는 `watchfiles`가 필요한데, `[standard]` 묶음에 들어 있습니다.
   ```bash
   uv add "uvicorn[standard]"
   ```

### 4.14.6 `/docs`가 404로 나옴

```
{"detail":"Not Found"}
```

거의 100% **주소 오타**입니다. 정확히 `/docs`(슬래시 포함)인지 확인하세요. 또 다른 가능성으로, `FastAPI(docs_url=None)`처럼 docs를 일부러 끈 코드일 수도 있습니다. 우리 코드에는 그런 옵션이 없으니 보통 오타입니다.

### 4.14.7 한글이 응답에서 깨져 보임

이 가이드의 코드대로라면 한글이 그대로 출력돼야 합니다. 만약 깨져 보인다면:

- **터미널 인코딩**: macOS·최신 Linux는 UTF-8 기본. Windows CMD는 인코딩 문제가 잦으니 WSL2 권장.
- **브라우저**: 거의 모든 모던 브라우저는 UTF-8 기본. 의심되면 페이지 인코딩을 UTF-8로 바꿔 보세요.

### 4.14.8 VS Code가 `import fastapi`를 빨간 줄로 표시함

라이브러리는 깔렸는데 VS Code가 다른 인터프리터(예: 시스템 Python)를 보고 있는 상태입니다.

해결:

1. `Cmd+Shift+P`(macOS) / `Ctrl+Shift+P`(Linux) → **`Python: Select Interpreter`**.
2. 후보 중 `.venv` 안의 Python을 고릅니다 (`./.venv/bin/python` 같은 경로).
3. VS Code 창을 한 번 닫았다가 다시 열면 더 확실히 적용됩니다.

03장에서 이미 다뤘지만, 새 프로젝트마다 한 번씩 해줘야 합니다.

---

## 4.15 이 챕터의 변경 내역과 최종 코드

이번 챕터의 마지막 시점에서 `app/main.py`는 다음 모양이어야 합니다.

```python
"""FastAPI 앱 엔트리 모듈.

`uv run uvicorn app.main:app --reload` 명령으로 띄울 때
이 파일의 `app` 변수가 진입점이 된다.
"""

from fastapi import FastAPI
from pydantic import BaseModel


# 응답 데이터의 모양을 클래스로 명시한다.
# `BaseModel`을 상속한 클래스의 인스턴스는 FastAPI가 자동으로 JSON으로 직렬화한다.
class HelloResponse(BaseModel):
    """`/hello/{name}` 라우트의 응답 본문 형식."""

    message: str
    name: str


app = FastAPI(
    title="Hello FastAPI",
    description="FastAPI 가이드 04장 — 첫 프로젝트 예제",
    version="0.1.0",
)


@app.get("/")
def read_root() -> dict[str, str]:
    """루트 경로(`/`) GET 요청 처리.

    매우 단순한 환영 메시지를 JSON으로 돌려준다.
    """
    return {"message": "Hello, FastAPI!"}


@app.get("/hello/{name}", response_model=HelloResponse)
def hello_name(name: str) -> HelloResponse:
    """경로 매개변수 `name`을 받아 `HelloResponse`를 돌려준다.

    예: `GET /hello/Alice` → `{"message": "안녕하세요, Alice님!", "name": "Alice"}`
    """
    return HelloResponse(message=f"안녕하세요, {name}님!", name=name)
```

`pyproject.toml`은 다음 모양이어야 합니다(버전 숫자는 시점에 따라 다름).

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "FastAPI 가이드 04장 — 첫 프로젝트 예제"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]
```

이 두 파일이 위 모양이고, `uv run uvicorn app.main:app --reload`가 에러 없이 떠서 `/`, `/hello/Alice`, `/docs`가 모두 응답한다면 이 챕터는 완성입니다.

> **완성된 예제 폴더**: 본 가이드 저장소의 `examples/04-HelloFastAPI/`에 같은 모양으로 정리되어 있습니다. 직접 친 코드가 동작하지 않으면 그쪽과 비교해 보세요.

---

## 4.16 이 챕터 체크리스트

다음을 모두 통과하면 다음 챕터로 넘어갈 준비가 된 것입니다.

- [ ] `~/projects/04-HelloFastAPI` 폴더를 만들고 `uv init`을 실행했다.
- [ ] `pyproject.toml`이 무엇인지, 어떤 항목이 들어 있는지 한 줄로 설명할 수 있다.
- [ ] `uv add fastapi "uvicorn[standard]"`로 의존성을 추가하고 `uv.lock`이 생긴 것을 확인했다.
- [ ] `app/__init__.py`가 빈 파일로 존재한다.
- [ ] `app/main.py`에 `FastAPI` 인스턴스 생성 + 두 개의 라우트(`/`, `/hello/{name}`) + Pydantic `HelloResponse` 모델이 들어 있다.
- [ ] `uv run uvicorn app.main:app --reload`로 서버가 8000번 포트에 떴다.
- [ ] 브라우저에서 `http://127.0.0.1:8000/`이 JSON을 돌려준다.
- [ ] 브라우저에서 `http://127.0.0.1:8000/hello/Alice`가 한국어 인사를 돌려준다.
- [ ] `http://127.0.0.1:8000/docs`(Swagger UI), `/redoc`(ReDoc), `/openapi.json` 세 페이지가 모두 보인다.
- [ ] `Ctrl+C`로 서버를 정상 종료할 수 있다.
- [ ] `app.main:app` 명령의 의미("`app/main.py` 파일의 `app` 변수")를 자기 말로 설명할 수 있다.

위가 모두 통과하면 **이 챕터의 본문은 완료**입니다. 다음 챕터(05)에서는 같은 골격 위에 라우팅과 Pydantic을 본격적으로 다룹니다.

---

## 4.17 이 챕터 요약

- 03장의 5줄 새너티 체크에서 출발해, **표준 폴더 구조**(`app/main.py`)를 갖춘 첫 프로젝트로 확장했다.
- `uv init`으로 `pyproject.toml`·`.python-version`·`.gitignore` 등이 자동 생성되며, 이 파일들이 프로젝트의 표준 메타데이터다.
- `uv add fastapi "uvicorn[standard]"` 한 줄로 가상환경·라이브러리 설치·잠금 파일 작성이 동시에 처리된다.
- FastAPI 앱의 핵심 패턴은 **`app = FastAPI(...)` + 데코레이터(`@app.get(...)`) + 처리기 함수**의 세 박자다.
- `uv run uvicorn app.main:app --reload`의 의미: "uv 환경 안에서 Uvicorn으로 `app/main.py`의 `app` 변수를 띄우고, 코드 변경 시 자동 재시작."
- FastAPI는 `/docs`(Swagger UI), `/redoc`(ReDoc), `/openapi.json`(원천 명세) 세 페이지를 자동 생성한다. 이게 FastAPI의 핵심 차별점이다.
- 경로 매개변수는 `@app.get("/hello/{name}")` + `def hello_name(name: str)`처럼 **이름 일치**로 자동 매핑된다.
- 응답을 `dict` 대신 `BaseModel` 모델로 돌려주면 자동 문서의 응답 스키마가 정확해지고, 이후 챕터의 검증·필터링 기능과 자연스럽게 이어진다.
- `def`와 `async def`는 둘 다 라우트로 쓸 수 있다. 입문 단계에서는 `await`이 필요할 때만 `async def`를 쓰는 게 단순하다.
- `Ctrl+C`로 서버를 끄고, 같은 명령으로 다시 띄운다.

다음 챕터에서는 같은 골격 위에 **여러 종류의 요청 입력**(쿼리 스트링, 본문)과 **본격적인 Pydantic 모델**(요청 검증, 필드 제약, 모델 중첩)을 다룹니다.

---

← [03. 설치 가이드](03-installation.md) | 다음 문서로 이동: **[05. 라우팅과 Pydantic →](05-routing-content.md)**
