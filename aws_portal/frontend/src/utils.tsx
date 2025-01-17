import { IStudySubjectDetails, ResponseBody } from "./interfaces";

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
    ...((jwt && !(opts.headers && "Authorization" in opts.headers)) && { Authorization: `Bearer ${jwt}` }),
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
 * Downloads a file from a specified URL.
 * @param url - The URL of the file to download.
 * @returns A promise that resolves to the filename or an error message.
 */
export async function downloadExcelFromUrl(url: string): Promise<string | void> {
  // Fetch the file from the server
  try {
    const jwt = localStorage.getItem("jwt");
    const opts: RequestInit = {
      method: "GET",
      credentials: "include",
      headers: {
        Authorization: `Bearer ${jwt}`,
        Accept: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      },
    };

    const response = await fetch(`${process.env.REACT_APP_FLASK_SERVER}${url}`, opts);

    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
    }

    // Handle case where no data is found
    const contentType = response.headers.get("Content-Type");
    if (contentType && contentType.includes("application/json")) {
      const jsonResponse: ResponseBody = await response.json();
      if (jsonResponse.msg && jsonResponse.msg.includes("not found")) {
        return jsonResponse.msg;
      }
    }

    // Extract the filename from the "Content-Disposition" header
    const contentDisposition = response.headers.get("Content-Disposition");
    let filename = "download.xlsx"; // Default filename
    if (contentDisposition && contentDisposition.includes("filename=")) {
      filename = contentDisposition.split("filename=")[1].split(";")[0].replace(/"/g, "");
    }

    // Read the response as a Blob
    const blob = await response.blob();

    // Create a temporary anchor element to trigger the download
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;

    // Append the link to the document and trigger a click event
    document.body.appendChild(link);
    link.click();

    // Clean up by removing the link element and revoking the object URL
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
  } catch (error) {
    console.error("Error downloading participant data:", error);
    return "Error downloading participant data.";
  }
}


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


export const getStartOnAndExpiresOnForStudy = (
  studySubject: IStudySubjectDetails,
  studyId?: number,
) => {
  const currStudy = studySubject.studies.find(s => s.study.id == studyId || -1);

  if (currStudy) {
    const { startsOn, expiresOn } = currStudy;
    return { startsOn: new Date(startsOn), expiresOn: new Date(expiresOn) };
  }

  const startsOn = new Date();
  const expiresOn = new Date();
  expiresOn.setDate(expiresOn.getDate() + 14);

  return { startsOn, expiresOn };
}


export const formatDateForInput = (date: Date) => {
  // Get the year, month, and day
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
  const day = String(date.getDate()).padStart(2, '0');

  // Format the date string
  return `${year}-${month}-${day}`;
}
