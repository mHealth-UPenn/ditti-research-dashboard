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

import type { AxiosRequestConfig, AxiosResponse } from "axios";

/**
 * API for HTTP client, providing both generic request methods and
 * verb-specific shortcuts (get, post, etc.) that return parsed data.
 */
export interface HttpClientApi {
  /** Generic request method with full config options */
  request: <TResp = unknown, TData = unknown>(
    url: string,
    cfg?: Omit<AxiosRequestConfig<TData>, "url">
  ) => Promise<TResp>;

  /** Request method that returns the full Axios response object */
  requestRawResponse: <TResp = unknown, TData = unknown>(
    url: string,
    cfg?: Omit<AxiosRequestConfig<TData>, "url">
  ) => Promise<AxiosResponse<TResp>>;

  /** GET shortcut that returns the parsed response data */
  get: <TResp = unknown>(
    url: string,
    cfg?: Omit<AxiosRequestConfig, "url" | "method">
  ) => Promise<TResp>;

  /** POST shortcut that returns the parsed response data */
  post: <TResp = unknown>(
    url: string,
    data?: unknown,
    cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
  ) => Promise<TResp>;

  /** PUT shortcut that returns the parsed response data */
  put: <TResp = unknown>(
    url: string,
    data?: unknown,
    cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
  ) => Promise<TResp>;

  /** DELETE shortcut that returns the parsed response data */
  delete: <TResp = unknown>(
    url: string,
    cfg?: Omit<AxiosRequestConfig, "url" | "method">
  ) => Promise<TResp>;

  /** PATCH shortcut that returns the parsed response data */
  patch: <TResp = unknown>(
    url: string,
    data?: unknown,
    cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
  ) => Promise<TResp>;
}
