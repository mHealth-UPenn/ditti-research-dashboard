import { useState, useEffect } from "react";
import { IStudySubject, Study, UserDetails, ViewProps } from "../../interfaces";
import SubjectsEdit from "../dittiApp/subjectsEdit";
import { downloadExcelFromUrl, getAccess } from "../../utils";
import { SmallLoader } from "../loader";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import CardContentRow from "../cards/cardContentRow";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import { APP_ENV } from "../../environment";
import { CoordinatorWearableDataProvider } from "../../contexts/wearableDataContext";
import WearableVisualization from "../visualizations/wearableVisualization";

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
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getAccess(3, "Edit", "Users", studyDetails.id)
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
    const url = `/admin/fitbit_data/download/participant/${studySubject.dittiId}?app=3`;
    const res = await downloadExcelFromUrl(url);
    if (res) {
      flashMessage(<span>{res}</span>, "danger");
    }
  };

  // TODO: Update this to pull from join table instead
  // const expTimeDate = new Date(user.expTime);
  // const expTimeAdjusted = new Date(
  //   expTimeDate.getTime() - expTimeDate.getTimezoneOffset() * 60000
  // );

  // const dateOpts = {
  //   year: "numeric",
  //   month: "short",
  //   day: "numeric",
  //   hour: "numeric",
  //   minute: "2-digit"
  // };

  // const expTimeFormatted = expTimeAdjusted.toLocaleDateString(
  //   "en-US",
  //   dateOpts as Intl.DateTimeFormatOptions
  // );

  // const handleClickEditDetails = () =>
  //   handleClick(
  //     ["Edit"],
  //     <SubjectsEdit
  //       dittiId={user.userPermissionId}
  //       studyId={studyDetails.id}
  //       studyEmail={studyDetails.email}
  //       studyPrefix={studyDetails.dittiId}
  //       flashMessage={flashMessage}
  //       goBack={goBack}
  //       handleClick={handleClick}
  //     />
  //   );

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
            <Title>{studySubject.dittiId}</Title>
            {/* <Subtitle>Expires on: {expTimeFormatted}</Subtitle> */}
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
            {/* <Button
              variant="secondary"
              onClick={handleClickEditDetails}
              disabled={!(canEdit || APP_ENV === "demo")}
              rounded={true}>
              Edit Details
            </Button> */}
          </div>
        </CardContentRow>

        <CardContentRow>
            <CoordinatorWearableDataProvider dittiId={studySubject.dittiId}>
              <WearableVisualization />
            </CoordinatorWearableDataProvider>
          </CardContentRow>
      </Card>
    </ViewContainer>
  );
}
