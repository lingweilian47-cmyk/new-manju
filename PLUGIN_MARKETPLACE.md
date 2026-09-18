# Codex 插件市场导入

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
- `skills/new-manju-workflow/SKILL.md`：轻量安装入口，仅转交根 `SKILL.md`，不新增工作流；
- 原版 `SKILL.md`、`references/` 与 `scripts/`。

安装后，输入完成的专业剧本即可按原版流程继续资产、完整分镜、提示词和质检。插件不要求小说改编中间稿。
