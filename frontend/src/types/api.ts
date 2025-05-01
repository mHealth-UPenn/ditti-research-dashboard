/**
 * Represents an account with user details and permissions.
 * @property id - The database primary key.
 * @property createdOn - The timestamp when the account was created.
 * @property lastLogin - The timestamp when the account was last logged in.
 * @property firstName - The account holder's first name.
 * @property lastName - The account holder's last name.
 * @property email - The account holder's email.
 * @property phoneNumber - The account holder's phone number.
 * @property isConfirmed - Whether the account has been confirmed after first login.
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
 * @property dataSummary - Text describing why participant data is collected.
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
  api: { id: number; name: string };
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
 * User data as returned from the backend.
 * @property tap_permission - Whether the user has access to taps.
 * @property information - Content from the assigned about sleep template.
 * @property user_permission_id - The user's ditti ID.
 * @property exp_time - Expiration time of the user's ID.
 * @property team_email - The team email assigned to this user.
 * @property createdAt - When the user was created.
 * @property updatedAt - When the user was last updated.
 * @property id - The user's ID.
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
 * Represents a tap as returned from the backend.
 * @property dittiId - The user's ditti ID.
 * @property time - The tap's timestamp.
 * @property timezone - The timezone associated with the tap.
 */
export interface Tap {
  dittiId: string;
  time: string;
  timezone: string;
}

/**
 * Represents an audio tap as returned from the backend.
 * @property dittiId - The user's ditti ID.
 * @property audioFileTitle - The title of the audio file.
 * @property time - The timestamp of the audio tap.
 * @property timezone - The timezone associated with the audio tap.
 * @property action - The action recorded with the audio tap.
 */
export interface AudioTap {
  dittiId: string;
  audioFileTitle: string;
  time: string;
  timezone: string;
  action: string;
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
  status:
    | "Pending"
    | "InProgress"
    | "Success"
    | "Failed"
    | "CompletedWithErrors";
  billedMs: number | null;
  createdOn: string;
  updatedOn: string;
  completedOn: string | null;
  logFile: string | null;
  errorCode: string | null;
}

/**
 * The study subject data structure as it is returned from the database.
 * @property id - The database primary key.
 * @property createdOn - When the database entry for the study subject was created.
 * @property dittiId - The study subject's primary key.
 * @property studies - The studies that the study subject is enrolled in and information about their enrollment.
 * @property apis - The APIs that the study subject granted access to and information about the access they granted.
 */
export interface StudySubject {
  id: number;
  createdOn: string;
  dittiId: string;
  studies: StudyJoin[];
  apis: ApiJoin[];
}

/**
 * Represents an API that a participant has granted access to.
 * @property scope - The scope that the participant granted with the API.
 * @property apiName - The name of the API.
 */
export interface ParticipantApi {
  scope: string[];
  apiName: string;
}

/**
 * Represents a study that a participant is enrolled in.
 * @property studyName - The name of the study.
 * @property studyId - The ID of the study.
 * @property createdOn - When the participant was enrolled in the study.
 * @property startsOn - When the participant's enrollment in the study begins.
 * @property expiresOn - When the participant's enrollment in the study ends.
 * @property consentInformation - The consent text shown to the participant.
 * @property didConsent - Whether the participant consented to being enrolled in the study.
 * @property dataSummary - Text describing why participant data is collected.
 */
export interface ParticipantStudy {
  studyName: string;
  studyId: number;
  createdOn: string;
  startsOn: string;
  expiresOn?: string;
  consentInformation?: string;
  didConsent: boolean;
  dataSummary?: string;
}

/**
 * Represents a participant with their Ditti ID and associated APIs and studies.
 * @property dittiId - The participant's Ditti ID.
 * @property apis - The APIs that the participant has granted access to.
 * @property studies - The studies that the participant is enrolled in.
 */
export interface Participant {
  dittiId: string;
  apis: ParticipantApi[];
  studies: ParticipantStudy[];
}

/**
 * Stages sleep levels.
 */
export type SleepLevelStages = "deep" | "light" | "rem" | "wake";

/**
 * Classic sleep levels.
 */
export type SleepLevelClassic = "asleep" | "restless" | "awake";

/**
 * Represents a sleep level with details about the level and duration.
 * @property dateTime - The timestamp of the sleep level.
 * @property level - The sleep level (stages or classic).
 * @property seconds - The duration of the sleep level in seconds.
 * @property isShort - Whether the sleep level is considered short.
 */
export interface SleepLevel {
  dateTime: string;
  level: SleepLevelStages | SleepLevelClassic;
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
export interface SleepLog {
  dateOfSleep: string;
  logType: "auto_detected" | "manual";
  type: "stages" | "classic";
  levels: SleepLevel[];
}

/**
 * Represents a data processing task status.
 */
type DataProcessingTaskStatus =
  | "Pending"
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
export interface DataProcessingTask {
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
