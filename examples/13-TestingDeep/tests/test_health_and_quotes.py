"""기본 엔드포인트와 인메모리 CRUD 테스트.

픽스처(`client`, `sample_quote`)와 에러 케이스(404 / 422)를 보여준다.
테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다.
"""

from httpx import AsyncClient


class TestHealth:
    async def test_헬스_체크는_ok_를_돌려준다(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestCreateQuote:
    async def test_정상_생성은_201_과_본문을_돌려준다(
        self,
        client: AsyncClient,
        sample_quote: dict,
    ) -> None:
        res = await client.post("/quotes", json=sample_quote)
        assert res.status_code == 201

        body = res.json()
        assert body["id"] == 1
        assert body["text"] == sample_quote["text"]
        assert body["author"] == sample_quote["author"]

    async def test_빈_본문이면_422(self, client: AsyncClient) -> None:
        res = await client.post("/quotes", json={})
        assert res.status_code == 422

    async def test_text_가_280자를_넘으면_422(self, client: AsyncClient) -> None:
        too_long = "가" * 281
        res = await client.post(
            "/quotes", json={"text": too_long, "author": "익명"}
        )
        assert res.status_code == 422


class TestReadQuote:
    async def test_없는_id_조회는_404(self, client: AsyncClient) -> None:
        res = await client.get("/quotes/9999")
        assert res.status_code == 404
        # detail 메시지 형식도 함께 확인한다.
        assert "9999" in res.json()["detail"]

    async def test_생성_후_단건_조회가_가능하다(
        self,
        client: AsyncClient,
        sample_quote: dict,
    ) -> None:
        created = (await client.post("/quotes", json=sample_quote)).json()

        res = await client.get(f"/quotes/{created['id']}")
        assert res.status_code == 200
        assert res.json()["author"] == sample_quote["author"]


class TestIsolation:
    """reset_store(autouse) 픽스처가 테스트 사이 상태를 비우는지 확인."""

    async def test_첫_테스트에서_명언을_하나_만든다(
        self,
        client: AsyncClient,
        sample_quote: dict,
    ) -> None:
        await client.post("/quotes", json=sample_quote)
        res = await client.get("/quotes")
        assert len(res.json()) == 1

    async def test_두번째_테스트는_빈_저장소에서_시작한다(
        self,
        client: AsyncClient,
    ) -> None:
        # 앞 테스트가 만든 데이터가 새지 않아야 한다. 새 id 는 다시 1 이다.
        res = await client.get("/quotes")
        assert res.json() == []

        created = (
            await client.post(
                "/quotes", json={"text": "처음부터 다시", "author": "익명"}
            )
        ).json()
        assert created["id"] == 1
