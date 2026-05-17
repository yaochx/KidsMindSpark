# 开发里程碑 M0-M6

每次开发只实现一个 milestone。除非当前 milestone 明确要求，不得提前实现后续功能。

## M0 项目初始化

### 目标

建立本地 MVP 的基础工程结构、文档入口和最小运行骨架。

### 交付物

- Next.js + TypeScript + TailwindCSS 前端骨架。
- Flask + Python 3.11 后端骨架。
- README 中说明本地启动方式。
- 基础类型目录和 API 目录占位。

### 文件清单

- `README.md`
- `frontend/`
- `backend/`
- `backend/app/`
- `backend/data/`
- `docs/`

### 验收标准

- 前端可本地启动并显示基础页面。
- 后端可本地启动并返回健康检查。
- README 包含前后端启动命令。
- 未实现故事生成业务。

### 不允许做的事情

- 不做真实 AI 接入。
- 不做 32 页生成。
- 不做 PDF 导出。
- 不做复杂 UI。

## M1 故事输入页

### 目标

实现非聊天式故事概念输入页，收集故事标题、概念、风格和目标读者年龄段。

### 交付物

- 故事输入表单。
- 表单校验。
- 调用 `POST /api/story/outline` 的 mock 流程。
- 生成核心设定后进入主线生成流程。

### 文件清单

- `frontend/app/`
- `frontend/components/story/`
- `frontend/lib/api/`
- `frontend/lib/types/`
- `backend/app/api/`
- `backend/app/services/`
- `backend/app/providers/mock_provider.py`

### 验收标准

- 页面不是聊天窗口。
- 用户只能通过结构化表单提交故事概念。
- 危险元素应被儿童适龄改写，例如“猎枪”改为“玩具探险杖”或“木头探险杖”。
- 不生成正文和 PDF。

### 不允许做的事情

- 不允许开放式聊天。
- 不允许直接生成 32 页正文。
- 不允许接入真实 AI。

## M2 主线确认页

### 目标

实现图形化故事主线确认页，让用户确认或编辑主线节点。

### 交付物

- 主线节点可视化。
- 节点详情卡片。
- 确认与返回编辑操作。
- 调用 `POST /api/story/timeline` 和 `PUT /api/story/timeline`。

### 文件清单

- `frontend/components/timeline/`
- `frontend/components/story/`
- `frontend/lib/types/timeline.ts`
- `backend/app/api/story.py`
- `backend/app/services/timeline_service.py`

### 验收标准

- 主线以图形化节点呈现。
- 必须包含：开场、主角、目标、伙伴、阻碍、转折、危机、解决、结局。
- 节点、卡片、按钮不重叠。
- 用户确认前不能生成 32 页分镜。

### 不允许做的事情

- 不允许纯文本主线确认。
- 不允许跳过确认。
- 不允许生成 PDF。

## M3 32 页分镜脚本页

### 目标

基于已确认主线生成固定 32 页漫画分镜脚本。

### 交付物

- 32 页脚本数据。
- 每页 1-4 个分镜。
- 每页短对白。
- 分镜脚本查看页。

### 文件清单

- `frontend/components/script/`
- `frontend/lib/types/script.ts`
- `backend/app/services/script_service.py`
- `backend/app/providers/mock_provider.py`
- `backend/data/`

### 验收标准

- 输出必须正好 32 页。
- 每页分镜数必须在 1-4。
- 对白适合小学生阅读，不出现长段落。
- 不改变已确认主线，除非用户返回 M2 编辑。

### 不允许做的事情

- 不允许可变页数。
- 不允许无限续写。
- 不允许纯文字故事页替代分镜。

## M4 彩色漫画预览页

### 目标

展示面向中式/日式彩色漫画的预览结构，MVP 使用 mock 图片占位。

### 交付物

- 漫画页预览组件。
- 分镜图像占位。
- 角色对白气泡。
- 旁白和页码。
- 调用 `POST /api/comic/mock-images`。

### 文件清单

- `frontend/components/comic/`
- `frontend/lib/types/comic.ts`
- `backend/app/api/comic.py`
- `backend/app/services/mock_image_service.py`

### 验收标准

- 预览不是纯文本。
- 每个分镜具备图像占位或图像引用。
- 页面可滚动浏览 32 页。
- 文本、图像、按钮、卡片不重叠。

### 不允许做的事情

- 不允许把脚本原文直接当最终预览。
- 不允许接入真实图像生成作为必需功能。
- 不允许破坏 32 页结构。

## M5 PDF 导出

### 目标

导出 A4 PDF 预览，结构上服务于后续 32 开漫画打印。

### 交付物

- PDF 导出入口。
- 后端或浏览器打印方案。
- PDF 中包含漫画页、分镜、mock 图像、对白、页码。
- 调用 `GET /api/export/pdf`。

### 文件清单

- `frontend/components/export/`
- `backend/app/api/export.py`
- `backend/app/export/`
- `backend/data/exports/`

### 验收标准

- PDF 不是纯文字故事。
- PDF 包含固定 32 页漫画结构。
- A4 预览可打开。
- 文档说明后续 32 开打印适配点。

### 不允许做的事情

- 不允许只导出文本。
- 不允许在 PDF 阶段改变故事内容。
- 不允许引入复杂云存储。

## M6 优化与测试

### 目标

优化 MVP 的稳定性、布局、错误状态和基础测试。

### 交付物

- 基础单元测试或集成测试。
- UI 空状态、loading 状态、错误状态。
- 32 页和 1-4 分镜约束测试。
- README 更新。

### 文件清单

- `frontend/components/`
- `frontend/lib/`
- `backend/app/`
- `backend/tests/`
- `README.md`

### 验收标准

- 核心流程可从输入走到 PDF 导出。
- 关键约束有测试或显式校验。
- 常见错误有友好提示。
- 桌面和移动宽度下无明显重叠。

### 不允许做的事情

- 不允许大规模重写已稳定流程。
- 不允许新增非 MVP 功能。
- 不允许引入无限续写或聊天入口。
