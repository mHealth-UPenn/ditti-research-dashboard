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

import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { HttpClientProvider } from "../../src/contexts/httpClientContext";
import { useHttpClient } from "../../src/hooks/useHttpClient";
import type { AxiosRequestConfig, AxiosResponse } from "axios";

const mockRequestFn = vi.fn();
const mockRequestRawResponseFn = vi.fn();

vi.mock("../../src/lib/http", async (importActualOriginal) => {
  const actual =
    await importActualOriginal<typeof import("../../src/lib/http")>();
  return {
    ...actual,
    HttpClient: vi.fn().mockImplementation(() => {
      return {
        request: mockRequestFn,
        requestRawResponse: mockRequestRawResponseFn,
      };
    }),
  };
});

import { HttpClient } from "../../src/lib/http";

// A simple component to test the hook
const TestConsumerComponent: React.FC<{
  url: string;
  config?: Omit<AxiosRequestConfig, "url">;
  action:
    | "request"
    | "requestRaw"
    | "get"
    | "post"
    | "put"
    | "delete"
    | "patch";
  data?: unknown;
}> = ({ url, config, action, data }) => {
  const client = useHttpClient();
  const handleClick = () => {
    void (async () => {
      try {
        if (action === "request") {
          await client.request(url, config);
        } else if (action === "requestRaw") {
          await client.requestRawResponse(url, config);
        } else if (action === "get") {
          await client.get(url, config);
        } else if (action === "post") {
          await client.post(url, data, config);
        } else if (action === "put") {
          await client.put(url, data, config);
        } else if (action === "delete") {
          await client.delete(url, config);
        } else {
          await client.patch(url, data, config);
        }
      } catch {
        // Error is intentionally not used in this test component
      }
    })();
  };
  return <button onClick={handleClick}>Make Request</button>;
};

// A component to test the error boundary of the hook
const ErrorBoundaryTestComponent = () => {
  let error: Error | null = null;
  try {
    useHttpClient();
  } catch (e) {
    error = e as Error;
  }
  return <div data-testid="error-message">{error?.message ?? ""}</div>;
};

