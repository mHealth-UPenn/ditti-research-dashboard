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
  const studySubjectsFiltered = studySubjects.filter((ss) => {
    const prefix = String(studyDetails.dittiId);
    return new RegExp(`^${prefix}\\d`).test(ss.dittiId);
  });

  const getSubjectSummary = (
    subject: StudySubjectModel
  ): React.ReactElement => {
    const { expiresOn } = getEnrollmentInfoForStudy(subject, study?.id);
    const expiresOnDiff = differenceInDays(new Date(expiresOn), new Date());

    return (
      <CardContentRow key={subject.dittiId} className="border-b border-light">
        <div className="flex flex-col">
          <div className="flex items-center">
            {/* Active icon */}
            {canViewWearableData && (
              <ActiveIcon active={true} className="mr-2" />
            )}

            {/* Link to the subject's visualization */}
            {canViewWearableData && subject.apis.length ? (
              <Link
                to={`/coordinator/wearable/participants/view?dittiId=${subject.dittiId}&sid=${String(studyDetails.id)}`}
              >
                <LinkComponent>{subject.dittiId}</LinkComponent>
              </Link>
            ) : (
              <span>{subject.dittiId}</span>
            )}
          </div>
          <i className="w-max">
            Enrollment ends in:{" "}
            {expiresOnDiff ? `${String(expiresOnDiff)} days` : "Today"}
          </i>
        </div>

        {/* A list of connected APIs for the current study subject */}
        {canViewWearableData && (
          <div className="flex grow-0 overflow-x-hidden">
            <div className="hidden items-center md:flex">
              {subject.apis.length ? (
                subject.apis.map((api, i) => (
                  <span
                    className={i ? "ml-2 border-l border-light pl-2" : ""}
                    key={api.api.id}
                  >
                    {api.api.name}
                  </span>
                ))
              ) : (
                <span>No APIs connected</span>
              )}
            </div>
          </div>
        )}
      </CardContentRow>
    );
  };

  if (studySubjectLoading) {
    return <SmallLoader />;
  }

  return (
    <>
      {studySubjectsFiltered.length
        ? studySubjectsFiltered.map(getSubjectSummary)
        : "No active subjects"}
    </>
  );
}
