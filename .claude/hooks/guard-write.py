#!/usr/bin/env python3
"""PreToolUse guard — steward의 Write/Edit/MultiEdit 대상 경로를 토픽 소유권 경계로 제한.

허용:
  - $OPS_WORKFLOW_ROOT/docs/ops-workflow/**   (정책 문서 저작)
  - $OPS_WORKFLOW_ROOT/.claude/**             (공통 하네스 — skill·hook·rules)
  - $OPS_WORKFLOW_ROOT/harness/**             (역할별 하네스 — design-partner·adr-judge)
  - $OPS_WORKFLOW_ROOT/CLAUDE.md              (규약 — 하네스의 일부. 정책 변경 시 갱신)
  - $TICKET_ENGINEER_ROOT/**                  (티켓 집행 agent 하네스 — 저장소 전체. 설계 §6)
  - $CLAUDE_PROJECT_DIR/** 단 .claude/ 제외    (steward 자기 repo: pilots.md·감사로그.
                                               자기 하네스(.claude)는 사람만 개정 — 설계 §5)
  - .claude/write-allow.txt 에 적힌 루트들     (일시 허용 — 사람이 쓰고 지운다. 아래 참조)
그 외(다른 토픽 docs, 임의 경로)는 거부한다.

Bash: accept.py · supersede.py · unaccept.py 실행은 거부한다 — 동결선 전이는 adr-judge의 것(설계 §5).
      `gh issue close`는 거부한다 — close는 사람의 것(설계 §5).

경계는 env var OPS_WORKFLOW_ROOT / TICKET_ENGINEER_ROOT 로 동적이다(하드코딩 없음) —
Claude Code 권한 패턴이 env 확장을 못 하므로 이 hook 가 대신 강제한다.

★ 일시 허용 — `.claude/write-allow.txt`(gitignored · 사람만 편집):
  절대경로를 한 줄씩 적는다. `#` 시작 줄은 주석. env 가 아니라 파일인 이유:
  env 는 세션 시작 시 고정되지만 이 파일은 **매 호출 읽힌다** — "잠깐 허용"을
  세션 재시작 없이 켜고(파일 작성) 끈다(파일 삭제). 이 파일은 .claude/ 안에 있으므로
  steward 자신은 쓸 수 없다 — 허용의 주체는 언제나 사람이다.
"""
import os
import re
import sys
import json


def out_deny(reason):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, ensure_ascii=False))
    sys.exit(0)


def allow():
    sys.exit(0)


def norm(p):
    return os.path.realpath(os.path.abspath(p))


def under(path, root):
    if not root:
        return False
    root = norm(root)
    path = norm(path)
    return path == root or path.startswith(root + os.sep)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        allow()  # 입력 파싱 불가 → 가드 불가. 세션을 브릭하지 않는다(fail-open).

    tool = data.get("tool_name", "")
    if tool == "Bash":
        cmd = (data.get("tool_input") or {}).get("command", "")
        if re.search(r"\bgh\s+issue\s+close\b", cmd):
            out_deny("Issue close는 사람의 것이다(CLAUDE.md §5) — steward는 닫지 않는다. "
                     "닫을 때가 됐으면 사람에게 알린다.")
        if re.search(r"\b(accept|supersede|unaccept)\.py\b", cmd):
            out_deny("동결선 전이(accept·supersede·unaccept)는 adr-judge와 사람의 것이다(CLAUDE.md §5) — "
                     "초안 저자는 심사하지 않는다. 초안을 proposed로 두고 사람에게 adr-judge 세션을 요청한다.")
        allow()
    if tool not in ("Write", "Edit", "MultiEdit"):
        allow()

    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp:
        allow()

    ops = os.environ.get("OPS_WORKFLOW_ROOT")
    eng = os.environ.get("TICKET_ENGINEER_ROOT")
    proj = os.environ.get("CLAUDE_PROJECT_DIR")

    # steward 자기 repo (단 .claude 제외 — 자기 하네스는 사람만)
    if proj and under(fp, proj) and not under(fp, os.path.join(proj, ".claude")):
        allow()

    # ops-workflow 허용: 정책 문서 · 하네스(.claude · harness/<역할> · 루트 CLAUDE.md 규약)
    if ops and (under(fp, os.path.join(ops, "docs", "ops-workflow"))
                or under(fp, os.path.join(ops, ".claude"))
                or under(fp, os.path.join(ops, "harness"))
                or norm(fp) == norm(os.path.join(ops, "CLAUDE.md"))):
        allow()

    # ticket-engineer 하네스 — 저장소 전체가 steward의 관리 대상 (설계 §6)
    if eng and under(fp, eng):
        allow()

    # 일시 허용 루트 — 사람이 .claude/write-allow.txt 에 적어 둔 경로 (docstring 참조)
    if proj:
        allow_file = os.path.join(proj, ".claude", "write-allow.txt")
        if os.path.isfile(allow_file):
            try:
                with open(allow_file, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and under(fp, line):
                            allow()
            except OSError:
                pass  # 읽기 실패 = 허용 없음. 기본 경계로 떨어진다.

    if not ops:
        out_deny("OPS_WORKFLOW_ROOT 미설정 — 대상 경계를 확인할 수 없어 거부한다. "
                 ".claude/settings.local.json 을 확인하라.")
    out_deny(
        "쓰기 경계 위반: %s — steward는 $OPS_WORKFLOW_ROOT의 docs/ops-workflow/** · CLAUDE.md · "
        ".claude/** · harness/** 와 $TICKET_ENGINEER_ROOT/** 만 편집한다"
        "(자기 repo는 .claude 제외). 다른 토픽 docs는 design-partner 관할이다. "
        "일시 허용이 필요하면 사람이 .claude/write-allow.txt 에 경로를 적는다." % fp
    )


if __name__ == "__main__":
    main()
