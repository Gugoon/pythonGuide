"""파라미터화와 예외 단언 테스트.

- `@pytest.mark.parametrize` 로 한 테스트 함수를 여러 입력으로 반복 실행한다.
- `pytest.raises` 로 "예외가 나는 것이 정상" 인 케이스를 단언한다.
"""

import pytest
from httpx import AsyncClient

from app.main import QuoteCreate


class TestQuoteValidationParametrized:
    """잘못된 입력 여러 개를 표로 만들어 한 번에 검증한다."""

    @pytest.mark.parametrize(
        "payload",
        [
            {},  # 둘 다 누락
            {"text": "본문만 있음"},  # author 누락
            {"author": "저자만 있음"},  # text 누락
            {"text": "", "author": "익명"},  # text 빈 문자열
            {"text": "정상", "author": ""},  # author 빈 문자열
            {"text": "가" * 281, "author": "익명"},  # text 너무 김
        ],
    )
    async def test_잘못된_본문은_모두_422(
        self,
        client: AsyncClient,
        payload: dict,
    ) -> None:
        res = await client.post("/quotes", json=payload)
        assert res.status_code == 422

    @pytest.mark.parametrize(
        ("text", "author"),
        [
            ("짧은 명언", "A"),
            ("가" * 280, "경계값 저자"),  # text 최대 길이 경계
            ("이모지도 된다 🚀", "유니코드"),
        ],
    )
    async def test_경계값_본문은_201(
        self,
        client: AsyncClient,
        text: str,
        author: str,
    ) -> None:
        res = await client.post("/quotes", json={"text": text, "author": author})
        assert res.status_code == 201
        assert res.json()["text"] == text


class TestPydanticRaises:
    """라우터를 거치지 않고 스키마 자체를 직접 검증하며 예외를 단언한다."""

    def test_정상_입력은_검증을_통과한다(self) -> None:
        model = QuoteCreate(text="유효한 본문", author="작가")
        assert model.author == "작가"

    def test_빈_text_는_ValidationError(self) -> None:
        # Pydantic 검증 실패는 ValidationError 를 던진다.
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            QuoteCreate(text="", author="작가")

        # 어느 필드에서 실패했는지까지 확인한다.
        assert exc_info.value.error_count() == 1
        assert exc_info.value.errors()[0]["loc"] == ("text",)
