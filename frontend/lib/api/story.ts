import type {
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
import { apiUrl, readJsonResponse } from "@/lib/api/client";

export async function createStoryOutline(
  payload: StoryOutlineRequest
): Promise<StoryOutlineResponse> {
  const response = await fetch(apiUrl("/api/story/outline"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<StoryOutlineResponse>(response, "故事核心设定生成失败。");
}

export async function createStoryTimeline(
  payload: StoryTimelineRequest
): Promise<StoryTimelineResponse> {
  const response = await fetch(apiUrl("/api/story/timeline"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<StoryTimelineResponse>(response, "故事主线生成失败。");
}

export async function updateStoryTimeline(
  payload: UpdateStoryTimelineRequest
): Promise<StoryTimelineResponse> {
  const response = await fetch(apiUrl("/api/story/timeline"), {
    method: "PUT",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<StoryTimelineResponse>(response, "故事主线保存失败。");
}

export async function createStoryScript(
  payload: StoryScriptRequest
): Promise<StoryScriptResponse> {
  const response = await fetch(apiUrl("/api/story/script"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  return readJsonResponse<StoryScriptResponse>(response, "分镜脚本生成失败。");
}
