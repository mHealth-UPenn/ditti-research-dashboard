import DOMPurify from "isomorphic-dompurify";
import { StudySubjectModel } from "./types/models";
import { ResponseBody } from "./types/api";
import { AttributesByTag, ClassAllowlist } from "./utils.types";

/**
 * Sanitizes HTML content from the Quill editor to prevent XSS attacks
 * while preserving the necessary formatting and structure.
 * @param html The HTML content to sanitize.
 * @returns Sanitized HTML string.
 */
export function sanitize_quill_html(html: string): string {
  const allowed_tags = [
    "a",
    "blockquote",
    "br",
    "div",
    "em",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "iframe",
    "img",
    "li",
    "ol",
    "p",
    "pre",
    "span",
    "strong",
    "sub",
    "sup",
    "table",
    "tbody",
    "td",
    "tr",
    "ul",
    "select",
    "option",
    "u",
    "s",
  ];

  const all_attributes = [
    "class",
    "style",
    "data-language",
    "data-row",
    "data-list",
    "allowfullscreen",
    "frameborder",
    "src",
    "href",
    "target",
    "value",
    "alt",
  ];

  const attributes_by_tag: AttributesByTag = {
    div: ["class", "style", "data-language"],
    td: ["class", "style", "data-row"],
    li: ["class", "style", "data-list"],
    iframe: ["class", "style", "allowfullscreen", "frameborder", "src"],
    a: ["class", "style", "href", "target"],
    select: ["class", "style"],
    option: ["class", "style", "value"],
    img: ["class", "style", "src", "alt"],
    p: ["class", "style"],
    span: ["class", "style"],
    h1: ["class", "style"],
    h2: ["class", "style"],
    h3: ["class", "style"],
    h4: ["class", "style"],
    h5: ["class", "style"],
    h6: ["class", "style"],
    blockquote: ["class", "style"],
    pre: ["class", "style"],
    ol: ["class", "style"],
    ul: ["class", "style"],
    table: ["class", "style"],
    tbody: ["class", "style"],
    tr: ["class", "style"],
    strong: ["class", "style"],
    em: ["class", "style"],
    sub: ["class", "style"],
    sup: ["class", "style"],
    br: ["class", "style"],
    u: ["class", "style"],
    s: ["class", "style"],
  };

  const class_allowlist: ClassAllowlist = {
    div: [
      "ql-code-block-container",
      "ql-code-block",
      "ql-token",
      "ql-ui",
      "ql-align-center",
      "ql-align-right",
      "ql-align-justify",
      "ql-indent-1",
      "ql-indent-2",
      "ql-indent-3",
      "ql-indent-4",
      "ql-indent-5",
      "ql-indent-6",
      "ql-indent-7",
      "ql-indent-8",
      "ql-indent-9",
      "ql-size-small",
      "ql-size-large",
      "ql-size-huge",
      "ql-video",
    ],
    span: [
      "ql-token",
      "hljs-keyword",
      "hljs-number",
      "hljs-string",
      "hljs-comment",
      "hljs-function",
      "hljs-title",
      "hljs-params",
      "hljs-variable",
      "hljs-operator",
      "hljs-builtin",
      "ql-ui", // "ql-ui" is explicitly allowed
    ],
    p: [
      "ql-align-center",
      "ql-align-right",
      "ql-align-justify",
      "ql-indent-1",
      "ql-indent-2",
      "ql-indent-3",
      "ql-indent-4",
      "ql-indent-5",
      "ql-indent-6",
      "ql-indent-7",
      "ql-indent-8",
      "ql-indent-9",
    ],
    li: [
      "ql-align-center",
      "ql-align-right",
      "ql-align-justify",
      "ql-indent-1",
      "ql-indent-2",
      "ql-indent-3",
      "ql-indent-4",
      "ql-indent-5",
      "ql-indent-6",
      "ql-indent-7",
      "ql-indent-8",
      "ql-indent-9",
    ],
    iframe: ["ql-video"],
    td: ["ql-align-center", "ql-align-right", "ql-align-justify"],
    select: ["ql-ui"],
    tr: ["ql-align-center", "ql-align-right", "ql-align-justify"],
  };

  const config = {
    ALLOWED_TAGS: allowed_tags,
    ALLOWED_ATTR: all_attributes,
    ALLOWED_URI_REGEXP:
      /^(?:(?:https?|mailto|tel):|[^a-z]|[a-z+-]+(?:[^a-z+-:]|$))/i,
    FORBID_CONTENTS: [] as string[],
  };

  // Add a hook to filter out unauthorized attributes and classes.
  DOMPurify.addHook("afterSanitizeAttributes", (node: Element) => {
    const tagName = node.nodeName.toLowerCase();

    // Remove any attribute not allowed for this tag.
    if (tagName in attributes_by_tag) {
      const allowedAttributes = new Set(attributes_by_tag[tagName]);
      const attrs = Array.from(node.attributes);
      for (const attr of attrs) {
        if (!allowedAttributes.has(attr.name)) {
          node.removeAttribute(attr.name);
        }
      }
    }

    // Filter class names: only allow those in the defined class allowlist.
    if (node.hasAttribute("class") && tagName in class_allowlist) {
      const allowedClasses = new Set(class_allowlist[tagName]);
      const classNames = node.getAttribute("class")?.split(/\s+/) ?? [];
      const filteredClasses = classNames.filter((cls: string) =>
        allowedClasses.has(cls)
      );

      if (filteredClasses.length > 0) {
        node.setAttribute("class", filteredClasses.join(" "));
      } else {
        node.removeAttribute("class");
      }
    }

    // For anchor tags, enforce a safe "rel" when target is "_blank".
    if (tagName === "a" && node.hasAttribute("href")) {
      if (node.getAttribute("target") === "_blank") {
        node.setAttribute("rel", "noopener noreferrer");
      }
    }
  });

  return DOMPurify.sanitize(html, config);
}

