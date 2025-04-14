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

import { useContext } from "react";
import { StudySubjectContext } from "../contexts/studySubjectContext";
import { StudySubjectContextValue } from "../contexts/studySubjectContext.types";

/**
 * Hook for accessing context data
 * @returns The current study subjects context.
 */
export function useStudySubjects(): StudySubjectContextValue {
  const context = useContext(StudySubjectContext);
  if (!context) {
    throw new Error("useStudySubjects must be used within a StudySubjectContext provider");
  }
  return context;
}
