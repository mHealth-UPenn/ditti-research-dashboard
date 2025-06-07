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

import React, { createContext, ReactNode } from "react";
import { HttpClient } from "../lib/http";
import type { AxiosRequestConfig } from "axios";
import type { HttpClientApi } from "./httpClientContext.types";

// HttpClientContext needs to be exported for the hook to use it.
export const HttpClientContext = createContext<HttpClientApi | null>(null);

export const HttpClientProvider: React.FC<{
  children: ReactNode;
  client: HttpClient;
}> = ({ children, client }) => {
  const api: HttpClientApi = {
    request: client.request.bind(client),
    requestRawResponse: client.requestRawResponse.bind(client),

    // HTTP verb shortcuts
    get: <TResp = unknown,>(
      url: string,
      cfg?: Omit<AxiosRequestConfig, "url" | "method">
    ) => client.request<TResp>(url, { method: "GET", ...cfg }),

    post: <TResp = unknown,>(
      url: string,
      data?: unknown,
      cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
    ) => client.request<TResp>(url, { method: "POST", data, ...cfg }),

    put: <TResp = unknown,>(
      url: string,
      data?: unknown,
      cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
    ) => client.request<TResp>(url, { method: "PUT", data, ...cfg }),

    delete: <TResp = unknown,>(
      url: string,
      cfg?: Omit<AxiosRequestConfig, "url" | "method">
    ) => client.request<TResp>(url, { method: "DELETE", ...cfg }),

    patch: <TResp = unknown,>(
      url: string,
      data?: unknown,
      cfg?: Omit<AxiosRequestConfig, "url" | "method" | "data">
    ) => client.request<TResp>(url, { method: "PATCH", data, ...cfg }),
  };

  return (
    <HttpClientContext.Provider value={api}>
      {children}
    </HttpClientContext.Provider>
  );
};
