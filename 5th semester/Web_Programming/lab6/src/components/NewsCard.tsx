import { Link } from "react-router-dom";
import dayjs from "dayjs";

import type { NewsItem, UserProfile } from "../types";

interface NewsCardProps {
  news: NewsItem;
  author?: UserProfile;
  onDelete?(id: number): Promise<void> | void;
  onEdit?(news: NewsItem): void;
  canManage?: boolean;
}

export const NewsCard = ({ news, author, onDelete, onEdit, canManage }: NewsCardProps) => {
  const publishedAt = dayjs(news.publication_date).format("DD.MM.YYYY HH:mm");

  return (
    <article className="card news-card">
      <header>
        <h3>
          <Link to={`/news/${news.id}`}>{news.title}</Link>
        </h3>
        <p className="muted">
          {publishedAt} • Автор: {author?.name ?? `#${news.author_id}`}
        </p>
      </header>
      <p className="news-preview">
        {typeof news.content === "string"
          ? news.content
          : (news.content as Record<string, unknown>)?.body ?? JSON.stringify(news.content)}
      </p>
      {news.cover && (
        <img src={news.cover} alt={news.title} className="news-cover" />
      )}
      {canManage && (
        <div className="card-actions">
          {onEdit && (
            <button type="button" className="btn btn-secondary" onClick={() => onEdit(news)}>
              Редактировать
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              className="btn btn-danger"
              onClick={() => onDelete(news.id)}
            >
              Удалить
            </button>
          )}
        </div>
      )}
    </article>
  );
};


