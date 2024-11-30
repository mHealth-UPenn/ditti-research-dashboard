// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { StudySubjectContextType, Study, StudyJoin, ApiJoin } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";

export const StudySubjectContext = createContext<StudySubjectContextType | undefined>(undefined);


/**
 * StudySubjectProvider component that wraps children with the study subject context.
 */
export default function StudySubjectProvider({
  children
}: PropsWithChildren<unknown>) {
  const [studies, setStudies] = useState<StudyJoin[]>([]);
  const [apis, setApis] = useState<ApiJoin[]>([])
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      // return new DataFactory();
      return null;  // Until this data is available in the data factory
    }
    return null;
  }, []);

  useEffect(() => {
    // Use a list to mirror context design pattern
    const promises: Promise<any>[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      promises.push(getStudySubject().then(([studiesData, apisData]) => {
        setStudies(studiesData);
        setApis(apisData);
      }));
    // } else if (APP_ENV === "demo" && dataFactory) {
    }

    Promise.all(promises).then(() => setStudySubjectLoading(false));
  }, []);

  const getStudySubject = async (): Promise<[StudyJoin[], ApiJoin[]]> => {
    const studiesData: StudyJoin[] = [];
    const apisData: ApiJoin[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      const data = await makeRequest(`/participant`)
        .catch(() => {
          console.error("Unable to fetch participant data.")
          return [];
        });
      console.log(data);
    // } else if (dataFactory) {
    //   studies = dataFactory.studies;
    }

    return [studiesData, apisData];
  };

  return (
    <StudySubjectContext.Provider
      value={{ studies, apis, studySubjectLoading }}>
        {children}
    </StudySubjectContext.Provider>
  );
}


export function useStudySubjectContext() {
  const context = useContext(StudySubjectContext);
  if (!context) {
    throw new Error("useStudySubjectContext must be used within a StudySubjectContext provider");
  }
  return context;
}
