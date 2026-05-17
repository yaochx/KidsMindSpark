export type VisualStyle =
  | "chinese_color_comic"
  | "japanese_color_manga"
  | "mixed_east_asian_color_comic";

export type StoryOutlineRequest = {
  title: string;
  concept: string;
  targetAge: string;
  visualStyle: VisualStyle;
};

export type Character = {
  id: string;
  name: string;
  role: "hero" | "companion" | "helper" | "obstacle" | "mystery";
  ageLabel?: string;
  personality: string;
  appearance: string;
  colorPalette: string[];
};

export type StoryOutlineResponse = {
  storyId: string;
  workspaceId?: string;
  projectId?: string;
  title: string;
  safeConcept: string;
  characters: Character[];
  status: "outlined";
};

export type ApiErrorResponse = {
  error: {
    code: string;
    message: string;
    details?: Record<string, string>;
  };
};
