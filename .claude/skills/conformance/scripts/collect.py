#!/usr/bin/env python3
"""conformance 수집기 — accepted ADR + 피관리 하네스 파일 인벤토리 + pilots 로드.

피관리 하네스는 둘: docs-tickets($OPS_WORKFLOW_ROOT) · ticket-engineer($TICKET_ENGINEER_ROOT).
diff/판정은 agent가 수행한다.
"""
import os
import sys
import re
import json
import glob


def die(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(1)


def parse_frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = {}
    key = None
    for line in text[3:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                data[key] = []
            elif val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                data[key] = [x.strip().strip("\"'") for x in inner.split(",") if x.strip()]
            else:
                data[key] = val.strip().strip("\"'")
        else:
            m2 = re.match(r"^\s*-\s*(.+)$", line)
            if m2 and key is not None and isinstance(data.get(key), list):
                data[key].append(m2.group(1).strip().strip("\"'"))
    return data


def steward_root():
    r = os.environ.get("CLAUDE_PROJECT_DIR")
    if r:
        return r
    # .claude/skills/conformance/scripts/collect.py → repo root
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


def harness_inventory(root, patterns):
    files = []
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            files.append({"path": p, "bytes": os.path.getsize(p)})
    return files


def main():
    root = os.environ.get("OPS_WORKFLOW_ROOT")
    if not root:
        die("OPS_WORKFLOW_ROOT env var가 없다. .claude/settings.local.json 을 확인하라.")

    adr_dir = os.path.join(root, "docs", "ops-workflow", "adr")
    accepted = []
    if os.path.isdir(adr_dir):
        for path in sorted(glob.glob(os.path.join(adr_dir, "*.md"))):
            with open(path, encoding="utf-8") as f:
                fm = parse_frontmatter(f.read())
            if fm.get("status") == "accepted":
                accepted.append({
                    "id": fm.get("id"),
                    "file": os.path.basename(path),
                    "path": path,
                    "title": fm.get("title"),
                })

    docs_tickets = harness_inventory(root, [
        os.path.join(root, "CLAUDE.md"),
        os.path.join(root, ".claude", "agents", "*.md"),
        os.path.join(root, ".claude", "skills", "*", "SKILL.md"),
    ])

    eng = os.environ.get("TICKET_ENGINEER_ROOT")
    ticket_engineer = None
    if eng and os.path.isdir(eng):
        ticket_engineer = harness_inventory(eng, [
            os.path.join(eng, "CLAUDE.md"),
            os.path.join(eng, ".claude", "agents", "*.md"),
            os.path.join(eng, ".claude", "skills", "*", "SKILL.md"),
            os.path.join(eng, ".claude", "hooks", "*"),
        ])

    pilots_path = os.path.join(steward_root(), "pilots.md")
    pilots_present = os.path.isfile(pilots_path)

    out = {
        "ops_root": root,
        "accepted_adrs": accepted,
        "accepted_count": len(accepted),
        "harnesses": {
            "docs-tickets": {"root": root, "files": docs_tickets},
            "ticket-engineer": (
                {"root": eng, "files": ticket_engineer}
                if ticket_engineer is not None
                else {"root": eng, "files": None,
                      "note": "TICKET_ENGINEER_ROOT 미설정이거나 경로가 없다 — 이 하네스는 이번 감사에서 빠진다."}
            ),
        },
        "pilots_path": pilots_path,
        "pilots_present": pilots_present,
        "note": "accepted_adrs 가 0건이면 아직 전파할 대상이 없다(정상). "
                "각 accepted ADR이 어느 하네스를 구속하는지 매핑한 뒤 대조하는 판정은 "
                "agent 가 SKILL.md 기준으로 수행한다. "
                "pilots.md 의 파일럿 델타는 정합성 검사에서 제외한다.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
