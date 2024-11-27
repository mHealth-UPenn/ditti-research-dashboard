import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from "react";
import { ISleepLog, IWearableDataContextType } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";


const ParticipantWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);
const CoordinatorWearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);


export const ParticipantWearableDataProvider = ({ children }: PropsWithChildren<any>) => {
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production") {
          const response = await fetch("/api/sleepdata");
          if (!response.ok) {
            throw new Error("Failed to fetch sleep data");
          }
          const data: ISleepLog[] = await response.json();
          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error: any) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSleepData();
  }, []);

  return (
    <ParticipantWearableDataContext.Provider value={{ sleepLogs, isLoading, error }}>
      {children}
    </ParticipantWearableDataContext.Provider>
  );
};


export const CoordinatorWearableDataProvider = ({ children }: PropsWithChildren<any>) => {
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    const fetchSleepData = async () => {
      try {
        if (APP_ENV === "production") {
          const response = await fetch("/api/sleepdata");
          if (!response.ok) {
            throw new Error("Failed to fetch sleep data");
          }
          const data: ISleepLog[] = await response.json();
          setSleepLogs(data);
        } else if (dataFactory) {
          await dataFactory.init();
          setSleepLogs(dataFactory.sleepLogs);
        }
      } catch (error: any) {
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchSleepData();
  }, []);

  return (
    <CoordinatorWearableDataContext.Provider value={{ sleepLogs, isLoading, error }}>
      {children}
    </CoordinatorWearableDataContext.Provider>
  );
};


// Custom hook for accessing the context
export const useWearableData = (): IWearableDataContextType => {
  let participantContext = useContext(ParticipantWearableDataContext);
  let coordinatorContext = useContext(CoordinatorWearableDataContext);
  if (participantContext !== undefined) {
    return participantContext;
  } else if (coordinatorContext !== undefined) {
    return coordinatorContext;
  }
  throw new Error("useWearableData must be used within a WearableDataProvider");
};
