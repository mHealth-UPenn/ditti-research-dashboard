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

import { Study } from "../types/api";

/**
 * Defines the context containing information about studies.
 * @property studies - The studies fetched from the database.
 * @property studiesLoading - Whether data is being fetched from the database.
 * @property study - The study currently being viewed.
 */
export interface StudiesContextValue {
  studies: Study[];
  studiesLoading: boolean;
  study: Study | null;
}

/**
 * Props for the StudiesProvider component.
 * @property app - The app ID of the studies.
 */
export interface StudiesProviderProps {
  app: 2 | 3; // Ditti App, Wearable Dashboard
}
