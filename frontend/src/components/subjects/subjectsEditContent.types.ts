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
