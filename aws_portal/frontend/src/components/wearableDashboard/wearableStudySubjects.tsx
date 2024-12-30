import React from "react";
import { IStudySubject, Study } from "../../interfaces";
import { differenceInDays } from "date-fns";
import CardContentRow from "../cards/cardContentRow";
import ActiveIcon from "../icons/activeIcon";
import LinkComponent from "../links/linkComponent";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { Link } from "react-router-dom";
import { SmallLoader } from "../loader";


/**
 * Props for wearable study subjects.
 * @property studyDetails: The details of study to list subjects for.
 * @property canViewWearableData: Whether the current user can view wearable data for the current study.
 */
interface WearableStudySubjectsProps {
  studyDetails: Study;
  canViewWearableData: boolean;
}


export default function WearableStudySubjects({
  studyDetails,
  canViewWearableData,
}: WearableStudySubjectsProps) {
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjectContext();

  // Get only study subjects with prefixes that equal the current study's prefix
  const studySubjectsFiltered = studySubjects.filter(ss => new RegExp(`^${studyDetails.dittiId}\\d`).test(ss.dittiId));

  const getSubjectSummary = (subject: IStudySubject): React.ReactElement => {
    // Use the last `expiresOn` date as the date of last data collection
    const endDate = new Date(Math.max(...subject.studies.map(s => new Date(s.expiresOn).getTime())));
    const expiresOn = differenceInDays(endDate, new Date());

    return (
      <CardContentRow
        key={subject.dittiId}
        className="border-b border-light">
          <div className="flex flex-col">
            <div className="flex items-center">

              {/* Active icon */}
              {canViewWearableData && <ActiveIcon active={true} className="mr-2" />}

              {/* Link to the subject's visualization */}
              {canViewWearableData ?
                <Link to={`/coordinator/wearable/participants/view?dittiId=${subject.dittiId}&sid=${studyDetails.id}`}>
                  <LinkComponent>
                    {subject.dittiId}
                  </LinkComponent>
                </Link> :
                <span>{subject.dittiId}</span>
              }
            </div>
            <i className="w-max">Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
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
