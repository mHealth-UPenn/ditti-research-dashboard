// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { StudySubjectContextType, IParticipant, IParticipantApi, IParticipantStudy } from "../interfaces";
import { APP_ENV } from "../environment";
import { DataFactory } from "../dataFactory";

export const StudySubjectContext = createContext<StudySubjectContextType | undefined>(undefined);


// StudySubjectProvider component that wraps children with the study subject context.
export function StudySubjectProvider({
  children
}: PropsWithChildren<unknown>) {
  const [studies, setStudies] = useState<IParticipantStudy[]>([]);
  const [apis, setApis] = useState<IParticipantApi[]>([])
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      // return new DataFactory();
      return null;  // Until this data is available in the data factory
    }
    return null;
  }, []);

  // Fetch the participant's enrolled studies and connected APIs
  useEffect(() => {
    const promises: Promise<any>[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      promises.push(getStudySubject().then(([studiesData, apisData]) => {
        setStudies(studiesData);
        setApis(apisData);
      }));
    // } else if (APP_ENV === "demo" && dataFactory) {
    //   setStudies(dataFactory.studyJoins);
    //   setApis(dataFactory.apiJoins);
    }

    Promise.all(promises).then(() => setStudySubjectLoading(false));
  }, []);

  // Async fetch the participant's enrolled studies and connected APIs
  const getStudySubject = async (): Promise<[IParticipantStudy[], IParticipantApi[]]> => {
    let studiesData: IParticipantStudy[] = [];
    let apisData: IParticipantApi[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      await makeRequest(`/participant`)
        .then((res: IParticipant) => {
          studiesData = res.studies;
          apisData = res.apis;
        })
        .catch(() => {
          console.error("Unable to fetch participant data.")
        });
    // } else if (dataFactory) {
    //   studies = dataFactory.studies;
    }

    return [studiesData, apisData];
  };

  // Function to refetch participant data
  const refetch = async () => {
    setStudySubjectLoading(true);
    try {
      const [studiesData, apisData] = await getStudySubject();
      setStudies(studiesData);
      setApis(apisData);
    } catch (error) {
      console.error("Failed to refetch participant data:", error);
    } finally {
      setStudySubjectLoading(false);
    }
  };

  return (
    <StudySubjectContext.Provider
      value={{ studies, apis, studySubjectLoading, refetch }}>
        {children}
    </StudySubjectContext.Provider>
  );
}


// Hook for accessing context data
export function useStudySubjectContext() {
  const context = useContext(StudySubjectContext);
  if (!context) {
    throw new Error("useStudySubjectContext must be used within a StudySubjectContext provider");
  }
  return context;
}
