# 15. 백그라운드 작업 — BackgroundTasks

> **이 챕터의 목표**
> - **응답을 먼저 보내고, 무거운 부수 작업은 그 뒤에서** 실행하는 흐름을 자기 말로 설명할 수 있다.
> - FastAPI의 `BackgroundTasks`를 라우터 파라미터로 받아 `add_task(...)`로 작업을 등록한다.
> - `BackgroundTasks`를 **의존성으로 주입**받아, 라우터마다 반복되는 공통 작업을 한곳에 모은다.
> - 한 요청에 **여러 작업을 등록**하고, 실행 순서를 이해한다.
> - 작업 함수를 안전하게 설계한다 — **예외 처리**(실패해도 다른 작업·요청에 영향 없게)와 **멱등성**(두 번 실행돼도 안전하게).
> - **동기(`def`)와 비동기(`async def`) 작업 함수**의 차이를 안다.
> - `BackgroundTasks`의 **한계**(같은 프로세스·요청 수명에 묶임)를 분명히 이해하고, 무겁거나 재시도가 필요한 일은 Celery·RQ·arq 같은 외부 큐로 넘겨야 한다는 판단 기준을 세운다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터에서 처음 등장하는 용어 대부분은 본문 흐름에서도 한 줄 정의로 함께 풀어 적습니다.

> **소요 시간**: 1.5~2.5시간

> **전제**: 05장(라우팅·요청/응답)과 07장(라우터 분리·`Depends` 의존성)을 읽었다. `@app.post(...)`, Pydantic 요청/응답 스키마, `Depends(...)`의 모양을 한 번씩 만나봤다.

---

## 15.1 왜 백그라운드 작업인가

웹 API를 만들다 보면, "요청을 처리하긴 했는데 **응답과 직접 상관없는 뒷일**이 남는" 경우를 자주 만난다.

- 회원가입을 받았다 → 가입 자체는 끝났는데, **환영 이메일**을 보내야 한다.
- 글을 저장했다 → 저장은 끝났는데, **검색 인덱스를 갱신**해야 한다.
- 파일을 업로드받았다 → 받긴 했는데, **썸네일을 만들어야** 한다.
- 어떤 동작이 일어났다 → 본 처리는 끝났는데, **감사 로그**를 한 줄 남겨야 한다.

이 뒷일들의 공통점은 **"클라이언트는 그 결과를 굳이 기다릴 필요가 없다"** 는 것이다. 가입한 사람은 "가입됐습니다" 라는 응답만 빨리 받으면 충분하다. 환영 이메일이 0.3초 뒤에 가든 2초 뒤에 가든 상관없다.

그런데 이 뒷일을 라우터 안에서 그냥 `await send_email(...)` 처럼 처리하면, **클라이언트가 그 시간만큼 더 기다리게 된다**. 이메일 서버가 느리면 응답도 같이 느려진다. 사용자 입장에서는 "가입 버튼을 눌렀는데 한참 멈춰 있다" 가 된다.

**백그라운드 작업**은 이 문제를 단순하게 푼다.

> **백그라운드 작업이란?** "응답을 먼저 클라이언트에게 돌려보낸 뒤, 그 다음에 실행되는 일" 이다. 클라이언트는 빠르게 응답을 받고, 서버는 그 뒤에서 남은 일을 처리한다.

FastAPI는 이걸 위한 가장 가벼운 도구로 `BackgroundTasks`를 기본 제공한다. 별도 라이브러리도, 별도 서버도 필요 없다.

```python
@app.post("/signup")
async def signup(payload: SignupRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_welcome_email, payload.email)
    return {"status": "registered"}   # ← 이 응답이 먼저 나간다
    # send_welcome_email 은 응답이 전송된 "뒤"에 실행된다
```

이 한 챕터에서 우리는 이 도구를 끝까지 다룬다. 그리고 **이 도구로 충분한 경우와, 더 큰 도구(외부 큐)가 필요한 경우의 경계선**을 분명히 긋는다. 경계선을 아는 것이 이 챕터의 진짜 목표다.

---

## 15.2 실행 순서를 그림으로

