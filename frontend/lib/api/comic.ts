import type { ApiErrorResponse } from "@/lib/types/story";
import type {
  MockImagesRequest,
  MockImagesResponse
} from "@/lib/types/comic";

export async function createMockComicImages(
  payload: MockImagesRequest
): Promise<MockImagesResponse> {
  const response = await fetch("/api/comic/mock-images", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as MockImagesResponse | ApiErrorResponse;

  if (!response.ok) {
    const message = "error" in data ? data.error.message : "漫画预览生成失败。";
    throw new Error(message);
  }

  return data as MockImagesResponse;
}
