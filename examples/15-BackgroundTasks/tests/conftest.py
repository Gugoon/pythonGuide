"""pytest 공통 fixture.

이 파일이 하는 일은 두 가지다.

1. 매 테스트 전에 인메모리 상태(`app/state.py`)를 깨끗이 초기화한다.
   백그라운드 작업이 누적해 남기는 기록이 다른 테스트로 새지 않도록 격리한다.
2. ASGI 인터페이스로 앱에 직접 요청을 보내는 비동기 HTTP 클라이언트를 제공한다.

**핵심 타이밍**: httpx 의 `ASGITransport` 로 보낸 요청은, `await client.post(...)` 가
반환될 때 응답 전송이 끝나 있고 그 직후 BackgroundTasks 도 모두 실행된 상태가 된다.
즉, 호출이 끝난 뒤 `/notifications` 등을 조회하면 백그라운드 작업의 결과를 확인할 수 있다.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import state
from app.main import app


@pytest.fixture(autouse=True)
def reset_state() -> None:
    """매 테스트 전에 인메모리 상태를 비운다(autouse 라 자동 적용)."""
    state.reset()
    yield
    state.reset()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """ASGI 인터페이스로 앱에 직접 요청을 보내는 비동기 클라이언트.

    실제 네트워크/서버를 띄우지 않으므로 빠르고 격리된다.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
