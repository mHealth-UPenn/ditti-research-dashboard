/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { FlashMessageVariant } from "./components/flashMessage/flashMessage";
import { QuillOptions } from "quill";

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
 * @property defaultExpiryDelta - The default number of days that a subject is enrolled in the study.
 * @property consentInformation - The consent text shown to a study subject.
 * @property dataSummary - Text describing why participant data is collected.
 * @property isQi - Indicates if the study is QI (Quality Improvement).
 */
export interface Study {
  id: number;
  name: string;
  acronym: string;
  dittiId: string;
  email: string;
  role?: Role;
  defaultExpiryDelta: number;
  consentInformation?: string;
  dataSummary?: string;
  isQi: boolean;
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
  startsOn: string;
  expiresOn: string;
  dataSummary: string;
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
  csrfAccessToken?: string;
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
 * Study subject data used for the SubjectsEdit form
 * @property tapPermission - Indicates if the participant has access to taps.
 * @property information - Content from the assigned about sleep template.
 * @property dittiId - The participant's Ditti ID
 * @property startTime - When the participant's enrollment in the study begins
 * @property expTime - When the participant's enrollment in the study begins
 */
export interface StudySubjectPrefill {
  tapPermission: boolean;
  information: string;
  dittiId: string;
  startTime: string;
  expTime: string;
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

export interface ConsentModalProps {
  isOpen: boolean;
  onAccept: () => void;
  onDeny: () => void;
  onClose: () => void;
  contentHtml: string;
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
 * Represents a data retrieval task mapped from the `lambda_task` database table.
 *
 * @property id - The primary key of the task.
 * @property status - The current status of the task ("Pending", "InProgress", "Success", "Failed", "CompletedWithErrors").
 * @property billedMs - The billed duration of the Lambda function in milliseconds.
 * @property createdOn - The ISO 8601 timestamp indicating when the task was created.
 * @property updatedOn - The ISO 8601 timestamp indicating when the task was last updated.
 * @property completedOn - The ISO 8601 timestamp indicating when the task was completed, or null if not completed.
 * @property logFile - The S3 URI of the task's log file, or null if not available.
 * @property errorCode - The error code associated with the task, or null if no error occurred.
 */
export interface DataRetrievalTask {
  id: number;
  status: "Pending" | "InProgress" | "Success" | "Failed" | "CompletedWithErrors";
  billedMs: number | null;
  createdOn: string;
  updatedOn: string;
  completedOn: string | null;
  logFile: string | null;
  errorCode: string | null;
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


/**
 * Defines the context containing information about studies.
 * @property studies - The studies fetched from the database.
 * @property studiesLoading - Whether data is being fetched from the database.
 */
export interface StudiesContextType {
  studies: Study[];
  studiesLoading: boolean;
  study: Study | null;
}


/**
 * Defines the context containing information about a study subject.
 * @property studies - The studies the study subject is enrolled information and information about their enrollment.
 * @property apis - The APIs the study subject granted access to and information about the access granted.
 * @property studySubjectLoading - Whether data is being fetched from the database.
 */
export interface StudySubjectContextType {
  studies: IParticipantStudy[];
  apis: IParticipantApi[];
  studySubjectLoading: boolean;
  refetch: () => Promise<void>;
}


/**
 * Defines the context containing information about a coordinator's study subjects.
 * @property studySubjects - The study subjects and information about their study enrollments.
 * @property studySubjectLoading - Whether data is being fetched from the database.
 * @property getStudySubjectByDittiId - Function to get a study subject by their Ditti ID.
 * @property fetchStudySubjects - Function to fetch study subjects from the database. This is useful for refreshing
 *  data after enrolling or updating a study subject.
 */
export interface CoordinatorStudySubjectContextType {
  studySubjects: IStudySubjectDetails[];
  studySubjectLoading: boolean;
  getStudySubjectByDittiId: (id: string) => IStudySubjectDetails | undefined;
  fetchStudySubjects: () => void;
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

export interface IParticipantApi {
  scope: string[];
  apiName: string;
}

export interface IParticipantStudy {
  studyName: string;
  studyId: number;
  createdOn: string;
  startsOn: string;
  expiresOn?: string;
  consentInformation?: string;
  didConsent: boolean;
  dataSummary?: string;
}

export interface IParticipant {
  dittiId: string;
  apis: IParticipantApi[];
  studies: IParticipantStudy[];
}


/**
 * A combination of participant data fetched from both the database and AWS, minus `userPermissionId` in favor of
 * `dittiId`
 */
export interface IStudySubjectDetails {
  id: number;
  createdOn: string;
  dittiId: string;
  studies: StudyJoin[];
  apis: ApiJoin[];
  tapPermission: boolean;
  information: string;
  dittiExpTime: string;
  teamEmail: string;
  createdAt: string;
}


export interface IFlashMessage {
  id: number;
  element: React.ReactElement;
  containerRef: React.RefObject<HTMLDivElement>;
}


/**
 * Stages sleep levels.
 */
export type ISleepLevelStages = "deep" | "light" | "rem" | "wake";


/**
 * Classic sleep levels.
 */
export type ISleepLevelClassic = "asleep" | "restless" | "awake";


/**
 * Represents a sleep level with details about the level and duration.
 * @property dateTime - The timestamp of the sleep level.
 * @property level - The sleep level (stages or classic).
 * @property seconds - The duration of the sleep level in seconds.
 * @property isShort - Whether the sleep level is considered short.
 */
export interface ISleepLevel {
  dateTime: string;
  level: ISleepLevelStages | ISleepLevelClassic;
  seconds: number;
  isShort: boolean | null;
}


/**
 * Represents a sleep log entry.
 * @property dateOfSleep - The date of the sleep log.
 * @property logType - The type of log entry.
 * @property type - The type of sleep log.
 * @property levels - The sleep levels for the log entry.
 */
export interface ISleepLog {
  dateOfSleep: string;
  logType: "auto_detected" | "manual";
  type: "stages" | "classic";
  levels: ISleepLevel[];
}


/**
 * Defines the context containing information about wearable data.
 * @property startDate - The start date of the data range.
 * @property endDate - The end date of the data range.
 * @property sleepLogs - The sleep logs for the data range.
 * @property isLoading - Whether data is being fetched from the database.
 * @property isSyncing - Whether data is being synced with the wearable API.
 * @property dataIsUpdated - Whether the current data has been updated since the first load.
 * @property firstDateOfSleep - The first date of sleep data available.
 * @property syncData - Function to invoke a data processing task and sync data with the wearable API.
 * @property decrementStartDate - Function to decrement the start and end dates by one day.
 * @property incrementStartDate - Function to increment the start and end dates by one day.
 * @property resetStartDate - Function to reset the start and end dates.
 * @property canIncrementStartDate - Whether the start date can be incremented.
 */
export interface IWearableDataContextType {
  startDate: Date;
  endDate: Date;
  sleepLogs: ISleepLog[];
  isLoading: boolean;
  isSyncing?: boolean;
  dataIsUpdated?: boolean;
  firstDateOfSleep?: Date | null;
  syncData?: () => void;
  decrementStartDate?: () => void;
  incrementStartDate?: () => void;
  resetStartDate?: () => void;
  canIncrementStartDate?: boolean;
}


/**
 * Default props to pass to any visualization component.
 * @property marginTop - The default margin at the top of the visualization.
 * @property marginRight - The default margin at the right of the visualization.
 * @property marginBottom - The default margin at the bottom of the visualization.
 * @property marginLeft - The default margin at the left of the visualization.
 */
export interface IVisualizationProps {
  marginTop?: number;
  marginRight?: number;
  marginBottom?: number;
  marginLeft?: number;
}


/**
 * Represents a data processing task status.
 */
type DataProcessingTaskStatus = "Pending"
  | "InProgress"
  | "Success"
  | "Failed"
  | "CompletedWithErrors";


/**
 * Represents a data processing task.
 * @property id - The database primary key.
 * @property status - The status of the data processing task.
 * @property billedMs - The amount of milliseconds the task took to process (not used).
 * @property createdOn - When the task was created.
 * @property updatedOn - When the task was last updated.
 * @property completedOn - When the task was completed.
 * @property logFile - The S3 URI of the function's log file.
 * @property errorCode - The error code if the task failed.
 */
export interface IDataProcessingTask {
  id: number;
  status: DataProcessingTaskStatus;
  billedMs: string;
  createdOn: string;
  updatedOn: string;
  completedOn: string;
  logFile: string | null;
  errorCode: string | null;
}


/**
 * Breadcrumbs for display in the Navbar component.
 * @property name - The name of the breadcrumb to display in the navbar.
 * @property link - The link to navigate to when the breadcrumb is clicked.
 */
export interface IBreadcrumb {
  name: string;
  link: string | null;
}


/**
 * Defines the context containing information about the navbar.
 * @property breadcrumbs - The breadcrumbs to display in the navbar.
 * @property setStudySlug - Function to set the study slug in the breadcrumbs.
 * @property setSidParam - Function to set the SID parameter in the breadcrumbs.
 * @property setDittiIdParam - Function to set the Ditti ID parameter in the breadcrumbs.
 */
export interface NavbarContextType {
  breadcrumbs: IBreadcrumb[];
  setStudySlug: (studyCrumb: string) => void;
  setSidParam: (sid: string) => void;
  setDittiIdParam: (dittiId: string) => void;
}


/**
 * Defines the context containing information about the flash messages.
 * @property flashMessages - The flash messages to display on the page.
 * @property flashMessage - Function to flash a message on the page.
 */
export interface FlashMessageContextType {
  flashMessages: IFlashMessage[];
  flashMessage: (msg: React.ReactElement, variant: FlashMessageVariant) => void;
}


export interface QuillFieldProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  description?: string;
  placeholder?: string;
  id?: string;
  config?: QuillOptions;
  className?: string;
  containerClassName?: string;
  readOnly?: boolean;
}