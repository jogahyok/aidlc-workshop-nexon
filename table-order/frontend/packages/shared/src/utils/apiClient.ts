import axios, { type AxiosInstance, type AxiosError } from 'axios';
import type { ApiError } from '../types/api';

export interface ApiClientConfig {
  baseUrl: string;
  getToken: () => string | null;
  onUnauthorized: () => void;
  onNetworkError?: () => void;
  timeout?: number;
}

/**
 * 인증 인터셉터가 포함된 Axios 인스턴스를 생성합니다.
 */
export function createApiClient(config: ApiClientConfig): AxiosInstance {
  const client = axios.create({
    baseURL: config.baseUrl,
    timeout: config.timeout ?? 10000,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 요청 인터셉터: 토큰 자동 주입
  client.interceptors.request.use((requestConfig) => {
    const token = config.getToken();
    if (token) {
      requestConfig.headers.Authorization = `Bearer ${token}`;
    }
    return requestConfig;
  });

  // 응답 인터셉터: 에러 처리
  client.interceptors.response.use(
    (response) => response,
    (error: AxiosError<ApiError>) => {
      if (error.response?.status === 401) {
        config.onUnauthorized();
      }

      if (!error.response && config.onNetworkError) {
        config.onNetworkError();
      }

      return Promise.reject(error);
    },
  );

  return client;
}
