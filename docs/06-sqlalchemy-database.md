# 06. SQLAlchemy 2.0과 데이터베이스 연동 (SQLite / MySQL / PostgreSQL)

> **이 챕터의 목표**
> - 데이터베이스의 핵심 개념(테이블·행·열·기본 키·외래 키·트랜잭션)을 자기 말로 설명할 수 있다.
> - **ORM**이 무엇이고 왜 직접 SQL을 쓰는 것보다 입문자에게 유리한지 이해한다.
> - **SQLAlchemy 2.0의 비동기 API** (`AsyncEngine`, `AsyncSession`, `select(...)`)로 FastAPI 안에서 데이터를 읽고 쓸 수 있다.
> - SQLAlchemy 2.0의 새 표기법(`Mapped[...]`, `mapped_column(...)`)으로 모델을 선언한다.
> - **Pydantic 스키마**와 **ORM 모델**의 역할을 분리하고 `from_attributes=True`로 연결한다.
> - **Alembic**으로 마이그레이션을 만들고(`autogenerate`) 적용한다(`upgrade head`).
> - 같은 코드를 SQLite ↔ PostgreSQL ↔ MySQL 사이에서 **`DATABASE_URL`만 바꿔** 옮길 수 있다.
> - N+1 문제를 인식하고 `selectinload`로 첫 대응을 할 수 있다.

> **모르는 단어가 나오면** [용어 사전(glossary.md)](glossary.md)을 펼쳐 한두 줄만 읽고 돌아오세요. 이 챕터는 새 용어가 많아서 가장 자주 펼치게 될 챕터입니다.

> **소요 시간**: 4 ~ 6시간 (개념 → 실습 → 마이그레이션 → DB 전환 시도)

> **이 챕터의 위치**: 04장에서 첫 FastAPI 앱을 띄웠고, 05장에서 라우팅과 Pydantic으로 JSON을 주고받는 법을 배웠습니다. 이제 데이터를 **메모리에 두지 않고 디스크의 데이터베이스**에 저장하는 단계입니다. 여기서 만든 토대 위에 07장(Todo CRUD), 08장(인증), 10·11장(종합 예제)이 모두 올라갑니다.

---

## 6.1 왜 데이터베이스가 필요한가

지금까지 우리가 짠 코드는 모두 **메모리**에 데이터를 둔 상태였습니다. 04·05장에서 만든 작은 라우트들은 함수가 끝나면 변수도 사라지고, 서버를 끄면 모든 자료가 증발합니다. 그래도 학습 단계에서는 충분했습니다.

하지만 실제 백엔드는 **요청과 요청 사이에 자료가 살아 있어야** 합니다. 사용자가 회원가입한 정보, 작성한 글, 올린 사진의 위치 — 이 모든 것을 어딘가 안전한 곳에 적어 두고, 다음 요청 때 다시 꺼내야 합니다. 그 "어딘가 안전한 곳"이 바로 **데이터베이스**입니다.

> **데이터베이스(database, DB)란?** 자료를 표(table) 형태로 모아 두고, 빠르게 검색하고 수정할 수 있게 해주는 저장소 프로그램입니다. 우리는 흔히 "DB에 저장한다"는 말을 씁니다.

> **DBMS(Database Management System)란?** 데이터베이스를 다루는 프로그램 본체입니다. **PostgreSQL, MySQL, SQLite** 등이 모두 DBMS입니다. 흔히 "DB"라고 줄여 말하면 둘 중 어느 쪽을 가리키는지 문맥으로 구분합니다.

### 6.1.1 메모리 저장 vs 데이터베이스 저장

| 비교 | 메모리(파이썬 dict / list) | 데이터베이스 |
|------|--------------------------|--------------|
| 서버 재시작 후 | 모두 사라짐 | 그대로 남아 있음 |
| 여러 프로세스가 공유 | 안 됨 | 됨 |
| 검색 속도 | 자료가 적으면 빠름, 많으면 느려짐 | 인덱스로 매우 빠름 |
| 동시 수정 안전성 | 별도 락이 필요 | 트랜잭션으로 안전 |
| 디스크에 저장 | 안 됨 | 기본 |
| 다른 도구로 읽기 | 어려움 | SQL/도구로 누구나 |

서버가 한 번이라도 다시 실행되거나, 여러 사람이 동시에 자료를 만지거나, 자료가 많아지는 순간 **메모리만으로는 더 못 버팁니다.** 그래서 거의 모든 백엔드는 데이터베이스를 끼고 동작합니다.

### 6.1.2 이 가이드가 다루는 DB의 종류

| DBMS | 한 줄 소개 | 이 가이드의 위치 |
|------|----------|------------------|
| **SQLite** | 파일 하나로 동작하는 가벼운 DB | **개발·학습용 기본** — 별도 서버 불필요 |
| **PostgreSQL** | 가장 표준적인 오픈소스 DB | 운영 환경 권장 — 10·11장 배포에서 사용 |
| **MySQL** | 가장 널리 쓰이는 오픈소스 DB | 회사·기존 코드와 통합할 때 사용 |

이 챕터에서는 **SQLite로 시작합니다.** 별도 DB 서버를 깔 필요가 없어서 환경 구축이 가장 빠르고, SQLAlchemy로 작성한 코드는 나중에 **DB URL만 바꾸면 PostgreSQL/MySQL에서도 그대로 동작**합니다. 이 점이 ORM의 가장 큰 실용적 장점입니다.

---

## 6.2 데이터베이스 개념 빠른 복습

여기까지 한 번도 SQL을 본 적 없어도 따라올 수 있도록 핵심 용어만 짧게 정리합니다. 이미 익숙하다면 6.3으로 건너뛰어도 됩니다.

### 6.2.1 테이블·행·열

자료는 **표(table)** 형태로 저장됩니다. 표의 가로줄 한 개가 자료 한 건이고, 세로줄 한 개가 속성 한 가지입니다.

```
┌──────────────────────  todos 테이블  ──────────────────────┐
│  id  │ title          │ is_done │ created_at              │
├──────┼────────────────┼─────────┼─────────────────────────┤
│  1   │ 우유 사기      │ false   │ 2026-04-25 10:00:00      │   ← 행(row) 하나
│  2   │ 빨래 돌리기   │ true    │ 2026-04-25 11:30:00      │
│  3   │ 보고서 쓰기   │ false   │ 2026-04-25 12:00:00      │
└──────┴────────────────┴─────────┴─────────────────────────┘
   ↑          ↑              ↑              ↑
   열(column)이 4개
```

> **테이블(table)이란?** 자료를 표 형태로 모은 단위입니다. 흔히 "엑셀 시트 한 장"으로 비유합니다. 위 예시에서 `todos`는 테이블 이름입니다.

> **행(row, record)이란?** 표의 가로줄 한 개입니다. 자료 한 건을 의미합니다. "1번 할 일"은 한 행입니다.

> **열(column, field)이란?** 표의 세로줄 한 개입니다. 속성 하나를 나타냅니다. `title`, `is_done`은 열입니다. 각 열은 미리 정해진 **타입**(문자열·정수·날짜 등)을 가집니다.

### 6.2.2 기본 키 (Primary Key)

표 안에서 **각 행을 유일하게 가리키는 열**입니다. 보통 `id`라는 이름의 정수 자동 증가 열을 씁니다.

> **기본 키(Primary Key, PK)란?** 행 하나를 다른 행과 구별해 주는 열입니다. 두 행이 같은 PK 값을 가질 수 없습니다(중복 금지). 우리는 보통 정수 `id`를 PK로 두고 1, 2, 3, ... 자동으로 번호를 매깁니다.

PK 덕분에 "3번 todo 가져와", "5번 user 지워"처럼 **하나를 콕 집어 가리킬** 수 있습니다.

### 6.2.3 외래 키 (Foreign Key)

다른 표의 PK를 가리키는 열입니다. 표 사이의 **연결**을 표현합니다.

```
users 테이블                       posts 테이블
┌────┬───────┐                    ┌────┬─────────┬──────────┐
│ id │ email │                    │ id │ title   │ user_id  │
├────┼───────┤                    ├────┼─────────┼──────────┤
│ 1  │ a@... │ ◄──────────────┐  │ 11 │ 첫 글  │   1      │
│ 2  │ b@... │                  │  │ 12 │ 두번째 │   1      │
└────┴───────┘                  │  │ 13 │ 다른 글│   2      │
                                  │  └────┴─────────┴──────────┘
                                  │              ↑
                                  └─── 이 user_id가 외래 키. users.id를 가리킴
```

> **외래 키(Foreign Key, FK)란?** 다른 테이블의 PK를 참조하는 열입니다. "이 글의 작성자(=`user_id`)는 users 테이블의 그 사용자"라는 연결을 표현합니다. DB는 잘못된 FK 값(예: 존재하지 않는 user를 가리키는 값)이 들어오는 것을 자동으로 막을 수 있습니다.

이 챕터의 예제는 표가 하나(Todo)뿐이라 외래 키가 등장하지 않습니다. 11장 Blog API에서 본격적으로 다룹니다.

### 6.2.4 인덱스

자주 검색하는 열에 미리 만들어 두는 "찾아보기" 자료구조입니다.

> **인덱스(index)란?** 책의 색인처럼 "이 값이 어느 행에 있는지"를 미리 정리해 둔 표입니다. `WHERE email = 'a@b.com'` 같은 검색을 매우 빠르게 합니다. 단점은 디스크 공간을 더 쓰고, INSERT/UPDATE 시 인덱스도 함께 갱신해야 해 살짝 느려진다는 점입니다. 자주 검색하는 열에만 만드는 게 원칙입니다.

### 6.2.5 SQL — 데이터베이스에게 말하는 언어

데이터베이스에 "이런 자료를 가져와줘", "이 자료를 새로 넣어줘"라고 지시할 때 쓰는 언어가 **SQL**입니다.

> **SQL(Structured Query Language)이란?** 관계형 DB를 다루는 표준 언어입니다. "구조화된 질의 언어"라는 뜻이고, 보통 "씨퀄" 또는 "에스큐엘"로 읽습니다.

가장 자주 보는 네 가지:

```sql
-- SELECT: 자료 가져오기
SELECT * FROM todos WHERE is_done = false;

-- INSERT: 새 자료 만들기
INSERT INTO todos (title, is_done) VALUES ('우유 사기', false);

-- UPDATE: 자료 수정
UPDATE todos SET is_done = true WHERE id = 1;

-- DELETE: 자료 지우기
DELETE FROM todos WHERE id = 1;
```

이 가이드는 **직접 SQL을 쓰지 않습니다.** 대신 SQLAlchemy(ORM)를 통해 파이썬 코드로 같은 일을 합니다. 다만 ORM이 내부에서 만들어 보내는 SQL이 이런 모양이라는 점은 알고 있어야, 문제가 생겼을 때 디버깅이 가능합니다.

