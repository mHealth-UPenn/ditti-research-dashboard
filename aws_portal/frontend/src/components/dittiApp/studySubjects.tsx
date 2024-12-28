import React from "react";
import { IStudySubjectDetails, Study, UserDetails, ViewProps } from "../../interfaces";
import { add, differenceInDays, isWithinInterval, sub } from "date-fns";
import SubjectVisuals from "./subjectVisualsV2";
import CardContentRow from "../cards/cardContentRow";
import ActiveIcon from "../icons/activeIcon";
import Link from "../links/link";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";

/**
 * studyPrefix: the ditti app prefix of the current study
 * getTaps: get tap data
 * studyDetials: the current study's information
 */
interface StudySubjectsProps extends ViewProps {
  studyPrefix: string;
  studyDetails: Study;
  canViewTaps: boolean;
}

const StudySubjects: React.FC<StudySubjectsProps> = ({
  studyPrefix,
  studyDetails,
  canViewTaps,
  flashMessage,
  goBack,
  handleClick,
}) => {
  const { taps, audioTaps } = useDittiDataContext();
  const { studySubjects } = useCoordinatorStudySubjectContext();
  const filteredStudySubjects = studySubjects.filter(ss => ss.dittiId.startsWith(studyPrefix));

  /**
   * Render recent summary tap data for a user
   * @param user 
   * @returns 
   */
  const getSubjectSummary = (studySubject: IStudySubjectDetails): React.ReactElement => {
    let summaryTaps: React.ReactElement[];
    let totalTaps = 0;

    // if the studySubject has access to tapping
    if (studySubject.tapPermission) {
      // for each day of the week
      summaryTaps = [6, 5, 4, 3, 2, 1, 0].map((i) => {
        const today = new Date(new Date().setHours(9, 0, 0, 0));

        // start from today minus i
        const start = sub(today, { days: i });

        // end at start plus 1 day
        const end = add(start, { days: 1 });

        // get taps and filter for only taps between start and end
        const filteredTaps = taps
          .filter(
            (t) =>
              t.dittiId === studySubject.dittiId &&
              isWithinInterval(new Date(t.time), { start, end })
          ).length;

        const filteredAudioTaps = audioTaps
          .filter(
            (t) =>
              t.dittiId === studySubject.dittiId &&
              isWithinInterval(new Date(t.time), { start, end })
          ).length;

        // get the current weekday (Mon, Tue, Wed, etc.)
        const weekday = start.toLocaleString("en-US", { weekday: "narrow" });

        return (
          <div key={i} className="hidden md:flex flex-grow-0 flex-col w-[60px] items-center border-r border-light">
            <span>{weekday}</span>
            <span>{filteredTaps + filteredAudioTaps}</span>
          </div>
        );
      });

      const today = new Date(new Date().setHours(9, 0, 0, 0));

      // get all taps starting from 7 days ago
      const start = sub(today, { days: 7 });
      const tapsCount = taps
        .filter(
          (t) =>
            t.dittiId === studySubject.dittiId &&
            isWithinInterval(new Date(t.time), { start, end: new Date() })
        ).length;
      const audioTapsCount = audioTaps
        .filter(
          (t) =>
            t.dittiId === studySubject.dittiId &&
            isWithinInterval(new Date(t.time), { start, end: new Date() })
        ).length;
      totalTaps = tapsCount + audioTapsCount;

      summaryTaps.push(
        <div key="total" className="flex flex-col items-center w-[80px] font-bold">
          <span>Total</span>
          <span>{totalTaps}</span>
        </div>
      );
    } else {
      summaryTaps = [
        <span key={0}>
          No tapping access
        </span>
      ];
    }

    // get the number of days until the user's id expires
    const expiresOn = differenceInDays(new Date(studySubject.expTime), new Date());

    const handleClickSubject = () =>
      handleClick(
        [studySubject.dittiId],
        <SubjectVisuals
          flashMessage={flashMessage}
          goBack={goBack}
          handleClick={handleClick}
          studyDetails={studyDetails}
          studySubject={studySubject}
        />
      );

    return (
      <CardContentRow
        key={studySubject.dittiId}
        className="border-b border-light">
          <div className="flex flex-col">
            <div className="flex items-center">
              {/* active tapping icon */}
              {canViewTaps && <ActiveIcon active={!!totalTaps} className="mr-2" />}
              {/* link to the studySubject's summary page */}
              {canViewTaps ?
                <Link onClick={handleClickSubject}>
                  {studySubject.dittiId}
                </Link> :
                <span>{studySubject.dittiId}</span>
              }
            </div>
            <i className="w-max">Expires in: {expiresOn ? expiresOn + " days" : "Today"}</i>
            {/* summary tap data */}
          </div>

          {canViewTaps &&
            <div className="flex flex-grow-0 overflow-x-hidden">
              {summaryTaps}
            </div>
          }
      </CardContentRow>
    );
  };

  // all users whose ids have not expired
  const activeUsers = filteredStudySubjects.filter(
    ss => new Date() < new Date(ss.expTime)
  );

  return (
    <>
      {activeUsers.length ? activeUsers.map(getSubjectSummary) : "No active subjects"}
    </>
  );
};

export default StudySubjects;
