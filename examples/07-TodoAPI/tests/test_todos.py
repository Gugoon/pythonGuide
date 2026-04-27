"""Todo API 통합 테스트.

각 테스트는 깨끗한 in-memory DB 위에서 돈다(`conftest.py` 참고).
테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다.
"""

from httpx import AsyncClient


class TestHealthEndpoint:
    async def test_헬스_체크는_ok_를_돌려준다(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestCreateTodo:
    async def test_정상_생성은_201_과_본문을_돌려준다(
        self,
        client: AsyncClient,
        sample_payload: dict,
    ) -> None:
        res = await client.post("/todos", json=sample_payload)
        assert res.status_code == 201

        body = res.json()
        assert body["id"] > 0
        assert body["title"] == sample_payload["title"]
        assert body["description"] == sample_payload["description"]
        assert body["is_done"] is False
        # 시각 필드는 자동으로 채워진다.
        assert body["created_at"] is not None
        assert body["updated_at"] is not None

    async def test_제목이_빈_문자열이면_422(self, client: AsyncClient) -> None:
        res = await client.post("/todos", json={"title": ""})
        assert res.status_code == 422

    async def test_제목이_없는_본문이면_422(self, client: AsyncClient) -> None:
        res = await client.post("/todos", json={"description": "제목이 없네요"})
        assert res.status_code == 422

    async def test_제목_길이가_200자를_넘으면_422(self, client: AsyncClient) -> None:
        too_long = "가" * 201
        res = await client.post("/todos", json={"title": too_long})
        assert res.status_code == 422


class TestReadTodo:
    async def test_없는_id_조회는_404(self, client: AsyncClient) -> None:
        res = await client.get("/todos/9999")
        assert res.status_code == 404

    async def test_생성_후_단건_조회가_가능하다(
        self,
        client: AsyncClient,
        sample_payload: dict,
    ) -> None:
        created = (await client.post("/todos", json=sample_payload)).json()

        res = await client.get(f"/todos/{created['id']}")
        assert res.status_code == 200
        assert res.json()["id"] == created["id"]
        assert res.json()["title"] == sample_payload["title"]


class TestListTodos:
    async def test_목록_응답_구조(self, client: AsyncClient) -> None:
        for i in range(3):
            await client.post("/todos", json={"title": f"item {i}"})

        res = await client.get("/todos")
        assert res.status_code == 200
        body = res.json()
        assert {"items", "total", "skip", "limit"} == set(body.keys())
        assert body["total"] == 3
        assert body["skip"] == 0
        assert body["limit"] == 20
        assert len(body["items"]) == 3

    async def test_skip_limit_페이지네이션이_적용된다(
        self,
        client: AsyncClient,
    ) -> None:
        for i in range(5):
            await client.post("/todos", json={"title": f"item {i}"})

        res = await client.get("/todos", params={"skip": 1, "limit": 2})
        assert res.status_code == 200
        body = res.json()
        assert body["total"] == 5
        assert body["skip"] == 1
        assert body["limit"] == 2
        assert len(body["items"]) == 2

    async def test_is_done_필터로_미완료만_가져온다(
        self,
        client: AsyncClient,
    ) -> None:
        a = (await client.post("/todos", json={"title": "A"})).json()
        await client.post("/todos", json={"title": "B"})
        # A 만 완료 처리.
        await client.patch(f"/todos/{a['id']}", json={"is_done": True})

        # 미완료(is_done=false) 만 조회.
        res = await client.get("/todos", params={"is_done": False})
        body = res.json()
        assert body["total"] == 1
        assert all(item["is_done"] is False for item in body["items"])

    async def test_limit_상한을_벗어나면_422(self, client: AsyncClient) -> None:
        res = await client.get("/todos", params={"limit": 1000})
        assert res.status_code == 422


class TestUpdateTodo:
    async def test_부분_수정은_보낸_필드만_바꾼다(
        self,
        client: AsyncClient,
        sample_payload: dict,
    ) -> None:
        created = (await client.post("/todos", json=sample_payload)).json()

        # title 만 보내고 description, is_done 은 그대로 두자.
        res = await client.patch(
            f"/todos/{created['id']}",
            json={"title": "수정된 제목"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["title"] == "수정된 제목"
        # 보내지 않은 필드는 원래 값 유지.
        assert body["description"] == sample_payload["description"]
        assert body["is_done"] is False

    async def test_없는_id_수정은_404(self, client: AsyncClient) -> None:
        res = await client.patch("/todos/9999", json={"title": "x"})
        assert res.status_code == 404

    async def test_빈_본문도_정상_처리되어_원본을_돌려준다(
        self,
        client: AsyncClient,
        sample_payload: dict,
    ) -> None:
        created = (await client.post("/todos", json=sample_payload)).json()

        res = await client.patch(f"/todos/{created['id']}", json={})
        assert res.status_code == 200
        assert res.json()["title"] == created["title"]


class TestDeleteTodo:
    async def test_삭제는_204_를_돌려주고_본문이_없다(
        self,
        client: AsyncClient,
        sample_payload: dict,
    ) -> None:
        created = (await client.post("/todos", json=sample_payload)).json()

        res = await client.delete(f"/todos/{created['id']}")
        assert res.status_code == 204
        # 204 는 본문이 없어야 한다.
        assert res.content == b""

        # 다시 조회하면 404.
        res = await client.get(f"/todos/{created['id']}")
        assert res.status_code == 404

    async def test_없는_id_삭제는_404(self, client: AsyncClient) -> None:
        res = await client.delete("/todos/9999")
        assert res.status_code == 404


class TestFullFlow:
    async def test_생성_조회_수정_삭제_전체_흐름(
        self,
        client: AsyncClient,
    ) -> None:
        # 1) 생성
        res = await client.post(
            "/todos",
            json={"title": "장보기"},
        )
        assert res.status_code == 201
        todo_id = res.json()["id"]

        # 2) 단건 조회
        res = await client.get(f"/todos/{todo_id}")
        assert res.status_code == 200
        assert res.json()["title"] == "장보기"
        assert res.json()["is_done"] is False

        # 3) 완료 처리(부분 수정)
        res = await client.patch(
            f"/todos/{todo_id}",
            json={"is_done": True},
        )
        assert res.status_code == 200
        assert res.json()["is_done"] is True

        # 4) 삭제
        res = await client.delete(f"/todos/{todo_id}")
        assert res.status_code == 204

        # 5) 재조회는 404
        res = await client.get(f"/todos/{todo_id}")
        assert res.status_code == 404
