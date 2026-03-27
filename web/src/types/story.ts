export interface Character {
  name: string;
  type: string;
  description: string;
}

export interface Scene {
  scene_number: number;
  text: string;
  background: string;
  image_description: string;
  image_url?: string;
}

export interface Story {
  id: string;
  title: string;
  setting: string;
  art_style: string;
  moral?: string;
  characters: Character[];
  scenes: Scene[];
  animation_style?: string;
  category?: string;
  categories?: string[];
  tags?: string[];
  cover_image_url?: string;
  scene_count?: number;
  created_at?: string;
  pdf_url?: string;
  is_public?: boolean;
}

export interface StoryListResponse {
  stories: Story[];
  total: number;
  page: number;
  per_page: number;
}

export interface AnimationStyle {
  id: string;
  name: string;
  description: string;
}

export interface JobStatus {
  job_id: string;
  status:
    | "queued"
    | "generating_story"
    | "generating_images"
    | "overlaying_text"
    | "compiling_video"
    | "compiling_pdf"
    | "completed"
    | "failed";
  progress: number;
  message?: string;
  story_id?: string;
}

export type StoryCategory =
  | "animals"
  | "adventure"
  | "friendship"
  | "fantasy"
  | "nature"
  | "family"
  | "seasons"
  | "bedtime"
  | "funny"
  | "learning";
