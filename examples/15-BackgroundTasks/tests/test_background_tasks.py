"""BackgroundTasks 통합 테스트.

각 테스트는 깨끗한 인메모리 상태 위에서 돈다(`conftest.py` 의 reset_state).

검증 전략: `ASGITransport` 에서 BackgroundTasks 는 **응답 전송이 끝난 뒤** 실행되며,
`await client.post(...)` 가 반환될 시점에는 그 작업들이 이미 완료돼 있다. 그래서
요청을 보낸 뒤 상태(`/notifications`, `/audit-log`)를 조회해 작업 수행 여부를 확인한다.
테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다.
"""

from httpx import AsyncClient

from app import state


class TestHealthEndpoint:
    async def test_헬스_체크는_ok_를_돌려준다(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestSignupResponseFirst:
    async def test_가입은_201_과_사용자명을_즉시_돌려준다(
        self, client: AsyncClient
    ) -> None:
        res = await client.post("/signup", json={"username": "alice"})
        assert res.status_code == 201
        body = res.json()
        assert body["username"] == "alice"
        assert body["status"] == "registered"

    async def test_빈_사용자명은_422(self, client: AsyncClient) -> None:
        res = await client.post("/signup", json={"username": ""})
        assert res.status_code == 422


class TestBackgroundTaskRuns:
    async def test_가입_후_환영_알림이_백그라운드로_기록된다(
        self, client: AsyncClient
    ) -> None:
        # 응답을 받은 시점엔 백그라운드 작업이 이미 실행돼 있다.
        await client.post("/signup", json={"username": "bob"})

        res = await client.get("/notifications")
        notifications = res.json()["notifications"]
        assert len(notifications) == 1
        assert "bob" in notifications[0]

    async def test_비동기_작업_함수도_실행되어_감사로그가_남는다(
        self, client: AsyncClient
    ) -> None:
        await client.post("/signup", json={"username": "carol"})

        res = await client.get("/audit-log")
        entries = res.json()["entries"]
        assert len(entries) == 1
        assert entries[0] == {"username": "carol", "source": "signup"}


class TestMultipleTasks:
    async def test_여러_작업이_모두_실행된다(self, client: AsyncClient) -> None:
        # /signup 은 알림·감사로그·포인트 지급 세 작업을 등록한다.
        await client.post("/signup", json={"username": "dave"})

        notifications = (await client.get("/notifications")).json()["notifications"]
        audit = (await client.get("/audit-log")).json()["entries"]

        assert any("dave" in n for n in notifications)
        assert any(e["username"] == "dave" for e in audit)
        # 보너스 포인트도 지급됐는지 인메모리 상태로 직접 확인.
        assert state.points["dave"] == 100

    async def test_여러_번_가입하면_알림이_누적된다(
        self, client: AsyncClient
    ) -> None:
        await client.post("/signup", json={"username": "u1"})
        await client.post("/signup", json={"username": "u2"})

        notifications = (await client.get("/notifications")).json()["notifications"]
        assert len(notifications) == 2


class TestIdempotency:
    async def test_같은_사용자_보너스는_한_번만_지급된다(
        self, client: AsyncClient
    ) -> None:
        # 같은 사용자로 두 번 가입(중복 등록 상황을 흉내).
        await client.post("/signup", json={"username": "eve"})
        await client.post("/signup", json={"username": "eve"})

        # grant_starter_points 는 멱등이라 두 배가 되지 않는다.
        assert state.points["eve"] == 100


class TestExceptionSafety:
    async def test_부수_작업이_실패해도_뒤_작업은_실행된다(
        self, client: AsyncClient
    ) -> None:
        # risky_side_effect(실패) 를 먼저 등록하고 notify_welcome 을 뒤에 등록.
        await client.post("/signup-with-risky-task", json={"username": "frank"})

        # 실패는 함수 안에서 삼켜 기록되고,
        assert len(state.failures) == 1
        assert "frank" in state.failures[0]
        # 뒤에 등록한 환영 알림은 정상 실행된다.
        notifications = (await client.get("/notifications")).json()["notifications"]
        assert any("frank" in n for n in notifications)


class TestDependencyInjectedTasks:
    async def test_의존성에서_등록한_작업과_라우터_작업이_함께_실행된다(
        self, client: AsyncClient
    ) -> None:
        await client.post("/signup-via-dependency", json={"username": "grace"})

        # 의존성(audit_logger)이 등록한 감사 로그(source="dependency").
        audit = (await client.get("/audit-log")).json()["entries"]
        assert len(audit) == 1
        assert audit[0]["source"] == "dependency"

        # 라우터가 직접 등록한 환영 알림.
        notifications = (await client.get("/notifications")).json()["notifications"]
        assert any("grace" in n for n in notifications)
