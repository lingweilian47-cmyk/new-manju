#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "short-drama-director"


def read(path: Path) -> str:
    return path.read_text("utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, "utf-8")


def insert_before_once(path: Path, anchor: str, block: str, sentinel: str) -> None:
    text = read(path)
    if sentinel in text:
        return
    if anchor not in text:
        raise RuntimeError(f"anchor missing in {path}: {anchor[:100]}")
    write(path, text.replace(anchor, block + anchor, 1))


def insert_after_once(path: Path, anchor: str, block: str, sentinel: str) -> None:
    text = read(path)
    if sentinel in text:
        return
    if anchor not in text:
        raise RuntimeError(f"anchor missing in {path}: {anchor[:100]}")
    write(path, text.replace(anchor, anchor + block, 1))


def replace_once(path: Path, old: str, new: str) -> None:
    text = read(path)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"replacement anchor missing in {path}: {old[:120]}")
    write(path, text.replace(old, new, 1))


novel_reference = r'''# 小说原文最小增量补齐与专业剧本转写规范 (Novel-to-Screenplay Adapter)

本规范是 **P1 剧本阶段的一种输入模式**，用于把用户提供的小说原文转换为原管线可继续生产的标准专业剧本页。它不是新的 P0~P5 流程，也不建立小说专用下游入口。

核心公式：

```text
原文 = 主体
补充 = 补丁
梗知识／参考世界观 = 只读理解词典
最终产物 = 标准专业生产剧本
后续 = 原版 P2 → P3 → P4 → P5
```

> **最高规则：原文是主体，补充是补丁。只补原剧情中尚不能连续、明确落成画面的硬缺口，不重写已经成立的原文，不替作者重新设计故事。**

---

## 〇、 模式定位与触发边界

1. 仅在用户明确提出 `/小说转剧本`、`把这本小说转成专业剧本`、`按原剧情补齐后做成剧本` 等需求时触发。
2. 用户只是要求阅读、总结、分析、续写或讨论小说时，不得自动进入本模式。
3. 本模式只负责完成 P1：`小说原文 → 最小增量补齐 → 标准专业剧本`。
4. 专业剧本通过自检后，直接视为原管线 P1 已完成，从 P2 实体与资产提取继续。
5. 不建立 S1／S2／S3、冻结母稿、小说导入包、上游基础分镜或任何平行工作流。
6. 不因小说来自同人、跨作品或网络梗题材，就自动扩大改写权限。

---

## 一、 收到小说后的第一轮动作：先校准理解，不直接动笔

### 1. 必须先读再问

收到小说后，先读取用户指定范围与理解该范围所必需的前后文，再输出一张简短确认卡。禁止让用户在模型尚未阅读原文时填写空白问卷。

### 2. 最低理解与需求确认卡

首次响应只输出以下内容，不输出人物百科、剧情总结长文、受众分析、改编策划或剧本正文：

```text
【小说理解与需求确认】

处理范围：
叙事方式与文本特点：
当前事件链：
主要人物在当前情节中的直接目的：
关键身份、知情差与误解：
可能涉及的梗、简称或外部世界观：
目前发现的理解不确定项：
预计只需补齐的画面缺口类型：

请用户补充或纠正：
- 具体需求与表达倾向；
- 必须保留；
- 禁止改动；
- 梗知识／术语注释；
- 参考世界观及作者自定义改动；
- 目标单集时长或分集偏好；
- P0 尚未锁定的模型版本、画幅与交付形态。
```

确认卡只用于让用户检查是否漏读、误读或把梗当成客观设定。它不是改编方案，不判断什么剧情“更精彩”，不提出新增冲突、强化恋爱、制造反转或平台删改建议。

### 3. 确认门

- 默认必须等用户确认或补充后再进入正文处理。
- 用户明确说“无需确认理解，直接执行”时，可以跳过前台等待，但仍须在内部完成同等校准。
- 出现会改变人物、关系、能力、因果或结局的歧义时，必须停下询问；普通动作与空间缺口按最低充分原则处理。

---

## 二、 用户补充信息的三类权限

用户补充的内容必须先分类，禁止混成一锅设定汤。

### A. 当前作品事实

例如人物真实身份、谁知道什么、作者自定义能力规则、小说已修改的原作设定。此类信息可以约束补齐与剧本转换。

### B. 梗知识、术语和参考世界观

此类信息只用于避免误读：

- 识别称呼指向谁；
- 判断一句话是玩梗、反讽还是客观事实；
- 判断人物为何不能知道某件事；
- 避免把同人改设错误纠回原作；
- 避免把跨作品名词按错误体系解释。

> **世界观是只读词典，不是创作素材库。梗知识是理解注释，不是扩写燃料。**

不得因为用户提供了参考世界观，就自动把百科设定、未登场人物、额外能力、历史事件或原作桥段写进当前小说与剧本。

### C. 表达倾向

例如更克制、更轻松、保留吐槽感、法术反馈清楚、某人物不要被写成恋爱脑。此类信息只影响补丁的措辞与最低表现浓度，不赋予新增、删除、重排或改写故事的权限。

### 信息优先级

```text
用户当前明确裁决
>
当前小说明确写出的事实
>
当前项目已确认设定
>
用户指定的参考世界观
>
类型常识与模型推断
```

当前小说与原作品设定冲突时，以当前小说为准。模型常识只能帮助理解，不能补成新事实。

---

## 三、 原文最小增量补齐算法

### 1. 先保留，再检查

逐段沿原文顺序处理。凡是已经能被理解、能形成动作或能作为小说叙述成立的内容，原则上保持原句、原顺序、原人称、原语气与原信息密度，不为“更影视化”统一润色。

### 2. 只检查七类硬缺口

仅在不补就会造成画面、因果或连续性断裂时，允许补入：

1. **最低功能空间**：动作必须依赖但原文完全没有交代的柜台、出口、落脚处等；
2. **动作链**：动作的发起者、起点、完成过程与既定结果；
3. **必要接收**：动作或信息直接作用到某人时，其最低接收、听见、接稳或受力结果；
4. **物件连续**：物件从哪里取得、由谁递出、谁接稳、最终归谁；
5. **同期关系**：小说线性书写、实际同时发生的动作与反应；
6. **能力与特殊效果**：原文既定的触发、媒介／路径、作用对象、结果与残留；
7. **状态继承**：前后段落必须延续的人物位置、伤势、服装、持物、能力或环境状态。

### 3. 最低充分测试

每一句新增内容都必须能回答：

```text
它具体修补了哪一个画面、动作、接收、物件、能力或连续性缺口？
如果删掉它，哪一处会无法成立？
```

答不出来，立即删除。合理但非必要，不等于可以新增。

### 4. 已成立原文不重写

原文已经写出“大手一挥”“欲言又止”“瞳孔收缩”“抓起后甩飞”等动作与反应时，直接保留，不再叠加一套统一的眼神、呼吸、手指、肩颈和慢动作表演。

### 5. 禁止项

小说补齐阶段禁止：

- 整段换成模型自己的文风；
- 全文润色或重写对白；
- 为合理性补新动机、新计划、新冲突或新对话；
- 把后文信息提前搬到当前场景；
- 删除、压缩、筛选、调序原剧情；
- 为平台节奏改写故事；
- 把所有心理活动强行改成微表情；
- 用参考世界观补小说没有写出的设定；
- 把玩梗解释成正文百科；
- 无依据增加群众、排队、追逐、亲密动作或环境奇观；
- 把私密认知变成其他人物能听见的公开对白。

---

## 四、 心理、旁白与隐藏信息的处理

1. 小说阶段允许继续保留内心吐槽、作者旁白、身份说明和世界观说明，不要求全部可视化。
2. 只有心理变化直接决定当前动作，而原文缺少任何动作承接时，才补一个最低行为反馈。
3. 原文已有行为证明心理时，不重复添加表演。
4. 谁知道什么、谁不知道什么必须保持。补齐不得让人物提前知道隐藏身份、未来信息或他人内心。
5. 梗知识只帮助判断语义，不自动进入对白、旁白或设定说明。

---

## 五、 从补齐原文转换为专业生产剧本

补齐层完成后，执行媒介等价转换，不执行二次创作。

### 1. 必须保持不变

- 主要事件；
- 人物动机与关系；
- 知情范围与误解；
- 原有对白的含义与顺序；
- 事件顺序与因果；
- 能力机制、胜负和结果；
- 原作经营的吐槽、反讽与信息差。

### 2. 允许的格式转换

- 地点、时间或在场人物真正变化时建立新场次；
- 原文动作写入剧本动作段；
- 原对白写入人物对白；
- 必须保留的私密心理，可标为 OS／内心声，或在已有依据下由动作承载；
- 公共播报、屏幕、天幕、广播等写成对应公共信息层；
- 实际同期发生的内容恢复为同步动作与反应；
- 事件成立所需的最低环境、声音、物件与能力过程写入场次。

### 3. 小说模式对五阶门控的覆盖

小说已经提供故事前提、事件、人物和因果。Gate 1~4 只用于检查是否读懂与是否存在矛盾，不得据此重新设计钩子、删除场次、强制三幕比例、重写对白或把原作改成另一部短剧。

- Gate 2 的约 100 秒与 30%／50%／20%结构，不自动覆盖小说；分集服从用户在 P0／确认卡中锁定的目标时长与原剧情自然断点。
- 没有自然断点时继续到最近的完整事件结果，不切断动作、对白、物件交接、能力作用链或未完成因果。
- 内容过长时拆成下一集，不通过删剧情解决。

### 4. 剧本禁止提前做分镜

不得写镜头编号、镜头数量、观看对象、景别、机位、构图、焦段、运镜、切镜、单镜时长或视频生成组。这些由原版 P3 完整决定。

### 5. 默认交付

默认只交付标准专业剧本正文，不附人物分析、事件表、改编报告、增补账、冻结说明或交接总结。用户明确要求审阅补齐小说时，才额外交付保持小说形态的补齐版本。

---

## 六、 三轮自检门禁

专业剧本进入 P2 前必须完成以下三轮后台自检。默认不把检查报告塞进交付正文，只有失败项或用户要求时才展示。

### N0｜重写倾向检查

- 是否出现大段替换原文；
- 是否把作者语言统一成模型文风；
- 是否新增解释对白、情绪戏或桥段；
- 是否把全部心理改成动作；
- 是否因“更精彩”调整事件；
- 是否从参考世界观偷渡新内容。

发现任一项，退回原文，改成最小补丁。

### N1｜原作保真检查

- 主要事件、对白含义、人物动机、关系、知情边界、能力与结果是否保持；
- 原作独立信息、梗义、反讽和认知差是否遗漏；
- 每项新增是否能说明具体硬缺口；
- 用户提供的梗知识与世界观是否只用于理解；
- 是否用外部原设“纠正”了当前小说。

### N2｜生产连续性检查

- 人物是否凭空出现、消失或换位；
- 动作是否有发起、过程、接收与结果；
- 物件是否瞬移、复原或换持有人；
- 能力是否缺触发、作用、结果或残留；
- 私密信息是否被错误公开；
- 场景转换是否继承位置、伤势、持物和状态；
- 分集是否切断未完成事件；
- 剧本是否混入分镜语言。

三轮全部通过，才标记 P1 完成。

---

## 七、 与原版生产线的衔接

小说模式最终只生成一份正常的专业生产剧本。随后严格回到原版流程：

```text
P1 专业生产剧本完成
  ↓
P2 从剧本提取角色、场景、道具与声音，建立／核验资产
  ↓
P3 Work 重新提取观看任务，自行选择、合并、拆分并完成完整分镜
  ↓
P4 生成组与视频提示词
  ↓
P5 质检与交付
```

P3 不继承任何上游预分镜，因为小说模式不产生预分镜。项目合同、确认后的硬设定、连续状态和已有素材按原版普通附件读取，不构成第二份故事正文。

---

## 八、 极简正反例

### 例一：原文缺动作支点

原文：

```text
“都给我包起来！”
```

正确补丁：

```text
她扫过展开的衣服，抬手一挥。
“都给我包起来！”
```

错误重写：新增长篇审美回忆、招揽计划、暧昧心理或店外群众反应。

### 例二：世界观只用于防误读

用户说明“某称呼是网络梗，不是当前世界真实人物”。正确处理是保留原文吐槽语义，禁止把该人物写成登场、旁白设定或公共知识。
'''
write(PLUGIN / "references" / "novel-to-screenplay-adapter.md", novel_reference)