가장 헷갈리는 부분이 "그래서 정확히 **언제** 실행되는가" 이다. 시간 순으로 그려 보자.

일반 라우터(백그라운드 없음):

```
클라이언트 ──요청──▶ [ 라우터: 가입 처리 + 이메일 발송(2초) ] ──응답──▶ 클라이언트
                     └──────────── 2초 넘게 기다림 ────────────┘
```

`BackgroundTasks` 사용:

```
클라이언트 ──요청──▶ [ 라우터: 가입 처리 + 작업 등록 ] ──응답──▶ 클라이언트  (빠름)
                                                          │
                                                          ▼
                              [ 백그라운드: 이메일 발송(2초) ]   ← 응답 후 실행
```

핵심은 **"응답이 클라이언트에게 모두 전송된 뒤, 등록된 작업이 실행된다"** 는 점이다. 등록(`add_task`)은 "예약" 일 뿐, 그 자리에서 바로 실행되는 게 아니다.

> **그럼 작업이 실패하면 클라이언트가 알 수 있나?** 알 수 없다. 응답은 이미 나갔기 때문이다. 그래서 백그라운드 작업은 **"실패해도 클라이언트에게 알릴 필요가 없는 일"** 에만 써야 한다. 이 성질이 뒤에서 다룰 "예외 처리"·"한계" 의 출발점이다.

---

## 15.3 첫 번째 예제 — 응답을 먼저, 알림은 나중에

가장 단순한 형태부터 만든다. 회원가입 응답을 즉시 돌려주고, "환영 알림" 을 백그라운드로 기록한다.

이 챕터의 예제는 DB를 쓰지 않는다. 주제가 "백그라운드 작업이 응답 이후에 정말로 실행되는가" 이므로, 가장 단순한 형태인 **프로세스 메모리 안의 리스트**에 기록하고, 조회 엔드포인트로 확인한다. 실무라면 이 자리에 이메일 발송·DB 쓰기가 들어간다.

먼저 작업 함수와 상태를 둘 모듈을 만든다.

```python
# app/state.py — 학습용 인메모리 상태
notifications: list[str] = []


def reset() -> None:
    notifications.clear()
```

```python
# app/tasks.py — 백그라운드에서 실행될 작업 함수
from app import state


def notify_welcome(username: str) -> None:
    """가입 환영 알림을 "기록"한다(실무라면 이메일 발송)."""
    state.notifications.append(f"환영합니다, {username}님!")
```

그리고 라우터.

```python
# app/main.py
from fastapi import BackgroundTasks, FastAPI, status
from pydantic import BaseModel, Field

from app import state, tasks

app = FastAPI()


class SignupRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)


@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    return {"username": payload.username, "status": "registered"}


@app.get("/notifications")
async def list_notifications():
    return {"notifications": list(state.notifications)}
```

여기서 일어나는 일을 한 줄씩 보자.

1. **`background_tasks: BackgroundTasks`** — 라우터 함수의 인자로 이 타입을 적기만 하면, FastAPI가 `BackgroundTasks` 객체를 알아서 주입해 준다. (`Depends`도 필요 없다. 특별 취급되는 타입이다.)
2. **`background_tasks.add_task(tasks.notify_welcome, payload.username)`** — "이 함수를, 이 인자로, 나중에 실행해 줘" 라는 예약이다. 이 줄에서 `notify_welcome`이 바로 실행되지는 **않는다**.
3. **`return {...}`** — 이 응답이 먼저 클라이언트에게 전송된다.
4. **그 뒤** FastAPI가 등록된 `notify_welcome("alice")`를 실행한다. 그래서 `state.notifications`에 메시지가 쌓인다.

> **`add_task`의 인자 전달 방식** : `add_task(함수, 인자1, 인자2, 키워드=값)` 형태다. 함수를 먼저 적고, 그 뒤에 그 함수에 넘길 인자들을 이어 적는다. 함수를 `notify_welcome()` 처럼 **호출해서** 넘기는 게 아니라, `notify_welcome` 이라는 **함수 자체**를 넘긴다는 점을 주의하자. 호출해서 넘기면 그 자리에서 실행돼 버린다.

---

## 15.4 정말 "응답 후" 실행되는지 테스트로 확인

