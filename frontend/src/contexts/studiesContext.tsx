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
  useMemo,
  useCallback,
} from "react";
import { useHttpClient } from "../lib/HttpClientContext";
import { APP_ENV } from "../environment";
import { DataFactory } from "../dataFactory";
import { useNavbar } from "../hooks/useNavbar";
import { useSearchParams } from "react-router-dom";
import {
  StudiesContextValue,
  StudiesProviderProps,
} from "./studiesContext.types";
import { Study } from "../types/api";

export const StudiesContext = createContext<StudiesContextValue | undefined>(
  undefined
);

// StudiesProvider component that wraps children with studies context.
export function StudiesProvider({
  app,
  children,
}: PropsWithChildren<StudiesProviderProps>) {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;

  const [studies, setStudies] = useState<Study[]>([]);
  const [study, setStudy] = useState<Study | null>(null);
  const [studiesLoading, setStudiesLoading] = useState(true);
  const { setStudySlug, setSidParam } = useNavbar();

  const { request } = useHttpClient();

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  // Make an sync request to get studies from the database
  const getStudiesAsync = useCallback(async (): Promise<Study[]> => {
    let studies: Study[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      // Explicitly cast the response type and convert app to string
      try {
        studies = await request<Study[]>(`/db/get-studies?app=${String(app)}`);
      } catch {
        console.error(
          "Unable to fetch studies data. Check account permissions."
        );
        return [] as Study[]; // Return empty array on error
      }
    } else if (dataFactory) {
      studies = dataFactory.studies;
    }

    return studies;
  }, [app, dataFactory, request]);

  // Fetch studies on load
  useEffect(() => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      getStudiesAsync()
        .then((studies) => {
          setStudies(studies);
          const study = studies.find((s) => s.id === studyId);
          if (study) {
            setStudy(study);
            setStudySlug(study.acronym);
            setSidParam(study.id.toString());
          }
          setStudiesLoading(false);
        })
        .catch((error: unknown) => {
          console.error("Error fetching studies:", error);
          setStudiesLoading(false); // Ensure loading is false on error
        });
    } else if (APP_ENV === "demo" && dataFactory) {
      setStudies(dataFactory.studies);
      setStudiesLoading(false);
    }
  }, [studyId, dataFactory, getStudiesAsync, setSidParam, setStudySlug]);

  return (
    <StudiesContext.Provider value={{ studies, studiesLoading, study }}>
      {children}
    </StudiesContext.Provider>
  );
}
