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
import { httpClient } from "../lib/http";
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

  const dataFactory: DataFactory | null = useMemo(() => {
    if (APP_ENV === "development" || APP_ENV === "demo") {
      return new DataFactory();
    }
    return null;
  }, []);

  // Make an async request to get studies from the database
  const getStudiesAsync = useCallback(async (): Promise<Study[]> => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      try {
        // Specify the expected type and use await directly
        const studies = await httpClient.request<Study[]>(
          `/db/get-studies?app=${String(app)}`
        );
        return studies;
      } catch (error) {
        console.error(
          "Unable to fetch studies data. Check account permissions.",
          error // Log the actual error
        );
        return []; // Return empty array on error, matches previous behavior
      }
    } else if (dataFactory) {
      // Assuming dataFactory is already initialized or handles its own errors
      return dataFactory.studies;
    }
    // Default return if no condition met
    return [];
  }, [app, dataFactory]);

  // Fetch studies on load
  useEffect(() => {
    setStudiesLoading(true);
    const fetchAndSetStudies = async () => {
      try {
        const studiesData = await getStudiesAsync();
        setStudies(studiesData);
        const currentStudy = studiesData.find((s) => s.id === studyId);
        if (currentStudy) {
          setStudy(currentStudy);
          setStudySlug(currentStudy.acronym);
          setSidParam(currentStudy.id.toString());
        } else {
          // Handle case where the studyId from URL doesn't match any fetched study
          setStudy(null);
          setStudySlug(""); // Or some default/error state
          // setSidParam(""); // Optionally clear sid param if invalid
        }
      } catch (error) {
        // Catch errors from getStudiesAsync if it were to re-throw
        console.error("Error setting studies state:", error);
        setStudy(null); // Ensure study state is cleared on error
        setStudySlug("");
      } finally {
        setStudiesLoading(false);
      }
    };

    void fetchAndSetStudies();
  }, [studyId, getStudiesAsync, setSidParam, setStudySlug]); // Dependencies updated

  return (
    <StudiesContext.Provider value={{ studies, studiesLoading, study }}>
      {children}
    </StudiesContext.Provider>
  );
}