### 6.2.6 트랜잭션

여러 SQL을 **한 묶음으로 실행**하고, 도중에 어느 하나라도 실패하면 전체를 되돌리는 단위입니다.

> **트랜잭션(transaction)이란?** "이 SQL 묶음은 전부 성공하거나 전부 취소되어야 한다"는 안전장치입니다. 송금이 대표적입니다 — A 통장에서 1만원 빼고 B 통장에 1만원 넣는 두 SQL이 둘 다 성공하거나 둘 다 취소되어야지, 한쪽만 성공하면 큰일이 납니다. SQLAlchemy 세션이 트랜잭션을 자동으로 시작/커밋/롤백합니다.

세 가지 핵심 동작:

- **commit** — "여기까지 한 작업을 진짜 디스크에 반영해 줘"
- **rollback** — "지금까지 한 작업을 모두 취소해 줘"
- **자동 시작** — 세션을 만들면 트랜잭션이 자동으로 열립니다

이 챕터에서 우리가 직접 부를 일은 거의 `await session.commit()` 하나뿐입니다. 나머지는 SQLAlchemy/FastAPI가 알아서 합니다.

---

## 6.3 ORM이란 무엇이고 왜 쓰는가

### 6.3.1 정의

> **ORM(Object Relational Mapper)이란?** 데이터베이스의 표(테이블)와 프로그래밍 언어의 객체(클래스)를 자동으로 연결해 주는 도구입니다. SQL을 직접 쓰지 않고도 파이썬 객체를 다루듯 DB를 다룰 수 있습니다.

이름이 어렵게 느껴질 수 있습니다. 풀어 쓰면 다음 비교가 거의 전부입니다.

### 6.3.2 같은 일, 두 가지 방법

"3번 할 일을 가져와서 완료 표시하기"를 두 방식으로 비교해 봅니다.

**SQL을 직접 쓸 때:**

```python
# 1) DB 연결을 가져온다
conn = some_db_lib.connect(url)
cur = conn.cursor()

# 2) SELECT 쿼리를 문자열로 만들어 보낸다
cur.execute("SELECT id, title, is_done FROM todos WHERE id = ?", (3,))
row = cur.fetchone()

if row is None:
    raise HTTPException(404)

# 3) 튜플에서 직접 위치로 값을 꺼낸다 — 어느 위치가 어느 열인지 외워야 함
todo_id, title, is_done = row

# 4) UPDATE 쿼리도 문자열로
cur.execute("UPDATE todos SET is_done = ? WHERE id = ?", (True, 3))
conn.commit()
```

**SQLAlchemy ORM을 쓸 때:**

```python
# 1) 세션 의존성으로 받아오면 됨 (FastAPI가 자동 주입)
todo = await session.get(Todo, 3)

if todo is None:
    raise HTTPException(404)

# 2) 그냥 파이썬 객체의 속성을 바꾼다
todo.is_done = True

# 3) commit만 부르면 ORM이 알아서 UPDATE를 만들어 보낸다
await session.commit()
```

같은 일을 다른 방식으로 표현했을 뿐이지만, 두 번째 코드의 장점이 분명합니다.

### 6.3.3 ORM이 주는 이득

1. **SQL 인젝션 자동 방지** — `WHERE id = ?` 자리에 사용자 입력을 직접 끼워 넣지 않으므로, 악의적인 입력으로 DB를 망가뜨리는 공격을 막아 줍니다.
2. **타입 안전과 자동 완성** — `todo.title`, `todo.is_done`을 IDE가 인식해 자동 완성과 오타 검출을 해 줍니다. SQL 문자열 안의 오타는 IDE가 잡아 주지 않습니다.
3. **DB 종류에 덜 의존적** — SQLite로 짠 ORM 코드는 PostgreSQL/MySQL에서도 거의 그대로 동작합니다. SQL은 종류별로 미묘한 차이(예: `LIMIT` 표기)가 있어 그대로 옮기기 어렵습니다.
4. **모델 = 단일 진실 공급원** — 표 구조를 파이썬 클래스에 한 번만 적으면, 그 정의가 마이그레이션·쿼리·응답 구조에 모두 재사용됩니다.
5. **관계를 객체처럼 다룸** — `user.posts`처럼 자연스러운 표기로 1:N 관계의 자료를 가져올 수 있습니다.

### 6.3.4 ORM의 단점과 현실

ORM은 만능이 아닙니다. 단점도 정직하게 짚고 갑니다.

- **느린 학습** — 새 도구의 API와 약속을 익혀야 합니다. 본 챕터에서 압축해 다룹니다.
- **복잡한 쿼리에서는 SQL이 더 깔끔** — 통계·집계 쿼리(예: 월별 주문 합계, 윈도우 함수)는 SQL이 더 직관적입니다. SQLAlchemy는 필요할 때 raw SQL을 섞어 쓸 수도 있습니다.
- **N+1 문제** — ORM 표기로 무심코 짜면 쿼리가 N+1번 나가는 비효율이 잘 생깁니다(6.16에서 다룸).
- **추상화의 누수** — 결국 어느 시점에는 "ORM이 뒤에서 무슨 SQL을 만드는지" 봐야 합니다. SQLAlchemy는 `echo=True` 옵션으로 SQL을 다 찍어 줍니다.

> **결론**: 입문 단계와 일반 CRUD에서는 ORM이 압도적으로 편하고 안전합니다. 통계 분석이 핵심인 코드만 부분적으로 SQL로 내려가면 됩니다. 이 가이드는 그 입문 단계에 집중합니다.

### 6.3.5 왜 SQLAlchemy인가

파이썬 ORM 후보는 여러 개가 있습니다.

- **SQLAlchemy 2.0** ← 이 가이드의 선택
- **Django ORM** — Django 프레임워크와 묶여 있음. FastAPI와 결합 어려움
- **SQLModel** — FastAPI 저자가 만든 라이브러리. 사실상 SQLAlchemy의 얇은 래퍼
- **Tortoise ORM** — 비동기 전용. 사용자 풀이 작음

이 가이드가 SQLAlchemy 2.0을 못 박은 이유:

1. **가장 널리 쓰이는 파이썬 ORM** — 회사에서 만나는 백엔드 코드의 대다수가 SQLAlchemy를 씁니다.
2. **FastAPI 공식 튜토리얼이 SQLAlchemy 사용** — 표준 경로입니다.
3. **2.0에서 비동기와 타입 표기가 매우 깔끔해짐** — `Mapped[...]` 표기가 IDE의 도움을 가장 많이 받습니다.
4. **Alembic이 거의 표준 마이그레이션 도구** — SQLAlchemy 2.0 + Alembic 한 쌍이 사실상 정답입니다.

---

## 6.4 비동기 ORM과 `AsyncSession`

### 6.4.1 왜 비동기 DB가 중요한가

FastAPI는 비동기(async) 프레임워크라고 1·5장에서 짧게 언급했습니다. 비동기의 가장 큰 효과는 **DB·외부 API처럼 "기다리는" 작업**에서 나타납니다.

> **비동기 I/O란?** "디스크/네트워크 응답이 올 때까지 기다리는 동안, 같은 워커가 다른 요청을 처리할 수 있게 하는" 방식입니다. DB 쿼리가 0.05초 걸린다면, 그 0.05초 동안 다른 요청이 처리됩니다. 동기 방식은 그 시간 동안 멍하니 막혀 있습니다.

```python
# 동기 (옛날 방식)
def get_todos():
    rows = db.execute("SELECT * FROM todos")   # 여기서 실제로 멈춰 기다림
    return rows

# 비동기 (FastAPI + SQLAlchemy 2.0)
async def get_todos(session):
    result = await session.execute(select(Todo))   # 기다리는 동안 다른 요청 처리 가능
    return result.scalars().all()
```

차이는 코드 두 글자(`async`, `await`)뿐이지만, 동시 처리량이 크게 달라집니다. 특히 트래픽이 많은 서비스에서 비용 절감 효과가 큽니다.

### 6.4.2 SQLAlchemy 2.0의 비동기 API

SQLAlchemy 2.0은 다음 한 쌍이 비동기의 핵심입니다.

| 이름 | 역할 |
|------|------|
| **`AsyncEngine`** | DB와의 연결 풀(여러 연결의 묶음). 앱 시작 시 한 개 만들어 두고 끝까지 재사용 |
| **`AsyncSession`** | 한 묶음의 DB 작업(보통 한 요청에 한 개)을 처리하는 객체. 트랜잭션 단위 |

이 두 개의 관계는 다음과 같습니다.

```
   AsyncEngine (연결 풀, 앱 전체에 1개)
        │
        ├── 요청 A → AsyncSession A → 한 트랜잭션
        ├── 요청 B → AsyncSession B → 한 트랜잭션
        ├── 요청 C → AsyncSession C → 한 트랜잭션
        ...
```

**FastAPI 안에서의 흐름**은 이렇게 됩니다.

1. 앱 시작 시: `AsyncEngine`을 한 번 만든다.
2. 요청 들어옴: 의존성 함수 `get_session()`이 새 `AsyncSession`을 만들어 라우트에 주입한다.
3. 라우트가 동작: `await session.execute(...)`, `session.add(...)` 등으로 DB 작업.
4. 라우트 종료: 의존성 함수가 `commit` 또는 `rollback`을 처리하고 세션을 닫는다.

자세한 구현은 6.6에서 코드로 보여 드립니다.

### 6.4.3 비동기 드라이버 — DB 종류별로 별도

SQLAlchemy 2.0의 비동기 API를 쓰려면 DB 종류에 맞는 **비동기 드라이버 라이브러리**도 같이 깔아야 합니다.

> **DB 드라이버(driver)란?** 파이썬 코드와 실제 DB 사이를 통역하는 작은 라이브러리입니다. SQLAlchemy 자체는 "어느 DB든 다룰 수 있는 공통 인터페이스"이고, 실제로 PostgreSQL과 통신하려면 PostgreSQL용 드라이버가 추가로 필요합니다.

이 가이드의 표준은 다음과 같습니다.

| DB | 비동기 드라이버 | 설치 명령 |
|----|------------------|-----------|
| **SQLite** | `aiosqlite` | `uv add aiosqlite` |
| **PostgreSQL** | `asyncpg` | `uv add asyncpg` |
| **MySQL** | `asyncmy` | `uv add asyncmy` |

이 챕터는 SQLite로 시작하므로 `aiosqlite`만 깝니다. 다른 DB로 옮길 때 추가로 깔면 됩니다.

> **왜 같은 DB에 동기/비동기 드라이버가 따로 있나요?** 비동기 함수는 안에서 진짜로 비동기로 동작해야 합니다. 옛날 동기 드라이버를 그대로 쓰면 "기다리는 동안 멈춰 있는" 동기 동작이 되어 비동기의 의미가 사라집니다. 그래서 `aiosqlite`/`asyncpg`/`asyncmy` 같은 비동기 전용 드라이버가 필요합니다.

