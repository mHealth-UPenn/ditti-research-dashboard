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

import { createContext, useState, useEffect, PropsWithChildren } from "react";
import { makeRequest } from "../utils";
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

  // Fetch the participant's enrolled studies and connected APIs
  useEffect(() => {
    const promises: Promise<void>[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      promises.push(
        getStudySubject().then(([studiesData, apisData]) => {
          setStudies(studiesData);
          setApis(apisData);
        })
      );
    }

    Promise.all(promises)
      .then(() => {
        setStudySubjectLoading(false);
      })
      .catch((error: unknown) => {
        console.error("Error fetching initial study subject data:", error);
        setStudySubjectLoading(false);
      });
  }, []);

  // Async fetch the participant's enrolled studies and connected APIs
  const getStudySubject = async (): Promise<
    [ParticipantStudy[], ParticipantApi[]]
  > => {
    let studiesData: ParticipantStudy[] = [];
    let apisData: ParticipantApi[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      await makeRequest(`/participant`)
        .then((res) => {
          // Explicitly cast the response type
          const participantData = res as unknown as Participant;
          studiesData = participantData.studies;
          apisData = participantData.apis;
        })
        .catch(() => {
          console.error("Unable to fetch participant data.");
        });
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
    } catch (error: unknown) {
      console.error("Failed to refetch participant data:", error);
    } finally {
      setStudySubjectLoading(false);
    }
  };

  return (
    <StudySubjectContext.Provider
      value={{ studies, apis, studySubjectLoading, refetch }}
    >
      {children}
    </StudySubjectContext.Provider>
  );
}
