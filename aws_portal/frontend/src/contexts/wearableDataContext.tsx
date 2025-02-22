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

import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from "react";
import { IDataProcessingTask, ISleepLog,  IWearableDataContextType } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";
import { makeRequest } from "../utils";
// import { useFlashMessageContext } from "./flashMessagesContext";


// Context return type for participants
const ParticipantWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);

// Context return type for coordinators
const CoordinatorWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);


/**
 * Format a date in YYYY-MM-DD format.
 * @param date The date to format.
 * @returns string: The formatted date.
 */
const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}


// ParticipantWearableDataProvider component that wraps children with the study subject context.
export const ParticipantWearableDataProvider = ({ children }: PropsWithChildren<any>) => {
  const start = new Date();
  start.setDate(start.getDate() - 6);

  // For now participants do not have the ability to change the start and end dates
  const [startDate, setStartDate] = useState<Date>(start);  // Start one week ago
  const [endDate, setEndDate] = useState<Date>(new Date());  // End today
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // const { flashMessage } = useFlashMessageContext();

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  const handleFailure = (error: any) => {
    console.error(error);
    // const msg = 
    //   <span>
    //     <b>An unexpected error occurred</b>
    //     <br />
    //     {error.msg ? error.msg : "Internal server error"}
    //   </span>
    // flashMessage(msg, "danger");
  }

  useEffect(() => {

    // Async fetch sleep data
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production" || APP_ENV === "development") {
          const params = new URLSearchParams();
          params.append("start_date", formatDate(startDate));
          params.append("end_date", formatDate(endDate));
          const url = `/participant/fitbit_data?${params.toString()}`
          let data: ISleepLog[] = await makeRequest(url);

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
      } catch (error: any) {
        handleFailure(error);
      }
    };

    const promises: Promise<void>[] = [];
    promises.push(fetchSleepData());
    Promise.all(promises).finally(() => setIsLoading(false))
  }, []);

  return (
    <ParticipantWearableDataContext.Provider value={{
        startDate,
        endDate,
        sleepLogs,
        isLoading,
      }}>
        {children}
    </ParticipantWearableDataContext.Provider>
  );
};


/**
 * Props for the coordinator wearable data provider.
 * @property dittiId: The Ditti ID of the participant whose data to fetch.
 * @property studyId: The ID of the study to fetch data for.
 */
export interface ICoordinatorWearableDataProvider {
  dittiId: string;
  studyId: number;
}


