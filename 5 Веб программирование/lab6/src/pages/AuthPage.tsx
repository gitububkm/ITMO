import { FormEvent, useCallback, useEffect, useState } from "react";

import { authApi } from "../api/auth";
import { useAuth } from "../context/AuthContext";

interface LoginFormState {
  email: string;
  password: string;
}

interface RegisterFormState {
  name: string;
  email: string;
  password: string;
}

export const AuthPage = () => {
  const { user, login, register, logoutAll, loading } = useAuth();
  const [loginForm, setLoginForm] = useState<LoginFormState>({ email: "", password: "" });
  const [registerForm, setRegisterForm] = useState<RegisterFormState>({
    name: "",
    email: "",
    password: ""
  });
  const [submitState, setSubmitState] = useState<"idle" | "login" | "register" | "logoutAll">("idle");
  const [error, setError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Array<{ token_prefix: string; user_agent?: string; created_at: string }>>([]);

  const loadSessions = useCallback(async () => {
    if (!user) {
      setSessions([]);
      return;
    }
    try {
      const data = await authApi.sessions();
      setSessions(data);
    } catch (err) {
      console.error(err);
    }
  }, [user]);

  useEffect(() => {
    void loadSessions();
  }, [loadSessions]);

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitState("login");
    try {
      await login(loginForm);
      setLoginForm({ email: "", password: "" });
      await loadSessions();
    } catch (err) {
      console.error(err);
      setError("Ошибка входа. Проверьте данные.");
    } finally {
      setSubmitState("idle");
    }
  };

  const handleRegister = async (event: FormEvent) => {
    event.preventDefault();
    setError(null);
    setSubmitState("register");
    try {
      await register(registerForm);
      setRegisterForm({ name: "", email: "", password: "" });
      await loadSessions();
    } catch (err) {
      console.error(err);
      setError("Ошибка регистрации. Возможен дубликат email.");
    } finally {
      setSubmitState("idle");
    }
  };

  const handleLogoutAll = async () => {
    setSubmitState("logoutAll");
    try {
      await logoutAll();
      setSessions([]);
    } finally {
      setSubmitState("idle");
    }
  };

  return (
    <div className="grid-2">
      <section className="card">
        <h2>Вход</h2>
        <p className="muted">Используйте email и пароль, созданные в API.</p>
        <form className="stack-sm" onSubmit={handleLogin}>
          <div className="form-field">
            <label htmlFor="login-email">Email</label>
            <input
              id="login-email"
              type="email"
              value={loginForm.email}
              onChange={(event) => setLoginForm((prev) => ({ ...prev, email: event.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <div className="form-field">
            <label htmlFor="login-password">Пароль</label>
            <input
              id="login-password"
              type="password"
              value={loginForm.password}
              onChange={(event) => setLoginForm((prev) => ({ ...prev, password: event.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitState !== "idle"}>
            Войти
          </button>
        </form>
      </section>

      <section className="card">
        <h2>Регистрация</h2>
        <p className="muted">Создайте нового пользователя. Роль по умолчанию — USER.</p>
        <form className="stack-sm" onSubmit={handleRegister}>
          <div className="form-field">
            <label htmlFor="reg-name">Имя</label>
            <input
              id="reg-name"
              type="text"
              value={registerForm.name}
              onChange={(event) => setRegisterForm((prev) => ({ ...prev, name: event.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <div className="form-field">
            <label htmlFor="reg-email">Email</label>
            <input
              id="reg-email"
              type="email"
              value={registerForm.email}
              onChange={(event) => setRegisterForm((prev) => ({ ...prev, email: event.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <div className="form-field">
            <label htmlFor="reg-password">Пароль</label>
            <input
              id="reg-password"
              type="password"
              value={registerForm.password}
              onChange={(event) => setRegisterForm((prev) => ({ ...prev, password: event.target.value }))}
              required
              disabled={loading}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={submitState !== "idle"}>
            Зарегистрироваться
          </button>
        </form>
      </section>

      <section className="card grid-span-2">
        <header className="section-head">
          <div>
            <h2>Статус авторизации</h2>
            <p className="muted">
              {loading
                ? "Проверка токена..."
                : user
                ? `Вы вошли как ${user.name} (${user.role})`
                : "Вы не авторизованы"}
            </p>
          </div>
          {user && (
            <button
              type="button"
              className="btn btn-danger"
              onClick={handleLogoutAll}
              disabled={submitState !== "idle"}
            >
              Выйти из всех сессий
            </button>
          )}
        </header>
        {error && <p className="error">{error}</p>}
        {user && (
          <>
            <p>Активные сессии refresh-токенов:</p>
            <ul className="session-list">
              {sessions.length === 0 && <li className="muted">Сессий не найдено</li>}
              {sessions.map((session) => (
                <li key={session.token_prefix}>
                  <strong>{session.token_prefix}</strong> — {session.user_agent ?? "N/A"} (
                  {new Date(session.created_at).toLocaleString()})
                </li>
              ))}
            </ul>
          </>
        )}
      </section>
    </div>
  );
};


