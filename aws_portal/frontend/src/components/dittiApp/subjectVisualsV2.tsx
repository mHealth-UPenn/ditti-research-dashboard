import React, { useState, useEffect } from "react";
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

  return (
    <div className="bg-white md:bg-[transparent] max-h-[calc(calc(100vh-8rem)-1px)] overflow-scroll overflow-x-hidden">
      <div className="bg-white p-8 md:mx-8 md:my-16 md:shadow-lg lg:mx-16">
        {loading ? (
          <SmallLoader />
        ) : (
          <React.Fragment>

            {/* the subject's details */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <div className="flex flex-col">
                  <span className="text-2xl font-bold">{user.userPermissionId}</span>
                  <span>
                    Expires on: <b>{expTimeFormatted}</b>
                  </span>
                </div>

                <div className="flex flex-col">
                  {/* download the subject's data as excel */}
                  <button
                    className="button-primary button-lg mb-2"
                    style={{ width: "12rem" }}
                    onClick={downloadExcel}
                  >
                    Download Excel
                  </button>
                  {/* if the user can edit, show the edit button */}
                  {canEdit ? (
                    <button
                      className="button-secondary button-lg"
                      onClick={() =>
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
                        )
                      }
                    >
                      Edit Details
                    </button>
                  ) : null}
                </div>
              </div>
            </div>

            <VisualizationController>
              <TapVisualizationButtons />
              <TimestampHistogram timestamps={getTaps().map(t => t.time.getTime())} />
            </VisualizationController>
          </React.Fragment>
        )}
      </div>
    </div>
  );
};

export default SubjectVisualsV2;
