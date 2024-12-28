import { PropsWithChildren } from "react";
import CoordinatorStudySubjectProvider from "../../contexts/coordinatorStudySubjectContext";
import { Outlet } from "react-router-dom";


function WearableDashboard() {
  return (
    <CoordinatorStudySubjectProvider app={3}>
      <Outlet />
    </CoordinatorStudySubjectProvider>
  );
}


export default WearableDashboard;
