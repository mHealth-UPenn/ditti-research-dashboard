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
import { ApiError, HttpError } from "./http.types";
import { ResponseBody } from "../types/api";

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
      throw this.normalizeError(err);
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

        // Add CSRF token for non-GET requests
        if (
          config.method &&
          ["post", "put", "delete", "patch"].includes(
            config.method.toLowerCase()
          )
        ) {
          // Read CSRF token from cookie (single source of truth)
          const csrfToken = getCookieValue("csrf_token") ?? "";

          if (csrfToken) {
            // Use the header name that Flask-WTF expects for AJAX requests
            config.headers["X-CSRFToken"] = csrfToken;

            // For form submissions (urlencoded), add the token only if it
            // hasn't already been added by the caller.
            if (config.data instanceof URLSearchParams) {
              if (!config.data.has("csrf_token")) {
                config.data.append("csrf_token", csrfToken);
              }
            }
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
            return Promise.reject(this.createSessionExpiredError());
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
                return Promise.reject(this.normalizeError(err));
              });
          }

          // Start the token refresh process
          this.refreshTokenInProgress = true;

          try {
            // Special handling for Flask-WTF CSRF protection
            // The key insight is that Flask-WTF expects the CSRF token in:
            // 1. The form data with key "csrf_token", OR
            // 2. The header "X-CSRFToken" AND matching a value in the session cookie

            // For this to work we need to:
            // 1. Send the request with proper Content-Type: application/x-www-form-urlencoded
            // 2. Format the data correctly as form data
            // 3. Include the token in both places

            // Create form URLEncoded data (not FormData)
            const urlEncodedData = new URLSearchParams();

            // Add standard CSRF token
            const csrfToken = getCookieValue("csrf_token") ?? "";

            urlEncodedData.append("csrf_token", csrfToken);

            // Make the token refresh request with proper CSRF token handling
            await this.instance.post(
              "/api/auth/refresh-token",
              urlEncodedData,
              {
                headers: {
                  "Content-Type": "application/x-www-form-urlencoded",
                  "X-CSRFToken": csrfToken,
                },
              }
            );

            // Token refresh completed successfully
            this.refreshTokenInProgress = false;

            // Get the new ID token from cookies
            const newIdToken = getCookieValue("id_token");

            // No longer mirror CSRF token to sessionStorage. Token rotation is
            // handled entirely via cookies set by the backend.

            // Process all queued requests
            this.processQueue(null, newIdToken);

            // Retry the original request
            return await this.instance(originalRequest);
          } catch (refreshError: unknown) {
            // Token refresh failed
            this.refreshTokenInProgress = false;

            const normalizedError = this.normalizeError(refreshError);

            // Check if it's a CSRF error (status 400 with specific error code)
            const isCSRFError =
              isAxiosError(refreshError) &&
              refreshError.response?.status === 400 &&
              (refreshError.response.data as { code?: string }).code ===
                "CSRF_ERROR";

            // For CSRF errors, we need to redirect to login as the session is invalid
            if (isCSRFError) {
              // Simplify by creating a standard session expired error
              const sessionExpiredError = this.createSessionExpiredError();
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
        return Promise.reject(this.normalizeError(error));
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
   * Creates a standardized session expired error
   * @returns A normalized HttpError for session expiration
   */
  private createSessionExpiredError(): HttpError {
    return new HttpError("Session expired. Please log in again", {
      message: "Session expired. Please log in again",
      status: 401,
      code: "SESSION_EXPIRED",
    });
  }

  /**
   * Normalizes errors from various sources into `HttpError` or `Error`.
   * @param err The caught error object.
   * @returns A normalized error instance.
   */
  private normalizeError(err: unknown): HttpError | Error {
    if (isCancel(err)) {
      return new Error("Request canceled");
    }

    if (isAxiosError(err)) {
      // Attempt to provide a hint for common network/CORS issues (e.g., Safari)
      const isNetwork = !err.response && !!err.request;
      const corsHint =
        isNetwork && /(Failed to fetch|Network Error)/i.test(err.message)
          ? " (check network connection or CORS configuration)"
          : "";

      const apiErrorDetails: ApiError = {
        message: err.message,
        status: err.response?.status ?? 0, // 0 == network error or unknown
        code: err.code ?? "AXIOS_ERROR",
        data: err.response?.data as ResponseBody | undefined,
        original: err, // Preserve original error for deeper debugging if needed
      };

      // Extract more specific error info from response if available
      if (err.response?.data && typeof err.response.data === "object") {
        const responseData = err.response.data as Record<string, unknown>;

        // Extract message from msg or message field
        if (responseData.msg && typeof responseData.msg === "string") {
          apiErrorDetails.message = responseData.msg;
        } else if (
          responseData.message &&
          typeof responseData.message === "string"
        ) {
          apiErrorDetails.message = responseData.message;
        }

        // Extract code from code field
        if (responseData.code && typeof responseData.code === "string") {
          apiErrorDetails.code = responseData.code;
        }
      }

      // Wrap details in a custom HttpError.
      return new HttpError(
        `${apiErrorDetails.message}${corsHint}`,
        apiErrorDetails
      );
    }

    // If it's already a HttpError, return it directly
    if (err instanceof HttpError) {
      return err;
    }

    // If it's a standard Error, wrap it in HttpError
    if (err instanceof Error) {
      return new HttpError(err.message, {
        message: err.message,
        status: 0,
        code: "UNKNOWN_ERROR",
        original: err,
      });
    }

    // Fallback for non-Error throwables.
    return new HttpError("An unknown error occurred", {
      message: "An unknown error occurred",
      status: 0,
      code: "UNKNOWN_ERROR",
      original: err,
    });
  }

  public get<TResp = unknown, TData = unknown>(
    url: string,
    config?: AxiosRequestConfig<TData>
  ): Promise<AxiosResponse<TResp>> {
    return this.instance.get<TResp>(url, config);
  }

  public post<TResp = unknown, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig<TData>
  ): Promise<AxiosResponse<TResp>> {
    return this.instance.post<TResp>(url, data, config);
  }

  public put<TResp = unknown, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig<TData>
  ): Promise<AxiosResponse<TResp>> {
    return this.instance.put<TResp>(url, data, config);
  }

  public delete<TResp = unknown, TData = unknown>(
    url: string,
    config?: AxiosRequestConfig<TData>
  ): Promise<AxiosResponse<TResp>> {
    return this.instance.delete<TResp>(url, config);
  }

  public patch<TResp = unknown, TData = unknown>(
    url: string,
    data?: TData,
    config?: AxiosRequestConfig<TData>
  ): Promise<AxiosResponse<TResp>> {
    return this.instance.patch<TResp>(url, data, config);
  }

  /**
   * Explicitly refreshes the token and CSRF value.
   * Can be called after long periods of inactivity or when performing
   * sensitive operations that require a fresh CSRF token.
   *
   * @returns Promise that resolves when token refresh is complete
   */
  public async refreshTokens(): Promise<void> {
    try {
      // Create form URLEncoded data (not FormData)
      const urlEncodedData = new URLSearchParams();

      // Add standard CSRF token
      const csrfToken = getCookieValue("csrf_token") ?? "";

      urlEncodedData.append("csrf_token", csrfToken);

      // Make the token refresh request with proper CSRF token handling
      await this.instance.post("/api/auth/refresh-token", urlEncodedData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "X-CSRFToken": csrfToken,
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
        console.error("CSRF Token validation failed. Redirecting to login.");
        this.redirectToLogin();
        throw this.createSessionExpiredError();
      }

      throw this.normalizeError(error);
    }
  }
}

export const httpClient = new HttpClient(
  import.meta.env.VITE_FLASK_SERVER as string
);

export { HttpClient };

// Helper function to get cookie by name
function getCookieValue(name: string): string | null {
  const nameEQ = name + "=";
  const ca = document.cookie.split(";");
  for (const cookiePart of ca) {
    let c = cookiePart;
    while (c.startsWith(" ")) {
      c = c.substring(1, c.length);
    }
    if (c.startsWith(nameEQ)) {
      return c.substring(nameEQ.length, c.length);
    }
  }
  return null;
}
