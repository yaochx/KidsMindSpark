# MindSpark

儿童中式/日式彩色漫画故事生成 MVP。

当前进度：M10 之后规划 M11 Panel Prompt Builder。

## 开发约束

每次开发前先阅读：

1. `docs/AI_CONTRACT.md`
2. `docs/MILESTONE.md`

当前已包含结构化故事输入页、图形化故事主线确认、固定 32 页分镜脚本、彩色漫画 mock 预览、A4 PDF 预览导出、后端集成测试、可选 OpenAI / DeepSeek StoryProvider，以及可选 OpenAI / 豆包 Seedream ImageProvider。下一阶段 M11 将引入统一 Panel Prompt Builder。

## 前端启动

```bash
cd frontend
npm install
npm run dev
```

默认地址：

```text
http://localhost:3000
```

## 后端启动

```bash
.venv/bin/flask --app backend.app run --debug
```

如果本机 `5000` 被系统服务占用，可将后端启动到 `5001`：

```bash
.venv/bin/flask --app backend.app run --debug --host 127.0.0.1 --port 5001
```

前端代理到 `5001`：

```bash
cd frontend
BACKEND_URL=http://127.0.0.1:5001 npm run dev
```

真实文本 provider 生成 32 页脚本可能超过 Next rewrite 代理的默认等待时间。手动验证 DeepSeek 等真实文本生成时，建议在 `frontend/.env.local` 中配置浏览器直连后端：

```text
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:5001
```

后端只允许 `http://localhost:3000` 和 `http://127.0.0.1:3000` 的本地 CORS 请求。

## Provider 配置

默认使用 mock provider，不调用真实模型：

```bash
export STORY_PROVIDER=mock
export IMAGE_PROVIDER=mock
```

也可以复制 `.env.example` 为根目录 `.env`，由后端启动时自动读取：

```bash
cp .env.example .env
```

`.env` 示例：

```text
STORY_PROVIDER=deepseek
DEEPSEEK_API_KEY=<your_api_key>
DEEPSEEK_STORY_MODEL=deepseek-v4-flash
IMAGE_PROVIDER=mock
```

说明：shell 中已 `export` 的同名环境变量优先级更高，`.env` 不会覆盖它们。`.env` 已加入 `.gitignore`，不要提交真实 key。

说明：

- `StoryProvider` 负责故事核心设定、主线、32 页脚本和 `imagePrompt`。
- `ImageProvider` 负责根据 `imagePrompt` 生成或返回图片记录。
- `STORY_PROVIDER=mock` 时仍使用本地 mock，不调用真实模型。
- `STORY_PROVIDER=openai` 时后端通过 OpenAI Responses API 生成故事核心设定、主线和 32 页分镜。
- `STORY_PROVIDER=deepseek` 时后端通过 DeepSeek Chat Completions API 生成故事核心设定、主线和 32 页分镜。
- `IMAGE_PROVIDER=mock` 当前仍使用 mock 图片记录。
- `IMAGE_PROVIDER=openai_image` 时后端通过 OpenAI Images API 生成单页或单格漫画图像。
- `IMAGE_PROVIDER=doubao_seedream` 时后端通过豆包 Seedream 图像生成 API 生成单页或单格漫画图像。
- 真实图像生成必须指定 `panelId` 或 `pageNumber`，不允许默认一次性生成 32 页全部分镜。
- API key 只允许放在后端环境变量中，不能写入前端、代码或 Git。

OpenAI StoryProvider 本地配置示例：

```bash
export STORY_PROVIDER=openai
export OPENAI_API_KEY=<your_api_key>
export OPENAI_STORY_MODEL=gpt-4o-mini
```

`OPENAI_STORY_MODEL` 可不设置，默认使用 `gpt-4o-mini`。没有 API key 时请保持 `STORY_PROVIDER=mock`。

DeepSeek StoryProvider 本地配置示例：

```bash
export STORY_PROVIDER=deepseek
export DEEPSEEK_API_KEY=<your_api_key>
export DEEPSEEK_STORY_MODEL=deepseek-v4-flash
export IMAGE_PROVIDER=mock
```

`DEEPSEEK_STORY_MODEL` 可不设置，默认使用 `deepseek-v4-flash`。DeepSeek 仅作为文本 StoryProvider 使用，不作为 ImageProvider。

OpenAI ImageProvider 本地配置示例：

```bash
export IMAGE_PROVIDER=openai_image
export OPENAI_API_KEY=<your_api_key>
export OPENAI_IMAGE_MODEL=gpt-image-1
export OPENAI_IMAGE_SIZE=1024x1024
```

`OPENAI_IMAGE_MODEL` 和 `OPENAI_IMAGE_SIZE` 可不设置。真实图像会缓存到后端本地 `backend/data/images/`，前端当前优先展示图片记录和状态。

豆包 Seedream ImageProvider 本地配置示例：

```bash
export IMAGE_PROVIDER=doubao_seedream
export DOUBAO_SEEDREAM_API_KEY=<your_api_key>
export DOUBAO_SEEDREAM_MODEL=doubao-seedream-4-0-250828
export DOUBAO_SEEDREAM_SIZE=1024x1024
export DOUBAO_SEEDREAM_RESPONSE_FORMAT=b64_json
```

