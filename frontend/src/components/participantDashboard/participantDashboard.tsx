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
        className="z-10 flex h-16 flex-shrink-0 items-center justify-between
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
