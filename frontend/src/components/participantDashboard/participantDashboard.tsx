/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
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
