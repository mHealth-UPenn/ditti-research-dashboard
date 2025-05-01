import { useContext } from "react";
import {
  ParticipantWearableDataContext,
  CoordinatorWearableDataContext,
} from "../contexts/wearableDataContext";
import { WearableDataContextValue } from "../contexts/wearableDataContext.types";

// Returns either the participant or coordinator context depending on which provider was used
export const useWearableData = (): WearableDataContextValue => {
  const participantContext = useContext(ParticipantWearableDataContext);
  const coordinatorContext = useContext(CoordinatorWearableDataContext);
  if (participantContext !== undefined) {
    return participantContext;
  } else if (coordinatorContext !== undefined) {
    return coordinatorContext;
  }
  throw new Error("useWearableData must be used within a WearableDataProvider");
};