/**
 * Makes a request with specified options.
 * @param url - The endpoint URL.
 * @param opts - Request options including method, headers, and body.
 * @returns A promise that resolves to the response body.
 */

export const makeRequest = async (
  url: string,
  opts: RequestInit = {}
): Promise<ResponseBody> => {
  const jwt = localStorage.getItem("jwt");

  // Set credentials to include to send cookies
  opts.credentials = "include";

  // Set headers
  const headers = {
    ...Object.fromEntries(Object.entries(opts.headers ?? {})),
    ...(jwt &&
      !(opts.headers && "Authorization" in opts.headers) && {
        Authorization: `Bearer ${String(jwt)}`,
      }),
  };

  opts.headers = headers;

  // Add additional headers for specific request methods
  if (["POST", "PUT", "DELETE"].includes(opts.method ?? "")) {
    const updatedHeaders = {
      ...Object.fromEntries(Object.entries(opts.headers ?? {})),
      "Content-Type": "application/json",
      "X-CSRF-TOKEN": localStorage.getItem("csrfToken") ?? "",
    };

    opts.headers = updatedHeaders;
  }

  // Execute the request
  const response = await fetch(
    `${String(import.meta.env.VITE_FLASK_SERVER)}${url}`,
    opts
  );
  const body = (await response.json()) as ResponseBody;

  // Store CSRF token for future requests
  if (response.status === 200) {
    if (body.csrfAccessToken)
      localStorage.setItem("csrfToken", body.csrfAccessToken);
    if (body.jwt) localStorage.setItem("jwt", body.jwt);
  }

  // Throw an error if the response is not successful
  if (response.status !== 200) {
    // Return the original body to maintain compatibility with existing error handling
    const errorMessage =
      body.msg || `Request failed with status: ${String(response.status)}`;
    throw new Error(errorMessage);
  }

  return body;
};

/**
 * Downloads a file from a specified URL.
 * @param url - The URL of the file to download.
 * @returns A promise that resolves to the filename or an error message.
 */
