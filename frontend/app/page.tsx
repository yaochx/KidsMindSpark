import { StoryInputForm } from "@/components/story/StoryInputForm";

const milestones = [
  "M0 项目初始化",
  "M1 故事输入页",
  "M2 主线确认页",
  "M3 32 页分镜脚本页",
  "M4 彩色漫画预览页",
  "M5 PDF 导出",
  "M6 优化与测试"
];

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-10">
      <section className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="rounded-lg border border-amber-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold text-leaf">M5 PDF 导出</p>
          <h1 className="mt-3 text-3xl font-bold text-ink">
            儿童中式/日式彩色漫画故事生成 MVP
          </h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-700">
            先输入故事概念，确认图形化故事主线，生成固定 32 页分镜脚本，再用 mock 图片展示彩色漫画预览，最后导出 A4 PDF 预览。
          </p>
        </header>

        <StoryInputForm />

        <section className="grid gap-4 sm:grid-cols-2">
          {milestones.map((item, index) => (
            <article
              className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
              key={item}
            >
              <p className="text-sm font-semibold text-sun">
                {index < 5 ? "完成" : index === 5 ? "当前" : "待开发"}
              </p>
              <h2 className="mt-2 text-xl font-semibold text-ink">{item}</h2>
            </article>
          ))}
        </section>
      </section>
    </main>
  );
}
