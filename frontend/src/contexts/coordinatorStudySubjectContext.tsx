/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import {
  createContext,
  useState,
  useEffect,
  PropsWithChildren,
  useCallback,
} from "react";
import { useHttpClient } from "../lib/HttpClientContext";
import {
  CoordinatorStudySubjectContextValue,
  CoordinatorStudySubjectProviderProps,
} from "./coordinatorStudySubjectContext.types";
import { APP_ENV } from "../environment";
import { StudySubjectModel, UserModel } from "../types/models";
import { StudySubject } from "../types/api";

export const CoordinatorStudySubjectContext = createContext<
  CoordinatorStudySubjectContextValue | undefined
>(undefined);

// CoordinatorStudySubjectProvider component that wraps children with the study subject context.
export function CoordinatorStudySubjectProvider({
  app,
  children,
}: PropsWithChildren<CoordinatorStudySubjectProviderProps>) {
  const { request } = useHttpClient();
  const [studySubjects, setStudySubjects] = useState<StudySubjectModel[]>([]);
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
    studySubjects: StudySubject[],
    userDetails: UserModel[]
  ): StudySubjectModel[] => {
    const result: StudySubjectModel[] = [];

    // Get all unique Ditti IDs in the database and on AWS
    const ids = new Set([
      ...studySubjects.map((ss) => ss.dittiId),
      ...userDetails.map((u) => u.userPermissionId),
    ]);

    // Map each data entry with its Ditti ID
    const studySubjectMap = new Map(
      studySubjects.map((ss) => [ss.dittiId, ss])
    );
    const userDetailsMap = new Map(
      userDetails.map((user) => [user.userPermissionId, user])
    );

    // Create empty placeholders for when data is missing in the database or on AWS
    const emptyStudySubject: StudySubject = {
      id: -1,
      createdOn: "",
      dittiId: "",
      studies: [],
      apis: [],
    };
    const emptyUser: UserModel = {
      tapPermission: false,
      information: "",
      userPermissionId: "",
      expTime: "",
      teamEmail: "",
      createdAt: "",
    };

    // Join data on Ditti IDs
    for (const id of ids) {
      const matchedStudySubject = studySubjectMap.get(id) ?? emptyStudySubject;
      const matchedUserDetail = userDetailsMap.get(id) ?? emptyUser;

      // Build the result minus `userPermissionId`
      const dittiId =
        matchedStudySubject.dittiId === ""
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
  const fetchStudySubjectsDB = useCallback(async (): Promise<
    StudySubject[]
  > => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      const data = await request<StudySubject[]>(
        `/admin/study_subject?app=${String(app)}`
      );
      return data;
    }
    return [];
  }, [app, request]);

  // Fetch data from AWS
  const fetchStudySubjectsAWS = useCallback(async (): Promise<UserModel[]> => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      const data = await request<UserModel[]>(
        `/aws/get-users?app=${String(app)}`
      );
      return data;
    }
    return [];
  }, [app, request]);

  // Fetch and join data from AWS and the database
  const fetchStudySubjects = () => {
    setStudySubjectLoading(true);
    const promises: [Promise<StudySubject[]>, Promise<UserModel[]>] = [
      fetchStudySubjectsDB(),
      fetchStudySubjectsAWS(),
    ];

    Promise.all(promises)
      .then(([studySubjects, studySubjectsAWS]) => {
        setStudySubjects(
          joinByDittiIdAndUserPermissionId(studySubjects, studySubjectsAWS)
        );
        setStudySubjectLoading(false);
      })
      .catch((error: unknown) => {
        console.error(
          `Failed to fetch participants: ${String(
            error
          )}. Check coordinator permissions.`
        );
        setStudySubjectLoading(false);
      });
  };

  // Fetch study subjects on load
  useEffect(fetchStudySubjects, [fetchStudySubjectsAWS, fetchStudySubjectsDB]);

  /**
   * Get a study subject by Ditti ID from fetched data.
   * @param dittiId - The Ditti ID of the study subject to get.
   * @returns - The study subject with the given Ditti ID, or `undefined` if not found.
   */
  const getStudySubjectByDittiId = (
    dittiId: string
  ): StudySubjectModel | undefined => {
    return studySubjects.find((ss) => ss.dittiId === dittiId);
  };

  return (
    <CoordinatorStudySubjectContext.Provider
      value={{
        studySubjects,
        studySubjectLoading,
        getStudySubjectByDittiId,
        fetchStudySubjects,
      }}
    >
      {children}
    </CoordinatorStudySubjectContext.Provider>
  );
}
