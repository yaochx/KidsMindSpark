# MVP API Spec

所有 API 默认使用 mock 行为。本地 JSON 是默认持久化方式。M8 已支持通过后端环境变量切换 OpenAI 或 DeepSeek StoryProvider；M9 已支持通过后端环境变量切换 OpenAI 或豆包 Seedream ImageProvider。M11 已支持使用统一 Panel Prompt Builder 为真实 ImageProvider 构建单格漫画 prompt。M12 已支持真实图片缓存、预览读取和 PDF 嵌图。

Provider 配置示例：

```text
STORY_PROVIDER=mock
IMAGE_PROVIDER=mock
```

OpenAI StoryProvider 配置示例：

```text
STORY_PROVIDER=openai
OPENAI_API_KEY=<your_api_key>
OPENAI_STORY_MODEL=gpt-4o-mini
IMAGE_PROVIDER=mock
```

DeepSeek StoryProvider 配置示例：

```text
STORY_PROVIDER=deepseek
DEEPSEEK_API_KEY=<your_api_key>
DEEPSEEK_STORY_MODEL=deepseek-v4-flash
IMAGE_PROVIDER=mock
```

OpenAI ImageProvider 配置示例：

```text
IMAGE_PROVIDER=openai_image
OPENAI_API_KEY=<your_api_key>
OPENAI_IMAGE_MODEL=gpt-image-1
OPENAI_IMAGE_SIZE=1024x1024
```

豆包 Seedream ImageProvider 配置示例：

```text
IMAGE_PROVIDER=doubao_seedream
DOUBAO_SEEDREAM_API_KEY=<your_api_key>
DOUBAO_SEEDREAM_MODEL=doubao-seedream-4-0-250828
DOUBAO_SEEDREAM_SIZE=1024x1024
DOUBAO_SEEDREAM_RESPONSE_FORMAT=b64_json
```

如火山控制台给出不同网关，可通过 `DOUBAO_SEEDREAM_ENDPOINT` 覆盖默认 endpoint。

真实 API key 只能放在后端环境变量中，不允许出现在前端、Git、日志或 API 响应里。

