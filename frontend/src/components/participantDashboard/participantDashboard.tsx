import { StudySubjectProvider } from "../../contexts/studySubjectContext";
import { useAuth } from "../../hooks/useAuth";
import { Button } from "../buttons/button";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { ParticipantDashboardContent } from "./participantDashboardContent";

export function ParticipantDashboard() {
  const { participantLogout } = useAuth();

  return (
    <main className="flex h-screen flex-col">
      {/* the header */}
      <div
        className="z-10 flex h-16 shrink-0 items-center justify-between
          bg-secondary text-white shadow-xl"
      >
        <div className="ml-8 flex flex-col text-2xl">
          <span className="mr-2">Ditti</span>
          <span className="overflow-hidden whitespace-nowrap text-sm">
            Participant Dashboard
          </span>
        </div>
        <div className="mr-8">
          <Button
            variant="tertiary"
            size="sm"
            rounded={true}
            onClick={participantLogout}
          >
            Logout
          </Button>
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
