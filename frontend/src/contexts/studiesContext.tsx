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

// TODO: Extend implementation to Ditti App Dashboard
import { createContext, useState, useEffect, PropsWithChildren, useMemo } from "react";
import { makeRequest } from "../utils";
import { StudiesContextType, Study } from "../interfaces";
import { APP_ENV } from "../environment";
import { DataFactory } from "../dataFactory";
import { useNavbar } from "../hooks/useNavbar";
import { useSearchParams } from "react-router-dom";

export const StudiesContext = createContext<StudiesContextType | undefined>(undefined);

interface IStudiesProviderProps {
  app: 2 | 3;  // Ditti App, Wearable Dashboard
}


// StudiesProvider component that wraps children with studies context.
export function StudiesProvider({
  app,
  children
}: PropsWithChildren<IStudiesProviderProps>) {
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

  // Make an sync request to get studies from the database
  const getStudiesAsync = async (): Promise<Study[]> => {
    let studies: Study[] = [];

    if (APP_ENV === "production" || APP_ENV === "development") {
      studies = await makeRequest(`/db/get-studies?app=${app}`)
        .catch(() => {
          console.error("Unable to fetch studies data. Check account permissions.")
          return [];
        });
    } else if (dataFactory) {
      studies = dataFactory.studies;
    }

    return studies;
  };

  // Fetch studies on load
  useEffect(() => {
    if (APP_ENV === "production" || APP_ENV === "development") {
      getStudiesAsync().then(studies => {
        setStudies(studies)
        const study = studies.find(s => s.id === studyId);
        if (study) {
          setStudy(study);
          setStudySlug(study.acronym);
          setSidParam(study.id.toString());
        }
        setStudiesLoading(false)
      });
    } else if (APP_ENV === "demo" && dataFactory) {
      setStudies(dataFactory.studies);
      setStudiesLoading(false);
    }
  }, [studyId]);

  return (
    <StudiesContext.Provider
      value={{ studies, studiesLoading, study }}>
        {children}
    </StudiesContext.Provider>
  );
}
