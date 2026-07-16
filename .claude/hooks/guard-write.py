#!/usr/bin/env python3
"""PreToolUse guard — steward의 Write/Edit/MultiEdit 대상 경로를 토픽 소유권 경계로 제한.

허용:
  - $OPS_WORKFLOW_ROOT/docs/ops-workflow/**   (정책 문서 저작)
  - $OPS_WORKFLOW_ROOT/.claude/**             (하네스 전파·정합 — agent·skill)
  - $OPS_WORKFLOW_ROOT/CLAUDE.md              (규약 — 하네스의 일부. 정책 변경 시 갱신)
  - $CLAUDE_PROJECT_DIR/** 단 .claude/ 제외    (steward 자기 repo: pilots.md·감사로그.
                                               자기 하네스(.claude)는 사람만 개정 — 설계 §5)
그 외(다른 토픽 docs, 임의 경로)는 거부한다.

경계는 env var OPS_WORKFLOW_ROOT 로 동적이다(하드코딩 없음) — Claude Code 권한 패턴이
env 확장을 못 하므로 이 hook 가 대신 강제한다.
"""
import os
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

    if data.get("tool_name", "") not in ("Write", "Edit", "MultiEdit"):
        allow()

    fp = (data.get("tool_input") or {}).get("file_path")
    if not fp:
        allow()

    ops = os.environ.get("OPS_WORKFLOW_ROOT")
    proj = os.environ.get("CLAUDE_PROJECT_DIR")

    # steward 자기 repo (단 .claude 제외 — 자기 하네스는 사람만)
    if proj and under(fp, proj) and not under(fp, os.path.join(proj, ".claude")):
        allow()

    # ops-workflow 허용: 정책 문서 · 하네스(.claude + 루트 CLAUDE.md 규약)
    if ops and (under(fp, os.path.join(ops, "docs", "ops-workflow"))
                or under(fp, os.path.join(ops, ".claude"))
                or norm(fp) == norm(os.path.join(ops, "CLAUDE.md"))):
        allow()

    if not ops:
        out_deny("OPS_WORKFLOW_ROOT 미설정 — 대상 경계를 확인할 수 없어 거부한다. "
                 ".claude/settings.local.json 을 확인하라.")
    out_deny(
        "쓰기 경계 위반: %s — steward는 $OPS_WORKFLOW_ROOT/docs/ops-workflow/** 와 "
        "$OPS_WORKFLOW_ROOT/.claude/** 만 편집한다(자기 repo는 .claude 제외). "
        "다른 토픽 docs는 docs-tickets 관할이다." % fp
    )


if __name__ == "__main__":
    main()
