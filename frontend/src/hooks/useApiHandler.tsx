import React, { useCallback, useState } from "react";
import { HttpError } from "../lib/http.types";
import { useFlashMessages } from "./useFlashMessages";

/** Potential structure of data within an `ApiError`'s `data` field. */
interface ErrorData {
  /** Server-provided error message. */
  msg?: string;
  /** Server-defined error code (e.g., 'AUTH_INVALID_CREDENTIALS'). */
  error_code?: string;
}

/** Configuration options for the `useApiHandler` hook. */
interface ApiHandlerOptions<TSuccessData = unknown> {
  /** Custom message on success, or a function generating one from response data. */
  successMessage?: string | ((data: TSuccessData) => string);
  /** Custom message on error, or a function generating one from the error object. */
  errorMessage?: string | ((error: Error | HttpError) => string);
  /** Callback executed after successful request and message display. */
  onSuccess?: (data: TSuccessData) => void | Promise<void>;
  /** Callback executed after failed request and message display. Receives the normalized error. */
  onError?: (error: Error | HttpError) => void | Promise<void>;
  /** If `false`, suppresses the default success flash message. Default: `true`. */
  showDefaultSuccessMessage?: boolean;
  /** If `false`, suppresses the default error flash message. Default: `true`. */
  showDefaultErrorMessage?: boolean;
}

/**
 * Custom hook to standardize API request handling (loading state, success/error notifications, callbacks).
 *
 * Provides a `safeRequest` function to wrap asynchronous API calls and exposes an `isLoading` state.
 *
 * @template TSuccessData The expected type of the data returned upon successful API call.
 * @param options Configuration options for message display and callbacks.
 * @returns An object containing `safeRequest` function and `isLoading` boolean.
 */
export function useApiHandler<TSuccessData = unknown>(
  options: ApiHandlerOptions<TSuccessData> = {}
) {
  const [isLoading, setIsLoading] = useState(false);
  const { flashMessage } = useFlashMessages();
  const {
    successMessage,
    errorMessage,
    onSuccess,
    onError,
    showDefaultSuccessMessage = true,
    showDefaultErrorMessage = true,
  } = options;

  /** Handles successful API responses: displays flash message and calls `onSuccess`. */
  const handleSuccess = useCallback(
    async (data: TSuccessData) => {
      if (showDefaultSuccessMessage) {
        const messageContent =
          typeof successMessage === "function"
            ? successMessage(data)
            : (successMessage ?? "Operation successful."); // Provide a generic default
        flashMessage(<span>{messageContent}</span>, "success");
      }
      if (onSuccess) {
        await Promise.resolve(onSuccess(data)); // Ensure async callbacks are awaited
      }
    },
    [flashMessage, onSuccess, successMessage, showDefaultSuccessMessage]
  );

  /** Handles failed API responses: logs error, displays flash message, and calls `onError`. */
  const handleError = useCallback(
    async (error: unknown) => {
      // Ensure error is an instance of Error for consistent handling.
      const processedError =
        error instanceof Error ? error : new Error("An unknown error occurred");

      console.error("API Request Error:", processedError);

      if (showDefaultErrorMessage) {
        let message: string;
        let errorBody: ErrorData | undefined;
        let msgElement: React.ReactElement; // Use ReactElement for flash messages

        // Extract message and potential error code from HttpError or fallback
        if (processedError instanceof HttpError && processedError.apiError) {
          errorBody = processedError.apiError.data as ErrorData | undefined;
          message = errorBody?.msg ?? processedError.message; // Prefer server msg
        } else {
          message = processedError.message;
        }

        // Determine the flash message content based on options and error details.
        if (typeof errorMessage === "function") {
          msgElement = <span>{errorMessage(processedError)}</span>;
        } else if (typeof errorMessage === "string") {
          msgElement = <span>{errorMessage}</span>;
        } else if (errorBody?.error_code) {
          // Example: Special formatting for Authentication errors
          const errorCode = errorBody.error_code;
          if (
            errorCode.includes("AUTH_") ||
            errorCode === "SESSION_EXPIRED" ||
            errorCode === "FORBIDDEN"
          ) {
            msgElement = (
              <span>
                <b>Authentication Error</b>
                <br />
                {message}
              </span>
            );
          } else {
            // Generic formatting for other coded errors
            msgElement = <span>{message}</span>;
          }
        } else {
          // Default formatting for uncategorized errors
          msgElement = (
            <span>
              <b>An unexpected error occurred</b>
              <br />
              {message || "Please try again."}
            </span>
          );
        }

        flashMessage(msgElement, "danger");
      }

      if (onError) {
        await Promise.resolve(onError(processedError)); // Ensure async callbacks are awaited
      }
    },
    [flashMessage, onError, errorMessage, showDefaultErrorMessage]
  );

  /**
   * Wraps an asynchronous function (typically an API call) to provide
   * standardized loading state management, success/error handling, and notifications.
   *
   * @param requestFn The asynchronous function to execute (e.g., `() => httpClient.request(...)`).
   *                  Should return a Promise resolving with `TSuccessData`.
   * @returns A Promise that resolves with `TSuccessData` on success, or `null` if an error occurs
   *          and is handled by the hook. The hook manages the `isLoading` state.
   */
  const safeRequest = useCallback(
    async (
      requestFn: () => Promise<TSuccessData>
    ): Promise<TSuccessData | null> => {
      setIsLoading(true);
      try {
        const data = await requestFn();
        await handleSuccess(data);
        return data; // Return data if successful
      } catch (error) {
        await handleError(error);
        return null; // Indicate error occurred and was handled
      } finally {
        setIsLoading(false); // Reset loading state regardless of outcome
      }
    },
    [handleSuccess, handleError] // Removed setIsLoading dependency: useState setters are stable
  );

  return {
    safeRequest,
    isLoading, // Expose loading state for UI feedback
  };
}
