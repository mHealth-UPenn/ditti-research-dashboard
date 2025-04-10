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
