"""블로그 API 통합 테스트.

각 케이스는 conftest의 인메모리 DB 위에서 독립 실행됩니다.
테스트 묶음:
1. 회원가입 + 로그인 + 내 정보
2. 글 작성·목록·검색·태그 필터·페이지네이션
3. 비공개 글이 비로그인에게 보이지 않는다
4. 본인이 아닌 글은 수정·삭제 불가
5. 글 게시 토글(publish/unpublish)
6. 댓글 작성·수정·삭제
7. 태그 자동 생성 및 N:M 연결
8. PATCH로 태그 전체 교체
9. 글 삭제 시 댓글·태그 cascade (lazy load 회귀 방지)
10. 헬스체크
"""

from __future__ import annotations

from httpx import AsyncClient


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# 1) 회원가입 + 로그인 + 내 정보

async def test_signup_login_me(
    client: AsyncClient, alice_payload: dict[str, str]
) -> None:
    r = await client.post("/auth/signup", json=alice_payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == alice_payload["email"]
    assert body["name"] == alice_payload["name"]
    assert "hashed_password" not in body

    r = await client.post(
        "/auth/login",
        data={
            "username": alice_payload["email"],
            "password": alice_payload["password"],
        },
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    r = await client.get("/auth/me", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["email"] == alice_payload["email"]


# 2) 글 작성, 목록, 검색, 태그 필터, 페이지네이션

async def test_create_and_list_posts_with_search_and_tag_filter(
    client: AsyncClient, alice_token: str
) -> None:
    # 두 개의 공개 글 (서로 다른 태그)
    r = await client.post(
        "/posts",
        json={
            "title": "Hello FastAPI",
            "body": "FastAPI 가이드 본문",
            "published": True,
            "tags": ["python", "fastapi"],
        },
        headers=auth(alice_token),
    )
    assert r.status_code == 201, r.text
    first = r.json()
    assert first["slug"].startswith("hello-fastapi")
    tag_names = {t["name"] for t in first["tags"]}
    assert tag_names == {"python", "fastapi"}

    r = await client.post(
        "/posts",
        json={
            "title": "MySQL Tips",
            "body": "asyncmy로 비동기 연결",
            "published": True,
            "tags": ["python", "mysql"],
        },
        headers=auth(alice_token),
    )
    assert r.status_code == 201

    # 비로그인 목록
    r = await client.get("/posts")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2

    # 검색
    r = await client.get("/posts", params={"q": "FastAPI"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "Hello FastAPI"

    # 태그 필터
    r = await client.get("/posts", params={"tag": "mysql"})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) == 1
    assert items[0]["title"] == "MySQL Tips"

    # 페이지네이션 — 한 페이지에 1개씩
    r = await client.get("/posts", params={"page": 1, "size": 1})
    assert r.status_code == 200
    page1 = r.json()
    assert page1["total"] == 2
    assert len(page1["items"]) == 1

    r = await client.get("/posts", params={"page": 2, "size": 1})
    page2 = r.json()
    assert page2["total"] == 2
    assert len(page2["items"]) == 1
    # 두 페이지의 글이 다르다
    assert page1["items"][0]["id"] != page2["items"][0]["id"]


# 3) 비공개 글은 비로그인에게 보이지 않는다

async def test_draft_invisible_to_anonymous_visible_to_owner(
    client: AsyncClient, alice_token: str
) -> None:
    r = await client.post(
        "/posts",
        json={"title": "Secret Note", "body": "draft", "published": False},
        headers=auth(alice_token),
    )
    assert r.status_code == 201
    post_id = r.json()["id"]

    # 비로그인 단건 조회 → 404
    r = await client.get(f"/posts/{post_id}")
    assert r.status_code == 404

    # 비로그인 목록 → 빈 결과(공개 글이 없으므로)
    r = await client.get("/posts")
    assert r.status_code == 200
    assert r.json()["total"] == 0

    # 본인은 단건도 목록도 보임
    r = await client.get(f"/posts/{post_id}", headers=auth(alice_token))
    assert r.status_code == 200
    r = await client.get("/posts", headers=auth(alice_token))
    assert r.status_code == 200
    assert r.json()["total"] == 1


# 4) 다른 사람의 글은 수정·삭제 불가

async def test_cannot_modify_others_post(
    client: AsyncClient, alice_token: str, bob_token: str
) -> None:
    r = await client.post(
        "/posts",
        json={"title": "Alice Post", "body": "...", "published": True},
        headers=auth(alice_token),
    )
    assert r.status_code == 201
    post_id = r.json()["id"]

    # Bob이 수정 시도 → 403
    r = await client.patch(
        f"/posts/{post_id}",
        json={"title": "hacked"},
        headers=auth(bob_token),
    )
    assert r.status_code == 403

    # Bob이 삭제 시도 → 403
    r = await client.delete(f"/posts/{post_id}", headers=auth(bob_token))
    assert r.status_code == 403

    # 토큰 없이 → 401
    r = await client.delete(f"/posts/{post_id}")
    assert r.status_code == 401


# 5) 게시 상태 토글

async def test_publish_unpublish_toggle(
    client: AsyncClient, alice_token: str
) -> None:
    r = await client.post(
        "/posts",
        json={"title": "Draft", "body": "...", "published": False},
        headers=auth(alice_token),
    )
    assert r.status_code == 201
    post_id = r.json()["id"]
    assert r.json()["published"] is False
    assert r.json()["published_at"] is None

    # publish
    r = await client.post(f"/posts/{post_id}/publish", headers=auth(alice_token))
    assert r.status_code == 200
    assert r.json()["published"] is True
    assert r.json()["published_at"] is not None

    # 비로그인도 볼 수 있다
    r = await client.get(f"/posts/{post_id}")
    assert r.status_code == 200

    # unpublish
    r = await client.post(f"/posts/{post_id}/unpublish", headers=auth(alice_token))
    assert r.status_code == 200
    assert r.json()["published"] is False

    # 다시 비로그인은 못 본다
    r = await client.get(f"/posts/{post_id}")
    assert r.status_code == 404


# 6) 댓글 CRUD

async def test_comment_crud_and_authorization(
    client: AsyncClient, alice_token: str, bob_token: str
) -> None:
    # Alice의 공개 글
    r = await client.post(
        "/posts",
        json={"title": "Open Post", "body": "...", "published": True},
        headers=auth(alice_token),
    )
    post_id = r.json()["id"]

    # Bob이 댓글
    r = await client.post(
        f"/posts/{post_id}/comments",
        json={"body": "good post"},
        headers=auth(bob_token),
    )
    assert r.status_code == 201
    comment_id = r.json()["id"]
    assert r.json()["body"] == "good post"
    assert r.json()["author"]["name"] == "Bob"

    # 댓글 목록 (비로그인도 가능 — 공개 글이므로)
    r = await client.get(f"/posts/{post_id}/comments")
    assert r.status_code == 200
    assert len(r.json()) == 1

    # Alice는 Bob의 댓글을 수정 못 함 → 403
    r = await client.patch(
        f"/comments/{comment_id}",
        json={"body": "hijack"},
        headers=auth(alice_token),
    )
    assert r.status_code == 403

    # Bob은 자기 댓글 수정 가능
    r = await client.patch(
        f"/comments/{comment_id}",
        json={"body": "edited"},
        headers=auth(bob_token),
    )
    assert r.status_code == 200
    assert r.json()["body"] == "edited"

    # Bob이 자기 댓글 삭제
    r = await client.delete(f"/comments/{comment_id}", headers=auth(bob_token))
    assert r.status_code == 204

    # 댓글이 사라짐
    r = await client.get(f"/posts/{post_id}/comments")
    assert r.json() == []


# 7) 태그 자동 생성 + 같은 이름 재사용

async def test_tag_dedup_and_normalization(
    client: AsyncClient, alice_token: str
) -> None:
    # 첫 글 — "Python", "FastAPI" (대문자 포함, 공백 포함)
    r = await client.post(
        "/posts",
        json={
            "title": "First",
            "body": "x",
            "published": True,
            "tags": [" Python ", "FastAPI", "python"],   # 중복 + 대소문자
        },
        headers=auth(alice_token),
    )
    assert r.status_code == 201
    tags1 = {t["name"] for t in r.json()["tags"]}
    assert tags1 == {"python", "fastapi"}     # 모두 소문자, 중복 제거

    # 두 번째 글 — 같은 태그 + 새 태그
    r = await client.post(
        "/posts",
        json={
            "title": "Second",
            "body": "y",
            "published": True,
            "tags": ["python", "mysql"],
        },
        headers=auth(alice_token),
    )
    assert r.status_code == 201

    # 태그 목록 (전역) — 셋 다 한 번씩만 있어야 한다
    r = await client.get("/tags")
    assert r.status_code == 200
    names = {t["name"] for t in r.json()}
    assert names == {"python", "fastapi", "mysql"}


# 8) 태그 교체 (PATCH)

async def test_post_tags_replace(
    client: AsyncClient, alice_token: str
) -> None:
    r = await client.post(
        "/posts",
        json={
            "title": "Replace tags",
            "body": "x",
            "published": True,
            "tags": ["python", "fastapi"],
        },
        headers=auth(alice_token),
    )
    post_id = r.json()["id"]

    # tags=[]로 PATCH → 모든 태그 제거
    r = await client.patch(
        f"/posts/{post_id}",
        json={"tags": []},
        headers=auth(alice_token),
    )
    assert r.status_code == 200
    assert r.json()["tags"] == []

    # 다른 태그로 교체
    r = await client.patch(
        f"/posts/{post_id}",
        json={"tags": ["docker"]},
        headers=auth(alice_token),
    )
    assert r.status_code == 200
    assert {t["name"] for t in r.json()["tags"]} == {"docker"}


# 9) 글 삭제 — 댓글·태그가 같이 사라지는지 (cascade)

async def test_delete_post_cascades_comments_and_tags(
    client: AsyncClient, alice_token: str, bob_token: str
) -> None:
    """본인 글을 지우면 그 글의 댓글·태그 연결이 함께 사라진다.

    이전 라운드에서 발견된 lazy load 버그(post.comments / post.tags 가 비동기
    컨텍스트에서 lazy load → MissingGreenlet)의 회귀 방지를 겸한다.
    """
    # 태그가 붙은 글
    r = await client.post(
        "/posts",
        json={
            "title": "Will be deleted",
            "body": "x",
            "published": True,
            "tags": ["python", "fastapi"],
        },
        headers=auth(alice_token),
    )
    assert r.status_code == 201
    post_id = r.json()["id"]

    # 댓글도 하나 달아 둔다(다른 사용자로)
    r = await client.post(
        f"/posts/{post_id}/comments",
        json={"body": "곧 사라질 댓글"},
        headers=auth(bob_token),
    )
    assert r.status_code == 201

    # 본인이 글 삭제 — 204 + 내부에서 lazy load 가 터지지 않아야 한다
    r = await client.delete(f"/posts/{post_id}", headers=auth(alice_token))
    assert r.status_code == 204

    # 단건 조회 → 404
    r = await client.get(f"/posts/{post_id}")
    assert r.status_code == 404


# 10) 헬스체크

async def test_health(client: AsyncClient) -> None:
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
