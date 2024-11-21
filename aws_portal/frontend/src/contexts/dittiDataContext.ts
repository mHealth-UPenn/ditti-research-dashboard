import { createContext, useContext } from "react";
import { AudioFile, AudioTapDetails, Study, TapDetails, User, UserDetails } from "../interfaces";

interface IDittiDataContext {
  dataLoading: boolean;
  studies: Study[];
  taps: TapDetails[]
  audioTaps: AudioTapDetails[]
  audioFiles: AudioFile[]
  users: UserDetails[];
  refreshAudioFiles: () => Promise<void>;
  getUserByDittiId: (id: string) => Promise<User>;
}

const DittiDataContext = createContext<IDittiDataContext | undefined>(undefined);


export const useDittiDataContext = () => {
  const context = useContext(DittiDataContext);
  if (!context) {
    throw new Error("useDittiDataContext must be used within a DittiDataContext provider");
  }
  return context;
};


export default DittiDataContext;
