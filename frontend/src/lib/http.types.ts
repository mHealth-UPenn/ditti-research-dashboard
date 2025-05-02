/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

/**
 * Defines the standardized structure for detailed API error information.
 * Used within `HttpError` to provide context about HTTP failures.
 *
 * @template T The expected type of the `data` field, typically the error response body.
 */
export interface ApiError<T = unknown> {
  /** The primary error message, often from the underlying error or Axios. */
  message: string;
  /** The HTTP status code associated with the error (0 for network/unknown errors). */
  status: number;
  /** A code representing the error type (e.g., 'AXIOS_ERROR', 'ECONNABORTED', or a server-defined code). */
  code: string;
  /** Optional data payload associated with the error, usually the server's response body. */
  data?: T;
  /** The original error object (e.g., AxiosError) for deeper debugging if necessary. */
  original?: unknown;
}

/**
 * Custom error class for HTTP-related errors originating from the `HttpClient`.
 * Extends the native `Error` class and includes structured API error details.
 */
export class HttpError extends Error {
  /** Structured details about the API error, if available. */
  apiError?: ApiError;

  /**
   * Constructs an `HttpError` instance.
   *
   * @param message A descriptive error message.
   * @param apiError Optional structured details about the API error.
   */
  constructor(message: string, apiError?: ApiError) {
    super(message);
    this.name = "HttpError"; // Standard way to identify custom errors
    this.apiError = apiError;
  }
}
