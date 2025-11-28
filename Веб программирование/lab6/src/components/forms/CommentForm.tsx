import { FormEvent, useState } from "react";

interface CommentFormProps {
  initialText?: string;
  submitLabel?: string;
  onSubmit(text: string): Promise<void> | void;
  onCancel?(): void;
  disabled?: boolean;
}

export const CommentForm = ({
  initialText = "",
  submitLabel = "Отправить",
  onSubmit,
  onCancel,
  disabled
}: CommentFormProps) => {
  const [text, setText] = useState(initialText);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await onSubmit(text);
    if (!initialText) {
      setText("");
    }
  };

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      <div className="form-field">
        <label htmlFor="comment-text">Комментарий</label>
        <textarea
          id="comment-text"
          rows={4}
          value={text}
          onChange={(event) => setText(event.target.value)}
          required
          disabled={disabled}
        />
      </div>
      <div className="form-actions">
        {onCancel && (
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={disabled}>
            Отмена
          </button>
        )}
        <button type="submit" className="btn btn-primary" disabled={disabled}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
};


