"use client";

import { useMemo, useState } from "react";
import { PdfExportPanel } from "@/components/export/PdfExportPanel";
import { createMockComicImages } from "@/lib/api/comic";
import type { ComicImage } from "@/lib/types/comic";
import type { ScriptPage } from "@/lib/types/script";

type ComicPreviewProps = {
  storyId: string;
  pages: ScriptPage[];
};

const paletteClasses = [
  "from-amber-200 via-orange-100 to-sky-200",
  "from-emerald-200 via-lime-100 to-cyan-200",
  "from-rose-200 via-pink-100 to-violet-200",
  "from-blue-200 via-indigo-100 to-amber-100"
];

export function ComicPreview({ storyId, pages }: ComicPreviewProps) {
  const [images, setImages] = useState<ComicImage[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const imageByPanelId = useMemo(() => {
    return new Map(images.map((image) => [image.panelId, image]));
  }, [images]);

  async function handleGeneratePreview() {
    setIsLoading(true);
    setError("");

    try {
      const result = await createMockComicImages({ storyId });
      setImages(result.images);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "漫画预览生成失败。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="rounded-lg border border-emerald-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-emerald-700">
            M4 彩色漫画预览页
          </p>
          <h2 className="mt-2 text-2xl font-bold text-ink">彩色漫画预览</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-700">
            使用 mock 彩色图像占位展示 32 页漫画结构。后续真实图像生成会替换这些占位图。
          </p>
        </div>

        <button
          className="min-h-11 rounded-md bg-emerald-700 px-5 py-3 text-base font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={pages.length !== 32 || isLoading}
          onClick={handleGeneratePreview}
          type="button"
        >
          {isLoading ? "正在生成彩色预览" : "生成彩色漫画预览"}
        </button>
        </div>

        {pages.length !== 32 ? (
          <p className="mt-5 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-base text-amber-800">
            请先生成固定 32 页分镜脚本，再生成漫画预览。
          </p>
        ) : null}

        {error ? (
          <p className="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
            {error}
          </p>
        ) : null}

        {images.length ? (
          <>
          <div className="mt-5 grid gap-3 rounded-lg border border-emerald-100 bg-emerald-50 p-4 sm:grid-cols-3">
            <p className="text-base font-semibold text-emerald-900">
              页数：{pages.length}/32
            </p>
            <p className="text-base font-semibold text-emerald-900">
              mock 图片：{images.length} 张
            </p>
            <p className="text-base font-semibold text-emerald-900">
              状态：彩色预览已生成
            </p>
          </div>

          <div className="mt-6 grid gap-8">
            {pages.map((page) => (
              <article
                className="mx-auto w-full max-w-3xl rounded-lg border border-slate-300 bg-white p-4 shadow-sm"
                key={page.pageNumber}
              >
                <div className="mb-4 flex items-start justify-between gap-4">
                  <div>
                    <p className="text-sm font-bold text-emerald-700">
                      Page {String(page.pageNumber).padStart(2, "0")}
                    </p>
                    <h3 className="mt-1 text-xl font-bold text-ink">
                      {page.title}
                    </h3>
                  </div>
                  <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
                    {page.panels.length} 格
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-2">
                  {page.panels.map((panel, panelIndex) => {
                    const image = imageByPanelId.get(panel.id);
                    return (
                      <section
                        className="min-h-72 rounded-lg border-2 border-slate-900 bg-white p-2"
                        key={panel.id}
                      >
                        <div
                          className={`flex min-h-44 flex-col justify-between rounded-md bg-gradient-to-br ${
                            paletteClasses[panelIndex % paletteClasses.length]
                          } p-3`}
                        >
                          <div className="rounded-md bg-white/80 px-3 py-2 text-sm font-semibold text-slate-800">
                            {image?.uri ?? "mock-image-pending"}
                          </div>
                          <p className="rounded-md bg-white/80 px-3 py-2 text-base font-semibold leading-6 text-ink">
                            {panel.sceneDescription}
                          </p>
                        </div>

                        {panel.narration ? (
                          <p className="mt-3 rounded-md bg-slate-900 px-3 py-2 text-sm leading-6 text-white">
                            {panel.narration}
                          </p>
                        ) : null}

                        {panel.dialogue.length ? (
                          <div className="mt-3 flex flex-col gap-2">
                            {panel.dialogue.map((line) => (
                              <p
                                className="max-w-full rounded-lg border border-slate-900 bg-white px-3 py-2 text-sm font-semibold leading-6 text-ink"
                                key={`${panel.id}-${line.characterId}-${line.text}`}
                              >
                                {line.characterId}：{line.text}
                              </p>
                            ))}
                          </div>
                        ) : null}
                      </section>
                    );
                  })}
                </div>
              </article>
            ))}
          </div>
          </>
        ) : (
          <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6">
            <h3 className="text-xl font-semibold text-ink">尚未生成漫画预览</h3>
            <p className="mt-3 text-base leading-7 text-slate-700">
              生成后会看到 32 页漫画结构、彩色 mock 图像占位、对白气泡、旁白和页码。
            </p>
          </div>
        )}
      </div>

      <PdfExportPanel canExport={images.length > 0} storyId={storyId} />
    </section>
  );
}
