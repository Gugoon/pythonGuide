"""표준 라이브러리 `logging` 설정.

운영에서 쓸 만한 최소 구성을 한 함수로 모은다.

- **포매터(Formatter)**: 로그 한 줄의 모양. 시각·레벨·로거 이름·요청 ID·메시지를 한 줄에 담는다.
- **핸들러(Handler)**: 로그를 어디로 보낼지. 여기서는 표준 출력(stdout) 하나만 둔다.
- **필터(Filter)**: 모든 로그 레코드에 `request_id` 속성을 주입한다. 이 덕분에
  포맷 문자열에서 `%(request_id)s` 를 쓸 수 있고, 로그와 요청을 상관(correlate)지을 수 있다.

structlog 같은 구조적 로깅 라이브러리는 12장(유틸리티) 12.36 절을 참고하라.
이 장은 "표준 logging 만으로 어디까지 깔끔하게 되는가"에 집중한다.
"""

import logging
import sys

from app.request_context import get_request_id

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s [req=%(request_id)s] %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class RequestIdFilter(logging.Filter):
    """모든 로그 레코드에 현재 요청 ID 를 붙여주는 필터.

    포매터가 `%(request_id)s` 를 쓰려면 모든 레코드에 `request_id` 속성이 있어야 한다.
    이 필터가 레코드마다 그 속성을 채워 넣는다. (요청 밖에서 찍힌 로그는 '-' 가 된다.)
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True  # True 를 돌려줘야 레코드가 통과한다(필터링 탈락이 아님).


def setup_logging(level: int = logging.INFO) -> None:
    """애플리케이션 로깅을 한 번 설정한다.

    앱이 뜰 때 한 번만 부르면 된다. 여러 번 불려도 기존 핸들러를 정리하고
    다시 붙이므로 핸들러가 중복되지 않는다(중복되면 로그가 두 번씩 찍힌다).
    """
    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.setLevel(level)

    # 핸들러 중복 방지: 이미 붙어 있던 것을 떼고 우리 핸들러 하나만 둔다.
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
