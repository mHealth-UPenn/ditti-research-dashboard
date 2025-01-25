import { createContext, useState, useEffect, PropsWithChildren, useMemo, useContext } from "react";
import { makeRequest } from "../utils";
import { IStudySubject, CoordinatorStudySubjectContextType, UserDetails, IStudySubjectDetails } from "../interfaces";
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";

export const CoordinatorStudySubjectContext = createContext<CoordinatorStudySubjectContextType | undefined>(undefined);

interface ICoordinatorStudySubjectProviderProps {
  app: 2 | 3;  // Cannot be accessed from admin dashboard (`1`)
}


// CoordinatorStudySubjectProvider component that wraps children with the study subject context.
export default function CoordinatorStudySubjectProvider({
  app,
  children
}: PropsWithChildren<ICoordinatorStudySubjectProviderProps>) {
  const [studySubjects, setStudySubjects] = useState<IStudySubjectDetails[]>([]);
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      // return new DataFactory();
      return null;  // Until this data is available in the data factory
    }
    return null;
  }, []);

  /**
   * Joins participant data fetched from the database and from AWS by Ditti ID. If a Ditti ID exists in only one data
   * source, then an empty placeholder is filled in for the other. `UserDetails.userPermissionId` is removed from the
   * joined data in favor of `dittiId`.
   * @param studySubjects - Participant data fetched from the database.
   * @param userDetails - Participant data fetched from AWS.
   * @returns - Merged participant data.
   */
  const joinByDittiIdAndUserPermissionId = (
    studySubjects: IStudySubject[],
    userDetails: UserDetails[]
  ): IStudySubjectDetails[] => {
    const result: IStudySubjectDetails[] = [];

    // Get all unique Ditti IDs in the database and on AWS
    const ids = new Set([
      ...studySubjects.map(ss => ss.dittiId),
      ...userDetails.map(u => u.userPermissionId)
    ]);

    // Map each data entry with its Ditti ID
    const studySubjectMap = new Map(studySubjects.map(ss => [ss.dittiId, ss]));
    const userDetailsMap = new Map(
      userDetails.map(user => [user.userPermissionId, user])
    );

    // Create empty placeholders for when data is missing in the database or on AWS
    const emptyStudySubject: IStudySubject = {
      id: -1,
      createdOn: "",
      dittiId: "",
      studies: [],
      apis: [],
    }
    const emptyUser: UserDetails = {
      tapPermission: false,
      information: "",
      userPermissionId: "",
      expTime: "",
      teamEmail: "",
      createdAt: "",
    }

    // Join data on Ditti IDs
    for (const id of ids) {
      const matchedStudySubject = studySubjectMap.get(id) || emptyStudySubject;
      const matchedUserDetail = userDetailsMap.get(id) || emptyUser;

      // Build the result minus `userPermissionId`
      const dittiId = matchedStudySubject.dittiId === ""
        ? matchedUserDetail.userPermissionId
        : matchedStudySubject.dittiId;

      const res = {
        id: matchedStudySubject.id,
        createdOn: matchedStudySubject.createdOn,
        dittiId: dittiId,
        studies: matchedStudySubject.studies,
        apis: matchedStudySubject.apis,
        tapPermission: matchedUserDetail.tapPermission,
        information: matchedUserDetail.information,
        dittiExpTime: matchedUserDetail.expTime,
        teamEmail: matchedUserDetail.teamEmail,
        createdAt: matchedUserDetail.createdAt,
      };
      result.push(res);
    }

    return result;
  };

  // Fetch data from the database
  const fetchStudySubjectsDB = async (): Promise<IStudySubject[]> => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      const data: IStudySubject[] = await makeRequest(`/admin/study_subject?app=${app}`);
      return data;
    }
    return [];
  };

  // Fetch data from AWS
  const fetchStudySubjectsAWS = async (): Promise<UserDetails[]> => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      const data: UserDetails[] = await makeRequest(`/aws/get-users?app=${app}`);
      return data;
    }
    return [];
  };

  // Fetch and join data from AWS and the database
  const fetchStudySubjects = () => {
    setStudySubjectLoading(true);
    const promises: [Promise<IStudySubject[]>, Promise<UserDetails[]>] = [
      fetchStudySubjectsDB(),
      fetchStudySubjectsAWS(),
    ];

    Promise.all(promises).then(([studySubjects, studySubjectsAWS]) => {
      setStudySubjects(joinByDittiIdAndUserPermissionId(studySubjects, studySubjectsAWS));
      setStudySubjectLoading(false);
    })
    .catch(error => {
      console.error(`Failed to fetch participants: ${error}. Check coordinator permissions.`)
      setStudySubjectLoading(false);
    });
  }

  // Fetch study subjects on load
  useEffect(fetchStudySubjects, []);

  /**
   * Get a study subject by Ditti ID from fetched data.
   * @param dittiId - The Ditti ID of the study subject to get.
   * @returns - The study subject with the given Ditti ID, or `undefined` if not found.
   */
  const getStudySubjectByDittiId = (dittiId: string): IStudySubjectDetails | undefined => {
    return studySubjects.find(ss => ss.dittiId === dittiId);
  }

  return (
    <CoordinatorStudySubjectContext.Provider
      value={{
          studySubjects,
          studySubjectLoading,
          getStudySubjectByDittiId,
          fetchStudySubjects
        }}>
          {children}
    </CoordinatorStudySubjectContext.Provider>
  );
}


// Hook for retrieving context data
export function useCoordinatorStudySubjectContext() {
  const context = useContext(CoordinatorStudySubjectContext);
  if (!context) {
    throw new Error("useCoordinatorStudySubjectContext must be used within a CoordinatorStudySubjectContext provider");
  }
  return context;
}