말로만 "응답 후에 실행된다" 고 하면 와닿지 않는다. 테스트로 직접 확인하자. 이 챕터의 테스트 전략 자체가 학습 포인트다.

```python
# tests/conftest.py
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app import state
from app.main import app


@pytest.fixture(autouse=True)
def reset_state():
    """매 테스트 전에 인메모리 상태를 비운다(autouse 라 자동 적용)."""
    state.reset()
    yield
    state.reset()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

```python
# tests/test_background_tasks.py
async def test_가입_후_환영_알림이_백그라운드로_기록된다(client):
    # 가입 요청. 응답을 받은 시점엔 백그라운드 작업이 이미 실행돼 있다.
    res = await client.post("/signup", json={"username": "bob"})
    assert res.status_code == 201

    # 백그라운드 작업의 결과를 조회해서 확인.
    res = await client.get("/notifications")
    notifications = res.json()["notifications"]
    assert len(notifications) == 1
    assert "bob" in notifications[0]
```

### 15.4.1 테스트 타이밍의 핵심 — 왜 이게 통과하는가

여기서 반드시 짚어야 할 미묘한 지점이 있다. 우리는 `POST /signup` 직후에 곧장 `GET /notifications`를 부르는데, **어떻게 그 사이에 백그라운드 작업이 이미 끝나 있을까?**

답은 **httpx의 `ASGITransport`** 에 있다.

> **`ASGITransport`란?** httpx가 요청을 진짜 네트워크가 아니라 ASGI 인터페이스로 앱에 직접 전달하는 방식이다(07·13장에서 통합 테스트에 썼다). 진짜 서버를 띄우지 않으므로 빠르고 격리된다.

ASGI에서 한 요청의 수명은 "응답 본문 전송 → 백그라운드 작업 실행 → 요청 종료" 순서로 끝난다. 그리고 `ASGITransport`는 **이 수명이 모두 끝날 때까지 기다렸다가** `await client.post(...)`의 결과를 돌려준다. 그래서 `await client.post(...)`가 반환된 시점에는 백그라운드 작업까지 이미 완료돼 있다.

정리하면:

```
await client.post("/signup", ...)
   └─ 내부에서: 응답 생성 → 응답 전송 → 백그라운드 작업 실행 → 종료
                                                      ▲
                          여기까지 끝난 뒤에 await 가 반환된다
```

그래서 그 다음 줄에서 `GET /notifications`를 부르면 이미 기록이 쌓여 있는 것이다.

> **실제 운영 서버(uvicorn + 진짜 네트워크)에서도 같나?** 동작의 의미("응답 후 실행")는 같지만, 타이밍은 다르다. 진짜 클라이언트는 응답 본문을 다 받으면 그 자리에서 `await`가 풀려 다음 줄로 갈 수 있고, 그 시점에 서버의 백그라운드 작업은 아직 진행 중일 수 있다. **테스트가 통과한다고 해서 "운영에서도 호출 직후 즉시 끝나 있다" 고 가정하면 안 된다.** 테스트가 깔끔하게 검증되는 건 어디까지나 `ASGITransport`의 in-process 특성 덕분이다.

이 타이밍 차이는 헷갈리기 쉬우니 표로 정리한다.

| | `ASGITransport`(테스트) | 진짜 uvicorn + 네트워크(운영) |
|---|---|---|
| `await client.post(...)` 반환 시점 | 백그라운드 작업까지 **완료됨** | 응답 수신만 완료, 백그라운드는 **진행 중일 수 있음** |
| 검증 방법 | 호출 직후 상태 조회로 OK | 잠깐 대기·폴링하거나 결과 저장소를 확인 |

---

## 15.5 여러 작업을 등록하기

`add_task`는 여러 번 부를 수 있다. 등록한 **순서대로** 실행된다.

```python
@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignupRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    background_tasks.add_task(tasks.record_signup_audit, payload.username)
    background_tasks.add_task(tasks.grant_starter_points, payload.username)
    return {"username": payload.username, "status": "registered"}