export const CoordinatorWearableDataProvider = ({
  children,
  dittiId,
  studyId,
}: PropsWithChildren<ICoordinatorWearableDataProvider>) => {
  const start = new Date();
  start.setDate(start.getDate() - 7);

  const [startDate, setStartDate] = useState<Date>(start);  // Start one week ago
  const [endDate, setEndDate] = useState<Date>(new Date());  // End today
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSyncing, setIsSyncing] = useState<boolean>(false);

  // True when new data was fetched and updated
  const [dataIsUpdated, setDataIsUpdated] = useState(false);

  // The date of the first sleep log entry
  const [firstDateOfSleep, setFirstDateOfSleep] = useState<Date | null>(null);

  // const { flashMessage } = useFlashMessageContext();

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  const handleFailure = (error: any) => {
    console.error(error);
    const msg = 
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {error.msg ? error.msg : "Internal server error"}
      </span>
    // flashMessage(msg, "danger");
  }

  /**
   * Fetch sleep log data asynchronously from a start date to an end date.
   * @param start: The start date to fetch data from.
   * @param end: The end date to fetch data to.
   * @returns ISleepLog[]: The fetched sleep log data.
   */
  const fetchSleepDataAsync = async (start: Date, end: Date) => {
    const params = new URLSearchParams();
    params.append("start_date", formatDate(start));
    params.append("end_date", formatDate(end));
    params.append("app", "3");  // Assume Wearable Dashboard is app 3
    params.append("study", studyId.toString());
    const url = `/admin/fitbit_data/${dittiId}?${params.toString()}`

    let data: ISleepLog[] = await makeRequest(url);
    data = data.sort((a, b) => {
      if (a.dateOfSleep > b.dateOfSleep) return 1;
      else if (a.dateOfSleep < b.dateOfSleep) return -1;
      else return 0;
    });

    return data;
  };

  // Fetch sleep data and data processing tasks on component mount
  useEffect(() => {
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production" || APP_ENV === "development") {
          const data = await fetchSleepDataAsync(startDate, endDate);
          if (data.length) {
            setFirstDateOfSleep(new Date(data[0].dateOfSleep));
          }
          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error: any) {
        handleFailure(error);
      }
    };

    // Fetch all data processing tasks and find if any are syncing
    const fetchDataProcessingTasks = async () => {
      try {
        if (APP_ENV === "production" || APP_ENV === "development") {
          const params = new URLSearchParams();
          params.append("app", "3");  // Assume Wearable Dashboard is app 3
          params.append("study", studyId.toString());
          const url = `/data_processing_task/?${params.toString()}`;
          const tasks: IDataProcessingTask[] = await makeRequest(url);

          // Check if any tasks are syncing
          const syncingTask = tasks.find(task => task.status == "Pending" || task.status == "InProgress");
          if (syncingTask) {
            setIsSyncing(true);
            scheduleSyncCheck(syncingTask.id);
          }
        }
      } catch (error: any) {
        handleFailure(error);
      }
    };

    const promises: Promise<void>[] = [];
    promises.push(fetchSleepData());
    promises.push(fetchDataProcessingTasks());
    Promise.all(promises).finally(() => setIsLoading(false))
  }, []);

  /**
   * Schedule an interval to repeatedly check the status of a data processing task.
   * @param taskId: The ID of the data processing task to check.
   */
  const scheduleSyncCheck = (taskId: number) => {
    const id = setInterval(async () => {
      const params = new URLSearchParams();
      params.append("app", "3");  // Assume Wearable Dashboard is app 3
      params.append("study", studyId.toString());
      const url = `/data_processing_task/${taskId}?${params.toString()}`;
      const tasks: IDataProcessingTask[] = await makeRequest(url);

      // Assume one task is returned
      if (!(tasks[0].status == "Pending" || tasks[0].status == "InProgress")) {
        // When the task is no longer running, clear the interval
        clearInterval(id);
        setIsSyncing(false);

        // Reset the start and end dates to fetch new data
        const updatedStartDate = new Date();
        updatedStartDate.setDate(updatedStartDate.getDate() - 7);
        setStartDate(updatedStartDate);
        const updatedEndDate = new Date();
        setEndDate(updatedEndDate);

        // Fetch new data
        fetchSleepDataAsync(updatedStartDate, updatedEndDate)
          .then(data => {
            setSleepLogs(data);
            if (data.length) {
              setFirstDateOfSleep(new Date(data[0].dateOfSleep));
            }
            setDataIsUpdated(false);
          })
          .catch(error => console.error(`Error updating sleep log data: ${error}`));
      }
    }, 1000);
  };

  // Handle the user clicking Sync Data
  const syncData = async () => {
    // Only sync data if not already syncing
    if (!isSyncing) {
      // Invoke the data processing task
      const params = new URLSearchParams();
      params.append("app", "3");
      params.append("study", studyId.toString());
      const url = `/data_processing_task/invoke?${params.toString()}`;
      const opts: RequestInit = {
        method: "POST",
        body: JSON.stringify({ app: 3 }),
      }

      // Fetch the data processing task ID for checking status
      type ResponseBody = { msg: string; task: IDataProcessingTask; };
      const res: ResponseBody  = await makeRequest(url, opts);

      setIsSyncing(true);
      scheduleSyncCheck(res.task.id);
    }
  };

  // The start date can be incremented if the end date is less than today
  const canIncrementStartDate = useMemo(() => {
    const today = new Date();
    const todayWithoutTime = new Date(today.getFullYear(), today.getMonth(), today.getDate());
    const endWithoutTime = new Date(endDate.getFullYear(), endDate.getMonth(), endDate.getDate());

    // Only increment if the end date is less than today
    return endWithoutTime < todayWithoutTime;
  }, [startDate, endDate]);

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
        .then(data => {
          const updatedSleepLogs = [...data, ...sleepLogs];
          setSleepLogs(updatedSleepLogs);
          if (data.length) {
            setFirstDateOfSleep(new Date(data[0].dateOfSleep));
          }
          setDataIsUpdated(true);
        })
        .catch(error => console.error(`Error updating sleep log data: ${error}`));
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
    <CoordinatorWearableDataContext.Provider value={{
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
        syncData,
      }}>
        {children}
    </CoordinatorWearableDataContext.Provider>
  );
};


// Custom hook for accessing the context
// Returns either the participant or coordinator context depending on which provider was used
export const useWearableData = (): IWearableDataContextType => {
  const participantContext = useContext(ParticipantWearableDataContext);
  const coordinatorContext = useContext(CoordinatorWearableDataContext);
  if (participantContext !== undefined) {
    return participantContext;
  } else if (coordinatorContext !== undefined) {
    return coordinatorContext;
  }
  throw new Error("useWearableData must be used within a WearableDataProvider");
};
