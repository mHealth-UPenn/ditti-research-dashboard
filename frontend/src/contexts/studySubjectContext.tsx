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
import { httpClient } from "../lib/http";
import { APP_ENV } from "../environment";
import { StudySubjectContextValue } from "./studySubjectContext.types";
import { Participant, ParticipantApi, ParticipantStudy } from "../types/api";

export const StudySubjectContext = createContext<
  StudySubjectContextValue | undefined
>(undefined);

// StudySubjectProvider component that wraps children with the study subject context.
export function StudySubjectProvider({ children }: PropsWithChildren) {
  const [studies, setStudies] = useState<ParticipantStudy[]>([]);
  const [apis, setApis] = useState<ParticipantApi[]>([]);
  const [studySubjectLoading, setStudySubjectLoading] = useState(true);

  // Async fetch the participant's enrolled studies and connected APIs
  const getStudySubject = useCallback(async (): Promise<
    [ParticipantStudy[], ParticipantApi[]]
  > => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      try {
        const participantData =
          await httpClient.request<Participant>("/participant");
        return [participantData.studies, participantData.apis];
      } catch (error) {
        console.error("Unable to fetch participant data:", error);
        return [[], []];
      }
    }
    // Return empty arrays if not in prod/dev
    return [[], []];
  }, []);

  // Fetch the participant's enrolled studies and connected APIs on mount
  useEffect(() => {
    setStudySubjectLoading(true);
    const fetchInitialData = async () => {
      try {
        const [studiesData, apisData] = await getStudySubject();
        setStudies(studiesData);
        setApis(apisData);
      } catch (error) {
        console.error("Error setting initial participant data:", error);
      } finally {
        setStudySubjectLoading(false);
      }
    };
    void fetchInitialData();
  }, [getStudySubject]);

  // Function to refetch participant data
  const refetch = useCallback(async () => {
    setStudySubjectLoading(true);
    try {
      const [studiesData, apisData] = await getStudySubject();
      setStudies(studiesData);
      setApis(apisData);
    } catch (error: unknown) {
      console.error("Failed to refetch participant data:", error);
    } finally {
      setStudySubjectLoading(false);
    }
  }, [getStudySubject]);

  return (
    <StudySubjectContext.Provider
      value={{ studies, apis, studySubjectLoading, refetch }}
    >
      {children}
    </StudySubjectContext.Provider>
  );
}
