/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
  const [loadingDb, setLoadingDb] = useState<boolean>(true);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const touch = async (): Promise<string> => {
      try {
        const res: ResponseBody = await makeRequest("/touch");
        if (res.msg === "OK") setLoadingDb(false);
        if (res.msg === "OK" && intervalId) clearInterval(intervalId);
        return res.msg;
      } catch {
        return "Error";
      }
    };

    touch().then((msg: string) => {
      if (msg !== "OK") {
        intervalId = setInterval(() => touch(), 2000);
      }
    });

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  return loadingDb;
};
