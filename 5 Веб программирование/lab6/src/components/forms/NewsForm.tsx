import { FormEvent, useState } from "react";

export interface NewsFormValues {
  title: string;
  body: string;
  cover?: string;
}

interface NewsFormProps {
  initialValues?: NewsFormValues;
  submitLabel?: string;
  onSubmit(values: NewsFormValues): Promise<void> | void;
  onCancel?(): void;
  disabled?: boolean;
}

const defaultValues: NewsFormValues = {
  title: "",
  body: "",
  cover: ""
};

export const NewsForm = ({
  initialValues,
  submitLabel = "Сохранить",
  onSubmit,
  onCancel,
  disabled
}: NewsFormProps) => {
  const [values, setValues] = useState<NewsFormValues>(initialValues ?? defaultValues);

  const handleChange = (field: keyof NewsFormValues) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setValues((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    await onSubmit(values);
  };

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      <div className="form-field">
        <label htmlFor="news-title">Заголовок</label>
        <input
          id="news-title"
          type="text"
          value={values.title}
          onChange={handleChange("title")}
          required
          disabled={disabled}
        />
      </div>
      <div className="form-field">
        <label htmlFor="news-body">Контент</label>
        <textarea
          id="news-body"
          value={values.body}
          onChange={handleChange("body")}
          rows={6}
          placeholder="Введите текст новости. Он будет сохранен в JSON поле body."
          required
          disabled={disabled}
        />
      </div>
      <div className="form-field">
        <label htmlFor="news-cover">Обложка (необязательно)</label>
        <input
          id="news-cover"
          type="url"
          value={values.cover ?? ""}
          onChange={handleChange("cover")}
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


