# New Manju 漫剧导演插件

本仓库把上游 **漫剧老李 AIGC 全流程 Skill V6.8 Lite** 封装为可安装插件。核心生产逻辑保持原版：

```text
P0 立项与模型／画幅锁定
→ P1 剧本门控
→ P2 数字资产包
→ P3 空间调度与完整分镜
→ P4 视频模型提示词
→ P5 独立质检
```

## 输入方式

- **故事想法、梗概或未完成内容**：按原版 P0→P5 全流程执行。
- **已经完成的专业生产剧本**：将该剧本视为现成的 P1 剧本产物，直接从 P2 资产提取继续；除非用户明确要求，不重新写一版剧本。
- **已有剧本与正式素材**：从对应的资产核验、空间和分镜阶段继续。

插件不会识别或要求任何小说改编中间稿，不设置 S1／S2／S3、冻结母稿、小说专用导入门或 Chat 基础分镜。小说如何改成专业剧本属于插件外部流程；进入本插件时，专业剧本就是正常剧本输入。

## Work 的职责

收到专业剧本后，插件依照原版规则自行完成：

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

项目合同、世界观、连续状态、已有素材和用户硬约束可以随剧本一并提供，但它们是普通生产附件，不会触发另一套流程。

## 安装

仓库已包含：

- `.agents/plugins/marketplace.json`
- `short-drama-director/plugin.json`
- `short-drama-director/.codex-plugin/plugin.json`
- `short-drama-director/skills/new-manju-workflow/SKILL.md`

Codex 插件市场导入说明见 [`PLUGIN_MARKETPLACE.md`](./PLUGIN_MARKETPLACE.md)。

## 上游与许可证

核心规则库来自 `lixiaoxiao9888-create/manju-laoli-skill` 的 V6.8 Lite 工作流，保留原 MIT 许可证。当前仓库额外提供插件清单和安装包装，不改变原版生产阶段的权力边界。
