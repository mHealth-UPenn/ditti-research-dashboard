import { useState, useEffect } from "react";
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
import { Link } from "react-router-dom";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { useStudiesContext } from "../../contexts/studiesContext";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";


/**
 * Fetch the width and height of the current window.
 * @returns { width: number; height: number; }
 */
function getWindowDimensions(): { width: number; height: number; } {
  const { innerWidth: width, innerHeight: height } = window;
  return { width, height };
}


/**
 * Hook for fetching the current window size.
 * @returns { width: number; height: number; }
 */
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


interface IWearableVisualsContentProps {
  dittiId: string;
}


export default function WearableVisualsContent({
  dittiId,
}: IWearableVisualsContentProps) {
  const [canEdit, setCanEdit] = useState(false);
  const [canInvoke, setCanInvoke] = useState(false);
  const [canViewTaps, setCanViewTaps] = useState(false);
  const [loading, setLoading] = useState(true);

  const { isSyncing, syncData } = useWearableData();
  
  const { studySubjectLoading, getStudySubjectByDittiId } = useCoordinatorStudySubjectContext();
  const { studiesLoading, study } = useStudiesContext();
  const { flashMessage } = useFlashMessageContext();

  const studySubject = getStudySubjectByDittiId(dittiId);

  // Use the last `expiresOn` as the date of last data collection
  const endDate = studySubject
    ? new Date(Math.max(...studySubject.studies.map(s => new Date(s.expiresOn).getTime())))
    : new Date();
  const dateOpts: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit"
  };

  const expTimeFormatted = endDate.toLocaleDateString("en-US", dateOpts);

  // Get user access permission on load
  useEffect(() => {
    if (study) {
      const promises: Promise<unknown>[] = [];
      promises.push(getAccess(3, "Edit", "Participants", study.id)
        .then(() => setCanEdit(true)));
      promises.push(getAccess(3, "Invoke", "Data Retrieval Task", study.id)
        .then(() => setCanInvoke(true)));
      promises.push(getAccess(3, "View", "Taps", study.id)
        .then(() => setCanViewTaps(true)));

      Promise.all(promises)
        .then(() => setLoading(false))
        .catch(() => setLoading(false));
    }
  }, [study]);

  // Download the current participant's data in Excel format.
  const downloadExcel = async (): Promise<void> => {
    const url = `/admin/fitbit_data/download/participant/${studySubject?.dittiId}?app=3`;
    const res = await downloadExcelFromUrl(url);
    if (res) {
      flashMessage(<span>{res}</span>, "danger");
    }
  };

  // Custom breakpoint used only for managing certain visx properties
  const { width: windowWidth } = useWindowDimensions();
  const md = windowWidth >= 768;

  if (loading || studiesLoading || studySubjectLoading) {
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
        <CardContentRow>
          <div className="flex flex-grow flex-col lg:flex-row lg:justify-between">

            {/* The participant's details */}
            <div className="flex flex-col mb-4 lg:mb-0">
              <Title>{studySubject?.dittiId}</Title>
              <Subtitle>Expires on: {expTimeFormatted}</Subtitle>
            </div>

            {/* Buttons for downloading Excel data and editing details */}
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
                <Link to={`/coordinator/wearable/participants/edit?dittiId=${studySubject?.dittiId}&sid=${study?.id}`}>
                  <Button
                    variant="secondary"
                    disabled={!(canEdit || APP_ENV === "demo")}
                    rounded={true}>
                      Edit Details
                  </Button>
                </Link>
              </div>

              {/* Button for syncing data and invoking a data processing task */}
              <div className="flex">
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

        {/* The wearable visualization */}
        <CardContentRow>
          <WearableVisualization
            showDayControls={true}
            showTapsData={canViewTaps}
            dittiId={studySubject?.dittiId}
            horizontalPadding={md} />
        </CardContentRow>
      </Card>
    </ViewContainer>
  );
}
