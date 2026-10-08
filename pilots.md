---
title: 파일럿 매니페스트 — proposed 정책의 하네스 시범 투입
type: pilots
status: active
---

# pilots — proposed 정책의 하네스 시범 투입 기록

`proposed`(미accept) 정책을 피관리 하네스(ops-workflow 역할 하네스·ticket-engineer)에 **시범 투입**할 때 여기 기록한다. 표식이 없으면 `conformance` 감사가 이 **의도된 비정합**을 드리프트로 오탐한다.

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
| **ADR-0016** | **docs-tickets**: `ticket/scripts/create.py`(리프 저장소 게이트 — target 지정 XOR 명시적 부재, 본문 '저장소' 절, Project `Target Repos` 필드) · `ticket/scripts/repo_context.py`(**표기의 원본** — YAML 블록 emitter+엄격 파서+왕복 자가검증. 절은 `### 저장소` + ```` ```yaml ```` 펜스, `target-repos:` 목록 XOR `null`, `ref-repos:` 목록/`[]`) · `ticket/scripts/set-repos.py`(사후 소급 기입·갱신 — pre-0016 리프 + 구식 산문 절의 YAML 마이그레이션) · `_lib/gh.py`(`issue_view`·`update_issue_body`·`project_item`) · `ticket/SKILL.md` §2 · `CLAUDE.md` §5("리프는 저장소 맥락을 명시한다" 절) —— **ticket-engineer**: `_lib/repos.py`(**쌍둥이 파서** — 원본과 함께 움직인다. conformance 감사 시 원본과 대조) · `ticket-start/scripts/ticket-run.py`(`parse_repos` — 쌍둥이 파서 사용, 산문 정규식 제거) · `ticket-report/scripts/preflight.py`(검사 ⑤ — 동일) · `CLAUDE.md` §1(target/ref 의미)·§2③·§3(target 확장 = 멈추고 묻기 → set-repos.py 로 갱신 필수, 손편집 금지) · `ticket-start/SKILL.md` ④ · `ticket-report/SKILL.md` ①② | 2026-07-22 | 리프 티켓의 저장소 맥락(수정 대상 target = 권위·갱신 필수 / 참조 ref = 비완전 힌트·권장). 본문 표기는 YAML 펜스 블록 — ADR-0016이 표기를 도구에 위임했으므로 표기 변경은 supersede 사유가 아니다. GitHub Project #1에 `Target Repos` 텍스트 필드 필요. rejected 시 롤백: 게이트·본문 절·필드 기입·preflight ⑤ 제거 + `repo_context.py`·`set-repos.py`·`_lib/repos.py` 삭제·`gh.py` 3함수 제거(단, 기입된 이슈 본문 절은 이미 발행물 — 되돌리지 않는다), engineer 절차를 산문 판별로 복원 |

| **ADR-0017** | **docs-tickets**: `ticket/scripts/create.py`(리프 선행 의존 게이트 — `--blocked-by` 나열 XOR `--no-deps` 무의존 선언, 침묵 거부, 발행 후 네이티브 관계 기입) · `ticket/scripts/dep_context.py`(게이트·기입 공용 로직 — 선행은 열린 리프만, 자기참조 거부, 통째 교체 `replace`) · `ticket/scripts/set-deps.py`(사후 갱신 — 전체 답 교체, 컨테이너·닫힌 이슈 거부) · `_lib/gh.py`(`issue_brief`·`issue_blocked_by`·`add_blocked_by`·`remove_blocked_by`) · `ticket/SKILL.md`(선행 의존 절 + 사후 기입 3종화) · `CLAUDE.md` §5("리프는 선행 의존에 답한다" 절) —— **ticket-engineer**: `ticket-start/scripts/ticket-run.py`(`check_dependencies` — 열린 선행: 새 착수 exit 1 / In Progress 재개 exit 3 보고만 · `blockedBy` 쿼리 추가 · `current_status`) · `ticket-start/SKILL.md` ④(선행 거부 사유) · `CLAUDE.md` §2③(착수 게이트)·§3(미기재 선행 발견 → set-deps.py 갱신 필수·사이드바 손편집 금지) | 2026-07-25 | 리프 티켓의 선행 의존(blocked-by). **ADR은 "한 자리·사본 금지"까지만 — 표기는 도구에 위임**(0016의 target/ref 표기 위임과 동형 — 표기 변경은 supersede 사유가 아니다). 현행 표기 = GitHub 네이티브 의존 관계 하나, 본문 절·Project 필드 없음. 무의존 선언은 발행의 문에서만 강제되고 기록되지 않는다(현행 표기의 성질 — 도구 수준). 선행 완료 기준 = close(사람 검수). rejected 시 롤백: create.py 게이트·기입 블록과 `dep_context.py`·`set-deps.py` 삭제, `gh.py` 4함수 제거, SKILL.md·CLAUDE.md 절 제거, engineer 쪽 `check_dependencies`·`current_status`·쿼리 필드·문서 절 제거 (단, 이미 걸린 네이티브 관계는 발행물 — 되돌리지 않는다) |

| **ADR-0022** | **docs-tickets**: `CLAUDE.md` §7(frontmatter 표 — discussion 전용 `ref-adrs` 행 · "필드 집합은 하한" 불릿 · 역방향 뷰 안내 불릿) · `.claude/scripts/build-index.py`(`ref-adrs` 수집 — discussion 한정 · id 꼴/미해석 경고 · by-type/discussion 에 `ref-adrs` 열 · `_index/by-ref-adr.md` 역방향 뷰 방출 · 보고 카운트) · 시연 소급 기입 1건: `docs/ops-workflow/discussion/260715_1551_cross-adr-references.md`(`ref-adrs: [ADR-0004, ADR-0005]`) | 2026-08-01 | discussion 최소 메타데이터(5필드) 중 **연결 필드(`ref-adrs`)만** 하네스 반영 — 공통 4필드는 기존 규약이 이미 담당. 형제 ADR-0023(타입·생명주기)·0024(비보관·비동결)는 현재 하네스 델타 없음 — §3 서술 갱신("done(ADR 파생)"·"전부 동결형")은 accept 시점 일. rejected 시 롤백: §7 표 행·불릿 2개 제거, build-index 의 ref-adrs 수집·경고·열·by-ref-adr 방출 제거 + `_index/by-ref-adr.md` 삭제. 이미 기입된 frontmatter 값은 임의 필드로 남아도 무방(열린 집합) — 롤백 대상 아님 |

| **ADR-0033** | **docs-tickets**: `ticket/scripts/create.py`(타입별 초기 Status — Epic·Feature·Task=`Draft` · Bug=`Todo`. 초기값 자체는 도구의 관할 — ADR은 로스터만) · `ticket/scripts/adr-gate.py`(발행 거부 기준 완화 — accepted 요구 제거, superseded·rejected·미공표만 거부. "accepted 전제" → "존재·공표 전제(발행) + accepted(착수)") · `ticket/scripts/adr_context.py`(`parse_section` 신설 + render 왕복 자가검증 — '근거 ADR' 절 기계 읽기의 **표기 원본**) · `ticket/scripts/set-adr.py`(게이트 서술 문구) · `ticket/SKILL.md`(전제 표 · 착수의 문 문단 · 타입별 초기 Status · Draft 해제=사람 · Done/Cancelled 종착) · `CLAUDE.md` §5(두 불릿 한 줄 갱신 — "공표 전제·accepted는 착수의 문"·"로스터는 ADR-0033" — 상세는 전부 `ticket` SKILL.md가 단일 소스) · Project #1 Status 필드에 `Draft`·`Cancelled` 추가(보드 설정 — 사람, 완료) —— **ticket-engineer**: `_lib/adrs.py` 신설(**쌍둥이 파서** — '근거 ADR' 절 + 코퍼스 frontmatter status 조회. 원본 adr_context.py 와 함께 움직인다) · `ticket-start/scripts/ticket-run.py`(`START_STATUSES`=(`Todo`,) — Backlog 제거 · `fetch_issue`/`load_ancestors` 계층 상향 · **`check_start_gate` 신설** — 계층 전체 ADR accepted + Status Todo/In Progress, 새 착수 exit 1 / In Progress 재개 exit 3 보고만 · `transition_parents` — Todo 부모 → In Progress 파생 전이 · `_set_status` 추출) · `ticket-start/SKILL.md` ④(게이트 거부 해소 = 사람) · `CLAUDE.md` §2(착수 게이트 한 줄) | 2026-08-07 | Status 로스터 6종(Draft·Todo·In Progress·In Review·Done·Cancelled)과 **착수 게이트 신설**(발행→착수로 게이트 이동). 착수 게이트 자체는 ADR 불저작 — 하네스 강제 방식이라 ADR감이 아니다(discussion 260806_2235 "다음"). ADR-0032 교차(정책 ADR proposed 장기 유지)는 **면제 없음**으로 확정 — 정책 토픽 작업은 티켓으로 흐르지 않고 steward 직접 요청이다(사용자 확정, 2026-08-07). 잔여 사람 작업: 기존 열린 티켓 재배치(Backlog→Draft/Todo — #29는 Todo) **먼저**, 그다음 보드 구옵션 4종(Backlog·Triage·Diagnosed·Recovering) 제거. rejected 시 롤백: create.py `INITIAL_STATUS="Backlog"` 단일값 복원, adr-gate accepted 검사 복원, adr_context `parse_section`·왕복 검증 제거(예고 주석 복원), set-adr 문구 원복, SKILL.md·CLAUDE.md §5 문구 원복, engineer `_lib/adrs.py` 삭제 + ticket-run 의 게이트·계층·파생 전이 제거·`START_STATUSES=("Backlog","Todo")` 복원, 보드 옵션 정리는 사람 |

*ADR-0009·0010(티켓 단일 타입·컨테이너/리프)은 하네스 델타가 없어 행이 없다 — 이미 있던 Issue Type 구조의 영수증일 뿐이다.*
