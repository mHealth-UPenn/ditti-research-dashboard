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

import {
  createContext,
  PropsWithChildren,
  useEffect,
  useMemo,
  useState,
  useCallback,
} from "react";
import { APP_ENV } from "../environment";
import { DataFactory } from "../dataFactory";
import { httpClient } from "../lib/http";
import {
  WearableDataContextValue,
  CoordinatorWearableDataProviderProps,
} from "./wearableDataContext.types";
import { SleepLog, DataProcessingTask, ResponseBody } from "../types/api";

// Context return type for participants
export const ParticipantWearableDataContext = createContext<
  WearableDataContextValue | undefined
>(undefined);

// Context return type for coordinators
export const CoordinatorWearableDataContext = createContext<
  WearableDataContextValue | undefined
>(undefined);

/**
 * Format a date in YYYY-MM-DD format.
 * @param date The date to format.
 * @returns string: The formatted date.
 */
const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  // Ensure year is treated as a string in the template literal
  return `${String(year)}-${month}-${day}`;
};

// ParticipantWearableDataProvider component that wraps children with the study subject context.
export const ParticipantWearableDataProvider = ({
  children,
}: PropsWithChildren) => {
  const start = new Date();
  start.setDate(start.getDate() - 6);

  const [sleepLogs, setSleepLogs] = useState<SleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // For now participants do not have the ability to change the start and end dates
  const startDate = start; // Start one week ago
  const endDate = useMemo(() => new Date(), []); // End today

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  const handleFailure = useCallback((error: unknown, context?: string) => {
    const prefix = context ? `${context}: ` : "";
    console.error(prefix, error);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    setIsLoading(true);
    // Async fetch sleep data
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production" || APP_ENV === "development") {
          const params = new URLSearchParams();
          params.append("start_date", formatDate(startDate));
          params.append("end_date", formatDate(endDate));
          const url = `/participant/fitbit_data?${params.toString()}`;
          let data = await httpClient.request<SleepLog[]>(url);

          data = data.sort((a, b) => {
            if (a.dateOfSleep > b.dateOfSleep) return 1;
            else if (a.dateOfSleep < b.dateOfSleep) return -1;
            else return 0;
          });

          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error) {
        handleFailure(error, "Failed to fetch participant sleep data");
      } finally {
        setIsLoading(false);
      }
    };

    void fetchSleepData();
  }, [dataFactory, startDate, endDate, handleFailure]);

  return (
    <ParticipantWearableDataContext.Provider
      value={{
        startDate,
        endDate,
        sleepLogs,
        isLoading,
      }}
    >
      {children}
    </ParticipantWearableDataContext.Provider>
  );
};

