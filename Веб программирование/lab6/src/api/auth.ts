import api from "./client";
import type { Tokens, UserProfile } from "../types";

export const authApi = {
  async register(data: { name: string; email: string; password: string }): Promise<Tokens> {
    const response = await api.post<Tokens>("/auth/register", data);
    return response.data;
  },
  async login(data: { email: string; password: string }): Promise<Tokens> {
    const response = await api.post<Tokens>("/auth/login", data);
    return response.data;
  },
  async me(): Promise<UserProfile> {
    const response = await api.get<UserProfile>("/auth/me");
    return response.data;
  },
  async sessions(): Promise<Array<{ token_prefix: string; user_agent?: string; created_at: string }>> {
    const response = await api.get("/auth/sessions");
    return response.data;
  },
  async logout(refresh_token: string): Promise<void> {
    await api.post("/auth/logout", { refresh_token });
  },
  async logoutAll(): Promise<void> {
    await api.delete("/auth/sessions");
  }
};

