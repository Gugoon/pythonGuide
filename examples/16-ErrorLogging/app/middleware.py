"""요청 ID 미들웨어.

들어오는 모든 요청에 고유 ID 를 하나씩 부여한다.

- 클라이언트가 이미 `X-Request-ID` 헤더를 보냈으면 그 값을 존중한다(분산 추적에서
  여러 서비스가 같은 ID 를 공유하기 위함).
- 없으면 `uuid4` 로 새로 만든다.
- 그 ID 를 컨텍스트(`request_context`)에 심어 로그가 같은 ID 로 찍히게 하고,
- 응답 헤더 `X-Request-ID` 로 되돌려 줘 클라이언트도 자기 요청을 추적할 수 있게 한다.

이 ID 하나로 "이 사용자의 그 요청에서 무슨 로그가 찍혔나"를 한 줄로 묶을 수 있다.
이것을 **로그 상관관계(log correlation)** 라고 부른다.
"""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.request_context import set_request_id

logger = logging.getLogger("app.request")

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIdMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> Response:
        # 1) 클라이언트가 보낸 ID 를 쓰거나, 없으면 새로 만든다.
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming or uuid.uuid4().hex

        # 2) 컨텍스트에 심는다. 이제 이 요청을 처리하는 모든 로그가 이 ID 를 단다.
        set_request_id(request_id)
        # 라우터 등에서 request.state.request_id 로도 꺼내 쓸 수 있게 둔다.
        request.state.request_id = request_id

        logger.info("요청 시작 %s %s", request.method, request.url.path)

        # 3) 다음 단계(다른 미들웨어 → 라우터)를 호출한다.
        #    예외가 나도 응답 헤더에 ID 를 넣어주기 위해 try/finally 로 감쌀 수도 있지만,
        #    예외는 예외 핸들러가 만든 JSONResponse 로 변환되어 이 자리로 돌아오므로
        #    아래 한 줄로 충분하다.
        response = await call_next(request)

        # 4) 응답 헤더에 같은 ID 를 실어 돌려준다.
        response.headers[REQUEST_ID_HEADER] = request_id

        logger.info("요청 종료 -> %s", response.status_code)
        return response
