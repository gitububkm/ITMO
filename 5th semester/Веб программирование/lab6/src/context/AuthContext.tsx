import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState
} from "react";

import { authApi } from "../api/auth";
import { tokenStorage } from "../lib/tokenStorage";
import type { Tokens, UserProfile } from "../types";

type LoginPayload = { email: string; password: string };
type RegisterPayload = { name: string; email: string; password: string };

interface AuthContextValue {
  user: UserProfile | null;
  loading: boolean;
  login(values: LoginPayload): Promise<void>;
  register(values: RegisterPayload): Promise<void>;
  logout(): Promise<void>;
  logoutAll(): Promise<void>;
  refreshProfile(): Promise<void>;
  tokens: Tokens | null;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

const useInitialTokens = (): Tokens | null => {
  try {
    return tokenStorage.hydrate();
  } catch {
    return null;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [tokens, setTokens] = useState<Tokens | null>(useInitialTokens);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  const loadProfile = useCallback(async () => {
    if (!tokenStorage.getAccess()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const me = await authApi.me();
      setUser(me);
    } catch {
      tokenStorage.clear();
      setTokens(null);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleAuthSuccess = useCallback(async (newTokens: Tokens) => {
    tokenStorage.save(newTokens);
    setTokens(newTokens);
    await loadProfile();
  }, [loadProfile]);

  const login = useCallback(
    async (values: LoginPayload) => {
      const response = await authApi.login(values);
      await handleAuthSuccess(response);
    },
    [handleAuthSuccess]
  );

  const register = useCallback(
    async (values: RegisterPayload) => {
      const response = await authApi.register(values);
      await handleAuthSuccess(response);
    },
    [handleAuthSuccess]
  );

  const logout = useCallback(async () => {
    const refresh = tokenStorage.getRefresh();
    if (refresh) {
      try {
        await authApi.logout(refresh);
      } catch {
        // ignore
      }
    }
    tokenStorage.clear();
    setTokens(null);
    setUser(null);
  }, []);

  const logoutAll = useCallback(async () => {
    try {
      await authApi.logoutAll();
    } finally {
      tokenStorage.clear();
      setTokens(null);
      setUser(null);
    }
  }, []);

  const refreshProfile = useCallback(async () => {
    await loadProfile();
  }, [loadProfile]);

  const value = useMemo(
    () => ({
      user,
      loading,
      login,
      register,
      logout,
      logoutAll,
      refreshProfile,
      tokens
    }),
    [user, loading, login, register, logout, logoutAll, refreshProfile, tokens]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
};


