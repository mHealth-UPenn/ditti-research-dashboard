// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { StudiesContextType, Study } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";
import { useNavbarContext } from "./navbarContext";
import { useSearchParams } from "react-router-dom";

export const StudiesContext = createContext<StudiesContextType | undefined>(undefined);

interface IStudiesProviderProps {
  app: 2 | 3;  // Ditti App, Wearable Dashboard
}


// StudiesProvider component that wraps children with studies context.
export default function StudiesProvider({
  app,
  children
}: PropsWithChildren<IStudiesProviderProps>) {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;

  const [studies, setStudies] = useState<Study[]>([]);
  const [study, setStudy] = useState<Study | null>(null);
  const [studiesLoading, setStudiesLoading] = useState(true);
  const { setStudyCrumb } = useNavbarContext();

  const appSlug = app === 2 ? "ditti" : "wearable";

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  // Make an sync request to get studies from the database
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

  // Fetch studies on load
  useEffect(() => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      getStudiesAsync().then(studies => {
        setStudies(studies)
        const study = studies.find(s => s.id === studyId);
        if (study) {
          setStudy(study);
          setStudyCrumb({ name: study.acronym, link: `/coordinator/${appSlug}/study?sid=${study.id}` });
        }
        setStudiesLoading(false)
      });
    } else if (APP_ENV === "demo" && dataFactory) {
      setStudies(dataFactory.studies);
      setStudiesLoading(false);
    }
  }, [studyId]);

  return (
    <StudiesContext.Provider
      value={{ studies, studiesLoading, study }}>
        {children}
    </StudiesContext.Provider>
  );
}


// Hook for accessing context data
export function useStudiesContext() {
  const context = useContext(StudiesContext);
  if (!context) {
    throw new Error("useStudiesContext must be used within a StudiesContext provider");
  }
  return context;
}
