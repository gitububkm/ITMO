import { useEffect, useState } from "react";

import { newsApi } from "../api/news";
import { NewsCard } from "../components/NewsCard";
import { NewsForm, NewsFormValues } from "../components/forms/NewsForm";
import { useAuth } from "../context/AuthContext";
import { canCreateNews } from "../lib/roleUtils";
import type { NewsItem } from "../types";

export const HomePage = () => {
  const { user } = useAuth();
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreator, setShowCreator] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const loadNews = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await newsApi.list({ limit: 50 });
      setNews(data);
    } catch (err) {
      console.error(err);
      setError("Не удалось загрузить новости. Попробуйте позже.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadNews();
  }, []);

  const handleCreateNews = async (values: NewsFormValues) => {
    setFormError(null);
    setSubmitting(true);
    try {
      const payload = {
        title: values.title.trim(),
        content: { body: values.body.trim() },
        cover: values.cover?.trim() || undefined
      };
      const created = await newsApi.create(payload);
      setNews((prev) => [created, ...prev]);
      setShowCreator(false);
    } catch (err) {
      console.error(err);
      setFormError("Не удалось создать новость. Проверьте права и заполненные поля.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="stack-lg">
      <section className="card">
        <div className="section-head">
          <div>
            <h1>Новости</h1>
            <p className="muted">Просматривайте публикации и открывайте детали, чтобы обсудить.</p>
          </div>
          <div className="section-actions">
            <button type="button" className="btn btn-secondary" onClick={() => void loadNews()}>
              Обновить
            </button>
            {canCreateNews(user) && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={() => setShowCreator((prev) => !prev)}
              >
                {showCreator ? "Скрыть форму" : "Создать новость"}
              </button>
            )}
          </div>
        </div>
        {showCreator && (
          <div className="stack-sm">
            <p>Только верифицированные авторы и администраторы могут публиковать новости.</p>
            {formError && <p className="error">{formError}</p>}
            <NewsForm submitLabel="Опубликовать" onSubmit={handleCreateNews} disabled={submitting} />
          </div>
        )}
      </section>

      {error && <p className="error">{error}</p>}
      {loading ? (
        <p>Загрузка ленты...</p>
      ) : (
        <div className="news-grid">
          {news.length === 0 && <p>Пока нет опубликованных новостей.</p>}
          {news.map((item) => (
            <NewsCard key={item.id} news={item} />
          ))}
        </div>
      )}
    </div>
  );
};


