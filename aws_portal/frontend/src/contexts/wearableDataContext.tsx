import { createContext, PropsWithChildren, useContext, useEffect, useMemo, useState } from 'react';
import { ISleepLog, IWearableDataContextType } from '../interfaces';
import { APP_ENV } from '../environment';
import DataFactory from '../dataFactory';


const WearableDataContext = createContext<IWearableDataContextType | undefined>(undefined);


export const WearableDataProvider = ({ children }: PropsWithChildren<void>) => {
  const [sleepLogs, setSleepLogs] = useState<ISleepLog[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    const fetchSleepData = async () => {
      setIsLoading(true);
      try {
        if (APP_ENV === "production") {
          const response = await fetch('/api/sleepdata'); // Adjust API endpoint as necessary
          if (!response.ok) {
            throw new Error('Failed to fetch sleep data');
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
    <WearableDataContext.Provider value={{ sleepLogs, isLoading, error }}>
      {children}
    </WearableDataContext.Provider>
  );
};

// Custom hook for accessing the context
export const useWearableData = (): IWearableDataContextType => {
  const context = useContext(WearableDataContext);
  if (context === undefined) {
    throw new Error('useWearableData must be used within a WearableDataProvider');
  }
  return context;
};
