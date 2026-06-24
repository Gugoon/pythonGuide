# 14. 파일 업로드 — UploadFile

> **이 챕터의 목표**
> - 클라이언트가 보낸 파일을 FastAPI 가 어떻게 받는지, `UploadFile` 과 `bytes` 의 차이를 분명히 안다.
> - `File()` / `Form()` 로 파일과 일반 폼 필드를 함께 받는 멀티파트 요청을 다룬다.
> - 업로드를 **검증**한다 — 확장자·콘텐츠 타입·크기 상한. 실패하면 400 / 413 으로 일관되게 거절한다.
> - 클라이언트가 보낸 파일명을 절대 믿지 않고, **무작위 파일명**으로 안전하게 저장해 경로 traversal 을 막는다.
> - 저장된 파일을 `FileResponse` 로 다시 내려준다.
> - 메모리에 통째로 올리기 vs 디스크에 스트리밍하기의 트레이드오프를 손에 익힌다.
> - `pytest` + `httpx.AsyncClient` 로 업로드/다운로드를 16개 케이스로 검증한다.

> **소요 시간**: 2~3시간

> **전제**: 05장에서 `UploadFile` 을 잠깐 봤다. FastAPI 한 줄 라우트, Pydantic, `Depends` 의존성 주입, `pytest` + `httpx.AsyncClient` 통합 테스트(07장)에 한 번씩 손을 대 봤다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오시면 됩니다.

---

## 14.1 파일 업로드는 왜 "조금 다른가"

지금까지 우리가 받은 요청 본문은 모두 **JSON** 이었다. `{"title": "..."}` 같은 텍스트다. 그런데 파일은 다르다.

- 이미지·PDF·동영상은 **바이너리**다. JSON 안에 그대로 넣을 수 없다.
- 한 번에 수십 MB ~ 수백 MB 가 될 수 있다. 텍스트 본문처럼 가볍지 않다.
- 보통 "파일 + 설명 텍스트" 를 **함께** 보낸다(예: 프로필 사진 + 닉네임).

그래서 브라우저·HTTP 는 파일 전송에 `multipart/form-data` 라는 별도 형식을 쓴다. JSON(`application/json`) 이 아니다.

> **`multipart/form-data` 가 뭔가요?** 하나의 요청 본문을 여러 "파트(part)" 로 나눠 담는 인코딩이다. 각 파트는 자기만의 헤더(파일명, 콘텐츠 타입)를 가진다. HTML `<form enctype="multipart/form-data">` 가 파일을 올릴 때 쓰는 바로 그 형식이다. 텍스트 필드와 파일을 한 본문에 섞어 보낼 수 있다.

이번 장은 "할 일 API" 같은 CRUD 가 아니라, **파일 한 건을 받아 검증하고, 안전하게 저장하고, 다시 내려주는** 작은 서비스를 만든다.

### 14.1.1 무엇을 만들 것인가

엔드포인트 표:

| 메서드 | 경로 | 설명 | 성공 상태 |
|--------|------|------|-----------|
| `POST` | `/files` | 단일 파일 업로드(검증 → 저장 → 메타 반환) | 201 Created |
| `POST` | `/files/batch` | 다중 파일 업로드(+ 선택 폼 필드) | 201 Created |
| `GET` | `/files/{file_id}` | 파일 다운로드 | 200 OK |
| `GET` | `/health` | 헬스 체크 | 200 OK |

검증 실패의 응답 약속:

- 허용 안 된 확장자·콘텐츠 타입, 빈 파일 → **400 Bad Request**
- 크기 상한 초과 → **413 Request Entity Too Large**(= Payload Too Large)
- 없는 파일 다운로드 → **404 Not Found**

이 챕터에서 새로 익힐 것은 다음 다섯 가지다.

1. **`UploadFile`** 로 파일을 받고, `File()` / `Form()` 로 멀티파트 필드를 선언한다.
2. **검증** — 확장자(화이트리스트), 콘텐츠 타입, 크기 상한을 코드로 강제한다.
3. **안전한 저장** — 파일명을 무작위로 새로 만들어 경로 traversal 을 차단한다.
4. **`FileResponse`** 로 저장된 파일을 원본 파일명으로 내려준다.
5. **메모리 vs 디스크** 트레이드오프 — 큰 파일을 청크 스트리밍으로 다루는 패턴.

---

## 14.2 `python-multipart` — 왜 따로 깔아야 하나

본격적인 코드 전에 의존성 하나를 먼저 짚는다. 파일 업로드 코드를 쓰기 전에 다음을 설치해야 한다.

```bash
uv add fastapi "uvicorn[standard]" python-multipart
```

`python-multipart` 가 빠지면, 파일을 받는 라우트가 있는 앱을 띄울 때 FastAPI 가 다음과 비슷한 에러를 던진다.

```
RuntimeError: Form data requires "python-multipart" to be installed.
```

> **왜 FastAPI 에 기본 포함이 아닌가요?** FastAPI(정확히는 그 아래의 Starlette)는 멀티파트 본문을 직접 파싱하지 않고, `python-multipart` 라는 별도 라이브러리에 맡긴다. JSON API 만 만드는 사람은 이 의존성이 필요 없으므로, "필요한 사람만 깐다" 는 방향으로 분리되어 있다. 우리는 파일을 받을 거라 반드시 깐다.

이 예제의 `pyproject.toml` 핵심부는 다음과 같다(예제 폴더의 파일과 동일).