```

이 라우터는 가입 응답을 즉시 돌려주고, 그 뒤에 세 작업을 차례로 실행한다.

1. `notify_welcome` — 환영 알림 기록
2. `record_signup_audit` — 감사 로그 한 줄
3. `grant_starter_points` — 가입 보너스 포인트 지급

> **순서가 보장되나?** 그렇다. `BackgroundTasks`는 등록된 작업을 등록 순서대로 **하나씩 순차** 실행한다. 동시에 병렬로 돌리지 않는다. 그래서 "A가 끝난 뒤 B" 같은 순서 의존이 있어도 안전하다. (반대로, 병렬 처리로 빨라지길 기대하면 안 된다.)

테스트로 세 작업이 모두 수행됐는지 본다.

```python
async def test_여러_작업이_모두_실행된다(client):
    await client.post("/signup", json={"username": "dave"})

    notifications = (await client.get("/notifications")).json()["notifications"]
    audit = (await client.get("/audit-log")).json()["entries"]

    assert any("dave" in n for n in notifications)
    assert any(e["username"] == "dave" for e in audit)
    assert state.points["dave"] == 100   # 보너스 포인트도 지급됨
```

---

## 15.6 동기 함수와 비동기 함수 — 둘 다 등록할 수 있다

작업 함수는 `def`(동기)로 짜도 되고 `async def`(비동기)로 짜도 된다. `add_task`는 둘 다 받는다.

```python
# 동기 작업 함수
def notify_welcome(username: str) -> None:
    state.notifications.append(f"환영합니다, {username}님!")


# 비동기 작업 함수
async def record_signup_audit(username: str, *, source: str = "signup") -> None:
    state.audit_log.append({"username": username, "source": source})
```

둘 다 똑같이 등록한다.

```python
background_tasks.add_task(notify_welcome, "alice")           # 동기
background_tasks.add_task(record_signup_audit, "alice")      # 비동기
```

### 15.6.1 그럼 둘 중 무엇을 써야 하나

기준은 **"그 작업 안에서 `await`가 필요한가"** 이다.

- **`await`가 필요하면** (DB 세션 사용, httpx로 외부 API 호출 등) → `async def`로 짠다.
- **`await`가 필요 없으면** (단순 계산, 파일 쓰기, 동기 라이브러리 호출) → `def`로 짜도 된다.

> **동기 함수를 등록하면 이벤트 루프가 막히지 않나?** 안 막힌다. FastAPI(정확히는 Starlette)는 **동기 작업 함수를 스레드풀에서 실행**한다. 그래서 동기 함수 안에서 약간의 블로킹 작업(파일 쓰기 등)을 해도 메인 이벤트 루프를 멈추지 않는다. 반대로 `async def`로 짜 놓고 그 안에서 무거운 동기 CPU 작업을 `await` 없이 돌리면, 그게 오히려 이벤트 루프를 막을 수 있으니 주의하자.

> **그럼 무거운 CPU 작업(이미지 변환 등)은?** 동기 함수로 짜서 스레드풀에 맡기면 이벤트 루프는 안 막힌다. 다만 스레드풀은 크기가 정해져 있어서, 무거운 작업이 많아지면 풀이 금방 가득 찬다. 이 지점이 바로 "외부 큐로 옮길 때" 의 신호다(15.9에서 다룬다).

---

## 15.7 의존성으로 BackgroundTasks 주입받기

라우터가 여러 개로 늘어나면, **"이런 요청에는 항상 이 감사 로그를 남긴다"** 같은 공통 작업이 생긴다. 매 라우터에 똑같은 `add_task` 줄을 복사하는 대신, **의존성** 안에서 등록하면 한곳에 모을 수 있다.

핵심은 **의존성 함수도 `BackgroundTasks`를 주입받을 수 있다**는 점이다. 그리고 한 요청 안에서는 **같은 `BackgroundTasks` 객체가 공유**된다.

```python
from fastapi import BackgroundTasks, Depends


def audit_logger(background_tasks: BackgroundTasks) -> BackgroundTasks:
    """의존성 안에서 공통 작업(감사 로그)을 미리 등록한다."""
    background_tasks.add_task(
        tasks.record_signup_audit, "(dependency)", source="dependency"
    )
    # 같은 객체를 돌려주면, 라우터가 이어서 다른 작업도 등록할 수 있다.
    return background_tasks


