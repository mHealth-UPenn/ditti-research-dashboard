import { Study } from "../../types/api";

/**
 * @property {Study} study - The study to display subjects for.
 * @property {boolean} canViewTaps - Whether the logged in coordinator can view tapping data.
 */
export interface StudySubjectsProps {
  study: Study;
  canViewTaps: boolean;
}

/**
 * Metadata for an audio file to upload.
 * @property {string} name - The name of the file.
 * @property {string} title - The title of the file.
 * @property {string} size - The size of the file.
 * @property {number} length - The length of the file.
 * @property {boolean} exists - Whether the file exists.
 */
export interface FileMetadata {
  name: string;
  title: string;
  size: string;
  length: number;
  exists: boolean;
}