export const CoordinatorWearableDataProvider = ({
  children,
  dittiId,
  studyId,
}: PropsWithChildren<CoordinatorWearableDataProviderProps>) => {
  const start = new Date();
  start.setDate(start.getDate() - 7);

  const [startDate, setStartDate] = useState<Date>(start); // Start one week ago
  const [endDate, setEndDate] = useState<Date>(new Date()); // End today
  const [sleepLogs, setSleepLogs] = useState<SleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  // True when new data was fetched and updated
  const [dataIsUpdated, setDataIsUpdated] = useState(false);

  // The date of the first sleep log entry
  const [firstDateOfSleep, setFirstDateOfSleep] = useState<Date | null>(null);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  const handleFailure = useCallback((error: unknown, context?: string) => {
    const prefix = context ? `${context}: ` : "";
    console.error(prefix, error);
    setIsLoading(false);
    setIsSyncing(false);
  }, []);

  /**
   * Fetch sleep log data asynchronously from a start date to an end date.
   * @param start: The start date to fetch data from.
   * @param end: The end date to fetch data to.
   * @returns Promise<SleepLog[]>: The fetched sleep log data.
   */
  const fetchSleepDataAsync = useCallback(
    async (start: Date, end: Date): Promise<SleepLog[]> => {
      const params = new URLSearchParams();
      params.append("start_date", formatDate(start));
      params.append("end_date", formatDate(end));
      params.append("app", "3");
      params.append("study", String(studyId));
      const url = `/admin/fitbit_data/${dittiId}?${params.toString()}`;

      try {
        let data = await httpClient.request<SleepLog[]>(url);
        data = data.sort((a, b) => {
          if (a.dateOfSleep > b.dateOfSleep) return 1;
          else if (a.dateOfSleep < b.dateOfSleep) return -1;
          else return 0;
        });
        return data;
      } catch (error) {
        console.error("Failed to fetch sleep data async:", error);
        throw error;
      }
    },
    [dittiId, studyId]
  );

  /**
   * Schedule an interval to repeatedly check the status of a data processing task.
   * @param taskId: The ID of the data processing task to check.
   */
  const scheduleSyncCheck = useCallback(
    (taskId: number) => {
      const checkStatus = async () => {
        try {
          const params = new URLSearchParams();
          params.append("app", "3");
          params.append("study", String(studyId));
          const url = `/data_processing_task/${String(taskId)}?${params.toString()}`;
          const tasks = await httpClient.request<DataProcessingTask[]>(url);

          if (
            tasks.length > 0 &&
            !(tasks[0].status == "Pending" || tasks[0].status == "InProgress")
          ) {
            clearInterval(intervalId);
            setIsSyncing(false);

            // Reset dates and fetch new data
            const updatedStartDate = new Date();
            updatedStartDate.setDate(updatedStartDate.getDate() - 7);
            setStartDate(updatedStartDate);
            const updatedEndDate = new Date();
            setEndDate(updatedEndDate);

            try {
              const data = await fetchSleepDataAsync(
                updatedStartDate,
                updatedEndDate
              );
              setSleepLogs(data);
              if (data.length) {
                setFirstDateOfSleep(new Date(data[0].dateOfSleep));
              }
              setDataIsUpdated(false);
            } catch (fetchError) {
              handleFailure(fetchError, "Failed to refresh data after sync");
            }
          }
        } catch (error: unknown) {
          console.error(
            `Error checking sync status for task ${String(taskId)}:`,
            error
          );
          clearInterval(intervalId);
          handleFailure(error, `Sync check failed for task ${String(taskId)}`);
        }
      };

      const intervalId = setInterval(() => {
        void checkStatus();
      }, 5000);

      return () => {
        clearInterval(intervalId);
      };
    },
    [fetchSleepDataAsync, studyId, handleFailure]
  );

  // Fetch initial sleep data and check for ongoing sync tasks
  useEffect(() => {
    setIsLoading(true);
    let cleanupInterval: (() => void) | undefined;

    const fetchInitialData = async () => {
      try {
        // Fetch initial sleep data
        const initialSleepDataPromise = (async () => {
          try {
            const data = await fetchSleepDataAsync(startDate, endDate);
            if (data.length) {
              setFirstDateOfSleep(new Date(data[0].dateOfSleep));
            }
            setSleepLogs(data);
          } catch (error) {
            console.error("Failed to fetch initial sleep data:", error);
            handleFailure(error, "Initial data fetch failed");
          }
        })();

        // Fetch data processing tasks
        const tasksPromise = (async () => {
          try {
            if (APP_ENV === "production" || APP_ENV === "development") {
              const params = new URLSearchParams();
              params.append("app", "3");
              params.append("study", String(studyId));
              const url = `/data_processing_task/?${params.toString()}`;
              const tasks = await httpClient.request<DataProcessingTask[]>(url);

              const syncingTask = tasks.find(
                (task) =>
                  task.status == "Pending" || task.status == "InProgress"
              );
              if (syncingTask) {
                setIsSyncing(true);
                cleanupInterval = scheduleSyncCheck(syncingTask.id);
              }
            }
          } catch (error) {
            console.error("Failed to fetch data processing tasks:", error);
            handleFailure(error, "Failed to check sync status");
          }
        })();

        // Wait for both fetches
        await Promise.all([initialSleepDataPromise, tasksPromise]);
      } catch (error) {
        console.error("Error during initial data loading sequence:", error);
        handleFailure(error, "Initial load error");
      } finally {
        setIsLoading(false);
      }
    };

    void fetchInitialData();

    return () => {
      if (cleanupInterval) {
        cleanupInterval();
      }
    };
  }, [
    dittiId,
    studyId,
    startDate,
    endDate,
    dataFactory,
    fetchSleepDataAsync,
    scheduleSyncCheck,
    handleFailure,
  ]);

  // Handle the user clicking Sync Data
  const syncData = async () => {
    if (!isSyncing) {
      setIsSyncing(true);
      setIsLoading(true);
      try {
        const params = new URLSearchParams();
        params.append("app", "3");
        params.append("study", String(studyId));
        const url = `/data_processing_task/invoke/${dittiId}?${params.toString()}`;

        const res = await httpClient.request<ResponseBody>(url, {
          method: "POST",
        });

        if (res.msg.includes("successfully invoked")) {
          const tasks = await httpClient.request<DataProcessingTask[]>(
            `/data_processing_task/?app=3&study=${String(studyId)}`
          );
          const newTask = tasks.find(
            (t) => t.status === "Pending" || t.status === "InProgress"
          );
          if (newTask) {
            scheduleSyncCheck(newTask.id);
          } else {
            console.warn("Sync invoked but no pending task found immediately.");
            setIsSyncing(false);
          }
        } else {
          console.warn("Sync invoked but response format unexpected:", res.msg);
          handleFailure(
            new Error(res.msg || "Invocation failed"),
            "Sync Invocation Problem"
          );
        }
      } catch (error: unknown) {
        console.error(`Error invoking sync task:`, error);
        handleFailure(error, "Sync Invocation Failed");
      } finally {
        setIsLoading(false);
      }
    }
  };

  // The start date can be incremented if the end date is less than today
  const canIncrementStartDate = useMemo(() => {
    const today = new Date();
    const todayWithoutTime = new Date(
      today.getFullYear(),
      today.getMonth(),
      today.getDate()
    );
    const endWithoutTime = new Date(
      endDate.getFullYear(),
      endDate.getMonth(),
      endDate.getDate()
    );

    // Only increment if the end date is less than today
    return endWithoutTime < todayWithoutTime;
  }, [endDate]);

  // Decrement the start and end dates by one day
  const decrementStartDate = () => {
    const updatedStartDate = new Date(startDate);
    updatedStartDate.setDate(startDate.getDate() - 1);
    setStartDate(updatedStartDate);

    const updatedEndDate = new Date(endDate);
    updatedEndDate.setDate(endDate.getDate() - 1);
    setEndDate(updatedEndDate);

    // Fetch new data if the start date is before the first date of sleep
    if (firstDateOfSleep && updatedStartDate < firstDateOfSleep) {
      fetchSleepDataAsync(updatedStartDate, updatedStartDate)
        .then((data) => {
          const updatedSleepLogs = [...data, ...sleepLogs];
          setSleepLogs(updatedSleepLogs);
          if (data.length) {
            setFirstDateOfSleep(new Date(data[0].dateOfSleep));
          }
          setDataIsUpdated(true);
        })
        .catch((error: unknown) => {
          console.error(`Error updating sleep log data: ${String(error)}`);
        });
    }
  };

  // Increment the start and end dates by one day
  const incrementStartDate = () => {
    if (canIncrementStartDate) {
      const updatedStartDate = new Date(startDate);
      updatedStartDate.setDate(startDate.getDate() + 1);
      setStartDate(updatedStartDate);

      const updatedEndDate = new Date(endDate);
      updatedEndDate.setDate(endDate.getDate() + 1);
      setEndDate(updatedEndDate);
    }
  };

  // Reset the start and end dates
  const resetStartDate = () => {
    const start = new Date();
    start.setDate(start.getDate() - 7);
    setStartDate(start);
    setEndDate(new Date());
  };

  return (
    <CoordinatorWearableDataContext.Provider
      value={{
        startDate,
        endDate,
        sleepLogs,
        isLoading,
        isSyncing,
        dataIsUpdated,
        firstDateOfSleep,
        canIncrementStartDate,
        decrementStartDate,
        incrementStartDate,
        resetStartDate,
        syncData: () => {
          void syncData();
        },
      }}
    >
      {children}
    </CoordinatorWearableDataContext.Provider>
  );
};
