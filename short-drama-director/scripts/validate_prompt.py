#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Seedance 七段式提示词结构自检。

默认使用原版标准时间轴。只有项目合同或用户明确要求最终提示词不写时间码时，
才使用 ``--profile no-timecode``。该 profile 只是输出校验模式，不是独立生产入口。
"""
from __future__ import annotations

from collections import Counter
import json
import re
import sys
from pathlib import Path
from typing import Iterable

LIMITS = {"2.5": 30.0, "2.0": 15.0}
SECTIONS = [
    "【画幅风格】",
    "【场景资产】",
    "【核心人物】",
    "【站位声明】",
    "【时间轴分镜】",
    "【音效】",
    "【强制禁止项】",
]
TIME_RANGE_RE = re.compile(
    r"(?:(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?|(?<!\w)(\d+(?:\.\d+)?)\s*s?)"
    r"\s*[-~～→]\s*"
    r"(?:(\d{1,2}):(\d{2})(?:[.:](\d{1,2}))?|(?<!\w)(\d+(?:\.\d+)?)\s*s?)",
    re.I,
)
EXPLICIT_SECONDS_RE = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:秒|s\b)", re.I)
BEAT_COUNT_RE = re.compile(r"(?:停顿|保持|停留)\s*[一二三四五六七八九十两0-9]+\s*拍")
HIGH_RISK = [
    "鲜血", "血喷", "血肉模糊", "喷血", "断肢", "断臂", "断头", "碎尸",
    "内脏", "脑浆", "割喉", "虐杀", "凌迟", "开膛破肚", "裸体", "露点",
    "床戏", "自杀", "自残", "割腕", "上吊", "吸毒",
]


def _seconds(groups: tuple[str | None, ...], offset: int) -> float:
    minute, second, fraction, plain = groups[offset:offset + 4]
    if plain is not None:
        return float(plain)
    return int(minute or 0) * 60 + int(second or 0) + int(fraction or 0) / 100


def ranges(text: str) -> list[tuple[float, float, int]]:
    found: list[tuple[float, float, int]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        for match in TIME_RANGE_RE.finditer(line):
            groups = match.groups()
            found.append((_seconds(groups, 0), _seconds(groups, 4), line_no))
    return found


def section(text: str, heading: str, next_headings: Iterable[str]) -> str:
    start = text.find(heading)
    if start < 0:
        return ""
    start += len(heading)
    ends = [text.find(item, start) for item in next_headings]
    ends = [item for item in ends if item >= 0]
    return text[start:min(ends) if ends else len(text)]


def shared_checks(text: str, model: str, issues: list[str], warnings: list[str]) -> None:
    style = section(text, "【画幅风格】", ["【场景资产】"])
    if not re.search(r"aspect_ratio\s*=", text) and not re.search(r"16:9|9:16|21:9|1:1", style):
        issues.append("C6 缺少画幅声明")

    missing = [item for item in SECTIONS if item not in text]
    if missing:
        issues.append(f"C7 七段式缺栏：{missing}")
    else:
        positions = [text.index(item) for item in SECTIONS]
        if positions != sorted(positions):
            issues.append("C7 七段式段序错误")

    if "【时间轴分镜】" in text and "【接续状态】" not in text:
        issues.append("C11 缺少【接续状态】")

    if model == "2.0" and re.search(r"首尾帧|first_frame|last_frame|first_last_frame", text, re.I):
        issues.append("C8 Seedance 2.0 禁用首尾帧")

    risky = [word for word in HIGH_RISK if word in text]
    if risky:
        issues.append(f"C9 平台高危词：{risky}")


def rhythm_check(time_ranges: list[tuple[float, float, int]], warnings: list[str]) -> None:
    durations = [round(end - start, 2) for start, end, _ in time_ranges if end > start]
    if len(durations) < 4:
        return
    common_duration, count = Counter(durations).most_common(1)[0]
    if count / len(durations) >= 0.70:
        warnings.append(
            f"C13 镜长雷同风险：{common_duration:g}s 占 {count}/{len(durations)}，请由剧情倒推快慢节奏"
        )


def validate_standard(text: str, model: str) -> tuple[list[str], list[str], dict[str, object]]:
    issues: list[str] = []
    warnings: list[str] = []
    time_ranges = ranges(text)
    duration = max((end for _, end, _ in time_ranges), default=0.0)

    if not time_ranges:
        warnings.append("C1-C3 未识别时间轴")
    else:
        if duration > LIMITS[model] + 0.01:
            issues.append(f"C1 总时长 {duration:g}s 超过模型上限 {LIMITS[model]:g}s")
        previous_end = -1.0
        for start, end, line_no in time_ranges:
            if end <= start:
                issues.append(f"C3 第 {line_no} 行时间倒挂")
                continue
            if start < previous_end:
                issues.append(f"C3 第 {line_no} 行时间重叠或回退")
            previous_end = max(previous_end, end)
            shot_length = end - start
            if shot_length < 3:
                warnings.append(f"C2 第 {line_no} 行碎切风险：{shot_length:g}s")
            if shot_length > 6:
                warnings.append(f"C10 第 {line_no} 行长镜风险：{shot_length:g}s")
        rhythm_check(time_ranges, warnings)

    if len(text) > 4500:
        issues.append(f"C4 字符数 {len(text)} 超出建议预算")
    shared_checks(text, model, issues, warnings)
    return issues, warnings, {
        "profile": "standard",
        "duration_s": duration,
        "shots": len(time_ranges),
        "chars": len(text),
    }


def validate_no_timecode(text: str, model: str) -> tuple[list[str], list[str], dict[str, object]]:
    issues: list[str] = []
    warnings: list[str] = []
    shared_checks(text, model, issues, warnings)

    time_ranges = ranges(text)
    seconds = [
        (match.group(0), text[:match.start()].count("\n") + 1)
        for match in EXPLICIT_SECONDS_RE.finditer(text)
    ]
    beats = [
        (match.group(0), text[:match.start()].count("\n") + 1)
        for match in BEAT_COUNT_RE.finditer(text)
    ]
    if time_ranges:
        issues.append(f"N1 禁止时间码：发现 {len(time_ranges)} 处")
    if seconds:
        issues.append("N1 禁止数字秒数：" + ", ".join(f"第{line}行 {value}" for value, line in seconds[:5]))
    if beats:
        issues.append("N1 禁止数字拍数：" + ", ".join(f"第{line}行 {value}" for value, line in beats[:5]))
    if len(text) > 8000:
        issues.append(f"N2 字符数 {len(text)} 超出硬上限")
    elif len(text) > 4500:
        warnings.append(f"N2 字符数 {len(text)} 超出建议清洁线")

    shots = len(re.findall(r"\[镜头\s*\d+\]", text))
    if shots == 0:
        warnings.append("N3 未识别镜头编号；请确认分镜顺序可读")
    return issues, warnings, {
        "profile": "no-timecode",
        "duration_s": None,
        "shots": shots,
        "chars": len(text),
    }


def validate(text: str, model: str, profile: str):
    if model not in LIMITS:
        raise ValueError(f"不支持的模型版本：{model}")
    if profile == "no-timecode":
        return validate_no_timecode(text, model)
    if profile != "standard":
        raise ValueError(f"不支持的 profile：{profile}")
    return validate_standard(text, model)


def self_test() -> int:
    standard = """【画幅风格】
