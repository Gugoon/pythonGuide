# 03. 설치 가이드 (macOS / Linux)

> **이 챕터의 목표**
> - macOS 또는 Linux에 **Python 3.13**과 **uv**를 설치한다.
> - 코드 에디터(VS Code)를 FastAPI 개발에 맞게 세팅한다.
> - 가상환경을 만들고 FastAPI 라이브러리를 설치한 뒤, 가장 짧은 "Hello FastAPI" 한 줄을 띄워 환경이 정상인지 검증한다.
> - Windows에서 따라할 때의 권장 경로(WSL2)를 짧게 안내한다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 30분 ~ 1시간 (Python·VS Code 미설치 시 다운로드 시간 포함)

---

## 3.1 이 챕터에서 깔 도구 한눈에

본격적으로 명령어를 치기 전에, 이 챕터에서 어떤 도구를 어떤 순서로 깔지 큰 그림부터 잡고 가겠습니다.

| 순서 | 도구 | 역할 | 한 줄 설명 |
|------|------|------|------------|
| 1 | **Python 3.13** | 언어 + 표준 런타임 | 우리가 짤 모든 코드를 실행하는 인터프리터 |
| 2 | **uv** | 패키지/가상환경 매니저 | "어떤 라이브러리를 어느 버전으로 깔지"를 빠르게 관리 |
| 3 | **VS Code** | 코드 에디터 | 코드를 짜고 디버깅하는 작업 환경 |
| 4 | (검증용) **FastAPI + Uvicorn** | 1번 검증 | 환경이 잘 깔렸는지 한 줄짜리 앱으로 확인 |

순서가 곧 의존 관계입니다. **Python이 있어야 → uv가 의미가 있고 → 그 위에 FastAPI가 동작합니다.** VS Code는 어느 단계에서 깔든 상관없지만, 이 챕터에서는 마지막에 다룹니다.

> **인터프리터(interpreter)란?** 우리가 작성한 Python 코드(텍스트 파일)를 한 줄씩 읽어 실제로 실행해 주는 프로그램입니다. 우리가 깔 "Python 3.13"이 사실은 이 인터프리터 프로그램입니다. 터미널에서 `python3` 명령을 치면 깔려 있는 인터프리터가 실행되는 것입니다.

> **패키지 매니저(package manager)란?** 외부 라이브러리(예: `fastapi`, `sqlalchemy`)를 인터넷에서 받아 우리 프로젝트에 설치·업그레이드·삭제해 주는 도구입니다. Python에는 표준 도구로 `pip`가, 차세대 도구로 `uv`가 있습니다. 이 가이드는 **uv를 1순위**로 씁니다.

> **에디터(editor)란?** 코드를 작성·편집하는 텍스트 편집기입니다. 메모장도 에디터지만, 개발자가 쓰는 에디터는 코드 자동 완성·문법 색칠·디버깅 같은 기능이 더 많습니다. 이 가이드는 **VS Code**를 권장합니다.

### 3.1.1 왜 이 조합인가

- **Python 3.13**: 2024년 10월 정식 출시된 가장 최신 안정 버전. 새 프로젝트는 가능하면 가장 최신을 쓰는 게 미래 호환에 유리합니다(라이브러리들도 새 버전을 계속 지원하기 때문).
- **uv**: `pip`/`venv`/`pip-tools`가 따로 하던 일을 한 도구로 묶었고, 같은 일을 10~100배 빠르게 합니다. 명령 체계도 일관됩니다.
- **VS Code**: 무료, 가볍고, Python 확장 생태계가 가장 풍부합니다. PyCharm Community도 좋지만, 이 가이드는 VS Code 기준으로 스크린샷·설명을 통일합니다.

> **선택지 안내**: PyCharm Community도 무료이고 충분히 좋습니다. 이미 익숙하면 그대로 써도 됩니다. 본문은 VS Code 기준으로만 적습니다.

---

## 3.2 시스템 요구사항 (2026-04 기준)

| 항목 | 요구사항 |
|------|----------|
| Python | **3.13 이상** (3.12도 동작은 하지만 이 가이드는 3.13 기준) |
| OS | macOS 13 Ventura 이상 / 최신 Ubuntu 22.04, 24.04 LTS 권장 |
| 디스크 여유 공간 | 최소 **5GB** (Python + 가상환경 + 라이브러리들) |
| 메모리 | 4GB 이상 권장 (8GB 이상이면 쾌적) |
| 인터넷 연결 | 라이브러리 다운로드 시 필요 |

### 3.2.1 OS별 권장 경로 한눈에

- **macOS**: Homebrew → Python 3.13 → uv → VS Code 순서
- **Linux (Ubuntu/Debian)**: apt 또는 deadsnakes PPA → Python 3.13 → uv → VS Code 순서
- **Windows**: **가능하면 WSL2(Ubuntu)에서 위 Linux 절차를 따르는 것을 강력 권장.** 순수 Windows 직접 설치도 가능하지만 배포 환경이 거의 다 Linux이므로 처음부터 같은 환경에서 익히는 것이 편합니다.

