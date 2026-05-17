import type {
  MockImagesRequest,
  MockImagesResponse
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
