#!/usr/bin/env python3
"""ops-run — ops-workflow 스크립트를 올바른 cwd($OPS_WORKFLOW_ROOT)로 실행하는 래퍼.

  ops-run.py .claude/skills/adr/scripts/next-id.py [args...]

왜 필요한가: ops-workflow 스크립트는 대상 repo 를 **CWD 에서 .git 을 위로 탐색**해 찾는다
(_lib/opsdoc.repo_root). steward 는 자기 repo(별도 .git)가 cwd 이므로, 절대경로로만
호출하면 스크립트가 **steward repo 를 대상으로 오작동**한다. 이 래퍼가 cwd 를 대상 repo 로
바꿔 그 실수를 원천 차단한다.
"""
import os
import runpy
import sys

root = os.environ.get("OPS_WORKFLOW_ROOT")
if not root:
    sys.exit("OPS_WORKFLOW_ROOT 미설정 — .claude/settings.local.json 을 확인하라.")
if not os.path.isdir(root):
    sys.exit("OPS_WORKFLOW_ROOT 경로가 없다: %s" % root)
if len(sys.argv) < 2:
    sys.exit("usage: ops-run.py <ops-repo 기준 상대경로 script.py> [args...]")

rel = sys.argv[1]
target = rel if os.path.isabs(rel) else os.path.join(root, rel)
if not os.path.isfile(target):
    sys.exit("대상 스크립트가 없다: %s" % target)

os.chdir(root)                       # ★ repo_root 가 여기서 ops-workflow 의 .git 을 찾는다
sys.argv = [target] + sys.argv[2:]   # 대상 스크립트가 자기 인자를 그대로 보도록
runpy.run_path(target, run_name="__main__")
