"use client";

import { useState } from "react";
import { downloadComicPdf } from "@/lib/api/export";

type PdfExportPanelProps = {
  storyId: string;
  canExport: boolean;
};

export function PdfExportPanel({ storyId, canExport }: PdfExportPanelProps) {
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleExport() {
    setIsLoading(true);
    setError("");

    try {
      const blob = await downloadComicPdf(storyId);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${storyId}_a4_preview.pdf`;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "PDF 导出失败。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="rounded-lg border border-slate-300 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-700">M5 PDF 导出</p>
          <h2 className="mt-2 text-2xl font-bold text-ink">A4 PDF 预览</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-slate-700">
            导出包含漫画结构、分镜框、mock 图像占位、旁白和对白的 A4 预览 PDF。后续可升级为 32 开精确打印。
          </p>
        </div>

        <button
          className="min-h-11 rounded-md bg-slate-900 px-5 py-3 text-base font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          disabled={!canExport || isLoading}
          onClick={handleExport}
          type="button"
        >
          {isLoading ? "正在导出 PDF" : "导出 A4 PDF"}
        </button>
      </div>

      {!canExport ? (
        <p className="mt-5 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-base text-amber-800">
          请先生成彩色漫画预览，再导出 PDF。
        </p>
      ) : null}

      {error ? (
        <p className="mt-5 rounded-md border border-red-200 bg-red-50 px-4 py-3 text-base text-red-700">
          {error}
        </p>
      ) : null}
    </section>
  );
}