```toml
[project]
name = "file-upload"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "python-multipart>=0.0.9",
]

[dependency-groups]
dev = [
    "pytest>=8",
    "pytest-asyncio>=0.23",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

이번 장은 DB 를 쓰지 않으므로(메타데이터는 메모리에 둔다) SQLAlchemy·Alembic·pydantic-settings 가 없다. 의존성이 07장보다 훨씬 가볍다.

---

## 14.3 폴더 구조 한 그림

```
14-FileUpload/
├── pyproject.toml
├── uv.lock                   (uv sync 후 생성)
├── .python-version
├── .gitignore                ← 업로드 산출물(uploads/) 무시
├── README.md
├── app/
│   ├── __init__.py
│   └── main.py               ← 앱 + 업로드/다운로드 라우트 + 검증/저장 로직
└── tests/
    ├── __init__.py
    ├── conftest.py           ← 임시 저장 디렉터리 + 의존성 오버라이드
    └── test_files.py
```

07장보다 단순하다. DB 가 없으니 `models.py` / `crud.py` / `alembic/` 이 없고, 핵심 로직이 `app/main.py` 한 파일에 모여 있다.

> **`.gitignore` 에 업로드 폴더를 꼭 넣는다.** 업로드된 파일은 코드가 아니다. 사용자가 올린 산출물이라 git 에 들어가면 안 된다. 이 예제는 `uploads/` 와 `fastapi-uploads/` 를 무시한다.

---

## 14.4 `UploadFile` vs `bytes` — 무엇으로 받을까

FastAPI 에서 파일을 받는 방법은 두 가지다.

### 14.4.1 `bytes` 로 받기 — 통째로 메모리에

```python
from fastapi import FastAPI, File

app = FastAPI()


@app.post("/upload-bytes")
async def upload_bytes(file: bytes = File(...)) -> dict:
    # 이 시점에 파일 전체가 이미 메모리(RAM)에 올라와 있다.
    return {"size": len(file)}
```

`file: bytes = File(...)` 라고 적으면, FastAPI 가 파일 전체를 읽어 **하나의 `bytes` 객체** 로 넘겨준다. 다루기는 가장 쉽다. 하지만 치명적인 단점이 있다.

> **`bytes` 의 함정**: 100MB 파일을 올리면 그 100MB 가 통째로 RAM 에 올라온다. 동시에 열 명이 올리면 1GB. 큰 파일이나 동시 업로드가 있는 서비스에서는 메모리가 순식간에 터진다. **작은 파일이 확실할 때만** 쓴다.

### 14.4.2 `UploadFile` 로 받기 — 파일 같은 객체

```python
from fastapi import FastAPI, UploadFile

app = FastAPI()


@app.post("/upload-file")
async def upload_file(file: UploadFile) -> dict:
    content = await file.read()      # 필요할 때 읽는다(청크 단위도 가능)
    return {
        "filename": file.filename,    # 원본 파일명
        "content_type": file.content_type,  # MIME 타입
        "size": len(content),
    }
```

`UploadFile` 은 "파일처럼 생긴 객체" 다. 통째로 메모리에 올리는 대신, 내부적으로 **`SpooledTemporaryFile`** 을 쓴다. 작은 동안은 메모리에 있다가, 일정 크기를 넘으면 자동으로 디스크의 임시 파일로 넘어간다. 그래서 큰 파일도 메모리를 폭발시키지 않는다.

`UploadFile` 이 주는 것:

| 속성/메서드 | 설명 |
|-------------|------|
| `.filename` | 클라이언트가 보낸 원본 파일명(예: `photo.png`) |
| `.content_type` | MIME 타입(예: `image/png`) |
| `await .read(size)` | `size` 바이트만큼 읽는다. 인자 없으면 전부 |
| `await .seek(offset)` | 읽기 위치 이동(예: 다시 처음부터) |
| `await .close()` | 닫기 |

> **결론: 거의 항상 `UploadFile`.** 메모리 안전성, 파일명·콘텐츠 타입 메타데이터, 청크 읽기 — 셋 다 `UploadFile` 만 준다. 이 장의 본 예제도 처음부터 끝까지 `UploadFile` 을 쓴다.

> **왜 `File(...)` 을 안 붙여도 되나요?** 타입 힌트가 `UploadFile` 이면 FastAPI 가 "아, 이건 파일 파트구나" 를 자동으로 안다. `bytes` 의 경우엔 그냥 본문 전체로 오해할 수 있어 `File(...)` 을 명시한다. `UploadFile` 에도 `File(...)` 을 붙일 수 있고(설명·검증 메타를 달 때), 이 예제는 명시하는 쪽을 택한다.

---

## 14.5 `File()` 과 `Form()` — 멀티파트 한 본문에 파일과 텍스트를

파일만 받는 일은 드물다. 보통 "파일 + 부가 정보(설명, 카테고리...)" 를 함께 받는다. 그런데 한 가지 규칙이 있다.

> **멀티파트 요청에는 JSON 바디(`Pydantic` 모델)를 섞을 수 없다.** 한 요청은 `application/json` 이거나 `multipart/form-data` 이거나 둘 중 하나다. 파일을 받는 순간 그 요청은 멀티파트이고, 텍스트 필드도 **`Form()`** 으로 받아야 한다.

```python
from fastapi import FastAPI, File, Form, UploadFile

app = FastAPI()


@app.post("/profile")
async def upload_profile(
    nickname: str = Form(...),          # 텍스트 파트
    bio: str | None = Form(default=None),
    avatar: UploadFile = File(...),     # 파일 파트
) -> dict:
    return {"nickname": nickname, "bio": bio, "avatar": avatar.filename}
