import { createContext, useContext } from "react";
import { AudioFile, AudioTapDetails, Study, TapDetails, User, UserDetails } from "../interfaces";

interface IDittiDataContext {
  dataLoading: boolean;
  taps: TapDetails[]
  audioTaps: AudioTapDetails[]
  audioFiles: AudioFile[]
  refreshAudioFiles: () => Promise<void>;
}

const DittiDataContext = createContext<IDittiDataContext | undefined>(undefined);


export const useDittiDataContext = (): IDittiDataContext => {
  const context = useContext(DittiDataContext);
  if (!context) {
    // Do not throw error and return empty data to accommodate call on participant dashboard.
    return {
      dataLoading: false,
      taps: [],
      audioTaps: [],
      audioFiles: [],
      refreshAudioFiles: async () => { return; },
    }
  }
  return context;
};


export default DittiDataContext;
