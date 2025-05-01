import { useEffect, useState } from "react";
import { makeRequest } from "../utils";
import { ResponseBody } from "../types/api";

/**
 * Monitor the application's connection status with the database.
 *
 * It attempts an initial request to the `/touch` endpoint to check if the database is reachable.
 *
 * @returns {boolean} - `true` if the database is still loading or unreachable, `false` if connected.
 */
export const useDbStatus = () => {
  const [loadingDb, setLoadingDb] = useState<boolean>(true);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const touch = async (): Promise<string> => {
      try {
        const res: ResponseBody = await makeRequest("/touch");
        if (res.msg === "OK") {
          setLoadingDb(false);
          clearInterval(intervalId);
        }
        return res.msg;
      } catch {
        return "Error";
      }
    };

    // Use void to explicitly mark promise as intentionally not awaited
    void (async () => {
      const msg = await touch();
      if (msg !== "OK") {
        intervalId = setInterval(() => {
          void touch();
        }, 2000);
      }
    })();

    return () => {
      clearInterval(intervalId);
    };
  }, []);

  return loadingDb;
};