```

- **`Form(...)`** — 이 값은 JSON 바디가 아니라 멀티파트의 **텍스트 폼 필드** 에서 온다. `Field(...)` 처럼 기본값·검증을 달 수 있다.
- **`File(...)`** — 파일 파트.

> **`Form` 과 `Query` 는 뭐가 다른가요?** `Query` 는 URL 의 `?key=value` 에서 값을 읽고, `Form` 은 멀티파트/`urlencoded` **본문**의 폼 필드에서 읽는다. 둘 다 Pydantic 검증을 똑같이 받는다.

---

## 14.6 `app/main.py` — 설정과 검증 규칙

이제 본 예제다. 위에서부터 한 조각씩 만든다. 먼저 import 와 **검증 규칙·저장 위치** 부터.

```python
# app/main.py
from __future__ import annotations

import secrets
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

# 허용할 확장자(소문자, 점 포함). 화이트리스트 방식 — "허용한 것만 통과".
ALLOWED_EXTENSIONS: frozenset[str] = frozenset({".png", ".jpg", ".jpeg", ".gif", ".pdf", ".txt"})

# 허용할 콘텐츠 타입(MIME). 확장자와 함께 이중으로 점검한다.
ALLOWED_CONTENT_TYPES: frozenset[str] = frozenset(
    {
        "image/png",
        "image/jpeg",
        "image/gif",
        "application/pdf",
        "text/plain",
    }
)

# 업로드 크기 상한(바이트). 5 MiB.
MAX_FILE_SIZE: int = 5 * 1024 * 1024

# 한 번에 스트리밍으로 읽어들일 청크 크기(바이트). 64 KiB.
CHUNK_SIZE: int = 64 * 1024
```

세 가지 검증 축을 상수로 못 박았다.

1. **확장자 화이트리스트** — `.png`, `.pdf` 등 **허용할 것만** 모은 집합. 블랙리스트("이것만 막기")가 아니라 화이트리스트인 게 핵심이다.
2. **콘텐츠 타입 화이트리스트** — `image/png` 등. 확장자와 별개로 한 번 더 본다.
3. **크기 상한** — 5 MiB. 이걸 넘으면 413.

> **왜 블랙리스트가 아니라 화이트리스트인가?** "위험한 것을 막는다"(블랙리스트)는 늘 빈틈이 생긴다. `.exe` 를 막아도 `.bat`, `.sh`, `.php` ... 끝이 없다. 반대로 "허용할 것만 통과"(화이트리스트)는 새로운 위협이 나와도 자동으로 막힌다. 보안의 기본 원칙이다.

> **`frozenset` 을 쓴 이유**: 변하지 않는 집합이라 의도를 분명히 하고(실수로 추가 못 함), `in` 검사가 빠르다. 일반 `set` 이나 `tuple` 로 둬도 동작은 같다.

### 14.6.1 저장 위치를 의존성으로 빼기

```python
def get_storage_dir() -> Path:
    """업로드 파일을 저장할 디렉터리.

    의존성으로 빼 두었다. 테스트에서는 app.dependency_overrides 로
    이 함수를 임시 디렉터리를 돌려주는 함수로 갈아끼운다.
    """
    base = Path(tempfile.gettempdir()) / "fastapi-uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base
```

저장 디렉터리를 **함수 하나로 빼서 의존성으로 만든** 게 이 예제의 작은 핵심이다. 이유는 07장에서 `get_session` 을 의존성으로 둔 것과 똑같다.

- 운영에서는 OS 임시 폴더 아래 `fastapi-uploads/`(또는 환경 변수로 `./uploads`)를 쓴다.
- **테스트에서는 `app.dependency_overrides[get_storage_dir]` 한 줄로** 매 테스트마다 깨끗한 임시 폴더로 갈아끼운다. 진짜 저장 폴더를 더럽히지 않는다.

> **`tempfile.gettempdir()` 가 뭔가요?** OS 의 임시 디렉터리 경로를 돌려준다(리눅스 `/tmp`, macOS 의 `/var/folders/...` 등). 학습 예제의 기본 저장 위치로 적당하다. 운영에서는 재부팅에도 살아남는 고정 경로(`./uploads`, 또는 S3 같은 오브젝트 스토리지)를 쓴다.

---

## 14.7 메타데이터 저장소와 검증 헬퍼

### 14.7.1 메타데이터 — 학습용 인메모리

실제 파일은 디스크에 저장하고, "이 파일이 무엇인지"(원본 이름, 타입, 크기)는 따로 기록해야 다운로드할 때 찾을 수 있다. 이 메타데이터를 이번 장은 메모리 딕셔너리에 둔다.

```python
@dataclass
class StoredFile:
    """저장된 파일 한 건의 메타데이터."""

    file_id: str
    original_name: str
    stored_name: str
    content_type: str
    size: int


# file_id -> StoredFile
_FILES: dict[str, StoredFile] = {}
```

> **실전에서는 이 자리에 DB 가 온다.** `_FILES` 딕셔너리는 학습을 위해 단순화한 것이다. 서버를 재시작하면 사라지고, 여러 워커로 띄우면 공유도 안 된다. 실무에서는 6·7장의 SQLAlchemy 모델(`files` 표)로 이 메타데이터를 영속화한다. 구조는 똑같다 — "파일은 스토리지에, 메타는 DB 에".

### 14.7.2 검증 헬퍼

파일을 읽기 **전에** 확장자와 콘텐츠 타입을 먼저 본다. 큰 파일을 다 읽고 나서 거절하면 자원 낭비다.

```python
def _extension_of(filename: str | None) -> str:
    """파일명에서 소문자 확장자를 뽑는다. 없으면 빈 문자열."""
    if not filename:
        return ""
    return Path(filename).suffix.lower()


def _validate_metadata(upload: UploadFile) -> str:
    """파일을 읽기 전에 확장자/콘텐츠 타입을 먼저 점검한다.

    통과하면 확장자를 돌려주고, 실패하면 400 을 던진다.
    """
    ext = _extension_of(upload.filename)
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않은 확장자입니다: '{ext or '(없음)'}'. 허용: {allowed}",
        )
    if upload.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"허용되지 않은 콘텐츠 타입입니다: '{upload.content_type}'",
        )
    return ext
