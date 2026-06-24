"""에러 핸들링·로깅 심화 통합 테스트.

테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다.
크게 세 묶음이다.

1. 정상 응답 — 핸들러가 정상 흐름을 망가뜨리지 않는지.
2. 일관된 에러 스키마 — 커스텀 예외·HTTPException·검증 에러·500 이 모두 같은 모양인지.
3. 요청 ID — X-Request-ID 가 응답 헤더에 늘 있고, 보낸 값이 그대로 전파되는지.
"""

from httpx import AsyncClient

from app.middleware import REQUEST_ID_HEADER


def assert_error_shape(body: dict) -> dict:
    """에러 응답이 일관된 스키마를 따르는지 확인하고, error 본문을 돌려준다.

    모양: {"error": {"code": str, "message": str, "detail": ..., "request_id": str}}
    """
    assert set(body.keys()) == {"error"}
    err = body["error"]
    assert set(err.keys()) == {"code", "message", "detail", "request_id"}
    assert isinstance(err["code"], str) and err["code"]
    assert isinstance(err["message"], str) and err["message"]
    assert isinstance(err["request_id"], str) and err["request_id"]
    return err


class TestHealthyResponses:
    async def test_헬스_체크는_정상_200(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}

    async def test_존재하는_상품_조회는_200(self, client: AsyncClient) -> None:
        res = await client.get("/items/1")
        assert res.status_code == 200
        body = res.json()
        assert body["id"] == 1
        assert body["name"] == "노트북"

    async def test_정상_주문은_성공_본문을_돌려준다(self, client: AsyncClient) -> None:
        res = await client.post("/orders", json={"item_id": 1, "quantity": 2})
        assert res.status_code == 200
        body = res.json()
        assert body["ordered"] is True
        assert body["item_id"] == 1
        assert body["quantity"] == 2


class TestCustomException:
    async def test_없는_상품_조회는_커스텀_404와_일관된_스키마(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/items/9999")
        assert res.status_code == 404

        err = assert_error_shape(res.json())
        assert err["code"] == "resource_not_found"
        # detail 에 어떤 자원이 없었는지가 담긴다.
        assert err["detail"]["resource"] == "item"
        assert err["detail"]["id"] == 9999

    async def test_재고_부족_주문은_비즈니스_규칙_409(
        self, client: AsyncClient
    ) -> None:
        # 2번 상품은 재고 0. 1개라도 주문하면 규칙 위반.
        res = await client.post("/orders", json={"item_id": 2, "quantity": 1})
        assert res.status_code == 409

        err = assert_error_shape(res.json())
        assert err["code"] == "business_rule_violation"
        assert err["detail"]["in_stock"] == 0
        assert err["detail"]["requested"] == 1

    async def test_주문_대상_상품이_없으면_404(self, client: AsyncClient) -> None:
        res = await client.post("/orders", json={"item_id": 777, "quantity": 1})
        assert res.status_code == 404
        err = assert_error_shape(res.json())
        assert err["code"] == "resource_not_found"


class TestValidationError:
    async def test_수량이_범위를_벗어나면_422_일관된_스키마(
        self, client: AsyncClient
    ) -> None:
        # quantity 상한은 100. 초과하면 검증 실패.
        res = await client.post("/orders", json={"item_id": 1, "quantity": 999})
        assert res.status_code == 422

        err = assert_error_shape(res.json())
        assert err["code"] == "validation_error"
        # detail 에는 Pydantic 이 준 상세 목록이 그대로 들어 있다.
        assert isinstance(err["detail"], list)
        assert len(err["detail"]) >= 1
        # 어느 필드가 틀렸는지 loc 로 알 수 있다.
        locs = [tuple(item["loc"]) for item in err["detail"]]
        assert ("body", "quantity") in locs

    async def test_필수_필드_누락도_422(self, client: AsyncClient) -> None:
        res = await client.post("/orders", json={"item_id": 1})
        assert res.status_code == 422
        err = assert_error_shape(res.json())
        assert err["code"] == "validation_error"

    async def test_없는_경로는_404도_같은_에러_스키마(
        self, client: AsyncClient
    ) -> None:
        # 라우트가 없는 경로 → Starlette 의 404. HTTPException 핸들러가 통일한다.
        res = await client.get("/no-such-path")
        assert res.status_code == 404
        err = assert_error_shape(res.json())
        assert err["code"] == "http_404"


class TestUnhandledException:
    async def test_예상_못_한_예외는_500이지만_내부를_노출하지_않는다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/boom")
        assert res.status_code == 500

        err = assert_error_shape(res.json())
        assert err["code"] == "internal_error"
        # 트레이스백·예외 메시지 원문이 그대로 새지 않아야 한다(보안).
        assert "ValueError" not in err["message"]
        assert "의도적으로" not in err["message"]
        # 대신 request_id 가 있어 로그에서 추적할 수 있다.
        assert err["request_id"] != "-"


class TestRequestId:
    async def test_정상_응답에도_X_Request_ID_헤더가_있다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/health")
        assert REQUEST_ID_HEADER in res.headers
        assert res.headers[REQUEST_ID_HEADER]  # 빈 문자열이 아니다.

    async def test_에러_응답에도_X_Request_ID_헤더가_있다(
        self, client: AsyncClient
    ) -> None:
        res = await client.get("/items/9999")
        assert res.status_code == 404
        assert REQUEST_ID_HEADER in res.headers
        # 헤더의 ID 와 본문의 request_id 가 같아야 한다(상관관계).
        assert res.headers[REQUEST_ID_HEADER] == res.json()["error"]["request_id"]

    async def test_클라이언트가_보낸_요청_ID가_그대로_전파된다(
        self, client: AsyncClient
    ) -> None:
        my_id = "test-correlation-id-123"
        res = await client.get("/health", headers={REQUEST_ID_HEADER: my_id})
        assert res.headers[REQUEST_ID_HEADER] == my_id

    async def test_보내지_않으면_매_요청마다_다른_ID가_생성된다(
        self, client: AsyncClient
    ) -> None:
        r1 = await client.get("/health")
        r2 = await client.get("/health")
        assert r1.headers[REQUEST_ID_HEADER] != r2.headers[REQUEST_ID_HEADER]
