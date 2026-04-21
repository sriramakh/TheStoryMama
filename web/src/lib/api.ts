import { API_URL } from "./constants";
import type { Story, StoryListResponse, AnimationStyle, JobStatus } from "@/types/story";
import type { CreditBalance, User } from "@/types/user";

async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_URL}${endpoint}`;
  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }

  return res.json();
}

// Public library endpoints
export async function getLibraryStories(params: {
  page?: number;
  per_page?: number;
  category?: string;
  style?: string;
  search?: string;
  orientation?: string;
}): Promise<StoryListResponse> {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.per_page) searchParams.set("per_page", String(params.per_page));
  if (params.category) searchParams.set("category", params.category);
  if (params.style) searchParams.set("style", params.style);
  if (params.search) searchParams.set("search", params.search);
  if (params.orientation) searchParams.set("orientation", params.orientation);
  return fetchAPI<StoryListResponse>(
    `/api/v1/library?${searchParams.toString()}`
  );
}

export async function getStory(storyId: string): Promise<Story> {
  return fetchAPI<Story>(`/api/v1/stories/${storyId}`);
}

export async function getStyles(): Promise<{ styles: AnimationStyle[] }> {
  return fetchAPI<{ styles: AnimationStyle[] }>(`/api/v1/styles`);
}

// Story image URL helper
export function getSceneImageUrl(storyId: string, sceneNum: number): string {
  return `${API_URL}/api/v1/stories/${storyId}/scenes/${sceneNum}/image`;
}

export function getStoryPdfUrl(storyId: string): string {
  return `${API_URL}/api/v1/stories/${storyId}/pdf`;
}

// Authenticated endpoints — routed through Next.js proxy routes that
// handle session → backend JWT minting. No client-side token required.
async function proxyFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API error: ${res.status}`);
  }
  return res.json();
}

export async function generateStory(data: {
  description?: string;
  num_scenes?: number;
  animation_style?: string;
  avatar_ids?: string[];
}): Promise<JobStatus> {
  return proxyFetch<JobStatus>("/api/stories/generate", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

// Avatar endpoints
export interface Avatar {
  id: string;
  name: string;
  type: string;
  description: string | null;
  image_url: string;
  created_at: string;
}

export interface AvatarListResponse {
  avatars: Avatar[];
  quota: number;
  used: number;
  can_create: boolean;
}

export async function listAvatars(): Promise<AvatarListResponse> {
  return proxyFetch<AvatarListResponse>("/api/avatars");
}

export async function createAvatar(data: {
  name: string;
  type: string;
  photo: File;
}): Promise<Avatar> {
  const form = new FormData();
  form.append("name", data.name);
  form.append("type", data.type);
  form.append("photo", data.photo);

  const res = await fetch("/api/avatars/create", {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Avatar creation failed (${res.status})`);
  }
  return res.json();
}

export async function deleteAvatar(avatarId: string): Promise<void> {
  const res = await fetch(`/api/avatars/${avatarId}`, { method: "DELETE" });
  if (!res.ok) {
    throw new Error(`Failed to delete avatar (${res.status})`);
  }
}

export function getAvatarImageUrl(avatarId: string): string {
  return `/api/avatars/${avatarId}/image`;
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return proxyFetch<JobStatus>(`/api/stories/generate/${jobId}`);
}

export async function getUserProfile(token: string): Promise<User> {
  return fetchAPI<User>("/api/v1/users/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getUserCredits(token: string): Promise<CreditBalance> {
  return fetchAPI<CreditBalance>("/api/v1/users/me/credits", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export async function getUserStories(
  token: string,
  page = 1
): Promise<StoryListResponse> {
  return fetchAPI<StoryListResponse>(
    `/api/v1/users/me/stories?page=${page}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
}
