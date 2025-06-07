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

import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  AxiosError,
  AxiosHeaders,
  AxiosResponse,
  CanceledError,
  isAxiosError,
  isCancel,
} from "axios";
import {
  getCookieValue,
  createSessionExpiredError,
  normalizeError,
} from "../../src/lib/http.helpers";
import { HttpError } from "../../src/lib/http.types";
import type { InternalAxiosRequestConfig } from "axios";

vi.mock("axios", async (importOriginal) => {
  const actualAxios = await importOriginal<typeof import("axios")>();
  return {
    ...actualAxios,
    isAxiosError: vi.fn(),
    isCancel: vi.fn(),
  };
});

describe("HTTP Helper Functions", () => {
  describe("getCookieValue", () => {
    beforeEach(() => {
      // Setup mock document.cookie
      Object.defineProperty(document, "cookie", {
        writable: true,
        value: "XSRF-TOKEN=abc123; id_token=xyz789; theme=dark",
      });
    });

    it("should return the correct cookie value when present", () => {
      expect(getCookieValue("XSRF-TOKEN")).toBe("abc123");
      expect(getCookieValue("id_token")).toBe("xyz789");
      expect(getCookieValue("theme")).toBe("dark");
    });

    it("should return null when cookie is not found", () => {
      expect(getCookieValue("nonexistent")).toBeNull();
    });

    it("should return cookie value with spaces preserved", () => {
      document.cookie = "spaced= value with spaces ; another=test";
      expect(getCookieValue("spaced")).toBe(" value with spaces ");
    });
  });

  describe("createSessionExpiredError", () => {
    it("should create a properly formatted HttpError for session expiration", () => {
      const error = createSessionExpiredError();
      expect(error).toBeInstanceOf(HttpError);
      expect(error.message).toBe("Session expired. Please log in again");
      expect(error.apiError).toEqual({
        message: "Session expired. Please log in again",
        status: 401,
        code: "SESSION_EXPIRED",
      });
    });
  });

  describe("normalizeError", () => {
    beforeEach(() => {
      vi.mocked(isAxiosError).mockImplementation((err): err is AxiosError => {
        return err instanceof AxiosError;
      });

      vi.mocked(isCancel).mockImplementation((err): boolean => {
        return err instanceof CanceledError;
      });
    });

    it("should handle cancellation errors", () => {
      const cancelError = new CanceledError("Request was canceled");
      vi.mocked(isCancel).mockReturnValueOnce(true);

      const normalized = normalizeError(cancelError);

      expect(normalized).toBeInstanceOf(Error);
      expect(normalized.message).toBe("Request canceled");
    });

    it("should normalize Axios errors with response data", () => {
      const mockConfig: InternalAxiosRequestConfig = {
        headers: new AxiosHeaders(),
      };

      const axiosError = new AxiosError(
        "Request failed",
        "ERR_BAD_REQUEST",
        mockConfig,
        {},
        {
          data: { msg: "Validation failed", code: "VALIDATION_ERROR" },
          status: 400,
          statusText: "Bad Request",
          headers: {},
          config: mockConfig,
        } as AxiosResponse
      );

      vi.mocked(isAxiosError).mockReturnValueOnce(true);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(axiosError);

      expect(normalized).toBeInstanceOf(HttpError);
      expect(normalized.message).toBe("Validation failed");
      expect((normalized as HttpError).apiError?.status).toBe(400);
      expect((normalized as HttpError).apiError?.code).toBe("VALIDATION_ERROR");
    });

    it("should add CORS hint for network errors", () => {
      const networkError = new AxiosError("Network Error");
      delete networkError.response;
      networkError.request = {};

      vi.mocked(isAxiosError).mockReturnValueOnce(true);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(networkError);

      expect(normalized).toBeInstanceOf(HttpError);
      expect(normalized.message).toContain("Network Error");
      expect(normalized.message).toContain(
        "(check network connection or CORS configuration)"
      );
    });

    it("should pass through existing HttpError instances", () => {
      const originalHttpError = new HttpError("Already normalized", {
        message: "Already normalized",
        status: 418,
        code: "TEAPOT",
      });

      vi.mocked(isAxiosError).mockReturnValueOnce(false);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(originalHttpError);

      expect(normalized).toBe(originalHttpError);
    });

    it("should wrap regular Error instances", () => {
      const regularError = new Error("Regular error");

      vi.mocked(isAxiosError).mockReturnValueOnce(false);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(regularError);

      expect(normalized).toBeInstanceOf(HttpError);
      expect(normalized.message).toBe("Regular error");
      expect((normalized as HttpError).apiError?.code).toBe("UNKNOWN_ERROR");
      expect((normalized as HttpError).apiError?.status).toBe(0);
    });

    it("should handle non-Error throwables", () => {
      const nonError = "Just a string";

      vi.mocked(isAxiosError).mockReturnValueOnce(false);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(nonError);

      expect(normalized).toBeInstanceOf(HttpError);
      expect(normalized.message).toBe("An unknown error occurred");
      expect((normalized as HttpError).apiError?.original).toBe(nonError);
    });

    it("should extract message from response data when available", () => {
      const mockConfig: InternalAxiosRequestConfig = {
        headers: new AxiosHeaders(),
      };

      const axiosError = new AxiosError(
        "Generic error",
        "GENERIC_CODE",
        mockConfig,
        {},
        {
          data: { message: "More specific message" },
          status: 500,
          statusText: "Server Error",
          headers: {},
          config: mockConfig,
        } as AxiosResponse
      );

      vi.mocked(isAxiosError).mockReturnValueOnce(true);
      vi.mocked(isCancel).mockReturnValueOnce(false);

      const normalized = normalizeError(axiosError);

      expect(normalized).toBeInstanceOf(HttpError);
      expect(normalized.message).toBe("More specific message");
    });
  });
});
