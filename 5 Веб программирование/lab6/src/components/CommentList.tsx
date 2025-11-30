import dayjs from "dayjs";
import { useState } from "react";

import type { CommentItem, UserProfile } from "../types";
import { CommentForm } from "./forms/CommentForm";

interface CommentListProps {
  comments: CommentItem[];
  currentUser: UserProfile | null;
  onUpdate(id: number, text: string): Promise<void>;
  onDelete(id: number): Promise<void>;
  canManage(comment: CommentItem): boolean;
}

export const CommentList = ({
  comments,
  currentUser,
  onUpdate,
  onDelete,
  canManage
}: CommentListProps) => {
  const [editingId, setEditingId] = useState<number | null>(null);

  return (
    <div className="comment-list">
      {comments.length === 0 && <p className="muted">Комментариев пока нет.</p>}
      {comments.map((comment) => {
        const isEditing = editingId === comment.id;
        return (
          <article key={comment.id} className="card comment-card">
            <header>
              <strong>{comment.author?.name ?? `Пользователь #${comment.author_id}`}</strong>
              <span className="muted">{dayjs(comment.publication_date).format("DD.MM.YYYY HH:mm")}</span>
            </header>
            {isEditing ? (
              <CommentForm
                initialText={comment.text}
                submitLabel="Сохранить"
                onCancel={() => setEditingId(null)}
                onSubmit={async (text) => {
                  await onUpdate(comment.id, text);
                  setEditingId(null);
                }}
              />
            ) : (
              <p>{comment.text}</p>
            )}
            {canManage(comment) && !isEditing && (
              <div className="card-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setEditingId(comment.id)}
                >
                  Редактировать
                </button>
                <button
                  type="button"
                  className="btn btn-danger"
                  onClick={() => onDelete(comment.id)}
                  disabled={currentUser == null}
                >
                  Удалить
                </button>
              </div>
            )}
          </article>
        );
      })}
    </div>
  );
};


