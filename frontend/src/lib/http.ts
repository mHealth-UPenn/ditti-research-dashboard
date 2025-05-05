/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import axios, {
  AxiosError,
  AxiosHeaders,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  isCancel,
  Method,
  isAxiosError,
} from "axios";
import retry, {
  exponentialDelay,
  isNetworkOrIdempotentRequestError,
} from "axios-retry";
import { ApiError, HttpError } from "./http.types";
import { ResponseBody } from "../types/api";

/**
 * Axios request configuration override.
 * Omits properties handled directly by the `HttpClient` methods (`url`, `method`, `data`).
 * Includes an optional `signal` for AbortController integration,
 * useful for scenarios like React 18 strict-mode cleanup.
 */
type RequestConfig<TData> = Omit<
  AxiosRequestConfig<TData>,
  "url" | "method" | "data" | "signal"
> & {
  /** Abort controller signal for request cancellation. */
  signal?: AbortSignal;
};

/**
 * Centralized HTTP client for API interactions.
 * Features include:
 * - Base URL and timeout configuration.
 * - Automatic JWT and CSRF token management via interceptors.
 * - Request retries with exponential backoff.
 * - Consistent error handling and normalization.
 */
class HttpClient {
  /**
   * The configured Axios instance. Exposed for direct use in specialized cases
   * (e.g., file downloads requiring direct Axios response handling).
   */
  public instance: AxiosInstance;

  /**
   * Initializes the HttpClient.
   * @param baseURL The base URL for all API requests.
   */
  constructor(baseURL: string) {
    this.instance = axios.create({
      baseURL,
      timeout: 30_000,
      withCredentials: true,
      headers: new AxiosHeaders({
        "Content-Type": "application/json",
      }),
      // Treat 2xx and 3xx responses as successful.
      validateStatus: (s) => s >= 200 && s < 400,
    });

    this.registerInterceptors();
    this.registerRetryPolicy();
  }

  /**
   * Performs an HTTP request and returns the response data.
   * Handles interceptors, retries, and error normalization automatically.
   *
   * @template TResp The expected type of the response body data.
   * @template TData The type of the request body data.
   * @param url The target URL path (relative to `baseURL`).
   * @param config Optional request configuration, including method, data, and signal.
   * @returns A promise that resolves with the response data (`TResp`).
   * @throws {HttpError | Error} A normalized error if the request fails.
   */
  async request<TResp = unknown, TData = unknown>(
    url: string,
    {
      method = "GET",
      data,
      signal,
      ...rest
    }: {
      method?: Method;
      data?: TData;
      signal?: AbortSignal;
    } & RequestConfig<TData> = {}
  ): Promise<TResp> {
    try {
      const res: AxiosResponse<TResp> = await this.instance.request({
        url,
        method,
        data,
        signal,
        ...rest,
      });
      return res.data;
    } catch (err) {
      throw this.normalizeError(err);
    }
  }

  /**
   * Performs an HTTP request and returns the full AxiosResponse object.
   * Useful when access to response headers or status code is required.
   * Includes interceptors, retries, and error normalization.
   *
   * @template TResp The expected type of the response body data.
   * @template TData The type of the request body data.
   * @param url The target URL path (relative to `baseURL`).
   * @param config Optional request configuration.
   * @returns A promise that resolves with the full AxiosResponse (`AxiosResponse<TResp>`).
   * @throws {HttpError | Error} A normalized error if the request fails.
   */
  async requestRawResponse<TResp = unknown, TData = unknown>(
    url: string,
    {
      method = "GET",
      data,
      signal,
      ...rest
    }: {
      method?: Method;
      data?: TData;
      signal?: AbortSignal;
    } & RequestConfig<TData> = {}
  ): Promise<AxiosResponse<TResp>> {
    try {
      const res: AxiosResponse<TResp> = await this.instance.request({
        url,
        method,
        data,
        signal,
        ...rest,
      });
      return res;
    } catch (err) {
      throw this.normalizeError(err);
    }
  }

  /** Registers Axios interceptors for request modification and response handling. */
  private registerInterceptors() {
    // Request interceptor: Automatically attach JWT and CSRF tokens.
    this.instance.interceptors.request.use((cfg) => {
      const jwt = localStorage.getItem("jwt");
      const csrf = localStorage.getItem("csrfToken");
      const headers = cfg.headers as AxiosHeaders; // Assume headers are present

      if (jwt && !headers.has("Authorization")) {
        headers.set("Authorization", `Bearer ${jwt}`);
      }
      // Only attach CSRF for potentially state-changing methods.
      if (
        csrf &&
        ["post", "put", "delete"].includes(cfg.method?.toLowerCase() ?? "")
      ) {
        headers.set("X-CSRF-TOKEN", csrf);
      }
      return cfg;
    });

    // Response interceptor: Extract and store tokens from the response body if present.
    this.instance.interceptors.response.use(
      (res) => {
        const body = res.data as ResponseBody | undefined; // Check if body matches expected token structure
        if (body?.jwt) localStorage.setItem("jwt", body.jwt);
        if (body?.csrfAccessToken)
          localStorage.setItem("csrfToken", body.csrfAccessToken);
        return res; // Pass the full response along
      },
      (error: AxiosError) => Promise.reject(error) // Let request catch block handle errors
    );
  }

  /** Configures the automatic retry mechanism using `axios-retry`. */
  private registerRetryPolicy() {
    retry(this.instance, {
      retries: 3,
      retryDelay: exponentialDelay,
      // Retry conditions: network errors, idempotent requests, 5xx server errors, or 429 status.
      retryCondition: (err) =>
        isNetworkOrIdempotentRequestError(err) || err.response?.status === 429,
    });
  }

  /**
   * Normalizes errors from various sources into a consistent `HttpError` or standard `Error`.
   * @param err The caught error object.
   * @returns A normalized error instance.
   */
  private normalizeError(err: unknown): Error {
    if (isCancel(err)) {
      return new Error("Request canceled"); // Consistent error for cancellations.
    }

    if (isAxiosError(err)) {
      // Attempt to provide a hint for common network/CORS issues, especially in Safari.
      const isNetwork = !err.response && !!err.request;
      const corsHint =
        isNetwork && /(Failed to fetch|Network Error)/i.test(err.message)
          ? " (check network connection or CORS configuration)"
          : "";

      const apiErrorDetails: ApiError = {
        message: err.message,
        status: err.response?.status ?? 0, // 0 indicates network error or unknown status
        code: err.code ?? "AXIOS_ERROR",
        data: err.response?.data,
        original: err, // Preserve original error for deeper debugging if needed
      };

      // Wrap details in a custom HttpError.
      return new HttpError(`${err.message}${corsHint}`, apiErrorDetails);
    }

    // If it's already a standard Error, return it directly.
    if (err instanceof Error) {
      return err;
    }

    // Fallback for non-Error throwables.
    return new Error("An unknown error occurred", { cause: err });
  }
}

// --- Singleton Instance ---
// Create and export a single instance of HttpClient for global use.
export const httpClient = new HttpClient(
  // Base URL is configured via environment variables.
  import.meta.env.VITE_FLASK_SERVER as string
);
