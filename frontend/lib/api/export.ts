import { apiUrl, readJsonResponse } from "@/lib/api/client";

export async function downloadComicPdf(storyId: string): Promise<Blob> {
  const params = new URLSearchParams({
    storyId,
    format: "a4_preview_pdf"
  });
  const response = await fetch(apiUrl(`/api/export/pdf?${params.toString()}`));

  if (!response.ok) {
    await readJsonResponse(response, "PDF 导出失败。");
  }

  return response.blob();
}
