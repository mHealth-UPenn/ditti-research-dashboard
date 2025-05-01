import { ParticipantApi, ParticipantStudy } from "../types/api";

/**
 * Defines the context containing information about a study subject.
 * @property studies - The studies the study subject is enrolled information and information about their enrollment.
 * @property apis - The APIs the study subject granted access to and information about the access granted.
 * @property studySubjectLoading - Whether data is being fetched from the database.
 */
export interface StudySubjectContextValue {
  studies: ParticipantStudy[];
  apis: ParticipantApi[];
  studySubjectLoading: boolean;
  refetch: () => Promise<void>;
}
