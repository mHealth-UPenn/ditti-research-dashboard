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
    throw new Error(
      "useStudySubjects must be used within a StudySubjectContext provider"
    );
  }
  return context;
}
