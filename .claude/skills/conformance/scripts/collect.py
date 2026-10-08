#!/usr/bin/env python3
"""conformance 수집기 — 공표된 정책 ADR + 피관리 하네스 파일 인벤토리 + pilots 경로.

기준선은 accepted 가 아니다 — 정책 ADR은 proposed 가 현행 규범이다(ADR-0032). 그래서
origin/main 에 있는(공표된) 정책 ADR 전부(proposed·accepted)를 대조 대상으로 낸다.
superseded·rejected 는 "역행" 판정의 재료로 따로 낸다. 로컬에만 있는 ADR 은 아직 아무도 못 본
초안이라 전파 대상이 아니다 — 참고로만 보고한다.

피관리 하네스는 두 저장소: ops-workflow($OPS_WORKFLOW_ROOT — 규약·공통 .claude·harness/<역할>) ·
ticket-engineer($TICKET_ENGINEER_ROOT).
diff/판정은 agent가 수행한다.
"""
import os
import sys
import re
import json
import glob
import subprocess


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

    adr_rel = os.path.join("docs", "ops-workflow", "adr")
    adr_dir = os.path.join(root, adr_rel)

    # 공표된 사본(origin/main)을 읽는다 — adr-gate.py 와 같은 기준. fetch 실패는 경고로만.
    warnings = []
    fetched = subprocess.run(["git", "-C", root, "fetch", "-q", "origin", "main"],
                             capture_output=True, text=True)
    if fetched.returncode != 0:
        warnings.append("origin/main 을 당기지 못했다 — 로컬에 있는 마지막 사본으로 판단한다.")
    listed = subprocess.run(["git", "-C", root, "ls-tree", "--name-only", "origin/main", adr_rel + "/"],
                            capture_output=True, text=True)
    published_files = [ln for ln in listed.stdout.splitlines() if ln.endswith(".md")]

    published, dead = [], []
    for rel in published_files:
        shown = subprocess.run(["git", "-C", root, "show", "origin/main:" + rel],
                               capture_output=True, text=True)
        fm = parse_frontmatter(shown.stdout)
        entry = {"id": fm.get("id"), "status": fm.get("status"), "file": os.path.basename(rel),
                 "path": os.path.join(root, rel), "title": fm.get("title")}
        if fm.get("status") in ("proposed", "accepted"):
            published.append(entry)
        else:
            entry["superseded_by"] = fm.get("superseded_by")
            dead.append(entry)

    local_only = []
    if os.path.isdir(adr_dir):
        pub_names = {os.path.basename(r) for r in published_files}
        for path in sorted(glob.glob(os.path.join(adr_dir, "*.md"))):
            if os.path.basename(path) not in pub_names:
                with open(path, encoding="utf-8") as f:
                    fm = parse_frontmatter(f.read())
                local_only.append({"id": fm.get("id"), "file": os.path.basename(path), "status": fm.get("status")})

    ops_workflow = harness_inventory(root, [
        os.path.join(root, "CLAUDE.md"),
        os.path.join(root, ".claude", "rules", "*.md"),
        os.path.join(root, ".claude", "agents", "*.md"),
        os.path.join(root, ".claude", "skills", "*", "SKILL.md"),
        os.path.join(root, ".claude", "hooks", "*"),
        os.path.join(root, "harness", "*", "CLAUDE.md"),
        os.path.join(root, "harness", "*", ".claude", "skills", "*", "SKILL.md"),
    ])

    eng = os.environ.get("TICKET_ENGINEER_ROOT")
    ticket_engineer = None
    if eng and os.path.isdir(eng):
        ticket_engineer = harness_inventory(eng, [
            os.path.join(eng, "CLAUDE.md"),
            os.path.join(eng, ".claude", "rules", "*.md"),
            os.path.join(eng, ".claude", "agents", "*.md"),
            os.path.join(eng, ".claude", "skills", "*", "SKILL.md"),
            os.path.join(eng, ".claude", "hooks", "*"),
        ])

    pilots_path = os.path.join(steward_root(), "pilots.md")
    pilots_present = os.path.isfile(pilots_path)

    out = {
        "ops_root": root,
        "published_ref": "origin/main",
        "warnings": warnings,
        "published_adrs": published,
        "published_count": len(published),
        "dead_adrs": dead,
        "local_only_adrs": local_only,
        "harnesses": {
            "ops-workflow": {"root": root, "files": ops_workflow},
            "ticket-engineer": (
                {"root": eng, "files": ticket_engineer}
                if ticket_engineer is not None
                else {"root": eng, "files": None,
                      "note": "TICKET_ENGINEER_ROOT 미설정이거나 경로가 없다 — 이 하네스는 이번 감사에서 빠진다."}
            ),
        },
        "pilots_path": pilots_path,
        "pilots_present": pilots_present,
        "note": "published_adrs(proposed·accepted) 가 대조 기준선이다 — 정책 ADR 은 proposed 가 현행 규범(ADR-0032). "
                "dead_adrs(superseded·rejected) 는 하네스가 아직 그것을 따르는지(역행) 보는 재료. "
                "각 ADR 이 어느 하네스를 구속하는지 매핑한 뒤 대조하는 판정은 agent 가 SKILL.md 기준으로 수행한다. "
                "pilots.md 는 어느 ADR 의 델타가 어디 들어갔는지의 롤백 원장 — 대조의 출발점이다.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
