"""Note API 통합 테스트.

흐름:
- 회원가입 → 로그인 → 메모 CRUD 한 바퀴
- 인증 실패(토큰 없음)
- 본인 소유 검사(타인 메모 접근 시 404)
- 검색·필터·페이지네이션
"""

from __future__ import annotations

from httpx import AsyncClient

from .conftest import signup_and_login


async def test_health(client: AsyncClient) -> None:
    """헬스체크는 인증 없이 200."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_signup_login_me_flow(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
) -> None:
    """회원가입 → 로그인 → 메모 생성 → 목록까지 한 바퀴."""
    # 1) 회원가입
    r = await client.post("/auth/signup", json=alice_signup)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == alice_signup["email"]
    assert body["is_active"] is True
    # 응답에 비밀번호가 새 나가지 않는지 확인.
    assert "hashed_password" not in body
    assert "password" not in body

    # 2) 로그인
    r = await client.post("/auth/login", data=alice_login)
    assert r.status_code == 200
    token = r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"

    # 3) 메모 생성
    r = await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "첫 메모", "body": "FastAPI 시작!", "tag": "diary"},
    )
    assert r.status_code == 201, r.text
    note = r.json()
    assert note["title"] == "첫 메모"
    assert note["tag"] == "diary"
    note_id = note["id"]

    # 4) 단건 조회
    r = await client.get(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert r.json()["body"] == "FastAPI 시작!"

    # 5) 부분 수정
    r = await client.patch(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"title": "제목 수정됨"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "제목 수정됨"
    assert body["body"] == "FastAPI 시작!"  # body는 안 보냈으니 그대로

    # 6) 삭제 → 204
    r = await client.delete(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 204
    assert r.content == b""

    # 7) 다시 조회 → 404
    r = await client.get(
        f"/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 404


async def test_signup_duplicate_email_returns_409(
    client: AsyncClient,
    alice_signup: dict[str, str],
) -> None:
    """같은 이메일로 두 번 가입하면 409."""
    r1 = await client.post("/auth/signup", json=alice_signup)
    assert r1.status_code == 201
    r2 = await client.post("/auth/signup", json=alice_signup)
    assert r2.status_code == 409
    assert "이미" in r2.json()["detail"]


async def test_login_wrong_password_returns_401(
    client: AsyncClient,
    alice_signup: dict[str, str],
) -> None:
    """잘못된 비밀번호로 로그인하면 401, 메시지는 통일."""
    await client.post("/auth/signup", json=alice_signup)

    r = await client.post(
        "/auth/login",
        data={"username": alice_signup["email"], "password": "wrongpassword"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다"


async def test_login_unknown_user_same_message(client: AsyncClient) -> None:
    """존재하지 않는 사용자도 같은 메시지(=정보 누설 방지)."""
    r = await client.post(
        "/auth/login",
        data={"username": "nobody@example.com", "password": "whatever123"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다"


async def test_notes_without_token_returns_401(client: AsyncClient) -> None:
    """토큰 없이 보호된 라우트에 접근하면 401."""
    r = await client.get("/notes")
    assert r.status_code == 401


async def test_create_note_validation_errors(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
) -> None:
    """제목·본문이 빈 문자열이면 422가 떨어진다."""
    token = await signup_and_login(client, alice_signup, alice_login)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/notes", headers=headers, json={"title": "", "body": "x"}
    )
    assert r.status_code == 422

    r = await client.post(
        "/notes", headers=headers, json={"title": "ok", "body": ""}
    )
    assert r.status_code == 422


async def test_other_users_note_returns_404(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
    bob_signup: dict[str, str],
    bob_login: dict[str, str],
) -> None:
    """타인 메모에 접근 시 403이 아니라 404로 응답.

    "권한 없음"이라고 알려주면 "그 ID의 메모가 다른 누군가에게 존재한다"는
    정보를 노출하게 된다. 그래서 표준 패턴은 그냥 404다.
    """
    # Alice가 메모 한 건 만든다.
    alice_token = await signup_and_login(client, alice_signup, alice_login)
    r = await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "alice의 비밀", "body": "ssh"},
    )
    assert r.status_code == 201
    alice_note_id = r.json()["id"]

    # Bob 가입·로그인
    bob_token = await signup_and_login(client, bob_signup, bob_login)
    bob_headers = {"Authorization": f"Bearer {bob_token}"}

    # Bob이 Alice의 메모를 GET 시도 → 404
    r = await client.get(f"/notes/{alice_note_id}", headers=bob_headers)
    assert r.status_code == 404

    # PATCH 시도 → 404
    r = await client.patch(
        f"/notes/{alice_note_id}",
        headers=bob_headers,
        json={"title": "bob이 훔쳤다"},
    )
    assert r.status_code == 404

    # DELETE 시도 → 404
    r = await client.delete(f"/notes/{alice_note_id}", headers=bob_headers)
    assert r.status_code == 404

    # Alice가 자기 메모를 다시 조회하면 잘 나오는지 확인 (안 망가졌는지)
    r = await client.get(
        f"/notes/{alice_note_id}",
        headers={"Authorization": f"Bearer {alice_token}"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "alice의 비밀"


async def test_list_notes_returns_only_my_notes(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
    bob_signup: dict[str, str],
    bob_login: dict[str, str],
) -> None:
    """내 목록에는 내 메모만 보인다."""
    alice_token = await signup_and_login(client, alice_signup, alice_login)
    await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "A1", "body": "alice 1"},
    )
    await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {alice_token}"},
        json={"title": "A2", "body": "alice 2"},
    )

    bob_token = await signup_and_login(client, bob_signup, bob_login)
    await client.post(
        "/notes",
        headers={"Authorization": f"Bearer {bob_token}"},
        json={"title": "B1", "body": "bob 1"},
    )

    # Alice의 목록 — 2건만.
    r = await client.get(
        "/notes", headers={"Authorization": f"Bearer {alice_token}"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    titles = sorted(item["title"] for item in body["items"])
    assert titles == ["A1", "A2"]


async def test_list_notes_pagination_and_filter(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
) -> None:
    """skip/limit 페이지네이션과 tag 필터, 검색 필터가 모두 동작한다."""
    token = await signup_and_login(client, alice_signup, alice_login)
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(5):
        await client.post(
            "/notes",
            headers=headers,
            json={"title": f"item {i}", "body": f"body {i}", "tag": "work"},
        )
    await client.post(
        "/notes",
        headers=headers,
        json={"title": "diary 1", "body": "오늘 일기", "tag": "diary"},
    )

    # 페이지네이션
    r = await client.get(
        "/notes", headers=headers, params={"skip": 1, "limit": 2}
    )
    body = r.json()
    assert body["total"] == 6
    assert body["skip"] == 1
    assert body["limit"] == 2
    assert len(body["items"]) == 2

    # 태그 필터
    r = await client.get("/notes", headers=headers, params={"tag": "diary"})
    body = r.json()
    assert body["total"] == 1
    assert body["items"][0]["title"] == "diary 1"

    # 검색 (대소문자 무시 — 본문에 "오늘"이 들어간 것만)
    r = await client.get("/notes", headers=headers, params={"search": "오늘"})
    body = r.json()
    assert body["total"] == 1


async def test_patch_with_empty_body_keeps_original(
    client: AsyncClient,
    alice_signup: dict[str, str],
    alice_login: dict[str, str],
) -> None:
    """빈 본문 PATCH는 원본을 그대로 돌려준다(`exclude_unset=True` 덕분)."""
    token = await signup_and_login(client, alice_signup, alice_login)
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.post(
        "/notes",
        headers=headers,
        json={"title": "원본", "body": "원본 본문", "tag": "x"},
    )
    note_id = r.json()["id"]

    r = await client.patch(f"/notes/{note_id}", headers=headers, json={})
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "원본"
    assert body["body"] == "원본 본문"
    assert body["tag"] == "x"
