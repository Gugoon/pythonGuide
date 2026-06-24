"""외부 의존성을 부르는 함수만 모아 둔 모듈.

이 파일에는 **외부 세계와 통신하는 함수**(환율 API 호출)를 격리해 둔다.
라우터에서 직접 httpx 를 호출하지 않고 이 함수를 거치게 하면, 테스트할 때
이 함수 하나만 가짜로 갈아끼우면(monkeypatch) 진짜 네트워크 없이 라우터 전체를
검증할 수 있다.

핵심 약속:
- 외부 호출의 "입구"는 `fetch_rate` 하나로 좁힌다.
- 라우터(`app/main.py`)는 이 함수만 import 해서 부른다.
"""

import httpx

# 데모용 가짜 환율 API 주소. 실제로 부르지는 않지만(테스트에서 모킹),
# "외부 URL 을 호출한다" 는 의도를 코드에 남겨 둔다.
RATES_API_BASE = "https://api.example.com/rates"

# 외부 호출 타임아웃(초). 외부 API 가 느릴 때 우리 앱이 무한정 매달리지 않도록 둔다.
HTTP_TIMEOUT = 5.0


class RateUnavailableError(Exception):
    """환율 정보를 가져오지 못했을 때 던지는 우리 도메인 예외.

    httpx 의 저수준 예외(`httpx.HTTPError`)를 라우터까지 그대로 흘리지 않고,
    우리 앱이 이해하는 예외 하나로 감싸서 올려보낸다. 라우터는 이 예외만 알면 된다.
    """


async def fetch_rate(code: str) -> float:
    """통화 코드(예: "USD")에 대한 원화 환율을 외부 API 에서 가져온다.

    이 함수가 이 챕터 모킹의 주인공이다. 테스트에서는 `monkeypatch` 로 이 함수를
    통째로 가짜 함수로 바꿔치워, 진짜 네트워크 호출 없이 라우터를 검증한다.

    실패하면 `RateUnavailableError` 로 감싸서 올린다.
    """
    url = f"{RATES_API_BASE}/{code.upper()}"
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as http:
            res = await http.get(url)
            res.raise_for_status()
            data = res.json()
            return float(data["rate"])
    except (httpx.HTTPError, KeyError, ValueError) as exc:
        # 네트워크 오류, 4xx/5xx, 응답 형식 오류를 모두 한 예외로 정규화한다.
        raise RateUnavailableError(str(exc)) from exc
