---
title: 파일럿 매니페스트 — proposed 정책의 하네스 시범 투입
type: pilots
status: active
---

# pilots — proposed 정책의 하네스 시범 투입 기록

`proposed`(미accept) 정책을 docs-tickets 하네스에 **시범 투입**할 때 여기 기록한다. 표식이 없으면 `conformance` 감사가 이 **의도된 비정합**을 드리프트로 오탐한다.

## 규칙

- 파일럿 투입 시 아래 표에 행 추가: `{proposed ADR id → 하네스 델타 위치}`.
- ADR이 **accepted** 되면 → 델타를 영구화하고 해당 행 제거.
- ADR이 **rejected** 되면 → 델타를 롤백하고 해당 행 제거.
- `conformance` 감사는 이 표의 델타를 **정합성 검사에서 제외**한다.

## 지금은 롤백 원장이다 — 오탐 방지 기능은 잠들어 있다

**accepted ADR이 0건**이라 `conformance`의 `collect.py`는 `accepted_adrs: []` → *"전파 대상 없음"* 을 낸다. **비교할 기준선이 없으니 드리프트 오탐 자체가 불가능**하다 — 위 명분의 절반은 아직 작동하지 않는다.

그래서 당분간 이 표의 값은 **롤백 원장**이다: *"이 proposed ADR이 바뀌거나 rejected되면 하네스의 어디를 되돌려야 하는가."* 첫 accept가 나오면 그때부터 원래 명분(오탐 방지)이 켜진다.

**원래 하네스 자체는 파일럿이 아니다.** 마찰 로그가 보여주듯 **스킬이 먼저 있었고 ADR이 그 결정의 영수증으로 뒤따랐다** — 하네스가 ADR을 앞서 시험한 게 아니다. 아래 표에 오르는 것은 **ADR이 먼저 굳고 하네스가 따라간** 경우뿐이다.

## 활성 파일럿

| proposed ADR | 하네스 델타 위치 | 투입일 | 비고 |
|---|---|---|---|
| **ADR-0006** | `_lib/opsdoc.py`(`FROZEN` += `rejected`) · `adr/scripts/{freeze-check,accept,doc-path,supersede}.py` · `adr/SKILL.md` §2·§3·§4 · `agents/docs-tickets.md` · `CLAUDE.md` §3·§7 | 2026-07-16 | 동결 = **본문(의미)** 만 · **proposed 밖**(accepted·rejected·superseded) · **경로·포맷은 자유**(일괄 마이그레이션 가능). `freeze-check`의 경로-스캔 모드·`moved()`를 **삭제**했으므로, 0006이 뒤집히면 그 복원이 가장 큰 롤백이다 |
| **ADR-0004** | `adr/SKILL.md`(`references` 인자·frontmatter 템플릿) · `CLAUDE.md` §7(역할 기반 가변성) | 2026-07-16 | 메타데이터 가변성을 **역할**에서 파생 — 분류(`topic`·`subjects`)는 확정 후에도 가변, 출처(`references`)는 동결 |

*ADR-0009·0010(티켓 단일 타입·컨테이너/리프)은 하네스 델타가 없어 행이 없다 — 이미 있던 Issue Type 구조의 영수증일 뿐이다.*
