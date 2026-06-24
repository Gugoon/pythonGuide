"""pytest 전역 설정 / 공통 fixture.

DB 가 없는 예제라 conftest 가 하는 일은 단 하나다:
실제 서버를 띄우지 않고 앱에 직접 요청을 보낼 수 있는 `httpx.AsyncClient` 를 만든다.

`ASGITransport(app=app)` 는 HTTP 를 진짜 네트워크가 아니라 ASGI 인터페이스로
곧장 앱에 전달한다. 빠르고 격리가 깔끔하다(07·13장과 동일한 패턴).

`raise_app_exceptions=False` 를 주는 이유:
기본값(True)이면, 앱에서 처리되지 못한 예외를 테스트 클라이언트가 그대로 다시
던진다. 우리는 500 핸들러가 만든 JSON 응답 자체를 검증하고 싶으므로(=실제 서버가
클라이언트에게 보내는 것과 같은 응답), 이 옵션을 꺼서 예외 대신 500 응답을 받는다.
"""

from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