skill = PLUGIN / "SKILL.md"
h_block = r'''### H · 小说输入的 P1 原文补丁模式（2026-09-18 New Manju 扩展 · 不新增下游阶段）

- 用户明确提供小说并要求转剧本时，先读取指定范围，输出一张**最低理解与需求确认卡**，让用户纠正事件链、知情差、梗义和参考世界观；未确认前不直接改写。
- **最高规则：原文是主体，补充是补丁。**只补动作、接收、物件、能力与连续性中不补就无法成立的硬缺口；已成立原文不重写、不统一润色、不做平台删改。
- 用户补充的梗知识与参考世界观只作为**只读理解词典**，用于防止漏读和误判，不自动写成新剧情、设定说明或人物知识。
- 小说模式只在 P1 内完成 `原文最小增量补齐 → 标准专业剧本 → 三轮自检`；完成后直接回到原版 P2~P5。不得建立 S1/S2/S3、小说冻结包、上游基础分镜或第二套 Work 入口。
- 完整执行合同见 `references/novel-to-screenplay-adapter.md`（★权威）。

'''
insert_before_once(
    skill,
    "---\n\n## 一、 系统架构与专业规则库索引",
    h_block,
    "### H · 小说输入的 P1 原文补丁模式",
)

screenplay_ref_line = "    ├── ★ screenplay-gate-engine.md          # 五阶门控剧本引擎 (Premise->Structure->Beat->Entity->Page)\n"
insert_after_once(
    skill,
    screenplay_ref_line,
    "    ├── ★ novel-to-screenplay-adapter.md      # 小说原文最小增量补齐→专业剧本（P1 输入模式；世界观只读；完成后回归 P2）\n",
    "├── ★ novel-to-screenplay-adapter.md",
)

