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
import { Study } from "../../types/api";

/**
 * Props for the wearable visuals content.
 * @property dittiId: The Ditti ID of the participant whose data is being visualized.
 */
export interface WearableVisualsContentProps {
  dittiId: string;
}

/**
 * Props for wearable study subjects.
 * @property studyDetails: The details of study to list subjects for.
 * @property canViewWearableData: Whether the current user can view wearable data for the current study.
 */
export interface WearableStudySubjectsProps {
  studyDetails: Study;
  canViewWearableData: boolean;
}

/**
 * Interface for details of each study to display.
 * @key number: The study ID.
 * @property numSubjects: The number of subjects enrolled in the study.
 * @property numSubjectsWithApi: The number of subjects who are enrolled in the study and who have connected any API.
 */
export type WearableStudyDetails = Record<number, {
    numSubjects: number;
    numSubjectsWithApi: number;
  }>;
