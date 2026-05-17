# 开发里程碑 M0-M14

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
- 不做漫画分镜生成。
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
- 不允许直接生成漫画正文。
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
- 用户确认前不能生成漫画分镜。

### 不允许做的事情

- 不允许纯文本主线确认。
- 不允许跳过确认。
- 不允许生成 PDF。

## M3 漫画分镜脚本页

### 目标

基于已确认主线生成漫画分镜脚本。M14 后页数由 `story_first_bounded` 策略控制。

### 交付物

- 漫画脚本数据。
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

- 输出必须满足当前页数策略。M14 后为 16-48 页。
- 每页分镜数必须在 1-4。
- 对白适合小学生阅读，不出现长段落。
- 不改变已确认主线，除非用户返回 M2 编辑。

### 不允许做的事情

- 不允许超出当前页数策略。
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
- 页面可滚动浏览所有漫画页面。
- 文本、图像、按钮、卡片不重叠。

### 不允许做的事情

- 不允许把脚本原文直接当最终预览。
- 不允许接入真实图像生成作为必需功能。
- 不允许破坏脚本结构。

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
- PDF 包含漫画页结构。
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
- 页数策略和 1-4 分镜约束测试。
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

## M7 Provider 拆分与真实模型预备层

### 目标

将当前混合 mock 生成能力拆成两个独立 provider 边界：`StoryProvider` 和 `ImageProvider`。M7 只建立可切换、可校验、可回退的 provider 架构，为后续接入 ChatGPT/OpenAI、MiniMax、GLM、DeepSeek 等文本模型，以及 OpenAI Images、MiniMax Image、可灵、即梦、通义万相等图像模型做准备。

### 为什么要拆分

漫画应用需要两类能力：

- 文本结构能力：故事核心设定、图形化主线、漫画分镜、每个分镜的图像提示词。
- 图像生成能力：根据每个 panel 的 `imagePrompt` 生成漫画图像，并返回 `ComicImage` 数据。

DeepSeek、GLM、OpenAI 文本模型适合第一类。图像能力必须由 OpenAI Images、MiniMax Image、可灵、即梦、通义万相等图像 provider 承担。

### Provider 边界

- `StoryProvider`
  - 负责故事核心设定。
  - 负责图形化主线节点。
  - 负责漫画分镜脚本。
  - 负责生成每个分镜的 `imagePrompt`。
  - 可选实现：`mock`、`openai`、`deepseek`、`glm`、`minimax`。

- `ImageProvider`
  - 负责根据 `Panel.imagePrompt` 生成或返回分镜图像。
  - 负责输出 `ComicImage` 记录。
  - 不负责改写故事、页数、对白和分镜结构。
  - 可选实现：`mock`、`openai_image`、`minimax_image`、`kling`、`jimeng`、`wanxiang`。

### 交付物

- Provider interface 文档和代码骨架。
- `StoryProvider` 与 `ImageProvider` 分离后的 mock 实现。
- provider 选择配置，例如 `STORY_PROVIDER=mock`、`IMAGE_PROVIDER=mock`。
- 真实 provider 的环境变量占位和错误提示，但不强制接入真实 API。
- 现有 M1-M6 流程不变。
- 后端测试继续覆盖页数策略、每页 1-4 个分镜、短对白、预览和 PDF 导出。

### 文件清单

- `backend/app/providers/story/`
- `backend/app/providers/image/`
- `backend/app/providers/config.py`
- `backend/app/services/story_service.py`
- `backend/app/services/timeline_service.py`
- `backend/app/services/script_service.py`
- `backend/app/services/mock_image_service.py`
- `backend/tests/`
- `docs/ARCHITECTURE.md`
- `docs/API_SPEC.md`
- `README.md`

### 推荐实施步骤

1. 新建 Provider Interface
   - 新增 `backend/app/providers/story/base.py`。
   - 新增 `backend/app/providers/image/base.py`。
   - 使用 `Protocol` 或抽象基类定义接口。
   - 不引入外部依赖。

