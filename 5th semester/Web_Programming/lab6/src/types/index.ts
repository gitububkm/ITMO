export type UserRole = "user" | "author" | "admin";

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  is_verified_author: boolean;
  avatar?: string | null;
  registration_date: string;
}

export interface NewsItem {
  id: number;
  title: string;
  content: Record<string, unknown> | string;
  publication_date: string;
  author_id: number;
  cover?: string | null;
  author?: UserProfile;
}

export interface CommentItem {
  id: number;
  text: string;
  news_id: number;
  author_id: number;
  publication_date: string;
  author?: UserProfile;
}

export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