> **WSL2(Windows Subsystem for Linux 2)란?** Windows 안에서 진짜 Linux(Ubuntu 등)를 거의 그대로 돌릴 수 있게 해 주는 마이크로소프트의 공식 기능입니다. Windows를 쓰면서도 Linux 명령어가 그대로 통하므로, 백엔드 학습에는 거의 항상 WSL2 쪽이 편합니다. 설치는 [공식 안내](https://learn.microsoft.com/ko-kr/windows/wsl/install)를 참고하세요. (PowerShell 관리자에서 `wsl --install` 한 줄로 보통 됩니다.)

---

## 3.3 macOS — Python 3.13 설치

### 3.3.1 단계 1 — Homebrew 확인 또는 설치

**Homebrew**는 macOS에서 명령어 한 줄로 외부 프로그램을 설치해 주는 패키지 매니저입니다. 우리는 Python을 깔 때 Homebrew를 사용합니다.

> **Homebrew란?** macOS·Linux용 패키지 매니저. `brew install <이름>` 한 줄로 외부 소프트웨어를 설치할 수 있게 해 줍니다. 이 가이드는 macOS 사용자에게 Homebrew를 전제로 합니다.

이미 깔려 있는지 먼저 확인합니다.

```bash
brew --version
```

`Homebrew 4.x.x` 또는 `Homebrew 5.x.x` 같은 출력이 나오면 다음 단계로. `command not found: brew`가 나오면 아래 한 줄로 설치합니다.

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

설치 후 Apple Silicon(M1/M2/M3 등) Mac에서는 PATH 설정을 한 번 해 줘야 `brew` 명령이 잡힙니다.

```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

> **PATH란?** 터미널이 명령을 받았을 때 "이 이름의 실행 파일을 어느 폴더에서 찾아야 하지?"를 정해주는 환경 변수입니다. PATH에 등록된 폴더 순서대로 뒤져서 찾습니다. PATH에 안 들어 있는 폴더의 명령어는 `command not found`가 됩니다.

> **`~/.zshrc`란?** macOS 기본 셸인 zsh이 시작될 때마다 자동으로 읽는 설정 파일입니다. 여기에 환경 변수, 별칭(alias) 등을 적어두면 셸을 새로 켤 때마다 적용됩니다. `~`는 홈 디렉터리(예: `/Users/yourname`)를 뜻합니다.

다시 확인해서 버전이 출력되면 OK.

```bash
brew --version
```

### 3.3.2 단계 2 — Python 3.13 설치

```bash
brew install python@3.13
```

설치가 끝나면 다음 명령으로 확인합니다.

```bash
python3.13 --version
```

다음과 같이 나오면 성공입니다(마이너 버전 숫자는 시점에 따라 다릅니다).

```
Python 3.13.x
```

### 3.3.3 단계 3 — `python` / `python3` / `python3.13` 정리

Python 입문자를 가장 자주 헷갈리게 하는 부분입니다. **macOS의 시스템에는 옛날 Python 3가 이미 깔려 있을 수 있고**, 우리가 새로 깐 3.13이 그 위에 별도로 추가된 상태가 됩니다.

확인해 보겠습니다.

```bash
which python3.13
# 예상: /opt/homebrew/bin/python3.13  (Apple Silicon)
# 또는: /usr/local/bin/python3.13     (Intel Mac)

which python3
# 위와 같을 수도, /usr/bin/python3 (시스템 기본)일 수도

which python
# command not found 가 가장 흔합니다
```

이 가이드의 약속은 다음과 같습니다.

- **`python3.13`** : 우리가 깐 새 인터프리터를 명확히 가리킬 때
- **`python3`** : 가상환경을 켠 뒤(=`.venv` 활성화 후)에는 그 안의 Python을 가리키는 별칭이 되므로 안전
- **`python`** : 가상환경 안에서만 가끔 통함. 시스템 전역에서는 보통 안 통함

**가상환경을 켠 상태에서는 `python`/`python3`/`python3.13`이 모두 같은 것을 가리킵니다.** 그래서 가상환경에 들어간 뒤에는 그냥 `python`만 써도 안전합니다. 가상환경 밖에서 명시적으로 3.13을 쓸 때는 `python3.13`을 쓰는 게 가장 명확합니다.

> **가상환경(virtual environment)이란?** 프로젝트마다 라이브러리를 격리해 두는 작은 "독립된 Python 공간"입니다. 시스템 Python을 더럽히지 않고 프로젝트별로 다른 라이브러리·버전을 쓸 수 있게 해 줍니다. 자세한 내용은 [용어 사전](glossary.md#가상환경-virtual-environment)에 있습니다.

### 3.3.4 (대안) pyenv로 여러 Python 버전을 갈아끼우고 싶다면

여러 프로젝트가 다른 Python 버전을 요구할 때 쓰는 도구가 **pyenv**입니다. Node.js의 nvm, Ruby의 rbenv와 비슷합니다. 본 가이드의 권장 경로는 아니지만 짧게 적어 둡니다.

```bash
brew install pyenv
pyenv install 3.13
pyenv global 3.13
```

`~/.zshrc`에 다음을 추가해야 셸이 pyenv의 Python을 우선 찾습니다.

```bash
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - zsh)"
```

> **참고**: 이 가이드는 Homebrew로 깐 Python 3.13 하나를 그대로 씁니다. pyenv는 "여러 버전을 자주 갈아끼울 일이 생기면 그때" 도입해도 늦지 않습니다.

---

## 3.4 Linux (Ubuntu/Debian) — Python 3.13 설치

Ubuntu·Debian 계열을 기준으로 설명합니다. 다른 배포판(Fedora·Arch 등)은 패키지 매니저 명령(`dnf`, `pacman`)만 다르고 흐름은 같습니다.

### 3.4.1 단계 1 — apt로 시도

먼저 OS의 기본 패키지 매니저인 `apt`로 3.13이 바로 깔리는지 시도합니다.

```bash
sudo apt update
sudo apt install -y python3.13 python3.13-venv
```

설치 후 확인:

```bash
python3.13 --version
```

`Python 3.13.x`가 나오면 3.6 절(uv 설치)로 넘어가도 됩니다. **`E: Unable to locate package python3.13`이 나오면** OS의 기본 저장소에 아직 3.13이 없다는 뜻입니다(특히 Ubuntu 22.04 LTS나 Debian 12에서 그럴 수 있습니다). 이때는 다음 단계로.

### 3.4.2 단계 2 — deadsnakes PPA 추가 (Ubuntu)

**deadsnakes**는 Ubuntu 사용자들이 가장 많이 쓰는 "최신 Python을 제공하는 비공식 저장소"입니다. 한 번 등록해 두면 `apt`로 새 Python 버전을 깔 수 있습니다.

> **PPA(Personal Package Archive)란?** Ubuntu에서 사용자·단체가 직접 만드는 작은 패키지 저장소입니다. 공식 저장소에는 없는 새 버전이나 도구를 PPA를 통해 추가로 받을 수 있습니다. deadsnakes는 그중에서 Python 전용으로 잘 관리되는 PPA입니다.

```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.13 python3.13-venv python3.13-dev
```

확인:

```bash
python3.13 --version
```

### 3.4.3 (대안) pyenv로 직접 컴파일

Debian이거나 어떤 사정으로 PPA를 못 쓰는 환경이라면 pyenv가 가장 확실합니다.

```bash
# 빌드에 필요한 시스템 의존성 (Ubuntu/Debian)
sudo apt install -y \
    build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev curl libncursesw5-dev \
    xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# pyenv 설치