## 通用错误格式

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求参数不符合要求。",
    "details": {}
  }
}
```

## POST /api/story/outline

### Request

```json
{
  "title": "三只小猫的森林桃源",
  "concept": "三只小猫老大老二老三，拿着猎枪去森林流浪冒险，遇到刺猬、眼珠和奇怪动物，最后发现一座世外桃源。",
  "targetAge": "小学 1-4 年级",
  "visualStyle": "mixed_east_asian_color_comic"
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "title": "三只小猫的森林桃源",
  "safeConcept": "三只小猫老大、老二、老三，带着木头探险杖去森林冒险，遇到刺猬、会眨眼的神秘果实和奇怪动物，最后发现一座世外桃源。",
  "characters": [],
  "status": "outlined"
}
```

### Error

- `VALIDATION_ERROR`: title 或 concept 为空。
- `AGE_UNSUPPORTED`: targetAge 不在 MVP 支持范围内。

### Mock 行为

- 创建 story JSON。
- 将危险道具改写为安全冒险道具。
- 返回核心设定，不生成主线、不生成正文。

### M8 真实 StoryProvider 行为

- 可由真实文本 provider 生成核心设定。
- 输出必须解析为结构化 JSON。
- 解析失败或结构不合格时不得落库。
- 仍必须执行儿童适龄改写和后端校验。

## POST /api/story/timeline

### Request

```json
{
  "storyId": "story_cat_adventure_001"
}
```

真实图像 provider 下必须指定单格或单页目标：

```json
{
  "storyId": "story_cat_adventure_001",
  "panelId": "panel_001_01"
}
```

或：

```json
{
  "storyId": "story_cat_adventure_001",
  "pageNumber": 1
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "timeline": [
    {
      "id": "node_opening",
      "type": "opening",
      "title": "森林边的小路",
      "summary": "三只小猫听说森林深处有一条会发光的小溪。",
      "order": 1,
      "nextNodeIds": ["node_hero"]
    }
  ],
  "status": "outlined"
}
```

### Error

- `STORY_NOT_FOUND`: 找不到 storyId。
- `OUTLINE_REQUIRED`: 尚未生成核心设定。

### Mock 行为

- 生成固定 9 类主线节点：开场、主角、目标、伙伴、阻碍、转折、危机、解决、结局。
- 不生成漫画分镜。

### M8 真实 StoryProvider 行为

- 可由真实文本 provider 生成 9 类主线节点。
- 缺少必需节点、顺序非法或节点过长时必须返回错误。
- 用户确认前仍不得生成漫画分镜。

## PUT /api/story/timeline

### Request

```json
{
  "storyId": "story_cat_adventure_001",
  "timeline": [
    {
      "id": "node_opening",
      "type": "opening",
      "title": "森林边的小路",
      "summary": "三只小猫听说森林深处有一条会发光的小溪。",
      "order": 1,
      "nextNodeIds": ["node_hero"]
    }
  ],
  "confirmed": true
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "timeline": [],
  "status": "timeline_confirmed"
}
```

### Error

- `STORY_NOT_FOUND`: 找不到 storyId。
- `TIMELINE_INVALID`: 缺少必需节点或节点顺序非法。
- `NODE_OVERFLOW`: 节点内容过长，不适合图形化展示。

### Mock 行为

- 校验 9 类节点是否齐全。
- 保存用户编辑后的 timeline。
- `confirmed=true` 时将状态改为 `timeline_confirmed`。

## POST /api/story/script

### Request

```json
{
  "storyId": "story_cat_adventure_001"
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "pageCount": 24,
  "pages": [
    {
      "pageNumber": 1,
      "title": "森林的邀请",
      "storyBeat": "三只小猫在家门口发现一张发光树叶地图。",
      "panels": []
    }
  ],
  "status": "script_generated"
}
```

### Error

- `STORY_NOT_FOUND`: 找不到 storyId。
- `TIMELINE_NOT_CONFIRMED`: 主线尚未确认。
- `SCRIPT_CONSTRAINT_FAILED`: 未满足 16-48 页、每页 1-4 分镜、最多 96 个分镜或短对白约束。

### Mock 行为

- 必须生成 16-48 个 `ScriptPage`。
- 每页生成 1-4 个 `Panel`。
- 每页对白保持短句。
- 单故事最多 96 个 panel。

### M8 真实 StoryProvider 行为

- 可由真实文本 provider 生成 16-48 页分镜脚本。
- 每个 panel 必须包含可供图像 provider 使用的 `imagePrompt`。
- 不满足 16-48 页、1-4 分镜、最多 96 个分镜或短对白约束时必须拒绝落库。

## POST /api/comic/mock-images

### Request

```json
{
  "storyId": "story_cat_adventure_001"
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "images": [
    {
      "id": "img_panel_001_01",
      "panelId": "panel_001_01",
      "provider": "mock",
      "status": "generated",
      "uri": "/mock-images/color-comic-placeholder-001.svg",
      "width": 1024,
      "height": 768
    }
  ],
  "status": "preview_generated"
}
```

### Error

- `STORY_NOT_FOUND`: 找不到 storyId。
- `SCRIPT_REQUIRED`: 尚未生成漫画分镜。
- `IMAGE_TARGET_REQUIRED`: 真实图像 provider 未指定 `panelId` 或 `pageNumber`。
- `IMAGE_PROMPT_REQUIRED`: 目标分镜缺少 `imagePrompt`。
- `PROVIDER_CALL_FAILED`: 真实图像 provider 请求失败。

### Mock 行为

- 为每个 panel 生成一个 mock image 记录。
- 图片可以是本地占位 SVG/PNG 或前端占位 URI。
- 不调用真实图像生成。

### M9 真实 ImageProvider 行为

- 可由真实图像 provider 根据 `Panel.imagePrompt` 生成图片。
- 当前支持单 panel 或单页生成。
- 不默认一次性生成整本故事全部分镜。
- 图像 provider 不得修改故事、页数、分镜和对白结构。
- OpenAI ImageProvider 将 base64 图片保存到后端本地 `backend/data/images/` 并写入 `ComicImage.uri`。
- 豆包 Seedream ImageProvider 支持 `b64_json` 或 `url` 响应；`b64_json` 会保存到后端本地，`url` 会直接写入 `ComicImage.uri`。
- 生成失败时应记录失败状态，并允许 mock fallback。

### M11 Panel Prompt Builder 行为

- 真实 ImageProvider 应使用统一 `build_panel_image_prompt(story, page, panel)` 构建 prompt。
- `panel.imagePrompt` 仍是核心画面描述，但不再是唯一 prompt 内容。
- prompt 必须融合角色设定、页码和分镜号、场景、镜头、动作、中文对白气泡内容、儿童安全约束和单格漫画构图要求。
- 有对白的 panel 应要求图片模型生成清晰中文漫画对白气泡。
- 气泡内只允许写 `dialogue.text`，不得写角色名、冒号、编号或额外旁白。
- 说话角色必须通过气泡尾巴、指向线和靠近对应角色的位置表达；多个气泡应按阅读顺序排列，不能遮挡角色脸部和关键动作。
- 无对白的 panel 应要求图片模型不要生成文字或对白气泡。
- prompt builder 不得修改 story、page、panel、对白、页数或主线确认状态。

### M12 真实图片预览与 PDF 嵌图行为

- 真实生图产物应保存为 Image Asset，记录 `storyId`、`panelId`、`provider`、`model`、`size`、`promptHash`、`prompt`、`uri`、`status`、`createdAt`。
- 同一 panel 可以保留多张候选图，panel 使用 `selectedImageId` 指向最终选择。
- 相同 `provider + model + size + promptHash + panelId` 命中缓存时，默认复用历史图片，不重复调用真实生图 API。
- 前端应把 `ComicImage.uri` 渲染为真实图片，而不是只显示 uri 文本。
- 后端可提供受限图片读取接口，用于读取本地生成图片；接口不得允许任意路径访问。
- PDF 导出应把已选中图片嵌入对应 panel 分镜框。
- 缺图、图片读取失败或远程 URL 不可用时，应保留占位和错误状态，不得中断整本 PDF 导出。

### M13 批量生成队列行为

- 可新增批量任务 API，为缺失图片的 panel 创建生成队列。
- 批量任务必须记录每个 panel 的状态、错误摘要和重试次数。
- 批量任务必须先查 Image Asset Cache，缓存命中时不得消耗真实生图额度。
- 一键自动化必须受预算限制，例如单任务最大图片数、最大重试次数和总调用次数。
- 用户必须能按单个 panel 调整 prompt 并生成新候选图，不需要重跑整本。
- 用户必须能从候选图中选择某个 panel 的最终图片。
- 批量任务不得修改故事、页数、分镜、对白或已确认主线。

## POST /api/comic/generation-jobs

### Request

```json
{
  "storyId": "story_cat_adventure_001",
  "maxImages": 12,
  "forceNew": false
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "job": {
    "id": "job_001",
    "storyId": "story_cat_adventure_001",
    "status": "completed",
    "budget": {
      "maxImages": 12,
      "maxRetriesPerPanel": 0
    },
    "items": []
  },
  "images": [],
  "imageAssets": [],
  "status": "generation_job_completed"
}
```

### M13 行为

- `maxImages` 必须在 1-24 之间。
- 默认只为缺失选中图片的 panel 创建任务。
- `forceNew=true` 时会为目标 panel 生成新候选图。
- 执行前必须优先复用 Image Asset Cache。

## PUT /api/comic/images/select

### Request

```json
{
  "storyId": "story_cat_adventure_001",
  "panelId": "panel_001_01",
  "imageId": "img_panel_001_01_xxxxxxxx"
}
```

### Response

```json
{
  "storyId": "story_cat_adventure_001",
  "image": {},
  "images": [],
  "imageAssets": [],
  "status": "image_selected"
}
```

### M13 行为

- 只能选择属于该 `panelId` 的已存在候选图。
- 选择后会更新该 panel 的 `selectedImageId`，并更新当前预览使用的 `images`。

### M14 故事优先页数与预算行为

- 已将固定 32 页升级为 `story_first_bounded` 页数策略。
- 默认建议页数范围为 16-48 页，每页 1-4 格，单故事最多 96 个 panel。
- 生图预算应限制单故事最大生成图片数、单批任务最大生成图片数、每个 panel 最大候选图数量。
- 本地 MVP 可先使用 `workspaceId=local_default` 和 `projectId` 管理故事、缓存、候选图和预算，不引入账号登录。

## GET /api/comic/images/:imageId

### Request

```text
/api/comic/images/img_panel_001_01_xxxxxxxx
```

### Response

成功时返回 `image/png` 文件流。

### Error

- `IMAGE_NOT_FOUND`: 找不到图片，或 `imageId` 不符合安全命名规则。

### M12 行为

- 只允许读取后端本地 images 目录下由系统生成的 PNG。
- 不允许通过该接口读取任意本地路径。
- 前端漫画预览可使用该接口渲染真实单格图片。

## GET /api/export/pdf

### Request

Query:

```text
/api/export/pdf?storyId=story_cat_adventure_001&format=a4_preview_pdf
```

### Response

成功时返回 PDF 文件流，或在异步模式下返回：

```json
{
  "exportJobId": "export_001",
  "storyId": "story_cat_adventure_001",
  "format": "a4_preview_pdf",
  "status": "completed",
  "outputUri": "/exports/story_cat_adventure_001_a4_preview.pdf"
}
```

### Error

- `STORY_NOT_FOUND`: 找不到 storyId。
- `PREVIEW_REQUIRED`: 尚未生成漫画预览。
- `EXPORT_FAILED`: PDF 生成失败。

### Mock 行为

- 基于漫画预览结构生成 A4 预览 PDF。
- 不允许只输出纯文本故事。
- 记录 `ExportJob`。