describe("HttpClientContext", () => {
  let mockHttpClientInstance: HttpClient;

  beforeEach(() => {
    vi.clearAllMocks();

    mockRequestFn.mockResolvedValue({ data: "mocked data" });
    mockRequestRawResponseFn.mockResolvedValue({
      data: "mocked raw data",
      status: 200,
      statusText: "OK",
      headers: {},
      config: {},
    } as AxiosResponse);

    mockHttpClientInstance = new HttpClient("http://fake-base-url.com");
  });

  it("should provide HttpClient methods via useHttpClient hook", async () => {
    render(
      <HttpClientProvider client={mockHttpClientInstance}>
        <TestConsumerComponent url="/test" action="request" />
      </HttpClientProvider>
    );

    const button = screen.getByText("Make Request");
    fireEvent.click(button);
    await vi.dynamicImportSettled();

    expect(mockRequestFn).toHaveBeenCalledTimes(1);
    expect(mockRequestFn).toHaveBeenCalledWith("/test", undefined);
  });

  it("should call request method with correct parameters", async () => {
    const testUrl = "/api/data";
    const testConfig = { method: "POST" as const, data: { foo: "bar" } };

    render(
      <HttpClientProvider client={mockHttpClientInstance}>
        <TestConsumerComponent
          url={testUrl}
          config={testConfig}
          action="request"
        />
      </HttpClientProvider>
    );

    const button = screen.getByText("Make Request");
    fireEvent.click(button);
    await vi.dynamicImportSettled();

    expect(mockRequestFn).toHaveBeenCalledTimes(1);
    expect(mockRequestFn).toHaveBeenCalledWith(testUrl, testConfig);
  });

  it("should call requestRawResponse method with correct parameters", async () => {
    const testUrl = "/api/raw";
    const testConfig = { headers: { "X-Custom": "true" } };
    const mockAxiosResponse = {
      data: "raw data",
      status: 200,
      statusText: "OK",
      headers: {},
      config: {} as AxiosRequestConfig,
    } as AxiosResponse;

    mockRequestRawResponseFn.mockResolvedValueOnce(mockAxiosResponse);

    render(
      <HttpClientProvider client={mockHttpClientInstance}>
        <TestConsumerComponent
          url={testUrl}
          config={testConfig}
          action="requestRaw"
        />
      </HttpClientProvider>
    );

    const button = screen.getByText("Make Request");
    fireEvent.click(button);
    await vi.dynamicImportSettled();

    expect(mockRequestRawResponseFn).toHaveBeenCalledTimes(1);
    expect(mockRequestRawResponseFn).toHaveBeenCalledWith(testUrl, testConfig);
  });

  it("useHttpClient should throw error when used outside of HttpClientProvider", () => {
    const originalError = console.error;
    console.error = vi.fn(); // Suppress expected error message from jsdom

    render(<ErrorBoundaryTestComponent />);

    expect(screen.getByTestId("error-message").textContent).toBe(
      "useHttpClient must be used within a <HttpClientProvider>"
    );

    console.error = originalError; // Restore console.error
  });

  it("request function from hook should correctly pass through to client instance", async () => {
    const testUrl = "/items";
    const payload = { id: 1, name: "Test Item" };
    const expectedResponse = { id: 1, name: "Test Item", created: true };

    mockRequestFn.mockResolvedValueOnce(expectedResponse);

    let receivedResponse: unknown;
    const HookCaller = () => {
      const client = useHttpClient();
      const callRequest = () => {
        void (async () => {
          receivedResponse = await client.request(testUrl, {
            method: "POST",
            data: payload,
          });
        })();
      };
      return <button onClick={callRequest}>Call Request</button>;
    };

    render(
      <HttpClientProvider client={mockHttpClientInstance}>
        <HookCaller />
      </HttpClientProvider>
    );

    fireEvent.click(screen.getByText("Call Request"));
    await vi.dynamicImportSettled();

    expect(mockRequestFn).toHaveBeenCalledWith(testUrl, {
      method: "POST",
      data: payload,
    });
    expect(receivedResponse).toEqual(expectedResponse);
  });

  it("requestRawResponse function from hook should correctly pass through to client instance", async () => {
    const testUrl = "/download";
    const mockRawAxiosResponse = {
      data: new Blob(["file content"]),
      status: 200,
      statusText: "OK",
      headers: { "content-type": "application/octet-stream" },
      config: { headers: {} } as AxiosRequestConfig,
    } as AxiosResponse;

    mockRequestRawResponseFn.mockResolvedValueOnce(mockRawAxiosResponse);

    let receivedRawResponse: AxiosResponse | undefined;
    const HookCallerRaw = () => {
      const client = useHttpClient();
      const callRequestRaw = () => {
        void (async () => {
          receivedRawResponse = await client.requestRawResponse(testUrl, {
            responseType: "blob",
          });
        })();
      };
      return <button onClick={callRequestRaw}>Call Raw Request</button>;
    };

    render(
      <HttpClientProvider client={mockHttpClientInstance}>
        <HookCallerRaw />
      </HttpClientProvider>
    );

    fireEvent.click(screen.getByText("Call Raw Request"));
    await vi.dynamicImportSettled();

    expect(mockRequestRawResponseFn).toHaveBeenCalledWith(testUrl, {
      responseType: "blob",
    });
    expect(receivedRawResponse).toEqual(mockRawAxiosResponse);
  });

  describe("HTTP verb methods", () => {
    const testUrl = "/api/items";
    const testData = { name: "Test" };
    const itemUrl = `${testUrl}/1`;
    const mockResponseData = { id: 1, ...testData };
    const testConfig = { headers: { "X-Test": "true" } };

    it("should correctly call get method", async () => {
      mockRequestFn.mockResolvedValueOnce(mockResponseData);
      render(
        <HttpClientProvider client={mockHttpClientInstance}>
          <TestConsumerComponent
            url={testUrl}
            config={testConfig}
            action="get"
          />
        </HttpClientProvider>
      );
      fireEvent.click(screen.getByText("Make Request"));
      await vi.dynamicImportSettled();

      expect(mockRequestFn).toHaveBeenCalledWith(testUrl, {
        method: "GET",
        ...testConfig,
      });
    });

    it("should correctly call post method with data", async () => {
      mockRequestFn.mockResolvedValueOnce(mockResponseData);
      render(
        <HttpClientProvider client={mockHttpClientInstance}>
          <TestConsumerComponent
            url={testUrl}
            data={testData}
            config={testConfig}
            action="post"
          />
        </HttpClientProvider>
      );
      fireEvent.click(screen.getByText("Make Request"));
      await vi.dynamicImportSettled();
      expect(mockRequestFn).toHaveBeenCalledWith(testUrl, {
        method: "POST",
        data: testData,
        ...testConfig,
      });
    });

    it("should correctly call put method with data", async () => {
      mockRequestFn.mockResolvedValueOnce(mockResponseData);
      render(
        <HttpClientProvider client={mockHttpClientInstance}>
          <TestConsumerComponent
            url={itemUrl}
            data={testData}
            config={testConfig}
            action="put"
          />
        </HttpClientProvider>
      );
      fireEvent.click(screen.getByText("Make Request"));
      await vi.dynamicImportSettled();
      expect(mockRequestFn).toHaveBeenCalledWith(itemUrl, {
        method: "PUT",
        data: testData,
        ...testConfig,
      });
    });

    it("should correctly call delete method", async () => {
      mockRequestFn.mockResolvedValueOnce(undefined);
      render(
        <HttpClientProvider client={mockHttpClientInstance}>
          <TestConsumerComponent
            url={itemUrl}
            config={testConfig}
            action="delete"
          />
        </HttpClientProvider>
      );
      fireEvent.click(screen.getByText("Make Request"));
      await vi.dynamicImportSettled();
      expect(mockRequestFn).toHaveBeenCalledWith(itemUrl, {
        method: "DELETE",
        ...testConfig,
      });
    });

    it("should correctly call patch method with data", async () => {
      mockRequestFn.mockResolvedValueOnce(mockResponseData);
      render(
        <HttpClientProvider client={mockHttpClientInstance}>
          <TestConsumerComponent
            url={itemUrl}
            data={testData}
            config={testConfig}
            action="patch"
          />
        </HttpClientProvider>
      );
      fireEvent.click(screen.getByText("Make Request"));
      await vi.dynamicImportSettled();
      expect(mockRequestFn).toHaveBeenCalledWith(itemUrl, {
        method: "PATCH",
        data: testData,
        ...testConfig,
      });
    });
  });
});
