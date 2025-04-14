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

import React from "react";
import { differenceInDays } from "date-fns";
import { CardContentRow } from "../cards/cardContentRow";
import { ActiveIcon } from "../icons/activeIcon";
import { LinkComponent } from "../links/linkComponent";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { Link } from "react-router-dom";
import { SmallLoader } from "../loader/loader";
import { getEnrollmentInfoForStudy } from "../../utils";
import { useStudies } from "../../hooks/useStudies";
import { StudySubjectModel } from "../../types/models";
import { WearableStudySubjectsProps } from "./wearableDashboard.types";

export function WearableStudySubjects({
  studyDetails,
  canViewWearableData,
}: WearableStudySubjectsProps) {
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjects();
  const { study } = useStudies();

  // Get only study subjects with prefixes that equal the current study's prefix
  const studySubjectsFiltered = studySubjects.filter(ss => new RegExp(`^${studyDetails.dittiId}\\d`).test(ss.dittiId));

  const getSubjectSummary = (subject: StudySubjectModel): React.ReactElement => {
    const { expiresOn } = getEnrollmentInfoForStudy(subject, study?.id);
    const expiresOnDiff = differenceInDays(new Date(expiresOn), new Date());

    return (
      <CardContentRow
        key={subject.dittiId}
        className="border-b border-light">
          <div className="flex flex-col">
            <div className="flex items-center">

              {/* Active icon */}
              {canViewWearableData && <ActiveIcon active={true} className="mr-2" />}

              {/* Link to the subject's visualization */}
              {canViewWearableData && subject.apis.length ?
                <Link to={`/coordinator/wearable/participants/view?dittiId=${subject.dittiId}&sid=${studyDetails.id}`}>
                  <LinkComponent>
                    {subject.dittiId}
                  </LinkComponent>
                </Link> :
                <span>{subject.dittiId}</span>
              }
            </div>
            <i className="w-max">Enrollment ends in: {expiresOnDiff ? expiresOnDiff + " days" : "Today"}</i>
          </div>

          {/* A list of connected APIs for the current study subject */}
          {canViewWearableData &&
            <div className="flex flex-grow-0 overflow-x-hidden">
              <div className="hidden md:flex items-center">
                {subject.apis.length ?
                  subject.apis.map((api, i) =>
                    <span
                      className={i ? "border-l border-light ml-2 pl-2" : ""}
                      key={api.api.id}>
                        {api.api.name}
                    </span>
                  ) :
                  <span>No APIs connected</span>
                }
              </div>
            </div>
          }
      </CardContentRow>
    );
  };

  if (studySubjectLoading) {
    return <SmallLoader />;
  }

  return (
    <>
      {studySubjectsFiltered.length ? studySubjectsFiltered.map(getSubjectSummary) : "No active subjects"}
    </>
  );
}
