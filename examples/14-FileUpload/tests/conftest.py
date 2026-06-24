"""pytest 전역 설정 / 공통 fixture.

이 파일이 하는 일은 두 가지다.

1. 매 테스트마다 깨끗한 **임시 저장 디렉터리**를 준비하고, `get_storage_dir`
   의존성을 그 디렉터리로 갈아끼운다(의존성 오버라이드).
2. 진짜 서버 없이 앱에 직접 요청을 보내는 비동기 HTTP 클라이언트를 만든다.

이렇게 해두면 테스트가 실제 디스크의 고정 폴더를 더럽히지 않고, 매 테스트가
서로 격리된 임시 폴더 위에서 돈다.
"""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import _FILES, app, get_storage_dir


@pytest_asyncio.fixture
async def client(tmp_path: Path) -> AsyncGenerator[AsyncClient, None]:
    """의존성 오버라이드된 비동기 HTTP 클라이언트.

    `tmp_path` 는 pytest 가 매 테스트마다 만들어 주는 고유한 임시 디렉터리다.
    그 안에 `uploads/` 를 만들어 저장 경로로 주입한다.
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
    """아주 작은 유효한 PNG(1x1) 바이트. 콘텐츠 자체는 검증하지 않지만,
    실제 파일처럼 다뤄 보기 위해 진짜 PNG 헤더를 쓴다."""
    return (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
        b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
        b"\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
