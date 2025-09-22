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
import { useHttpClient } from "../hooks/useHttpClient";
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

  // Make an sync request to get studies from the database
  const getStudiesAsync = useCallback(async (): Promise<Study[]> => {
    return await request<Study[]>(`/db/get-studies?app=${String(app)}`);
  }, [app, request]);

  // Fetch studies on load
  useEffect(() => {
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
  }, [studyId, getStudiesAsync, setSidParam, setStudySlug]);

  return (
    <StudiesContext.Provider value={{ studies, studiesLoading, study }}>
      {children}
    </StudiesContext.Provider>
  );
}
