import { ResponseBody } from "./interfaces";

// TODO: Find out what this was meant for
// const crossorigin = Boolean(process.env.CROSSORIGIN);

/**
 * Makes a request with specified options.
 * @param url - The endpoint URL.
 * @param opts - Request options including method, headers, and body.
 * @returns A promise that resolves to the response body.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const makeRequest = async (url: string, opts: RequestInit = {}): Promise<any> => {
  const jwt = localStorage.getItem("jwt");

  // Set credentials to include to send cookies
  opts.credentials = 'include';

  // Set headers
  opts.headers = {
    ...opts.headers,
    ...((jwt && !(opts.headers && "Authorization" in opts.headers) ) && { Authorization: `Bearer ${jwt}` }),
  };

  // Add additional headers for specific request methods
  if (["POST", "PUT", "DELETE"].includes(opts.method || "")) {
    opts.headers = {
      ...opts.headers,
      "Content-Type": "application/json",
      "X-CSRF-TOKEN": localStorage.getItem("csrfToken") || "",
    };
  }

  // Execute the request
  const response = await fetch(`${process.env.REACT_APP_FLASK_SERVER}${url}`, opts);
  const body: ResponseBody = await response.json();

  // Store CSRF token for future requests
  if (response.status === 200) {
    if (body.csrfAccessToken) localStorage.setItem("csrfToken", body.csrfAccessToken);
    if (body.jwt) localStorage.setItem("jwt", body.jwt);
  }

  // Handle unauthorized responses
  // if (response.status === 401) {
  //   localStorage.removeItem("jwt");
  //   localStorage.removeItem("csrfToken");
  //   throw body;
  // }

  // Throw an error if the response is not successful
  if (response.status !== 200) {
    throw body;
  }

  return body;
};

/**
 * Checks if the user has permission to perform a specified action on a resource.
 * @param app - Application ID.
 * @param action - Action to be checked (e.g., "read", "write").
 * @param resource - Resource identifier.
 * @param study - (Optional) Study ID.
 * @returns A promise that resolves if authorized or throws an error if unauthorized.
 */
export const getAccess = async (
  app: number,
  action: string,
  resource: string,
  study?: number
): Promise<void> => {
  let url = `/iam/get-access?app=${app}&action=${action}&resource=${resource}`;
  if (study) url += `&study=${study}`;

  const res: ResponseBody = await makeRequest(url);
  if (res.msg !== "Authorized") throw new Error("Unauthorized");
};
