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
- `skills/new-manju-workflow/SKILL.md`：轻量安装入口，转交根 `SKILL.md`；
- `references/novel-to-screenplay-adapter.md`：P1 小说原文最小增量剧本化规范；
- 原版 `SKILL.md`、其余 `references/` 与 `scripts/`。

安装后可直接输入小说并要求 `/小说转剧本`：插件先展示最低理解卡，用户补充梗知识与世界观后，只补硬缺口并转成专业剧本，再按原版流程继续。也可直接输入已经完成的专业剧本，从 P2 资产阶段继续。
