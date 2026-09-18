# 多平台 Agent 架构与国产工作流适配规范 (Multi-Agent Platform Adapters)

本规范专为解决不同 Agent 运行平台（如 **OpenClaw**、**WorkBuddy**、**豆包智能体 / 扣子 Coze**、**Dify**）在交互协议、状态机、文件挂载与上下文长度等方面的差异，提供全平台无缝兼容方案。

---

## 一、 平台差异与核心适配机制

```text
               ┌──> OpenClaw (命令行 / Tool-Call / 完整 Skill 目录挂载)
               ├──> WorkBuddy (卡片式 Action Card / 侧边栏产出册 / 会话状态机)
[导演 Skill 总控] ├──> 豆包智能体 / 扣子 Coze (节点式工作流 / 插件输入输出 / JSON 契约)
               └──> Dify / 通用 LLM (单文件 Prompt 模式 / 标准 Markdown 输出)
```

---

## 二、 平台专属适配规范

### 0. 小说漫剧已改编入口（全平台 CURRENT）
- 检测到冻结 S1/S2/S3 时，状态机从 `P1-N 导入验收` 开始，不再运行剧本生成；
- Work 读取 Novel Production Pack，完成资产、人物距离、空间、精确摄影、内部容量与 Seedance 2.5 七段式无时间码 Prompt；
- 内部工作流/API 控制层可以保存技术时长参数，最终 `positive_prompt` 正文不得出现时间码、数字秒数与镜长；
- 回流严格按 S1（人物/机制）、S2（剧情/对白/体验）、S3（镜头功能）责任边界执行。

### 1. WorkBuddy 平台专属适配
- **会话状态机驱动（双入口 P0 ~ P5 阶段流转）**：
  - `P0 立项锁定阶段`：锁定画幅（16:9/9:16）、风格预设、平台模型、目标时长（见 `aspect-ratio-adaptation.md`）；
  - `P1 剧本门控阶段`：输入剧本大纲，输出前提与节拍表，自动生成侧边栏《剧组_资产图册.md》骨架与《剧组_全片情绪曲线.png》；
  - `P2 数字资产包阶段`（本 skill 核心）：
    - P2a 从剧本自动提取全部 CHR/SCN/PRP/AUD 实体；
    - P2b 输出《完整资产清单》（16 项五官 + 6 项材质 + 亲缘推导表）→ 用户确认无遗漏；
    - P2c 分批出图：①角色（T1→T2→T3 4 View 资产板，Action Card 出图确认）②场景（核心场景资产图（母版+机位调度版或站位版+拼接图））③道具（关键道具图），每批锁定；
    - P2d 交付《资产图册》（CHR/SCN/PRP 全附资产参考图 + 短锚点 @名）；
  - `P3 空间调度与分镜阶段`：输出 2x2 顶视图（`主体顶视图_演员机位_Ep1-4.png`）与文武双模分镜，**每个镜头引用已锁定的 @资产图**；
  - `P4 批量投喂与成片阶段`：自动导出解耦提示词与执行载荷（绑定资产图）；
  - `P5 质检与交付阶段`：P0/P1/P2 门禁 + 资产一致性检查（画幅/脸型/服装与资产图一致）。
- **文件交互与侧边栏渲染**：
  - 产出文件统一命名为标准规范（如 `剧组_资产图册.md`、`剧组_全片情绪曲线_v1.png`、`主体顶视图_演员机位_Ep1-4.png`）；
  - 支持 WorkBuddy 在线预览、一键复制与本地 Download 自动归档。

### 2. 豆包智能体 / 扣子 (Coze) 工作流专属适配
- **节点化入参与出参契约（Node Payload Contract）**：
  - 针对豆包工作流的节点流转，输出标准 JSON 格式数据块，便于上游节点抓取字段：
    ```json
    {
      "episode_id": "EP01",
      "shot_index": "U01",
      "duration": 15,
      "model": "seedance-2.5",
      "positive_prompt": "[主体] ... [环境] ... [运镜] ...",
      "negative_prompt": "blurry, low quality, distorted",
      "character_ids": ["CHR-楚灵风-战损", "CHR-厉绝-幽冥"],
      "camera_id": "CAM1",
      "speech_speed_check": {
        "word_count": 0,
        "status": "PASS"
      }
    }
    ```
- **上下文分块与长文本流式防护（Chunking Protocol）**：
  - 遇到长篇剧本时，自动启用分集分块处理（Chunking），单次响应控制在 2000 Tokens 以内，避免豆包对话上下文截断。

### 3. OpenClaw 平台适配
- **标准 Skill 规范**：完整保留 `SKILL.md`、`references/` 规则库与 `scripts/` 校验脚本；
- **命令行快速安装**：支持 `openclaw skills install ./short-drama-director --as short-drama-director` 一键部署。

### 4. Dify / FastGPT / 通用大模型适配
- **免依赖单文件 Prompt 模式**：
  - 用户输入 `导出全量 Prompt` 或直接复制 `SKILL.md` 时，自动内嵌核心规则摘要，无需本地读取 references 子文件即可独立运行。

---

## 三、 全平台通用指令路由一览

无论在哪个 Agent 平台，以下指令均可统一触发：
- `/小说漫剧制作` / `/导入S1S2S3`：启动 P1-N 小说导入验收与 Work 技术施工
- `/写剧本` / `初始化项目`：启动原入口门控编剧与台账初始化
- `/剧组产出册`：输出标准化 Markdown 台账（兼容 WorkBuddy 挂载）
- `/情绪曲线`：输出 12 节拍张力分析（支持豆包 JSON 与图片绘制）
- `/顶视图`：输出机位调度与 180° 轴线方案
- `/生成视频提示词`：存在 S1/S2/S3 时输出 Seedance 2.5 七段式无时间码 Prompt；否则沿用原入口模型分流
- `/导出工作流参数`：输出豆包工作流 / API 标准 JSON 载荷