@app.post("/signup-via-dependency", status_code=status.HTTP_201_CREATED)
async def signup_via_dependency(
    payload: SignupRequest,
    background_tasks: BackgroundTasks = Depends(audit_logger),
):
    # 의존성이 이미 감사 로그 작업을 등록했고,
    # 여기서 같은 객체에 환영 알림 작업을 이어 등록한다.
    background_tasks.add_task(tasks.notify_welcome, payload.username)
    return {"username": payload.username, "status": "registered"}
```

이 라우터는 두 작업을 실행한다. **의존성이 등록한** 감사 로그와, **라우터가 등록한** 환영 알림이다. 둘 다 같은 `BackgroundTasks` 객체에 쌓였기 때문에 함께 실행된다.

> **왜 이게 가능한가?** FastAPI의 의존성 주입은 "요청 단위" 로 동작한다. 한 요청을 처리하는 동안 `BackgroundTasks`는 하나만 만들어지고, 의존성 함수든 라우터 함수든 그 시그니처에 `BackgroundTasks`를 적으면 **모두 같은 인스턴스**를 받는다. 그래서 의존성에서 등록한 작업과 라우터에서 등록한 작업이 한 묶음으로 실행된다.

테스트:

```python
async def test_의존성에서_등록한_작업과_라우터_작업이_함께_실행된다(client):
    await client.post("/signup-via-dependency", json={"username": "grace"})

    audit = (await client.get("/audit-log")).json()["entries"]
    assert len(audit) == 1
    assert audit[0]["source"] == "dependency"   # 의존성이 등록한 작업

    notifications = (await client.get("/notifications")).json()["notifications"]
    assert any("grace" in n for n in notifications)   # 라우터가 등록한 작업
```

---

## 15.8 작업 함수를 안전하게 설계하기

백그라운드 작업은 **응답이 이미 나간 뒤에 실행**된다. 이 성질 때문에 작업 함수는 일반 함수보다 더 조심해서 설계해야 한다. 두 가지 원칙이 핵심이다.

### 15.8.1 예외 처리 — 실패해도 조용히

응답이 이미 나갔으므로, 작업 함수가 예외를 던져도 **클라이언트는 그 사실을 알 수 없다**. 게다가 문제가 하나 더 있다.

> **작업 하나가 예외를 던지면, 그 뒤에 등록된 다른 작업이 실행되지 않을 수 있다.** `BackgroundTasks`는 작업을 순차 실행하는데, 중간 작업이 예외로 멈추면 그 다음 작업까지 도달하지 못한다.

그래서 **"실패해도 무방한 부수 작업"** 은 함수 안에서 예외를 직접 잡아 로그만 남기고 조용히 끝내는 게 안전하다.

```python
import logging

logger = logging.getLogger("background-tasks")


def risky_side_effect(username: str) -> None:
    """실패할 수 있는 부수 작업(예: 외부 알림 서버 호출)."""
    try:
        # 실무라면 여기서 외부 호출이 일어나고, 실패할 수 있다.
        raise RuntimeError("외부 알림 서버 응답 없음")
    except Exception as exc:   # 부수 작업이라 광범위하게 잡아 삼킨다
        state.failures.append(f"{username}: {exc}")
        logger.warning("side effect failed for %s: %s", username, exc)
```

이렇게 해 두면, 이 작업을 다른 작업보다 **먼저** 등록해도 뒤 작업이 멈추지 않는다.

```python
@app.post("/signup-with-risky-task", status_code=status.HTTP_201_CREATED)
async def signup_with_risky_task(payload, background_tasks):
    background_tasks.add_task(tasks.risky_side_effect, payload.username)  # 먼저
    background_tasks.add_task(tasks.notify_welcome, payload.username)     # 뒤
    return {"username": payload.username, "status": "registered"}
```

테스트로 "앞 작업이 실패해도 뒤 작업은 실행된다" 를 확인한다.

```python
async def test_부수_작업이_실패해도_뒤_작업은_실행된다(client):
    await client.post("/signup-with-risky-task", json={"username": "frank"})

    # 실패는 함수 안에서 삼켜 기록되고,
    assert len(state.failures) == 1
    # 뒤에 등록한 환영 알림은 정상 실행된다.
    notifications = (await client.get("/notifications")).json()["notifications"]
    assert any("frank" in n for n in notifications)
