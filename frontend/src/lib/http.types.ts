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

import { ResponseBody } from "../types/api";

/**
 * Defines the standardized structure for detailed API error information.
 * Used within `HttpError` to provide context about HTTP failures.
 *
 * @template T The expected type of the `data` field, typically the error response body.
 */
export interface ApiError<T = ResponseBody> {
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
