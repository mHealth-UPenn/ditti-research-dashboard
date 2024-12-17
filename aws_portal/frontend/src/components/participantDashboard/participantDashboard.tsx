import StudySubjectProvider from "../../contexts/studySubjectContext";
import { useAuth } from "../../hooks/useAuth";
import Button from "../buttons/button";
import ViewContainer from "../containers/viewContainer";
import ParticipantDashboardContent from "./participantDashboardContent";


export default function ParticipantDashboard() {
  const { cognitoLogout } = useAuth();

  return (
    <main className="flex flex-col h-screen">
      {/* the header */}
      <div className="bg-secondary text-white flex items-center justify-between flex-shrink-0 h-16 shadow-xl z-10">
        <div className="flex flex-col text-2xl ml-8">
          <span className="mr-2">Ditti</span>
          <span className="text-sm whitespace-nowrap overflow-hidden">Participant Dashboard</span>
        </div>
        <div className="mr-8">
          <Button variant="tertiary" size="sm" rounded={true} onClick={cognitoLogout}>Logout</Button>
        </div>
      </div>

      <ViewContainer navbar={false}>
        <StudySubjectProvider>
          <ParticipantDashboardContent />
        </StudySubjectProvider>
      </ViewContainer>
    </main>
  );
}
