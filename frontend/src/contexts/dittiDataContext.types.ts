/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
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
