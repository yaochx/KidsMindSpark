export type ComicImage = {
  id: string;
  panelId: string;
  provider: "mock" | "real";
  status: "pending" | "generated" | "failed";
  uri: string;
  prompt: string;
  width: number;
  height: number;
  style: string;
};

export type MockImagesRequest = {
  storyId: string;
};

export type MockImagesResponse = {
  storyId: string;
  images: ComicImage[];
  status: "preview_generated";
};