```

- **`Path(filename).suffix.lower()`** — `pathlib` 로 확장자를 뽑고 소문자로 통일한다. `PHOTO.PNG` 도 `.png` 로 본다.
- 확장자가 화이트리스트에 없으면 **400**. 콘텐츠 타입도 마찬가지.

> **확장자와 콘텐츠 타입을 둘 다 보는 이유**: 어느 쪽도 100% 믿을 수 없기 때문이다. 클라이언트는 `.png` 확장자에 아무 콘텐츠 타입이나 붙여 보낼 수 있고, 반대도 된다. 둘 다 화이트리스트로 걸러 **둘 다 통과한 것만** 받는다. (정말 엄격하게 하려면 파일의 첫 바이트(매직 넘버)까지 보는 방법도 있지만, 이 장의 범위는 넘는다.)

---

## 14.8 핵심 — 검증하며 디스크로 스트리밍 저장

이 절이 이 챕터에서 **가장 중요한 함수**다. 검증, 무작위 파일명, 청크 스트리밍, 크기 상한이 한 곳에 모인다.

```python
async def _save_upload(upload: UploadFile, storage_dir: Path) -> StoredFile:
    """검증 → 무작위 파일명으로 디스크에 스트리밍 저장 → 메타 반환.

    핵심 두 가지:
    1. 파일명을 secrets.token_hex 로 새로 만든다. 클라이언트가 보낸 원본
       파일명(../../etc/passwd 같은)을 경로에 절대 쓰지 않는다 → 경로 traversal 차단.
    2. 청크 단위로 읽으며 누적 크기를 센다. 상한을 넘는 순간 끊고 413 을 던진다.
       파일 전체를 메모리에 올리지 않으므로 큰 파일도 안전하다.
    """
    ext = _validate_metadata(upload)

    # 무작위 파일명. 원본 이름은 메타로만 보관한다.
    stored_name = f"{secrets.token_hex(16)}{ext}"
    dest = storage_dir / stored_name

    size = 0
    try:
        with dest.open("wb") as buffer:
            while chunk := await upload.read(CHUNK_SIZE):
                size += len(chunk)
                if size > MAX_FILE_SIZE:
                    # 여기까지 쓴 부분 파일은 지운다.
                    buffer.close()
                    dest.unlink(missing_ok=True)
                    # 413 Payload Too Large. Starlette 버전에 따라 상태 상수 이름이
                    # 달라(REQUEST_ENTITY_TOO_LARGE → CONTENT_TOO_LARGE) 정수 413 을 직접 쓴다.
                    raise HTTPException(
                        status_code=413,
                        detail=f"파일이 너무 큽니다. 최대 {MAX_FILE_SIZE} 바이트까지 허용됩니다.",
                    )
                buffer.write(chunk)
    finally:
        await upload.close()

    if size == 0:
        dest.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="빈 파일은 업로드할 수 없습니다.",
        )

    file_id = secrets.token_urlsafe(16)
    record = StoredFile(
        file_id=file_id,
        original_name=upload.filename or stored_name,
        stored_name=stored_name,
        content_type=upload.content_type or "application/octet-stream",
        size=size,
    )
    _FILES[file_id] = record
    return record
```

한 줄씩 뜯어 보자.

### 14.8.1 무작위 파일명으로 경로 traversal 차단

```python
stored_name = f"{secrets.token_hex(16)}{ext}"
dest = storage_dir / stored_name
```

**이것이 이 장의 가장 중요한 보안 한 줄이다.** 클라이언트가 보낸 `upload.filename` 을 디스크 경로에 **절대 그대로 쓰지 않는다**. 대신 `secrets.token_hex(16)` 으로 무작위 이름을 새로 만든다(확장자만 보존).

> **경로 traversal(path traversal) 공격이 뭔가요?** 공격자가 파일명에 `../../etc/passwd` 같은 상대 경로를 넣어, 저장 폴더 **바깥**의 파일을 덮어쓰거나 읽으려는 시도다. 만약 우리가 `storage_dir / upload.filename` 처럼 원본 이름을 그대로 이어 붙였다면, `..` 가 상위 폴더로 빠져나가 시스템 파일을 건드릴 수 있다. **무작위 이름으로 새로 지으면** 이 공격이 원천 봉쇄된다 — 공격자가 보낸 이름은 경로에 한 글자도 안 들어가니까.

> **`secrets` vs `random` vs `uuid`**: `secrets` 는 암호학적으로 안전한 난수다. 추측 불가능한 식별자가 필요할 때 쓴다. `random` 은 예측 가능할 수 있어 보안 용도엔 부적합하다. `uuid.uuid4()` 도 좋은 선택지다 — 여기서는 `secrets.token_hex`(파일명용)와 `secrets.token_urlsafe`(URL 에 들어갈 file_id 용)를 썼다.

### 14.8.2 청크 스트리밍 + 크기 상한

```python
while chunk := await upload.read(CHUNK_SIZE):
    size += len(chunk)
    if size > MAX_FILE_SIZE:
        ...
        raise HTTPException(status_code=413, ...)
    buffer.write(chunk)
