# 团队协作规范

本文件面向所有参与本仓库开发的同学和自动化编码代理。开发前必须先阅读本文件，再阅读 `docs/AI_CONTRACT.md`、`docs/MILESTONE.md` 和当前 milestone 相关文档。

## 基础开发流程

1. 每次只实现一个 milestone，不要一次性生成整个项目。
2. 修改前先确认当前目标是否符合 `docs/AI_CONTRACT.md` 的硬约束。
3. 修改后运行当前阶段可用的测试、编译或静态检查。
4. 若行为、启动方式或阶段状态发生变化，必须同步更新 `README.md` 或对应文档。
5. 一个 PR 只承载一个明确目标，优先对应一个 milestone 或一个独立修复。

## 分支模型

1. 主干分支为保护分支：`main` 或 `master`。
2. 禁止直接在 `main` 或 `master` 上开发并直接 push。
3. 所有业务开发、修复、发布准备必须从保护分支拉出短生命周期分支。
4. 分支完成后只能通过 GitHub PR 合并回保护分支。
5. 分支内容必须聚焦单一目标，不得把多个无关改动混在同一分支。

## 分支命名规范

分支名必须符合以下格式之一：

```text
feature/<scope>-<topic>
fix/<scope>-<issue>
hotfix/<version>-<topic>
release/<version>
```

规则：

1. `scope` 必须稳定、可复用、小写，优先使用仓库已有模块名、目录名或领域标识，例如 `frontend`、`backend`、`docs`、`comic`、`export`、`timeline`、`script`。
2. `topic` 和 `issue` 使用小写英文、数字和连字符，描述具体目标。
3. `version` 使用稳定版本号或发布标识，例如 `v0.1.0`。
4. 禁止使用无信息量或随意命名的分支名，例如 `test`、`update`、`dev`、`aaa`、`bugfix`。
5. 禁止长期复用个人开发分支承载多个不相关任务。

示例：

```text
feature/docs-git-policy
feature/frontend-story-input
fix/backend-outline-validation
hotfix/v0.1.0-pdf-export
release/v0.1.0
```

## Commit Message 规范

commit message 必须使用 Conventional Commits 风格，且本仓库强制使用完整的 subject、body、footer。

格式必须为：

```text
<type>(<scope>): <subject>

1. <body line>
2. <body line>

<footer-key>: <footer-value>
```

### Type

`type` 仅允许使用以下集合：

```text
feat
fix
docs
refactor
test
chore
```

含义：

1. `feat`：新增用户可感知能力或新流程。
2. `fix`：修复缺陷或错误行为。
3. `docs`：只修改文档、规范或说明。
4. `refactor`：不改变外部行为的结构调整。
5. `test`：新增或修改测试。
6. `chore`：构建、配置、依赖、工具或仓库维护。

### Scope

1. `scope` 必须为小写英文。
2. `scope` 可使用模块名、目录名或稳定领域标识，例如 `frontend`、`backend`、`docs`、`comic`、`export`、`timeline`、`script`。
3. 禁止使用 `misc`、`temp`、`stuff` 等无稳定含义的 scope。

### Subject

1. `subject` 必须使用中文描述结果；术语、标识符、版本号可保留英文。
2. `subject` 必须明确说明本次提交达成了什么结果。
3. 禁止使用低信息量标题，例如 `fix bug`、`update`、`test`、`modify code`、`调整`。
4. `subject` 不得把多个不相关目标塞进同一句。

示例：

```text
docs(docs): 补充 Git 分支与提交规范
feat(frontend): 增加故事输入表单
fix(backend): 修正主线确认状态校验
```

## Commit Body 强约束

1. body 必填，且必须与 subject 之间空一行。
2. body 每一行都必须使用数字 bullet，格式为 `1. 修正 xxx`、`2. 补充 xxx`。
3. body 每行只表达一个独立修改点。
4. body 必须使用真实换行，禁止把 `\n` 当普通文本塞进一行。
5. 禁止把 subject、body、footer 压成一个单行字符串提交。
6. 生成 commit message 时，必须使用真实多行输入方式，例如多个 `-m`、`git commit -F <file>` 或编辑器输入。

推荐命令：

```bash
git commit \
  -m "docs(docs): 补充 Git 分支与提交规范" \
  -m "1. 新增分支命名格式和保护分支要求
2. 明确 commit body 必须使用数字 bullet
3. 补充 PR 合并策略和常见禁止事项" \
  -m "Refs: git-policy
Review: required"
```

也可以使用文件提交：

```bash
git commit -F .git/COMMIT_EDITMSG
```

## Footer 规范

1. footer 必填，且必须与 body 之间空一行。
2. footer 必须使用键值格式。
3. 如无外部 issue，也必须至少保留一个治理类 footer。

允许示例：

```text
Refs: #123
Review: required
RFC: branch-policy
BREAKING CHANGE: 调整本地数据结构
```

无外部 issue 时推荐：

```text
Refs: internal
Review: required
```

## 单提交单意图

1. 一个 commit 只表达一个独立意图。
2. 文档规范、前端 UI、后端 API、数据迁移、测试补充应按实际意图拆分提交。
3. 禁止一个 commit 同时混入多个不相关改动。
4. 如果为了完成同一个 milestone 必须改多个模块，body 中逐条说明每个修改点。
5. 若发现提交混入无关改动，必须在合并前拆分或重做提交。

## GitHub PR 合并策略

1. `main` 和 `master` 是保护分支，禁止直接 push。
2. 本项目使用 GitHub，合并请求统一称为 PR；GitLab 中的 MR 仅作为概念等价物，不作为本仓库执行口径。
3. 只允许通过 GitHub PR 合并到保护分支。
4. PR 必须说明目标、影响范围、验证结果和对应 milestone。
5. PR 必须经过至少 1 名 reviewer 审核。
6. 合并前必须通过当前仓库可用的检查，例如后端编译、路由检查、前端 lint、单元测试或文档检查。
7. 默认使用 Squash Merge 合并，最终 squash commit 也必须符合本文件的 commit message 规范。
8. 禁止把多个无关改动混入同一个 PR。
9. 禁止为省事跳过 review、检查、body 或 footer。

## 常见不规范行为限制

以下行为一律禁止：

1. 随意命名分支，例如 `test`、`update`、`dev`、`aaa`、`bugfix`。
2. 使用无信息量 commit 标题，例如 `fix bug`、`update`、`test`、`modify code`、`调整`。
3. 一个 commit 混入多个不相关改动。
4. 为了省事跳过 commit body 或 footer。
5. 直接 push 到 `main` 或 `master`。
6. 在提交信息里使用伪换行，或提交格式不完整的 message。
7. 绕过 GitHub PR 合并策略。
8. 在当前 milestone 中提前实现后续 milestone 的功能。

## 提交前自检

提交前必须确认：

1. 分支名符合本文件规范。
2. commit message 符合 Conventional Commits、body、footer 规则。
3. 本次提交是单提交单意图。
4. 没有直接在保护分支上开发并 push。
5. 没有混入与当前 milestone 或当前修复无关的文件。
6. 已运行当前阶段可用检查，并在 PR 中记录结果。