2. 拆分 Mock Provider
   - 将 `create_outline`、`create_timeline`、`create_script_pages` 移到 `MockStoryProvider`。
   - 将 mock image 生成移到 `MockImageProvider`。
   - 保留 API 响应结构不变。

3. 增加 Provider Config
   - 新增 `backend/app/providers/config.py`。
   - 读取 `STORY_PROVIDER=mock` 和 `IMAGE_PROVIDER=mock`。
   - 未配置时默认 mock。
   - 未知 provider 必须返回清晰错误。

4. 改造服务层依赖
   - `story_service.py` 使用 `get_story_provider()`。
   - `timeline_service.py` 使用 `get_story_provider()`。
   - `script_service.py` 使用 `get_story_provider()`。
   - `mock_image_service.py` 使用 `get_image_provider()`。
   - 服务层不直接 import 具体厂商 provider。

5. 更新测试
   - 保留完整流程测试。
   - 增加 provider 配置测试。
   - 确认页数策略、1-4 分镜、短对白、预览、PDF 导出仍通过。

6. 更新 README
   - 增加本地配置说明：

```bash
export STORY_PROVIDER=mock
export IMAGE_PROVIDER=mock
```

   - 明确 M7 只完成 provider 拆分。
   - 明确真实文本模型和真实图像模型在后续 milestone 接入。
   - 明确 API key 只允许放在后端环境变量，不允许进入前端或 Git。

### 验收标准

- Story 与 Image provider 边界清晰，服务层不直接依赖具体厂商实现。
- 默认配置仍使用 mock provider，现有本地流程可完整跑通。
- DeepSeek 等纯文本模型只能挂到 `StoryProvider`，不得被当作 `ImageProvider`。
- 图像 provider 只能消费已生成的 `imagePrompt` 和 panel 数据，不得改变脚本结构。
- 所有真实 provider 输出必须经过现有结构校验。
- 未配置真实 API key 时必须返回友好错误或自动使用 mock，不能在前端暴露 key。
- 不破坏 M1-M6 API。

### 不允许做的事情

- 不允许把 API key 写入前端、代码或 Git。
- 不允许把 ChatGPT Pro、Codex login、浏览器 cookie 或个人会话当作应用 provider。
- 不允许一次性接入多个真实文本模型和多个真实图像模型。
- 不允许在 M7 接入真实 OpenAI、DeepSeek、GLM、MiniMax API。
- 不允许在 M7 生成真实漫画图片。
- 不允许改变前端主流程。
- 不允许真实图像生成默认一次性跑完整本故事全部分镜。
- 不允许绕过主线确认、页数策略、1-4 分镜、短对白等硬约束。
- 不允许把图像 provider 设计成能改写故事正文。

## M8 真实 StoryProvider 接入

### 目标

在 M7 provider 边界完成后，接入一个真实文本模型作为 `StoryProvider`，用于生成故事核心设定、图形化主线、漫画分镜脚本和每格 `imagePrompt`。M8 只接入一个真实文本 provider，默认仍保留 mock provider 可切换。

### 推荐首选

优先从一个文本 provider 开始，不要同时接多个。可选优先级：

1. `openai`
2. `deepseek`
3. `glm`
4. `minimax`

DeepSeek 可用于文本结构生成，但不能用于图片生成。

### 交付物

- 一个真实 `StoryProvider` 实现。
- `STORY_PROVIDER=<provider>` 环境变量切换。
- 对应 API key 环境变量，例如 `OPENAI_API_KEY`、`DEEPSEEK_API_KEY`、`GLM_API_KEY` 或 `MINIMAX_API_KEY`。
- JSON 输出解析与结构校验。
- 失败时的友好错误和 mock fallback 策略。
- README 中的本地配置说明。

### 文件清单

