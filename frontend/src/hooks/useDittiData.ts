import { useContext } from "react";
import { DittiDataContext } from "../contexts/dittiDataContext";
import { DittiDataContextValue } from "../contexts/dittiDataContext.types";

/**
 * Hook for retrieving context data
 * @returns The current ditti data context.
 */
export const useDittiData = (): DittiDataContextValue => {
  const context = useContext(DittiDataContext);
  if (!context) {
    // Do not throw error and return empty data to accommodate call on participant dashboard.
    return {
      dataLoading: false,
      taps: [],
      audioTaps: [],
      audioFiles: [],
      refreshAudioFiles: () => {
        return Promise.resolve();
      },
    };
  }
  return context;
};
