import type { Tokens } from "../types";

const ACCESS_KEY = "news_app_access";
const REFRESH_KEY = "news_app_refresh";

export const tokenStorage = {
  save(tokens: Tokens) {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
  getAccess() {
    return localStorage.getItem(ACCESS_KEY);
  },
  getRefresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  hydrate(): Tokens | null {
    const access = localStorage.getItem(ACCESS_KEY);
    const refresh = localStorage.getItem(REFRESH_KEY);
    if (!access || !refresh) {
      return null;
    }
    return {
      access_token: access,
      refresh_token: refresh,
      token_type: "bearer"
    };
  }
};

