#!/usr/bin/env python3
"""ops-workflow 도구 라이브 인벤토리 — 정책 문서 저작에 쓸 스크립트 지도.

드리프트 없음: ops-workflow 의 SKILL.md 와 각 스크립트 docstring 을 **그 자리에서 읽어**
목적·사용법을 보여준다. steward 에 정적 목록을 박지 않는다 —
스크립트가 바뀌면(그것도 steward 가 conformance 로 바꿀 수 있다) 이 출력도 함께 바뀐다.
"""
import glob
import os
import re
import sys


def die(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)


def module_docstring(path):
    with open(path, encoding="utf-8") as f:
        m = re.search(r'"""(.*?)"""', f.read(), re.S)
    return m.group(1).strip() if m else ""


def skill_description(skill_md):
    if not os.path.isfile(skill_md):
        return ""
    with open(skill_md, encoding="utf-8") as f:
        for line in f:
            m = re.match(r"\s*description:\s*(.+)", line)
            if m:
                return m.group(1).strip().strip("\"'")
    return ""


def main():
    root = os.environ.get("OPS_WORKFLOW_ROOT")
    if not root:
        die("OPS_WORKFLOW_ROOT 미설정 — .claude/settings.local.json 을 확인하라.")
    skill_dirs = (sorted(glob.glob(os.path.join(root, ".claude", "skills", "*")))
                  + sorted(glob.glob(os.path.join(root, "harness", "*", ".claude", "skills", "*"))))

    print("ops-workflow 도구 지도 (라이브)  root=%s" % root)
    print("★ 아래 스크립트는 CWD 로 대상 repo 를 찾는다. 반드시 다음 래퍼로 실행한다:")
    print('    python3 "${CLAUDE_PROJECT_DIR}/.claude/skills/ops-tools/scripts/ops-run.py" '
          "<script 상대경로> [args]")
    print("  (또는 cwd=$OPS_WORKFLOW_ROOT). 절대경로로만 부르면 엉뚱한 repo 를 대상으로 삼는다.")
    print()

    for sd in skill_dirs:
        name = os.path.basename(sd)
        if name.startswith("_") or not os.path.isdir(sd):
            continue
        smd = os.path.join(sd, "SKILL.md")
        where = os.path.relpath(os.path.dirname(os.path.dirname(os.path.dirname(sd))), root)
        where = "공통" if where == "." else where
        print("## skill: %s (%s) — %s" % (name, where, skill_description(smd)))
        if os.path.isfile(smd):
            print("   SKILL.md: %s" % os.path.relpath(smd, root))
        scripts = sorted(glob.glob(os.path.join(sd, "scripts", "*.py"))
                         + glob.glob(os.path.join(sd, "scripts", "*.sh")))
        for script in scripts:
            base = os.path.basename(script)
            doc_lines = module_docstring(script).splitlines()
            purpose = doc_lines[0].strip() if doc_lines else ""
            rel = os.path.relpath(script, root)
            print("   - %s" % rel)
            print("       목적: %s" % purpose)
            usages = [ln.strip() for ln in doc_lines if base in ln and ln.strip() != purpose]
            for u in usages[:3]:
                print("       사용: %s" % u)
        print()

    print("## scripts: .claude/scripts (스킬 아님 — 생성물 재생성)")
    for script in sorted(glob.glob(os.path.join(root, ".claude", "scripts", "*.py"))):
        doc_lines = module_docstring(script).splitlines()
        print("   - %s" % os.path.relpath(script, root))
        print("       목적: %s" % (doc_lines[0].strip() if doc_lines else ""))
    print()
    print("판단 맥락(임계선·입도·why-only 등)이 필요하면 위 SKILL.md 를 읽는다.")
    print("⚠ 그 판단 규약은 **현행 정책**이다 — 기본으로 따르되, 정책 관리자로서 사용자와 함께")
    print("  재고할 수 있다. steward 의 법이 아니다 (CLAUDE.md §0).")


if __name__ == "__main__":
    main()