- `backend/app/providers/story/`
- `backend/app/providers/config.py`
- `backend/app/services/story_service.py`
- `backend/app/services/timeline_service.py`
- `backend/app/services/script_service.py`
- `backend/tests/`
- `README.md`

### 推荐实施步骤

1. 选择一个文本 provider。
2. 定义 provider 请求 prompt，要求输出严格 JSON。
3. 在后端读取对应 API key，禁止前端接触 key。
4. 实现 outline、timeline、script 三类文本生成。
5. 对模型输出做 JSON parse。
6. 对 parse 后的数据执行现有结构校验。
7. 失败时返回友好错误，或在本地配置允许时回退 mock。
8. 增加测试覆盖 provider 缺 key、JSON 解析失败、结构不合格等场景。

### 验收标准

- `STORY_PROVIDER=mock` 时现有流程不变。
- `STORY_PROVIDER=<real>` 时，outline、timeline、script 可由真实文本模型生成。
- 主线仍必须先确认，不能跳过。
- 脚本仍必须满足当前页数策略。
- 每页仍必须 1-4 个分镜。
- 对白仍必须短。
- `imagePrompt` 必须存在，供 M9 图像 provider 使用。
- API key 不出现在前端、日志、Git 或返回值中。

### 不允许做的事情

- 不允许同时接入多个真实文本 provider。
- 不允许接入真实图片生成。
- 不允许模型绕过现有结构校验直接落库。
- 不允许把 ChatGPT Pro、Codex login、cookie 或个人 session 作为 provider。
- 不允许把 API key 写进代码或文档示例真实值。

## M9 真实 ImageProvider 接入

### 目标

在 M7 provider 边界完成后，接入一个真实图像模型作为 `ImageProvider`，根据 `Panel.imagePrompt` 生成漫画分镜图像。M9 只接入一个真实图像 provider，并优先支持单 panel 或单页生成，不默认一次性生成整本故事。

### 推荐首选

优先从一个图像 provider 开始，不要同时接多个。可选：

1. `openai_image`
2. `minimax_image`
3. `kling`
4. `jimeng`
5. `wanxiang`

### 交付物

- 一个真实 `ImageProvider` 实现。
- `IMAGE_PROVIDER=<provider>` 环境变量切换。
- 对应 API key 环境变量。
- 单 panel 或单页生成能力。
- 图片状态记录：`pending`、`generated`、`failed`。
- 图片 URI 或本地缓存路径写入 `ComicImage`。
- mock fallback 策略。
- 成本和批量生成风险提示。

### 文件清单

- `backend/app/providers/image/`
- `backend/app/providers/config.py`
- `backend/app/services/mock_image_service.py`
- `backend/app/api/comic.py`
- `backend/data/`
- `frontend/components/comic/`
- `backend/tests/`
- `README.md`

### 推荐实施步骤

1. 选择一个图像 provider。
2. 保留 `POST /api/comic/mock-images` 作为 mock 批量预览入口。
3. 新增或扩展图像生成接口，优先支持单 panel 或单页。
4. 从 `Panel.imagePrompt` 读取 prompt，不允许图像 provider 改写脚本结构。
5. 生成成功后写入 `ComicImage`。
6. 生成失败时记录 `failed` 和错误摘要。
7. 前端展示生成状态、失败重试和 mock fallback。
8. 增加测试覆盖无脚本、无 prompt、生成失败、缓存命中等场景。

### 验收标准

- 默认 `IMAGE_PROVIDER=mock` 时现有流程不变。
- 真实图像 provider 只消费 `imagePrompt`，不得改变故事、页数、分镜和对白。
- 至少支持单 panel 或单页生成。
- 不默认一次性生成整本故事所有分镜。
- 失败时不破坏已有 mock 预览和 PDF 导出。
- API key 不出现在前端、日志、Git 或返回值中。

### 不允许做的事情

- 不允许 DeepSeek 等纯文本模型作为 ImageProvider。
- 不允许默认全量生成整本故事全部图片。
- 不允许图像生成失败时删除已有脚本或主线。
- 不允许把真实图片生成和真实文本生成混在同一个 provider。
- 不允许跳过成本、耗时和失败提示。

