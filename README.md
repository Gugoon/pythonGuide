# FastAPI 백엔드 가이드

**Python 입문자를 위한 비동기 웹 프레임워크 FastAPI 완벽 가이드**

---

## 이 가이드에 대하여

이 문서는 **Python 문법은 어느 정도 익혔지만 백엔드 개발은 처음**인 독자를 대상으로, Python의 비동기 웹 프레임워크인 **FastAPI**로 실전 REST API 백엔드를 구축하는 방법을 처음부터 끝까지 안내합니다.

> "백엔드"란 사용자에게 직접 보이지 않는, 서버에서 동작하는 프로그램을 말합니다. 모바일 앱이나 웹 페이지(=프론트엔드)가 데이터를 요청하면, 서버에 있는 백엔드 프로그램이 데이터베이스에서 자료를 꺼내 다시 돌려주는 역할을 합니다.

- **대상 독자**: Python 기본 문법(함수·클래스·타입 힌트)에 익숙하고, 이제 본격적으로 서버를 만들어보고 싶은 분
- **선수 지식**: Python 3 기초, 터미널(명령 프롬프트)에서 명령어 실행 경험. HTML/HTTP는 몰라도 됩니다 — 02장에서 처음부터 설명합니다.
- **학습 방식**: 이론 → 개별 요소 실습 → 종합 프로젝트 2개
- **집필 기준**: 2026년 4월 시점의 최신 공식 문서 (Python 3.13, FastAPI 0.115.x 이상)

이 가이드는 **선택지로 독자를 괴롭히지 않습니다.** 백엔드 입문자에게 도움이 될 도구·라이브러리를 한 가지로 못 박고, 그 이유를 풀어 설명한 뒤 그것 하나로 끝까지 진행합니다. 다른 도구가 궁금하다면 12장 레퍼런스에 짧게 정리해 두었습니다.

## 사용 기술 스택 (2026-04 기준)

이 가이드에서 사용하는 도구의 전체 목록입니다. 지금은 이름만 훑어보고 넘어가도 좋습니다 — 각 항목은 해당 챕터에서 처음부터 다시 설명합니다.

| 구성요소 | 사용 버전 / 도구 | 한 줄 설명 |
|----------|----------|------------|
| Python | 3.13 이상 | 우리가 쓰는 프로그래밍 언어 |
| FastAPI | 0.115.x 이상 | 웹 서버를 만드는 핵심 프레임워크 |
| Pydantic | 2.x | 요청·응답 데이터의 타입을 자동으로 검증해 주는 도구 |
| SQLAlchemy | 2.0.x (async) | 파이썬 코드로 데이터베이스를 다루는 ORM |
| Alembic | 1.13.x 이상 | 데이터베이스 표(테이블) 구조 변경 이력을 관리하는 도구 |
| DB 드라이버 | `aiosqlite` / `asyncmy` / `asyncpg` | 각각 SQLite, MySQL, PostgreSQL과 통신하는 라이브러리 |
| PyJWT | 2.8.x 이상 | 로그인 인증에 쓰이는 JWT 토큰을 만들고 검증하는 라이브러리 |
| bcrypt | 4.x | 비밀번호를 안전하게 한 방향 암호화(해싱)하는 라이브러리 |
| Uvicorn | 0.30.x 이상 | 우리가 만든 FastAPI 앱을 실제로 실행해 주는 서버 |
| Gunicorn | 23.x | 운영 환경에서 Uvicorn을 여러 개 띄워 부하를 분산하는 도구 |
| uv | 0.4.x 이상 | 파이썬 패키지를 설치·관리하는 차세대 도구 (옛날의 `pip`을 빠르게 대체) |

> **왜 `pip` 대신 `uv`인가?** `uv`는 같은 일을 10~100배 빠르게 하면서도, 가상 환경 만들기·라이브러리 설치·잠금 파일 관리까지 한 명령으로 처리합니다. 03장에서 설치 방법을 안내합니다. 만약 회사·학교 PC 정책으로 `uv`를 쓸 수 없다면 `pip`/`venv`로도 따라할 수 있도록 03장에 대체 명령을 함께 적어둡니다.

> **왜 비밀번호 해싱은 `bcrypt`만 쓰는가?** 파이썬 생태계에는 비밀번호 해싱 라이브러리가 여러 개 있지만(`passlib`, `argon2-cffi` 등), 입문자에게는 API가 가장 단순한 `bcrypt`를 직접 쓰는 쪽이 가장 이해하기 쉽고 오류도 적습니다. 다른 옵션은 12장에서 짧게 다룹니다.

## 학습 목표

이 가이드를 완주하면 다음을 할 수 있습니다.

1. 백엔드 개발의 핵심 개념(HTTP, REST, DB, 인증, 배포)을 이해하고 자기 말로 설명할 수 있다.
2. FastAPI 프로젝트를 처음부터 생성하고 라우팅·의존성 주입을 구성할 수 있다.
3. SQLAlchemy 2.0으로 SQLite, MySQL, PostgreSQL 중 어떤 DB와도 연결해 데이터를 읽고 쓸 수 있다.
4. JWT 기반의 회원가입·로그인·인증 흐름을 처음부터 끝까지 직접 구현할 수 있다.
5. Docker로 앱을 컨테이너화하고 Render·Fly.io·AWS·Ubuntu 서버 어디든 배포할 수 있다.
6. 실전 규모의 Note API, Blog API를 백지 상태에서 완성할 수 있다.