curl https://pyenv.run | bash
```

`pyenv.run` 스크립트가 알려주는 대로 셸 설정 파일(`~/.bashrc` 또는 `~/.zshrc`)에 두세 줄을 추가하고 셸을 다시 켭니다. 그 다음:

```bash
pyenv install 3.13
pyenv global 3.13
python3.13 --version
```

> **빌드가 오래 걸려요**: pyenv는 Python을 소스에서 직접 컴파일하므로 5~15분 걸립니다. 한 번만 하면 됩니다.

---

## 3.5 Windows — WSL2 한 단락 안내

이 가이드는 macOS/Linux 전제이므로, Windows는 **WSL2(Ubuntu)**를 강하게 권장합니다.

1. **WSL2 설치** — 관리자 권한 PowerShell에서 한 줄.
   ```powershell
   wsl --install
   ```
   설치가 끝나면 재부팅 후 Ubuntu 셸이 한 번 자동으로 뜹니다. 사용자 이름·비밀번호를 만들면 준비 완료.

2. **그 다음**부터는 위 **3.4 Linux 절차**를 그대로 따라 하면 됩니다.

3. (선택) **VS Code의 "WSL" 확장**을 설치하면, Windows의 VS Code에서 WSL 안의 Linux 파일을 직접 열고 편집·디버깅할 수 있습니다. 거의 모든 Windows + Python 백엔드 개발자가 이렇게 씁니다.

> **순수 Windows에 직접 설치해도 되나요?** 됩니다. [python.org](https://www.python.org/downloads/windows/)에서 공식 인스톨러를 받아 설치하고, 설치 화면에서 **"Add python.exe to PATH"**를 반드시 체크하세요. uv도 Windows용 설치 명령이 있습니다(공식 문서 참고). 다만 이 가이드의 명령어 예시(`source .venv/bin/activate` 등)는 macOS/Linux 셸 기준이라 Windows PowerShell에서는 일부 명령이 다릅니다(예: `.venv\Scripts\activate`). 학습 단계에서 그런 차이까지 신경 쓰는 것은 부담스러우므로 WSL2를 권합니다.

---

## 3.6 uv 설치

이제 본격적으로 패키지 매니저 **uv**를 깝니다.

### 3.6.1 왜 uv인가 (다시 한 번)

`pip`도 충분히 잘 동작합니다. 하지만 백엔드 프로젝트가 커지면 다음과 같은 작업이 자주 일어납니다.

1. 가상환경 만들기 (`python -m venv .venv`)
2. 가상환경 켜기 (`source .venv/bin/activate`)
3. 라이브러리 설치 (`pip install fastapi`)
4. 설치된 라이브러리 목록 잠그기 (`pip freeze > requirements.txt`)
5. 다른 컴퓨터에서 똑같이 복원 (`pip install -r requirements.txt`)

`uv`는 이 다섯 단계를 **한 도구로 일관되게**, 그리고 **압도적으로 빠르게** 처리합니다. 명령 체계도 더 간결합니다(`uv add fastapi` 한 줄).

> **uv와 pip의 관계는?** 같은 일을 하는 두 도구입니다. uv는 안에서 pip이 하던 일을 직접 다시 짠 것에 가깝습니다. `uv pip install ...`처럼 pip의 명령을 그대로 흉내낼 수도 있고, `uv add ...`처럼 더 현대적인 명령도 제공합니다. 자세한 비교는 [용어 사전의 pip와 uv 표](glossary.md#pip-와-uv-의-관계)를 참고하세요.

### 3.6.2 설치 — macOS / Linux 공통

[공식 문서](https://docs.astral.sh/uv/getting-started/installation/)가 권장하는 한 줄 설치 명령입니다.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

설치 스크립트가 셸 설정 파일(`~/.zshenv`, `~/.bashrc` 등)에 PATH를 자동으로 추가해 주지만, **현재 켜져 있는 터미널에는 자동 적용되지 않습니다.** **터미널을 한 번 닫았다 다시 열거나** 다음 한 줄을 실행해 주세요.

```bash
# macOS (zsh): 보통 ~/.zshenv 에 추가됩니다
source ~/.zshenv

