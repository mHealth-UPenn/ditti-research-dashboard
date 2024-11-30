import { FlashMessageVariant } from "./components/flashMessage/flashMessage";

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
  role?: Role;
}

/**
 * Represents a join between a study subject and a study they are enrolled in.
 * @property study - The study the study subject is enrolled in.
 * @property didConsent - Whether the study subject consented to being enrolled in the study.
 * @property createdOn - When the study subject was enrolled in the study. Actually the date when the database entry was
 *   created.
 * @property expiresOn - When the study subject's participation in the study ends.
 */
export interface StudyJoin {
  study: Study;
  didConsent: boolean;
  createdOn: string;
  expiresOn: string;
}

/**
 * Represents a join between a study subject and an api they granted access to.
 * @property apiUserUuid - The study subject's unique ID with the API.
 * @property scope - The scope that the study subject granted with the API.
 * @property api - The API the study subject granted access to.
 * @property lastSyncDate - The last time data from this API was synced with the database.
 * @property createdOn - When the study subject granted access to the API. Actually the data when the database entry was
 *   created.
 */
export interface ApiJoin {
  apiUserUuid: string;
  scope: string[];
  api: { id: number; name: string; };
  lastSyncDate: string;
  createdOn: string;
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
  timezone: string;
}

/**
 * Represents a tap as returned from the backend.
 */
export interface Tap {
  dittiId: string;
  time: string;
  timezone: string;
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
  flashMessage: (msg: React.ReactElement, type: FlashMessageVariant) => void;
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
 * @property isIamAuthenticated - Indicates if the user is authenticated with IAM (Identity and Access Management).
 * @property isCognitoAuthenticated - Indicates if the user is authenticated with Amazon Cognito.
 * @property isIamLoading - Indicates if the IAM authentication status is being checked.
 * @property isCognitoLoading - Indicates if the Cognito authentication status is being checked.
 * @property firstLogin - Indicates if it's the user's first login.
 * @property csrfToken - The CSRF token for secure requests.
 * @property iamLogin - Function to log in the user with email and password with IAM.
 * @property iamLogout - Function to log out the user with IAM.
 * @property cognitoLogin - Function to log in the user specifically with Cognito authentication.
 * @property cognitoLogout - Function to log out the user from Cognito.
 * @property setFirstLogin - Sets whether this is the user's first login.
 */
export interface AuthContextType {
  isIamAuthenticated: boolean;
  isCognitoAuthenticated: boolean;
  isIamLoading: boolean;
  isCognitoLoading: boolean;
  firstLogin: boolean;
  csrfToken: string;
  dittiId: string | null;
  iamLogin: (email: string, password: string) => Promise<void>;
  iamLogout: () => void;
  cognitoLogin: (options?: { elevated: boolean }) => void;
  cognitoLogout: () => void;
  setFirstLogin: React.Dispatch<React.SetStateAction<boolean>>;
}


export interface StudiesContextType {
  studies: Study[];
  studiesLoading: boolean;
}


/**
 * Defines the context containing information about a study subject.
 * @property studies - The studies the study subject is enrolled information and information about their enrollment.
 * @property apis - The APIs the study subject granted access to and information about the access granted.
 * @property studySubjectLoading - Whether data is being fetched from the database.
 */
export interface StudySubjectContextType {
  studies: StudyJoin[];
  apis: ApiJoin[];
  studySubjectLoading: boolean;
}


/**
 * The study subject data structure as it is returned from the database.
 * @property id - The database primary key.
 * @property createdOn - When the database entry for the study subject was created.
 * @property dittiId - The study subject's primary key.
 * @property studies - The studies that the study subject is enrolled in and information about their enrollment.
 * @property apis - The APIs that the study subject granted access to and information about the access they granted.
 */
export interface IStudySubject {
  id: number;
  createdOn: string;
  dittiId: string;
  studies: StudyJoin[];
  apis: ApiJoin[];
}


export interface IFlashMessage {
  id: number;
  element: React.ReactElement;
  containerRef: React.RefObject<HTMLDivElement>;
  closeRef: React.RefObject<HTMLDivElement>;
}

export type ISleepLevelStages = "deep" | "light" | "rem" | "wake";
export type ISleepLevelClassic = "asleep" | "restless" | "awake";

export interface ISleepLevel {
  dateTime: Date;
  level: ISleepLevelStages | ISleepLevelClassic;
  seconds: number;
  isShort: boolean | null;
}

export interface ISleepLog {
  dateOfSleep: Date;
  startTime: Date;
  type: "stages" | "classic";
  levels: ISleepLevel[];
}

export interface IWearableDataContextType {
  sleepLogs: ISleepLog[];
  isLoading: boolean;
  error: string | null;
}

export interface IVisualizationProps {
  marginTop?: number;
  marginRight?: number;
  marginBottom?: number;
  marginLeft?: number;
}

export interface IWearableDetails {
  [key: number]: {
    numSubjects: number;
    numSubjectsWithApi: number;
  }
}
