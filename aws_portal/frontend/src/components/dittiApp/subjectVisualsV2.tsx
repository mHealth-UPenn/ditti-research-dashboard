import React, { useState, useEffect, useMemo } from "react";
import { AudioTapDetails, Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import SubjectsEdit from "./subjectsEdit";
import { format } from "date-fns";
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
import CardContentRow from "../cards/cardHeader";
import Title from "../cards/cardTitle";
import Subtitle from "../cards/cardSubtilte";
import Button from "../buttons/button";

/**
 * getTaps: get tap data
 * studyDetails: details of the subject's study
 * user: details of the subject
 */
interface SubjectVisualsV2Props extends ViewProps {
  getTaps: () => TapDetails[];
  getAudioTaps: () => AudioTapDetails[];
  studyDetails: Study;
  user: UserDetails;
}

const SubjectVisualsV2: React.FC<SubjectVisualsV2Props> = ({
  getTaps,
  getAudioTaps,
  studyDetails,
  user,
  flashMessage,
  goBack,
  handleClick
}) => {
  const [canEdit, setCanEdit] = useState(false);
  const [loading, setLoading] = useState(true);

  const taps = getTaps().filter((t) => t.dittiId === user.userPermissionId);
  const audioTaps = getAudioTaps().filter((at) => at.dittiId === user.userPermissionId);

  useEffect(() => {
    getAccess(2, "Edit", "Users", studyDetails.id)
      .then(() => {
        setCanEdit(true);
        setLoading(false);
      })
      .catch(() => {
        setCanEdit(false);
        setLoading(false);
      });
  }, [studyDetails.id]);

  const downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = user.userPermissionId;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);
    const data = taps.map((t) => {
      // localize tap timestamps
      const time = t.time.getTime() - t.time.getTimezoneOffset() * 60000;
      return [t.dittiId, new Date(time)];
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 }
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";
    sheet.addRows(data);

    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      // download the excel file
      saveAs(blob, fileName + ".xlsx");
    });
  };

  const expTimeDate = new Date(user.expTime);
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

  const timestamps = useMemo(
    () => getTaps().map(t => t.time.getTime()), [getTaps]
  );

  const handleClickEditDetails = () =>
    handleClick(
      ["Edit"],
      <SubjectsEdit
        dittiId={user.userPermissionId}
        studyId={studyDetails.id}
        studyEmail={studyDetails.email}
        studyPrefix={studyDetails.dittiId}
        flashMessage={flashMessage}
        goBack={goBack}
        handleClick={handleClick}
      />
    );

  if (loading) {
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
            <Title>{user.userPermissionId}</Title>
            <Subtitle>Expires on: {expTimeFormatted}</Subtitle>
          </div>

          <div className="flex flex-col md:flex-row">
            {/* download the subject's data as excel */}
            <Button
              variant="secondary"
              className="mb-2 md:mb-0 md:mr-2"
              onClick={downloadExcel}>
                Download Excel
            </Button>
            {/* if the user can edit, show the edit button */}
            {canEdit &&
              <Button variant="secondary" onClick={handleClickEditDetails}>
                Edit Details
              </Button>
            }
          </div>
        </CardContentRow>

        <VisualizationController>
          <TapVisualizationButtons />
          <TimestampHistogram timestamps={timestamps} />
          <BoutsTimeline timestamps={timestamps} />
          <AudioTapsTimeline audioTaps={audioTaps} />
        </VisualizationController>
      </Card>
    </ViewContainer>
  );
};

export default SubjectVisualsV2;
