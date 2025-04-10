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
