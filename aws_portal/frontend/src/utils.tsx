import { ResponseBody } from "./interfaces";

let csrfAccessToken = "";
const crossorigin = Boolean(process.env.CROSSORIGIN)

// make a request with options
export const makeRequest = async (url: string, opts?: any): Promise<any> => {

  // set credentials and crossorigin options
  if (opts) {
    // opts.credentials = "include";
    opts.crossorigin = crossorigin;
  } else
    opts = {
      // credentials: "include",
      corssorigin: crossorigin
    };

  // if making a POST request
  if (opts && opts.method == "POST") {

    // set the content type and CSRF token headers
    if (opts.headers) {
      opts.headers["Content-Type"] = "application/json";
      opts.headers["X-CSRF-Token"] = csrfAccessToken;
    } else
      opts.headers = {
        "Content-Type": "application/json",
        "X-CSRF-Token": csrfAccessToken
      };
  }

  // make the request
  return fetch(process.env.REACT_APP_FLASK_SERVER + url, opts ? opts : {}).then(
    async (res) => {
      const body: ResponseBody = await res.json();

      // save the CSRF token for the next request
      if (res.status == 200 && body.csrfAccessToken)
        csrfAccessToken = body.csrfAccessToken;

      if (res.status != 200)

        // if the user's token expired, refresh the page to show the login screen
        if (body.msg == "Token has expired" && url != "/iam/check-login")
          location.reload();
        else throw body;
      else return body;
    }
  );
};

// check whether the user is allowed to complete a requested action on a requested resource
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
