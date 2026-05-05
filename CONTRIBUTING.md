# Contributing to net-code-audit-skill-master

感谢你对 .NET 攻防代码审计 Skill 项目的关注！本指南帮助贡献者保持项目的一致性和全球顶级质量。

## 行为准则

- 尊重所有参与者，禁止任何形式的骚扰。
- 所有技术讨论以建设性为前提。
- 遵守授权边界：不提交可用于未授权攻击的完整武器化 payload。

## 如何贡献

### 1. 报告问题（Issue）

- 使用清晰的标题描述问题。
- 提供复现步骤、期望结果和实际结果。
- 如果是 skill 内容错误，请标注具体的 SKILL.md 和章节。

### 2. 提交改进（Pull Request）

1. Fork 仓库并创建特性分支：`feature/<description>` 或 `fix/<description>`。
2. 遵循现有代码和文档风格。
3. 确保所有 Markdown 链接有效。
4. 更新相关的索引文件（见下方维护同步规则）。
5. 提交 PR 前在本地运行验证（见下方质量校验）。

## Skill 新增规范

新增专项 skill 必须包含：

```text
<skill-name>/
├── SKILL.md                    # 必须：frontmatter + 工作流 + 自检
├── references/                 # 必须：结构化 reference
│   └── ...
└── agents/
    └── openai.yaml             # 可选但推荐：agent interface 配置
```

### SKILL.md 模板要求

```markdown
---
name: <skill-name>
version: 2.0.0
description: <中文描述>
description_en: <English description>
author: <your-name-or-team>
tags: ["dotnet", "<category>", "security", "audit"]
compatibility: ["asp.net", "asp.net-core", ...]
---

# <标题>

## 工作流

1. ...
2. ...

## Reference 选择

| 任务 | 读取 |
|---|---|
| ... | ... |

## 输出要求

- ...

## 自检

- [ ] ...
```

## 维护同步规则

修改任何内容后，必须同步以下文件：

1. **对应 SKILL.md** — 保持内容准确。
2. **对应 references/** — 新增或更新结构化文档。
3. **`shared/DOTNET_ATTACK_SURFACE_TAXONOMY.md`** — 更新分类、sink、推荐 skill 映射。
4. **`dotnet-offsec-audit/scripts/collect_dotnet_surface.py`** — 新增规则必须补充 `recommended_skill`、`confidence`、`evidence_kind`。
5. **`dotnet-audit-pipeline/SKILL.md`** — 更新阶段和 agent 说明。
6. **根目录 README.md 与 net-skill/README.md** — 更新索引和表格。
7. **CHANGELOG.md** — 记录变更。

## 质量校验

提交前请运行：

```powershell
# Python 脚本语法检查
python -m py_compile net-skill/dotnet-offsec-audit/scripts/collect_dotnet_surface.py
python -m py_compile net-skill/dotnet-vuln-scanner/scripts/scan_dotnet_dependencies.py

# Markdown 链接检查（推荐安装 markdown-link-check）
# npx markdown-link-check README.md
# npx markdown-link-check net-skill/README.md

# 目录结构完整性
Get-ChildItem net-skill -Directory | Where-Object { Test-Path (Join-Path $_.FullName "SKILL.md") }
```

## 安全边界

- **禁止**在 PR 中提交真实密钥、token、连接串。
- **禁止**提交可直接用于未授权系统的完整武器化 payload。
- 审计样例中的无害验证优先；红队实验室内容必须标注场景和边界。

## 许可证

提交即表示你同意将你的贡献在 [Mulan PSL v2](LICENSE) 下发布。