> **`greenlet` 의존성**: SQLAlchemy 의 async API 는 내부적으로 `greenlet` 라이브러리를 써서 동기/비동기 다리를 놓습니다. `sqlalchemy[asyncio]` extras 로 자동 설치되지만, Alpine 같은 일부 환경에서는 휠이 없어 빌드 도구가 필요할 수 있습니다(`apk add gcc musl-dev`). 컨테이너에서 알 수 없는 빌드 에러가 나면 가장 먼저 의심하세요.

---

## 6.5 SQLAlchemy 2.0의 새 표기법

SQLAlchemy 2.0은 1.x에 비해 모델 정의 표기가 크게 바뀌었습니다. 옛 코드와 새 코드가 인터넷에 섞여 있어 혼란스러울 수 있어, 새 표기법(2.0 스타일)을 짧게 미리 보여드립니다.

### 6.5.1 새 표기법: `Mapped[...]`와 `mapped_column(...)`

```python
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """모든 모델의 부모 클래스."""
    pass

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )
```

각 줄이 무엇을 의미하는지 풀어 봅니다.

- **`__tablename__ = "todos"`** — DB의 테이블 이름. 관례는 복수형 snake_case.
- **`Mapped[int]`** — "이 속성은 파이썬에서 `int` 타입이고, DB의 어떤 정수 열에 매핑된다"는 표시. IDE가 이 정보를 읽고 자동 완성과 타입 검사를 해 줍니다.
- **`mapped_column(...)`** — DB 열의 세부 옵션(타입·길이·기본값·PK 여부 등)을 지정. 인자가 없으면 SQLAlchemy가 `Mapped[...]`의 타입을 보고 적당한 기본값을 씁니다.
- **`primary_key=True`** — 이 열이 PK(기본 키)임을 표시. 정수 PK는 자동 증가가 기본.
- **`String(200)`** — VARCHAR(200) 타입. 길이를 명시하면 DB 측에서 길이 제한을 강제합니다.
- **`default=False`** — 새 행을 만들 때 값이 안 들어오면 이 기본값.

### 6.5.2 옛 표기법(1.x)과의 비교

옛 코드는 이런 식이었습니다.

```python
# 옛날 (SQLAlchemy 1.4 스타일) — 이 가이드는 안 씁니다
from sqlalchemy import Column, Integer, String, Boolean

class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    is_done = Column(Boolean, default=False)
```

옛 표기법은 IDE가 `todo.title`의 타입을 모릅니다(`Column[str]`까지밖에 못 따라감). 새 표기법(`Mapped[str]`)은 IDE가 정확히 `str`로 추론합니다. **새 프로젝트는 항상 2.0 표기법을 쓰세요.**

### 6.5.3 `Mapped[...]`의 흔한 타입

| Mapped 타입 | DB 타입 (기본 매핑) | 설명 |
|-------------|---------------------|------|
| `Mapped[int]` | INTEGER | 정수. PK로 자주 사용 |
| `Mapped[str]` | VARCHAR | 문자열. `String(200)`처럼 길이 지정 권장 |
| `Mapped[bool]` | BOOLEAN | 참/거짓 |
| `Mapped[float]` | FLOAT | 실수 |
| `Mapped[datetime]` | TIMESTAMP / DATETIME | 날짜+시간 |
| `Mapped[date]` | DATE | 날짜만 |
| `Mapped[bytes]` | BLOB / BYTEA | 바이너리 데이터 |
| `Mapped[Optional[str]]` 또는 `Mapped[str \| None]` | NULL 허용 VARCHAR | nullable 열 |

> **NULL 허용을 표기하는 두 방식**: `Mapped[Optional[str]]`(파이썬 3.9 이전 호환)과 `Mapped[str | None]`(파이썬 3.10+). 이 가이드는 3.13을 쓰므로 후자를 권장합니다. 둘 다 동작합니다.

---

## 6.6 `db.py` 작성 — Engine, Session, 의존성

이제 손을 움직입니다. **표준 프로젝트 구조**(README의 약속과 동일)는 다음과 같습니다.

```
06-SQLAlchemyTodo/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .env.example
├── .gitignore
├── README.md
├── alembic.ini
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
└── app/
    ├── __init__.py
    ├── main.py
    ├── config.py
    ├── db.py            ← 이 절에서 만드는 파일
    ├── models.py
    └── schemas.py
```

### 6.6.1 새 프로젝트 만들기

03장에서 익힌 흐름과 같습니다.

```bash
mkdir 06-SQLAlchemyTodo
cd 06-SQLAlchemyTodo

uv init
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite
```

`uv add` 한 줄로 다음이 한꺼번에 들어옵니다.

- **`fastapi`** — 웹 프레임워크 본체
- **`uvicorn[standard]`** — ASGI 서버
- **`sqlalchemy`** — ORM 본체 (2.x를 자동으로 가져옵니다)
- **`alembic`** — 마이그레이션 도구
- **`aiosqlite`** — SQLite용 비동기 드라이버

설치가 끝나면 `app/` 폴더와 빈 `__init__.py`를 만듭니다.

```bash
mkdir -p app
touch app/__init__.py
```

### 6.6.2 `app/config.py` — DATABASE_URL 설정

DB 접속 주소(=`DATABASE_URL`)는 코드에 직접 박지 않고 **환경 변수**로 분리합니다. 환경마다(개발·테스트·운영) 다른 DB를 가리키도록 하기 위함입니다.

> **환경 변수(environment variable)란?** 운영체제가 프로세스에 전달하는 키-값 쌍입니다. 비밀번호·접속 주소처럼 "코드에 박으면 안 되는 값"을 운영체제 쪽에서 주입할 수 있게 합니다. 개발 중에는 `.env` 파일에 적어 두고 라이브러리가 그걸 읽어들입니다.

```python
# app/config.py
import os

# 개발 기본값: 현재 폴더에 todo.db 라는 SQLite 파일을 사용한다.
# 실제 운영에서는 환경 변수 DATABASE_URL 을 PostgreSQL 등의 주소로 바꾼다.
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo.db",
)
```

> **`sqlite+aiosqlite:///./todo.db`의 형식**: `드라이버명+비동기드라이버명:///경로`. 콜론과 슬래시 개수에 주의(`:///`로 슬래시 세 개). `./todo.db`는 "현재 작업 폴더의 todo.db 파일"이라는 뜻입니다. 메모리 SQLite를 쓰려면 `sqlite+aiosqlite:///:memory:`.

다른 DB의 URL 형식도 미리 표로 정리합니다(이 챕터 끝의 6.17에서 다시).

| DB | DATABASE_URL 예시 |
|----|---------------------|
| SQLite (파일) | `sqlite+aiosqlite:///./todo.db` |
| SQLite (메모리, 테스트용) | `sqlite+aiosqlite:///:memory:` |
| PostgreSQL | `postgresql+asyncpg://user:pass@localhost:5432/mydb` |
| MySQL | `mysql+asyncmy://user:pass@localhost:3306/mydb` |

### 6.6.3 `app/db.py` — Engine과 Session 만들기

이 가이드의 가장 중요한 인프라 파일입니다. 한 번 잘 만들어 두면 이후 챕터들이 모두 이걸 그대로 씁니다.

```python
# app/db.py
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    """모든 ORM 모델이 상속할 부모 클래스.

    이 클래스를 상속받은 클래스들이 모이면 SQLAlchemy 가
    "어떤 테이블들이 존재해야 하는가"를 알 수 있게 된다.
    """
    pass


# 1) 비동기 엔진 — 앱 전체에서 한 개만 만든다.
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,           # True 로 두면 모든 SQL 문이 콘솔에 찍힌다(디버깅용)
)

# 2) 세션 팩토리 — 요청마다 새 AsyncSession 을 만들어 주는 함수.
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,   # commit 후에도 객체 속성에 접근 가능하게 한다
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성 함수.

    한 요청마다 한 개의 세션을 만들고, 라우트가 끝나면
    자동으로 commit (성공 시) 또는 rollback (예외 시) 하고 닫는다.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            # 라우트 안에서 예외가 발생하면 트랜잭션을 되돌린다
            await session.rollback()
            raise
        else:
            # 라우트가 정상 종료되면 commit
            await session.commit()
```

각 부분을 풀어 설명합니다.

- **`Base`**: 모든 모델 클래스의 부모. 06.5에서 본 그것입니다. ORM 모델들이 다 이걸 상속합니다.
- **`create_async_engine(DATABASE_URL, ...)`**: 비동기 엔진을 만듭니다.
  - `echo=False`: SQL 로그를 안 찍습니다. 디버깅 시에만 `True`.
- **`async_sessionmaker(bind=engine, ...)`**: "이 엔진에 연결된 세션을 만들어 주는 공장"입니다. 호출하면 새 `AsyncSession`을 반환합니다.
  - `expire_on_commit=False`: commit 후에도 ORM 객체의 속성에 접근할 수 있게 합니다(기본 `True`이면 commit 직후 객체가 "유효 기한 만료" 상태가 되어 다시 로드해야 함). FastAPI에서는 거의 항상 `False`로 둡니다.
  - `autoflush=False`: 자동 flush를 끕니다(취향). 입문 단계에서는 이게 더 이해하기 쉽습니다. **주의**: 같은 세션에서 `session.add(x)` 직후 `select(...).where(...)` 로 `x` 를 못 찾는 경우가 생길 수 있습니다. 그런 흐름이 필요하면 `await session.flush()` 를 명시적으로 호출하세요.
- **`get_session()`**: FastAPI의 **의존성 함수**입니다. `Depends(get_session)`으로 라우트가 받게 됩니다. 한 요청에 한 세션이 만들어지고, 끝나면 자동으로 commit·close 됩니다.

> **`async with SessionLocal() as session:`이란?** 비동기 컨텍스트 매니저입니다. 블록을 벗어나면 자동으로 `await session.close()`가 호출됩니다. 우리는 명시적으로 close를 호출할 필요가 없습니다.

> **`yield session`은 왜 쓰나요?** FastAPI의 의존성 함수에서 `yield`는 "여기까지가 사전 처리, 라우트가 끝나면 다시 돌아오라"는 뜻입니다. 위 코드에서 라우트 함수가 모두 끝난 뒤에야 `else: await session.commit()` 또는 `except`가 실행됩니다.

### 6.6.4 의존성 함수의 동작 흐름 정리

`get_session`이 한 요청 동안 어떤 순서로 도는지 그림으로 정리합니다.