## 전체 목차

### 1부: 개념 이해

- [01. FastAPI 소개 — Python 개발자를 위한 안내](docs/01-introduction.md)
- [02. 백엔드 기본 용어 정리](docs/02-backend-basics.md)

### 2부: 환경 구축과 기초

- [03. 설치 가이드 (macOS / Linux)](docs/03-installation.md)
- [04. 첫 프로젝트 — Hello FastAPI](docs/04-first-project.md)

### 3부: FastAPI 핵심 기능

- [05. 라우팅과 Pydantic (JSON 요청/응답)](docs/05-routing-content.md)
- [06. SQLAlchemy 2.0과 데이터베이스 연동 (SQLite / MySQL / PostgreSQL)](docs/06-sqlalchemy-database.md)
- [07. CRUD 예제 — Todo API](docs/07-crud-example.md)
- [08. 사용자 인증 — JWT와 Bcrypt](docs/08-authentication.md)

### 4부: 운영

- [09. 배포 가이드 — Docker, Render/Fly.io, AWS, Ubuntu](docs/09-deployment.md)

### 5부: 종합 예제 (처음부터 따라하기)

- [10. 종합 예제 1 — Note API](docs/10-project-note-api.md)
- [11. 종합 예제 2 — Blog API](docs/11-project-blog-api.md)

### 6부: 레퍼런스

- [12. 유틸리티 및 라이브러리 — 최신 버전과 사용 예제](docs/12-utilities.md)
- [용어 사전 (Glossary) — 모르는 단어가 나올 때 펼쳐 보세요](docs/glossary.md)

## 권장 학습 순서

### 순차 학습 (처음 배우는 경우 — **이 길을 추천합니다**)

01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 순서로 차근차근 진행합니다. 12장은 필요할 때 꺼내보는 사전, 용어 사전(glossary)은 모르는 단어가 나올 때 펼쳐 보세요.

각 챕터의 권장 소요 시간은 챕터마다 본문 상단에 표시되어 있고, 분량 차이가 큽니다. 대략적인 예상은 다음과 같습니다.

| 챕터 | 본문 상단의 권장 소요 시간 |
|------|------|
| 01. FastAPI 소개 | 약 30분 (개념 읽기) |
| 02. 백엔드 기본 용어 | 1~2시간 |
| 03. 설치 가이드 | 30분 ~ 1시간 |
| 04. 첫 프로젝트 | 1~2시간 |
| 05. 라우팅과 Pydantic | 3~4시간 |
| 06. SQLAlchemy + DB | 4~6시간 |
| 07. CRUD 예제 | 3~5시간 |
| 08. 인증 (JWT + Bcrypt) | 4~6시간 |
| 09. 배포 가이드 | 4~8시간 (선택 경로에 따라 다름) |
| 10. 종합 예제 — Note API | 6~10시간 (하루~이틀) |
| 11. 종합 예제 — Blog API | 8~12시간 (이틀) |

전체를 처음부터 차근차근 따라가면 **하루 2~3시간 기준 약 4~5주**가 현실적인 페이스입니다(01장 자주 묻는 질문에서 같은 안내). 이미 백엔드 경험이 있다면 더 빠릅니다.

### 빠른 실습 (개념은 아는 경우)

03 → 04 → (선택적으로 05·07 훑기) → 10 (Note API) 순서로 곧장 만들어보고, 막히는 부분이 생기면 해당 챕터를 펼쳐 확인합니다. 10장은 회원가입·인증·CRUD까지 자체 안내가 들어 있어 한 챕터만 따라도 동작하는 결과물이 남습니다.

### 레퍼런스 사용 (특정 주제만)

목차에서 필요한 챕터로 바로 이동합니다. 각 챕터는 가능한 자기완결적으로 작성되어 있습니다. 특히 10, 11장 종합 예제는 설치부터 배포까지 다시 처음부터 안내하므로, 한 챕터만 봐도 실행 가능한 프로젝트가 완성됩니다(다만 Bcrypt·JWT의 *왜*에 대한 풀이는 08장에 더 깊게 적혀 있어, 10·11장에서 8장 절(8.3.4, 8.4.5, 8.7 등)로 가끔 링크가 걸려 있습니다).

### 챕터 사이의 연결 (이 가이드의 약속)

각 챕터의 코드는 다음 챕터에서 그대로 자라납니다.

