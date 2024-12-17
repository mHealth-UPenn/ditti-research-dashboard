import React, { useState, useEffect } from "react";
import { IStudySubject, Study, ViewProps } from "../../interfaces";
import { downloadExcelFromUrl, getAccess } from "../../utils";
import { SmallLoader } from "../loader";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import CardContentRow from "../cards/cardContentRow";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import { APP_ENV } from "../../environment";
import { useWearableData } from "../../contexts/wearableDataContext";
import WearableVisualization from "../visualizations/wearableVisualization";
import SyncIcon from '@mui/icons-material/Sync';


function getWindowDimensions() {
  const { innerWidth: width, innerHeight: height } = window;
  return {
    width,
    height
  };
}


function useWindowDimensions() {
  const [windowDimensions, setWindowDimensions] = useState(getWindowDimensions());

  useEffect(() => {
    function handleResize() {
      setWindowDimensions(getWindowDimensions());
    }

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  return windowDimensions;
}


/**
 * getTaps: get tap data
 * studyDetails: details of the subject's study
 * user: details of the subject
 */
interface WearableVisualsProps extends ViewProps {
  studyDetails: Study;
  studySubject: IStudySubject;
}

export default function WearableVisuals({
  studyDetails,
  studySubject,
  flashMessage,
  goBack,
  handleClick
}: WearableVisualsProps) {
  const [canEdit, setCanEdit] = useState(false);
  const [canInvoke, setCanInvoke] = useState(false);
  const [loading, setLoading] = useState(true);

  const { isSyncing, syncData } = useWearableData();

  const scope = [...(new Set(studySubject.apis.map(api => api.scope).flat()))];
  const endDate = new Date(Math.max(...studySubject.studies.map(s => new Date(s.expiresOn).getTime())));
  const expTimeAdjusted = new Date(
    endDate.getTime() - endDate.getTimezoneOffset() * 60000
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

  useEffect(() => {
    const promises: Promise<unknown>[] = [];
    promises.push(getAccess(3, "Edit", "Users", studyDetails.id)
      .then(() => setCanEdit(true)));
    promises.push(getAccess(3, "Invoke", "Data Retrieval Task", studyDetails.id)
      .then(() => setCanInvoke(true)));

    Promise.all(promises)
      .then(() => setLoading(false))
      .catch(() => setLoading(false));
  }, [studyDetails.id]);

  const downloadExcel = async (): Promise<void> => {
    const url = `/admin/fitbit_data/download/participant/${studySubject.dittiId}?app=3`;
    const res = await downloadExcelFromUrl(url);
    if (res) {
      flashMessage(<span>{res}</span>, "danger");
    }
  };

  const handleClickEditDetails = () =>
    handleClick(
      ["Edit"],
      <React.Fragment />
      // <SubjectsEdit
      //   dittiId={user.userPermissionId}
      //   studyId={studyDetails.id}
      //   studyEmail={studyDetails.email}
      //   studyPrefix={studyDetails.dittiId}
      //   flashMessage={flashMessage}
      //   goBack={goBack}
      //   handleClick={handleClick}
      // />
    );

  // Custom breakpoint used only for managing certain visx properties
  const { width: windowWidth } = useWindowDimensions();
  const md = windowWidth >= 768;

  if (loading) {
    return (
      <ViewContainer>
        <Card width="lg">
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
          <div className="flex flex-grow flex-col lg:flex-row lg:justify-between">
            <div className="flex flex-col mb-4 lg:mb-0">
              <Title>{studySubject.dittiId}</Title>
              <Subtitle>Expires on: {expTimeFormatted}</Subtitle>
            </div>

            <div className="flex flex-col lg:flex-row">
              <div className="flex mb-2 lg:mb-0 lg:mr-2">
                {/* download the subject's data as excel */}
                <Button
                  variant="secondary"
                  className="mr-2"
                  onClick={downloadExcel}
                  rounded={true}>
                    Download Excel
                </Button>
                {/* if the user can edit, show the edit button */}
                <Button
                  variant="secondary"
                  onClick={handleClickEditDetails}
                  disabled={!(canEdit || APP_ENV === "demo")}
                  rounded={true}>
                  Edit Details
                </Button>
              </div>
              <div className="flex">
                {/* download the subject's data as excel */}
                <Button
                  variant="secondary"
                  onClick={syncData}
                  rounded={true}
                  disabled={isSyncing || !canInvoke}>
                    <span className="mr-2">
                      {isSyncing && canInvoke ? "Data Syncing..." : "Sync Data"}
                    </span>
                    <SyncIcon
                      className={isSyncing && canInvoke ? "animate-spin-reverse-slow" : ""} />
                </Button>
              </div>
            </div>
          </div>
        </CardContentRow>

        <CardContentRow>
          <WearableVisualization showDayControls={true} horizontalPadding={md} />
        </CardContentRow>
      </Card>
    </ViewContainer>
  );
}
