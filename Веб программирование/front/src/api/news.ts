import api from "./client";
import type { NewsItem } from "../types";

type NewsPayload = {
  title: string;
  content: Record<string, unknown> | string;
  cover?: string | null;
};

export const newsApi = {
  async list(params?: { skip?: number; limit?: number }): Promise<NewsItem[]> {
    const response = await api.get<NewsItem[]>("/news", { params });
    return response.data;
  },
  async get(id: number): Promise<NewsItem> {
    const response = await api.get<NewsItem>(`/news/${id}`);
    return response.data;
  },
  async create(payload: NewsPayload): Promise<NewsItem> {
    const response = await api.post<NewsItem>("/news", payload);
    return response.data;
  },
  async update(id: number, payload: Partial<NewsPayload>): Promise<NewsItem> {
    const response = await api.put<NewsItem>(`/news/${id}`, payload);
    return response.data;
  },
  async remove(id: number): Promise<void> {
    await api.delete(`/news/${id}`);
  }
};


