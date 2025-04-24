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
import { AudioFile } from "../types/api";
import { AudioTapModel, TapModel } from "../types/models";

/**
 * Defines the context containing information about Ditti data.
 * @property dataLoading - Whether data is being fetched from the database.
 * @property taps - The taps for the current user.
 * @property audioTaps - The audio taps for the current user.
 * @property audioFiles - The audio files for the current user.
 * @property refreshAudioFiles - Function to refresh the audio files.
 */
export interface DittiDataContextValue {
  dataLoading: boolean;
  taps: TapModel[];
  audioTaps: AudioTapModel[];
  audioFiles: AudioFile[];
  refreshAudioFiles: () => Promise<void>;
}
