"""TestClient로 명언 API를 통합 테스트합니다.

각 테스트가 서로 영향을 주지 않도록 setup_function에서 메모리 저장소를 비웁니다.
"""

from fastapi.testclient import TestClient

from app.main import app
from app.routers import quotes

client = TestClient(app)


def setup_function(function):
    """각 테스트 함수 실행 전에 메모리 저장소를 깨끗이 비웁니다."""
    quotes._QUOTES.clear()
    quotes._NEXT_ID = 1


def test_root():
    """루트 엔드포인트가 200을 돌려준다."""
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "message" in body


def test_create_and_list_quote():
    """명언을 만들고 목록에서 다시 받을 수 있다."""
    # 생성
    response = client.post(
        "/quotes/",
        json={"text": "Stay hungry, stay foolish.", "author": "Steve Jobs"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["author"] == "Steve Jobs"
    assert body["text"] == "Stay hungry, stay foolish."
    assert "created_at" in body

    # 목록
    response = client.get("/quotes/")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 1
    assert items[0]["text"] == "Stay hungry, stay foolish."


def test_get_quote_not_found():
    """없는 quote_id로 조회하면 404 + 메시지가 온다."""
    response = client.get("/quotes/999")
    assert response.status_code == 404
    assert "찾을 수 없습니다" in response.json()["detail"]


def test_create_validation_error_empty_text():
    """빈 text는 검증 실패로 422가 온다."""
    response = client.post(
        "/quotes/",
        json={"text": "", "author": "Anon"},
    )
    assert response.status_code == 422


def test_patch_partial_update():
    """PATCH는 보낸 필드만 갱신한다."""
    # 먼저 하나 만든다
    created = client.post(
        "/quotes/",
        json={"text": "원본 텍스트", "author": "원본 저자"},
    ).json()
    qid = created["id"]

    # 저자만 바꾼다
    response = client.patch(f"/quotes/{qid}", json={"author": "새 저자"})
    assert response.status_code == 200
    body = response.json()
    assert body["author"] == "새 저자"
    assert body["text"] == "원본 텍스트"  # text는 그대로


def test_delete_then_404():
    """삭제 후 다시 조회하면 404가 온다."""
    created = client.post(
        "/quotes/",
        json={"text": "지울 명언", "author": "Anon"},
    ).json()
    qid = created["id"]

    response = client.delete(f"/quotes/{qid}")
    assert response.status_code == 204

    # 다시 조회하면 404
    response = client.get(f"/quotes/{qid}")
    assert response.status_code == 404
