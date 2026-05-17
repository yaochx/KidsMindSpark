import type { ApiErrorResponse } from "@/lib/types/story";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function apiUrl(path: string) {
  return `${apiBaseUrl}${path}`;
}

export async function readJsonResponse<T>(
  response: Response,
  fallbackMessage: string
): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    const text = await response.text();
    throw new Error(text.trim() || fallbackMessage);
  }

  const data = (await response.json()) as T | ApiErrorResponse;
  if (!response.ok) {
    const message = "error" in data ? data.error.message : fallbackMessage;
    throw new Error(message);
  }

  return data as T;
}
