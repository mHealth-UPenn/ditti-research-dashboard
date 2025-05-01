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
