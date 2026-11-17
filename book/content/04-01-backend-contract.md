---
id: backend-contract
chapter: 4
number: 4.1
title: 작은 백엔드와 인터페이스 계약
summary: 요청·응답 형식을 계약으로 먼저 정하고, 같은 계약으로 검증·오류·문서를 맞추기.
---

## 학습 목표와 선수 개념

- 인터페이스 계약이 무엇이고 왜 구현보다 먼저 합의해야 하는지 설명한다.
- 계약 하나로 입력 검증과 오류 응답을 만들고, 모든 위반을 한 번에 알려 준다.
- OpenAPI 문서와 코드가 어긋나지 않게 유지하는 방법을 고른다.

선수 개념: 2.1·2.2절(HTTP, problem details), 3.1절(SQL).

## 현장 상황

고객사의 프론트엔드 팀, FDE, 고객사 백엔드 팀이 동시에 일한다. "문의 생성 API"를 두고 프론트엔드는 `title`을, 백엔드는 `subject`를 쓰고 있었다는 사실이 통합 테스트 날에야 드러났다. 이틀이 사라졌다. OpenAI FDE 공고는 FDE가 고객 엔지니어링 팀과 함께 **기술 범위 설정과 시스템 설계**를 맡는다고 쓴다. 여러 팀이 함께 일할 때 가장 먼저 합의할 것은 구현이 아니라 경계, 즉 인터페이스다.

## 원리와 용어

**인터페이스 계약**은 두 시스템이 주고받을 요청·응답의 형식과 의미에 대한 합의다. 최소한 다음을 정한다.

- 경로와 메서드: `POST /tickets`, `GET /tickets/{id}`
- 요청 필드: 이름, 타입, 필수 여부, 길이·허용 값, 기본값
- 응답: 성공 상태 코드와 본문, 실패 상태 코드와 오류 형식(RFC 9457)
- 의미: "`channel`을 빼면 `email`로 간주한다", "알 수 없는 필드는 거부한다"

계약을 기계가 읽을 수 있는 형식으로 쓰는 표준이 **OpenAPI**다. 같은 내용을 OpenAPI 3.1로 쓰면 다음과 같다.

```yaml
paths:
  /tickets:
    post:
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              additionalProperties: false
              required: [subject, body]
              properties:
                subject: { type: string, maxLength: 120 }
                body:    { type: string, maxLength: 5000 }
                channel: { type: string, enum: [email, chat, phone], default: email }
      responses:
        "201": { description: 생성됨 }
        "422": { description: 계약 위반, content: { application/problem+json: {} } }
```

**계약이 단일 근거**여야 한다. 문서는 `maxLength: 120`인데 코드는 200자까지 받는다면, 어느 쪽이 맞는지 아무도 모른다. 방법은 두 가지다. (1) OpenAPI 문서에서 검증 코드를 생성하거나 런타임에 문서로 검증한다. (2) 코드의 계약 정의에서 문서를 생성한다. 이 절의 예제는 개념을 보이려고 계약을 Python 딕셔너리 하나에 두고 검증이 그것만 보게 했다.

**알 수 없는 필드 거부**(`additionalProperties: false`)는 오타를 빨리 드러낸다. `subjcet`처럼 틀린 이름을 조용히 무시하면 클라이언트는 필드가 저장됐다고 믿는다. 반대로 하위 호환을 위해 모르는 필드를 허용하는 API도 있으므로, 어느 쪽인지 계약에 명시한다.

## 예제: 계약으로 검증하는 문의 API

`CONTRACT`가 필드 규칙의 유일한 정의다. `validate`는 위반을 **모두** 모아 돌려주고, 서버는 그것을 problem details의 확장 필드 `errors`로 보낸다.

::example ch4/tickets_api.py

해설:

