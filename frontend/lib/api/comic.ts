import type {
  GenerationJobRequest,
  GenerationJobResponse,
  MockImagesRequest,
  MockImagesResponse,
  SelectPanelImageRequest,
  SelectPanelImageResponse
} from "@/lib/types/comic";
import { apiUrl, readJsonResponse } from "@/lib/api/client";

export async function createMockComicImages(
  payload: MockImagesRequest
): Promise<MockImagesResponse> {
  const response = await fetch(apiUrl("/api/comic/mock-images"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<MockImagesResponse>(response, "漫画预览生成失败。");
}

export async function createGenerationJob(
  payload: GenerationJobRequest
): Promise<GenerationJobResponse> {
  const response = await fetch(apiUrl("/api/comic/generation-jobs"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<GenerationJobResponse>(response, "批量生图任务失败。");
}

export async function selectPanelImage(
  payload: SelectPanelImageRequest
): Promise<SelectPanelImageResponse> {
  const response = await fetch(apiUrl("/api/comic/images/select"), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<SelectPanelImageResponse>(response, "候选图选择失败。");
}