law_anchor = r"1. **剧本五阶门控 (Gate 1~5)**：Premise $\rightarrow$ 30%/50%/20% 结构 $\rightarrow$ 因果节拍表 $\rightarrow$ 世界观与实体边界 $\rightarrow$ 专业剧本页。" + "\n"
insert_after_once(
    skill,
    law_anchor,
    "1-N. **小说原文最小增量剧本化（P1 输入模式）**：先展示最低理解卡并让用户补充梗义／世界观注释，再按“原文主体、补充补丁”修补不可视缺口；禁止重写、删改、调序与外部设定偷渡。输出标准专业剧本后直接进入 P2，完整规则见 `novel-to-screenplay-adapter.md`。\n",
    "1-N. **小说原文最小增量剧本化",
)

route_anchor = "| **`/写剧本`** 或 **`初始化项目`** | 启动五阶门控剧本引擎，输出前提、因果节拍表与标准排版剧本。 |\n"
insert_after_once(
    skill,
    route_anchor,
    "| **`/小说转剧本`** | 启动 P1 小说原文补丁模式：先输出最低理解与需求确认卡；用户补充梗知识／参考世界观后，只补原剧情无法连续落成画面的硬缺口，转成标准专业剧本并完成 N0~N2 自检；随后按原版 P2~P5 连续执行。 |\n",
    "| **`/小说转剧本`**",
)