- 첫 요청은 계약을 지켜 201과 저장된 문의를 받았다. 저장된 값을 다시 읽어 응답하므로 기본값(`status: open`)도 클라이언트가 확인할 수 있다.
- 두 번째 요청은 네 가지를 어겼다. 하나씩 고치며 네 번 왕복하지 않도록 한 번에 알려 준다.
- `errors`는 RFC 9457이 허용하는 확장 멤버다. 표준 멤버(`type`, `title`, `status`)는 그대로 두고 필요한 정보를 더한다.
- 이 서버는 `http.server`로 만든 학습용이다. Python 문서도 이 모듈을 운영용으로 권하지 않는다. 운영에서는 검증된 웹 프레임워크와 서버를 쓰되, 계약·검증·오류 형식의 원리는 같다.

## 흔한 오류와 디버깅

- **계약 없이 구현부터**: 통합 직전에 필드 이름·타입·날짜 형식 불일치가 터진다. 짧은 OpenAPI 초안과 예시 요청·응답을 먼저 공유하고 서명(합의)을 받는다.
- **날짜·금액 형식 미정**: `"2026-11-17"`인지 `"17/11/2026"`인지, 금액이 원 단위 정수인지 소수인지 계약에 적는다. 시간은 시간대를 포함한 ISO 8601이 안전하다.
- **오류마다 형식이 다름**: 어떤 엔드포인트는 `{"error": "…"}`, 어떤 것은 문자열을 돌려주면 클라이언트 오류 처리가 엔드포인트마다 달라진다.
- **조용한 변경**: 응답 필드를 지우거나 의미를 바꾸면 기존 클라이언트가 깨진다. 추가는 대체로 안전하고, 삭제·변경은 새 버전이나 사전 공지가 필요하다.

## 이해 확인

::quiz
`channel` 필드를 계약에서 `required: False`, 기본값 `email`로 정했다. 고객사가 "채널을 안 보내면 `null`로 저장해 달라"고 한다. 무엇을 확인하고 어디를 바꾸는가?
::answer
먼저 의미를 확인한다. "모름"을 구분해야 하는 업무 이유가 있다면 기본값 `email`은 사실을 왜곡하므로 고쳐야 한다. 바꿀 곳은 계약 하나(`CONTRACT`와 OpenAPI 문서)이며, DB 열의 `NOT NULL`도 함께 바꾼다. 기존 데이터에서 기본값으로 들어간 `email`과 실제 `email`을 구분할 수 없다는 한계도 고객에게 알린다.
::end

::quiz
클라이언트가 `{"subject": "환불", "body": "…", "subjcet": "환불 요청"}`을 보냈다. 알 수 없는 필드를 무시하는 서버와 거부하는 서버는 각각 어떻게 동작하며, 어느 쪽이 이 상황에서 나은가?
::answer
무시하는 서버는 201을 돌려주고 오타 필드를 버린다. 클라이언트는 문제를 모른 채 넘어간다. 거부하는 서버는 422와 `subjcet: 계약에 없는 필드`를 돌려줘 개발 중에 오타를 바로 찾게 한다. 새 통합을 만드는 지금은 거부가 낫다. 다만 이미 많은 클라이언트가 있는 API에 거부를 새로 도입하면 기존 클라이언트가 깨질 수 있으므로 공지와 단계적 적용이 필요하다.
::end

## 출처

- OpenAPI Specification v3.1.1. https://spec.openapis.org/oas/v3.1.1.html (접근일 2026-11-17)
- RFC 9457 Problem Details for HTTP APIs, 3.2절(확장 멤버). https://www.rfc-editor.org/rfc/rfc9457 (접근일 2026-11-17)
- Python 문서 `http.server` — 운영용으로 권장하지 않는다는 경고. https://docs.python.org/3/library/http.server.html (접근일 2026-11-17)
- OpenAI Forward Deployed Engineer – Seoul 공고 — discovery, technical scoping, system design. https://jobs.ashbyhq.com/openai/b43339a1-e830-4761-a193-3438f34f9ebb (접근일 2026-11-17)