## M10 真实工作流稳定化

### 目标

在 M8 和 M9 至少各接入一个真实 provider 后，补齐真实工作流的稳定性、可观测性和本地安全护栏，确保本地测试可控、失败可恢复、成本可预期。

### 交付物

- provider 调用日志摘要，不记录 API key 和完整敏感内容。
- 本地生成次数限制。
- 失败重试策略。
- mock fallback 开关。
- 图片缓存策略。
- README 中的真实 provider 本地测试指南。
- 测试覆盖真实 provider 关闭、mock fallback、结构校验失败等路径。

### 文件清单

- `backend/app/providers/`
- `backend/app/services/`
- `backend/tests/`
- `frontend/components/comic/`
- `README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`

### 验收标准

- 没有 API key 时应用仍可用 mock 完整跑通。
- 真实 provider 失败时有清晰错误，不产生半成品覆盖稳定数据。
- 文本结构不合格时不得落库。
- 图片生成失败时可保留 mock 或已有图片。
- 本地测试成本和调用次数可控。

### 不允许做的事情

- 不允许上线给班级使用。
- 不允许做复杂账号、班级权限或公开部署。
- 不允许记录 API key、cookie、个人 session。
- 不允许为了真实效果放松页数策略、1-4 分镜、短对白、主线确认等硬约束。

## M11 Panel Prompt Builder

### 目标

新增统一 `build_panel_image_prompt(story, page, panel)`，让 OpenAI ImageProvider 和豆包 Seedream ImageProvider 共用同一套单格漫画图片 prompt 构建逻辑。M11 不再让真实 ImageProvider 直接原样消费 `panel.imagePrompt`，而是基于结构化 `story/page/panel` 生成完整、可控、儿童适龄的单格漫画视觉指令。

### 交付物

- 统一 Panel Prompt Builder 设计和实现。
- OpenAI ImageProvider 与豆包 Seedream ImageProvider 共用 prompt builder。
- prompt 融合角色设定、页码和分镜号、场景、镜头、动作、`panel.imagePrompt`、中文对白气泡内容、儿童安全约束和单格漫画构图要求。
- 有对白的 panel 要求图片模型生成清晰中文漫画对白气泡，气泡内只写 `dialogue.text`，不得写角色名、冒号或编号。
- prompt 必须要求用气泡尾巴、指向线和靠近对应角色的位置表达说话角色。
- 无对白的 panel 要求图片模型不要生成文字或对白气泡。
- README、API_SPEC 和架构文档同步说明 M11 行为。

### 文件清单

- `backend/app/providers/image/`
- `backend/tests/`
- `README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/AI_CONTRACT.md`

### 验收标准

- 存在统一 `build_panel_image_prompt(story, page, panel)` 接口。
- OpenAI ImageProvider 和豆包 Seedream ImageProvider 不再各自拼接 prompt。
- `panel.imagePrompt` 仍是核心画面描述，但不再是唯一 prompt 内容。
- prompt 必须包含页码、分镜号和单格漫画约束，明确不生成整页拼图。
- prompt 必须包含儿童安全约束，不允许真实武器、血腥恐怖或危险行为。
- 有对白时，prompt 必须包含中文对白气泡生成要求，且气泡内只允许包含 `dialogue.text`。
- prompt 必须禁止在气泡内写角色名、冒号、编号或额外旁白。
- prompt 必须要求气泡尾巴或指向线指向对应角色，多个气泡按阅读顺序排列且不遮挡角色脸部和关键动作。
- 无对白时，prompt 必须禁止文字和对白气泡。
- 图像 provider 不得修改故事、页数、分镜、对白或主线确认状态。

### 不允许做的事情

