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
  app: 2 | 3;  // Cannot be accessed from admin dashboard (`1`)
}
