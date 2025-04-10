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

import { Permission, AccessGroup, Role, Study, App } from "../../types/api";

// Admin Navbar Types
export type AdminNavbarView =
  | "Accounts"
  | "Studies"
  | "Roles"
  | "Access Groups"
  | "About Sleep Templates"
  | "Data Retrieval Tasks";

/**
 * @property {string} activeView - The name of the active view
 */
export interface AdminNavbarProps {
  activeView: AdminNavbarView;
}

// About Sleep Templates Edit Types
/**
 * The form's prefill
 * @property {string} name - The name of the template
 * @property {string} text - The text of the template
 */
export interface AboutSleepTemplateFormPrefill {
  name: string;
  text: string;
}

// Roles Edit Types
/**
 * The form's prefill
 * @property {string} name - The name of the role
 * @property {Permission[]} permissions - The permissions of the role
 */
export interface RolesFormPrefill {
  name: string;
  permissions: Permission[];
}

// Accounts Edit Types
/**
 * A role selected for a study
 * @property {number} study - The database primary key of the study
 * @property {number} role - The database primary key of the role
 */
export interface RoleSelected {
  study: number;
  role: number;
}

/**
 * The form's prefill
 * @property {string} email - The email of the account
 * @property {string} firstName - The first name of the account
 * @property {string} lastName - The last name of the account
 * @property {string} phoneNumber - The phone number of the account
 * @property {AccessGroup[]} accessGroupsSelected - The access groups selected for the account
 * @property {RoleSelected[]} rolesSelected - The roles selected for the account
 * @property {Study[]} studiesSelected - The studies selected for the account
 */
export interface AccountFormPrefill {
  email: string;
  firstName: string;
  lastName: string;
  phoneNumber?: string;
  accessGroupsSelected: AccessGroup[];
  rolesSelected: RoleSelected[];
  studiesSelected: Study[];
}

/**
 * The state of the accounts edit page
 * @property {AccessGroup[]} accessGroups - All available access groups for selection
 * @property {Role[]} roles - All available roles for selection
 * @property {Study[]} studies - All available studies for selection
 * @property {boolean} loading - Whether to show the loader
 */
export interface AccountsEditState extends AccountFormPrefill {
  accessGroups: AccessGroup[];
  roles: Role[];
  studies: Study[];
  loading: boolean;
}

// Access Groups Edit Types
/**
 * The form's prefill
 * @property {string} name - The name of the access group
 * @property {App} appSelected - The app selected for the access group
 * @property {Permission[]} permissions - The permissions for the access group
 */
export interface AccessGroupFormPrefill {
  name: string;
  appSelected: App;
  permissions: Permission[];
}
