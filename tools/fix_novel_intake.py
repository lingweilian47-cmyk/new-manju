#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "short-drama-director"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text("utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"anchor missing: {path}: {old[:120]}")
    path.write_text(text.replace(old, new, 1), "utf-8")


skill = PLUGIN / "SKILL.md"
replace_once(
    skill,
    "- 用户明确提供小说并要求转剧本时，先读取指定范围，输出一张**最低理解与需求确认卡**，让用户纠正事件链、知情差、梗义和参考世界观；未确认前不直接改写。",
    "- 用户明确提供小说并要求转剧本时，先读取指定范围，输出一张**最低理解与需求确认卡**，让用户纠正事件链、知情差、梗义和参考世界观；未确认前不直接改写。该确认卡属于**只读入场校准**，不是创作：即使 A/B 尚未锁定，也允许先读原文并在同一张卡中一并询问 P0 参数；真正补齐与剧本写作必须等 A/B 锁定后开始。",
)

novel = PLUGIN / "references" / "novel-to-screenplay-adapter.md"
replace_once(
    novel,
    "收到小说后，先读取用户指定范围与理解该范围所必需的前后文，再输出一张简短确认卡。禁止让用户在模型尚未阅读原文时填写空白问卷。",
    "收到小说后，先读取用户指定范围与理解该范围所必需的前后文，再输出一张简短确认卡。禁止让用户在模型尚未阅读原文时填写空白问卷。**阅读原文与输出确认卡属于只读入场校准，可在模型版本／画幅尚未锁定时执行；应在同一张卡中补问缺失的 P0 参数，真正补齐与剧本写作必须等 P0 锁定后开始。**",
)
replace_once(
    novel,
    "叙事方式与文本特点：",
    "叙事方式、原文写法与文本逻辑：",
)
replace_once(
    novel,
    "- P0 尚未锁定的模型版本、画幅与交付形态。",
    "- P0 尚未锁定的平台、模型版本、画幅、视觉风格、目标时长与交付形态。",
)

wrapper = PLUGIN / "skills" / "new-manju-workflow" / "SKILL.md"
replace_once(
    wrapper,
    "1. 先执行 P0 参数锁定，并阅读用户指定范围与必要前后文；\n2. 前台先输出一张简短的【小说理解与需求确认】卡，说明事件链、人物直接目的、身份／知情差、可能涉及的梗与世界观、不确定项和预计只补的缺口；",
    "1. 先阅读用户指定范围与必要前后文；这一步是只读入场校准，即使 P0 尚未锁定也可以执行；\n2. 前台先输出一张简短的【小说理解与需求确认】卡，说明原文写法逻辑、事件链、人物直接目的、身份／知情差、可能涉及的梗与世界观、不确定项和预计只补的缺口，并在同一张卡中补齐平台、模型、画幅、风格、时长与交付形态；",
)
replace_once(
    wrapper,
    "3. 等用户补充或纠正需求、倾向、必须保留、禁止改动、梗知识、参考世界观与分集偏好；",
    "3. 等用户补充或纠正需求、倾向、必须保留、禁止改动、梗知识、参考世界观与分集偏好，并完成 P0 锁定；",
)

check_path = PLUGIN / "scripts" / "check_package.py"
replace_once(
    check_path,
    '    "最低理解与需求确认",\n',
    '    "最低理解与需求确认",\n    "只读入场校准",\n',
)

print("Novel intake preflight clarified.")
