/**
 * Represents an account with user details and permissions.
 * @property id - The database primary key.
 * @property createdOn - The timestamp when the account was created.
 * @property lastLogin - The timestamp when the account was last logged in.
 * @property firstName - The account holder's first name.
 * @property lastName - The account holder's last name.
 * @property email - The account holder's email.
 * @property phoneNumber - The account holder's phone number.
 * @property isConfirmed - Whether the account has been logged in and the account holder has set their password.
 * @property accessGroups - The access groups the account has access to.
 * @property studies - The studies the account has access to.
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
 * Represents an application with an identifier and name.
 * @property id - The database primary key.
 * @property name - The name of the app.
 */
export interface App {
  id: number;
  name: string;
}

/**
 * Represents an access group with permissions for a specific app.
 * @property id - The database primary key.
 * @property name - The name of the access group.
 * @property app - The app the access group provides permissions for.
 * @property permissions - The permissions that the access group grants.
 */
export interface AccessGroup {
  id: number;
  name: string;
  app: App;
  permissions: Permission[];
}

/**
 * Represents a specific permission on a resource.
 * @property id - The database primary key.
 * @property action - The action the permission allows.
 * @property resource - The resource the permission allows the action to be performed on.
 */
export interface Permission {
  id: number;
  action: string;
  resource: string;
}

/**
 * Represents a role with permissions assigned.
 * @property id - The database primary key.
 * @property name - The name of the role.
 * @property permissions - The permissions that the role grants.
 */
export interface Role {
  id: number;
  name: string;
  permissions: Permission[];
}

/**
 * Represents a study with associated details.
 * @property id - The database primary key.
 * @property name - The name of the study.
 * @property acronym - The study's acronym.
 * @property dittiId - The study's ditti ID.
 * @property email - The study's team email.
 * @property role - The role the user is assigned to for the study.
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
 * Represents a sleep template with descriptive content.
 * @property id - The database primary key.
 * @property name - The name of the sleep template.
 * @property text - The content of the sleep template.
 */
export interface AboutSleepTemplate {
  id: number;
  name: string;
  text: string;
}

/**
 * Represents an action or resource identifier.
 * @property id - The database primary key.
 * @property value - The string value of the action or resource.
 */
export interface ActionResource {
  id: number;
  value: string;
}

/**
 * Default response structure from application endpoints.
 * @property msg - A message returned from the endpoint.
 * @property csrfAccessToken - The active CSRF token.
 * @property jwt - Optional JWT token.
 */
export interface ResponseBody {
  msg: string;
  csrfAccessToken: string;
  jwt?: string;
}

/**
 * Ditti user data used in the frontend.
 * @property tapPermission - Indicates if the user has access to taps.
 * @property information - Content from the assigned about sleep template.
 * @property userPermissionId - The user's ditti ID.
 * @property expTime - Expiration time of the user's ID.
 * @property teamEmail - The team email assigned to this user.
 * @property createdAt - When the user was created.
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
 * User data as returned from the backend.
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
 * Represents a tap with details specific to frontend use.
 * @property dittiId - The ditti ID of the user who created the tap.
 * @property time - The tap's timestamp.
 */
export interface TapDetails {
  dittiId: string;
  time: Date;
}

/**
 * Represents a tap as returned from the backend.
 */
export interface Tap {
  dittiId: string;
  time: string;
}

/**
 * Represents an audio tap with details specific to frontend use.
 * @property dittiId - The ditti ID of the user who created the audio tap.
 * @property audioFileTitle - The title of the audio file.
 * @property time - The timestamp of the audio tap.
 * @property timezone - The timezone associated with the audio tap.
 * @property action - The action recorded with the audio tap.
 */
export interface AudioTapDetails {
  dittiId: string;
  audioFileTitle: string;
  time: Date;
  timezone: string;
  action: string;
}

/**
 * Represents an audio tap as returned from the backend.
 */
export interface AudioTap {
  dittiId: string;
  audioFileTitle: string;
  time: string;
  timezone: string;
  action: string;
}

/**
 * Default props structure for all dashboard views.
 * @property flashMessage - Function to flash messages on the page.
 * @property goBack - Function to handle navigation back.
 * @property handleClick - Function to handle navigation link clicks.
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
 * Account data as used by the dashboard header.
 * @property firstName - The account holder's first name.
 * @property lastName - The account holder's last name.
 * @property email - The account holder's email.
 * @property phoneNumber - The account holder's phone number.
 */
export interface AccountDetails {
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber: string;
}

/**
 * Represents an audio file as stored in DynamoDB.
 * @property id - Optional unique ID for the audio file.
 * @property fileName - Filename on S3.
 * @property title - Title as displayed in the Ditti App.
 * @property category - Type/category of the audio (e.g., nature, music).
 * @property availability - Either "all" or specific User ID for availability.
 * @property studies - List of studies the audio file is available for, empty if available for all.
 * @property length - Length of the audio file in seconds.
 */
export interface AudioFile {
  id?: string;
  _version?: number;
  fileName?: string;
  title?: string;
  category?: string;
  availability?: string;
  studies?: string[];
  length?: number;
}

/**
 * Defines the authentication context structure.
 * @property isAuthenticated - Indicates if the user is authenticated.
 * @property isLoading - Indicates if authentication status is being checked.
 * @property firstLogin - Indicates if it's the user's first login.
 * @property csrfToken - The CSRF token for secure requests.
 * @property login - Function to log in the user.
 * @property logout - Function to log out the user.
 * @property setFirstLogin - Sets whether this is the user's first login.
 * @property setCsrfToken - Sets the CSRF token.
 */
export interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  firstLogin: boolean;
  csrfToken: string;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setFirstLogin: (value: boolean) => void;
  setCsrfToken: (token: string) => void;
}
