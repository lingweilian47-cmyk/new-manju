#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""New Manju 包级静态自检。"""
from __future__ import annotations

from pathlib import Path
import json
import subprocess
import sys

BASE = Path(__file__).resolve().parent.parent
FAILURES: list[str] = []


def check(name: str, condition: bool) -> None:
    print(f"[{'PASS' if condition else 'FAIL'}] {name}")
    if not condition:
        FAILURES.append(name)


skill = (BASE / "SKILL.md").read_text("utf-8")
check("V6.8 core skill", "V6.8 轻量版" in skill)
check("no S1/S2/S3 route in core", all(x not in skill for x in ["S1 原作影视化母稿", "S2 抖音版单集事件稿", "S3 基础分镜方案", "P1-N"]))

refs = list((BASE / "references").rglob("*.md"))
check("38 reference files", len(refs) == 38)
check("novel-entry removed", not (BASE / "references" / "novel-entry").exists())

wrapper = (BASE / "skills" / "new-manju-workflow" / "SKILL.md").read_text("utf-8")
check("wrapper delegates to root", "../../SKILL.md" in wrapper and "不新增阶段" in wrapper)
check("wrapper has no novel stage", all(x not in wrapper for x in ["原作影视化母稿", "抖音版单集事件稿", "基础分镜方案", "P1-N"]))

for path in [BASE / "plugin.json", BASE / ".codex-plugin" / "plugin.json"]:
    data = json.loads(path.read_text("utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    check(f"manifest {path.name} no frozen stages", all(x not in blob for x in ["S1", "S2", "S3", "小说三阶段"]))

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
