import { useContext } from "react";
import { CoordinatorStudySubjectContext } from "../contexts/coordinatorStudySubjectContext";
import { CoordinatorStudySubjectContextValue } from "../contexts/coordinatorStudySubjectContext.types";

/**
 * Hook for retrieving context data
 * @returns The current coordinator study subjects context.
 */
export function useCoordinatorStudySubjects(): CoordinatorStudySubjectContextValue {
  const context = useContext(CoordinatorStudySubjectContext);
  if (!context) {
    throw new Error(
      "useCoordinatorStudySubjects must be used within a CoordinatorStudySubjectContext provider"
    );
  }
  return context;
}
