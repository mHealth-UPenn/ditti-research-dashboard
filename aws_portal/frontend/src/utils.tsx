import { ResponseBody } from "./interfaces";

const getCookie = (name: string): string => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    const cookie = parts.pop()?.split(";")?.shift();
    return cookie ? cookie : "";
  } else {
    return "";
  }
};

export const makeRequest = async (url: string, opts?: any): Promise<any> => {
  if (opts) {
    opts.credentials = "include";
    opts.crossorigin = true;
  } else
    opts = {
      credentials: "include",
      corssorigin: true
    };

  if (opts && opts.method == "POST") {
    if (opts.headers) {
      opts.headers["Content-Type"] = "application/json";
      opts.headers["X-CSRF-Token"] = getCookie("csrf_access_token");
    } else
      opts.headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": getCookie("csrf_access_token")
      };
  }

  return fetch(process.env.REACT_APP_FLASK_SERVER + url, opts ? opts : {}).then(
    async (res) => {
      const body: ResponseBody = await res.json();

      if (res.status != 200)
        if (body.msg == "Token has expired" && url != "/iam/check-login")
          location.reload();
        else throw body;
      else return body;
    }
  );
};

export const getAccess = async (
  app: number,
  action: string,
  resource: string,
  study?: number
): Promise<void> => {
  let url = `/iam/get-access?app=${app}&action=${action}&resource=${resource}`;
  if (study) url += `&study=${study}`;
  const res: ResponseBody = await makeRequest(url);
  if (res.msg != "Authorized") throw "Unauthorized";
};
