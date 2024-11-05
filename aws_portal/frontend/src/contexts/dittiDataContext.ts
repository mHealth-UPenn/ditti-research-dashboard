import { createContext, useContext } from "react";
import { AudioFile, AudioTapDetails, TapDetails, UserDetails } from "../interfaces";

interface IDittiDataContext {
  dataLoading: boolean;
  taps: TapDetails[]
  audioTaps: AudioTapDetails[]
  audioFiles: AudioFile[]
  users: UserDetails[];
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