```

`await upload.read(CHUNK_SIZE)` 는 한 번에 64KiB 만 읽는다. 그걸 즉시 디스크에 쓰고, 다음 청크를 읽는다. **파일 전체를 메모리에 올리지 않는다.** 100MB 파일이 와도 메모리에는 한 번에 64KiB 만 있다.

- `:=` 는 "월러스 연산자". `chunk` 에 읽은 값을 대입하면서 동시에 조건으로 쓴다. 더 읽을 게 없으면 `read` 가 빈 바이트(`b""`)를 돌려주고, 그게 거짓이라 루프가 끝난다.
- **누적 크기가 상한을 넘는 순간** 즉시 끊고, 여기까지 쓴 부분 파일을 지운 뒤 **413** 을 던진다.

> **왜 `Content-Length` 헤더만 믿지 않나요?** 클라이언트가 보낸 `Content-Length` 헤더는 거짓일 수 있다. "10바이트"라고 적고 1GB 를 보낼 수도 있다. 그래서 **실제로 읽으며 센 바이트** 를 기준으로 끊는 게 안전하다. 헤더는 참고용일 뿐이다.

> **413 상태 코드를 왜 정수로 직접 썼나요?** Starlette 버전에 따라 상수 이름이 `HTTP_413_REQUEST_ENTITY_TOO_LARGE` 에서 `HTTP_413_CONTENT_TOO_LARGE` 로 바뀌었다(둘 다 값은 413). 버전 호환을 위해 이 한 곳만 정수 `413` 을 직접 적었다. 나머지 상태 코드는 `status.HTTP_*` 상수를 그대로 쓴다.

### 14.8.3 `try/finally` 로 항상 닫기

```python
try:
    with dest.open("wb") as buffer:
        ...
finally:
    await upload.close()
```

검증에 실패해 예외가 나든, 정상으로 끝나든, **`upload.close()` 를 반드시 부른다**. `UploadFile` 은 내부적으로 임시 파일 자원을 들고 있을 수 있어, 닫아 주는 게 깔끔하다. `with` 블록은 디스크 파일(`buffer`)을 자동으로 닫는다.

### 14.8.4 빈 파일 거절

```python
if size == 0:
    dest.unlink(missing_ok=True)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="빈 파일은 ...")
```

0바이트 파일은 보통 실수(또는 장난)다. 빈 파일을 만들어 두고 400 으로 거절한다. `dest.unlink(missing_ok=True)` 로 방금 만든 0바이트 파일을 지운다.

---

## 14.9 응답 메타와 앱·라우트

### 14.9.1 응답으로 내보낼 메타

```python
def _to_meta(record: StoredFile) -> dict:
    """응답으로 내보낼 메타데이터 dict. 내부 저장 파일명은 노출하지 않는다."""
    return {
        "file_id": record.file_id,
        "filename": record.original_name,
        "content_type": record.content_type,
        "size": record.size,
    }
```

응답에는 **`stored_name`(내부 무작위 파일명)을 넣지 않는다.** 클라이언트는 `file_id` 만 알면 되고, 서버의 실제 저장 파일명은 내부 구현이라 숨긴다. (보안과 캡슐화 둘 다를 위해.)

### 14.9.2 앱과 업로드 라우트

```python
app = FastAPI(
    title="File Upload API",
    version="0.1.0",
    description="14장 파일 업로드 예제 — UploadFile, 검증, 안전한 저장, FileResponse 다운로드.",
)


@app.get("/health", tags=["meta"], summary="헬스 체크")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/files",
    status_code=status.HTTP_201_CREATED,
    tags=["files"],
    summary="단일 파일 업로드",
)
async def upload_file(
    file: UploadFile = File(..., description="업로드할 파일"),
    storage_dir: Path = Depends(get_storage_dir),
) -> dict:
    """파일 한 건을 받아 검증 후 저장하고 메타데이터를 돌려준다.

    - 허용 안 된 확장자/콘텐츠 타입 → 400
    - 크기 상한 초과 → 413
    """
    record = await _save_upload(file, storage_dir)
    return _to_meta(record)
```

- **`status_code=status.HTTP_201_CREATED`** — 새 자원(파일)이 만들어졌으니 201. 07장에서 익힌 규칙 그대로다.
- **`storage_dir: Path = Depends(get_storage_dir)`** — 저장 디렉터리를 의존성으로 주입받는다. 라우터는 "어디에 저장할지" 를 직접 모른다. 그래서 테스트에서 갈아끼울 수 있다.
- 라우터는 **HTTP 처리만** 하고, 검증·저장의 세부는 `_save_upload` 에 위임한다(07장의 "라우터는 HTTP, 로직은 분리" 정신).

### 14.9.3 다중 업로드 + 폼 필드

```python
@app.post(
    "/files/batch",
    status_code=status.HTTP_201_CREATED,
    tags=["files"],
    summary="다중 파일 업로드",
)
async def upload_files(
    files: list[UploadFile] = File(..., description="업로드할 파일들"),
    note: str | None = Form(default=None, description="선택 메모(폼 필드)"),
    storage_dir: Path = Depends(get_storage_dir),
) -> dict:
    """여러 파일을 한 번에 받는다. Form 필드와 파일을 같이 받는 예시도 겸한다."""
    saved = [_to_meta(await _save_upload(f, storage_dir)) for f in files]
    return {"count": len(saved), "items": saved, "note": note}
