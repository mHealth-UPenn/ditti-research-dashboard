/* Shared utilities for HttpClient ------------------------------------------------
 *
 * These helpers are intentionally extracted into a standalone module to avoid
 * circular-import headaches between utils.ts and the core HttpClient class.
 * They are pure functions with no dependency on the Axios instance itself so
 * they can be reused across the frontend codebase.
 */

import { isCancel, isAxiosError } from "axios";
import { ApiError, HttpError } from "./http.types";
import { ResponseBody } from "../types/api";

/**
 * Read a cookie value by name.
 * @param name Name of the cookie to retrieve
 * @returns The cookie value or null if not found
 */
export function getCookieValue(name: string): string | null {
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

/**
 * Construct a standardized "session expired" HttpError.
 */
export function createSessionExpiredError(): HttpError {
  return new HttpError("Session expired. Please log in again", {
    message: "Session expired. Please log in again",
    status: 401,
    code: "SESSION_EXPIRED",
  });
}

/**
 * Normalize any error thrown by Axios or by caller-defined code paths into a
 * consistent `HttpError` instance.
 */
export function normalizeError(err: unknown): HttpError | Error {
  if (isCancel(err)) {
    return new Error("Request canceled");
  }

  if (isAxiosError(err)) {
    const isNetwork = !err.response && !!err.request;
    const corsHint =
      isNetwork && /(Failed to fetch|Network Error)/i.test(err.message)
        ? " (check network connection or CORS configuration)"
        : "";

    const apiErrorDetails: ApiError = {
      message: err.message,
      status: err.response?.status ?? 0,
      code: err.code ?? "AXIOS_ERROR",
      data: err.response?.data as ResponseBody | undefined,
      original: err,
    };

    // Try to extract more specific message/code from server response
    if (err.response?.data && typeof err.response.data === "object") {
      const responseData = err.response.data as Record<string, unknown>;
      if (typeof responseData.msg === "string") {
        apiErrorDetails.message = responseData.msg;
      } else if (typeof responseData.message === "string") {
        apiErrorDetails.message = responseData.message;
      }
      if (typeof responseData.code === "string") {
        apiErrorDetails.code = responseData.code;
      }
    }

    return new HttpError(
      `${apiErrorDetails.message}${corsHint}`,
      apiErrorDetails
    );
  }

  if (err instanceof HttpError) {
    return err;
  }

  if (err instanceof Error) {
    return new HttpError(err.message, {
      message: err.message,
      status: 0,
      code: "UNKNOWN_ERROR",
      original: err,
    });
  }

  return new HttpError("An unknown error occurred", {
    message: "An unknown error occurred",
    status: 0,
    code: "UNKNOWN_ERROR",
    original: err,
  });
}