# 위가 안 되면 ~/.zshrc 도 시도해 봅니다
source ~/.zshrc

# Linux (bash): ~/.bashrc 에 추가됩니다
source ~/.bashrc
```

> **그래도 `uv: command not found`가 뜨면** 새 터미널을 여는 게 가장 확실합니다. uv의 기본 설치 경로는 `~/.local/bin/uv`이며, 3.11.4 절의 트러블슈팅을 참고하세요.

> **위 명령이 인터넷에서 스크립트를 받아 바로 실행하는 게 안전한가요?** 일반적으로 신뢰할 수 있는 도메인(`astral.sh`)의 공식 설치 방법입니다. 더 보수적인 환경(회사·학교 정책)에서는 [GitHub 릴리스](https://github.com/astral-sh/uv/releases)에서 바이너리를 직접 받아 PATH에 두는 방식, 또는 `pipx install uv`도 가능합니다.

### 3.6.3 설치 확인

```bash
uv --version
```

`uv 0.x.x` 같은 출력이 나오면 성공입니다.

```bash
uv python list
```

이 명령은 uv가 인식한 Python 인터프리터 목록을 보여줍니다. 우리가 위에서 깐 3.13이 보이면 환경이 깔끔하게 잡힌 겁니다.

---

## 3.7 uv로 처음 가상환경 만들고 FastAPI 설치하기

이번 절에서는 **테스트용 폴더**를 하나 만들고, uv로 가상환경 + 라이브러리 설치까지 진행합니다. 04장에서 본격적인 첫 프로젝트를 다시 만들 것이므로 여기서는 **환경이 잘 동작하는지 확인**하는 데 의의가 있습니다.

### 3.7.1 폴더 만들기

```bash
mkdir hello-fastapi
cd hello-fastapi
```

홈 디렉터리든 데스크톱이든 어디에 만들든 상관없습니다. 이 가이드에서는 보통 홈(`~`) 아래에 `projects/` 같은 작업 폴더를 두고 그 안에 둡니다.

### 3.7.2 uv 프로젝트 초기화

```bash
uv init
```

이 명령은 현재 폴더를 uv 프로젝트로 만듭니다. 실행 직후 폴더에 다음 파일들이 생깁니다.

- **`pyproject.toml`** — 프로젝트 메타데이터(이름·Python 버전·의존성 라이브러리 목록)를 적는 표준 파일.
- **`.python-version`** — 이 프로젝트가 쓸 Python 버전을 적어둔 작은 텍스트 파일.
- **`README.md`** — 빈 README. 지금은 신경 안 써도 됨.
- **`hello.py`** 또는 **`main.py`** (uv 버전에 따라 이름이 다를 수 있음) — 짧은 예시 스크립트.

> **`pyproject.toml`이란?** 현대 Python 프로젝트의 **표준 설정 파일**입니다. 옛날에는 `setup.py`, `requirements.txt`가 따로 했던 일을 한 파일로 모았습니다. 이름·버전·의존성·빌드 설정 등이 다 여기 들어갑니다. uv뿐 아니라 pip·poetry·ruff 등 거의 모든 현대 Python 도구가 이 파일을 읽습니다.

`pyproject.toml`을 한 번 열어 보면 대략 이렇게 생겼을 겁니다(uv 버전에 따라 약간 다를 수 있음).

```toml
[project]
name = "hello-fastapi"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.13"
dependencies = []
```

`requires-python = ">=3.13"` 줄이 보입니다. uv는 이 줄을 읽고 "이 프로젝트는 Python 3.13 이상이 필요하구나"를 압니다.

### 3.7.3 FastAPI와 Uvicorn 추가

이제 라이브러리를 추가합니다. `uv add` 명령은 **자동으로 가상환경을 만들고**(없으면) **거기에 라이브러리를 깔고** **잠금 파일을 만듭니다.** 한 번에 다 합니다.

```bash
uv add fastapi "uvicorn[standard]"
```

> **`uvicorn[standard]`의 대괄호는 뭔가요?** "추가 옵션 묶음"을 뜻하는 표기입니다. `uvicorn` 자체만 받으면 핵심 기능만 들어오고, `uvicorn[standard]`로 받으면 자주 쓰는 부가 라이브러리(예: 자동 리로드를 위한 `watchfiles`, 빠른 HTTP 파서 `httptools`, 더 빠른 이벤트 루프 `uvloop` 등)가 함께 깔립니다. 우리는 자동 리로드를 쓸 거라서 `[standard]`를 붙입니다. 따옴표는 일부 셸이 대괄호를 잘못 해석하지 않게 막아주는 안전장치입니다.

명령이 끝나면 폴더 구성은 다음처럼 확장됩니다.

```
hello-fastapi/
├── .venv/                ← 새로 생긴 "가상환경 폴더"
├── .python-version
├── pyproject.toml        ← dependencies 항목이 갱신됨
├── uv.lock               ← 새로 생긴 "잠금 파일"
├── README.md
└── hello.py (또는 main.py)
```

각 파일·폴더가 무엇을 의미하는지 정리합니다.

- **`.venv/`** — 이 프로젝트만의 격리된 Python 공간. 안에 Python 인터프리터의 복사본과 깔린 라이브러리들이 들어 있습니다. **이 폴더는 git에 올리지 않습니다.**(자동 생성되므로 다시 만들면 됨)
- **`uv.lock`** — 이번에 깔린 라이브러리들의 **정확한 버전과 해시값**을 기록한 잠금 파일. 다른 컴퓨터에서 `uv sync`를 돌리면 정확히 같은 버전들이 다시 깔립니다. 이 파일은 git에 올립니다.
- **`pyproject.toml`의 `dependencies`** — 위 명령으로 우리가 의도한 의존성 목록(`fastapi`, `uvicorn[standard]`)이 적힙니다. 사람이 읽고 편집하는 파일입니다.

> **잠금 파일(lock file)이란?** "이 프로젝트는 정확히 이 버전들로 동작한다"고 못 박아 두는 파일입니다. 협업 시 "내 컴퓨터에선 되는데"를 막아 줍니다. uv는 `uv.lock`, npm은 `package-lock.json`, Cargo는 `Cargo.lock` 등 비슷한 개념입니다.

### 3.7.4 가상환경 켜기 / 안 켜기

`uv add` 자체는 가상환경을 켤 필요가 없습니다. uv가 알아서 `.venv/`를 보고 거기에 깝니다. 하지만 **앞으로 `python` 명령을 직접 칠 일이 있다면 가상환경을 켜야** 그 안의 Python이 호출됩니다.

```bash
source .venv/bin/activate
```

켜지면 프롬프트 앞에 `(hello-fastapi)` 같은 표시가 붙습니다. 이 상태에서 `python --version`을 치면 프로젝트의 3.13이 나옵니다.

끄고 싶으면 그냥 `deactivate`.

> **uv를 쓰면 거의 가상환경을 직접 켤 일이 없습니다.** `uv run python ...`, `uv run uvicorn ...`, `uv add ...`처럼 **`uv run` 접두사**를 붙이면 uv가 알아서 가상환경 안에서 명령을 실행해 줍니다. 본 가이드의 표준 패턴은 `uv run`입니다.

### 3.7.5 깔린 것 확인

```bash
uv pip list
```

이 명령은 현재 가상환경에 깔린 라이브러리 목록을 보여줍니다. 다음 같은 출력이 나오면 성공입니다(버전 숫자는 시점에 따라 다름).

```
Package           Version
----------------- --------
annotated-types   0.7.0
anyio             4.x.x
fastapi           0.115.x
pydantic          2.x.x
pydantic_core     2.x.x
sniffio           1.3.x
starlette         0.x.x
typing_extensions 4.x.x
uvicorn           0.30.x
...
```

`fastapi`와 `uvicorn`이 보이면 환경 구축은 끝입니다.

---

## 3.8 (대체 절차) pip + venv로 똑같이 하기

회사·학교 PC 정책으로 외부 설치 스크립트를 못 돌리는 등 **uv를 쓸 수 없는 환경**을 위한 대체 절차입니다. 그 외의 경우라면 위의 uv 절차를 그대로 따르는 것을 권장합니다.

```bash
# 1) 폴더 만들기
mkdir hello-fastapi-pip
cd hello-fastapi-pip