gate = PLUGIN / "references" / "screenplay-gate-engine.md"
gate_block = r'''## 〇、 P1 输入路由：原创、小说与现成剧本三路收口

P1 只允许三种输入方式，三者最终必须收口为同一种 **Professional Script Page**：

1. **故事想法／梗概／未完成剧本**：执行下方 Gate 1~5 创作型门控。
2. **小说原文**：执行 `novel-to-screenplay-adapter.md`（★权威）的原文最小增量模式。先向用户展示最低理解与需求确认卡，用户补充梗义、参考世界观与禁区后，按“原文主体、补充补丁”转成专业剧本。
3. **已完成的专业生产剧本**：只做 Gate 5 格式与连续性核验；用户未要求改写时，不再生成另一版剧本。

### 小说模式覆盖条款（高于下方创作型 Gate 1~4）

- 小说已经提供故事、人物和事件。Gate 1~4 只用于核对理解，不得成为重新设计钩子、删场、改对白、强化冲突或重排剧情的授权。
- Gate 2 的约 100 秒与 30%／50%／20%结构**不自动强制小说模式**；小说分集服从用户锁定的目标时长与自然事件断点，不能靠删改原文达标。
- Gate 3 的“可删除场次”规则不用于删除小说已有情节；只能检查因果是否被正确保留。
- Gate 4 的参考世界观只用于防误读。当前小说事实优先，禁止用原作百科纠正同人改设或补入未写内容。
- 下方“压力、承重场景、冰山对白”等自然化法则在小说模式中只作诊断，不能以“优化”为名重写原对白或改变作者语气。
- 小说模式完成后直接标记 P1 完成，按原版 P2~P5 执行；不建立任何小说专用下游入口。

---

'''
insert_before_once(gate, "## 一、 工业五阶门控开发流水线", gate_block, "## 〇、 P1 输入路由")

