import React from "react";
import { add, differenceInDays, isWithinInterval, sub } from "date-fns";
import { CardContentRow } from "../cards/cardContentRow";
import { ActiveIcon } from "../icons/activeIcon";
import { LinkComponent } from "../links/linkComponent";
import { useDittiData } from "../../hooks/useDittiData";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { Link } from "react-router-dom";
import { getEnrollmentInfoForStudy } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { StudySubjectsProps } from "./dittiApp.types";

export const StudySubjects: React.FC<StudySubjectsProps> = ({
  study,
  canViewTaps,
}) => {
  const { dataLoading, taps, audioTaps } = useDittiData();
  const { studySubjectLoading, studySubjects } = useCoordinatorStudySubjects();

  // Get only study subjects enrolled in the current study
  const filteredStudySubjects = studySubjects.filter((ss) =>
    ss.dittiId.startsWith(study.dittiId)
  );

  const summaries: React.ReactElement[] = [];
  filteredStudySubjects.forEach((studySubject) => {
    let summaryTaps: React.ReactElement[];
    let totalTaps = 0;

    const { expiresOn } = getEnrollmentInfoForStudy(studySubject, study.id);

    // Skip expired participants
    if (new Date() >= new Date(expiresOn)) {
      return;
    }

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
        const filteredTaps = taps.filter(
          (t) =>
            t.dittiId === studySubject.dittiId &&
            isWithinInterval(new Date(t.time), { start, end })
        ).length;

        const filteredAudioTaps = audioTaps.filter(
          (t) =>
            t.dittiId === studySubject.dittiId &&
            isWithinInterval(new Date(t.time), { start, end })
        ).length;

        // get the current weekday (Mon, Tue, Wed, etc.)
        const weekday = start.toLocaleString("en-US", { weekday: "narrow" });

        return (
          <div
            key={i}
            className="hidden w-[60px] grow-0 flex-col items-center border-r
              border-light md:flex"
          >
            <span>{weekday}</span>
            <span>{filteredTaps + filteredAudioTaps}</span>
          </div>
        );
      });

      const today = new Date(new Date().setHours(9, 0, 0, 0));

      // get all taps starting from 7 days ago
      const start = sub(today, { days: 7 });
      const tapsCount = taps.filter(
        (t) =>
          t.dittiId === studySubject.dittiId &&
          isWithinInterval(new Date(t.time), { start, end: new Date() })
      ).length;
      const audioTapsCount = audioTaps.filter(
        (t) =>
          t.dittiId === studySubject.dittiId &&
          isWithinInterval(new Date(t.time), { start, end: new Date() })
      ).length;
      totalTaps = tapsCount + audioTapsCount;

      summaryTaps.push(
        <div
          key="total"
          className="flex w-[80px] flex-col items-center font-bold"
        >
          <span>Total</span>
          <span>{totalTaps}</span>
        </div>
      );
    } else {
      summaryTaps = [<span key={0}>No tapping access</span>];
    }

    // get the number of days until the user's id expires
    const expiresOnDiff = differenceInDays(new Date(expiresOn), new Date());

    summaries.push(
      <CardContentRow
        key={studySubject.dittiId}
        className="border-b border-light"
      >
        <div className="flex flex-col">
          <div className="flex items-center">
            {/* active tapping icon */}
            {canViewTaps && (
              <ActiveIcon active={!!totalTaps} className="mr-2" />
            )}
            {/* link to the studySubject's summary page */}
            {canViewTaps ? (
              <Link
                to={`/coordinator/ditti/participants/view?dittiId=${studySubject.dittiId}&sid=${String(study.id)}`}
              >
                <LinkComponent>{studySubject.dittiId}</LinkComponent>
              </Link>
            ) : (
              <span>{studySubject.dittiId}</span>
            )}
          </div>
          <i className="w-max">
            Enrollment ends in:{" "}
            {expiresOnDiff ? `${String(expiresOnDiff)} days` : "Today"}
          </i>
          {/* summary tap data */}
        </div>

        {canViewTaps && (
          <div className="flex grow-0 overflow-x-hidden">{summaryTaps}</div>
        )}
      </CardContentRow>
    );
  });

  if (dataLoading || studySubjectLoading) {
    return <SmallLoader />;
  }

  return <>{summaries.length ? summaries : "No active subjects"}</>;
};
