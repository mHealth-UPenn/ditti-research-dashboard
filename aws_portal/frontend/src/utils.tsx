import { TapDetails, User } from "./interfaces";

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
      if (res.status != 200) throw await res.json();
      else return await res.json();
    }
  );
};

export const mapTaps = (
  tapDetails: TapDetails[],
  userDetails: User[]
): { dittiId: string; time: Date }[] => {
  let taps = tapDetails.sort((a, b) => {
    if (a.tapUserId < b.tapUserId) return -1;
    if (a.tapUserId > b.tapUserId) return 1;
    return 0;
  });

  const unique = taps
    .map((t) => t.tapUserId)
    .filter((v, i, arr) => arr.indexOf(v) === i);

  const users = userDetails
    .filter((u) => unique.includes(u.id))
    .sort((a, b) => {
      if (a.id < b.id) return -1;
      if (a.id > b.id) return 1;
      return 0;
    });

  const data: { dittiId: string; time: Date }[] = [];

  let i = 0;
  while (taps[i].tapUserId != users[0].id) i += 1;
  taps = taps.slice(i);

  let skip = false;
  for (const t of taps) {
    if (users.length && !skip && t.tapUserId != users[0].id) users.shift();
    if (!users.length) break;
    skip = t.tapUserId != users[0].id;

    if (!skip) {
      const date = new Date(t.time);
      const time = date.getTime() - date.getTimezoneOffset() * 60000;
      data.push({ dittiId: users[0].user_permission_id, time: new Date(time) });
    }
  }

  return data;
};