- **04 → 05**: `app/main.py`에 라우트가 늘다가 `app/routers/`로 분리.
- **05 → 06**: 메모리 dict 저장소가 SQLAlchemy + SQLite로 교체. 라우트와 Pydantic 모델은 거의 그대로.
- **06 → 07**: 한 파일 안의 라우트가 `app/routers/`·`app/crud.py`로 분리되고 통합 테스트(`pytest` + `httpx.AsyncClient`)가 붙음.
- **07 → 08**: 같은 구조에 `app/security.py`(bcrypt + PyJWT)와 `app/deps.py`(`get_current_user`)가 추가.
- **08 → 09**: 개발용 `uvicorn --reload`에서 운영용 **Uvicorn 멀티워커**(`uvicorn ... --workers N --proxy-headers`)로.
- **09 → 10**: 이전 챕터들의 부품(SQLAlchemy 비동기 + bcrypt + JWT + Docker)을 한 프로젝트(Note API, PostgreSQL)로 통합.
- **10 → 11**: 단일 모델(Note)에서 다중 모델(User · Post · Comment · Tag) + N:M 관계로, PostgreSQL에서 MySQL로.

## 종합 예제 개요

### 프로젝트 1 — Note API (`docs/10-project-note-api.md`)

- 개인 메모 서비스 REST API
- 회원가입 / 로그인 / JWT 발급
- 로그인한 사용자의 메모 CRUD(생성·조회·수정·삭제)
- PostgreSQL 데이터베이스 + Docker Compose로 개발
- Docker 이미지 빌드 후 배포

### 프로젝트 2 — Blog API (`docs/11-project-blog-api.md`)

- 다중 사용자 블로그 REST API
- User / Post / Comment / Tag 모델과 관계 매핑(1:N, N:M 등 표 사이의 연결)
- 페이지네이션(긴 목록을 페이지로 나눠 보여주기), 검색, 정렬
- MySQL 데이터베이스 연동
- Render·Fly.io 또는 Ubuntu 서버에 직접 배포

두 프로젝트는 **완전히 독립적**입니다. 앞 챕터를 읽지 않아도 각 종합 예제 문서만 따라하면 프로젝트 하나가 완성되도록 작성되어 있습니다. 중복되는 설명은 반복 학습을 위해 의도적으로 포함했습니다.

## 이 가이드에서 다루지 않는 것

처음 백엔드를 배우는 사람의 시야를 좁혀 끝까지 완주하도록 돕기 위해, 아래 주제는 의도적으로 제외했습니다.

- **HTML 페이지 렌더링** (Jinja2 같은 템플릿 엔진) — 이 가이드는 데이터(JSON)만 주고받는 REST API에 집중합니다. 화면은 별도의 모바일 앱이나 React/Vue 같은 프론트엔드가 그린다고 가정합니다.
- **실시간 통신**(WebSocket의 깊은 활용) — 01장에서 개념만 언급합니다.
- **GraphQL** — REST와는 다른 또 하나의 API 스타일입니다. 이 가이드의 범위 밖입니다.
- **Kubernetes** — 한 단계 더 큰 운영 도구입니다. 이 가이드는 Docker로 한 대 서버에 띄우는 단계까지 다룹니다.
- **외부 OAuth 로그인 연동**(구글·깃허브 로그인 등) — 직접 만든 회원가입/로그인(JWT)에 집중합니다.
- **Django, Flask와의 심층 비교** — 01장에서 위치만 간단히 짚습니다.

## 참고 공식 자료

- [FastAPI 공식 문서 (한국어 일부 지원)](https://fastapi.tiangolo.com/)
- [FastAPI GitHub](https://github.com/fastapi/fastapi)
- [Pydantic 공식 문서](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 공식 문서](https://docs.sqlalchemy.org/en/20/)
- [Python 공식 사이트](https://www.python.org/)
- [uv 공식 문서](https://docs.astral.sh/uv/)

## 문서 형식에 대하여

- 모든 문서는 GitHub Flavored Markdown으로 작성되었습니다.
- 코드 블록은 언어 지정이 되어 있어 신택스 하이라이팅이 적용됩니다.
- 패키지 마이너 버전(예: `pyjwt 2.x`, `ruff 0.x`, `mypy 1.x`)은 작성 시점 스냅샷이며, `uv add` 는 항상 lock 파일·`>=` 제약을 만족하는 최신 호환 버전을 받습니다.

### 단일 PDF 변환

```bash
# 1) 단일 통합 파일을 그대로 변환 (npm: md-to-pdf)
npx md-to-pdf fastapi-guide-complete.md

# 2) docs/ 분할본을 합쳐서 (pandoc, 한글 폰트 필수)
pandoc README.md docs/*.md -o fastapi-guide.pdf \
  --toc --toc-depth=3 --pdf-engine=xelatex \
  -V mainfont="Noto Sans CJK KR" \
  -V monofont="D2Coding" \
  -V geometry:margin=1in
```

> **한글 폰트 지정이 없으면 PDF 에서 한글이 깨집니다.** macOS 기본 폰트는 `AppleSDGothicNeo`, Linux/Windows 는 `Noto Sans CJK KR` 등 시스템에 설치된 한글 폰트로 바꿔 사용하세요. `xelatex` 또는 `lualatex` 엔진이 필요합니다(`brew install --cask mactex-no-gui` / `apt install texlive-xetex`).

---

다음 문서로 이동: **[01. FastAPI 소개 →](docs/01-introduction.md)**
