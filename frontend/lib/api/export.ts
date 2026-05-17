export async function downloadComicPdf(storyId: string): Promise<Blob> {
  const params = new URLSearchParams({
    storyId,
    format: "a4_preview_pdf"
  });
  const response = await fetch(`/api/export/pdf?${params.toString()}`);

  if (!response.ok) {
    const data = (await response.json()) as {
      error?: { message?: string };
    };
    throw new Error(data.error?.message ?? "PDF 导出失败。");
  }

  return response.blob();
}
