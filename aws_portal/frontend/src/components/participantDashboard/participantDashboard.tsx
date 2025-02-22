/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

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
