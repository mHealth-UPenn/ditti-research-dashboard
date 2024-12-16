// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { IStudySubject, CoordinatorStudySubjectContextType } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";

export const CoordinatorStudySubjectContext = createContext<CoordinatorStudySubjectContextType | undefined>(undefined);


/**
 * CoordinatorStudySubjectProvider component that wraps children with the study subject context.
 */
export default function CoordinatorStudySubjectProvider({
  children
}: PropsWithChildren<unknown>) {
  const [studySubjects, setStudySubjects] = useState<IStudySubject[]>([]);
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      // return new DataFactory();
      return null;  // Until this data is available in the data factory
    }
    return null;
  }, []);

  useEffect(() => {
    const fetchStudySubjects = async () => {
      if (APP_ENV === "production" || APP_ENV === "development") {
        const data: IStudySubject[] = await makeRequest("/admin/study_subject?app=3");
        setStudySubjects(data);
      }
    };

    const promises: Promise<any>[] = [];
    promises.push(fetchStudySubjects());
    Promise.all(promises).then(() => setStudySubjectLoading(false));
  }, []);

  return (
    <CoordinatorStudySubjectContext.Provider
      value={{ studySubjects, studySubjectLoading }}>
        {children}
    </CoordinatorStudySubjectContext.Provider>
  );
}


export function useCoordinatorStudySubjectContext() {
  const context = useContext(CoordinatorStudySubjectContext);
  if (!context) {
    throw new Error("useCoordinatorStudySubjectContext must be used within a CoordinatorStudySubjectContext provider");
  }
  return context;
}
