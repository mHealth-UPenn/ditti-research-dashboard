import { useContext } from "react";
import { CoordinatorStudySubjectContext } from "../contexts/coordinatorStudySubjectContext";

// Hook for retrieving context data
export function useCoordinatorStudySubjects() {
  const context = useContext(CoordinatorStudySubjectContext);
  if (!context) {
    throw new Error("useCoordinatorStudySubjects must be used within a CoordinatorStudySubjectContext provider");
  }
  return context;
}
