import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from "react";
import { ISleepLog, IStudySubject, IWearableDataContextType } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";
import { makeRequest } from "../utils";


const ParticipantWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);
const CoordinatorWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);


const formatDate = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}


export const ParticipantWearableDataProvider = ({ children }: PropsWithChildren<any>) => {
  const start = new Date();
  start.setDate(start.getDate() - 6);

  const [startDate, setStartDate] = useState<Date>(start);  // Start one week ago
  const [endDate, setEndDate] = useState<Date>(new Date());  // End today
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
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
          })

          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error: any) {
        console.error(error);
      }
    };

    const promises: Promise<void>[] = [];
    promises.push(fetchSleepData());
    Promise.all(promises).finally(() => setIsLoading(false))
  }, []);

  return (
    <ParticipantWearableDataContext.Provider value={{ sleepLogs, isLoading }}>
      {children}
    </ParticipantWearableDataContext.Provider>
  );
};


export const CoordinatorWearableDataProvider = ({ children, dittiId }: PropsWithChildren<{ dittiId: string }>) => {
  const start = new Date();
  start.setDate(start.getDate() - 6);

  const [startDate, setStartDate] = useState<Date>(start);  // Start one week ago
  const [endDate, setEndDate] = useState<Date>(new Date());  // End today
  const [studySubjects, setStudySubjects] = useState<IStudySubject[]>([]);
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production" || APP_ENV === "development") {
          const params = new URLSearchParams();
          params.append("start_date", formatDate(startDate));
          params.append("end_date", formatDate(endDate));
          params.append("app", "3");
          const url = `/admin/fitbit_data/${dittiId}?${params.toString()}`
          let data: ISleepLog[] = await makeRequest(url);
          data = data.sort((a, b) => {
            if (a.dateOfSleep > b.dateOfSleep) return 1;
            else if (a.dateOfSleep < b.dateOfSleep) return -1;
            else return 0;
          })

          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error: any) {
        console.error(error);
        throw error;
      }
    };

    const promises: Promise<void>[] = [];
    promises.push(fetchSleepData());
    Promise.all(promises).finally(() => setIsLoading(false))
  }, []);

  return (
    <CoordinatorWearableDataContext.Provider value={{ sleepLogs, isLoading }}>
      {children}
    </CoordinatorWearableDataContext.Provider>
  );
};


// Custom hook for accessing the context
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
