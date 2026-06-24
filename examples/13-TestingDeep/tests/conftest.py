"""pytest 전역 설정 / 공통 픽스처.

이 파일이 하는 일:

1. ASGI 트랜스포트로 앱에 직접 요청을 보내는 `AsyncClient` 픽스처를 만든다.
2. 매 테스트 전에 인메모리 저장소를 비워, 테스트끼리 상태가 새지 않게 한다.
3. 여러 테스트가 함께 쓰는 작은 데이터 픽스처(`sample_quote`)를 둔다.

여기 둔 픽스처는 같은 `tests/` 폴더의 모든 테스트 파일이 별도 import 없이 바로 쓸 수 있다.
이것이 `conftest.py` 의 핵심 역할이다.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app, reset_state


@pytest.fixture(autouse=True)
def reset_store() -> None:
    """매 테스트 시작 전에 인메모리 저장소를 초기화한다.

    `autouse=True` 라서 테스트가 이 픽스처 이름을 인자로 적지 않아도 자동으로 적용된다.
    덕분에 모든 테스트가 "빈 저장소" 라는 같은 출발선에서 시작한다.
    """
    reset_state()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """ASGI 트랜스포트로 앱에 직접 요청을 보내는 비동기 클라이언트.

    진짜 네트워크를 타지 않고 앱의 ASGI 인터페이스로 곧장 요청이 전달되므로
    빠르고 격리가 깔끔하다. 07·08장에서 쓴 것과 같은 패턴이다.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_quote() -> dict:
    """기본 명언 생성 페이로드. 테스트마다 살짝 바꿔 쓴다."""
    return {"text": "단순함은 신뢰성의 전제 조건이다.", "author": "Dijkstra"}