```

> **모든 예외를 다 삼켜도 되나?** 아니다. "이 작업이 실패하면 데이터가 깨진다" 같은 **중요한 작업**이라면 예외를 삼키면 안 된다. 그런 작업은 애초에 백그라운드로 미루지 말고, 응답 전에 처리해 실패 시 4xx/5xx로 알리는 게 맞다. 예외를 삼켜도 되는 건 "실패해도 클라이언트와 무관한 부수 작업" 일 때뿐이다. **로그는 반드시 남기자.** 안 그러면 작업이 조용히 실패한 걸 아무도 모른다.

### 15.8.2 멱등성 — 두 번 실행돼도 안전하게

> **멱등성(idempotency)이란?** "같은 작업을 한 번 실행하든 여러 번 실행하든 결과가 같다" 는 성질이다. 예를 들어 "포인트를 100점으로 **설정**" 은 멱등이지만, "포인트를 100점 **추가**" 는 멱등이 아니다(두 번 하면 200점).

백그라운드 작업은 재시도·중복 등록 등으로 **같은 입력에 두 번 실행될 수 있다**. 그래서 가능하면 멱등하게 설계해 둔다.

```python
def grant_starter_points(username: str, points: int = 100) -> None:
    """가입 보너스 포인트를 1회만 지급한다(멱등)."""
    if username in state.points:
        logger.info("starter points already granted for %s — skip", username)
        return   # 이미 지급했으면 건너뛴다
    state.points[username] = points
```

"이미 처리했으면 건너뛴다" 는 조건 하나가 멱등성을 만든다. 같은 사용자로 두 번 가입 요청이 와도 포인트가 두 배가 되지 않는다.

```python
async def test_같은_사용자_보너스는_한_번만_지급된다(client):
    await client.post("/signup", json={"username": "eve"})
    await client.post("/signup", json={"username": "eve"})

    assert state.points["eve"] == 100   # 두 배가 되지 않는다
