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

import { useEffect, useState } from "react";
import { useHttpClient } from "../lib/HttpClientContext";
import { ResponseBody } from "../types/api";

/**
 * Monitor the application's connection status with the database.
 *
 * It attempts an initial request to the `/touch` endpoint to check if the database is reachable.
 *
 * @returns {boolean} - `true` if the database is still loading or unreachable, `false` if connected.
 */
export const useDbStatus = () => {
  const { request } = useHttpClient();
  const [loadingDb, setLoadingDb] = useState<boolean>(true);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const touch = async (): Promise<string> => {
      try {
        const res = await request<ResponseBody>("/touch");
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
  }, [request]);

  return loadingDb;
};
