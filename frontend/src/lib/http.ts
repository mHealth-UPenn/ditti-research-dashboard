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
  AxiosResponse,
  isCancel,
  isAxiosError,
  AxiosRequestConfig,
  InternalAxiosRequestConfig,
} from "axios";
import retry, {
  exponentialDelay,
  isNetworkOrIdempotentRequestError,
} from "axios-retry";
import {
  getCookieValue,
  createSessionExpiredError,
  normalizeError,
} from "./http.helpers";

// Type definitions for the token refresh queue
interface QueueItem {
  resolve: (value?: unknown) => void;
  reject: (reason?: unknown) => void;
}

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
  private instance: AxiosInstance;
  private refreshTokenInProgress = false;
  private tokenRefreshQueue: QueueItem[] = [];

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
   * Processes the queue of requests that were waiting for token refresh
   * @param error Optional error if token refresh failed
   * @param token New token if refresh was successful
   */
  private processQueue(error: Error | null, token: string | null = null): void {
    // Make a copy of the queue and clear it immediately to prevent race conditions
    const queue = [...this.tokenRefreshQueue];
    this.tokenRefreshQueue = [];

    // Process all the requests that were waiting
    queue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });
  }

  /**
   * Performs an HTTP request and returns the response data.
   * Handles interceptors, retries, and error normalization automatically.
   *
   * @template TResp The expected type of the response body data.
   * @template TData The type of the request body data.
   * @param url The target URL path (relative to `baseURL`).
   * @param config Optional request config, including method, data, and signal.
   * @returns A promise that resolves with the response data (`TResp`).
   * @throws {HttpError | Error} A normalized error if the request fails.
   */
  async request<TResp = unknown, TData = unknown>(
    url: string,
    config: Omit<AxiosRequestConfig<TData>, "url"> = {}
  ): Promise<TResp> {
    try {
      const { method = "GET", data, signal, ...rest } = config;
      const res: AxiosResponse<TResp> = await this.instance.request({
        url,
        method,
        data,
        signal,
        ...rest,
      });
      return res.data;
    } catch (err) {
      throw normalizeError(err);
    }
  }

  /**
   * Performs an HTTP request and returns the raw AxiosResponse object.
   * Useful for cases where response headers or the full response status
   * are needed, or for handling non-JSON response types like blobs.
   *
   * @template TResp The expected type of the response body data.
   * @template TData The type of the request body data.
   * @param url The target URL path (relative to `baseURL`).
   * @param config Optional request configuration.
   * @returns A promise that resolves with the full `AxiosResponse<TResp>`.
   * @throws {AxiosError | Error} An AxiosError if the request fails at the
   *     Axios level, or a standard Error for other issues (e.g., cancellation).
   */
  async requestRawResponse<TResp = unknown, TData = unknown>(
    url: string,
    config: Omit<AxiosRequestConfig<TData>, "url"> = {}
  ): Promise<AxiosResponse<TResp>> {
    try {
      const res: AxiosResponse<TResp> = await this.instance.request({
        url,
        ...config,
      });
      return res;
    } catch (err) {
      if (isAxiosError(err)) {
        throw err; // Re-throw for the caller to handle raw response/error data.
      }
      // For other types of errors (network, cancellations), normalize.
      if (isCancel(err)) {
        throw new Error("Request canceled");
      }

      if (err instanceof Error) {
        throw err;
      }

      throw new Error("An unknown error occurred during raw request", {
        cause: err,
      });
    }
  }

  /** Registers interceptors for request modification and response handling. */
  private registerInterceptors() {
    this.instance.interceptors.request.use(
      (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        // Get ID token from cookie and add it to Authorization header
        const idToken = getCookieValue("id_token");
        if (idToken) {
          config.headers.Authorization = `Bearer ${idToken}`;
        }

        // Add CSRF header for state-changing requests. When the SPA is
        // served from a different origin (e.g. Vite dev server on :3000)
        // Axios will not attach the X-XSRF-TOKEN header automatically, so we
        // add it manually using the value from the XSRF-TOKEN cookie.
        if (
          config.method &&
          ["post", "put", "delete", "patch"].includes(
            config.method.toLowerCase()
          )
        ) {
          const xsrfToken = getCookieValue("XSRF-TOKEN");
          if (xsrfToken) {
            config.headers["X-XSRF-TOKEN"] = xsrfToken;
          }
        }

        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // CSRF token rotation is handled via cookies by the backend

        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean;
        };

        // Only handle 401 Unauthorized errors for API endpoints that require
        // a refresh.  Skip auth-related endpoints such as check-login which
        // may legitimately return 401 for the "other" user type.
        const skipRefreshRegex =
          /\/auth\/(participant|researcher)\/check-login/;

        // Handle both 401 Unauthorized AND 422 Unprocessable Content
        const is401 = error.response?.status === 401;
        const is422 = error.response?.status === 422;

        if (
          (is401 || is422) &&
          !originalRequest._retry &&
          !skipRefreshRegex.test(originalRequest.url ?? "")
        ) {
          originalRequest._retry = true;

          // Skip token refresh for the refresh endpoint itself to avoid loops
          if (originalRequest.url === "/api/auth/refresh-token") {
            return Promise.reject(createSessionExpiredError());
          }

          // If a token refresh is already in progress, add this request to the queue
          if (this.refreshTokenInProgress) {
            return new Promise((resolve, reject) => {
              this.tokenRefreshQueue.push({ resolve, reject });
            })
              .then(() => {
                // Once the token is refreshed, retry the request
                return this.instance(originalRequest);
              })
              .catch((err: unknown) => {
                return Promise.reject(normalizeError(err));
              });
          }

          // Start the token refresh process
          this.refreshTokenInProgress = true;

          try {
            // A POST to /api/auth/refresh-token renews the ID/Access tokens as
            // well as the XSRF-TOKEN cookie.  Axios attaches the matching
            // X-XSRF-TOKEN header (added above for cross-origin calls), so no
            // extra payload is required.
            await this.instance.post("/api/auth/refresh-token", null, {
              headers: {
                "Content-Type": "application/json",
              },
            });

            // Token refresh completed successfully
            this.refreshTokenInProgress = false;

            // Get the new ID token from cookies
            const newIdToken = getCookieValue("id_token");

            // Process all queued requests
            this.processQueue(null, newIdToken);

            // Retry the original request
            return await this.instance(originalRequest);
          } catch (refreshError: unknown) {
            // Token refresh failed
            this.refreshTokenInProgress = false;

            const normalizedError = normalizeError(refreshError);

            // Check if it's a CSRF error (status 400 with specific error code)
            const isCSRFError =
              isAxiosError(refreshError) &&
              refreshError.response?.status === 400 &&
              (refreshError.response.data as { code?: string }).code ===
                "CSRF_ERROR";

            // CSRF failure means the session is invalid; force re-login.
            if (isCSRFError) {
              // Simplify by creating a standard session expired error
              const sessionExpiredError = createSessionExpiredError();
              this.processQueue(sessionExpiredError);
              console.error(
                "CSRF Token validation failed during token refresh. Redirecting to login."
              );
              this.redirectToLogin();
              return Promise.reject(sessionExpiredError);
            }

            // Reject all queued requests with the error
            this.processQueue(normalizedError);

            // Log the error and reject the original request
            console.error("Token refresh failed:", normalizedError.message);
            return Promise.reject(normalizedError);
          }
        }

        // Handle all other errors
        return Promise.reject(normalizeError(error));
      }
    );
  }

  /**
   * Redirect to the appropriate login page based on the current URL
   */
  private redirectToLogin(): void {
    // Determine which login page to use
    const currentPath = window.location.pathname;

    // If we're in the coordinator area, go to researcher login
    if (currentPath.startsWith("/coordinator")) {
      window.location.href = "/coordinator/login";
    } else {
      // Otherwise go to participant login
      window.location.href = "/login";
    }
  }

  /** Configures the automatic retry mechanism using `axios-retry`. */
  private registerRetryPolicy() {
    retry(this.instance, {
      retries: 3,
      retryDelay: exponentialDelay,
      // Retry conditions: network errors, idempotent requests, 5xx or 429
      retryCondition: (err) =>
        isNetworkOrIdempotentRequestError(err) || err.response?.status === 429,
    });
  }

  /**
   * Explicitly refreshes the token and CSRF value.
   * Can be called after long periods of inactivity or when performing
   * sensitive operations that require a fresh token.
   *
   * @returns Promise that resolves when token refresh is complete
   */
  public async refreshTokens(): Promise<void> {
    try {
      // Make the token refresh request
      // Axios will automatically include X-XSRF-TOKEN header from XSRF-TOKEN cookie
      await this.instance.post("/api/auth/refresh-token", null, {
        headers: {
          "Content-Type": "application/json",
        },
      });
    } catch (error) {
      console.error("Failed to refresh tokens:", error);

      // If it's a CSRF error, handle it as a session expiration
      if (
        isAxiosError(error) &&
        error.response?.status === 400 &&
        (error.response.data as { code?: string }).code === "CSRF_ERROR"
      ) {
        console.error("CSRF validation failed. Redirecting to login.");
        this.redirectToLogin();
        throw createSessionExpiredError();
      }

      throw normalizeError(error);
    }
  }
}

export const httpClient = new HttpClient(import.meta.env.VITE_FLASK_SERVER);

export { HttpClient };
