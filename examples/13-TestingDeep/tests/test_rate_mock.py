"""외부 HTTP 호출 모킹 테스트 — 이 챕터의 하이라이트.

`GET /rate/{code}` 는 외부 환율 API 를 부른다(`app/services.py` 의 `fetch_rate`).
테스트에서 진짜 네트워크를 타면 느리고, 불안정하고, 외부 서비스에 의존하게 된다.
그래서 외부 호출 함수를 **가짜로 바꿔치워** 우리 코드만 격리해서 검증한다.

여기서는 두 가지 방법을 모두 보여준다.
1. `monkeypatch` 로 `services.fetch_rate` 자체를 가짜 코루틴으로 교체.
2. `app.dependency_overrides` 로 의존성(`get_rate_fetcher`)을 교체.

추가로, httpx 의 `MockTransport` 로 "HTTP 레이어만" 가짜로 만드는 더 현실적인 방법도 본다.
"""

import httpx
import pytest

from app import services
from app.main import app, get_rate_fetcher


# ---------------------------------------------------------------------------
# 방법 1) monkeypatch 로 외부 함수 자체를 교체
# ---------------------------------------------------------------------------
class TestRateWithMonkeypatch:
    async def test_가짜_환율을_돌려주도록_교체한다(
        self,
        client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def fake_fetch_rate(code: str) -> float:
            # 진짜 네트워크 대신 고정된 값을 돌려준다.
            return 1387.5

        # services 모듈의 fetch_rate 를 가짜로 바꾼다.
        # 라우터의 의존성(get_rate_fetcher)이 services.fetch_rate 를 돌려주므로,
        # 모듈 속성을 바꾸면 라우터가 가짜를 부르게 된다.
        monkeypatch.setattr(services, "fetch_rate", fake_fetch_rate)

        res = await client.get("/rate/usd")
        assert res.status_code == 200
        body = res.json()
        assert body == {"code": "USD", "rate": 1387.5}

    async def test_외부가_실패하면_503_으로_변환된다(
        self,
        client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        async def failing_fetch_rate(code: str) -> float:
            raise services.RateUnavailableError("upstream 500")

        monkeypatch.setattr(services, "fetch_rate", failing_fetch_rate)

        res = await client.get("/rate/usd")
        assert res.status_code == 503
        assert "환율 정보를 가져올 수 없습니다" in res.json()["detail"]

    async def test_가짜_함수가_받은_인자를_검증한다(
        self,
        client,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        calls: list[str] = []

        async def recording_fetch_rate(code: str) -> float:
            calls.append(code)
            return 100.0

        monkeypatch.setattr(services, "fetch_rate", recording_fetch_rate)

        await client.get("/rate/eur")
        # 라우터가 우리 함수를 정확히 한 번, 올바른 인자로 불렀는지 확인.
        assert calls == ["eur"]

    @pytest.mark.parametrize("bad_code", ["1", "U", "TOOLONG", "U$D"])
    async def test_잘못된_코드_형식은_외부_호출_전에_422(
        self,
        client,
        monkeypatch: pytest.MonkeyPatch,
        bad_code: str,
    ) -> None:
        called = False

        async def should_not_be_called(code: str) -> float:
            nonlocal called
            called = True
            return 0.0

        monkeypatch.setattr(services, "fetch_rate", should_not_be_called)

        res = await client.get(f"/rate/{bad_code}")
        assert res.status_code == 422
        # 형식 검증에서 막혔다면 외부 호출은 일어나지 않아야 한다.
        assert called is False


# ---------------------------------------------------------------------------
# 방법 2) dependency_overrides 로 의존성을 교체
# ---------------------------------------------------------------------------
class TestRateWithDependencyOverride:
    async def test_의존성_오버라이드로_가짜_fetcher_를_주입한다(
        self,
        client,
    ) -> None:
        async def fake_fetch(code: str) -> float:
            return 9.99

        # get_rate_fetcher 가 돌려주는 "함수" 자체를 가짜로 바꾼다.
        app.dependency_overrides[get_rate_fetcher] = lambda: fake_fetch
        try:
            res = await client.get("/rate/jpy")
            assert res.status_code == 200
            assert res.json() == {"code": "JPY", "rate": 9.99}
        finally:
            # 다른 테스트에 영향이 가지 않도록 반드시 정리한다.
            app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# 방법 3) httpx.MockTransport 로 HTTP 레이어만 가짜로
# ---------------------------------------------------------------------------
class TestFetchRateUnit:
    """라우터가 아니라 services.fetch_rate 함수 자체를 단위 테스트한다.

    monkeypatch 로 httpx.AsyncClient 를 MockTransport 가 붙은 버전으로 바꾼다.
    이렇게 하면 fetch_rate 안의 'URL 조립 → 응답 파싱 → 예외 정규화' 로직까지 검증할 수 있다.
    """

    async def test_정상_응답을_파싱한다(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        captured: dict[str, str] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            return httpx.Response(200, json={"rate": 1400.0})

        transport = httpx.MockTransport(handler)

        # AsyncClient 를 만들 때 우리 transport 가 끼워지도록 감싼다.
        real_async_client = httpx.AsyncClient

        def patched_async_client(*args, **kwargs):
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

        rate = await services.fetch_rate("usd")
        assert rate == 1400.0
        # URL 이 대문자 코드로 조립됐는지 확인.
        assert captured["url"].endswith("/USD")

    async def test_5xx_응답은_RateUnavailableError(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(500, text="boom")

        transport = httpx.MockTransport(handler)
        real_async_client = httpx.AsyncClient

        def patched_async_client(*args, **kwargs):
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

        with pytest.raises(services.RateUnavailableError):
            await services.fetch_rate("usd")

    async def test_형식이_깨진_응답도_RateUnavailableError(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        def handler(request: httpx.Request) -> httpx.Response:
            # rate 키가 없는 JSON → KeyError → 정규화되어야 한다.
            return httpx.Response(200, json={"unexpected": True})

        transport = httpx.MockTransport(handler)
        real_async_client = httpx.AsyncClient

        def patched_async_client(*args, **kwargs):
            kwargs["transport"] = transport
            return real_async_client(*args, **kwargs)

        monkeypatch.setattr(httpx, "AsyncClient", patched_async_client)

        with pytest.raises(services.RateUnavailableError):
            await services.fetch_rate("usd")
