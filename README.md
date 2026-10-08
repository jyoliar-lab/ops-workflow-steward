# ops-workflow-steward

`ops-workflow`와 `ticket-engineer`를 **밖에서** 설계·감사·교정하는 거버넌스 하네스. 규약은 [`CLAUDE.md`](CLAUDE.md)에 있다 — 이 파일은 사람을 위한 **하네스 구조 안내**이고, agent는 읽지 않는다.

## 구조

```
ops-workflow-steward/
├── CLAUDE.md                    규약 — 매 세션 로드
├── pilots.md                    롤백 원장 — 어느 정책 ADR의 델타가 하네스의 어디에 들어갔나 (conformance가 읽는다)
├── staging/                     gitignored — steward가 사람에게 넘기는 개정안·마찰 로그
└── .claude/
    ├── agents/policy-steward.md 역할 프롬프트 (claude --agent policy-steward)
    ├── skills/                  ops-tools(저작 도구 구동) · conformance(하네스 정합·전파) · harness-authoring(하네스 파일 저작 규율)
    ├── rules/                   규약의 일부
    ├── hooks/guard-write.py     쓰기 경계·전이 금지 hook
    ├── settings.json            hook 등록 · 권한 — 공통
    ├── settings.local.json      gitignored · PC별 (아래)
    └── write-allow.txt          gitignored · 사람만 — 일시 쓰기 허용 루트
```

세션은 **저장소 루트에서** 연다 — hook·스크립트가 `$CLAUDE_PROJECT_DIR`(세션 cwd)을 자기 루트로 쓴다.

## ADR의 흐름에서 steward가 서는 자리

steward는 정책 ADR(`topic: ops-workflow`)의 **초안**을 `proposed`까지 쓴다. 심사(임계선·입도·"왜"만·자족성·기존 ADR과 충돌)는 ops-workflow의 **adr-judge** 하네스(`cd ops-workflow && claude --add-dir harness/adr-judge`)가 한다 — 사람이 그 세션을 연다. 정책 ADR은 통과해도 `proposed`로 남고(ADR-0032), accept는 사람이 "안정됐다"고 명시할 때만이다. 심사가 끝나면 steward가 하네스 델타를 내고 `pilots.md`에 위치를 적는다.

## 로컬 설정 — PC별

`.claude/settings.local.example.json`을 `.claude/settings.local.json`으로 복사해 채운다. 두 가지가 들어간다:

| 키 | 값 | 쓰는 곳 |
|---|---|---|
| `env.OPS_WORKFLOW_ROOT` · `env.TICKET_ENGINEER_ROOT` | 두 클론의 절대경로 | hook의 경계 판정 · 모든 스크립트 |
| `permissions.additionalDirectories` | 같은 두 경로 | Claude Code가 두 저장소 파일을 프롬프트 없이 읽고, 편집을 권한 모드에 따라 허용한다 (설정 파일로 지정한 디렉터리는 스킬·agent·CLAUDE.md를 로드하지 않는다 — `--add-dir`와 다르다) |

이 파일이 git 추적 대상이면 Claude Code가 "저장소에서 온 설정"으로 보고 신뢰 전까지 보류하므로 gitignored 상태를 유지한다. `env`는 공식 문서상 변수 단위로 적용된다(같은 변수가 여러 파일에 있으면 우선순위 높은 쪽) — 두 변수를 한 파일에 두면 어느 쪽이든 안전하다.

## 구조로 강제하는 것

| 지켜지는 것 | 강제하는 구조 |
|---|---|
| 쓰기 경계 — `$OPS_WORKFLOW_ROOT`의 `docs/ops-workflow/**`·`CLAUDE.md`·`.claude/**`·`harness/**`, `$TICKET_ENGINEER_ROOT/**`, 자기 repo(`.claude/` 제외) | `guard-write.py`(PreToolUse, Write·Edit)가 그 밖을 거부한다. 거부 사유에 허용 범위와 대안이 들어 있다 |
| 자기 하네스(`.claude/`)는 사람만 고친다 (CLAUDE.md §5) | 같은 hook가 자기 repo의 `.claude/**` Write·Edit를 거부한다. **Bash 경유(`sed -i`·리다이렉션·heredoc)는 막지 않는다** — 그 경로는 §5 산문이 유일한 보호다 |
| 동결선 전이 금지 — accept·supersede·unaccept는 adr-judge의 것 (§5) | `guard-write.py`(PreToolUse, Bash)가 `accept.py`·`supersede.py`·`unaccept.py`가 든 명령을 거부한다 |
| Issue close 금지 (§5) | 같은 Bash 분기가 `gh issue close`를 거부한다 |
| 일시 허용 | 사람이 `.claude/write-allow.txt`에 절대경로를 한 줄씩 적는다(`#` 주석). 매 호출 읽히므로 세션 재시작 없이 켜고(작성) 끈다(삭제). `.claude/` 안이라 steward 자신은 쓸 수 없다. **임시다 — 끝나면 지운다** |
| 동결·번호·게이트 | ops-workflow의 스크립트가 거부한다(exit 1) |
| env 미설정 | `OPS_WORKFLOW_ROOT`가 없으면 hook가 모든 밖 쓰기를 거부하고, 스크립트는 exit 1 |

hook는 **fail-open**이다 — 입력 파싱 실패·대상 도구 아님이면 통과시킨다. 세션을 브릭하지 않기 위한 선택이다.

## ops-workflow 스크립트 구동

ops-workflow 스크립트는 cwd에서 `.git`을 찾아 대상 repo를 정하므로 **cwd가 `$OPS_WORKFLOW_ROOT`**여야 한다. 두 방법은 동치다:

```bash
python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/ops-tools/scripts/ops-run.py" <ops 기준 상대경로> [args]   # 래퍼가 chdir 후 exec
cd "$OPS_WORKFLOW_ROOT" && python3 <ops 기준 상대경로> [args]
```

스크립트 위치는 ops-workflow README의 하네스 구조를 따른다 — 공통 `adr`은 루트 `.claude/skills/`, `ticket`은 `harness/design-partner/`, 인덱스는 `.claude/scripts/build-index.py`. `list-ops-tools.py`가 이 전부를 라이브로 보여준다(adr-judge의 `adr-accept`도 보이지만 steward는 부르지 않는다 — hook가 거부한다). ops-workflow 안에서는 PostToolUse hook가 `_index/`를 자동 재생성하지만 **steward 세션에는 그 hook가 없다** — 문서를 바꾼 뒤 `build-index.py`를 직접 돌린다.

## conformance의 기준선

정책 ADR은 `proposed`가 현행 규범이다(ADR-0032). 그래서 `conformance/collect.py`는 `accepted`가 아니라 **origin/main에 공표된 정책 ADR 전부**(proposed·accepted)를 대조 기준선으로 내고, superseded·rejected는 "역행" 판정의 재료로 따로 낸다. 로컬에만 있는 초안은 전파 대상이 아니다.
