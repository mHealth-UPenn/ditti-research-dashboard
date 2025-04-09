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

import { useEffect, useState } from "react";
import { getAccess } from "../../utils";
import { Card } from "../cards/card";
import { ViewContainer } from "../containers/viewContainer";
import { CardContentRow } from "../cards/cardContentRow";
import { Title } from "../text/title";
import { ActiveIcon } from "../icons/activeIcon";
import { useStudiesContext } from "../../contexts/studiesContext";
import { SmallLoader } from "../loader";
import { useCoordinatorStudySubjectContext } from "../../hooks/useCoordinatorStudySubjectContext";
import { LinkComponent } from "../links/linkComponent";
import { Link } from "react-router-dom";


/**
 * Interface for details of each study to display.
 * @key number: The study ID.
 * @property numSubjects: The number of subjects enrolled in the study.
 * @property numSubjectsWithApi: The number of subjects who are enrolled in the study and who have connected any API.
 */
interface IWearableDetails {
  [key: number]: {
    numSubjects: number;
    numSubjectsWithApi: number;
  }
}


export function WearableStudies() {
  const [canViewWearableData, setCanViewWearableData] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);

  const { studies, studiesLoading } = useStudiesContext();
  const { studySubjects, studySubjectLoading } = useCoordinatorStudySubjectContext();

  // The summary details to show for each study
  const wearableDetails: IWearableDetails = {};
  for (const ss of studySubjects) {
    // Count `hasApi` if the current subject has at least 1 API connected and is active in at least one study
    const hasApi = Number(
      ss.apis.length &&
      ss.studies.some(s => new Date(s.expiresOn) > new Date())
    );

    for (const join of ss.studies) {
      if (wearableDetails[join.study.id]) {
        wearableDetails[join.study.id].numSubjects += 1;
        wearableDetails[join.study.id].numSubjectsWithApi += hasApi;
      } else {
        wearableDetails[join.study.id] = {
          numSubjects: 1,
          numSubjectsWithApi: hasApi
        };
      }
    }
  }

  // Get which studies the current user can view wearable data for on load
  useEffect(() => {
    const updatedCanViewWearableData: Set<number> = new Set();
    const promises: Promise<unknown>[] = [];

    studies.forEach(s =>
      promises.push(
        getAccess(3, "View", "Wearable Data", s.id)
          .then(() => updatedCanViewWearableData.add(s.id))
          .catch(() => updatedCanViewWearableData.delete(s.id))
      )
    );

    Promise.all(promises).then(() => {
      setCanViewWearableData(updatedCanViewWearableData);
    }).catch(console.error)
    .finally(() => setLoading(false));
  }, [studies]);

  if (loading || studiesLoading || studySubjectLoading) {
    return (
      <ViewContainer>
        <Card width="md">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      <Card width="md">
        <CardContentRow>
          <Title>Studies</Title>
        </CardContentRow>
        {
          // For each study the user has access to
          studies.map((s) => {
            return (
              <CardContentRow key={s.id} className="border-b border-light">
                <div className="flex items-start">

                  {/* Active icon */}
                  {canViewWearableData.has(s.id) ?
                    <ActiveIcon active={true} className="mr-2" /> :
                    // Optimistic hydration
                    <ActiveIcon active={false} className="mr-2" />
                  }

                  {/* link to study summary */}
                  <div className="flex flex-col">
                    <Link to={`/coordinator/wearable/study?sid=${s.id}`}>
                      <LinkComponent>
                        {s.acronym}
                      </LinkComponent>
                    </Link>
                    <span className="text-sm">{s.name}</span>
                  </div>
                </div>

                {/* Study summary details */}
                <div className="flex flex-col">
                  <div className="text-sm font-bold">
                    {
                      s.id in wearableDetails
                        ? wearableDetails[s.id].numSubjectsWithApi
                        : 0
                    } subjects with connected APIs
                  </div>
                  <div className="text-sm">
                    {
                      s.id in wearableDetails
                        ? wearableDetails[s.id].numSubjects
                        : 0
                    } enrolled subjects
                  </div>
                </div>
              </CardContentRow>
            );
          })
        }
      </Card>
    </ViewContainer>
  );
}
