export type ComicImage = {
  id: string;
  panelId: string;
  provider: "mock" | "openai_image" | "real";
  status: "pending" | "generated" | "failed";
  uri: string;
  sourceUri?: string;
  prompt: string;
  promptHash?: string;
  fromCache?: boolean;
  model?: string;
  size?: string;
  width: number;
  height: number;
  style: string;
  error?: string;
};

export type MockImagesRequest = {
  storyId: string;
  panelId?: string;
  pageNumber?: number;
  forceNew?: boolean;
};

export type MockImagesResponse = {
  storyId: string;
  images: ComicImage[];
  imageAssets?: ComicImage[];
  imageCount: number;
  status: "preview_generated";
};

export type GenerationJobItem = {
  panelId: string;
  status: "pending" | "running" | "generated" | "failed" | "skipped" | "completed";
  imageId?: string;
  fromCache: boolean;
  retryCount: number;
  error?: string;
};

export type GenerationJob = {
  id: string;
  storyId: string;
  status: "pending" | "running" | "completed" | "failed";
  budget: {
    maxImages: number;
    maxRetriesPerPanel: number;
  };
  items: GenerationJobItem[];
  createdAt: string;
  completedAt?: string;
};

export type GenerationJobRequest = {
  storyId: string;
  maxImages?: number;
  forceNew?: boolean;
};

export type GenerationJobResponse = {
  storyId: string;
  job: GenerationJob;
  images: ComicImage[];
  imageAssets?: ComicImage[];
  status: "generation_job_completed";
};

export type SelectPanelImageRequest = {
  storyId: string;
  panelId: string;
  imageId: string;
};

export type SelectPanelImageResponse = {
  storyId: string;
  image: ComicImage;
  images: ComicImage[];
  imageAssets?: ComicImage[];
  status: "image_selected";
};
