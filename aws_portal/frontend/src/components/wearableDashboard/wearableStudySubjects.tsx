import React from "react";
import { IStudySubject, Study, UserDetails, ViewProps } from "../../interfaces";
import { differenceInDays } from "date-fns";
import CardContentRow from "../cards/cardContentRow";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import WearableVisuals from "./wearableVisuals";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";

/**
 * studyPrefix: the ditti app prefix of the current study
 * getTaps: get tap data
 * studyDetials: the current study's information
 */
interface WearableStudySubjectsProps extends ViewProps {
  studyDetails: Study;
  canViewWearableData: boolean;
}

export default function WearableStudySubjects({
  studyDetails,
  canViewWearableData,
  flashMessage,
  goBack,
  handleClick,
}: WearableStudySubjectsProps) {
  const { studySubjects } = useCoordinatorStudySubjectContext();
  const studySubjectsFiltered = studySubjects.filter(ss => new RegExp(`^${studyDetails.dittiId}\\d`).test(ss.dittiId));

  const getSubjectSummary = (subject: IStudySubject): React.ReactElement => {
    // get the number of days until the subject's id expires
    const endDate = new Date(Math.max(...subject.studies.map(s => new Date(s.expiresOn).getTime())));
    const expiresOn = differenceInDays(endDate, new Date());

    const handleClickSubject = () =>
      handleClick(
        [subject.dittiId],
        // TODO: Revise the current nav architecture so that navigating to new views can still access context
        // The current nav architecture still relies on prop drilling for some views like this one
        <CoordinatorWearableDataProvider dittiId={subject.dittiId}>
          <WearableVisuals
            flashMessage={flashMessage}
            goBack={goBack}
            handleClick={handleClick}
            studyDetails={studyDetails}
            studySubject={subject} />
        </CoordinatorWearableDataProvider>
      );

    return (
      <CardContentRow
        key={subject.dittiId}
        className="border-b border-light">
          <div className="flex flex-col">
            <div className="flex items-center">
              {/* active tapping icon */}
              {canViewWearableData && <ActiveIcon active={true} className="mr-2" />}
              {/* link to the subject's summary page */}
              {canViewWearableData ?
                <Link onClick={handleClickSubject}>
                  {subject.dittiId}
                </Link> :
                <span>{subject.dittiId}</span>
              }
            </div>
            <i className="w-max">Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
          </div>

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

  // all users whose ids have not expired
  // const activeUsers = filteredUsers.filter(
  //   (u: UserDetails) => new Date() < new Date(u.expTime)
  // );

  return (
    <>
      {studySubjectsFiltered.length ? studySubjectsFiltered.map(getSubjectSummary) : "No active subjects"}
    </>
  );
}
