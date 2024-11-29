// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { StudiesContextType, Study } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";

export const StudiesContext = createContext<StudiesContextType | undefined>(undefined);

interface IStudiesProviderProps {
  app: 1 | 2 | 3;  // Ditti App, Admin Dashboard, Wearable Dashboard
}


/**
 * StudiesProvider component that wraps children with studies context.
 */
export default function StudiesProvider({
  app,
  children
}: PropsWithChildren<IStudiesProviderProps>) {
  const [studies, setStudies] = useState<Study[]>([]);
  const [studiesLoading, setStudiesLoading] = useState(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  useEffect(() => {
    // Use a list to mirror context design pattern
    const promises: Promise<any>[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      promises.push(getStudiesAsync().then(setStudies));
    } else if (APP_ENV === "demo" && dataFactory) {
      setStudies(dataFactory.studies);
    }

    Promise.all(promises).then(() => setStudiesLoading(false));
  }, []);

  const getStudiesAsync = async (): Promise<Study[]> => {
    let studies: Study[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      studies = await makeRequest(`/db/get-studies?app=${app}`)
        .catch(() => {
          console.error("Unable to fetch studies data. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      studies = dataFactory.studies;
    }

    return studies;
  };

  return (
    <StudiesContext.Provider
      value={{ studies, studiesLoading }}>
        {children}
    </StudiesContext.Provider>
  );
}


export function useStudiesContext() {
  const context = useContext(StudiesContext);
  if (!context) {
    throw new Error("useStudiesContext must be used within a StudiesContext provider");
  }
  return context;
}