asset = PLUGIN / "references" / "asset-first-pipeline.md"
asset_block = r'''## 〇·五、 P1 输入收口规则（不改变 P2~P5）

P1 可以从三种材料进入：

```text
故事想法／梗概 → 五阶门控 → 专业剧本
小说原文 → 最小增量补齐与剧本转写 → 专业剧本
现成专业剧本 → Gate 5 核验 → 专业剧本
```

小说路径完整合同见 `novel-to-screenplay-adapter.md`。它只负责得到标准专业剧本，不产生上游分镜、冻结导入包或另一套资产入口。三路一旦收口，后续一律执行本文件原版 P2→P5；P3 仍由 Work 自行提取、选择、合并和拆分镜头。

---

'''
insert_before_once(asset, "## 一、 六阶段总览", asset_block, "## 〇·五、 P1 输入收口规则")
replace_once(
    asset,
    "P1 剧本五阶门控（前提 → 结构 → 节拍 → 实体 → 专业剧本页）",
    "P1 剧本门控（原创五阶／小说最小增量适配／现成剧本核验，统一收口为专业剧本页）",
)

agent = PLUGIN / "references" / "agent-platform-adapters.md"
replace_once(
    agent,
    "  - `P1 剧本门控阶段`：输入剧本大纲，输出前提与节拍表，自动生成侧边栏《剧组_资产图册.md》骨架与《剧组_全片情绪曲线.png》；",
    "  - `P1 剧本阶段`：故事想法／梗概走五阶门控；小说原文先输出最低理解与需求确认卡，再按 `novel-to-screenplay-adapter.md` 做最小增量补齐与专业剧本转写；现成专业剧本只核验不重写。三路统一生成标准剧本，并自动生成侧边栏《剧组_资产图册.md》骨架与《剧组_全片情绪曲线.png》；",
)
insert_before_once(
    agent,
    "- `/写剧本` / `初始化项目`：启动门控编剧与台账初始化",
    "- `/小说转剧本`：读取小说后先展示最低理解卡；用户补充梗义、世界观与禁区后，只补硬缺口并转成标准剧本，再回归 P2~P5\n",
    "- `/小说转剧本`：",
)

