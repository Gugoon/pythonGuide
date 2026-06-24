"""파일 업로드/다운로드 통합 테스트.

각 테스트는 깨끗한 임시 저장 디렉터리 위에서 돈다(`conftest.py` 참고).
테스트 함수 이름이 곧 사양이 되도록 한국어로 적는다.

httpx 로 multipart 업로드를 보낼 때는 `files=` 인자를 쓴다. 형식은
`{"필드명": (파일명, 바이트, 콘텐츠타입)}` 이다.
"""

from httpx import AsyncClient

from app.main import MAX_FILE_SIZE


class TestHealthEndpoint:
    async def test_헬스_체크는_ok_를_돌려준다(self, client: AsyncClient) -> None:
        res = await client.get("/health")
        assert res.status_code == 200
        assert res.json() == {"status": "ok"}


class TestUploadFile:
    async def test_정상_업로드는_201_과_메타데이터를_돌려준다(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        res = await client.post(
            "/files",
            files={"file": ("photo.png", png_bytes, "image/png")},
        )
        assert res.status_code == 201

        body = res.json()
        assert body["filename"] == "photo.png"
        assert body["content_type"] == "image/png"
        assert body["size"] == len(png_bytes)
        assert body["file_id"]  # 비어있지 않은 무작위 id

    async def test_텍스트_파일도_업로드된다(self, client: AsyncClient) -> None:
        res = await client.post(
            "/files",
            files={"file": ("memo.txt", b"hello world", "text/plain")},
        )
        assert res.status_code == 201
        assert res.json()["size"] == len(b"hello world")

    async def test_허용_안_된_확장자는_400(self, client: AsyncClient) -> None:
        res = await client.post(
            "/files",
            files={"file": ("evil.exe", b"MZ\x90\x00", "application/octet-stream")},
        )
        assert res.status_code == 400
        assert "확장자" in res.json()["detail"]

    async def test_허용_안_된_콘텐츠_타입은_400(self, client: AsyncClient) -> None:
        # 확장자는 .png 로 위장했지만 콘텐츠 타입이 허용 목록에 없다.
        res = await client.post(
            "/files",
            files={"file": ("fake.png", b"\x00\x01\x02", "application/x-msdownload")},
        )
        assert res.status_code == 400
        assert "콘텐츠 타입" in res.json()["detail"]

    async def test_너무_큰_파일은_413(self, client: AsyncClient) -> None:
        big = b"a" * (MAX_FILE_SIZE + 1)
        res = await client.post(
            "/files",
            files={"file": ("big.txt", big, "text/plain")},
        )
        assert res.status_code == 413
        assert "너무 큽니다" in res.json()["detail"]

    async def test_상한_경계_크기는_정상_저장된다(self, client: AsyncClient) -> None:
        exact = b"a" * MAX_FILE_SIZE
        res = await client.post(
            "/files",
            files={"file": ("edge.txt", exact, "text/plain")},
        )
        assert res.status_code == 201
        assert res.json()["size"] == MAX_FILE_SIZE

    async def test_빈_파일은_400(self, client: AsyncClient) -> None:
        res = await client.post(
            "/files",
            files={"file": ("empty.txt", b"", "text/plain")},
        )
        assert res.status_code == 400
        assert "빈 파일" in res.json()["detail"]

    async def test_확장자가_없으면_400(self, client: AsyncClient) -> None:
        res = await client.post(
            "/files",
            files={"file": ("noext", b"data", "text/plain")},
        )
        assert res.status_code == 400


class TestPathTraversalSafety:
    async def test_경로_조작_파일명도_안전하게_저장된다(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        # 원본 파일명에 경로 조작 시도가 들어와도, 서버는 무작위 이름으로 저장한다.
        res = await client.post(
            "/files",
            files={"file": ("../../etc/passwd.png", png_bytes, "image/png")},
        )
        assert res.status_code == 201
        # 메타의 filename 은 원본을 그대로 보존하되, 실제 저장은 무작위 이름이므로
        # 다운로드가 정상 동작해야 한다(경로가 깨지지 않았다는 증거).
        file_id = res.json()["file_id"]
        dl = await client.get(f"/files/{file_id}")
        assert dl.status_code == 200
        assert dl.content == png_bytes
        # 원본 파일명(의 마지막 구성요소)은 메타로 보존된다.
        assert "passwd.png" in dl.headers.get("content-disposition", "")


class TestUploadBatch:
    async def test_다중_업로드는_여러_건을_저장한다(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        res = await client.post(
            "/files/batch",
            files=[
                ("files", ("a.png", png_bytes, "image/png")),
                ("files", ("b.txt", b"second", "text/plain")),
            ],
        )
        assert res.status_code == 201
        body = res.json()
        assert body["count"] == 2
        assert {item["filename"] for item in body["items"]} == {"a.png", "b.txt"}

    async def test_폼_필드를_파일과_함께_받는다(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        res = await client.post(
            "/files/batch",
            data={"note": "여행 사진"},
            files=[("files", ("trip.png", png_bytes, "image/png"))],
        )
        assert res.status_code == 201
        body = res.json()
        assert body["count"] == 1
        assert body["note"] == "여행 사진"

    async def test_다중_업로드_중_하나라도_검증_실패면_400(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        res = await client.post(
            "/files/batch",
            files=[
                ("files", ("ok.png", png_bytes, "image/png")),
                ("files", ("bad.exe", b"MZ", "application/octet-stream")),
            ],
        )
        assert res.status_code == 400


class TestDownloadFile:
    async def test_업로드한_파일을_그대로_다운로드한다(
        self,
        client: AsyncClient,
        png_bytes: bytes,
    ) -> None:
        up = await client.post(
            "/files",
            files={"file": ("photo.png", png_bytes, "image/png")},
        )
        file_id = up.json()["file_id"]

        res = await client.get(f"/files/{file_id}")
        assert res.status_code == 200
        # 바이트가 손실 없이 그대로 돌아온다.
        assert res.content == png_bytes
        assert res.headers["content-type"].startswith("image/png")
        # 원본 파일명으로 내려받게 Content-Disposition 헤더가 붙는다.
        assert "photo.png" in res.headers.get("content-disposition", "")

    async def test_없는_id_다운로드는_404(self, client: AsyncClient) -> None:
        res = await client.get("/files/does-not-exist")
        assert res.status_code == 404


class TestFullFlow:
    async def test_업로드_후_다운로드_전체_흐름(
        self,
        client: AsyncClient,
    ) -> None:
        payload = b"the quick brown fox" * 100

        # 1) 업로드
        up = await client.post(
            "/files",
            files={"file": ("doc.txt", payload, "text/plain")},
        )
        assert up.status_code == 201
        file_id = up.json()["file_id"]
        assert up.json()["size"] == len(payload)

        # 2) 다운로드 — 내용 일치
        dl = await client.get(f"/files/{file_id}")
        assert dl.status_code == 200
        assert dl.content == payload
