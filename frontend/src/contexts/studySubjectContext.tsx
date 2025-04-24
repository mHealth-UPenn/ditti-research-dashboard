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
import { createContext, useState, useEffect, PropsWithChildren } from "react";
import { makeRequest } from "../utils";
import { APP_ENV } from "../environment";
import { StudySubjectContextValue } from "./studySubjectContext.types";
import { Participant, ParticipantApi, ParticipantStudy } from "../types/api";

export const StudySubjectContext = createContext<
  StudySubjectContextValue | undefined
>(undefined);

// StudySubjectProvider component that wraps children with the study subject context.
export function StudySubjectProvider({ children }: PropsWithChildren<unknown>) {
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

    Promise.all(promises).then(() => setStudySubjectLoading(false));
  }, []);

  // Async fetch the participant's enrolled studies and connected APIs
  const getStudySubject = async (): Promise<
    [ParticipantStudy[], ParticipantApi[]]
  > => {
    let studiesData: ParticipantStudy[] = [];
    let apisData: ParticipantApi[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      await makeRequest(`/participant`)
        .then((res: Participant) => {
          studiesData = res.studies;
          apisData = res.apis;
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
    } catch (error) {
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