```
요청 들어옴
   │
   ▼
get_session() 호출
   ├─ SessionLocal() 로 새 AsyncSession 생성 (← async with __aenter__)
   ├─ try 블록 진입
   │
   ▼ (yield)  ←── 라우트 함수 실행 (예: create_todo, get_todo, ...)
   │              ─ 라우트가 session.add, session.execute 등을 호출
   │              ─ 라우트가 정상 종료 또는 예외 발생
   ▼
case 정상 종료:  await session.commit()    ← else 블록
case 예외 발생:  await session.rollback()  ← except 블록 + raise
   │
   ▼
async with 블록 종료 (← async with __aexit__)
   └─ session 이 자동으로 close 된다
   │
   ▼
요청 종료
```

이 한 함수만 한 번 잘 짜 두면, 라우트들은 단지 `session: AsyncSession = Depends(get_session)`을 인자로 받기만 하면 끝입니다. **commit이나 rollback을 직접 부를 일이 거의 없어집니다.**

---

## 6.7 모델 정의 — `Todo`

`app/models.py`에 첫 ORM 모델을 만듭니다.

```python
# app/models.py
from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Todo(Base):
    """할 일 한 건을 표현하는 ORM 모델 (todos 테이블에 매핑)."""

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    is_done: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Todo id={self.id} title={self.title!r} is_done={self.is_done}>"
```

> **`server_default=func.now()` 가 왜 같이 있나요?** Python-side `default` 만 두면 ORM 경로(`session.add(...)` → INSERT)에서는 잘 동작하지만, raw SQL 로 INSERT 하거나 마이그레이션 스크립트에서 컬럼이 NOT NULL 일 때 NULL 위반이 날 수 있습니다. `server_default` 로 DB 측 기본값을 둬서 어느 경로로 들어와도 안전. `DateTime(timezone=True)` 는 PostgreSQL/MySQL 에서 timezone-aware 컬럼이 되어 `datetime.now(timezone.utc)` 와 일관됩니다.

설명:

- **`__tablename__ = "todos"`**: DB에 만들어질 테이블 이름.
- **`id`**: PK. `primary_key=True`만 주면 정수 자동 증가가 기본입니다.
- **`title`**: VARCHAR(200). 200자 제한. 200자가 너무 작거나 큰 것 같다면 프로젝트 요구사항에 맞춰 조정.
- **`is_done`**: BOOLEAN. 기본값 `False` — 새로 만든 할 일은 미완료.
- **`created_at`**: 만든 시각. `default=lambda: datetime.now(timezone.utc)`로 자동 채움. **UTC 시각을 저장하는 것이 표준입니다.** 지역 시간대는 응답 시점에 변환합니다.

> **왜 `datetime.utcnow`를 안 쓰나요?** Python 3.12부터 `datetime.utcnow()`는 **deprecated** 입니다(naive datetime을 돌려줘서 timezone 정보가 없습니다). 대신 명시적으로 `datetime.now(timezone.utc)`를 써서 UTC임을 분명히 합니다. `from datetime import datetime, timezone` 한 줄로 둘 다 import 합니다.

> **왜 함수를 호출하지 않고 `lambda`로 감싸 넘기나요?** `default=datetime.now(timezone.utc)`처럼 호출 결과를 넘기면 **모듈이 import되는 시점**의 시간이 박혀버립니다. 우리가 원하는 건 "행이 만들어질 때마다 그때의 시간"이므로, 함수 객체(여기서는 `lambda`)를 넘겨 SQLAlchemy가 INSERT 직전에 호출하도록 합니다.

> **`__repr__`은 꼭 필요하나요?** 디버깅용입니다. `print(todo)` 했을 때 보기 좋게 출력됩니다. 운영에 영향은 없습니다.

### 6.7.1 모델은 어디서 import되어야 하는가

마이그레이션이 모델을 발견하려면 어딘가에서 **이 클래스가 한 번은 import되어야** 합니다. 안 그러면 `Base.metadata`에 등록되지 않아 Alembic이 모릅니다. 이 가이드는 `app/main.py`에서 `from app.models import Todo`로 import하므로 자동으로 등록됩니다.

큰 프로젝트에서는 `app/models/__init__.py`에서 모든 모델을 한꺼번에 import해 두는 패턴이 흔합니다(11장 Blog API에서 다룸).

---

## 6.8 Pydantic 스키마와 ORM 모델의 분리

5장에서 Pydantic으로 요청·응답을 검증하는 법을 배웠습니다. 이제 그 Pydantic 스키마와 6.7에서 만든 ORM 모델을 어떻게 함께 쓸지 정리합니다.

### 6.8.1 왜 두 종류의 클래스가 필요한가

같은 "Todo"를 표현하는 클래스가 두 개 있는 게 처음에는 이상하게 느껴집니다. 이유를 정리합니다.

| | ORM 모델 (`models.py::Todo`) | Pydantic 스키마 (`schemas.py::TodoRead` 등) |
|--|------------------------------|---------------------------------------------|
| 역할 | DB 테이블에 매핑된 객체 | 요청·응답의 JSON 모양 |
| 가지는 정보 | DB의 모든 열 (PK, FK, 내부 플래그까지) | 외부에 보일/받을 필드만 |
| 사용처 | 라우트 안에서 DB 작업 | 라우트의 인자(요청)와 반환값(응답) |
| 변경 영향 | DB 마이그레이션이 따라옴 | 외부 API 호환성에 영향 |

**핵심**: ORM 모델과 외부 API의 모양은 자주 다릅니다. 예를 들어:

- **회원가입 요청**에는 `password`(평문)가 들어 있지만, **DB**에는 `password_hash`만 저장합니다. **응답**에는 어느 쪽도 안 나갑니다.
- **DB**에는 `is_deleted` 같은 내부 플래그가 있을 수 있지만, **외부**에는 노출하지 않습니다.

이 분리 덕분에 DB 구조가 바뀌어도 외부 API 모양은 그대로 유지할 수 있고, 반대로 외부 응답 형태가 변해도 DB는 멀쩡할 수 있습니다.

### 6.8.2 `app/schemas.py` 작성

```python
# app/schemas.py
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """POST /todos 의 요청 본문."""

    title: str = Field(min_length=1, max_length=200)


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 의 요청 본문 — 부분 수정."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_done: bool | None = None


class TodoRead(BaseModel):
    """GET 응답에 사용하는 스키마."""

    id: int
    title: str
    is_done: bool
    created_at: datetime

    # ORM 객체(Todo 인스턴스)에서 직접 값을 읽어들일 수 있게 한다.
    model_config = ConfigDict(from_attributes=True)
```

세 가지 스키마의 역할:

- **`TodoCreate`**: 새 todo를 만들 때의 요청. `title`만 받습니다. `id`나 `created_at`은 서버가 정합니다.
- **`TodoUpdate`**: 부분 수정. 모든 필드가 선택적입니다(둘 다 None이면 아무것도 안 바꾸는 결과).
- **`TodoRead`**: 응답. PK·생성 시각까지 포함합니다.

가장 중요한 한 줄은 **`model_config = ConfigDict(from_attributes=True)`** 입니다.

> **`from_attributes=True`란?** Pydantic이 "이 스키마는 dict뿐 아니라 일반 객체의 속성에서도 값을 읽어 만들 수 있다"는 표시입니다. 우리가 ORM에서 받아온 `Todo` 인스턴스를 그대로 `TodoRead.model_validate(todo)`로 변환하거나, FastAPI의 `response_model=TodoRead`에 그대로 넘길 수 있게 됩니다.

> **옛날 이름은 `orm_mode = True`**: Pydantic v1까지는 같은 옵션이 `class Config: orm_mode = True`였습니다. v2에서 `from_attributes=True`로 이름이 바뀌었습니다. 인터넷의 옛 코드와 비교할 때 헷갈리지 마세요.

### 6.8.3 ORM 객체 → Pydantic 스키마로 변환

라우트가 ORM의 `Todo` 인스턴스를 받아 `TodoRead`로 응답하는 흐름은 두 가지입니다.

**방법 A — `response_model`을 라우트에 지정 (권장)**

```python
@app.get("/todos/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)) -> Todo:
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(404, "Not Found")
    return todo   # FastAPI 가 알아서 TodoRead 로 변환
```

`response_model=TodoRead`만 적어두면, FastAPI는 함수가 어떤 타입을 반환하든 그것을 `TodoRead`로 자동 변환·검증해서 응답합니다. **이 방식이 가장 깔끔하고, 자동 문서에도 잘 반영됩니다.**

**방법 B — 함수 안에서 명시적으로 변환**

```python
@app.get("/todos/{todo_id}")
async def get_todo(todo_id: int, session: AsyncSession = Depends(get_session)) -> TodoRead:
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(404, "Not Found")
    return TodoRead.model_validate(todo)   # 명시적
```

둘 다 동작하지만, 본 가이드는 **방법 A를 표준**으로 합니다.

---

## 6.9 CRUD 구현 — 라우트로 직접

이제 모든 조각이 갖춰졌으니 실제 CRUD 라우트를 만듭니다. **이 챕터까지는 라우터 분리 없이** `app/main.py`에 모든 라우트를 모읍니다(07장에서 라우터 분리 패턴을 다룸).

### 6.9.1 `app/main.py` — 전체 코드

```python
# app/main.py
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

app = FastAPI(title="SQLAlchemy Todo")


@app.get("/health")
async def health() -> dict[str, str]:
    """앱이 살아 있는지 확인하는 헬스체크."""
    return {"status": "ok"}


@app.post(
    "/todos",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """새 할 일 한 건을 만든다."""
    todo = Todo(title=payload.title)
    session.add(todo)
    # commit 은 get_session 의존성이 라우트 종료 후 알아서 한다.
    # flush 만 해 두면 id, created_at 같은 자동 생성 값이 todo 객체에 채워진다.
    await session.flush()
    await session.refresh(todo)
    return todo


@app.get("/todos", response_model=list[TodoRead])
async def list_todos(
    session: AsyncSession = Depends(get_session),
) -> list[Todo]:
    """전체 할 일 목록을 최신순으로 돌려준다."""
    stmt = select(Todo).order_by(Todo.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


@app.get("/todos/{todo_id}", response_model=TodoRead)
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """id 로 할 일 한 건 조회. 없으면 404."""
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    return todo


@app.patch("/todos/{todo_id}", response_model=TodoRead)
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """할 일을 부분 수정한다.

    payload 에 들어 있는 필드만 갱신하고, 나머지는 그대로 둔다.
    """
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    # exclude_unset=True : 클라이언트가 명시적으로 보낸 필드만 가져온다.
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(todo, key, value)

    await session.flush()
    await session.refresh(todo)
    return todo


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """할 일을 영구 삭제한다."""
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    await session.delete(todo)
    # 커밋은 get_session 이 알아서 한다
    return None
```

여섯 개의 라우트를 표로 다시 정리합니다.

| HTTP | 경로 | 함수 | 역할 |
|------|------|------|------|
| GET | `/health` | `health` | 헬스 체크 |
| POST | `/todos` | `create_todo` | 새 todo 만들기 |
| GET | `/todos` | `list_todos` | 전체 목록 |
| GET | `/todos/{id}` | `get_todo` | 한 건 조회 |
| PATCH | `/todos/{id}` | `update_todo` | 부분 수정 |
| DELETE | `/todos/{id}` | `delete_todo` | 삭제 |