```

- **`files: list[UploadFile]`** — 같은 필드명(`files`)으로 여러 파일을 받으면 리스트가 된다. 단일과 다중의 차이는 타입 힌트 한 글자(`list[...]`)뿐이다.
- **`note: str | None = Form(default=None)`** — 파일과 함께 일반 텍스트 필드를 받는다. 멀티파트 요청이라 `Form()` 으로 받는다.

> **다중 업로드에서 하나가 실패하면?** 이 예제는 리스트 컴프리헨션 안에서 순서대로 저장하다가, 하나라도 검증에 실패하면 그 자리에서 예외가 올라가 400/413 으로 끊긴다. 앞에서 이미 저장된 파일은 디스크에 남을 수 있다 — 학습 예제라 단순하게 뒀다. 실무에서는 "전부 검증 먼저 → 전부 저장" 2단계로 나누거나, 실패 시 앞선 파일을 정리하는 로직을 더한다.

---

## 14.10 `FileResponse` — 파일 다운로드

저장한 파일을 다시 내려주는 라우트다.

```python
@app.get(
    "/files/{file_id}",
    tags=["files"],
    summary="파일 다운로드",
)
async def download_file(
    file_id: str,
    storage_dir: Path = Depends(get_storage_dir),
) -> FileResponse:
    """저장된 파일을 원본 파일명으로 내려준다.

    경로 파라미터로는 무작위 file_id 만 받는다. 실제 디스크 경로는 서버가
    메타데이터에서 찾아 구성하므로, 클라이언트가 경로를 조작할 수 없다.
    """
    record = _FILES.get(file_id)
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"파일 {file_id} 를 찾을 수 없습니다.",
        )

    path = storage_dir / record.stored_name
    if not path.exists():
        # 메타는 있는데 실제 파일이 사라진 경우(직접 삭제 등).
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="저장된 파일을 디스크에서 찾을 수 없습니다.",
        )

    return FileResponse(
        path=path,
        media_type=record.content_type,
        filename=record.original_name,
    )
```

### 14.10.1 `FileResponse` 가 해 주는 것

`FileResponse` 는 디스크의 파일을 효율적으로 내려주는 전용 응답 클래스다.

- 파일을 **청크 단위로 스트리밍** 한다. 통째로 메모리에 안 올린다(업로드와 대칭).
- `media_type` — 응답의 `Content-Type` 헤더.
- `filename` — 이걸 주면 `Content-Disposition: attachment; filename="..."` 헤더가 붙어, 브라우저가 그 이름으로 **다운로드** 한다.

> **`Content-Disposition` 헤더가 뭔가요?** "이 응답을 브라우저에 그려라(inline) vs 파일로 저장해라(attachment)" 를 정하는 헤더다. `FileResponse(filename=...)` 는 `attachment` 로 붙여, 클릭하면 다운로드되게 한다. 원본 파일명을 여기에 실어 보낸다.

### 14.10.2 file_id 만 받는 게 또 하나의 보안 장치

경로 파라미터로 **무작위 `file_id`** 만 받는다는 점이 중요하다. 만약 `GET /files/{경로}` 식으로 클라이언트가 파일 경로를 직접 넘기게 했다면, 또 경로 traversal 위험이 생긴다. 우리는 클라이언트가 추측 불가능한 `file_id` 만 알고, 실제 디스크 경로는 **서버가 메타데이터에서 찾아 구성** 한다. 클라이언트가 경로를 조작할 여지가 없다.

> **메타는 있는데 파일이 없으면?** 누군가 디스크에서 파일만 지웠을 수 있다. `path.exists()` 로 한 번 더 확인하고, 없으면 404 를 돌려준다. 메타와 실제 파일의 불일치를 우아하게 처리한다.

---

## 14.11 `tests/conftest.py` — 임시 저장 디렉터리 주입

07장에서 `get_session` 을 메모리 DB 로 갈아끼웠듯, 여기서는 `get_storage_dir` 을 **매 테스트마다 새 임시 폴더** 로 갈아끼운다.

```python
# tests/conftest.py
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import _FILES, app, get_storage_dir


@pytest_asyncio.fixture
async def client(tmp_path: Path) -> AsyncGenerator[AsyncClient, None]:
    """의존성 오버라이드된 비동기 HTTP 클라이언트.

    tmp_path 는 pytest 가 매 테스트마다 만들어 주는 고유한 임시 디렉터리다.
    그 안에 uploads/ 를 만들어 저장 경로로 주입한다.
    """
    storage_dir = tmp_path / "uploads"
    storage_dir.mkdir()

    def override_storage_dir() -> Path:
        return storage_dir

    # 앱의 저장 경로 의존성을 테스트용 임시 폴더로 교체.
    app.dependency_overrides[get_storage_dir] = override_storage_dir
    # 인메모리 메타데이터도 매 테스트마다 비워 격리한다.
    _FILES.clear()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    _FILES.clear()


