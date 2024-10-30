import React, { useState, useEffect, useCallback } from "react";
import { AudioTapDetails, Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import TextField from "../fields/textField";
import SubjectsEdit from "./subjectsEdit";
import { ReactComponent as Left } from "../../icons/arrowLeft.svg";
import { ReactComponent as Right } from "../../icons/arrowRight.svg";
import { ReactComponent as ZoomIn } from "../../icons/zoomIn.svg";
import { ReactComponent as ZoomOut } from "../../icons/zoomOut.svg";
import {
  add,
  differenceInMinutes,
  differenceInMilliseconds,
  format,
  isWithinInterval,
  sub
} from "date-fns";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import "./subjectVisuals.css";
import { getAccess } from "../../utils";
import { SmallLoader } from "../loader";
import TimestampHistogram from "./TimestampHistogram";

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
  const [start, setStart] = useState(sub(new Date(new Date().setHours(9, 0, 0, 0)), { hours: 24 }));
  const [stop, setStop] = useState(new Date(new Date().setHours(9, 0, 0, 0)));
  const [taps, setTaps] = useState(() => getTaps().filter((t) => t.dittiId === user.userPermissionId));
  const [audioTaps, setAudioTaps] = useState(() => getAudioTaps().filter((t) => t.dittiId === user.userPermissionId));
  const [loading, setLoading] = useState(true);

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
  }, [studyDetails.id, taps]);

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
    <div className="card-container">
      <div className="card-row">
        <div className="card-l bg-white shadow">
          {loading ? (
            <SmallLoader />
          ) : (
            <React.Fragment>

              {/* the subject's details */}
              <div className="subject-header">
                <div className="card-title flex-space">
                  <span>{user.userPermissionId}</span>

                  {/* download the subject's data as excel */}
                  <button
                    className="button-primary button-lg"
                    style={{ width: "12rem" }}
                    onClick={downloadExcel}
                  >
                    Download Excel
                  </button>
                </div>
                <div className="subject-header-info">
                  <div>
                    Expires on: <b>{expTimeFormatted}</b>
                  </div>

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
                      style={{ width: "12rem" }}
                    >
                      Edit Details
                    </button>
                  ) : null}
                </div>
              </div>

              <TimestampHistogram timestamps={getTaps().map(t => t.time.getTime())} />
            </React.Fragment>
          )}
        </div>
      </div>
    </div>
  );
};

export default SubjectVisualsV2;
