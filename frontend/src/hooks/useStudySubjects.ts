import { useContext } from "react";
import { StudySubjectContext } from "../contexts/studySubjectContext";

// Hook for accessing context data
export function useStudySubjects() {
  const context = useContext(StudySubjectContext);
  if (!context) {
    throw new Error("useStudySubjects must be used within a StudySubjectContext provider");
  }
  return context;
}
