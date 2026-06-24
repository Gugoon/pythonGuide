# 14-FileUpload — FastAPI 파일 업로드/다운로드 예제

FastAPI 가이드 [14장 파일 업로드](../../docs/14-file-upload.md)의 완성본입니다. `UploadFile` 로 파일을 받아 **검증**(확장자·콘텐츠 타입·크기)하고, **무작위 파일명**으로 안전하게 저장한 뒤, `FileResponse` 로 다시 내려주는 작은 API입니다.

## 사용 기술

- Python 3.13
- FastAPI 0.115.x
- python-multipart (멀티파트 폼 파싱 — 파일 업로드 필수)
- pytest + httpx (테스트)
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
- Swagger UI: http://127.0.0.1:8000/docs (파일 업로드 폼을 바로 눌러볼 수 있습니다)
- 헬스 체크: http://127.0.0.1:8000/health

저장 위치는 기본적으로 OS 임시 폴더 아래 `fastapi-uploads/` 입니다(`app/main.py`의 `get_storage_dir`). 고정 폴더(`./uploads`)로 바꾸고 싶다면 그 함수만 고치면 됩니다.

## 테스트 실행

```bash
uv run pytest -v
```

테스트는 `tmp_path` 기반 임시 디렉터리를 의존성 오버라이드로 주입하므로, 실제 저장 폴더를 더럽히지 않습니다.

## 폴더 구조

```
14-FileUpload/
├── pyproject.toml
├── uv.lock                   (uv sync 후 생성)
├── .python-version
├── .gitignore
├── README.md
├── app/
│   ├── __init__.py
│   └── main.py               # FastAPI 앱 + 업로드/다운로드 라우트 + 검증/저장 로직
└── tests/
    ├── __init__.py
    ├── conftest.py           # 임시 저장 디렉터리 + get_storage_dir 오버라이드
    └── test_files.py
```

## 엔드포인트

| 메서드 | 경로 | 설명 | 성공 상태 |
|--------|------|------|-----------|
| `POST` | `/files` | 단일 파일 업로드 | 201 |
| `POST` | `/files/batch` | 다중 파일 업로드(+ 선택 폼 필드 `note`) | 201 |
| `GET` | `/files/{file_id}` | 파일 다운로드 | 200 |
| `GET` | `/health` | 헬스 체크 | 200 |

검증 실패 시 응답:

- 허용 안 된 확장자/콘텐츠 타입, 빈 파일 → **400 Bad Request**
- 크기 상한(기본 5 MiB) 초과 → **413 Request Entity Too Large**
- 없는 `file_id` 다운로드 → **404 Not Found**

## curl 로 직접 호출

```bash
# 업로드
curl -F "file=@./photo.png" http://127.0.0.1:8000/files
# -> {"file_id":"...", "filename":"photo.png", "content_type":"image/png", "size":12345}

# 다운로드 (위에서 받은 file_id 사용)
curl -OJ http://127.0.0.1:8000/files/<file_id>
```

## 다음 단계

이 예제는 메타데이터를 메모리에 보관합니다. 실전에서는 이 자리에 DB(6·7장의 SQLAlchemy 패턴)가 들어가고, 업로드 직후 후처리(썸네일 생성, 바이러스 검사 등)는 **15장 백그라운드 작업**으로 넘깁니다.
