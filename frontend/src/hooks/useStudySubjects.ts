import { useContext } from "react";
import { StudySubjectContext } from "../contexts/studySubjectContext";
import { StudySubjectContextValue } from "../contexts/studySubjectContext.types";

/**
 * Hook for accessing context data
 * @returns The current study subjects context.
 */
export function useStudySubjects(): StudySubjectContextValue {
  const context = useContext(StudySubjectContext);
  if (!context) {
    throw new Error(
      "useStudySubjects must be used within a StudySubjectContext provider"
    );
  }
  return context;
}