```

> **실무에서는 어떻게 멱등성을 보장하나?** 흔한 방법은 (1) DB의 unique 제약으로 중복 INSERT를 막거나, (2) "처리 완료" 플래그를 두고 시작 전에 확인하거나, (3) 요청마다 고유한 **idempotency key**를 받아 이미 처리한 키면 건너뛰는 식이다. 외부 큐(Celery 등)를 쓸 때는 "작업이 최소 한 번 실행됨(at-least-once)" 을 보장하는 대신 중복 실행 가능성이 있어서, 멱등성이 더욱 중요해진다.

---

## 15.9 BackgroundTasks의 한계 — 언제 외부 큐로 넘겨야 하나

여기가 이 챕터에서 **가장 중요한 절**이다. `BackgroundTasks`는 강력하지만, 분명한 한계가 있다. 이 한계를 모르고 무거운 일을 맡기면 운영에서 사고가 난다.

### 15.9.1 같은 프로세스·같은 요청 수명에 묶인다

`BackgroundTasks`로 등록한 작업은 **그 요청을 처리한 바로 그 워커 프로세스 안에서, 응답 직후에** 실행된다. 여기서 세 가지 한계가 따라 나온다.

1. **서버가 죽으면 작업도 사라진다.** 작업이 메모리에만 있으므로, 응답을 보낸 직후 작업 실행 전(또는 도중)에 프로세스가 재시작·크래시되면 그 작업은 **그냥 유실**된다. 어디에도 기록이 남지 않는다.
2. **재시도가 없다.** 작업이 실패해도 자동으로 다시 시도하지 않는다. 직접 try/except로 처리하는 게 전부다.
3. **워커 자원을 같이 쓴다.** 백그라운드 작업은 그 요청을 처리한 워커의 자원(이벤트 루프·스레드풀)을 함께 쓴다. 무거운 작업이 쌓이면 **그 워커가 새 요청을 받는 능력**까지 갉아먹는다.

> **"요청 수명에 묶인다" 를 다시 정리하면** : 작업은 응답 전송이 끝난 직후, 같은 프로세스에서 실행된다. 별도의 영속 큐나 별도 워커가 없다. 그래서 "확실히 실행돼야 하는 일", "오래 걸리는 일", "여러 서버에 분산해야 하는 일" 에는 맞지 않는다.

### 15.9.2 BackgroundTasks가 적합한 경우 / 부적합한 경우

판단 기준을 표로 정리한다.

| 상황 | `BackgroundTasks` | 외부 큐(Celery·RQ·arq) |
|------|:---:|:---:|
| 가볍고 빠른 부수 작업(로그, 짧은 알림) | ✅ 적합 | 과함 |
| 실패해도 무방한 작업 | ✅ 적합 | 가능 |
| 무거운/오래 걸리는 작업(영상 변환, 대량 처리) | ❌ 부적합 | ✅ 적합 |
| 반드시 실행 보장(유실되면 안 됨) | ❌ 부적합 | ✅ 적합 |
| 자동 재시도가 필요 | ❌ 부적합 | ✅ 적합 |
| 정해진 시간에 실행(스케줄링) | ❌ 부적합 | ✅ 적합 |
| 여러 서버/워커로 분산 | ❌ 부적합 | ✅ 적합 |
| 작업 진행 상황·결과 추적 | ❌ 부적합 | ✅ 적합 |

한 줄 기준:

> **"가볍고, 실패해도 괜찮고, 지금 이 프로세스에서 끝내도 되는 일" 이면 `BackgroundTasks`. 그 밖이면 외부 큐.**

### 15.9.3 외부 큐는 어디서 배우나

무거운 작업을 본격적으로 다뤄야 한다면 **외부 작업 큐**로 넘어간다. 큐는 작업을 별도 저장소(보통 Redis)에 영속적으로 쌓아 두고, **별도의 워커 프로세스**가 그걸 꺼내 실행한다. 그래서 서버가 죽어도 작업이 안 사라지고, 재시도·스케줄링·분산이 가능해진다.

대표 도구:

- **arq** — asyncio 친화적이고 가볍다. 새 프로젝트에 권장.
- **Celery** — 가장 큰 생태계. 복잡한 워크플로·스케줄링이 필요할 때.
- **RQ** — Redis 기반의 단순한 큐.

이 도구들의 최신 버전과 사용 예제는 **[12장 유틸리티 및 라이브러리](12-utilities.md)** 에 정리돼 있다(특히 arq·Celery 절). 흐름의 모양만 미리 한 줄로 비유하면:

```
[ FastAPI 라우터 ] ──작업 등록──▶ [ Redis 큐 ] ◀──작업 꺼냄── [ 별도 워커 프로세스 ]
   (응답은 즉시 반환)              (영속 저장)              (서버가 죽어도 살아남음)
```

`BackgroundTasks`의 화살표가 "같은 프로세스 안" 으로 돌아왔던 것과 달리, 외부 큐는 **작업이 프로세스 밖의 저장소로 나간다**. 이 한 가지 차이가 위 표의 모든 차이를 만든다.

---

## 15.10 흔한 실수 / 트러블슈팅

### 15.10.1 `add_task`에 함수를 호출해서 넘김

```python
# ✗ 잘못 — 그 자리에서 실행돼 버린다(반환값을 등록하려는 꼴)
background_tasks.add_task(notify_welcome(username))

