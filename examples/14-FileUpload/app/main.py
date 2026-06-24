"""파일 업로드/다운로드 예제 — FastAPI `UploadFile`.

이 파일 하나에 14장의 핵심이 모두 들어 있다.

- POST /files       : 단일 파일 업로드(검증 → 안전한 저장 → 메타 반환)
- POST /files/batch : 다중 파일 업로드
- GET  /files/{id}  : 저장된 파일 다운로드(`FileResponse`)

학습용으로 메타데이터는 메모리 딕셔너리(`_FILES`)에 담는다. 실전에서는
이 자리에 DB(예: SQLAlchemy 모델) 가 들어간다 — 12장에서 다룬 패턴 그대로다.

`uvicorn app.main:app --reload` 가 이 파일의 `app` 객체를 찾아 실행한다.
"""

from __future__ import annotations

import secrets
import tempfile
from dataclasses import dataclass
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

# ---------------------------------------------------------------------------
# 설정 — 검증 규칙과 저장 위치
# ---------------------------------------------------------------------------

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


def get_storage_dir() -> Path:
    """업로드 파일을 저장할 디렉터리.

    의존성으로 빼 두었다. 테스트에서는 `app.dependency_overrides` 로
    이 함수를 임시 디렉터리를 돌려주는 함수로 갈아끼운다(conftest.py 참고).

    기본값은 OS 임시 폴더 아래 `fastapi-uploads/`. 운영에서는 환경 변수나
    설정 객체(7장 config.py 패턴)로 `./uploads` 같은 고정 경로를 주입한다.
    """
    base = Path(tempfile.gettempdir()) / "fastapi-uploads"
    base.mkdir(parents=True, exist_ok=True)
    return base


# ---------------------------------------------------------------------------
# 메타데이터 저장소(학습용 인메모리) — 실전에서는 DB 로 교체
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 검증 헬퍼
# ---------------------------------------------------------------------------


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


async def _save_upload(upload: UploadFile, storage_dir: Path) -> StoredFile:
    """검증 → 무작위 파일명으로 디스크에 스트리밍 저장 → 메타 반환.

    핵심 두 가지:
    1. 파일명을 `secrets.token_hex` 로 새로 만든다. 클라이언트가 보낸 원본
       파일명(`../../etc/passwd` 같은)을 경로에 절대 쓰지 않는다 → 경로 traversal 차단.
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


def _to_meta(record: StoredFile) -> dict:
    """응답으로 내보낼 메타데이터 dict. 내부 저장 파일명은 노출하지 않는다."""
    return {
        "file_id": record.file_id,
        "filename": record.original_name,
        "content_type": record.content_type,
        "size": record.size,
    }


# ---------------------------------------------------------------------------
# 앱과 라우트
# ---------------------------------------------------------------------------

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
    """여러 파일을 한 번에 받는다. `Form` 필드와 파일을 같이 받는 예시도 겸한다.

    하나라도 검증에 실패하면 그 시점에 4xx 로 끊는다(부분 저장이 남을 수 있으나,
    학습 예제이므로 단순하게 둔다 — 실전에서는 트랜잭션/정리 로직을 더한다).
    """
    saved = [_to_meta(await _save_upload(f, storage_dir)) for f in files]
    return {"count": len(saved), "items": saved, "note": note}


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

    경로 파라미터로는 무작위 `file_id` 만 받는다. 실제 디스크 경로는 서버가
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