### 6.9.2 라우트 한 줄 한 줄 풀어보기 — INSERT

POST `/todos`의 흐름을 자세히 봅니다.

```python
todo = Todo(title=payload.title)   # 1) 파이썬 객체 생성. 아직 DB에 안 들어감
session.add(todo)                  # 2) "이 객체를 INSERT 대기열에 넣어"
await session.flush()              # 3) 대기 중인 작업을 DB로 보냄(트랜잭션은 아직 안 닫힘)
await session.refresh(todo)        # 4) DB가 정한 id, created_at 값을 todo에 다시 가져옴
return todo                        # 5) 함수 종료
                                   # 6) get_session 의존성이 commit
```

> **`add`와 `commit`의 차이**: `add`는 메모리상 세션의 "대기열"에만 추가하는 것이고, 실제로 DB에 INSERT가 나가는 것은 `flush`(또는 `commit`이 자동으로 부르는 flush)입니다. `commit`은 "지금까지 한 작업을 트랜잭션째 디스크에 영구 반영하라"는 더 강한 동작입니다.

> **`flush`와 `refresh`가 왜 둘 다 필요?** `flush`만 하면 INSERT는 나가지만, DB가 자동 생성한 값(예: 자동 증가 id, default로 들어간 created_at)이 우리 손에 든 `todo` 인스턴스에는 반영되지 않을 수도 있습니다. `refresh`는 "DB에 가서 이 행의 값들을 다시 읽어와 인스턴스를 갱신하라"는 의미입니다. 이 한 줄을 빼면 응답 JSON의 `id`가 `null`로 나가는 상황이 생길 수 있습니다.

### 6.9.3 SELECT — `select()`와 `session.execute()`

목록 조회를 봅니다.

```python
stmt = select(Todo).order_by(Todo.created_at.desc())
result = await session.execute(stmt)
return list(result.scalars().all())
```

- **`select(Todo)`**: SQL의 `SELECT * FROM todos`에 해당하는 SQLAlchemy 표현입니다. SQLAlchemy 2.0의 표준 표기법.
- **`.order_by(Todo.created_at.desc())`**: 정렬. `desc()`는 내림차순.
- **`await session.execute(stmt)`**: 만든 SELECT 문을 실제로 실행합니다. 비동기이므로 `await`.
- **`result.scalars()`**: `execute`의 반환값은 행 단위의 결과인데, 우리는 단일 모델(Todo) 객체로 받고 싶으므로 `scalars()`로 변환합니다.
- **`.all()`**: 전부를 리스트로. (한 건만 원하면 `.first()`, `.one()`, `.one_or_none()`)

> **`scalars()`는 왜 필요한가?** `session.execute(select(Todo))`의 반환은 "각 행이 한 칸짜리 튜플인 결과 집합"입니다(`(<Todo>,)`, `(<Todo>,)`, ...). 우리는 그 첫 칸만 원하므로 `scalars()`로 풀어 평평한 모양(`<Todo>`, `<Todo>`, ...)으로 만듭니다.

### 6.9.4 단건 조회 — `session.get()` 단축

`session.get(Todo, todo_id)` 한 줄로 PK 조회를 끝낼 수 있습니다. 같은 일을 풀어 쓰면 다음과 같습니다.

```python
# 같은 일, 풀어 쓴 버전
stmt = select(Todo).where(Todo.id == todo_id)
result = await session.execute(stmt)
todo = result.scalars().one_or_none()
```

`session.get(Model, pk)`는 캐시까지 활용하므로 **PK 조회는 항상 `get`을 우선 고려**하세요.

### 6.9.5 UPDATE — 객체 속성 변경 + 자동 UPDATE

UPDATE 라우트의 핵심은 다음 패턴입니다.

```python
todo = await session.get(Todo, todo_id)
data = payload.model_dump(exclude_unset=True)
for key, value in data.items():
    setattr(todo, key, value)
await session.flush()
```

- 가져온 ORM 객체의 속성을 그냥 파이썬 코드로 바꾸기만 하면 됩니다.
- `flush`(또는 `commit`) 시점에 SQLAlchemy가 "이 객체가 어떤 속성이 바뀌었는지" 추적해 둔 정보를 바탕으로 UPDATE 문을 만들어 보냅니다.
- **변경한 속성이 하나도 없으면 UPDATE 자체가 안 나갑니다.**

> **`exclude_unset=True`의 의미**: 클라이언트가 PATCH 요청에서 명시적으로 보낸 필드만 dict에 담습니다. `title`만 보낸 요청이면 `is_done`은 dict에 안 들어옵니다. 만약 `True`로 안 두면 보내지 않은 필드가 모두 `None`으로 들어와 멀쩡한 데이터를 NULL로 덮어쓸 수 있습니다.

### 6.9.6 DELETE — `await session.delete(obj)`

```python
todo = await session.get(Todo, todo_id)
await session.delete(todo)
```

`session.delete(obj)`는 "다음 flush 때 이 행을 DELETE해 달라"는 표시입니다. 실제 DELETE는 flush/commit 시 나갑니다.

이 챕터는 **하드 삭제(hard delete)**만 다룹니다. 즉, 행 자체를 지웁니다. 일부 서비스는 `is_deleted` 플래그만 켜는 **소프트 삭제(soft delete)**를 쓰는데, 11장에서 다룹니다.

### 6.9.7 응답 코드 정리

본 라우트들이 돌려주는 HTTP 상태 코드는 다음과 같습니다.

| 라우트 | 정상 상태 코드 | 비정상 |
|--------|----------------|--------|
| POST `/todos` | **201 Created** | 422 (검증 실패) |
| GET `/todos` | 200 | (드뭄) |
| GET `/todos/{id}` | 200 | 404 |
| PATCH `/todos/{id}` | 200 | 404, 422 |
| DELETE `/todos/{id}` | **204 No Content** | 404 |

> **204 No Content란?** "잘 처리됐고 응답 본문은 없다"는 의미. DELETE의 표준 성공 코드입니다. 본 코드에서 `status_code=status.HTTP_204_NO_CONTENT`로 지정하고 함수가 `None`을 반환하게 했습니다.

---

## 6.10 트랜잭션과 세션 라이프사이클

이 챕터에서 트랜잭션은 6.6의 `get_session` 의존성이 거의 모든 일을 알아서 합니다. 하지만 안에서 무슨 일이 벌어지는지 짧게 점검하고 갑니다.

### 6.10.1 한 요청 = 한 트랜잭션

```
요청 시작
  └─ AsyncSession 생성
       └─ 트랜잭션 시작 (자동)
             ├─ session.add / select / delete ...
             ├─ ...
             ├─ ...
             └─ (라우트 종료)
       ├─ 정상: commit
       └─ 예외: rollback
  └─ AsyncSession close
요청 끝
```

이 한 단위가 우리의 표준입니다. **두 라우트 호출이 같은 트랜잭션을 공유하지 않습니다.** 한 요청 안에서 일어난 일들만 하나의 트랜잭션으로 묶입니다.

### 6.10.2 commit을 직접 부르고 싶을 때

대부분의 경우 의존성이 commit을 처리하므로 라우트 안에서 `await session.commit()`을 직접 부를 일이 없습니다. 다만 한 라우트 안에서 **여러 번 commit을 나누고 싶을 때**(예: 큰 배치 작업)는 직접 호출할 수 있습니다.

```python
for chunk in chunks_of_data:
    for item in chunk:
        session.add(Item(...))
    await session.commit()   # 청크 단위로 끊어서 커밋
```

이런 시나리오는 일반 CRUD에서는 잘 안 나옵니다. 본 챕터에서는 **무시하고, commit은 의존성에 맡깁니다.**

### 6.10.3 예외와 자동 rollback

라우트 안에서 `HTTPException`이나 다른 예외가 발생하면, 6.6의 `get_session`은 `except Exception:` 블록에서 `await session.rollback()`을 부른 뒤 예외를 다시 던집니다. 그래서 **DB가 어중간한 상태로 남는 일이 없습니다.**

### 6.10.4 세션의 수명: "요청 1개 = 세션 1개"

이 약속을 어기면 흔한 버그가 생깁니다. 이 챕터의 코드 예시는 모두 그 약속을 지키게 짜여 있고, 7장 이후 라우터 분리 패턴에서도 같은 약속이 유지됩니다.

> **세션을 라우트 함수 밖에 전역 변수로 두지 마세요.** 동시 요청들이 같은 세션을 건드리면 트랜잭션이 엉키고 알 수 없는 에러가 납니다. 항상 의존성으로 받아 함수 안에서만 씁니다.

---

## 6.11 마이그레이션이란 — 그리고 왜 필요한가

### 6.11.1 코드와 DB는 동시에 진화한다

새 기능을 추가하면 보통 이런 일이 함께 일어납니다.

1. ORM 모델에 새 필드를 추가했다 (`models.py`).
2. **DB 테이블에도 그 새 열이 생겨야 한다.**
3. 코드는 이미 그 새 열을 읽고 쓰는데, DB에 열이 없으면 런타임 에러.

이 "DB 구조 변경"을 **마이그레이션**이라고 부릅니다. 그냥 즉석에서 SQL로 ALTER TABLE을 날려도 동작은 합니다. 하지만 다음 문제가 생깁니다.

- **팀원이 한 일을 알 수 없다.** "어제 어떤 ALTER를 날렸지?" 기억이 안 나면 끝납니다.
- **다른 환경에 다시 적용할 수 없다.** 운영, 스테이징, 다른 개발자의 로컬 DB에 같은 변경이 똑같이 들어가야 하는데, 즉석 SQL은 재현이 어렵습니다.
- **롤백이 어렵다.** 잘못 날린 ALTER를 되돌리려면 그 반대 SQL을 직접 짜야 합니다.

마이그레이션 도구(=Alembic)는 이 문제를 다음으로 해결합니다.

- **각 변경을 파일 한 개로 기록**(`versions/abc123_add_email.py`).
- **순서대로 적용/되돌림 가능** (`upgrade head`, `downgrade -1`).
- **모델 변경을 자동으로 비교해 변경 파일 초안을 생성**(`autogenerate`).

> **마이그레이션(migration)이란?** DB의 스키마(표 구조) 변경을 코드 파일로 기록·실행하는 작업입니다. 변경 이력이 git에 함께 들어가, 어느 시점·어느 환경의 DB든 같은 순서로 같은 구조에 도달할 수 있습니다.

### 6.11.2 Alembic — SQLAlchemy의 짝 도구

