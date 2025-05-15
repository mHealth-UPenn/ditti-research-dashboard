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
 * Defines the context containing information about the navbar.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 * @property setStudySlug - Function to set the study slug in the breadcrumbs.
 * @property setSidParam - Function to set the SID parameter in the breadcrumbs.
 * @property setDittiIdParam - Function to set the Ditti ID parameter in the breadcrumbs.
 */
export interface NavbarContextValue {
  breadcrumbs: Breadcrumb[];
  setStudySlug: (studyCrumb: string) => void;
  setSidParam: (sid: string) => void;
  setDittiIdParam: (dittiId: string) => void;
}

/**
 * Breadcrumbs for display in the Navbar component.
 * @property name - The name of the breadcrumb to display in the navbar.
 * @property link - The link to navigate to when the breadcrumb is clicked.
 */
export interface Breadcrumb {
  name: string;
  link: string | null;
}

/**
 * Handles the breadcrumbs for the Navbar component.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 */
export interface Handle {
  breadcrumbs: Breadcrumb[];
}
