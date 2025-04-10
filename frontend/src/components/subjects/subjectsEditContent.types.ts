/**
 * Study subject data used for the SubjectsEdit form
 * @property tapPermission - Indicates if the participant has access to taps.
 * @property information - Content from the assigned about sleep template.
 * @property dittiId - The participant's Ditti ID
 * @property startTime - When the participant's enrollment in the study begins
 * @property expTime - When the participant's enrollment in the study begins
 */
export interface StudySubjectFormPrefill {
  tapPermission: boolean;
  information: string;
  dittiId: string;
  startTime: string;
  expTime: string;
}