`DOUBAO_SEEDREAM_MODEL`、`DOUBAO_SEEDREAM_SIZE` 和 `DOUBAO_SEEDREAM_RESPONSE_FORMAT` 可不设置。默认 endpoint 为火山方舟图片生成接口；如果你的控制台给出不同网关，可通过 `DOUBAO_SEEDREAM_ENDPOINT` 覆盖。`b64_json` 响应会缓存到后端本地 `backend/data/images/`，`url` 响应会直接写入图片记录。

## 后端测试

```bash
.venv/bin/python -m unittest discover backend/tests
```

健康检查：

```text
GET http://localhost:5000/health
```

故事核心设定 mock：

```text
POST http://localhost:5000/api/story/outline
```

故事主线 mock：

```text
POST http://localhost:5000/api/story/timeline
PUT http://localhost:5000/api/story/timeline
```

32 页分镜脚本 mock：

```text
POST http://localhost:5000/api/story/script
```

彩色漫画 mock 图片：

```text
POST http://localhost:5000/api/comic/mock-images
```

A4 PDF 预览导出：

```text
GET http://localhost:5000/api/export/pdf?storyId=<story_id>&format=a4_preview_pdf
```

说明：MVP 阶段导出 A4 PDF 预览，PDF 内包含 32 页漫画结构、分镜框、mock 图像占位、旁白、对白和页码。后续可在 M6 之后继续适配 32 开精确打印尺寸与出血边距。

## 里程碑

- M0 项目初始化：已完成。
- M1 故事输入页：已完成。
- M2 主线确认页：已完成。
- M3 32 页分镜脚本页：已完成。
- M4 彩色漫画预览页：已完成。
- M5 PDF 导出：已完成。
- M6 优化与测试：已完成。
- M7 Provider 拆分与真实模型预备层：已完成。
- M8 真实 StoryProvider 接入：已完成。
- M9 真实 ImageProvider 接入：已完成。
- M10 真实工作流稳定化：规划中。
- M11 Panel Prompt Builder：规划中。

## 真实 API 接入路线

当前应用默认使用 mock provider，不调用真实 GPT、DeepSeek、GLM、MiniMax 或图像生成 API。切换到 `STORY_PROVIDER=openai` 后，故事文本生成会调用 OpenAI API；切换到 `STORY_PROVIDER=deepseek` 后，故事文本生成会调用 DeepSeek API；切换到 `IMAGE_PROVIDER=openai_image` 后，单页或单格图像生成会调用 OpenAI Images API；切换到 `IMAGE_PROVIDER=doubao_seedream` 后，单页或单格图像生成会调用豆包 Seedream 图像生成 API。

后续真实 API 接入按阶段推进：

1. M7: 拆分 `StoryProvider` 和 `ImageProvider`，默认仍使用 mock。
2. M8: 接入一个真实文本 provider，用于故事、主线、32 页脚本和 `imagePrompt`。
3. M9: 接入一个真实图像 provider，优先支持单 panel 或单页生成。
4. M10: 补齐 fallback、缓存、错误处理、调用次数限制和测试。
5. M11: 新增 `build_panel_image_prompt(story, page, panel)`，不再让真实 ImageProvider 直接原样消费 `panel.imagePrompt`，而是用结构化 `story/page/panel` 构建完整单格漫画 prompt。

M11 的 prompt builder 会融合角色设定、页码和分镜号、场景、镜头、动作、`panel.imagePrompt`、中文对白气泡内容、儿童安全约束和单格漫画构图要求。默认策略是让豆包 Seedream 等图片模型生成单格画面和中文漫画对白气泡；应用继续负责拼页、边框、页码和 PDF。对白气泡内只允许写 `dialogue.text`，不得写角色名、冒号或编号；说话角色必须通过气泡尾巴、指向线和靠近对应角色的位置表达。

本地 provider 配置示例：

```bash
export STORY_PROVIDER=mock
export IMAGE_PROVIDER=mock
```

OpenAI 文本 provider 配置示例：

```bash
export STORY_PROVIDER=openai
export OPENAI_API_KEY=<your_api_key>
export OPENAI_STORY_MODEL=gpt-4o-mini
export IMAGE_PROVIDER=mock
```

DeepSeek 文本 provider 配置示例：

```bash
export STORY_PROVIDER=deepseek
export DEEPSEEK_API_KEY=<your_api_key>
export DEEPSEEK_STORY_MODEL=deepseek-v4-flash
export IMAGE_PROVIDER=mock
```

OpenAI 图像 provider 配置示例：

```bash
export IMAGE_PROVIDER=openai_image
export OPENAI_API_KEY=<your_api_key>
export OPENAI_IMAGE_MODEL=gpt-image-1
export OPENAI_IMAGE_SIZE=1024x1024
```

豆包 Seedream 图像 provider 配置示例：

```bash
export IMAGE_PROVIDER=doubao_seedream
export DOUBAO_SEEDREAM_API_KEY=<your_api_key>
export DOUBAO_SEEDREAM_MODEL=doubao-seedream-4-0-250828
export DOUBAO_SEEDREAM_SIZE=1024x1024
export DOUBAO_SEEDREAM_RESPONSE_FORMAT=b64_json
```

真实 API key 只能放在后端环境变量中，不能写入前端、代码或 Git。不要使用 ChatGPT Pro、Codex login、浏览器 cookie 或个人 session 作为应用 provider。
