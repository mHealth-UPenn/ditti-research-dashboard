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
export type WearableStudyDetails = Record<
  number,
  {
    numSubjects: number;
    numSubjectsWithApi: number;
  }
>;
