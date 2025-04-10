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
