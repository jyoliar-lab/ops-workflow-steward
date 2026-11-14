#!/usr/bin/env python3
"""list-memory — 피관리 하네스의 Claude Code 메모리를 그 자리에서 읽어 보여준다.

  list-memory.py            # 두 하네스 전부
  list-memory.py --paths    # 메모리 디렉터리 경로만

메모리 디렉터리는 ~/.claude/projects/<슬러그>/memory 이고, 슬러그는 저장소 루트
절대경로의 영숫자 외 문자를 '-'로 바꾼 것이다. 저장소 루트는 env var
OPS_WORKFLOW_ROOT · TICKET_ENGINEER_ROOT 로 온다.

항목 본문과 함께 색인(MEMORY.md)의 어긋남 — 파일 없는 포인터, 색인에 없는 파일 — 을 낸다.
"""
import os
import re
import sys
from dataclasses import dataclass, field

HARNESS_ENV: dict[str, str] = {
    "ops-workflow": "OPS_WORKFLOW_ROOT",
    "ticket-engineer": "TICKET_ENGINEER_ROOT",
}
INDEX_NAME: str = "MEMORY.md"
POINTER_RE: re.Pattern[str] = re.compile(r"\]\(([^)]+\.md)\)")


@dataclass
class Entry:
    filename: str
    name: str
    description: str
    type: str
    body: str
    indexed: bool


@dataclass
class Memory:
    harness: str
    directory: str
    exists: bool
    entries: list[Entry] = field(default_factory=list)
    dangling: list[str] = field(default_factory=list)  # 색인이 가리키지만 파일이 없다


def memory_dir(root: str) -> str:
    config: str = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    slug: str = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))
    return os.path.join(config, "projects", slug, "memory")


def front_value(front: str, key: str) -> str:
    m: re.Match[str] | None = re.search(r"^\s*%s:\s*(.*)$" % re.escape(key), front, re.M)
    return m.group(1).strip() if m else ""


def read_entry(path: str, indexed: bool) -> Entry:
    with open(path, encoding="utf-8") as f:
        text: str = f.read()
    front: str = ""
    body: str = text
    m: re.Match[str] | None = re.match(r"^---\n(.*?)\n---\n?(.*)$", text, re.S)
    if m:
        front, body = m.group(1), m.group(2)
    return Entry(
        filename=os.path.basename(path),
        name=front_value(front, "name"),
        description=front_value(front, "description"),
        type=front_value(front, "type"),
        body=body.strip(),
        indexed=indexed,
    )


def load(harness: str, root: str) -> Memory:
    directory: str = memory_dir(root)
    mem: Memory = Memory(harness=harness, directory=directory, exists=os.path.isdir(directory))
    if not mem.exists:
        return mem
    pointers: list[str] = []
    index_path: str = os.path.join(directory, INDEX_NAME)
    if os.path.isfile(index_path):
        with open(index_path, encoding="utf-8") as f:
            pointers = POINTER_RE.findall(f.read())
    files: list[str] = sorted(
        n for n in os.listdir(directory) if n.endswith(".md") and n != INDEX_NAME
    )
    mem.entries = [read_entry(os.path.join(directory, n), n in pointers) for n in files]
    mem.dangling = [p for p in pointers if p not in files]
    return mem


def render(mem: Memory) -> str:
    out: list[str] = ["# %s — %s" % (mem.harness, mem.directory)]
    if not mem.exists:
        out.append("(메모리 디렉터리 없음)")
        return "\n".join(out)
    if not mem.entries and not mem.dangling:
        out.append("(항목 없음)")
    for e in mem.entries:
        out.append("")
        out.append("## %s  [type: %s]%s" % (e.filename, e.type or "?", "" if e.indexed else "  ★ 색인에 없음"))
        if e.description:
            out.append("> %s" % e.description)
        out.append(e.body)
    for p in mem.dangling:
        out.append("")
        out.append("## %s  ★ 색인만 있고 파일 없음" % p)
    return "\n".join(out)


def main() -> None:
    paths_only: bool = "--paths" in sys.argv[1:]
    blocks: list[str] = []
    for harness, env in HARNESS_ENV.items():
        root: str | None = os.environ.get(env)
        if not root:
            sys.exit("%s 미설정 — .claude/settings.local.json 을 확인하라." % env)
        if paths_only:
            blocks.append("%s\t%s" % (harness, memory_dir(root)))
        else:
            blocks.append(render(load(harness, root)))
    print(("\n" if paths_only else "\n\n").join(blocks))


if __name__ == "__main__":
    main()