> **Alembic이란?** SQLAlchemy의 작성자가 같이 만든 마이그레이션 도구입니다. SQLAlchemy 모델을 읽어 DB와 비교한 뒤 차이를 파일로 만들어 줍니다(`autogenerate`). 그리고 그 파일을 적용·되돌릴 수 있는 CLI를 제공합니다.

Alembic의 핵심 명령은 세 개뿐입니다.

| 명령 | 용도 |
|------|------|
| `alembic init alembic` | 처음 한 번 — Alembic 폴더 골격 생성 |
| `alembic revision --autogenerate -m "..."` | 새 마이그레이션 파일 만들기 |
| `alembic upgrade head` | 미적용 마이그레이션을 모두 적용 |

> **head 란?** "최신 마이그레이션"을 가리키는 별칭입니다. 마이그레이션 파일들이 사슬처럼 이어진 그래프의 끝입니다. `upgrade head`는 "끝까지 다 적용해라"는 뜻.

추가로 자주 쓰는 명령:

| 명령 | 용도 |
|------|------|
| `alembic downgrade -1` | 가장 최근 한 단계만 되돌림 |
| `alembic downgrade base` | 모든 마이그레이션을 되돌림(빈 상태로) |
| `alembic history` | 마이그레이션 그래프를 보여줌 |
| `alembic current` | 지금 DB가 어느 마이그레이션까지 적용됐는지 |

---

## 6.12 Alembic 설치와 초기화

### 6.12.1 Alembic 설치 (이미 완료)

6.6.1에서 `uv add ... alembic`으로 함께 깔았습니다. 다음 한 줄로 확인.

```bash
uv run alembic --version
```

`alembic 1.x.x` 같은 출력이 나오면 OK.

### 6.12.2 폴더 골격 생성

프로젝트 루트(`pyproject.toml`이 있는 폴더)에서 한 번만 실행합니다.

```bash
uv run alembic init alembic
```

> **`alembic init alembic`의 두 번째 `alembic`은?** "마이그레이션 폴더의 이름"입니다. 관례적으로 `alembic`이라는 이름을 쓰지만, `migrations`, `db/migrations` 등으로 바꿔도 됩니다. 이 가이드는 표준대로 `alembic`을 씁니다.

실행 후 폴더 구조가 다음처럼 됩니다.

```
06-SQLAlchemyTodo/
├── alembic.ini              ← 새로 생김 (Alembic 전체 설정)
├── alembic/
│   ├── env.py               ← 새로 생김 (실행 시 호출되는 스크립트)
│   ├── script.py.mako       ← 새로 생김 (revision 파일 템플릿)
│   ├── README
│   └── versions/            ← 새로 생김 (마이그레이션 파일이 들어갈 폴더)
└── ...
```

각 파일의 역할:

- **`alembic.ini`** — Alembic의 메인 설정 파일. DB URL, 로깅, 스크립트 경로 등.
- **`alembic/env.py`** — 마이그레이션 명령이 실행될 때 호출되는 부트스트랩 코드. **여기를 우리 프로젝트에 맞게 수정해야 합니다.**
- **`alembic/script.py.mako`** — `alembic revision`으로 새 파일을 만들 때 쓰는 템플릿.
- **`alembic/versions/`** — 실제 마이그레이션 파일들이 들어갈 폴더. 처음에는 비어 있습니다.

### 6.12.3 `alembic.ini` 살짝 수정

`alembic.ini`를 열고 `sqlalchemy.url` 줄을 찾으면 다음처럼 들어 있을 겁니다.

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

이 줄을 **비워 두거나 그대로 둡니다.** 우리는 `env.py`에서 `DATABASE_URL`을 읽어서 덮어쓸 것이므로 여기 값은 무시됩니다.

```ini
sqlalchemy.url =
```

> **왜 ini 파일에 박아두지 않나요?** 환경별로 DB가 다를 수 있고(개발 SQLite, 운영 Postgres), `.env` 파일을 통해 주입하는 흐름이 더 안전합니다. ini 파일에 비밀번호를 박으면 git에 노출됩니다.

### 6.12.4 `alembic/env.py`를 비동기용으로 수정

이 부분이 본 챕터에서 가장 까다로운 한 단계입니다. Alembic은 기본적으로 동기 SQL 실행을 가정하고 만들어졌습니다. 우리 프로젝트는 **비동기 엔진(`AsyncEngine`)**을 쓰므로 약간의 수정이 필요합니다.

`alembic/env.py`를 통째로 다음 내용으로 교체합니다.

```python
# alembic/env.py
"""Alembic 환경 — 비동기 엔진(AsyncEngine)으로 마이그레이션을 실행한다."""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ─────────────────────────────────────────────────────────
# 우리 앱(app/) 을 import 가능하게 하기 위한 sys.path 보정.
# alembic/ 폴더가 프로젝트 루트의 자식이라는 전제.
# 이 줄이 없으면 일부 실행 환경에서 `ModuleNotFoundError: app` 가 납니다.
# ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import DATABASE_URL  # noqa: E402
from app.db import Base  # noqa: E402
from app import models  # noqa: E402, F401  - Base.metadata 에 모델이 등록되도록 import

# Alembic Config 객체
config = context.config

# alembic.ini 의 sqlalchemy.url 을 우리의 DATABASE_URL 로 덮어쓴다
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 가 비교할 메타데이터 (= 우리의 Base.metadata)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드 — 실제 DB 에 연결하지 않고 SQL 문만 출력."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """실제 마이그레이션 실행 본체. 동기 connection 위에서 돈다."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,            # 열의 타입 변경도 감지
        render_as_batch=True,         # SQLite 의 ALTER TABLE 제약을 우회
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진을 만들고 동기 컨텍스트로 변환해 마이그레이션을 실행."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드 — 실제 DB 에 연결해 마이그레이션 실행."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

핵심 포인트만 짚습니다.

- **`from app.config import DATABASE_URL`, `from app.db import Base`**: 우리가 만든 설정과 베이스 클래스를 그대로 가져옵니다.
- **`from app import models`**: 모델을 import해야 `Base.metadata`에 등록됩니다. **이 한 줄을 빼면 autogenerate가 빈 마이그레이션을 만듭니다.**
- **`config.set_main_option("sqlalchemy.url", DATABASE_URL)`**: ini 파일의 URL을 우리의 환경 변수로 덮어씁니다.
- **`async_engine_from_config(...)`**: 비동기 엔진을 만듭니다. `poolclass=pool.NullPool`은 마이그레이션은 일회성이라 풀이 필요 없어서 끄는 옵션.
- **`await connection.run_sync(do_run_migrations)`**: Alembic 본체는 동기 함수만 받으므로, 비동기 connection 안에서 동기 함수를 실행시키는 다리 역할입니다.
- **`compare_type=True`**: autogenerate가 열의 타입 변경(예: VARCHAR(100)→VARCHAR(200))도 감지하게 합니다.
- **`render_as_batch=True`**: SQLite 가 일부 `ALTER TABLE` 형식만 지원하므로 batch 모드를 켜둡니다. 이 옵션이 있어야 컬럼 변경 같은 마이그레이션이 SQLite 에서도 호환되게 처리됩니다(다른 DB 에는 영향 없음).

> **이 한 파일이 이 챕터에서 가장 손이 많이 가는 부분입니다.** 하지만 한 번 만들어 두면 이후 챕터에서 그대로 재사용합니다. 사실상 "FastAPI + SQLAlchemy async + Alembic" 표준 템플릿입니다.

---

## 6.13 첫 마이그레이션 — `autogenerate`와 `upgrade head`

### 6.13.1 새 마이그레이션 파일 만들기

이제 `app/models.py`의 `Todo` 모델을 보고 마이그레이션 파일을 자동 생성합니다.

```bash
uv run alembic revision --autogenerate -m "create todos table"
```

성공하면 다음 비슷한 출력이 나옵니다.

```
INFO  [alembic.autogenerate.compare] Detected added table 'todos'
  Generating .../alembic/versions/xxxxxxxxxxxx_create_todos_table.py ...  done
