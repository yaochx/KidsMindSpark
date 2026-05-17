export type TimelineNodeType =
  | "opening"
  | "hero"
  | "goal"
  | "companion"
  | "obstacle"
  | "twist"
  | "crisis"
  | "resolution"
  | "ending";

export type TimelineNode = {
  id: string;
  type: TimelineNodeType;
  title: string;
  summary: string;
  order: number;
  x?: number;
  y?: number;
  nextNodeIds: string[];
};

export type StoryTimelineRequest = {
  storyId: string;
};

export type StoryTimelineResponse = {
  storyId: string;
  timeline: TimelineNode[];
  status: "outlined" | "timeline_confirmed";
};

export type UpdateStoryTimelineRequest = {
  storyId: string;
  timeline: TimelineNode[];
  confirmed: boolean;
};