wrapper = r'''---
name: new-manju-workflow
description: 按漫剧老李 V6.8 Lite 原版 P0-P5 流程，支持故事创作、小说原文最小增量转专业剧本，以及现成专业剧本继续资产、完整分镜、视频提示词与质检。
---

# New Manju 漫剧工作流入口

本文件用于插件安装与发现。它只增加 **P1 小说输入模式**，不新增下游阶段、不改变 P2~P5 权力边界。

执行任何任务前，必须读取并以插件根目录的 `../../SKILL.md` 为总控，再按其中引用的 `references/` 执行。

## 输入处理

### 小说原文

用户明确要求小说转剧本时：

1. 先执行 P0 参数锁定，并阅读用户指定范围与必要前后文；
2. 前台先输出一张简短的【小说理解与需求确认】卡，说明事件链、人物直接目的、身份／知情差、可能涉及的梗与世界观、不确定项和预计只补的缺口；
3. 等用户补充或纠正需求、倾向、必须保留、禁止改动、梗知识、参考世界观与分集偏好；
4. 按 `../../references/novel-to-screenplay-adapter.md` 执行。最高规则是：**原文是主体，补充是补丁；世界观是只读词典。**
5. 只补不补就无法成立的动作、接收、物件、能力与连续性硬缺口，不重写已成立原文，不删改、调序或平台化重构；
6. 转成标准专业生产剧本并完成 N0~N2 自检；
7. 将该剧本视为已经完成的 P1 产物，直接回到原版 P2 人物、场景、道具和声音提取，继续完整分镜、提示词与 QA。

默认只交付专业剧本。用户明确要求先审补齐小说时，才展示保持小说形态的内部补齐版本。

### 已完成的专业生产剧本

- 先执行根 `SKILL.md` 的 P0 前置锁定，确认模型版本、画幅与交付形态；
- 将用户提供的专业剧本视为原版流程中已经完成的 P1 剧本产物；
- 除非用户明确要求改写，不再生成另一版剧本；
- 从 P2 人物、场景、道具与声音提取开始；
- 继续资产核验、空间调度、镜头任务提取、镜头选择、合并与拆分、完整分镜、提示词和 QA。

### 故事想法、梗概或未完成剧本

按根 `SKILL.md` 的原创 P0→P5 流程执行五阶门控，不套用小说保真模式。

### 已有剧本与正式素材

完成 P0 前置锁定并核验资产版本后，从原版流程中尚未完成的阶段继续。

## 禁止建立旁路

- 不得恢复 S1／S2／S3、冻结导入包、小说专用 Work 入口或上游基础分镜；
- 不得让小说补齐结果限制 P3 的完整分镜权；
- 不得把用户提供的参考世界观自动写成剧情；
- 不得让 Gate 1~4 在小说模式中重新创作或删改原故事。

小说模式结束于标准专业剧本。其后的资产、空间、分镜、生成组、提示词与质检始终由原版流程负责。
'''
write(PLUGIN / "skills" / "new-manju-workflow" / "SKILL.md", wrapper)

manifest_path = PLUGIN / "plugin.json"
manifest = json.loads(read(manifest_path))
manifest["version"] = "6.9.3"
manifest["description"] = "支持小说原文最小增量补齐转专业剧本，并从故事想法或现成剧本继续资产、完整分镜、Seedance 提示词与质检。"
if "小说转剧本" not in manifest["keywords"]:
    manifest["keywords"].insert(1, "小说转剧本")
interface = manifest["extensions"]["com.openai"]["interface"]
interface["shortDescription"] = "小说／专业剧本到资产、完整分镜与视频提示词"
interface["longDescription"] = "遵循 V6.8 Lite P0-P5 主流程。小说输入只在 P1 内先做最低理解确认，再按‘原文主体、补充补丁、世界观只读’完成最小增量补齐与专业剧本转写；现成专业剧本直接视为 P1 产物。两者随后统一进入原版资产、空间、镜头选择与合并拆分、完整分镜、Seedance 提示词和 QA。"
interface["defaultPrompt"] = [
    "读取我提供的小说，先给出最低理解与需求确认；不要重写，只补原剧情无法连续落成画面的硬缺口，转成专业剧本后继续原版流程。",
    "读取我提供的专业生产剧本，按原版流程从资产提取开始，连续完成完整分镜、视频提示词和质检。",
    "读取这个故事想法，按原创五阶门控完成剧本，并继续后续漫剧生产。",
]
write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")

codex_path = PLUGIN / ".codex-plugin" / "plugin.json"
codex = json.loads(read(codex_path))
codex["version"] = "6.9.3"
codex["description"] = "支持小说原文最小增量补齐转专业剧本，并从故事想法或现成剧本继续资产、完整分镜、Seedance 提示词与质检。"
cinterface = codex["interface"]
cinterface["shortDescription"] = "小说／专业剧本到资产、完整分镜与视频提示词"
cinterface["longDescription"] = "遵循 V6.8 Lite P0-P5 主流程。小说输入在 P1 内先校准理解，再以原文为主体做最小补丁并转成标准专业剧本；完成后与现成剧本一样进入原版资产、空间、完整分镜、提示词和 QA。"
cinterface["defaultPrompt"] = [
    "读取我提供的小说，先展示最低理解卡；不要重写，只补硬缺口并转成专业剧本，再继续原版生产。",
    "读取我提供的专业生产剧本，从原版资产阶段继续完成完整生产。",
    "读取这个故事想法，按原创 P0-P5 流程制作漫剧。",
]
write(codex_path, json.dumps(codex, ensure_ascii=False, indent=2) + "\n")

