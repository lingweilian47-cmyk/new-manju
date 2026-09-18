#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New Manju 包级静态自检。"""
from __future__ import annotations

from pathlib import Path
import hashlib
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(name: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    if not condition:
        FAILURES.append(name)


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


expected_core = {
    "SKILL.md": "2a2947e2f281ad96fd836db58d8b5f774284c958",
    "references/agent-platform-adapters.md": "4a265c7f624ece4f97519e51053466829bc1fe69",
    "references/asset-first-pipeline.md": "28858c752abf3a03d3330a90a3c22882ddfd2192",
    "references/model-adapters.md": "3f02418e6f2a42e031f05112878926612327e472",
    "references/quality-gate-review.md": "f2a6397e4bc3c6740ce8dae1955426330756e717",
    "references/screenplay-gate-engine.md": "5f22ee784689513c69434c3dad70445875cdeefd",
    "references/seedance-render-engine.md": "289f94853d289a0401d5815e57b1eee40f91c6f3",
    "references/★ prompt-feeding-checklist.md": "6ea09c83f64ea8a1c9e24ef78db7063d8c44f44d",
}

for relative, expected in expected_core.items():
    path = BASE / relative
    check(f"upstream core exact: {relative}", path.is_file() and git_blob_sha(path) == expected)

refs = list((BASE / "references").rglob("*.md"))
check("38 reference files", len(refs) == 38)
check("novel-entry removed", not (BASE / "references" / "novel-entry").exists())

wrapper_path = BASE / "skills" / "new-manju-workflow" / "SKILL.md"
wrapper = wrapper_path.read_text("utf-8")
check("wrapper delegates to root", "../../SKILL.md" in wrapper and "不新增阶段" in wrapper)
check("wrapper preserves P0", "P0 前置锁定" in wrapper)

operational_files = [BASE / "SKILL.md", wrapper_path, *refs]
operational_text = "\n".join(path.read_text("utf-8") for path in operational_files)
forbidden_routes = [
    "S1 原作影视化母稿",
    "S2 抖音版单集事件稿",
    "S3 基础分镜方案",
    "P1-N",
    "novel-entry/",
    "小说漫剧已改编入口",
]
check("no old novel route in operational core", all(term not in operational_text for term in forbidden_routes))

for path in [BASE / "plugin.json", BASE / ".codex-plugin" / "plugin.json"]:
    data = json.loads(path.read_text("utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    check(f"manifest {path} has no frozen stages", all(term not in blob for term in ["S1", "S2", "S3", "小说三阶段", "基础分镜方案"]))

validator = subprocess.run(
    [sys.executable, str(BASE / "scripts" / "validate_prompt.py"), "--self-test"],
    capture_output=True,
    text=True,
)
check("validator self-test", validator.returncode == 0)
if validator.returncode != 0:
    print(validator.stdout)
    print(validator.stderr)

print("FAILED", FAILURES if FAILURES else "none")
sys.exit(1 if FAILURES else 0)
