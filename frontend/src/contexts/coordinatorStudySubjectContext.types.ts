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

import { StudySubjectModel } from "../types/models";

/**
 * Defines the context containing information about a coordinator's study subjects.
 * @property studySubjects - The study subjects and information about their study enrollments.
 * @property studySubjectLoading - Whether data is being fetched from the database.
 * @property getStudySubjectByDittiId - Function to get a study subject by their Ditti ID.
 * @property fetchStudySubjects - Function to fetch study subjects from the database. This is useful for refreshing
 *  data after enrolling or updating a study subject.
 */
export interface CoordinatorStudySubjectContextValue {
  studySubjects: StudySubjectModel[];
  studySubjectLoading: boolean;
  getStudySubjectByDittiId: (id: string) => StudySubjectModel | undefined;
  fetchStudySubjects: () => void;
}

/**
 * Props for the CoordinatorStudySubjectProvider component.
 * @property app - The app ID of the coordinator.
 */
export interface CoordinatorStudySubjectProviderProps {
  app: 2 | 3; // Cannot be accessed from admin dashboard (`1`)
}
