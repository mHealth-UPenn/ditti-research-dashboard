import { useState, useEffect, useMemo } from "react";
import { differenceInMilliseconds, format } from "date-fns";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import "./subjectVisuals.css";
import { getAccess } from "../../utils";
import { SmallLoader } from "../loader";
import TimestampHistogram from "../visualizations/timestampHistogram";
import VisualizationController from "../visualizations/visualizationController";
import TapVisualizationButtons from "../visualizations/tapVisualizationButtons";
import BoutsTimeline from "../visualizations/boutsTimeline";
import AudioTapsTimeline from "../visualizations/audioTapsTimeline";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import CardContentRow from "../cards/cardContentRow";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { APP_ENV } from "../../environment";
import { Link, useSearchParams } from "react-router-dom";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { useStudiesContext } from "../../contexts/studiesContext";


const SubjectVisualsV2 = () => {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId") || "";

  const [canEdit, setCanEdit] = useState(false);
  const [loading, setLoading] = useState(true);

  const { dataLoading, taps, audioTaps } = useDittiDataContext();
  const { studiesLoading, study } = useStudiesContext();
  const { studySubjectLoading, getStudySubjectByDittiId } = useCoordinatorStudySubjectContext();

  useEffect(() => {
    getAccess(2, "Edit", "Participants", studyId)
      .then(() => {
        setCanEdit(true);
        setLoading(false);
      })
      .catch(() => {
        setCanEdit(false);
        setLoading(false);
      });
  }, [studyId]);

  const studySubject = getStudySubjectByDittiId(dittiId);
  const filteredTaps = taps.filter((t) => t.dittiId === dittiId);
  const filteredAudioTaps = audioTaps.filter((at) => at.dittiId === dittiId);

  const timestamps = useMemo(
    () => filteredTaps.map(t => t.time.getTime()), [filteredTaps]
  );

  const timezones = useMemo(() => {
    const timezones: { time: number; name: string }[] = [];
    let prevTimezone: string | null = null;
    [...filteredTaps, ...filteredAudioTaps].sort(
      (a, b) => differenceInMilliseconds(a.time, b.time)
    ).forEach(t => {
      const name = t.timezone === ""
        ? "GMT Universal Coordinated Time"
        : t.timezone;
      if (name !== prevTimezone) {
        timezones.push({ time: t.time.getTime(), name });
        prevTimezone = name;
      }
    });
  return timezones;
  }, [filteredTaps, filteredAudioTaps]);

  const downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = study?.acronym;
    const fileName = format(new Date(), `'${dittiId}_'yyyy-MM-dd'_'HH:mm:ss`);

    const tapsData = filteredTaps.map(t => {
      return [t.dittiId, t.time, t.timezone, "", ""];
    });

    const audioTapsData = filteredAudioTaps.map(t => {
      return [t.dittiId, t.time, t.timezone, t.action, t.audioFileTitle];
    });

    const data = tapsData.concat(audioTapsData).sort((a, b) => {
      if (a[1] > b[1]) return 1;
      else if (a[1] < b[1]) return -1;
      else return 0;
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 },
      { header: "Timezone", width: 30 },
      { header: "Audio Tap Action", width: 15 },
      { header: "Audio File Title", width: 20 },
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";

    // add data to the workbook
    sheet.addRows(data);

    // write the workbook to a blob
    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      // download the blob
      saveAs(blob, fileName + ".xlsx");
    });
  };

  const expTimeDate = studySubject ? new Date(studySubject.expTime) : new Date();
  const expTimeAdjusted = new Date(
    expTimeDate.getTime() - expTimeDate.getTimezoneOffset() * 60000
  );

  const dateOpts = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  };

  const expTimeFormatted = expTimeAdjusted.toLocaleDateString(
    "en-US",
    dateOpts as Intl.DateTimeFormatOptions
  );

  if (loading || studiesLoading || dataLoading || studySubjectLoading) {
    return (
      <ViewContainer>
        <Card>
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      <Card>
        {/* the subject's details */}
        <CardContentRow>
          <div className="flex flex-col">
            <Title>{dittiId}</Title>
            <Subtitle>Expires on: {expTimeFormatted}</Subtitle>
          </div>

          <div className="flex flex-col md:flex-row">
            {/* download the subject's data as excel */}
            <Button
              variant="secondary"
              className="mb-2 md:mb-0 md:mr-2"
              onClick={downloadExcel}
              rounded={true}>
                Download Excel
            </Button>
            {/* if the user can edit, show the edit button */}
            <Link to={`/coordinator/ditti/participants/edit?dittiId=${dittiId}&sid=${studyId}`}>
              <Button
                variant="secondary"
                disabled={!(canEdit || APP_ENV === "demo")}
                rounded={true}>
                  Edit Details
              </Button>
            </Link>
          </div>
        </CardContentRow>

        <VisualizationController
          defaultMargin={{ top: 50, right: 40, bottom: 75, left: 60 }}>
            <TapVisualizationButtons />
            <TimestampHistogram timestamps={timestamps} timezones={timezones} />
            <BoutsTimeline timestamps={timestamps} marginBottom={30} marginTop={30} />
            <AudioTapsTimeline audioTaps={filteredAudioTaps} marginBottom={30} marginTop={30} />
        </VisualizationController>
      </Card>
    </ViewContainer>
  );
};

export default SubjectVisualsV2;
