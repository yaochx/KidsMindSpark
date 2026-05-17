# MindSpark

儿童中式/日式彩色漫画故事生成 MVP。

当前进度：M6 优化与测试。

## 开发约束

每次开发前先阅读：

1. `docs/AI_CONTRACT.md`
2. `docs/MILESTONE.md`

当前 M6 包含结构化故事输入页、图形化故事主线确认、固定 32 页分镜脚本、彩色漫画 mock 预览、A4 PDF 预览导出，以及后端集成测试。

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