@pytest.fixture
def png_bytes() -> bytes:
    """아주 작은 유효한 PNG(1x1) 바이트."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
```

핵심을 짚자.

> **`tmp_path` 가 뭔가요?** pytest 가 기본 제공하는 fixture 다. 테스트 함수마다 **고유한 임시 디렉터리**(`Path` 객체)를 만들어 주고, 테스트가 끝나면 알아서 정리한다. 우리는 그 안에 `uploads/` 를 만들어 저장 경로로 주입한다. 매 테스트가 자기만의 폴더를 쓰므로 완벽히 격리된다.

- **`app.dependency_overrides[get_storage_dir] = override_storage_dir`** — 07장의 `get_session` 오버라이드와 똑같은 패턴. 앱 코드는 한 글자도 안 바꾸고 저장 위치만 테스트용으로 바꾼다.
- **`_FILES.clear()`** — 인메모리 메타데이터는 모듈 전역이라 테스트 간에 샐 수 있다. 시작·끝에 비워서 격리한다. (실전처럼 DB 였다면 DB fixture 가 이 역할을 했을 것이다.)
- **`png_bytes` fixture** — 진짜 PNG 헤더를 가진 1x1 이미지 바이트. 콘텐츠 자체를 검증하진 않지만, 실제 파일처럼 다뤄 본다.

> **httpx 로 파일을 어떻게 보내나요?** `client.post(url, files={"필드명": (파일명, 바이트, 콘텐츠타입)})` 형식이다. httpx 가 이 인자를 보면 자동으로 `multipart/form-data` 요청을 만든다. 폼 필드는 `data={"note": "..."}` 로 함께 보낸다.

---

## 14.12 `tests/test_files.py` — 16개 케이스

테스트 함수 이름이 곧 사양이다. 주요 케이스를 보자(전체는 예제 폴더의 `tests/test_files.py`).

```python
# tests/test_files.py 일부
from httpx import AsyncClient

from app.main import MAX_FILE_SIZE


class TestUploadFile:
    async def test_정상_업로드는_201_과_메타데이터를_돌려준다(
        self, client: AsyncClient, png_bytes: bytes
    ) -> None:
        res = await client.post(
            "/files",
            files={"file": ("photo.png", png_bytes, "image/png")},
        )
        assert res.status_code == 201
        body = res.json()
        assert body["filename"] == "photo.png"
        assert body["size"] == len(png_bytes)
        assert body["file_id"]

    async def test_너무_큰_파일은_413(self, client: AsyncClient) -> None:
        big = b"a" * (MAX_FILE_SIZE + 1)
        res = await client.post(
            "/files",
            files={"file": ("big.txt", big, "text/plain")},
        )
        assert res.status_code == 413


class TestPathTraversalSafety:
    async def test_경로_조작_파일명도_안전하게_저장된다(
        self, client: AsyncClient, png_bytes: bytes
    ) -> None:
        # 원본 파일명에 경로 조작 시도가 들어와도 무작위 이름으로 저장된다.
        res = await client.post(
            "/files",
            files={"file": ("../../etc/passwd.png", png_bytes, "image/png")},
        )
        assert res.status_code == 201
        # 다운로드가 정상 동작한다 = 경로가 깨지지 않았다는 증거.
        file_id = res.json()["file_id"]
        dl = await client.get(f"/files/{file_id}")
        assert dl.status_code == 200
        assert dl.content == png_bytes
        assert "passwd.png" in dl.headers.get("content-disposition", "")
```

전체 16개 케이스 목록:

1. 헬스 체크가 OK 를 돌려준다.
2. 정상 업로드는 201 과 메타데이터.
3. 텍스트 파일도 업로드된다.
4. 허용 안 된 확장자는 400.
5. 허용 안 된 콘텐츠 타입은 400.
6. 너무 큰 파일은 413.
7. 상한 경계 크기(정확히 `MAX_FILE_SIZE`)는 정상 저장된다.
8. 빈 파일은 400.
9. 확장자가 없으면 400.
10. 경로 조작 파일명도 안전하게 저장된다(다운로드까지 검증).
11. 다중 업로드는 여러 건을 저장한다.
12. 폼 필드(`note`)를 파일과 함께 받는다.
13. 다중 업로드 중 하나라도 검증 실패면 400.
14. 업로드한 파일을 그대로 다운로드한다(바이트 일치 + Content-Disposition).
15. 없는 id 다운로드는 404.
16. 업로드 → 다운로드 전체 흐름.

> **경계 케이스(7번)를 꼭 넣자.** "상한보다 1바이트 큰 건 거절(6번)" 과 "상한 정확히 같은 건 통과(7번)" 를 한 쌍으로 둔다. `>` 인지 `>=` 인지 같은 off-by-one 실수를 이 한 쌍이 잡아준다.

### 14.12.1 실행

```bash
uv run pytest -q
```

성공하면 다음과 비슷한 출력이 나온다.

```
................                                                         [100%]
16 passed in 0.08s
```

매 테스트가 자기만의 임시 폴더 위에서 돌고, 시작·끝에 `_FILES` 를 비우므로 **순서에 의존하지 않는다**.

---

## 14.13 서버 띄우고 직접 호출해 보기

```bash
uv run uvicorn app.main:app --reload
```

### 14.13.1 업로드

```bash
curl -F "file=@./photo.png" http://127.0.0.1:8000/files
```

응답(201):

```json
{
  "file_id": "x3aB7...무작위...",
  "filename": "photo.png",
  "content_type": "image/png",
  "size": 12345
}
```

### 14.13.2 허용 안 된 확장자

```bash
curl -i -F "file=@./script.exe" http://127.0.0.1:8000/files
```

응답(400):

```json
{ "detail": "허용되지 않은 확장자입니다: '.exe'. 허용: .gif, .jpeg, .jpg, .pdf, .png, .txt" }
```

### 14.13.3 다운로드

```bash
# 위에서 받은 file_id 로. -OJ 는 서버가 준 파일명으로 저장.
curl -OJ http://127.0.0.1:8000/files/<file_id>
```

원본 파일명(`photo.png`)으로 파일이 저장된다.

### 14.13.4 자동 문서로 한 번 더

브라우저에서 `http://127.0.0.1:8000/docs` 를 열면, `/files` 라우트에 **파일 선택 버튼이 달린 폼**이 자동으로 생긴다. `UploadFile` 타입을 보고 FastAPI 가 알아서 만들어 준 것이다. "Try it out" 으로 파일을 골라 바로 업로드해 볼 수 있다.

---

## 14.14 메모리 vs 디스크 — 트레이드오프 정리

이 장 내내 "메모리에 통째로 올리지 말고 스트리밍하라" 고 했다. 표로 정리한다.

| | `bytes = File(...)` (메모리) | `UploadFile` + 청크 스트리밍 (디스크) |
|---|---|---|
| 코드 단순함 | 가장 단순 | 약간 더 복잡 |
| 작은 파일(수십 KB) | 충분히 OK | OK |
| 큰 파일(수십~수백 MB) | **위험**(RAM 폭발) | 안전 |
| 동시 업로드 다수 | **위험** | 안전 |
| 크기 제한 | 다 읽고 나서야 앎 | 읽는 도중 끊을 수 있음 |
| 파일명/메타데이터 | 없음 | `.filename`, `.content_type` |

> **그럼 항상 디스크 스트리밍인가요?** 원칙적으로 그렇다. 다만 "썸네일처럼 작은 게 확실하고, 받자마자 메모리에서 변환만 하고 버린다" 같은 경우엔 `await file.read()` 로 한 번에 읽어도 괜찮다. 중요한 건 **무제한으로 메모리에 올리지 않는다** 는 감각이다.

### 14.14.1 한 단계 더 — 큰 파일과 스토리지

이 예제의 다음 진화 방향을 짧게만 짚는다(이 장의 범위는 아니다).

- **오브젝트 스토리지** — 운영에서는 로컬 디스크 대신 S3 / GCS 같은 오브젝트 스토리지에 올리고, 서버는 메타데이터(+ 스토리지 키)만 DB 에 남긴다.
- **업로드 직후 후처리** — 썸네일 생성, 바이러스 검사 같은 무거운 작업은 응답을 막지 않도록 **백그라운드 작업**으로 넘긴다. 바로 다음 15장의 주제다.

---

## 14.15 흔한 실수 / 트러블슈팅

### 14.15.1 `RuntimeError: Form data requires "python-multipart" to be installed.`

파일/폼을 받는 라우트가 있는데 `python-multipart` 가 안 깔렸다. `uv add python-multipart` 로 설치한다(14.2 절).

### 14.15.2 `415 Unsupported Media Type` 또는 본문이 안 들어옴

클라이언트가 `multipart/form-data` 가 아니라 JSON 으로 보냈을 때 흔하다. 파일 업로드는 멀티파트여야 한다. curl 은 `-F`(폼), httpx 는 `files=`/`data=` 를 쓴다. `-d '{...}'`(JSON)로 보내면 안 된다.

### 14.15.3 큰 파일을 올리면 메모리가 치솟는다

`file: bytes = File(...)` 로 받고 있을 가능성이 높다. `UploadFile` 로 바꾸고, `await file.read(CHUNK_SIZE)` 청크 루프로 디스크에 쓰자(14.8 절).

### 14.15.4 두 번째로 `read()` 하면 빈 바이트가 나온다

`UploadFile` 은 한 번 끝까지 읽으면 커서가 끝에 있다. 다시 읽으려면 `await file.seek(0)` 로 되감는다. (이 예제는 한 번만 읽으므로 해당 없음.)

### 14.15.5 다운로드한 파일이 깨진다

`FileResponse` 의 `media_type` 이 실제 파일과 다르거나, 업로드 저장 때 텍스트 모드로 열어(`"w"`) 바이너리가 깨졌을 수 있다. 저장은 반드시 **바이너리 모드(`"wb"`)** 로 연다(14.8 절).

### 14.15.6 클라이언트 파일명을 그대로 저장하고 있다

**가장 위험한 실수다.** `storage_dir / upload.filename` 처럼 원본 파일명을 경로에 쓰면 경로 traversal 에 노출된다. 무작위 파일명(`secrets.token_hex(...)`)으로 새로 지어 저장하자(14.8.1 절).

### 14.15.7 테스트가 실제 폴더를 더럽힌다

`get_storage_dir` 을 의존성으로 빼지 않았거나, 테스트에서 오버라이드하지 않았을 때다. `app.dependency_overrides[get_storage_dir]` 로 `tmp_path` 기반 폴더를 주입하자(14.11 절).

### 14.15.8 413 상태 코드 상수가 없다는 에러

Starlette 버전에 따라 `status.HTTP_413_REQUEST_ENTITY_TOO_LARGE` 또는 `status.HTTP_413_CONTENT_TOO_LARGE` 다. 버전에 상관없이 안전하게 하려면 이 한 곳만 정수 `413` 을 직접 쓴다(14.8.2 절).

---

## 14.16 이 챕터 요약

- 파일은 JSON 이 아니라 **`multipart/form-data`** 로 온다. 그래서 `python-multipart` 가 필요하고, 텍스트 필드는 `Form()`, 파일은 `UploadFile`/`File()` 로 받는다.
- **`UploadFile` 을 기본으로 쓴다.** 메모리 안전(청크 스트리밍), 파일명·콘텐츠 타입 메타, `seek`/`read` 를 모두 준다. `bytes` 는 작은 파일이 확실할 때만.
- **검증 세 축**: 확장자 화이트리스트, 콘텐츠 타입 화이트리스트, 크기 상한. 실패는 400(형식)·413(크기)으로 일관되게.
- **보안의 핵심 한 줄**: 클라이언트 파일명을 절대 경로에 쓰지 말고 `secrets` 로 무작위 이름을 새로 지어라. 경로 traversal 을 원천 차단한다.
- **크기 제한은 실제로 읽으며 센 바이트로** 끊는다. `Content-Length` 헤더는 못 믿는다.
- **다운로드는 `FileResponse(path, media_type, filename)`**. `filename` 을 주면 원본 이름으로 내려받게 된다. 클라이언트는 무작위 `file_id` 만 알고, 실제 경로는 서버가 메타에서 구성한다.
- **테스트**는 `get_storage_dir` 을 `tmp_path` 폴더로 오버라이드해 격리한다. 07장의 `get_session` 오버라이드와 같은 패턴이다. httpx 는 `files=`/`data=` 로 멀티파트를 보낸다.
- 메타데이터는 이 예제에서 메모리에 뒀지만, 실전에서는 **DB(스토리지엔 파일, DB엔 메타)** 로 영속화한다.

다음 챕터에서는 업로드 직후의 썸네일 생성·이메일 발송 같은 **무거운 후처리를 응답을 막지 않고 처리하는 백그라운드 작업**을 다룬다.

---

← [13. 테스트 작성 심화](13-testing-deep.md) | [README로 돌아가기](../README.md) | 다음 문서로 이동: **[15. 백그라운드 작업 →](15-background-tasks.md)**
