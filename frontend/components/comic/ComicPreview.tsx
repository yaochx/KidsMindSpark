"use client";

import { useMemo, useState } from "react";
import { PdfExportPanel } from "@/components/export/PdfExportPanel";
import { apiUrl } from "@/lib/api/client";
import {
  createGenerationJob,
  createMockComicImages,
  selectPanelImage
} from "@/lib/api/comic";
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

const MIN_STORY_PAGES = 16;
const MAX_STORY_PAGES = 48;

export function ComicPreview({ storyId, pages }: ComicPreviewProps) {
  const [images, setImages] = useState<ComicImage[]>([]);
  const [imageAssets, setImageAssets] = useState<ComicImage[]>([]);
  const [error, setError] = useState("");
  const [loadingTarget, setLoadingTarget] = useState("");
  const canPreview =
    pages.length >= MIN_STORY_PAGES && pages.length <= MAX_STORY_PAGES;

  const imageByPanelId = useMemo(() => {
    return new Map(images.map((image) => [image.panelId, image]));
  }, [images]);

  const assetsByPanelId = useMemo(() => {
    const grouped = new Map<string, ComicImage[]>();
    imageAssets.forEach((image) => {
      const items = grouped.get(image.panelId) ?? [];
      items.push(image);
      grouped.set(image.panelId, items);
    });
    return grouped;
  }, [imageAssets]);

  async function handleGenerateImages(
    payload: { panelId?: string; pageNumber?: number },
    targetLabel: string
  ) {
    setLoadingTarget(targetLabel);
    setError("");

    try {
      const result = await createMockComicImages({ storyId, ...payload });
      setImages((currentImages) => mergeImages(currentImages, result.images));
      setImageAssets((currentAssets) =>
        mergeAssets(currentAssets, result.imageAssets ?? result.images)
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "漫画预览生成失败。");
    } finally {
      setLoadingTarget("");
    }
  }

  async function handleCreateGenerationJob(forceNew = false) {
    setLoadingTarget(forceNew ? "batch-force" : "batch");
    setError("");

    try {
      const result = await createGenerationJob({ storyId, maxImages: 12, forceNew });
      setImages((currentImages) => mergeImages(currentImages, result.images));
      setImageAssets((currentAssets) =>
        mergeAssets(currentAssets, result.imageAssets ?? result.images)
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "批量生图任务失败。");
    } finally {
      setLoadingTarget("");
    }
  }

  async function handleSelectImage(panelId: string, imageId: string) {
    setLoadingTarget(`select-${imageId}`);
    setError("");

    try {
      const result = await selectPanelImage({ storyId, panelId, imageId });
      setImages(result.images);
      setImageAssets((currentAssets) =>
        mergeAssets(currentAssets, result.imageAssets ?? [result.image])
      );
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "候选图选择失败。");
    } finally {
      setLoadingTarget("");
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
              使用 mock 彩色图像占位展示漫画结构。后续真实图像生成会替换这些占位图。
            </p>
          </div>

          <button
            className="min-h-11 rounded-md bg-emerald-700 px-5 py-3 text-base font-semibold text-white transition hover:bg-emerald-800 disabled:cursor-not-allowed disabled:bg-slate-300"
            disabled={!canPreview || Boolean(loadingTarget)}
            onClick={() => handleGenerateImages({}, "all")}
            type="button"
          >
            {loadingTarget === "all" ? "正在生成完整预览" : "生成完整 mock 预览"}
          </button>
        </div>

        {!canPreview ? (
          <p className="mt-5 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-base text-amber-800">
            请先生成 16-48 页分镜脚本，再生成漫画预览。
          </p>
        ) : null}

        {error ? (
          <p className="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
            {error}
          </p>
        ) : null}

        <div className="mt-5 grid gap-3 rounded-lg border border-emerald-100 bg-emerald-50 p-4 sm:grid-cols-3">
          <p className="text-base font-semibold text-emerald-900">
            页数：{pages.length} 页
          </p>
          <p className="text-base font-semibold text-emerald-900">
            图片记录：{images.length} 张
          </p>
          <p className="text-base font-semibold text-emerald-900">
            状态：{images.length ? "彩色预览已生成" : "等待生成"}
          </p>
        </div>

        {canPreview ? (
          <div className="mt-5 grid gap-3 rounded-lg border border-emerald-100 bg-emerald-50 p-4 sm:grid-cols-3">
            <button
              className="min-h-11 rounded-md border border-emerald-700 bg-white px-4 py-2 text-base font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
              disabled={Boolean(loadingTarget)}
              onClick={() => handleCreateGenerationJob(false)}
              type="button"
            >
              {loadingTarget === "batch" ? "正在生成缺失图像" : "一键生成缺失图像"}
            </button>
            <button
              className="min-h-11 rounded-md border border-emerald-700 bg-white px-4 py-2 text-base font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
              disabled={Boolean(loadingTarget)}
              onClick={() => handleCreateGenerationJob(true)}
              type="button"
            >
              {loadingTarget === "batch-force" ? "正在生成新候选图" : "一键生成新候选图"}
            </button>
            <button
              className="min-h-11 rounded-md border border-emerald-700 bg-white px-4 py-2 text-base font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
              disabled={Boolean(loadingTarget)}
              onClick={() => handleGenerateImages({ pageNumber: 1 }, "page-1")}
              type="button"
            >
              {loadingTarget === "page-1" ? "正在生成第 1 页" : "生成第 1 页图像"}
            </button>
            <button
              className="min-h-11 rounded-md border border-emerald-700 bg-white px-4 py-2 text-base font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
              disabled={Boolean(loadingTarget)}
              onClick={() =>
                handleGenerateImages({ panelId: pages[0].panels[0].id }, "first-panel")
              }
              type="button"
            >
              {loadingTarget === "first-panel" ? "正在生成第 1 格" : "生成第 1 格图像"}
            </button>
            <p className="text-sm leading-6 text-emerald-900">
              真实图像 provider 下请优先批量缺失图、单页或单格生成，避免一次性生成整本故事。
            </p>
          </div>
        ) : null}

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
                  <h3 className="mt-1 text-xl font-bold text-ink">{page.title}</h3>
                </div>
                <p className="rounded-md bg-slate-100 px-3 py-2 text-sm font-semibold text-slate-700">
                  {page.panels.length} 格
                </p>
              </div>
              <button
                className="mb-4 min-h-10 rounded-md border border-emerald-700 bg-white px-4 py-2 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
                disabled={Boolean(loadingTarget)}
                onClick={() =>
                  handleGenerateImages(
                    { pageNumber: page.pageNumber },
                    `page-${page.pageNumber}`
                  )
                }
                type="button"
              >
                {loadingTarget === `page-${page.pageNumber}`
                  ? `正在生成第 ${page.pageNumber} 页`
                  : `生成第 ${page.pageNumber} 页图像`}
              </button>

              <div className="grid gap-3 sm:grid-cols-2">
                {page.panels.map((panel, panelIndex) => {
                  const image = imageByPanelId.get(panel.id);
                  const candidates = assetsByPanelId.get(panel.id) ?? [];
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
                        {image?.status === "generated" && renderableImageSrc(image.uri) ? (
                          // eslint-disable-next-line @next/next/no-img-element
                          <img
                            alt={`${page.title} 第 ${panel.panelNumber} 格`}
                            className="min-h-44 w-full rounded-md border border-white/70 object-cover"
                            src={renderableImageSrc(image.uri)}
                          />
                        ) : (
                          <div className="rounded-md bg-white/80 px-3 py-2 text-sm font-semibold text-slate-800">
                            {image?.uri || "image-pending"}
                          </div>
                        )}
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

                      {image?.status === "failed" ? (
                        <p className="mt-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm leading-6 text-red-700">
                          {image.error ?? "图像生成失败，可重试或切回 mock。"}
                        </p>
                      ) : null}

                      <button
                        className="mt-3 min-h-10 w-full rounded-md border border-slate-700 bg-white px-3 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
                        disabled={Boolean(loadingTarget)}
                        onClick={() =>
                          handleGenerateImages({ panelId: panel.id }, `panel-${panel.id}`)
                        }
                        type="button"
                      >
                        {loadingTarget === `panel-${panel.id}`
                          ? "正在生成本格"
                          : "生成本格图像"}
                      </button>
                      <button
                        className="mt-2 min-h-10 w-full rounded-md border border-slate-700 bg-white px-3 py-2 text-sm font-semibold text-slate-800 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:border-slate-300 disabled:text-slate-400"
                        disabled={Boolean(loadingTarget)}
                        onClick={() =>
                          handleGenerateImages(
                            { panelId: panel.id, forceNew: true },
                            `panel-force-${panel.id}`
                          )
                        }
                        type="button"
                      >
                        {loadingTarget === `panel-force-${panel.id}`
                          ? "正在生成候选图"
                          : "再生成一张候选图"}
                      </button>

                      {candidates.length > 1 ? (
                        <div className="mt-3 grid gap-2">
                          <p className="text-xs font-semibold text-slate-600">
                            候选图：{candidates.length} 张
                          </p>
                          {candidates.map((candidate) => (
                            <button
                              className="min-h-9 rounded-md border border-slate-300 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400"
                              disabled={
                                Boolean(loadingTarget) || candidate.id === image?.id
                              }
                              key={candidate.id}
                              onClick={() => handleSelectImage(panel.id, candidate.id)}
                              type="button"
                            >
                              {candidate.id === image?.id ? "当前选中" : "选择候选图"}
                              {candidate.fromCache ? " / 缓存" : ""}
                            </button>
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
      </div>

      <PdfExportPanel canExport={images.length > 0} storyId={storyId} />
    </section>
  );
}

function mergeImages(currentImages: ComicImage[], newImages: ComicImage[]) {
  const imageByPanelId = new Map(currentImages.map((image) => [image.panelId, image]));
  newImages.forEach((image) => imageByPanelId.set(image.panelId, image));
  return Array.from(imageByPanelId.values());
}

function mergeAssets(currentAssets: ComicImage[], newAssets: ComicImage[]) {
  const imageById = new Map(currentAssets.map((image) => [image.id, image]));
  newAssets.forEach((image) => imageById.set(image.id, image));
  return Array.from(imageById.values());
}

function renderableImageSrc(uri: string) {
  if (uri.startsWith("http://") || uri.startsWith("https://")) {
    return uri;
  }
  if (uri.startsWith("/api/")) {
    return apiUrl(uri);
  }
  return "";
}
