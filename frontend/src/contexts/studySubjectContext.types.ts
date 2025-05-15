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