16:9 横屏，Seedance 2.5。
【场景资产】
服装店。
【核心人物】
白厄、千仞雪。
【站位声明】
白厄在画面右侧柜台内，千仞雪在左侧柜台外。
【时间轴分镜】
00:00-00:04 白厄展开衣服。
00:04-00:08 千仞雪接过衣袋。
【接续状态】
千仞雪持有衣袋。
【音效】
布料声。
【强制禁止项】
禁止新增人物。
"""
    issues, _, _ = validate(standard, "2.5", "standard")
    if issues:
        print("FAIL standard", issues)
        return 1

    no_timecode = standard.replace("00:00-00:04 ", "[镜头1] ").replace("00:04-00:08 ", "[镜头2] ")
    issues, _, _ = validate(no_timecode, "2.5", "no-timecode")
    if issues:
        print("FAIL no-timecode", issues)
        return 1

    bad = no_timecode.replace("[镜头1]", "3秒 [镜头1]")
    issues, _, _ = validate(bad, "2.5", "no-timecode")
    if not any("N1" in item for item in issues):
        print("FAIL no-timecode detection")
        return 1

    print("[+] self-test PASSED")
    return 0


def main() -> None:
    args = sys.argv[1:]
    if "--self-test" in args:
        raise SystemExit(self_test())

    positional = [item for item in args if not item.startswith("-")]
    if not positional:
        print(__doc__)
        raise SystemExit(2)

    def option(name: str, default: str) -> str:
        if name not in args:
            return default
        index = args.index(name)
        if index + 1 >= len(args):
            raise ValueError(f"{name} 缺少参数")
        return args[index + 1]

    model = option("--model", "2.5")
    profile = option("--profile", "standard")
    text = Path(positional[0]).read_text("utf-8")
    issues, warnings, stats = validate(text, model, profile)

    if "--json" in args:
        print(json.dumps({"issues": issues, "warnings": warnings, "stats": stats}, ensure_ascii=False, indent=2))
    else:
        print(f"[+] profile={profile} model={model} shots={stats['shots']} chars={stats['chars']}")
        for warning in warnings:
            print("[!] WARN:", warning)
        for issue in issues:
            print("[-] FAIL:", issue)
        print("[+] PASSED" if not issues else f"[-] {len(issues)} error(s)")

    raise SystemExit(1 if issues else 0)


if __name__ == "__main__":
    main()
