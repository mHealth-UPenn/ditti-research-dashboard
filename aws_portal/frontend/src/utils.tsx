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
  if (opts && opts.method == "POST")
    opts.headers["X-CSRF-TOKEN"] = getCookie("csrf_access_token");

  return fetch(process.env.REACT_APP_FLASK_SERVER + url, opts ? opts : {}).then(
    async (res) => {
      if (res.status != 200) throw await res.json();
      else return await res.json();
    }
  );
};
