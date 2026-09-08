import api from "./client";
import type { CommentItem } from "../types";

type CommentPayload = {
  text: string;
  news_id: number;
};

export const commentsApi = {
  async listByNews(newsId: number): Promise<CommentItem[]> {
    const response = await api.get<CommentItem[]>(`/comments/news/${newsId}`);
    return response.data;
  },
  async create(payload: CommentPayload): Promise<CommentItem> {
    const response = await api.post<CommentItem>("/comments", payload);
    return response.data;
  },
  async update(id: number, payload: { text: string }): Promise<CommentItem> {
    const response = await api.put<CommentItem>(`/comments/${id}`, payload);
    return response.data;
  },
  async remove(id: number): Promise<void> {
    await api.delete(`/comments/${id}`);
  }
};


