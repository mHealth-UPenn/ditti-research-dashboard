import { CoordinatorStudySubjectProvider } from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";
import { StudiesProvider } from "../../contexts/studiesContext";


// React Router container for passing context to the WearableDashboard
export function WearableDashboard() {
  return (
    <StudiesProvider app={3}>
      <CoordinatorStudySubjectProvider app={3}>
        <Outlet />
      </CoordinatorStudySubjectProvider>
    </StudiesProvider>
  );
}