root_readme = r'''# New Manju 漫剧导演插件

本仓库以 **漫剧老李 AIGC 全流程 Skill V6.8 Lite** 为核心底座，并增加一个不改变下游权力边界的 **P1 小说输入模式**。

```text
P0 立项与模型／画幅锁定
→ P1 剧本阶段
   ├─ 故事想法／梗概：原创五阶门控
   ├─ 小说原文：最低理解确认 → 最小增量补齐 → 专业剧本
   └─ 现成专业剧本：格式与连续性核验
→ P2 数字资产包
→ P3 空间调度与完整分镜
→ P4 视频模型提示词
→ P5 独立质检
```

## 小说转剧本

使用 `/小说转剧本` 或明确说“把这本小说转成专业剧本”。插件不会立即重写，而是：

1. 阅读指定范围和必要前后文；
2. 先展示一张最低理解与需求确认卡，让用户纠正事件链、人物目的、身份／知情差、梗义和参考世界观；
3. 把用户补充的梗知识与世界观当成只读理解词典；
4. 以“原文是主体，补充是补丁”为最高规则，只补不补就无法成立的动作、接收、物件、能力与连续性缺口；
5. 转成不含镜头设计的标准专业剧本，并完成保真、重写倾向和生产连续性自检；
6. 直接汇入原版 P2→P5。

小说模式不删除、压缩、调序或平台化改写原剧情，不恢复 S1／S2／S3，也不产生上游基础分镜。

## 其他输入方式

- **故事想法、梗概或未完成内容**：按原创 P0→P5 全流程执行。
- **已经完成的专业生产剧本**：视为现成 P1 产物，直接从 P2 资产提取继续；除非用户明确要求，不再写另一版。
- **已有剧本与正式素材**：从对应的资产核验、空间和分镜阶段继续。

## Work 的职责

专业剧本完成后，插件依照原版规则自行完成：

```text
从剧本提取人物、场景、道具与声音
→ 建立或核验素材
→ 提取独立观看任务
→ 选择、合并与拆分镜头
→ 完整分镜与空间调度
→ 生成组装配
→ Seedance 提示词
→ QA
```

项目合同、参考世界观、连续状态、已有素材和用户硬约束是普通生产附件，不与剧本争夺故事解释权。

## 安装

仓库已包含：

- `.agents/plugins/marketplace.json`
- `short-drama-director/plugin.json`
- `short-drama-director/.codex-plugin/plugin.json`
- `short-drama-director/skills/new-manju-workflow/SKILL.md`

Codex 插件市场导入说明见 [`PLUGIN_MARKETPLACE.md`](./PLUGIN_MARKETPLACE.md)。

## 上游与许可证

核心规则库来自 `lixiaoxiao9888-create/manju-laoli-skill` 的 V6.8 Lite 工作流，保留原 MIT 许可证。小说适配只扩展 P1 输入，不改变原版 P2~P5 的资产与导演权力边界。
'''
write(ROOT / "README.md", root_readme)

inner_readme = r'''# 漫剧老李 AIGC 全流程 Skill · V6.8 Lite + New Manju P1 小说适配

本目录保留原版工业化漫剧生产流程，并增加 Agent Plugins / Codex 安装包装与一个 **P1 小说原文最小增量适配器**。

## 生产顺序

```text
P0 立项锁定
→ P1 剧本
   ├─ 原创五阶门控
   ├─ 小说最小增量补齐与剧本转写
   └─ 现成专业剧本核验
→ P2 数字资产包
→ P3 空间调度与完整分镜
→ P4 视频提示词
→ P5 独立质检
```

## 小说输入边界

- 先展示最低理解与需求确认卡，用户可补充梗知识、参考世界观和禁止改动项；
- 原文是主体，补充是补丁；世界观只读，不自动写成新内容；
- 只补动作、接收、物件、能力和连续性中的硬缺口；
- 不重写已成立原文，不删改、压缩、调序或强制平台化；
- 输出标准专业剧本后，直接回到原版 P2~P5；
- 不产生 S1／S2／S3、冻结导入包或上游基础分镜。

完整规范见 [`references/novel-to-screenplay-adapter.md`](./references/novel-to-screenplay-adapter.md)。

## 已有专业剧本的处理

当用户直接提供完成的专业生产剧本时：

1. 把该剧本作为现成 P1 产物；
2. 除非用户明确要求改写，否则从 P2 资产提取与核验继续；
3. 分镜的选择、合并、拆分、景别、机位、构图、运镜、时长与生成组仍由原版 P3 完成。

## 主要能力

- 小说原文最小增量转专业剧本；
- Seedance 2.5 / 2.0 分流适配；
- 16:9、9:16、21:9 画幅锁定；
- Asset-First 数字资产包；
- 文戏微表情与武戏动力链；
- 空间站位、轴线和完整分镜；
- 七段式视频提示词；
- P0～P2 质量门禁与提示词机检；
- Markdown 到离线分镜看板。

完整规则以 [`SKILL.md`](./SKILL.md) 和 [`references/`](./references/) 为准。
'''
write(PLUGIN / "README.md", inner_readme)

