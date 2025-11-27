import type { NewsItem, CommentItem, UserProfile } from "../types";

const isVerifiedAuthor = (user: UserProfile | null | undefined) =>
  Boolean(user && user.role === "author" && user.is_verified_author);

export const canCreateNews = (user?: UserProfile | null) =>
  Boolean(user && (user.role === "admin" || isVerifiedAuthor(user)));

export const canManageNews = (user: UserProfile | null, news: NewsItem) =>
  Boolean(
    user && (user.role === "admin" || (news.author_id === user.id && isVerifiedAuthor(user)))
  );

export const canManageComment = (user: UserProfile | null, comment: CommentItem) =>
  Boolean(user && (user.role === "admin" || comment.author_id === user.id));