```

`alembic/versions/` 안에 파일이 한 개 생겼습니다. 열어보면 다음과 같은 내용입니다(파일명의 해시는 매번 다름).

```python
"""create todos table

Revision ID: 1234567890ab
Revises:
Create Date: 2026-04-25 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1234567890ab"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("is_done", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("todos")
```

각 부분:

- **`upgrade()`**: 적용할 변경. "todos 테이블을 만들어라."
- **`downgrade()`**: 되돌릴 때 할 변경. "todos 테이블을 지워라."
- **`revision`, `down_revision`**: 마이그레이션 사슬의 ID. `down_revision = None`이면 첫 번째라는 뜻.

> **autogenerate가 자동으로 만들어 준 파일은 항상 한 번 읽어보세요.** 100% 정확하지 않습니다. 인덱스, 제약조건 이름, 데이터 마이그레이션(예: 기존 행을 변환) 같은 부분은 손으로 보강해야 할 때가 있습니다. 하지만 본 챕터처럼 단순한 표 한 개 추가는 거의 항상 그대로 동작합니다.

### 6.13.2 마이그레이션 적용

```bash
uv run alembic upgrade head
```

성공 출력:

```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 1234567890ab, create todos table
```

이제 프로젝트 루트에 **`todo.db`라는 SQLite 파일**이 새로 생겼습니다. 그 안에 `todos` 테이블과 Alembic이 자기가 쓰는 `alembic_version` 테이블이 들어 있습니다.

### 6.13.3 적용 확인 — `sqlite3`로 들여다보기

`sqlite3` CLI가 깔려 있으면 다음으로 들어가 봅니다.

```bash
sqlite3 todo.db
```

```
sqlite> .tables
alembic_version  todos

sqlite> .schema todos
CREATE TABLE todos (
        id INTEGER NOT NULL,
        title VARCHAR(200) NOT NULL,
        is_done BOOLEAN NOT NULL,
        created_at DATETIME NOT NULL,
        PRIMARY KEY (id)
);

sqlite> select * from alembic_version;
1234567890ab

sqlite> .quit
```

`alembic_version` 테이블이 우리 DB가 어느 마이그레이션까지 적용됐는지 기억합니다. **이 테이블을 함부로 지우거나 손대지 마세요.**

### 6.13.4 두 번째 마이그레이션을 만드는 흐름 (예시)

만약 나중에 `Todo` 모델에 `priority: Mapped[int] = mapped_column(default=0)`라는 새 열을 추가했다면, 같은 명령을 다시 부르기만 하면 됩니다.

```bash
# 1) models.py 에 priority 추가
# 2) 새 마이그레이션 파일 자동 생성
uv run alembic revision --autogenerate -m "add priority to todos"

# 3) 적용
uv run alembic upgrade head
```

Alembic은 두 번째 파일에서 `down_revision = "1234567890ab"`(첫 번째의 ID)를 자동으로 채워 사슬을 잇습니다.

### 6.13.5 되돌리기

```bash
uv run alembic downgrade -1     # 가장 최근 한 단계 되돌림
uv run alembic downgrade base   # 모든 마이그레이션 되돌림
uv run alembic upgrade head     # 다시 끝까지
```

개발 중에 마이그레이션을 잘못 만들었으면 `downgrade -1`로 되돌리고, 파일을 수정한 뒤 `upgrade head`로 다시 적용합니다.

> **운영 환경에서 downgrade는 신중하게**: 한 번 운영에 적용된 마이그레이션은 데이터 손실이 따를 수 있으므로 함부로 되돌리지 않습니다. 본 가이드는 개발 중 흐름만 다룹니다.

---

## 6.14 실행하기 — 서버를 띄우고 curl로 검증

### 6.14.1 서버 띄우기

```bash
uv run uvicorn app.main:app --reload
```

다음 비슷한 로그가 나오면 성공.

```
INFO:     Will watch for changes in these directories: ['...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

브라우저에서 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)를 열면 Swagger UI가 자동 생성된 모습이 보입니다.

### 6.14.2 curl로 CRUD 한 바퀴 돌리기

다른 터미널에서 다음을 차례대로 실행해 봅니다.

```bash
# 1) 헬스 체크
curl -s http://127.0.0.1:8000/health
# {"status":"ok"}

# 2) 새 todo 만들기
curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"우유 사기"}'
# {"id":1,"title":"우유 사기","is_done":false,"created_at":"2026-04-25T..."}

curl -s -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":"빨래 돌리기"}'

# 3) 목록 조회
curl -s http://127.0.0.1:8000/todos
# [{"id":2,...},{"id":1,...}]

# 4) 한 건 조회
curl -s http://127.0.0.1:8000/todos/1
# {"id":1,"title":"우유 사기","is_done":false,...}

# 5) 부분 수정 (완료 표시)
curl -s -X PATCH http://127.0.0.1:8000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"is_done":true}'
# {"id":1,"title":"우유 사기","is_done":true,...}

# 6) 삭제
curl -s -X DELETE http://127.0.0.1:8000/todos/2 -w "%{http_code}\n"
# (응답 본문 없음) 204

# 7) 없는 todo 조회 → 404
curl -s -i http://127.0.0.1:8000/todos/9999
# HTTP/1.1 404 Not Found
# ...
```

이 한 라운드가 모두 통과하면 **6장의 핵심 내용이 모두 동작하는 것입니다.** 축하합니다.

### 6.14.3 검증 실패는 어떻게 보이나

빈 title을 보내보면 422가 떨어집니다.

```bash
curl -s -i -X POST http://127.0.0.1:8000/todos \
  -H "Content-Type: application/json" \
  -d '{"title":""}'

# HTTP/1.1 422 Unprocessable Entity
# Content-Type: application/json
# ...
# {"detail":[{"type":"string_too_short","loc":["body","title"],"msg":"String should have at least 1 character",...}]}
```

`TodoCreate.title`에 `min_length=1`을 줬기 때문입니다. **이 검증은 ORM이 아니라 Pydantic이 한 일**이며, DB에 도달하기 전에 막혔습니다.

---

## 6.15 SQLite에서 PostgreSQL로 옮기기 — `DATABASE_URL`만 바꾸면 됨

ORM의 가장 큰 실용적 가치 중 하나가 이것입니다. 우리가 짠 모델·라우트 코드 한 줄도 바꾸지 않고 DB 종류만 바꿀 수 있습니다.

### 6.15.1 PostgreSQL 준비 (Docker로)

가장 간단한 방법은 Docker로 띄우는 것입니다.

```bash
docker run --name fastapi-pg \
  -e POSTGRES_DB=tododb \
  -e POSTGRES_USER=todouser \
  -e POSTGRES_PASSWORD=todopass \
  -p 5432:5432 \
  -d postgres:17
```

PostgreSQL이 5432 포트에서 떴습니다.

> **Docker가 없거나 설치가 부담스러우면** 이 절은 읽기만 하고 넘어가도 됩니다. 09장 배포에서 Docker를 본격적으로 다루며, 그때 다시 시도해 볼 수 있습니다.

### 6.15.2 비동기 PostgreSQL 드라이버 설치

```bash
uv add asyncpg
```

> **`asyncpg`란?** PostgreSQL용 비동기 파이썬 드라이버. SQLAlchemy 2.0이 PostgreSQL과 비동기로 대화할 때 가장 빠르고 표준입니다.

### 6.15.3 `DATABASE_URL` 한 줄 바꾸기

`.env` 파일을 만들고:

```
DATABASE_URL=postgresql+asyncpg://todouser:todopass@localhost:5432/tododb
```

그리고 셸에 적용해 주거나, 터미널에서 직접 export.

```bash
export DATABASE_URL="postgresql+asyncpg://todouser:todopass@localhost:5432/tododb"
```

> **`.env` 파일은 자동으로 읽히나요?** Pydantic Settings(추후 챕터)나 `python-dotenv` 같은 라이브러리가 있어야 자동으로 읽힙니다. 본 챕터는 단순화를 위해 `os.environ.get`만 씁니다. 다음 명령들은 셸에서 export한 환경 변수를 읽습니다.

### 6.15.4 마이그레이션 적용 + 서버 재시작

```bash
uv run alembic upgrade head     # PG에 todos 테이블이 새로 만들어진다
uv run uvicorn app.main:app --reload
```

이제 같은 코드가 SQLite가 아닌 PostgreSQL을 쓰고 있습니다. 6.14의 curl을 그대로 다시 실행해도 모두 동작합니다.

> **모델 코드는 한 줄도 안 바뀌었습니다.** 이게 ORM의 본질적인 가치입니다. SQLite로 빠르게 개발해서 검증하고, 운영 시 PostgreSQL로 옮기는 흐름이 흔합니다.

### 6.15.5 MySQL로 가려면

같은 식입니다.

```bash
uv add asyncmy
export DATABASE_URL="mysql+asyncmy://user:pass@localhost:3306/tododb"
uv run alembic upgrade head
```

> **드라이버 차이로 동작이 달라지는 경우**: 99% 똑같이 동작합니다. 다만 PostgreSQL의 JSONB·배열, MySQL의 utf8mb4 콜레이션, SQLite의 빈약한 ALTER TABLE 같은 DB별 특성을 쓰는 모델은 옮겼을 때 작은 차이가 날 수 있습니다. 본 챕터의 Todo 같은 단순한 모델은 차이가 없습니다.

---

## 6.16 N+1 문제와 `selectinload` 맛보기

### 6.16.1 무엇이 문제인가

이 챕터는 모델이 하나(Todo)뿐이라 N+1 문제가 등장하지 않습니다. 하지만 11장에서 `User`와 `Post`처럼 관계가 있는 모델을 다루면 곧 만나게 됩니다. 미리 한 번 보고 갑니다.

상상해 봅시다. 사용자가 100명, 각 사용자가 글을 5개씩 가지고 있고, "모든 사용자와 그들의 글을 함께 보여라"는 라우트가 있습니다.

**잘못된 구현 (N+1 쿼리):**

```python
# ⚠️ 안티패턴
users = (await session.execute(select(User))).scalars().all()  # 1번 쿼리
for user in users:
    posts = (await session.execute(
        select(Post).where(Post.user_id == user.id)
    )).scalars().all()                                          # 사용자마다 1번 = 100번 쿼리
    # 총 1 + 100 = 101 번 쿼리!
```

이게 **N+1 문제**입니다. 사용자 수(N)가 늘어날수록 쿼리가 선형으로 늘어 성능이 무너집니다.

> **N+1 문제란?** "목록을 가져오는 1번 쿼리"와 "그 목록의 각 항목마다 추가 1번씩 N번 쿼리"가 합쳐져 총 N+1번 쿼리가 나가는 비효율 패턴입니다. ORM 사용자가 가장 자주 만드는 성능 문제이며, eager loading으로 해결합니다.

### 6.16.2 `selectinload`로 해결

같은 일을 한 번의 SELECT(또는 두 번이지만 N에 무관하게 일정한 횟수)로 끝낼 수 있습니다.

```python
from sqlalchemy.orm import selectinload

stmt = select(User).options(selectinload(User.posts))
users = (await session.execute(stmt)).scalars().all()

for user in users:
    # user.posts 는 이미 로드되어 있음 — 추가 쿼리 없음
    print(user.email, len(user.posts))
```

`selectinload(User.posts)`는 SQLAlchemy에게 "User를 가져올 때, 관련 Post들도 한 번에 같이 가져와라"고 지시합니다. 내부적으로 두 번의 SELECT(`SELECT * FROM users`, `SELECT * FROM posts WHERE user_id IN (...)`)로 끝납니다. 사용자가 100명이든 10000명이든 두 번뿐입니다.

이외에도 `joinedload`(JOIN 한 번으로 처리), `subqueryload` 등 여러 옵션이 있지만, **본 가이드의 권장 1순위는 `selectinload`** 입니다. 거의 모든 1:N에서 무난히 동작하고 직관적입니다.

> **본 챕터에서는 깊이 안 들어갑니다.** 자세한 내용과 실전 사용은 11장 Blog API에서 1:N·N:M 관계를 만들 때 본격적으로 다룹니다. 지금은 "이런 함정과 도구가 있다"는 것만 기억해 두면 됩니다.

---

## 6.17 다른 DB로 옮길 때 — 정리

이 챕터에서 익힌 내용 중 **DB 전환에 관한 핵심**만 표로 모읍니다.

### 6.17.1 DATABASE_URL 형식

| DB | 형식 | 비고 |
|----|------|------|
| SQLite (파일) | `sqlite+aiosqlite:///./todo.db` | 슬래시 3개. 상대 경로 |
| SQLite (절대 경로) | `sqlite+aiosqlite:////absolute/path/db.sqlite` | 슬래시 4개에 주의 |
| SQLite (메모리) | `sqlite+aiosqlite:///:memory:` | 테스트용 |
| PostgreSQL | `postgresql+asyncpg://user:pass@host:5432/dbname` | 표준 포트 5432 |
| PostgreSQL (TLS) | `postgresql+asyncpg://user:pass@host:5432/db?ssl=true` | 운영 권장 |
| MySQL | `mysql+asyncmy://user:pass@host:3306/dbname` | 표준 포트 3306 |
| MariaDB | `mysql+asyncmy://user:pass@host:3306/dbname` | MySQL과 동일 드라이버 |

### 6.17.2 옮기는 절차 한 장 요약

1. 새 비동기 드라이버 설치 (`uv add asyncpg` 등)
2. `DATABASE_URL` 환경 변수를 새 형식으로 변경
3. `uv run alembic upgrade head`로 새 DB에 스키마 생성
4. 서버 재시작 (`uv run uvicorn app.main:app --reload`)
5. 끝

코드 변경: **0줄**. (단, DB별 특수 타입을 쓴 경우는 별도 검토 필요)

---

## 6.18 흔한 함정과 해결법

이 챕터에서 입문자가 가장 자주 만나는 문제들을 모았습니다.

### 6.18.1 commit 잊기

```python
# ⚠️ 안티패턴
@app.post("/todos")
async def create_todo(payload, session=Depends(get_session)):
    todo = Todo(title=payload.title)
    session.add(todo)
    return todo   # commit 을 안 했는데 어쩌지?
```

**우리 가이드의 패턴에서는 문제가 안 됩니다.** `get_session` 의존성이 라우트 종료 후 자동으로 commit하기 때문입니다. 다만 6.6의 `get_session`을 안 쓰고 의존성 함수에서 `yield session` 뒤에 commit을 안 적은 경우라면, 정말로 commit이 안 나가서 데이터가 사라집니다.

> **체크포인트**: 본 가이드의 `get_session`을 그대로 복사해 쓰면 안전합니다. 직접 변형하지 마세요.

### 6.18.2 async/sync 혼용

```python
# ⚠️ 안티패턴
@app.get("/todos")
async def list_todos(session=Depends(get_session)):
    rows = session.execute(select(Todo))   # await 빠뜨림!
    return rows
```

`session.execute`는 코루틴을 반환합니다. `await` 없이 그냥 변수에 담으면 실제 SQL은 실행되지 않고, 그 코루틴 객체가 반환됩니다. **에러 메시지가 어색해서 디버깅이 어렵습니다.** 항상 `await`를 잊지 마세요.

> **반대로 sync 함수에서 비동기 메서드를 부르면**: `await`를 못 써서 다음과 같은 경고가 뜹니다 — `RuntimeWarning: coroutine ... was never awaited`. 함수에 `async def`를 안 쓴 게 원인입니다.

### 6.18.3 세션을 함수 밖에서 쓰기

```python
# ⚠️ 안티패턴
session = SessionLocal()    # 모듈 전역에 한 번만!
@app.get("/todos")
async def list_todos():
    return await session.execute(select(Todo))   # 모든 요청이 같은 session 공유
```

이렇게 하면 **모든 요청이 같은 세션을 쓰기 시작**합니다. 트랜잭션이 엉키고, 한 요청의 rollback이 다른 요청에 영향을 주고, 알 수 없는 에러가 뜹니다.

> **항상 의존성으로 받아 함수 안에서만 쓰세요.** `Depends(get_session)`이 한 요청 한 세션을 보장합니다.

### 6.18.4 `id`가 `None`인 채로 응답

```python
todo = Todo(title="x")
session.add(todo)
return todo   # ⚠️ id 가 아직 채워지지 않았을 수 있음
```

`add`만 한 시점에는 `todo.id`가 `None`입니다(아직 INSERT 전이므로). 응답으로 나가기 전에 `await session.flush()` 또는 `await session.commit()`이 한 번 일어나야 자동 생성된 PK가 객체에 채워집니다. 6.9의 `create_todo`처럼 명시적으로 `await session.flush()`와 `await session.refresh(todo)`를 부르는 것이 가장 안전합니다.

### 6.18.5 `expire_on_commit=True`로 commit 후 속성 접근 시 에러

기본값(`True`)이면 commit 직후 객체의 모든 속성이 "만료" 상태가 되어, 다시 접근하려면 `refresh`가 필요합니다. FastAPI 라우트에서 응답 직전에 commit이 일어나는 흐름과는 잘 맞지 않습니다. **6.6의 `expire_on_commit=False` 설정을 그대로 쓰세요.**

### 6.18.6 마이그레이션이 빈 파일로 만들어짐

`alembic revision --autogenerate`를 돌렸는데 `upgrade()`/`downgrade()`가 비어 있는 경우, `env.py`에서 모델을 import하지 않아서 `Base.metadata`가 비어 있는 상태입니다. 6.12.4의 `from app import models  # noqa: F401` 한 줄을 빠뜨렸는지 확인하세요.

### 6.18.7 `sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such table: todos`

마이그레이션을 적용하지 않은 채로 라우트를 호출한 경우입니다. `uv run alembic upgrade head`를 한 번 실행하면 해결됩니다.

### 6.18.8 SQLite에서 `Boolean`이 `0/1`로 나옴

SQLite는 진짜 BOOLEAN 타입이 없고 INTEGER로 저장합니다. 그래서 외부 도구(예: `sqlite3` CLI)로 직접 보면 `is_done`이 `0`이나 `1`로 보입니다. **이는 정상입니다.** SQLAlchemy/Pydantic이 응답할 때는 `true`/`false`로 변환해 줍니다. PostgreSQL/MySQL은 진짜 BOOLEAN이라 그대로 `true`/`false`입니다.

### 6.18.9 PostgreSQL 연결 시 `password authentication failed`

비밀번호가 틀렸거나 사용자가 없습니다. Docker로 띄웠다면 `docker logs fastapi-pg`로 초기화 로그를 보고, 환경 변수가 우리가 지정한 것과 일치하는지 확인합니다.

### 6.18.10 `RuntimeWarning: coroutine 'AsyncSession.execute' was never awaited`

위 6.18.2의 `await` 누락이 원인입니다.

---

## 6.19 더 깊이 보기 — 이 챕터에서 의도적으로 미룬 것

이 챕터는 입문 분량을 지키기 위해 다음을 미뤘습니다.

- **관계(1:N, N:M) 모델링** — 11장 Blog API.
- **`selectinload`/`joinedload`의 자세한 비교** — 11장.
- **트랜잭션 중첩과 SAVEPOINT** — 본 가이드 범위 외(필요해지면 SQLAlchemy 공식 문서로).
- **Alembic의 분기·병합·라벨** — 본 가이드 범위 외.
- **수동(autogenerate 안 쓰는) 마이그레이션 작성** — 11장에서 데이터 마이그레이션 예시.
- **PostgreSQL 특화 기능(JSONB, 배열, 풀텍스트 검색)** — 12장 레퍼런스.
- **SQLAlchemy의 `Session.scalars(...)` 단축 표기** — 같은 일을 더 짧게 쓰는 형태가 있지만(`await session.scalars(select(Todo))`), 본 가이드는 표준적인 `execute() → scalars()` 흐름을 일관되게 사용했습니다.

---

## 6.20 이 챕터 요약

- 데이터베이스는 **요청 사이에 자료가 살아 있어야 하는** 모든 백엔드의 기본이다.
- **ORM**은 DB의 표를 파이썬 클래스에 매핑해, SQL을 직접 쓰지 않고도 객체처럼 데이터를 다룰 수 있게 한다.
- 이 가이드는 **SQLAlchemy 2.0 (async)** + **Alembic**을 표준으로 못 박는다.
- DB 드라이버는 비동기 전용을 쓴다: SQLite=`aiosqlite`, PostgreSQL=`asyncpg`, MySQL=`asyncmy`.
- 모델은 새 표기법(`Mapped[...]`, `mapped_column(...)`)으로 작성한다 — IDE 지원이 가장 좋다.
- **Pydantic 스키마**(요청·응답 모양)와 **ORM 모델**(DB 매핑)은 분리하고, `from_attributes=True`로 잇는다.
- `app/db.py`의 `get_session()` 의존성이 한 요청 = 한 세션 = 한 트랜잭션을 보장한다. 라우트는 `Depends(get_session)`만 받으면 끝.
- CRUD는 `select(...)`/`session.add(...)`/`session.get(...)`/`session.delete(...)` 그리고 객체 속성 변경 + 자동 UPDATE.
- **Alembic**은 모델 변경을 자동 감지(`autogenerate`)해 마이그레이션 파일을 만들고, `upgrade head`로 적용한다.
- `env.py`를 **비동기 엔진**용으로 한 번 수정해 두면, 이후 챕터들이 모두 그대로 쓴다.
- DB를 SQLite → PostgreSQL → MySQL로 옮길 때 **`DATABASE_URL`만 바꾸면 코드는 그대로**다.
- N+1 문제를 인식하고, 관계 자료를 미리 같이 가져오는 `selectinload`로 해결한다(11장에서 자세히).
- 다음 챕터(07)에서 본 챕터의 Todo 예제를 **라우터 분리 + 더 풍부한 검증·페이지네이션·테스트**로 확장한다.

---

## 부록 A. 본 챕터 예제 전체 파일 목록

`examples/06-SQLAlchemyTodo/` 폴더에 본 챕터의 코드가 모두 들어 있습니다.

```
06-SQLAlchemyTodo/
├── pyproject.toml          # uv add ... 가 만들고 갱신한 의존성 목록
├── uv.lock                 # 잠금 파일
├── .python-version         # 3.13
├── .env.example            # DATABASE_URL 의 기본값 예시
├── .gitignore              # *.sqlite, .env, __pycache__ 등 제외
├── README.md               # 실행·마이그레이션·curl 예시
├── alembic.ini             # Alembic 설정
├── alembic/
│   ├── env.py              # 비동기 엔진용으로 수정된 부트스트랩
│   ├── script.py.mako      # revision 파일 템플릿(기본)
│   └── versions/
│       └── .gitkeep
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI 앱 + 모든 CRUD 라우트
    ├── config.py           # DATABASE_URL
    ├── db.py               # AsyncEngine, async_sessionmaker, get_session
    ├── models.py           # Todo ORM 모델
    └── schemas.py          # TodoCreate, TodoRead, TodoUpdate
```

> **첫 마이그레이션 파일은 의도적으로 비워 두었습니다.** 본 가이드를 따라하는 학습자가 직접 `uv run alembic revision --autogenerate -m "create todos table"`을 실행해 자동 생성되는 흐름을 체험하기 위함입니다. `versions/.gitkeep`만 들어 있습니다.

---

## 부록 B. 자주 쓰는 명령 모음 (치트시트)

```bash
# 프로젝트 시작
uv init
uv add fastapi "uvicorn[standard]" "sqlalchemy[asyncio]" alembic aiosqlite

# Alembic 초기화 (한 번만)
uv run alembic init alembic
# → alembic/env.py 를 비동기용으로 수정

# 마이그레이션 만들기 + 적용
uv run alembic revision --autogenerate -m "create todos table"
uv run alembic upgrade head

# 마이그레이션 되돌리기
uv run alembic downgrade -1
uv run alembic downgrade base

# 히스토리 / 현재 상태 보기
uv run alembic history
uv run alembic current

# 서버 실행
uv run uvicorn app.main:app --reload

# DB 옮기기 (예: PostgreSQL)
uv add asyncpg
export DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/db"
uv run alembic upgrade head

# SQLite 파일 직접 들여다보기
sqlite3 todo.db
sqlite> .tables
sqlite> .schema todos
sqlite> select * from todos;
sqlite> .quit
```

---

← [05. 라우팅과 Pydantic](05-routing-content.md) | 다음 문서로 이동: **[07. CRUD 예제 — Todo API →](07-crud-example.md)**
