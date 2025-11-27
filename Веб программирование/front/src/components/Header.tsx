import { Link, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export const Header = () => {
  const { user, logout, loading } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    if (location.pathname !== "/") {
      navigate("/");
    }
  };

  return (
    <header className="app-header">
      <div className="app-header__inner">
        <Link to="/" className="brand">
          News Portal
        </Link>
        <nav className="nav-links">
          <Link to="/">Новости</Link>
          <Link to="/auth">Авторизация</Link>
        </nav>
        <div className="auth-status">
          {loading ? (
            <span className="badge">Загрузка...</span>
          ) : user ? (
            <>
              <span className="badge">
                {user.name} ({user.role}
                {user.is_verified_author ? ", автор" : ""})
              </span>
              <button type="button" className="btn btn-secondary" onClick={handleLogout}>
                Выйти
              </button>
            </>
          ) : (
            <Link to="/auth" className="btn btn-primary">
              Войти
            </Link>
          )}
        </div>
      </div>
    </header>
  );
};


