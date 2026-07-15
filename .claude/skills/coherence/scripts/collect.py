#!/usr/bin/env python3
"""coherence 수집기 — ADR 인벤토리 + 참조 그래프 + 후보 충돌 쌍.

수집만 한다. 충돌 판정은 agent가 SKILL.md 기준으로 본문을 읽어 수행한다.
대상 경로는 env var OPS_WORKFLOW_ROOT 로 주입된다(하드코딩 없음).
표준 라이브러리만 사용(PyYAML 미사용) — ops-workflow 파서 제약과 정합.
"""
import os
import sys
import re
import json
import glob
import itertools


def die(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False))
    sys.exit(1)


def parse_frontmatter(text):
    """--- ... --- 사이 YAML 서브셋 파싱(스칼라·인라인리스트·블록리스트)."""
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
                data[key] = []  # 블록 리스트 가능
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


def first_h1(text):
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def main():
    root = os.environ.get("OPS_WORKFLOW_ROOT")
    if not root:
        die("OPS_WORKFLOW_ROOT env var가 없다. .claude/settings.local.json 을 확인하라.")
    adr_dir = os.path.join(root, "docs", "ops-workflow", "adr")
    if not os.path.isdir(adr_dir):
        die("ADR 디렉터리 없음: %s" % adr_dir)

    docs = []
    for path in sorted(glob.glob(os.path.join(adr_dir, "*.md"))):
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fm = parse_frontmatter(text)
        docs.append({
            "id": fm.get("id"),
            "file": os.path.basename(path),
            "path": path,
            "title": fm.get("title") or first_h1(text),
            "status": fm.get("status"),
            "topic": fm.get("topic"),
            "subjects": as_list(fm.get("subjects")),
            "parent": fm.get("parent"),
            "references": as_list(fm.get("references")),
            "superseded_by": as_list(fm.get("superseded_by")),
        })

    def key(d):
        return d["id"] or d["file"]

    # 후보 쌍 = 우선 검토 대상. topic 은 신호로 쓰지 않는다 —
    # 정책 ADR은 전부 topic=ops-workflow 라 상수이며 아무것도 좁히지 못한다.
    # 유효 신호: subjects 공유 · parent/reference 링크.
    pairs = []
    for a, b in itertools.combinations(docs, 2):
        reasons = []
        shared = sorted(set(a["subjects"]) & set(b["subjects"]))
        if shared:
            reasons.append("subjects:%s" % shared)
        if b["id"] and (b["id"] == a["parent"] or b["id"] in a["references"]):
            reasons.append("%s->%s link" % (key(a), key(b)))
        if a["id"] and (a["id"] == b["parent"] or a["id"] in b["references"]):
            reasons.append("%s->%s link" % (key(b), key(a)))
        if reasons:
            pairs.append({"a": key(a), "b": key(b), "reasons": reasons})

    statuses = sorted({d["status"] for d in docs if d["status"]})
    out = {
        "adr_dir": adr_dir,
        "count": len(docs),
        "by_status": {s: [key(d) for d in docs if d["status"] == s] for s in statuses},
        "inventory": docs,
        "candidate_pairs": pairs,
        "note": "candidate_pairs 는 우선 검토 대상일 뿐이다. 충돌 판정은 SKILL.md 기준으로 "
                "agent 가 본문을 읽어 수행한다. 후보에 없는 쌍도 전수 확인을 권장한다.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
