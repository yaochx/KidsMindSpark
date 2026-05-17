"use client";

import { useState } from "react";
import { ComicPreview } from "@/components/comic/ComicPreview";
import { createStoryScript } from "@/lib/api/story";
import type { ScriptPage } from "@/lib/types/script";

type ScriptPageListProps = {
  storyId: string;
  canGenerate: boolean;
};

const shotTypeLabels: Record<string, string> = {
  wide: "远景",
  medium: "中景",
  closeup: "特写",
  detail: "细节",
  action: "动作"
};

export function ScriptPageList({ storyId, canGenerate }: ScriptPageListProps) {
  const [pages, setPages] = useState<ScriptPage[]>([]);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleGenerateScript() {
    setIsLoading(true);
    setError("");

    try {
      const result = await createStoryScript({ storyId });
      setPages(result.pages);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "分镜脚本生成失败。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="flex flex-col gap-6">
      <div className="rounded-lg border border-violet-200 bg-white p-5 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-violet-700">
            M3 32 页分镜脚本页
          </p>
          <h2 className="mt-2 text-2xl font-bold text-ink">漫画分镜脚本</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-700">
            基于已确认主线生成固定 32 页脚本。每页 1-4 个分镜，对白保持短句。
          </p>
        </div>

        <button
          className="min-h-11 rounded-md bg-violet-700 px-5 py-3 text-base font-semibold text-white transition hover:bg-violet-800 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={!canGenerate || isLoading}
          onClick={handleGenerateScript}
          type="button"
        >
          {isLoading ? "正在安排 32 页分镜" : "生成 32 页分镜脚本"}
        </button>
        </div>

        {!canGenerate ? (
          <p className="mt-5 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-base text-amber-800">
            请先确认图形化故事主线，再生成 32 页分镜脚本。
          </p>
        ) : null}

        {error ? (
          <p className="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
            {error}
          </p>
        ) : null}

        {pages.length ? (
          <>
          <div className="mt-5 grid gap-3 rounded-lg border border-violet-100 bg-violet-50 p-4 sm:grid-cols-3">
            <p className="text-base font-semibold text-violet-900">
              页数：{pages.length}/32
            </p>
            <p className="text-base font-semibold text-violet-900">
              每页分镜：1-4 个
            </p>
            <p className="text-base font-semibold text-violet-900">
              状态：脚本已生成
            </p>
          </div>

          <div className="mt-6 grid gap-5">
            {pages.map((page) => (
              <article
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                key={page.pageNumber}
              >
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="text-sm font-bold text-violet-700">
                      第 {String(page.pageNumber).padStart(2, "0")} 页
                    </p>
                    <h3 className="mt-1 text-xl font-bold text-ink">
                      {page.title}
                    </h3>
                  </div>
                  <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
                    {page.panels.length} 个分镜
                  </p>
                </div>

                <p className="mt-4 text-base leading-7 text-slate-700">
                  {page.storyBeat}
                </p>

                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  {page.panels.map((panel) => (
                    <section
                      className="rounded-lg border border-slate-200 bg-slate-50 p-4"
                      key={panel.id}
                    >
                      <p className="text-sm font-bold text-slate-600">
                        分镜 {panel.panelNumber} ·{" "}
                        {shotTypeLabels[panel.shotType]}
                      </p>
                      <p className="mt-2 text-base leading-7 text-ink">
                        {panel.sceneDescription}
                      </p>
                      {panel.narration ? (
                        <p className="mt-3 rounded-md bg-white px-3 py-2 text-sm leading-6 text-slate-700">
                          旁白：{panel.narration}
                        </p>
                      ) : null}
                      {panel.dialogue.length ? (
                        <div className="mt-3 flex flex-col gap-2">
                          {panel.dialogue.map((line) => (
                            <p
                              className="rounded-md bg-white px-3 py-2 text-sm leading-6 text-slate-700"
                              key={`${panel.id}-${line.characterId}-${line.text}`}
                            >
                              {line.characterId}：{line.text}
                            </p>
                          ))}
                        </div>
                      ) : null}
                    </section>
                  ))}
                </div>

                <p className="mt-4 text-sm leading-6 text-slate-500">
                  {page.pageNote}
                </p>
              </article>
            ))}
          </div>
          </>
        ) : (
          <div className="mt-6 rounded-lg border border-dashed border-slate-300 bg-slate-50 p-6">
            <h3 className="text-xl font-semibold text-ink">尚未生成分镜脚本</h3>
            <p className="mt-3 text-base leading-7 text-slate-700">
              主线确认后，可以生成固定 32 页分镜脚本，然后继续生成彩色 mock 漫画预览。本阶段仍不会导出 PDF。
            </p>
          </div>
        )}
      </div>

      {pages.length === 32 ? <ComicPreview pages={pages} storyId={storyId} /> : null}
    </section>
  );
}
