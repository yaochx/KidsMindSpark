export type ComicImage = {
  id: string;
  panelId: string;
  provider: "mock" | "openai_image" | "real";
  status: "pending" | "generated" | "failed";
  uri: string;
  prompt: string;
  promptHash?: string;
  width: number;
  height: number;
  style: string;
  error?: string;
};

export type MockImagesRequest = {
  storyId: string;
  panelId?: string;
  pageNumber?: number;
};

export type MockImagesResponse = {
  storyId: string;
  images: ComicImage[];
  imageCount: number;
  status: "preview_generated";
};
