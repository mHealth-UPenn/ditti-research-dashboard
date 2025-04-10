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
  taps: TapModel[]
  audioTaps: AudioTapModel[]
  audioFiles: AudioFile[]
  refreshAudioFiles: () => Promise<void>;
}
