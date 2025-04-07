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

import { createContext, useState, useEffect, PropsWithChildren, useContext } from "react";
import { makeRequest } from "../utils";
import { IStudySubject, CoordinatorStudySubjectContextType, UserDetails, IStudySubjectDetails } from "../interfaces";
import { APP_ENV } from "../environment";

export const CoordinatorStudySubjectContext = createContext<CoordinatorStudySubjectContextType | undefined>(undefined);

interface ICoordinatorStudySubjectProviderProps {
  app: 2 | 3;  // Cannot be accessed from admin dashboard (`1`)
}


// CoordinatorStudySubjectProvider component that wraps children with the study subject context.
export function CoordinatorStudySubjectProvider({
  app,
  children
}: PropsWithChildren<ICoordinatorStudySubjectProviderProps>) {
  const [studySubjects, setStudySubjects] = useState<IStudySubjectDetails[]>([]);
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

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
