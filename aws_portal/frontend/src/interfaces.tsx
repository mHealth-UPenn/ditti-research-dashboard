/**
 * id: the database primary key
 * createdOn: the timestamp when the account was created
 * lastLogin: the timestamp when the account was last logged in
 * firstName: the account holder's first name
 * lastName: the account holder's last name
 * email: the account holder's email
 * phoneNumber: the account holder's phone number
 * isConfirmed: whether the account has been logged in and the account holder has set their password
 * accessGroups: the access groups the account has access to
 * studies: the studies the account has access to
 */
export interface Account {
  id: number;
  createdOn: string;
  lastLogin: string;
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
  isConfirmed: boolean;
  accessGroups: AccessGroup[];
  studies: Study[];
}

/**
 * id: the database primary key
 * name: the name of the app
 */
export interface App {
  id: number;
  name: string;
}

/**
 * id: the database primary key
 * name: the name of the access group
 * app: the app the access group provides permissions for
 * permissions: the permissions that the access group grants
 */
export interface AccessGroup {
  id: number;
  name: string;
  app: App;
  permissions: Permission[];
}

/**
 * id: the database primary key
 * action: the action the permission allows
 * resource: the resource the permission allows the action to be performed on
 */
export interface Permission {
  id: number;
  action: string;
  resource: string;
}

/**
 * id: the database primary key
 * name: the name of the role
 * permissions: the permissions that the role grants
 */
export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

/**
 * id: the database primary key
 * name: the name of the study
 * acronym: the study's acronym
 * dittiId: the study's ditti ID
 * email: the study's team email
 * role: the role the user is assigned to for the study
 */
export interface Study {
  id: number;
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
  role: Role;
}

/**
 * id: the database primary key
 * name: the name of the sleep template
 * text: the content of the sleep template
 */
export interface AboutSleepTemplate {
  id: number;
  name: string;
  text: string;
}

/**
 * id: the database primary key
 * value: the string value of the action or resource
 */
export interface ActionResource {
  id: number;
  value: string;
}

/**
 * The default response from app endpoints
 * msg: a message returned from the endpoint
 * csrfAccessToken: the active CSRF token
 */
export interface ResponseBody {
  msg: string;
  csrfAccessToken: string;
  jwt?: string;
}

/**
 * Ditti user data as it is used in the frontend
 * tapPermission: whether the user has access to taps
 * information: the content of the about sleep template assigned to this user
 * userPermissionId: the user's ditti ID
 * expTime: when the user's ID expires
 * teamEmail: the team email assigned to this user
 * createdAt: when the user was created
 */
export interface UserDetails {
  tapPermission: boolean;
  information: string;
  userPermissionId: string;
  expTime: string;
  teamEmail: string;
  createdAt: string;
}

/**
 * User data as it is returned from the backend
 */
export interface User {
  tap_permission: boolean;
  information: string;
  user_permission_id: string;
  exp_time: string;
  team_email: string;
  createdAt: string;
  __typename: string;
  _lastChangedAt: number;
  _version: number;
  updatedAt: string;
  id: string;
}

/**
 * Tap data as it is used on the frontend
 * dittiId: The ditti ID of the user who created the tap
 * time: The tap's timestamp
 */
export interface TapDetails {
  dittiId: string;
  time: Date;
}

/**
 * Tap data as it is returned from the backend
 */
export interface Tap {
  dittiId: string;
  time: string;
}

/**
 * The default props for all dashboard views
 * flashMessage: any messages to flash on the page
 * goBack: a function to handle when the user clicks back on the nav bar
 * handleClick: a function to handle when the user clicks a nav link on the nav bar
 */
export interface ViewProps {
  flashMessage: (msg: React.ReactElement, type: string) => void;
  goBack: () => void;
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace?: boolean
  ) => void;
}

/**
 * An account's data as it is used by the dashboard header
 * firstName: the account holder's first name
 * lastName: the account holder's last name
 * email: the account holder's email
 * phoneNumber: the account hodler's phone number
 */
export interface AccountDetails {
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
}