# ✓ 올바름 — 함수와 인자를 따로 넘긴다
background_tasks.add_task(notify_welcome, username)
```

`add_task`는 "함수 자체 + 인자들" 을 받는다. 함수를 호출(`()`)해서 넘기면 그 자리에서 실행되고, 그 **반환값**(보통 `None`)이 작업으로 등록되는 이상한 상황이 된다.

### 15.10.2 응답에 작업 결과를 담으려 함

```python
# ✗ 백그라운드 작업의 결과는 응답에 담을 수 없다
result = background_tasks.add_task(...)   # add_task 는 결과를 돌려주지 않는다
```

백그라운드 작업은 **응답 후** 실행되므로, 그 결과를 같은 응답에 담는 것은 원리적으로 불가능하다. 결과가 필요하면 (1) 응답 전에 동기로 처리하거나, (2) 외부 큐 + 결과 저장소를 쓰고 클라이언트가 나중에 폴링하게 한다.

### 15.10.3 테스트에서 "작업이 아직 안 끝났다" 며 실패

`ASGITransport`를 쓰면 `await client.post(...)`가 반환될 때 백그라운드 작업까지 끝나 있다(15.4.1). 그런데도 실패한다면 의심할 곳:

- 작업 함수가 **조용히 예외를 던지고 있다** → 등록한 작업 안에서 예외가 나면 그 작업의 효과가 안 보인다. 함수에 try/except와 로그를 넣어 확인.
- **상태 초기화가 안 됐다** → 인메모리 상태가 이전 테스트에서 누적됐을 수 있다. `reset()`을 autouse fixture로 매 테스트 전에 부르는지 확인(15.4의 conftest).

### 15.10.4 진짜 서버에서 "호출 직후 결과가 없다"

운영(uvicorn + 네트워크)에서는 응답을 받은 직후에 백그라운드 작업이 아직 진행 중일 수 있다(15.4.1 표). 이건 버그가 아니라 정상이다. 결과를 확인해야 하면 잠깐 대기·폴링하거나, 애초에 결과 추적이 필요한 작업이라면 외부 큐로 옮기는 신호로 받아들이자.

### 15.10.5 무거운 작업을 BackgroundTasks에 맡겨 응답이 느려짐(처럼 보임)

`BackgroundTasks` 자체는 응답을 막지 않는다. 다만 무거운 작업이 그 워커의 스레드풀·이벤트 루프를 점유하면, **그 워커가 받는 다음 요청들**이 느려질 수 있다. "응답은 빠른데 서버 전체가 점점 느려진다" 면 작업이 너무 무거운 것이다 → 외부 큐로(15.9).

---

## 15.11 이 챕터 요약

- `BackgroundTasks`는 **응답을 먼저 보내고, 부수 작업을 그 뒤에서** 실행하는 FastAPI 기본 도구다. 별도 라이브러리·서버가 필요 없다.
- 라우터 인자에 `background_tasks: BackgroundTasks`를 적으면 자동 주입된다. `add_task(함수, 인자...)`로 등록하고, 등록은 "예약" 일 뿐 그 자리에서 실행되지 않는다.
- 작업은 **응답 전송이 끝난 뒤** 등록 순서대로 **순차** 실행된다. 테스트에서는 `ASGITransport` 덕분에 `await client.post(...)` 반환 시점에 작업까지 끝나 있어, 호출 직후 상태를 조회해 검증한다(운영의 타이밍과는 다름에 유의).
- 작업 함수는 **동기(`def`)·비동기(`async def`)** 둘 다 등록 가능하다. `await`가 필요하면 `async def`, 아니면 `def`(스레드풀에서 실행되어 이벤트 루프를 막지 않음).
- `BackgroundTasks`는 **의존성으로 주입**받을 수 있고, 한 요청 안에서 같은 객체가 공유되므로 공통 작업을 의존성에 모을 수 있다.
- 작업 함수는 **예외 처리**(부수 작업은 삼키고 로그, 중요 작업은 애초에 백그라운드로 미루지 않기)와 **멱등성**(두 번 실행돼도 안전)을 갖추도록 설계한다.
- **한계가 핵심이다.** `BackgroundTasks`는 같은 프로세스·요청 수명에 묶여서, 서버가 죽으면 유실되고, 재시도·스케줄링·분산이 없다. **무겁거나 반드시 실행돼야 하거나 재시도가 필요한 일은 arq·Celery·RQ 같은 외부 큐로** 넘긴다(→ [12장](12-utilities.md)).

다음 챕터에서는 에러를 일관되게 다루고, 무슨 일이 일어났는지 **로그로 남기는** 방법을 배운다. 백그라운드 작업이 조용히 실패했을 때 그걸 알아채는 것도 결국 로깅의 몫이다.

---

← [14. 파일 업로드](14-file-upload.md) | [README로 돌아가기](../README.md) | 다음 문서로 이동: **[16. 에러 핸들링·로깅 →](16-error-logging.md)**
