import StudySubjectProvider from "../../contexts/studySubjectContext";
import ParticipantDashboardContent from "./participantDashboardContent";


export default function ParticipantDashboard() {
  return (
    <StudySubjectProvider>
      <ParticipantDashboardContent />
    </StudySubjectProvider>
  );
}