- 不允许改变脚本结构。
- 不允许改变每页 1-4 个分镜约束。
- 不允许跳过图形化主线确认。
- 不允许让图片模型生成整页拼图或整本故事。
- 不允许真实图像生成默认一次性跑完整本故事全部分镜。
- 不允许在 prompt builder 中改写对白、扩写剧情或新增角色。
- 不允许把 prompt builder 做成某个单一 provider 的私有逻辑。

## M12 Image Asset Cache 与真实图片预览/PDF 嵌图

### 目标

将真实 ImageProvider 生成的单格图片保存为可复用 Image Asset，并真正展示到漫画预览和 PDF 中。M12 同时解决“文生图成本高，需要历史缓存和候选图管理”以及“已有 `ComicImage.uri` 但前端和 PDF 只显示 uri 文本”的问题。

### 交付物

- Image Asset Cache：保存每次真实生图产物、prompt、`promptHash`、provider、model、size、状态和创建时间。
- 同一 panel 允许保留多张候选图，不覆盖旧图。
- 每个 panel 保存一个 `selectedImageId`，用于前端预览和 PDF 导出。
- 缓存命中规则：相同 `provider + model + size + promptHash + panelId` 默认复用历史图片。
- 用户主动“再生成一张”时创建新候选图，不覆盖已选图片。
- 前端漫画预览中按 `panelId` 渲染真实图片。
- 后端为本地生成图片提供安全可访问的本地预览 URL 或读取接口。
- PDF 导出时把每个 panel 的 `selectedImageId` 对应图片嵌入分镜框。
- 图片缺失、生成失败、远程 URL 不可用时保留清晰占位和错误状态。
- 继续保留按单格或单页生成能力，不新增全量自动生成。

### 文件清单

- `frontend/components/comic/`
- `frontend/lib/types/comic.ts`
- `backend/app/api/`
- `backend/app/export/`
- `backend/app/storage/`
- `backend/tests/`
- `README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`

### 验收标准

- 已生成的单格图片在前端预览中显示为图片，而不是只显示 `uri` 字符串。
- 同一个 panel 可以查看历史候选图，并明确当前选中图片。
- 缓存命中时不得重复调用真实文生图 API。
- 用户重新生成时必须新增候选图，不得覆盖历史候选图。
- 每页仍按 1-4 个分镜拼接，图片必须落入对应分镜框。
- PDF 中每个有选中图片的 panel 应嵌入对应图片，缺图时显示稳定占位。
- PDF 仍保持漫画页结构、分镜边框、页码和必要文本信息。
- 远程 URL 或本地图片读取失败时不得中断整本故事导出。
- 不暴露本地任意文件读取能力，不允许通过图片接口读取非图片数据。

### 不允许做的事情

- 不允许在 M12 做一键全量真实生图。
- 不允许改变故事页数、分镜数量或对白结构。
- 不允许为了嵌图重写整个 PDF 导出架构。
- 不允许把图片读取接口做成任意路径代理。
- 不允许生成新图片时覆盖历史候选图。
- 不允许缓存命中时重复消耗真实生图额度。
- 不允许隐藏生成失败状态。

## M13 批量生成队列、一键自动化与候选图挑选

### 目标

在 M11 prompt 稳定、M12 有 Image Asset Cache 后，增加可控的一键自动化生图流程。M13 允许用户一键为当前故事创建批量生成任务，但必须先查缓存、再按预算生成缺失图片，并提供进度状态、失败重试、单格 prompt 调整和候选图挑选能力。

### 交付物

- 批量生成任务模型和状态记录。
- 一键生成入口：为当前故事缺失选中图片或缓存未命中的 panel 创建队列。
- 队列执行前先查 Image Asset Cache，命中缓存则标记 `skipped` 或 `fromCache`，不调用真实 API。
- 每页/每格生成状态：`pending`、`running`、`generated`、`failed`、`skipped`。
- 单格 prompt 调整入口：允许用户查看 builder 生成的 prompt，编辑后重新生成该 panel。
- 单格结果替换入口：允许用户从候选图里选择最终图片，也允许保留、重试或替换某个 panel 的图片。
- 调用预算限制：限制单次任务最大生图张数、最大重试次数和总调用次数。
- 队列失败可恢复，不覆盖已确认可用图片。

