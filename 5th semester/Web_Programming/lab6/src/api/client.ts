import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import type { Tokens } from "../types";
import { tokenStorage } from "../lib/tokenStorage";

export const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000
});

let refreshPromise: Promise<string | null> | null = null;

const triggerTokenRefresh = async (): Promise<string | null> => {
  if (refreshPromise) {
    return refreshPromise;
  }

  const refresh_token = tokenStorage.getRefresh();
  if (!refresh_token) {
    return null;
  }

  refreshPromise = axios
    .post<Tokens>(`${API_URL}/auth/refresh`, { refresh_token })
    .then((response) => {
      tokenStorage.save(response.data);
      return response.data.access_token;
    })
    .catch(() => {
      tokenStorage.clear();
      return null;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
};

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const accessToken = tokenStorage.getAccess();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as (typeof error.config) & {
      _retry?: boolean;
    };

    if (
      error.response?.status === 401 &&
      !originalRequest?._retry &&
      !originalRequest?.url?.includes("/auth/login") &&
      !originalRequest?.url?.includes("/auth/register")
    ) {
      originalRequest._retry = true;
      const newToken = await triggerTokenRefresh();
      if (newToken && originalRequest.headers) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      }
    }

    return Promise.reject(error);
  }
);

export default api;

