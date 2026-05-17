export type ShotType = "wide" | "medium" | "closeup" | "detail" | "action";

export type DialogueLine = {
  characterId: string;
  text: string;
};

export type Panel = {
  id: string;
  panelNumber: number;
  shotType: ShotType;
  sceneDescription: string;
  characters: string[];
  narration?: string;
  dialogue: DialogueLine[];
  imagePrompt: string;
  imageId?: string;
};

export type ScriptPage = {
  pageNumber: number;
  title: string;
  storyBeat: string;
  panels: Panel[];
  pageNote: string;
};

export type StoryScriptRequest = {
  storyId: string;
};

export type StoryScriptResponse = {
  storyId: string;
  pageCount: number;
  pages: ScriptPage[];
  status: "script_generated";
};
