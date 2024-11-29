import React from "react";
import { Study, UserDetails, ViewProps } from "../../interfaces";
import { differenceInDays } from "date-fns";
import CardContentRow from "../cards/cardContentRow";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";

/**
 * studyPrefix: the ditti app prefix of the current study
 * getTaps: get tap data
 * studyDetials: the current study's information
 */
interface WearableStudySubjectsProps extends ViewProps {
  studyPrefix: string;
  canViewWearableData: boolean;
}

export default function WearableStudySubjects({
  studyPrefix,
  canViewWearableData,
  handleClick,
}: WearableStudySubjectsProps) {
  const users: UserDetails[] = [];
  const filteredUsers = users.filter(u => u.userPermissionId.startsWith(studyPrefix));

  const getSubjectSummary = (user: UserDetails): React.ReactElement => {
    // get the number of days until the user's id expires
    const expiresOn = differenceInDays(new Date(user.expTime), new Date());

    const handleClickSubject = () =>
      handleClick(
        [user.userPermissionId],
        <React.Fragment />
        // <SubjectVisuals
        //   flashMessage={flashMessage}
        //   goBack={goBack}
        //   handleClick={handleClick}
        //   studyDetails={studyDetails}
        //   user={user}
        // />
      );

    return (
      <CardContentRow
        key={user.userPermissionId}
        className="border-b border-light">
          <div className="flex flex-col">
            <div className="flex items-center">
              {/* active tapping icon */}
              {canViewWearableData && <ActiveIcon active={true} className="mr-2" />}
              {/* link to the user's summary page */}
              {canViewWearableData ?
                <Link onClick={handleClickSubject}>
                  {user.userPermissionId}
                </Link> :
                <span>{user.userPermissionId}</span>
              }
            </div>
            <i className="w-max">Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
            {/* summary tap data */}
          </div>

          {canViewWearableData &&
            <div className="flex flex-grow-0 overflow-x-hidden">
              <div className="hidden md:flex flex-grow-0 flex-col w-[60px] items-center border-r border-light">
                <span>Fitbit</span>
              </div>
            </div>
          }
      </CardContentRow>
    );
  };

  // all users whose ids have not expired
  const activeUsers = filteredUsers.filter(
    (u: UserDetails) => new Date() < new Date(u.expTime)
  );

  return (
    <>
      {activeUsers.length ? activeUsers.map(getSubjectSummary) : "No active subjects"}
    </>
  );
}
