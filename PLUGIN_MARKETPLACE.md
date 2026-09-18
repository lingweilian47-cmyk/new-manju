# Codex 插件市场导入

本仓库已经包含 Codex Marketplace 清单与 New Manju 插件封装。

## 在“添加插件市场”中填写

```text
来源：https://github.com/lingweilian47-cmyk/new-manju
Git 引用：留空，或填写 main
稀疏路径：留空
```

不要把 `plugins/codex`、`.agents/plugins` 或 manifest 文件名填入“稀疏路径”。市场清单位于仓库根目录下的：

```text
.agents/plugins/marketplace.json
```

该市场会导入一个插件：

```text
new-manju
```

插件根目录：

```text
short-drama-director/
```

其中同时包含：

- `plugin.json`：Agent Plugins 1.0 可移植清单；
- `.codex-plugin/plugin.json`：Codex 兼容清单；
- `skills/new-manju-workflow/SKILL.md`：插件入口技能；
- 原项目完整 `SKILL.md`、`references/`、`scripts/` 与小说三阶段入口。

## 更新

通过 GitHub 市场导入后，后续可在市场详情页使用“立即同步／Sync now”拉取仓库更新。