# 2) 가상환경 만들기 (.venv 폴더가 생김)
python3.13 -m venv .venv

# 3) 가상환경 켜기
source .venv/bin/activate
# 켜진 뒤로는 python, pip이 모두 .venv 안의 것을 가리킵니다

# 4) FastAPI 설치
pip install --upgrade pip
pip install fastapi "uvicorn[standard]"

# 5) 깔린 라이브러리를 텍스트로 잠그기
pip freeze > requirements.txt
```

`requirements.txt`는 `uv.lock`보다 **간단하지만 정밀도가 떨어집니다**(예: 해시 검증이 없음). 작은 학습 프로젝트에선 충분합니다.

다른 사람이 같은 프로젝트를 받아서 환경을 복원할 때:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **언제 uv 대신 pip + venv를 써야 하나요?**
> - 회사·학교 보안 정책이 외부 설치 스크립트(curl | sh) 실행을 막을 때
> - 이미 운영 중인 프로젝트가 `requirements.txt`/`pip` 흐름으로 굳어져 있을 때
> - **그 외**: 거의 모든 새 프로젝트에서 uv를 권장.

---

## 3.9 VS Code 환경 세팅

### 3.9.1 VS Code 설치

[code.visualstudio.com](https://code.visualstudio.com/)에서 OS에 맞는 빌드를 받아 설치합니다.

- **macOS**: `.zip`을 받아 압축을 풀고 `Visual Studio Code.app`을 `/Applications`로 끌어다 둡니다. (또는 `brew install --cask visual-studio-code`)
- **Linux (Ubuntu/Debian)**: `.deb` 파일을 받아 `sudo apt install ./code_*.deb`로 설치하거나, `snap install code --classic`.
- **WSL2**: Windows에서 VS Code를 설치하면 WSL 확장을 통해 Linux 파일에 그대로 접근할 수 있습니다.

설치 후 터미널에서 `code` 명령이 통하는지 확인해 둡니다(없으면 VS Code의 명령 팔레트에서 "Shell Command: Install 'code' command in PATH"를 한 번 실행).

```bash
code --version
```

### 3.9.2 추천 확장 (Extensions)

VS Code의 좌측 막대에서 사각형 4개 모양의 **Extensions** 아이콘을 누르고, 다음 세 개를 검색해 설치합니다. **확장 이름과 발행자(Publisher)를 정확히** 맞춰 설치하세요(비슷한 이름의 다른 확장이 많습니다).

| 확장 이름 | 발행자 (Publisher) | 역할 |
|-----------|--------------------|------|
| **Python** | **Microsoft** | 파이썬 언어의 핵심 지원(인터프리터 선택, 디버깅, 실행) |
| **Pylance** | **Microsoft** | 빠른 자동 완성·타입 분석 (Python 확장과 함께 동작) |
| **Ruff** | **Astral Software** | 매우 빠른 린터·포매터(코드 스타일 자동 정리) |

> **린터(linter)란?** 코드의 잠재적 문제(쓰지 않는 변수, 잘못된 들여쓰기, 위험한 패턴 등)를 자동으로 잡아주는 도구입니다.
>
> **포매터(formatter)란?** 코드의 스타일(들여쓰기·줄바꿈 위치·따옴표 종류 등)을 약속한 규칙대로 자동 정렬해 주는 도구입니다. ruff는 두 역할을 한 번에 합니다.

추가로 **선택적**으로 다음도 자주 깝니다.

- **GitLens** (eamodio) — git 히스토리를 코드 옆에 보여줌
- **Docker** (Microsoft) — 09장 배포에서 유용
- **Even Better TOML** (tamasfe) — `pyproject.toml` 편집 시 자동 완성

### 3.9.3 가상환경 인터프리터 선택

위에서 만든 `hello-fastapi/` 폴더를 VS Code로 엽니다.

```bash
cd hello-fastapi
code .
```

**중요한 한 단계**: VS Code 우측 하단(또는 명령 팔레트 `Cmd+Shift+P` / `Ctrl+Shift+P` → `Python: Select Interpreter`)에서 **인터프리터를 `.venv`로 지정**해 줍니다. 보통 자동으로 `.venv` 안의 Python이 후보로 뜹니다. 거기를 골라 주면 VS Code가 다음을 그 가상환경 기준으로 동작시킵니다.

- 자동 완성·타입 검사(Pylance)
- 통합 터미널을 열 때 자동으로 가상환경 활성화
- "Run Python File" 시 그 인터프리터로 실행

> **이 단계를 빠뜨리면** Pylance가 `import fastapi`를 빨간 줄로 표시할 수 있습니다. "라이브러리는 깔렸는데 VS Code가 다른 Python을 보고 있는" 상태입니다.

### 3.9.4 권장 settings.json

프로젝트 루트에 `.vscode/settings.json`을 두면 그 프로젝트에만 적용되는 VS Code 설정을 만들 수 있습니다. 다음 정도면 충분합니다.

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    }
  },
  "ruff.fixAll": true
}
```

