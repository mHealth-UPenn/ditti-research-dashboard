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
  afterEach,
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

  type AxiosMockInstance = MockedAxiosInstanceType;

  const createMockInstance = (): AxiosMockInstance => ({
    request: vi.fn(),
    interceptors: {
      request: { use: vi.fn(), eject: vi.fn() },
      response: { use: vi.fn(), eject: vi.fn() },
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
  });

  const createSpy = vi.fn(() => createMockInstance());

  return {
    __esModule: true,
    default: {
      ...actualAxios,
      create: createSpy,
      AxiosHeaders: actualAxios.AxiosHeaders,
      isAxiosError: actualAxios.isAxiosError,
      isCancel: actualAxios.isCancel,
      CanceledError: actualAxios.CanceledError,
      AxiosError: actualAxios.AxiosError,
    },
    create: createSpy,
    AxiosHeaders: actualAxios.AxiosHeaders,
    isAxiosError: actualAxios.isAxiosError,
    isCancel: actualAxios.isCancel,
    CanceledError: actualAxios.CanceledError,
    AxiosError: actualAxios.AxiosError,
  };
});

vi.mock("axios-retry", () => ({
  default: vi.fn(),
  exponentialDelay: vi.fn(),
  isNetworkOrIdempotentRequestError: vi.fn(),
}));

const mockAxiosRetry = axiosRetry as MockedFunction<typeof axiosRetry>;

// Define types for test mocks
interface CallableAxiosInstance extends MockedAxiosInstanceType {
  (config: InternalAxiosRequestConfig): Promise<AxiosResponse>;
}

interface TestHttpClient {
  instance: CallableAxiosInstance;
  refreshTokenInProgress: boolean;
  tokenRefreshQueue: {
    resolve: (value?: unknown) => void;
    reject: (reason?: unknown) => void;
  }[];
  processQueue: (error: Error | null, token?: string | null) => void;
  redirectToLogin: () => void;
}

// Helper functions for test setup
const createMockAxiosInstance = (
  response: AxiosResponse,
  mockInstance: MockedAxiosInstanceType
): CallableAxiosInstance => {
  return Object.assign(vi.fn().mockResolvedValue(response), {
    post: vi.fn(),
    interceptors: mockInstance.interceptors,
    request: vi.fn(),
    defaults: mockInstance.defaults,
    get: vi.fn(),
    put: vi.fn(),
    delete: vi.fn(),
    patch: vi.fn(),
    head: vi.fn(),
    options: vi.fn(),
  }) as CallableAxiosInstance;
};

const getTestClient = (client: HttpClient): TestHttpClient => {
  return client as unknown as TestHttpClient;
};

