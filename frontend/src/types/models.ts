import { ApiJoin, StudyJoin } from "./api";

/**
 * Ditti user data used in the frontend.
 * @property tapPermission - Indicates if the user has access to taps.
 * @property information - Content from the assigned about sleep template.
 * @property userPermissionId - The user's ditti ID.
 * @property expTime - Expiration time of the user's ID.
 * @property teamEmail - The team email assigned to this user.
 * @property createdAt - When the user was created.
 */
export interface UserModel {
  tapPermission: boolean;
  information: string;
  userPermissionId: string;
  expTime: string;
  teamEmail: string;
  createdAt: string;
}

/**
 * Represents a tap with details specific to frontend use.
 * @property dittiId - The ditti ID of the user who created the tap.
 * @property time - The tap's timestamp.
 * @property timezone - The timezone associated with the tap.
 */
export interface TapModel {
  dittiId: string;
  time: Date;
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
export interface AudioTapModel {
  dittiId: string;
  audioFileTitle: string;
  time: Date;
  timezone: string;
  action: string;
}

/**
 * Account data as used by the dashboard header.
 * @property firstName - The account holder's first name.
 * @property lastName - The account holder's last name.
 * @property email - The account holder's email.
 * @property phoneNumber - The account holder's phone number (optional).
 */
export interface AccountModel {
  firstName: string;
  lastName: string;
  email: string;
  phoneNumber?: string;
}

/**
 * A combination of participant data fetched from both the database and AWS, minus `userPermissionId` in favor of
 * `dittiId`
 * @property id - The database primary key.
 * @property createdOn - When the database entry for the study subject was created.
 * @property dittiId - The study subject's primary key.
 * @property studies - The studies that the study subject is enrolled in and information about their enrollment.
 * @property apis - The APIs that the study subject granted access to and information about the access they granted.
 * @property tapPermission - Indicates if the participant has access to taps.
 * @property information - Content from the assigned about sleep template.
 */
export interface StudySubjectModel {
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

/**
 * Information for study contacts
 * @property fullName - The full name of the study contact
 * @property email - The email of the study contact
 * @property phoneNumber - The phone number of the study contact
 * @property role - The role of the study contact
 */
export interface StudyContactModel {
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
}