export async function downloadExcelFromUrl(
  url: string
): Promise<string | null> {
  // Fetch the file from the server
  try {
    const jwt = localStorage.getItem("jwt");
    const opts: RequestInit = {
      method: "GET",
      credentials: "include",
      headers: {
        Authorization: `Bearer ${String(jwt)}`,
        Accept:
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      },
    };

    const response = await fetch(
      `${String(import.meta.env.VITE_FLASK_SERVER)}${String(url)}`,
      opts
    );

    if (!response.ok) {
      throw new Error(
        `Failed to fetch data: ${String(response.status)} ${response.statusText}`
      );
    }

    // Handle case where no data is found
    const contentType = response.headers.get("Content-Type");
    if (contentType?.includes("application/json")) {
      const jsonResponse = (await response.json()) as ResponseBody;
      if (jsonResponse.msg.includes("not found")) {
        return jsonResponse.msg;
      }
    }

    // Extract the filename from the "Content-Disposition" header
    const contentDisposition = response.headers.get("Content-Disposition");
    let filename = "download.xlsx"; // Default filename
    if (contentDisposition?.includes("filename=")) {
      filename = contentDisposition
        .split("filename=")[1]
        .split(";")[0]
        .replace(/"/g, "");
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
  return null;
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
  let url = `/auth/researcher/get-access?app=${String(app)}&action=${action}&resource=${resource}`;
  if (study) url += `&study=${String(study)}`;

  const res: ResponseBody = await makeRequest(url);
  if (res.msg !== "Authorized") throw new Error("Unauthorized");
};

/**
 * Given a study subject and study, fetch the study from the study subject's list of studies and return the study
 * subject's enrollment start and end dates for that study. If the study is not found or if `studySubject` is `null`,
 * return default dates.
 * @param studySubject - The study subject to get enrollment dates for.
 * @param studyId - The study to get enrollment dates for.
 * @returns { startsOn: Date, expiresOn: Date } - The study subject's enrollment start and end dates for the study.
 */
export const getEnrollmentInfoForStudy = (
  studySubject?: StudySubjectModel,
  studyId?: number
) => {
  // Return default dates if study subject or study ID is not provided
  if (!studySubject || !studyId) {
    const startsOn = new Date();
    const expiresOn = new Date();
    expiresOn.setDate(expiresOn.getDate() + 14);
    return { startsOn, expiresOn };
  }

  const currStudy = studySubject.studies.find((s) => s.study.id === studyId);

  if (currStudy) {
    const { startsOn, expiresOn, didConsent } = currStudy;
    return {
      startsOn: new Date(startsOn),
      expiresOn: new Date(expiresOn),
      didConsent,
    };
  }

  // Return default dates if the study is not found
  const startsOn = new Date();
  const expiresOn = new Date();
  expiresOn.setDate(expiresOn.getDate() + 14);

  return { startsOn, expiresOn, didConsent: false };
};

/**
 * Format a date specifically for an input element.
 * @param date - The date to format
 * @returns A string representing the date in the format "YYYY-MM-DD".
 */
export const formatDateForInput = (date: Date) => {
  // Get the year, month, and day
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0"); // Months are 0-indexed
  const day = String(date.getDate()).padStart(2, "0");

  // Format the date string
  return `${String(year)}-${month}-${day}`;
};

/**
 * Formats a phone number to ensure consistent international format.
 * - Strips non-digit characters except plus sign
 * - Ensures number starts with "+" and a valid country code
 * - Defaults to US country code (+1) when appropriate
 *
 * @param value - The phone number to format
 * @returns A formatted string in international phone number format
 */
export const formatPhoneNumber = (value: string): string => {
  // Remove everything except digits and plus sign
  const formattedValue = value.replace(/[^\d+]/g, "");

  // If empty, return empty string
  if (!formattedValue) {
    return "";
  }

  // If it's just a plus sign with nothing after it, add "1" as default US country code
  if (formattedValue === "+") {
    return "+1";
  }

  // If user entered digits without a plus sign, assume US number with +1 prefix
  if (/^\d+$/.test(formattedValue)) {
    return "+1" + formattedValue;
  }

  // If it already has a plus sign
  if (formattedValue.startsWith("+")) {
    // Handle case of +0... which is invalid (country codes cannot start with 0)
    if (formattedValue.length > 1 && formattedValue.charAt(1) === "0") {
      // Replace the 0 with US country code 1
      return "+1" + formattedValue.substring(2);
    }

    // Check for valid international format: + followed by at least one digit
    if (!/^\+\d+$/.test(formattedValue)) {
      // If it has non-digit after the +, replace with +1
      return "+1";
    }

    // Valid international format, keep as is
    return formattedValue;
  }

  // Any other case, default to +1 prefix
  return "+1" + formattedValue;
};
