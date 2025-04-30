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

import { useState, useEffect, useMemo } from "react";
import { differenceInMilliseconds, format } from "date-fns";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import "./subjectVisuals.css";
import { getAccess, getEnrollmentInfoForStudy } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { TimestampHistogram } from "../visualizations/timestampHistogram";
import { TapVisualizationButtons } from "../visualizations/tapVisualizationButtons";
import { BoutsTimeline } from "../visualizations/boutsTimeline";
import { AudioTapsTimeline } from "../visualizations/audioTapsTimeline";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { Card } from "../cards/card";
import { CardContentRow } from "../cards/cardContentRow";
import { Title } from "../text/title";
import { Subtitle } from "../text/subtitle";
import { Button } from "../buttons/button";
import { useDittiData } from "../../hooks/useDittiData";
import { APP_ENV } from "../../environment";
import { Link, useSearchParams } from "react-router-dom";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { useStudies } from "../../hooks/useStudies";
import { VisualizationContextProvider } from "../../contexts/visualizationContext";

export const SubjectVisualsV2 = () => {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;
  const dittiId = searchParams.get("dittiId") || "";

  const [canEdit, setCanEdit] = useState(false);
  const [loading, setLoading] = useState(true);

  const { dataLoading, taps, audioTaps } = useDittiData();
  const { studiesLoading, study } = useStudies();
  const { studySubjectLoading, getStudySubjectByDittiId } =
    useCoordinatorStudySubjects();

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
  const { expiresOn } = getEnrollmentInfoForStudy(studySubject, study?.id);
  const filteredTaps = taps.filter((t) => t.dittiId === dittiId);
  const filteredAudioTaps = audioTaps.filter((at) => at.dittiId === dittiId);

  const timestamps = useMemo(
    () => filteredTaps.map((t) => t.time.getTime()),
    [filteredTaps]
  );

  const timezones = useMemo(() => {
    const timezones: { time: number; name: string }[] = [];
    let prevTimezone: string | null = null;
    [...filteredTaps, ...filteredAudioTaps]
      .sort((a, b) => differenceInMilliseconds(a.time, b.time))
      .forEach((t) => {
        const name =
          t.timezone === "" ? "GMT Universal Coordinated Time" : t.timezone;
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
    const fileName = format(new Date(), `'${dittiId}_'yyyy-MM-dd'_'HH:mm:ss`);

    const tapsData = filteredTaps.map((t) => {
      return [t.dittiId, t.time, t.timezone, "", ""];
    });

    const audioTapsData = filteredAudioTaps.map((t) => {
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
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });

      // download the blob
      saveAs(blob, fileName + ".xlsx");
    });
  };

  const dateOpts: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
  };

  const expTime = new Date(expiresOn).toLocaleDateString("en-US", dateOpts);

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
            <Subtitle>Enrollment ends on: {expTime}</Subtitle>
          </div>

          <div className="flex flex-col md:flex-row">
            {/* download the subject's data as excel */}
            <Button
              variant="secondary"
              className="mb-2 md:mb-0 md:mr-2"
              onClick={downloadExcel}
              rounded={true}
            >
              Download Excel
            </Button>
            {/* if the user can edit, show the edit button */}
            <Link
              to={`/coordinator/ditti/participants/edit?dittiId=${dittiId}&sid=${studyId}`}
            >
              <Button
                variant="secondary"
                disabled={!(canEdit || APP_ENV === "demo")}
                rounded={true}
              >
                Edit Details
              </Button>
            </Link>
          </div>
        </CardContentRow>

        <VisualizationContextProvider
          defaultMargin={{ top: 50, right: 40, bottom: 75, left: 60 }}
        >
          <TapVisualizationButtons />
          <TimestampHistogram timestamps={timestamps} timezones={timezones} />
          <BoutsTimeline
            timestamps={timestamps}
            marginBottom={30}
            marginTop={30}
          />
          <AudioTapsTimeline
            audioTaps={filteredAudioTaps}
            marginBottom={30}
            marginTop={30}
          />
        </VisualizationContextProvider>
      </Card>
    </ViewContainer>
  );
};
