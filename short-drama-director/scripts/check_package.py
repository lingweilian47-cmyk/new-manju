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


expected_unchanged = {
    "references/model-adapters.md": "3f02418e6f2a42e031f05112878926612327e472",
    "references/quality-gate-review.md": "f2a6397e4bc3c6740ce8dae1955426330756e717",
    "references/seedance-render-engine.md": "289f94853d289a0401d5815e57b1eee40f91c6f3",
    "references/★ prompt-feeding-checklist.md": "6ea09c83f64ea8a1c9e24ef78db7063d8c44f44d",
}
for relative, expected in expected_unchanged.items():
    path = BASE / relative
    check(f"upstream preserved: {relative}", path.is_file() and git_blob_sha(path) == expected)

refs = list((BASE / "references").rglob("*.md"))
novel_ref = BASE / "references" / "novel-to-screenplay-adapter.md"
check("39 reference files", len(refs) == 39)
check("old novel-entry directory absent", not (BASE / "references" / "novel-entry").exists())
check("P1 novel adapter exists", novel_ref.is_file())

novel_text = novel_ref.read_text("utf-8") if novel_ref.is_file() else ""
for phrase in [
    "原文是主体，补充是补丁",
    "世界观是只读词典",
    "最低理解与需求确认",
    "只读入场校准",
    "N0｜重写倾向检查",
    "N1｜原作保真检查",
    "N2｜生产连续性检查",
    "P2 从剧本提取角色",
]:
    check(f"novel adapter contract: {phrase}", phrase in novel_text)

skill_path = BASE / "SKILL.md"
skill = skill_path.read_text("utf-8")
check("root routes /小说转剧本", "/小说转剧本" in skill)
check("root indexes novel adapter", "├── ★ novel-to-screenplay-adapter.md" in skill)
check("root keeps novel mode inside P1", "P1 原文补丁模式" in skill and "不新增下游阶段" in skill)

screenplay = (BASE / "references" / "screenplay-gate-engine.md").read_text("utf-8")
check("screenplay gate has three-way P1 routing", "P1 输入路由：原创、小说与现成剧本三路收口" in screenplay)
check("novel mode does not force 100s structure", "不自动强制小说模式" in screenplay)

asset = (BASE / "references" / "asset-first-pipeline.md").read_text("utf-8")
check("asset pipeline converges P1 inputs", "P1 输入收口规则" in asset and "小说最小增量适配" in asset)
check("P2-P5 authority preserved", "P3 仍由 Work 自行提取、选择、合并和拆分镜头" in asset)

wrapper_path = BASE / "skills" / "new-manju-workflow" / "SKILL.md"
wrapper = wrapper_path.read_text("utf-8")
check("wrapper delegates to root", "../../SKILL.md" in wrapper)
check("wrapper preserves P0", "P0 参数锁定" in wrapper or "P0 前置锁定" in wrapper)
check("wrapper routes novel inside P1", "P1 小说输入模式" in wrapper and "原文是主体，补充是补丁" in wrapper)

operational_files = [skill_path, wrapper_path, *refs]
operational_text = "\n".join(path.read_text("utf-8") for path in operational_files)
forbidden_routes = [
    "S1 原作影视化母稿",
    "S2 抖音版单集事件稿",
    "S3 基础分镜方案",
    "P1-N",
    "novel-entry/",
    "小说漫剧已改编入口",
]
check("no old frozen novel route", all(term not in operational_text for term in forbidden_routes))

for path in [BASE / "plugin.json", BASE / ".codex-plugin" / "plugin.json"]:
    data = json.loads(path.read_text("utf-8"))
    blob = json.dumps(data, ensure_ascii=False)
    check(f"manifest {path.name} version 6.9.3", data.get("version") == "6.9.3")
    check(f"manifest {path.name} exposes novel prompt", "小说" in blob and "最低理解" in blob)
    check(f"manifest {path.name} has no frozen stages", all(term not in blob for term in ["S1", "S2", "S3", "小说三阶段", "基础分镜方案"]))

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
