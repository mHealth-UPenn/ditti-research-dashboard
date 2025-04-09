import { useContext } from "react";
import { ParticipantWearableDataContext } from "../contexts/wearableDataContext";
import { IWearableDataContextType } from "../interfaces";
import { CoordinatorWearableDataContext } from "../contexts/wearableDataContext";

// Returns either the participant or coordinator context depending on which provider was used
export const useWearableData = (): IWearableDataContextType => {
  const participantContext = useContext(ParticipantWearableDataContext);
  const coordinatorContext = useContext(CoordinatorWearableDataContext);
  if (participantContext !== undefined) {
    return participantContext;
  } else if (coordinatorContext !== undefined) {
    return coordinatorContext;
  }
  throw new Error("useWearableData must be used within a WearableDataProvider");
};