describe("HttpClient", () => {
  const baseURL = "http://test.com/api";
  let httpClient: HttpClient;
  let localStorageMock: Storage;

  // Variable to hold the mock instance for the current test
  let currentMockedAxiosInstance: MockedAxiosInstanceType;

  beforeEach(() => {
    const createMock = axios.create as MockedFunction<typeof axios.create>;
    createMock.mockClear();

    // Create a new HttpClient instance for each test,
    // this will call the mocked axios.create
    httpClient = new HttpClient(baseURL);

    // Get the mock instance that was returned by axios.create
    const mockInstance = createMock.mock.results[0]
      .value as MockedAxiosInstanceType;
    currentMockedAxiosInstance = mockInstance;

    // Setup localStorage mock
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

    it("should normalize AxiosError into HttpError, using response message", async () => {
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
        // Now the error message uses the 'msg' field from response data
        expect(httpError.message).toBe("Invalid request");
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

    it("should normalize generic errors into HttpError", async () => {
      const genericError = new Error("Something went wrong");
      currentMockedAxiosInstance.request.mockRejectedValueOnce(genericError);
      try {
        await httpClient.request("/generic-error");
      } catch (error) {
        expect(error).toBeInstanceOf(HttpError);
        expect((error as HttpError).message).toBe("Something went wrong");
        expect((error as HttpError).apiError?.original).toBe(genericError);
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
      beforeEach(() => {
        // Setup mock document.cookie
        vi.spyOn(document, "cookie", "get").mockImplementation(() => {
          return "XSRF-TOKEN=test-csrf-token; id_token=fake-id-token";
        });
      });

      afterEach(() => {
        vi.restoreAllMocks();
      });

      it("should attach X-XSRF-TOKEN for POST when XSRF-TOKEN cookie exists", () => {
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
        expect(newConfig.headers.get("X-XSRF-TOKEN")).toBe("test-csrf-token");
      });

      it("should not attach X-XSRF-TOKEN for GET even if cookie exists", () => {
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
        expect(newConfig.headers.get("X-XSRF-TOKEN")).toBeUndefined();
      });

      it("should not attach X-XSRF-TOKEN if cookie does not exist", () => {
        vi.spyOn(document, "cookie", "get").mockImplementation(() => "");

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
        expect(newConfig.headers.get("X-XSRF-TOKEN")).toBeUndefined();
      });
    });

    describe("Response Interceptor (CSRF)", () => {
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
        const axiosError = new AxiosError("Interceptor error", "CODE", {
          headers: new AxiosHeaders(),
        } as InternalAxiosRequestConfig);

        try {
          await responseInterceptorErrorHandler(axiosError);
          // Should not reach here
          expect(true).toBe(false);
        } catch (e) {
          // Now it should be a normalized HttpError
          expect(e).toBeInstanceOf(HttpError);
          expect((e as HttpError).message).toBe("Interceptor error");
          expect((e as HttpError).apiError?.original).toBe(axiosError);
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

  // ---------------------------------------------------------------------------
  // Response Interceptor – Token Refresh scenarios
  // ---------------------------------------------------------------------------

  describe("Response Interceptor (Token Refresh)", () => {
    const getErrorHandler = () => {
      const handler =
        currentMockedAxiosInstance.interceptors.response.use.mock.calls[0][1];
      if (!handler) {
        throw new Error(
          "Test setup error: Response interceptor error handler not found"
        );
      }
      return handler;
    };

    it("should refresh token and retry the original request on 401 error", async () => {
      const retryResponse: AxiosResponse = {
        data: { success: true },
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      };

      const refreshSuccessResp: AxiosResponse = {
        data: {},
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      };

      const callableInstance = createMockAxiosInstance(
        retryResponse,
        currentMockedAxiosInstance
      );
      callableInstance.post.mockResolvedValue(refreshSuccessResp);
      getTestClient(httpClient).instance = callableInstance;

      const origConfig = {
        url: "/api/protected/data",
        headers: new AxiosHeaders(),
      } as InternalAxiosRequestConfig;

      const axiosError = new AxiosError(
        "Unauthorized",
        undefined,
        origConfig,
        {},
        {
          data: {},
          status: 401,
          statusText: "Unauthorized",
          headers: new AxiosHeaders(),
          config: origConfig,
        } as AxiosResponse
      );

      const result = await getErrorHandler()(axiosError);

      expect(callableInstance.post).toHaveBeenCalledWith(
        "/api/auth/refresh-token",
        null,
        expect.objectContaining({
          headers: { "Content-Type": "application/json" },
        })
      );
      expect(callableInstance).toHaveBeenCalledWith(origConfig);
      expect(result).toBe(retryResponse);
    });

    it("should queue request when refresh is already in progress", async () => {
      getTestClient(httpClient).refreshTokenInProgress = true;

      const mockResponse: AxiosResponse = {
        data: "after",
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      };
      const callableInstance = createMockAxiosInstance(
        mockResponse,
        currentMockedAxiosInstance
      );
      getTestClient(httpClient).instance = callableInstance;

      const origConfig = {
        url: "/api/queued",
        headers: new AxiosHeaders(),
      } as InternalAxiosRequestConfig;

      const axiosError = new AxiosError(
        "Unauthorized",
        undefined,
        origConfig,
        {},
        {
          data: {},
          status: 401,
          statusText: "Unauthorized",
          headers: new AxiosHeaders(),
          config: origConfig,
        } as AxiosResponse
      );

      const promise = getErrorHandler()(axiosError);

      // Ensure the request is queued
      expect(getTestClient(httpClient).tokenRefreshQueue.length).toBe(1);

      // Resolve the queue (simulate successful refresh elsewhere)
      getTestClient(httpClient).processQueue(null, "token");

      const res = (await promise) as AxiosResponse;
      expect(callableInstance).toHaveBeenCalledWith(origConfig);
      expect(res.data).toBe("after");
    });

    it("should reject with SESSION_EXPIRED when 401 occurs on refresh endpoint", async () => {
      const origConfig = {
        url: "/api/auth/refresh-token",
        headers: new AxiosHeaders(),
      } as InternalAxiosRequestConfig;

      const axiosError = new AxiosError(
        "Unauthorized",
        undefined,
        origConfig,
        {},
        {
          data: {},
          status: 401,
          statusText: "Unauthorized",
          headers: new AxiosHeaders(),
          config: origConfig,
        } as AxiosResponse
      );

      try {
        await getErrorHandler()(axiosError);
        // Should not reach here
        expect(true).toBe(false);
      } catch (e) {
        expect(e).toBeInstanceOf(HttpError);
        expect((e as HttpError).apiError?.code).toBe("SESSION_EXPIRED");
      }
    });
  });

  // ---------------------------------------------------------------------------
  // Additional tests for queue processing, token refresh, and redirects
  // ---------------------------------------------------------------------------

  describe("processQueue", () => {
    it("should resolve all queued promises when no error is provided", () => {
      const resolveSpy = vi.fn();
      const rejectSpy = vi.fn();

      getTestClient(httpClient).tokenRefreshQueue.push({
        resolve: resolveSpy,
        reject: rejectSpy,
      });

      getTestClient(httpClient).processQueue(null, "new-token");

      expect(resolveSpy).toHaveBeenCalledWith("new-token");
      expect(rejectSpy).not.toHaveBeenCalled();
    });

    it("should reject all queued promises when an error is provided", () => {
      const resolveSpy = vi.fn();
      const rejectSpy = vi.fn();
      const err = new Error("boom");

      getTestClient(httpClient).tokenRefreshQueue.push({
        resolve: resolveSpy,
        reject: rejectSpy,
      });

      getTestClient(httpClient).processQueue(err);

      expect(rejectSpy).toHaveBeenCalledWith(err);
      expect(resolveSpy).not.toHaveBeenCalled();
    });
  });

  describe("refreshTokens", () => {
    beforeEach(() => {
      vi.spyOn(console, "error").mockImplementation(() => undefined);
    });

    afterEach(() => {
      vi.restoreAllMocks();
    });

    it("should POST to the refresh endpoint and resolve on success", async () => {
      currentMockedAxiosInstance.post.mockResolvedValueOnce({
        data: {},
        status: 200,
        statusText: "OK",
        headers: new AxiosHeaders(),
        config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
      });

      await httpClient.refreshTokens();

      expect(currentMockedAxiosInstance.post).toHaveBeenCalledWith(
        "/api/auth/refresh-token",
        null,
        expect.objectContaining({
          headers: { "Content-Type": "application/json" },
        })
      );
    });

    it("should throw SESSION_EXPIRED error and redirect on CSRF error", async () => {
      const csrfError = new AxiosError(
        "CSRF failed",
        "BAD_REQUEST",
        { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
        {},
        {
          data: { code: "CSRF_ERROR" },
          status: 400,
          statusText: "Bad Request",
          headers: new AxiosHeaders(),
          config: { headers: new AxiosHeaders() } as InternalAxiosRequestConfig,
        } as AxiosResponse
      );

      currentMockedAxiosInstance.post.mockRejectedValueOnce(csrfError);

      const redirectSpy = vi.spyOn(
        getTestClient(httpClient),
        "redirectToLogin"
      );

      try {
        await httpClient.refreshTokens();
        // Should not reach here
        expect(true).toBe(false);
      } catch (e) {
        expect(e).toBeInstanceOf(HttpError);
        expect((e as HttpError).apiError?.code).toBe("SESSION_EXPIRED");
      }

      expect(redirectSpy).toHaveBeenCalled();
    });
  });

  describe("redirectToLogin", () => {
    it("should redirect to coordinator login when pathname starts with /coordinator", () => {
      const locationMock = { pathname: "/coordinator/dashboard", href: "" };
      Object.defineProperty(window, "location", {
        value: locationMock,
        writable: true,
      });

      getTestClient(httpClient).redirectToLogin();

      expect(locationMock.href).toBe("/coordinator/login");
    });

    it("should redirect to participant login for all other paths", () => {
      const locationMock = { pathname: "/some/path", href: "" };
      Object.defineProperty(window, "location", {
        value: locationMock,
        writable: true,
      });

      getTestClient(httpClient).redirectToLogin();

      expect(locationMock.href).toBe("/login");
    });
  });
});
