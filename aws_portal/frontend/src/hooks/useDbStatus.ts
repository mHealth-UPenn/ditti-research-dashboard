import { useEffect, useState } from "react";
import { makeRequest } from "../utils";
import { ResponseBody } from "../interfaces";

/**
 * Monitor the application's connection status with the database.
 * 
 * It attempts an initial request to the `/touch` endpoint to check if the database is reachable.
 * 
 * @returns {boolean} - `true` if the database is still loading or unreachable, `false` if connected.
 */
export const useDbStatus = () => {
  const [loadingDb, setLoadingDb] = useState<boolean>(false);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const touch = async (): Promise<string> => {
      try {
        const res: ResponseBody = await makeRequest("/touch");
        if (res.msg === "OK" && intervalId) clearInterval(intervalId);
        return res.msg;
      } catch {
        return "Error";
      }
    };

    touch().then((msg: string) => {
      if (msg !== "OK") {
        setLoadingDb(true);
        intervalId = setInterval(() => touch(), 2000);
      }
    });

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  return loadingDb;
};