이 설정은 다음을 의미합니다.

- 이 프로젝트에서는 `.venv` 안의 Python을 인터프리터로 쓴다.
- 새 터미널을 열 때 가상환경을 자동 활성화한다.
- `.py` 파일을 저장할 때 ruff로 자동 포매팅 + import 정리 + 자동 수정 가능한 린트 오류 정리.

> **WSL2 사용자**: `python.defaultInterpreterPath`의 경로 구분자는 그대로 `/`를 씁니다(WSL 안은 Linux이므로). Windows 경로 표기(`\`)를 쓰지 마세요.

### 3.9.5 PyCharm Community도 무난

VS Code가 부담스럽다면 [PyCharm Community](https://www.jetbrains.com/pycharm/download/)도 무료이고, Python 프로젝트 인식이 자동입니다. 가상환경도 대체로 알아서 잡아 줍니다. 이 가이드의 본문 캡처와 단축키는 VS Code 기준으로만 적습니다.

---

## 3.10 새너티 체크 — 한 줄 FastAPI 앱 띄워보기

이제 환경이 정말 잘 깔렸는지 **가장 짧은 FastAPI 앱**으로 검증합니다. 04장에서 본격적으로 같은 작업을 다시 하므로 여기서는 가볍게.

> **새너티 체크(sanity check)란?** 본격적인 작업 전에 "기본적인 것이 제대로 돌아가는가?"를 빠르게 확인하는 절차입니다. 의학·공학에서 두루 쓰는 표현이며, 우리는 "환경이 깨지지 않았는지"를 1분 안에 확인하려는 것입니다.

### 3.10.1 `app.py` 작성

`hello-fastapi/` 폴더 안에 `app.py` 파일을 **새로** 만들어 다음 내용을 넣습니다. (uv가 자동으로 만들어 둔 `hello.py` / `main.py`는 그대로 두어도 됩니다 — 우리는 새로 만든 `app.py`만 사용합니다.)

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def hello():
    return {"message": "Hello, FastAPI!"}
```

겨우 다섯 줄입니다. 이 코드는 다음을 합니다.

1. `FastAPI` 클래스를 가져온다.
2. `app`이라는 이름으로 FastAPI 앱을 하나 만든다.
3. **`/` 경로로 GET 요청이 들어오면** `hello()` 함수가 처리하도록 등록한다.
4. 응답으로 `{"message": "Hello, FastAPI!"}` 라는 JSON을 돌려준다.

> **`@app.get("/")` 이 줄은 뭔가요?** **데코레이터**라고 부르는 표기로, "이 바로 아래의 함수를 GET / 요청 처리기로 등록해라"는 명령입니다. FastAPI 라우팅의 기본 단위입니다. [용어 사전 — 데코레이터](glossary.md#데코레이터-decorator)도 참고.

### 3.10.2 서버 띄우기

다음 명령으로 띄웁니다(uv 권장 경로 / pip 경로 둘 다 적습니다).

**uv 경로 (권장):**

```bash
uv run uvicorn app:app --reload
```

**pip + venv 경로:**

```bash
# 가상환경이 켜져 있어야 함
source .venv/bin/activate
uvicorn app:app --reload
```

`uvicorn app:app` 부분은 "**`app.py` 파일 안의 `app` 객체**를 띄우라"는 뜻입니다. 콜론 앞이 파일명, 뒤가 변수명입니다. `--reload`는 코드를 수정하면 서버가 자동으로 재시작되게 해 주는 개발용 옵션입니다.

성공하면 다음 비슷한 로그가 출력됩니다.

```
INFO:     Will watch for changes in these directories: ['/Users/.../hello-fastapi']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...] using WatchFiles
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3.10.3 브라우저에서 확인

다음 두 주소를 열어 봅니다.

1. http://127.0.0.1:8000/ — `{"message":"Hello, FastAPI!"}` JSON이 보입니다.
2. http://127.0.0.1:8000/docs — **자동 생성된 Swagger UI**가 보입니다. `GET /` 엔드포인트가 등록돼 있고, 펼치면 "Try it out" 버튼으로 직접 호출도 됩니다.

또는 다른 터미널에서 `curl`로 확인해도 좋습니다.

```bash
curl http://127.0.0.1:8000/
# 응답: {"message":"Hello, FastAPI!"}
```

확인이 끝나면 첫 터미널에서 `Ctrl+C`로 서버를 종료합니다. 테스트 폴더는 04장에서 다시 만들 거라 지워도 되고, 그대로 둬도 됩니다.

```bash
# 만약 지우고 싶으면
cd ..
rm -rf hello-fastapi
```

> **04장 예고**: 다음 챕터에서 같은 흐름을 처음부터 다시 만들면서 이번엔 라우트를 더 추가하고, 폴더 구조를 잡고, 자동 문서를 자세히 살펴봅니다.

---

## 3.11 OS·환경별 자주 발생하는 문제와 해결

### 3.11.1 macOS — `command not found: brew`

Homebrew가 설치되지 않았거나, 설치는 됐는데 PATH가 안 잡힌 상태입니다.

- 설치 자체가 안 된 경우: 3.3.1의 설치 한 줄을 다시.
- 설치는 됐는데 PATH가 안 잡힌 경우(Apple Silicon Mac에서 흔함):
  ```bash
  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
  source ~/.zshrc
  ```

### 3.11.2 macOS / Linux — `command not found: python3.13`

Python 3.13이 깔리지 않았거나, 깔린 곳이 PATH에 없는 상태입니다.

```bash
# 어디 있는지 직접 찾아보기
ls /opt/homebrew/bin/python3.13   # macOS Apple Silicon
ls /usr/local/bin/python3.13      # macOS Intel
ls /usr/bin/python3.13            # 일부 Linux
which python3                     # 다른 버전이라도 잡히는지
```

대부분은 위 3.3 / 3.4 절을 다시 따라 하면 해결됩니다. 시스템에 옛날 Python(예: 3.10)만 있고 3.13이 정말 없을 수도 있으니 버전 확인을 명확히 합니다.

### 3.11.3 Linux — `python3.13: not found` (Ubuntu LTS의 기본 Python 버전)

Ubuntu 22.04 LTS의 기본 저장소에는 보통 Python 3.10이, 24.04 LTS에는 보통 3.12가 들어 있습니다. 그래서 `apt install python3.13`이 곧장 안 통할 때가 있습니다. 해결책은 두 가지.

1. **deadsnakes PPA 추가** (3.4.2 절차)
2. **pyenv 사용** (3.4.3 절차)

> **시스템 Python을 함부로 바꾸지 마세요**: Ubuntu 시스템 자체가 기본 Python 3.x에 의존하는 부분이 있어서, 시스템 Python 자체를 갈아끼우면 OS가 망가질 수 있습니다. 우리는 항상 **시스템 Python과 별개로 새 Python을 추가**해 쓰는 방식을 씁니다. (위 두 방법 모두 그렇게 동작합니다.)

### 3.11.4 `uv: command not found` (uv 설치 후에)

설치 스크립트는 PATH 라인을 셸 설정 파일에 추가하지만, **현재 켜진 셸에는 자동 적용되지 않습니다.** 새 터미널을 열거나, 다음 한 줄을 시도합니다.

```bash
source ~/.zshenv     # macOS (zsh): uv 설치 스크립트가 보통 이 파일을 갱신
source ~/.zshrc      # macOS 보조
source ~/.bashrc     # 대부분의 Linux
```

여전히 안 통하면 직접 PATH를 확인합니다(uv의 기본 설치 경로는 `~/.local/bin/uv`).

```bash
ls ~/.local/bin/uv
echo $PATH | tr ':' '\n' | grep local
```

### 3.11.5 가상환경에서 `pip install`이 시스템에 깔리는 것 같음

가상환경을 켜는 걸 깜빡한 경우가 압도적으로 많습니다. 프롬프트 앞에 `(hello-fastapi)` 같은 표시가 있는지 다시 확인하세요. uv 사용자라면 그냥 `uv add ...`나 `uv run ...`을 쓰면 이 문제가 안 생깁니다.

### 3.11.6 8000번 포트가 이미 사용 중

```
ERROR: [Errno 48] Address already in use
```

다른 프로세스(또는 이전에 띄워두고 안 끈 uvicorn)가 8000을 잡고 있는 경우입니다.

```bash
# 8000 사용 중인 프로세스 찾기 (macOS / Linux)
lsof -i :8000
# 또는
sudo lsof -i :8000
```

원인 프로세스를 찾아 종료하거나, 다른 포트로 띄웁니다.

```bash
uv run uvicorn app:app --reload --port 8001
```

### 3.11.7 VS Code가 `import fastapi`를 빨간 줄로 표시함

라이브러리는 깔렸는데 VS Code가 다른 인터프리터(예: 시스템 Python)를 보고 있는 상태입니다. **`Cmd/Ctrl+Shift+P → Python: Select Interpreter`**에서 `.venv` 안의 Python을 골라 주면 해결됩니다. 그래도 안 되면 VS Code 창을 한 번 닫았다가 다시 열어 보세요.

### 3.11.8 Windows에서 `source .venv/bin/activate`가 안 통함

WSL2를 쓰지 않고 PowerShell·CMD에서 직접 작업 중이라면 활성화 명령이 다릅니다.

```powershell
.venv\Scripts\Activate.ps1   # PowerShell
.venv\Scripts\activate.bat   # CMD
```

이 가이드의 명령 표기는 macOS/Linux 기준이므로, Windows는 가능하면 **WSL2(Ubuntu)**에서 작업하길 다시 한 번 권장합니다.

---

## 3.12 설치 완료 체크리스트

다음이 모두 성공하면 다음 챕터로 넘어갈 준비가 끝난 것입니다.

- [ ] `python3.13 --version` → `Python 3.13.x` 출력
- [ ] `uv --version` → 버전 출력 (uv를 못 쓰는 환경이면 `pip --version` 출력으로 대체)
- [ ] `code --version` → VS Code 설치 확인
- [ ] VS Code에 **Python**, **Pylance**, **Ruff** 확장이 깔려 있다
- [ ] `mkdir hello-fastapi && cd hello-fastapi && uv init && uv add fastapi "uvicorn[standard]"` 가 에러 없이 끝남
- [ ] `app.py`에 5줄짜리 FastAPI 앱을 작성하고 `uv run uvicorn app:app --reload`로 띄움
- [ ] 브라우저에서 `http://127.0.0.1:8000/`이 JSON을 돌려줌
- [ ] 브라우저에서 `http://127.0.0.1:8000/docs`가 Swagger UI를 보여줌

위가 다 통과하면 환경 구축은 완료입니다. **다음 챕터에서 같은 흐름을 더 단단하게 다시 만들면서 라우트와 폴더 구조까지 정리합니다.**

---

## 3.13 이 챕터 요약

- Python 3.13 + uv + VS Code, 이 세 가지가 이 가이드의 표준 스택이다.
- macOS는 Homebrew로(`brew install python@3.13`), Ubuntu는 `apt`나 deadsnakes PPA로 Python 3.13을 깐다. Windows는 WSL2(Ubuntu)에서 위 Linux 절차를 따른다.
- uv는 한 줄(`curl -LsSf https://astral.sh/uv/install.sh | sh`)로 설치하고, 가상환경·라이브러리·잠금 파일을 한 도구로 관리한다.
- 권장 흐름은 `uv init` → `uv add fastapi "uvicorn[standard]"` → `uv run uvicorn app:app --reload`. 회사·학교 정책 등으로 uv를 못 쓰면 `python3.13 -m venv .venv` + `pip install`이 대체 절차다.
- VS Code에 **Python(Microsoft)**, **Pylance(Microsoft)**, **Ruff(Astral Software)** 확장을 깔고, `Python: Select Interpreter`로 `.venv`를 가리키게 한다.
- `app.py`에 다섯 줄짜리 FastAPI 앱을 만들고 `/`와 `/docs`가 모두 응답하면, 환경 구축은 끝난 것이다.

---

← [02. 백엔드 기본 용어 정리](02-backend-basics.md) | 다음 문서로 이동: **[04. 첫 프로젝트 →](04-first-project.md)**