notice = r'''# NOTICE

本仓库以 `lixiaoxiao9888-create/manju-laoli-skill` 的 V6.8 Lite 工作流为核心底座，保留原许可证与 P0→P5 生产逻辑。

当前仓库增加：

- Agent Plugins 1.0 清单；
- Codex 兼容清单；
- Codex Marketplace 清单；
- 一个轻量安装入口包装；
- P1 内部的小说原文最小增量转专业剧本适配器。

小说适配不建立新的下游流程。它只在 P1 中先校准用户需求和原文理解，再按“原文主体、补充补丁、世界观只读”完成剧本化；输出标准专业剧本后，仍由原版 P2~P5 继续资产、空间、完整分镜、提示词与质检。
'''
write(ROOT / "NOTICE.md", notice)

marketplace = r'''# Codex 插件市场导入

## 在“添加插件市场”中填写

```text
来源：https://github.com/lingweilian47-cmyk/new-manju
Git 引用：留空，或填写 main
稀疏路径：留空
```

市场清单位于：

```text
.agents/plugins/marketplace.json
```

导入的插件名称：

```text
new-manju
```

插件根目录：

```text
short-drama-director/
```

目录内包含：

- `plugin.json`：Agent Plugins 1.0 清单；
- `.codex-plugin/plugin.json`：Codex 兼容清单；
- `skills/new-manju-workflow/SKILL.md`：轻量安装入口，转交根 `SKILL.md`；
- `references/novel-to-screenplay-adapter.md`：P1 小说原文最小增量剧本化规范；
- 原版 `SKILL.md`、其余 `references/` 与 `scripts/`。

安装后可直接输入小说并要求 `/小说转剧本`：插件先展示最低理解卡，用户补充梗知识与世界观后，只补硬缺口并转成专业剧本，再按原版流程继续。也可直接输入已经完成的专业剧本，从 P2 资产阶段继续。
'''
write(ROOT / "PLUGIN_MARKETPLACE.md", marketplace)

changelog_path = PLUGIN / "CHANGELOG.md"
changelog = read(changelog_path)
if "## 6.9.3" not in changelog:
    entry = r'''# Change Log

## 6.9.3 · 2026-09-18

- 新增 P1 小说原文最小增量剧本化模式，不新增 P0~P5 之外的生产阶段。
- 小说输入后先展示最低理解与需求确认卡，供用户补充梗知识、参考世界观、必须保留和禁止改动项。
- 确立“原文是主体，补充是补丁；世界观是只读词典”最高规则，只补动作、接收、物件、能力与连续性硬缺口。
- 小说模式禁止重写、删改、调序、平台化压缩与外部设定偷渡；Gate 1~4 只做理解校验，不获得二次创作权。
- 新增 N0 重写倾向、N1 原作保真、N2 生产连续性三轮自检。
- 专业剧本完成后直接汇入原版 P2~P5；Work 仍拥有完整分镜的选择、合并与拆分权。
- 插件清单、安装入口、README、Marketplace 与包级自检同步更新。

'''
    if changelog.startswith("# Change Log\n\n"):
        changelog = entry + changelog[len("# Change Log\n\n"):]
    else:
        changelog = entry + changelog
    write(changelog_path, changelog)

check_package = r'''#!/usr/bin/env python3
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
'''
write(PLUGIN / "scripts" / "check_package.py", check_package)

print("P1 novel adapter patch staged.")