### 文件清单

- `frontend/components/comic/`
- `frontend/lib/api/`
- `frontend/lib/types/`
- `backend/app/api/`
- `backend/app/services/`
- `backend/app/providers/image/`
- `backend/app/storage/`
- `backend/tests/`
- `README.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`

### 验收标准

- 用户可以一键创建批量生图任务，但任务必须受预算限制。
- 一键任务必须优先复用缓存，只有缓存未命中或用户明确要求新候选图时才调用真实 API。
- 用户可以按页查看每个 panel 的生成进度和结果。
- 用户可以对单个 panel 调整 prompt 并重新生成新候选图，不需要重跑整本。
- 用户可以从某个 panel 的候选图中选择最终图片。
- 失败 panel 不影响已成功 panel，不删除脚本、主线或已有图片。
- 任务不会默认无限重试，不会无限消耗 token 或图片额度。
- 自动化流程完成后，M12 的前端预览和 PDF 导出能使用生成结果。

### 不允许做的事情

- 不允许无限制一键生成。
- 不允许跳过缓存直接批量调用真实生图 API。
- 不允许隐藏预计调用次数和当前消耗。
- 不允许失败后自动反复重试到耗尽额度。
- 不允许用户调整 prompt 时改写故事结构、页数、分镜或对白数据。
- 不允许把批量任务设计成必须同步阻塞等待全部完成。
- 不允许绕过 M11 prompt builder 直接调用真实图像 provider。

## M14 故事优先页数与本地项目/预算模型

### 目标

将“固定 32 页”升级为“故事表达优先，但受页数、分镜数和生图预算约束”的 bounded 模式。M14 解决固定页数不利于故事表达的问题，同时避免文生图次数失控。M14 还引入轻量本地项目概念，用于管理故事、缓存、候选图和预算，不引入正式账户系统。

### 交付物

- 本地项目模型：`workspaceId=local_default`、`projectId`、`storyId`。
- 页数策略：例如 `pagePolicy.mode=story_first_bounded`。
- 页数范围：默认 16-48 页。
- 分镜预算：每页 1-4 格，单故事最多 96 个 panel。
- 生图预算：单故事最多生成 96 张图片，单批任务最多 12-24 张图片，每个 panel 最多保留 4 张候选图。
- StoryProvider 生成脚本时根据故事表达决定页数，但必须落在预算范围内。
- UI 和导出逻辑读取实际页数，不再写死 32 页。
- 文档同步替换“固定 32 页”硬约束。

### 文件清单

- `docs/AI_CONTRACT.md`
- `docs/PRD.md`
- `docs/STORY_FLOW.md`
- `docs/UI_RULES.md`
- `docs/DATA_MODEL.md`
- `docs/API_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/MILESTONE.md`
- `README.md`
- `backend/app/services/`
- `backend/app/providers/story/`
- `backend/app/storage/`
- `backend/tests/`
- `frontend/components/`
- `frontend/lib/types/`

### 验收标准

- 系统不再要求故事必须正好 32 页，但必须有明确页数上下限。
- 生成脚本必须满足页数范围、每页 1-4 格、最大 panel 数和短对白约束。
- 生图任务必须受单故事、单批次、单 panel 候选数预算限制。
- 本地项目能隔离不同故事的缓存、候选图和预算记录。
- 旧的 32 页故事数据仍可读取和导出。
- 文档、测试和 UI 文案不再把 32 页作为不可违反硬约束。

### 不允许做的事情

- 不允许无限页数、无限分镜或无限续写。
- 不允许取消主线确认流程。
- 不允许为了故事表达放弃生图预算。
- 不允许在 M14 引入正式账号、登录、班级权限或公开部署。
- 不允许破坏已有 32 页故事的兼容性。
