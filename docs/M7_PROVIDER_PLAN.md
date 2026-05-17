# M7 Provider 拆分开发计划

## 目标

M7 的目标不是马上接入所有真实模型，而是先把生成能力拆成清晰的 provider 边界：

- `StoryProvider`: 负责故事、主线、脚本和 image prompt。
- `ImageProvider`: 负责根据 image prompt 生成或返回图片。

默认仍使用 mock provider，确保本地 MVP 流程稳定可跑。

## 为什么要拆分

漫画应用需要两类能力：

1. 文本结构能力
   - 故事核心设定。
   - 图形化主线。
   - 32 页漫画分镜。
   - 每个分镜的图像提示词。

2. 图像生成能力
   - 根据每个 panel 的 `imagePrompt` 生成漫画图像。
   - 返回 `ComicImage` 数据。
   - 支持失败、重试、缓存和成本控制。

DeepSeek、GLM、OpenAI 文本模型适合第一类。图像能力必须由 OpenAI Images、MiniMax Image、可灵、即梦、通义万相等图像 provider 承担。

## M7 范围

### 必做

1. 新增 provider 目录结构：

```text
backend/app/providers/
  config.py
  story/
    base.py
    mock_story_provider.py
  image/
    base.py
    mock_image_provider.py
```

2. 定义 `StoryProvider` interface：

```python
class StoryProvider:
    def create_outline(self, payload: dict, story_id: str) -> dict: ...
    def create_timeline(self, story: dict) -> list[dict]: ...
    def create_script_pages(self, story: dict) -> list[dict]: ...
```

3. 定义 `ImageProvider` interface：

```python
class ImageProvider:
    def create_images(self, story: dict) -> list[dict]: ...
```

4. 将现有 `backend/app/providers/mock_provider.py` 拆分到两个 mock provider。

5. 增加 provider 配置读取：

```text
STORY_PROVIDER=mock
IMAGE_PROVIDER=mock
```

6. 服务层只依赖 provider interface，不直接依赖具体 mock 实现。

7. 保留所有现有 API：

```text
POST /api/story/outline
POST /api/story/timeline
PUT /api/story/timeline
POST /api/story/script
POST /api/comic/mock-images
GET /api/export/pdf
```

8. 保留所有校验：

- 主线必须 9 个节点。
- 脚本必须 32 页。
- 每页必须 1-4 个分镜。
- 对白必须短。
- PDF 必须基于漫画结构。

### 不做

- 不接入真实 OpenAI、DeepSeek、GLM、MiniMax API。
- 不生成真实漫画图片。
- 不做学生登录、班级邀请码、权限系统。
- 不把 ChatGPT Pro、Codex login、浏览器 cookie 作为 provider。
- 不改变前端主流程。

## 推荐实施步骤

### Step 1: 新建 Provider Interface

- 新增 `story/base.py` 和 `image/base.py`。
- 用 `Protocol` 或抽象基类定义方法。
- 不引入外部依赖。

验收：

- 类型边界清晰。
- 无业务行为变化。

### Step 2: 拆分 Mock Provider

- 将 `create_outline`、`create_timeline`、`create_script_pages` 移到 `MockStoryProvider`。
- 将 mock image 生成移到 `MockImageProvider`。
- 保留旧函数兼容或一次性更新服务层引用。

验收：

- 现有测试全部通过。
- API 响应不变。

### Step 3: 增加 Provider Config

- 新增 `providers/config.py`。
- 读取环境变量：

```text
STORY_PROVIDER=mock
IMAGE_PROVIDER=mock
```

- 未配置时默认 mock。
- 配置未知 provider 时返回清晰错误。

验收：

- 默认本地运行不需要任何 key。
- 错误提示不暴露敏感信息。

### Step 4: 改造服务层依赖

- `story_service.py` 使用 `get_story_provider()`。
- `timeline_service.py` 使用 `get_story_provider()`。
- `script_service.py` 使用 `get_story_provider()`。
- `mock_image_service.py` 使用 `get_image_provider()`。

验收：

- 服务层不直接 import 具体厂商 provider。
- 所有结构校验仍在服务层执行。

### Step 5: 更新测试

- 保留完整流程测试。
- 新增 provider 配置测试：
  - 默认 provider 是 mock。
  - 未知 provider 返回错误或抛出可控异常。
- 确认 32 页、1-4 分镜、短对白测试仍通过。

验收：

```bash
.venv/bin/python -m unittest discover backend/tests
```

全部通过。

### Step 6: 更新 README

新增本地配置说明：

```bash
export STORY_PROVIDER=mock
export IMAGE_PROVIDER=mock
```

并说明：

- M7 只完成 provider 拆分。
- 真实文本模型和真实图像模型在后续 milestone 接入。
- API key 只允许放在后端环境变量，不允许进入前端或 Git。

## 后续建议

### M8: 接入一个真实 StoryProvider

优先接入一个文本模型，不要一次接多个。

可选：

- OpenAI。
- DeepSeek。
- GLM。
- MiniMax。

要求：

- 输出 JSON 必须解析。
- 解析失败要友好报错。
- 结构不合格不得落库。
- 保留 mock fallback。

### M9: 接入一个真实 ImageProvider

优先支持单页或单 panel 生成，不要默认一次生成全部 32 页。

要求：

- 支持成本提示。
- 支持失败重试。
- 支持缓存已生成图片。
- 支持 mock fallback。

## 安全约束

- API key 只放后端环境变量。
- 不允许前端读取或传递 provider key。
- 不允许共享 ChatGPT Pro 账号。
- 不允许使用 Codex login 作为应用认证。
- 不允许把浏览器 cookie、个人 session 或本地 CLI token 当作服务端凭据。
