import type {
  ApiErrorResponse,
  StoryOutlineRequest,
  StoryOutlineResponse
} from "@/lib/types/story";
import type {
  StoryTimelineRequest,
  StoryTimelineResponse,
  UpdateStoryTimelineRequest
} from "@/lib/types/timeline";
import type {
  StoryScriptRequest,
  StoryScriptResponse
} from "@/lib/types/script";

export async function createStoryOutline(
  payload: StoryOutlineRequest
): Promise<StoryOutlineResponse> {
  const response = await fetch("/api/story/outline", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as StoryOutlineResponse | ApiErrorResponse;

  if (!response.ok) {
    const message =
      "error" in data ? data.error.message : "故事核心设定生成失败。";
    throw new Error(message);
  }

  return data as StoryOutlineResponse;
}

export async function createStoryTimeline(
  payload: StoryTimelineRequest
): Promise<StoryTimelineResponse> {
  const response = await fetch("/api/story/timeline", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as StoryTimelineResponse | ApiErrorResponse;

  if (!response.ok) {
    const message = "error" in data ? data.error.message : "故事主线生成失败。";
    throw new Error(message);
  }

  return data as StoryTimelineResponse;
}

export async function updateStoryTimeline(
  payload: UpdateStoryTimelineRequest
): Promise<StoryTimelineResponse> {
  const response = await fetch("/api/story/timeline", {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as StoryTimelineResponse | ApiErrorResponse;

  if (!response.ok) {
    const message = "error" in data ? data.error.message : "故事主线保存失败。";
    throw new Error(message);
  }

  return data as StoryTimelineResponse;
}

export async function createStoryScript(
  payload: StoryScriptRequest
): Promise<StoryScriptResponse> {
  const response = await fetch("/api/story/script", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  const data = (await response.json()) as StoryScriptResponse | ApiErrorResponse;

  if (!response.ok) {
    const message = "error" in data ? data.error.message : "分镜脚本生成失败。";
    throw new Error(message);
  }

  return data as StoryScriptResponse;
}
