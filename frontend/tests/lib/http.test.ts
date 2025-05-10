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

import {
  describe,
  it,
  expect,
  vi,
  beforeEach,
  type MockedFunction,
} from "vitest";
import axios, {
  AxiosError,
  AxiosHeaders,
  AxiosResponse,
  isAxiosError,
  AxiosRequestConfig,
  type InternalAxiosRequestConfig,
  CanceledError,
  AxiosDefaults,
  HeadersDefaults,
} from "axios";
import axiosRetry, {
  exponentialDelay,
  isNetworkOrIdempotentRequestError,
} from "axios-retry";
import { HttpClient } from "../../src/lib/http";
import { HttpError } from "../../src/lib/http.types";
import type { ResponseBody } from "../../src/types/api";

// Define the type for our expected mocked axios instance structure
// This helps in typing the instance we retrieve in tests.
interface MockedAxiosInstanceType {
  request: MockedFunction<
    (config: AxiosRequestConfig) => Promise<AxiosResponse>
  >;
  interceptors: {
    request: {
      use: MockedFunction<
        (
          onFulfilled?: (
            config: InternalAxiosRequestConfig
          ) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>,
          onRejected?: (error: Error) => unknown
        ) => number
      >;
      eject: MockedFunction<(interceptorId: number) => void>;
    };
    response: {
      use: MockedFunction<
        (
          onFulfilled?: (
            value: AxiosResponse
          ) => AxiosResponse | Promise<AxiosResponse>,
          onRejected?: (error: AxiosError) => Promise<unknown>
        ) => number
      >;
      eject: MockedFunction<(interceptorId: number) => void>;
    };
  };
  defaults: AxiosDefaults;
  get: MockedFunction<
    (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse>
  >;
  post: MockedFunction<
    (
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig
    ) => Promise<AxiosResponse>
  >;
  put: MockedFunction<
    (
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig
    ) => Promise<AxiosResponse>
  >;
  delete: MockedFunction<
    (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse>
  >;
  patch: MockedFunction<
    (
      url: string,
      data?: unknown,
      config?: AxiosRequestConfig
    ) => Promise<AxiosResponse>
  >;
  head: MockedFunction<
    (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse>
  >;
  options: MockedFunction<
    (url: string, config?: AxiosRequestConfig) => Promise<AxiosResponse>
  >;
}

vi.mock("axios", async (importOriginal) => {
  const actualAxios = await importOriginal<typeof axios>();

  // Define mocks locally within the factory
  const factoryMockAxiosRequestFn =
    vi.fn<(config: AxiosRequestConfig) => Promise<AxiosResponse>>();
  const factoryMockRequestInterceptorUseFn =
    vi.fn<
      (
        onFulfilled?: (
          config: InternalAxiosRequestConfig
        ) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>,
        onRejected?: (error: Error) => unknown
      ) => number
    >();
  const factoryMockResponseInterceptorUseFn =
    vi.fn<
      (
        onFulfilled?: (
          value: AxiosResponse
        ) => AxiosResponse | Promise<AxiosResponse>,
        onRejected?: (error: AxiosError) => Promise<unknown>
      ) => number
    >();

  const factoryActualMockedAxiosInstance: MockedAxiosInstanceType = {
    request: factoryMockAxiosRequestFn,
    interceptors: {
      request: { use: factoryMockRequestInterceptorUseFn, eject: vi.fn() },
      response: { use: factoryMockResponseInterceptorUseFn, eject: vi.fn() },
    },
    defaults: {
      headers: {
        common: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
      } as unknown as HeadersDefaults,
      timeout: 30_000,
    } as AxiosDefaults,
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    head: vi.fn(),
    options: vi.fn(),
  };

  const mockCreate = vi.fn().mockReturnValue(factoryActualMockedAxiosInstance);

  return {
    __esModule: true,
    default: {
      ...actualAxios,
      create: mockCreate,
      isAxiosError: actualAxios.isAxiosError,
      isCancel: actualAxios.isCancel,
      CanceledError: actualAxios.CanceledError,
      AxiosError: actualAxios.AxiosError,
      AxiosHeaders: actualAxios.AxiosHeaders,
    },
    create: mockCreate,
    isAxiosError: actualAxios.isAxiosError,
    isCancel: actualAxios.isCancel,
    CanceledError: actualAxios.CanceledError,
    AxiosError: actualAxios.AxiosError,
    AxiosHeaders: actualAxios.AxiosHeaders,
  };
});

vi.mock("axios-retry", () => ({
  default: vi.fn(),
  exponentialDelay: vi.fn(),
  isNetworkOrIdempotentRequestError: vi.fn(),
}));

const mockAxiosRetry = axiosRetry as MockedFunction<typeof axiosRetry>;

describe("HttpClient", () => {
  const baseURL = "http://test.com/api";
  let httpClient: HttpClient;
  let localStorageMock: Storage;

  // Variable to hold the mock instance for the current test
  let currentMockedAxiosInstance: MockedAxiosInstanceType;

  beforeEach(() => {
    const createMock = axios.create as MockedFunction<typeof axios.create>;

    // Get the singleton mocked instance that axios.create() returns.
    // This instance persists across tests, so we need to clear its method mocks.
    // We can get it by calling createMock once if it hasn't been called,
    // or by accessing a previous result if it has.
    // A simpler way if factoryActualMockedAxiosInstance was exported from the mock,
    // but it's not. So, we rely on createMock returning it.

    // If createMock has been called before (e.g. in a previous test),
    // factoryActualMockedAxiosInstance is its last return value.
    // Otherwise, call createMock to get it for the first time (it will be memoized).
    let instanceToClear: MockedAxiosInstanceType;
    if (
      createMock.mock.results.length > 0 &&
      createMock.mock.results[createMock.mock.results.length - 1]?.value
    ) {
      instanceToClear = createMock.mock.results[
        createMock.mock.results.length - 1
      ].value as MockedAxiosInstanceType;
    } else {
      // This path might be taken if this is the very first call or if mock was fully reset.
      // Calling it will establish the instance.
      instanceToClear = createMock() as unknown as MockedAxiosInstanceType; // Cast via unknown
      // We called it, so clear this specific call to createMock itself for the actual test's count.
      createMock.mockClear();
    }

    // Clear all method mocks on the singleton instance before HttpClient uses it
    instanceToClear.request.mockClear();
    if (
      typeof instanceToClear.interceptors.request.use.mockClear === "function"
    ) {
      instanceToClear.interceptors.request.use.mockClear();
    }
    if (
      typeof instanceToClear.interceptors.response.use.mockClear === "function"
    ) {
      instanceToClear.interceptors.response.use.mockClear();
    }
    instanceToClear.get.mockClear();
    instanceToClear.post.mockClear();
    instanceToClear.put.mockClear();
    instanceToClear.delete.mockClear();
    instanceToClear.patch.mockClear();
    instanceToClear.head.mockClear();
    instanceToClear.options.mockClear();
    if (
      typeof instanceToClear.interceptors.request.eject.mockClear === "function"
    ) {
      instanceToClear.interceptors.request.eject.mockClear();
    }
    if (
      typeof instanceToClear.interceptors.response.eject.mockClear ===
      "function"
    ) {
      instanceToClear.interceptors.response.eject.mockClear();
    }

    // Now, clear history of calls to axios.create() itself for the current test
    createMock.mockClear();

    // Create a new HttpClient instance for each test, this will call the mocked axios.create
    httpClient = new HttpClient(baseURL);

    // Retrieve the instance that was created (it's the same singleton factoryActualMockedAxiosInstance)
    // Its method mocks were cleared above, so calls made during HttpClient construction are fresh.
    if (createMock.mock.results[0]?.value) {
      currentMockedAxiosInstance = createMock.mock.results[0]
        .value as MockedAxiosInstanceType;
    } else {
      throw new Error(
        "axios.create() was not called or did not return a value in HttpClient constructor"
      );
    }

    localStorageMock = (function () {
      let store: Record<string, string> = {};
      return {
        getItem(key: string) {
          return store[key] || null;
        },
        setItem(key: string, value: string) {
          store[key] = value.toString();
        },
        removeItem(key: string) {
          const newStore: Record<string, string> = {};
          for (const k in store) {
            if (k !== key) {
              newStore[k] = store[k];
            }
          }
          store = newStore;
        },
        clear() {
          store = {};
        },
        key(index: number): string | null {
          const keys = Object.keys(store);
          return keys[index] || null;
        },
        get length() {
          return Object.keys(store).length;
        },
      };
    })();
    Object.defineProperty(window, "localStorage", {
      value: localStorageMock,
      writable: true,
    });
  });

  describe("constructor", () => {
    it("should create an axios instance with correct default config", () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL,
        timeout: 30_000,
        withCredentials: true,
        headers: expect.any(AxiosHeaders),
        validateStatus: expect.any(Function),
      });
      expect(
        currentMockedAxiosInstance.defaults.headers.common["Content-Type"]
      ).toBe("application/json");
    });

    it("should register interceptors", () => {
      expect(axios.create).toHaveBeenCalledWith({
        baseURL,
        timeout: 30_000,
        withCredentials: true,
        headers: expect.any(AxiosHeaders),
        validateStatus: expect.any(Function),
      });
      // Assert against the mock functions on the instance directly
      expect(
        currentMockedAxiosInstance.interceptors.request.use
      ).toHaveBeenCalledTimes(1);
      expect(
        currentMockedAxiosInstance.interceptors.response.use
      ).toHaveBeenCalledTimes(1);
    });

    it("should register retry policy", () => {
      expect(mockAxiosRetry).toHaveBeenCalledWith(
        currentMockedAxiosInstance,
        expect.objectContaining({
          retries: 3,
          retryDelay: exponentialDelay,
          retryCondition: expect.any(Function),
        })
      );
    });
  });

  describe("request", () => {
    it("should make a GET request by default and return data", async () => {
      const responseData = { id: 1, name: "Test" };
      currentMockedAxiosInstance.request.mockResolvedValueOnce({
        data: responseData,
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      });
      const result = await httpClient.request("/items");
      expect(currentMockedAxiosInstance.request).toHaveBeenCalledWith({
        url: "/items",
        method: "GET",
        data: undefined,
        signal: undefined,
      });
      expect(result).toEqual(responseData);
    });

    it("should make a POST request with data and return data", async () => {
      const requestData = { name: "New Item" };
      const responseData = { id: 2, name: "New Item" };
      currentMockedAxiosInstance.request.mockResolvedValueOnce({
        data: responseData,
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      });
      const result = await httpClient.request("/items", {
        method: "POST",
        data: requestData,
      });
      expect(currentMockedAxiosInstance.request).toHaveBeenCalledWith({
        url: "/items",
        method: "POST",
        data: requestData,
        signal: undefined,
      });
      expect(result).toEqual(responseData);
    });

    it("should normalize AxiosError into HttpError", async () => {
      const errorResponseData = { msg: "Invalid request" };
      const mockReqConfig: InternalAxiosRequestConfig = {
        headers: new AxiosHeaders(),
      };
      const axiosError = new AxiosError(
        "Request failed with status code 400",
        "BAD_REQUEST",
        mockReqConfig,
        {},
        {
          data: errorResponseData,
          status: 400,
          statusText: "Bad Request",
          headers: new AxiosHeaders(),
          config: mockReqConfig,
        } as AxiosResponse
      );
      currentMockedAxiosInstance.request.mockRejectedValueOnce(axiosError);
      try {
        await httpClient.request("/error");
      } catch (error) {
        expect(error).toBeInstanceOf(HttpError);
        const httpError = error as HttpError;
        expect(httpError.message).toContain(
          "Request failed with status code 400"
        );
        expect(httpError.apiError?.status).toBe(400);
        expect(httpError.apiError?.code).toBe("BAD_REQUEST");
        expect(httpError.apiError?.data).toEqual(errorResponseData);
        expect(httpError.apiError?.original).toBe(axiosError);
      }
    });

    it("should handle network errors (no response object)", async () => {
      const networkError = new AxiosError("Network Error", "ERR_NETWORK");
      delete networkError.response;
      networkError.request = {};
      currentMockedAxiosInstance.request.mockRejectedValueOnce(networkError);
      try {
        await httpClient.request("/network-error");
      } catch (error) {
        expect(error).toBeInstanceOf(HttpError);
        const httpError = error as HttpError;
        expect(httpError.message).toContain("Network Error");
        expect(httpError.message).toContain(
          "(check network connection or CORS configuration)"
        );
        expect(httpError.apiError?.status).toBe(0);
        expect(httpError.apiError?.code).toBe("ERR_NETWORK");
      }
    });

    it("should handle cancellation errors", async () => {
      const cancelError = new CanceledError("Request canceled");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(cancelError);
      try {
        await httpClient.request("/cancel");
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe("Request canceled");
      }
    });

    it("should handle generic errors", async () => {
      const genericError = new Error("Something went wrong");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(genericError);
      try {
        await httpClient.request("/generic-error");
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe("Something went wrong");
        expect(error).toBe(genericError);
      }
    });

    it("should pass AbortSignal to axios request", async () => {
      const controller = new AbortController();
      const signal = controller.signal;
      currentMockedAxiosInstance.request.mockResolvedValueOnce({
        data: {},
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      });
      await httpClient.request("/items", { signal });
      expect(currentMockedAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({ signal })
      );
    });
  });

  describe("requestRawResponse", () => {
    it("should return the raw AxiosResponse", async () => {
      const mockReqConfig: InternalAxiosRequestConfig = {
        headers: new AxiosHeaders(),
      };
      const rawResponse: AxiosResponse = {
        data: { id: 1 },
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders({ "content-type": "application/json" }),
        config: mockReqConfig,
      };
      currentMockedAxiosInstance.request.mockResolvedValueOnce(rawResponse);
      const result = await httpClient.requestRawResponse("/raw");
      expect(result).toEqual(rawResponse);
      expect(currentMockedAxiosInstance.request).toHaveBeenCalledWith({
        url: "/raw",
      });
    });

    it("should re-throw AxiosError if request fails", async () => {
      const axiosError = new AxiosError("Raw request failed");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(axiosError);
      try {
        await httpClient.requestRawResponse("/raw-error");
      } catch (error) {
        expect(error).toBe(axiosError);
        expect(isAxiosError(error)).toBe(true);
      }
    });

    it("should throw a normalized error for cancellation in raw request", async () => {
      const cancelError = new CanceledError("Raw request canceled");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(cancelError);
      try {
        await httpClient.requestRawResponse("/raw-cancel");
      } catch (error) {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toBe("Raw request canceled");
      }
    });

    it("should throw generic error for other non-Axios errors in raw request", async () => {
      const genericError = new Error("Some other issue");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(genericError);
      try {
        await httpClient.requestRawResponse("/raw-generic-error");
      } catch (e) {
        expect(e).toBe(genericError);
      }
    });

    it("should throw unknown error for non-Error throwables in raw request", async () => {
      const nonErrorThrowable = { message: "Not an error instance" };
      currentMockedAxiosInstance.request.mockRejectedValueOnce(
        nonErrorThrowable
      );
      try {
        await httpClient.requestRawResponse("/raw-unknown-error");
      } catch (e) {
        expect(e).toBeInstanceOf(Error);
        expect((e as Error).message).toBe(
          "An unknown error occurred during raw request"
        );
        expect((e as Error).cause).toBe(nonErrorThrowable);
      }
    });
  });

  describe("Interceptors", () => {
    describe("Request Interceptor (CSRF)", () => {
      it("should attach X-CSRF-TOKEN for POST if csrfToken exists in localStorage", () => {
        localStorageMock.setItem("csrfToken", "test-csrf-token");
        const requestInterceptorHandler =
          currentMockedAxiosInstance.interceptors.request.use.mock.calls[0][0];
        if (!requestInterceptorHandler) {
          throw new Error(
            "Test setup error: Request interceptor handler not found."
          );
        }
        const config = { method: "POST" as const, headers: new AxiosHeaders() };
        const newConfig = requestInterceptorHandler(
          config as InternalAxiosRequestConfig
        ) as InternalAxiosRequestConfig;
        expect(newConfig.headers.get("X-CSRF-TOKEN")).toBe("test-csrf-token");
      });

      it("should not attach X-CSRF-TOKEN for GET even if token exists", () => {
        localStorageMock.setItem("csrfToken", "test-csrf-token");
        const requestInterceptorHandler =
          currentMockedAxiosInstance.interceptors.request.use.mock.calls[0][0];
        if (!requestInterceptorHandler) {
          throw new Error(
            "Test setup error: Request interceptor handler not found."
          );
        }
        const config = { method: "GET" as const, headers: new AxiosHeaders() };
        const newConfig = requestInterceptorHandler(
          config as InternalAxiosRequestConfig
        ) as InternalAxiosRequestConfig;
        expect(newConfig.headers.get("X-CSRF-TOKEN")).toBeUndefined();
      });

      it("should not attach X-CSRF-TOKEN if token does not exist in localStorage", () => {
        localStorageMock.removeItem("csrfToken");
        const requestInterceptorHandler =
          currentMockedAxiosInstance.interceptors.request.use.mock.calls[0][0];
        if (!requestInterceptorHandler) {
          throw new Error(
            "Test setup error: Request interceptor handler not found."
          );
        }
        const config = { method: "POST" as const, headers: new AxiosHeaders() };
        const newConfig = requestInterceptorHandler(
          config as InternalAxiosRequestConfig
        ) as InternalAxiosRequestConfig;
        expect(newConfig.headers.get("X-CSRF-TOKEN")).toBeUndefined();
      });
    });

    describe("Response Interceptor (CSRF)", () => {
      it("should set csrfToken in localStorage if csrfAccessToken is in response body", () => {
        const responseInterceptorSuccessHandler =
          currentMockedAxiosInstance.interceptors.response.use.mock.calls[0][0];
        if (!responseInterceptorSuccessHandler) {
          throw new Error(
            "Test setup error: Response interceptor success handler not found."
          );
        }
        const response = {
          data: { csrfAccessToken: "new-token-from-server" } as ResponseBody,
          status: 200,
          statusText: "OK",
          headers: new AxiosHeaders(),
          config: {} as InternalAxiosRequestConfig,
        } as AxiosResponse;
        void responseInterceptorSuccessHandler(response);
        expect(localStorageMock.getItem("csrfToken")).toBe(
          "new-token-from-server"
        );
      });

      it("should not set csrfToken if csrfAccessToken is not in response body", () => {
        localStorageMock.removeItem("csrfToken");
        const responseInterceptorSuccessHandler =
          currentMockedAxiosInstance.interceptors.response.use.mock.calls[0][0];
        if (!responseInterceptorSuccessHandler) {
          throw new Error(
            "Test setup error: Response interceptor success handler not found."
          );
        }
        const response = {
          data: { msg: "Some data" } as ResponseBody,
          status: 200,
          statusText: "OK",
          headers: new AxiosHeaders(),
          config: {} as InternalAxiosRequestConfig,
        } as AxiosResponse;
        void responseInterceptorSuccessHandler(response);
        expect(localStorageMock.getItem("csrfToken")).toBeNull();
      });

      it("should pass through the response object", () => {
        const responseInterceptorSuccessHandler =
          currentMockedAxiosInstance.interceptors.response.use.mock.calls[0][0];
        if (!responseInterceptorSuccessHandler) {
          throw new Error(
            "Test setup error: Response interceptor success handler not found."
          );
        }
        const response = {
          data: "test data",
          status: 200,
          statusText: "OK",
          headers: new AxiosHeaders(),
          config: {} as InternalAxiosRequestConfig,
        } as AxiosResponse;
        const result = responseInterceptorSuccessHandler(
          response
        ) as AxiosResponse;
        expect(result).toBe(response);
      });

      it("should reject promise on interceptor error", async () => {
        const responseInterceptorErrorHandler =
          currentMockedAxiosInstance.interceptors.response.use.mock.calls[0][1];
        if (!responseInterceptorErrorHandler) {
          throw new Error(
            "Test setup error: Response interceptor error handler not found."
          );
        }
        const error = new Error("Interceptor error");
        try {
          await responseInterceptorErrorHandler(error as AxiosError);
        } catch (e) {
          expect(e).toBe(error);
        }
      });
    });
  });

  describe("Retry Policy", () => {
    it("should configure axios-retry with correct parameters", () => {
      const retryConfig = mockAxiosRetry.mock.calls[0]?.[1];
      const retryConditionFn = retryConfig?.retryCondition;
      expect(retryConditionFn).toBeDefined();

      const mockError500: Partial<AxiosError> = {
        response: { status: 500 } as AxiosResponse,
        isAxiosError: true,
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      };
      const mockError429: Partial<AxiosError> = {
        response: { status: 429 } as AxiosResponse,
        isAxiosError: true,
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      };

      vi.mocked(isNetworkOrIdempotentRequestError).mockReturnValue(false);
      if (retryConditionFn) {
        expect(retryConditionFn(mockError500 as AxiosError)).toBe(false);
        expect(retryConditionFn(mockError429 as AxiosError)).toBe(true);
      }

      vi.mocked(isNetworkOrIdempotentRequestError).mockReturnValue(true);
      if (retryConditionFn) {
        expect(retryConditionFn({} as AxiosError)).toBe(true);
      }
    });
  });
});
