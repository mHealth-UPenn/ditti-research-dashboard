import { useState, useEffect } from "react";
import { Study, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import Subjects from "../dittiApp/subjects";
import SubjectsEdit from "../dittiApp/subjectsEdit";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import CardContentRow from "../cards/cardContentRow";
import { APP_ENV } from "../../environment";
import WearableStudySubjects from "./wearableStudySubjects";

/**
 * Information for study contacts
 */
interface StudyContact {
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
}

/**
 * studyId: the study's database primary key
 */
interface WearableStudySummaryProps extends ViewProps {
  studyId: number;
}

export default function WearableStudySummary({
  flashMessage,
  goBack,
  handleClick,
  studyId
}: WearableStudySummaryProps) {
  const [canCreate, setCanCreate] = useState(false);
  const [canViewWearableData, setCanViewWearableData] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContact[]>([]);
  const [studyDetails, setStudyDetails] = useState<Study>({} as Study);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // check whether the user can enroll new subjects
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(3, "Create", "Users", studyId)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    promises.push(
      getAccess(3, "View", "Wearable Data", studyId)
        .then(() => setCanViewWearableData(true))
        .catch(() => setCanViewWearableData(false))
    );

    // get other accounts that have access to this study
    promises.push(
      makeRequest(
        "/db/get-study-contacts?app=3&study=" + studyId
      ).then((contacts: StudyContact[]) => setStudyContacts(contacts))
    );

    // get this study's information
    promises.push(
      makeRequest(
        "/db/get-study-details?app=3&study=" + studyId
      ).then((details: Study) => setStudyDetails(details))
    );

    // when all promises resolve, hide the loader
    Promise.all(promises).then(() => setLoading(false));
  }, [studyId]);

  /**
   * Download all of the study's data in excel format
   */
  const downloadExcel = async (): Promise<void> => console.log("Download");

  const { dittiId, email, name, acronym } = studyDetails;

  const handleClickEnrollSubject = () =>
    handleClick(
      ["Enroll"],
      <SubjectsEdit
        flashMessage={flashMessage}
        dittiId=""
        goBack={goBack}
        handleClick={handleClick}
        studyId={studyId}
        studyPrefix={dittiId}
        studyEmail={email}
      />
    );

  const handleClickViewAllSubjects = () =>
    handleClick(
      ["Subjects"],
      <Subjects
        flashMessage={flashMessage}
        goBack={goBack}
        handleClick={handleClick}
        studyDetails={studyDetails}
      />
    );

  if (loading) {
    return (
      <ViewContainer>
        <Card width="md">
          <SmallLoader />
        </Card>
        <Card width="sm">
          <SmallLoader />
        </Card>
      </ViewContainer>
    );
  }

  return (
    <ViewContainer>
      <Card width="md">
        <CardContentRow>
          <div className="flex flex-col">
            <Title>{acronym}</Title>
            <Subtitle>{name}</Subtitle>
            <Subtitle>Study email: {email}</Subtitle>
            <Subtitle>Ditti acronym: {dittiId}</Subtitle>
          </div>
          {canViewWearableData &&
            <Button
              onClick={downloadExcel}
              variant="secondary"
              rounded={true}>
                Download Excel
            </Button>}
        </CardContentRow>

        <CardContentRow>
          <Title>Active Subjects</Title>
          <div className="flex">
            {(canCreate || APP_ENV === "demo") &&
              <Button
                className="mr-2"
                onClick={handleClickEnrollSubject}
                rounded={true}>
                  Enroll subject +
              </Button>
            }
            <Button
              variant="secondary"
              onClick={handleClickViewAllSubjects}
              rounded={true}>
                View all subjects
            </Button>
          </div>
        </CardContentRow>

        <WearableStudySubjects
          flashMessage={flashMessage}
          goBack={goBack}
          handleClick={handleClick}
          studyPrefix={dittiId}
          canViewWearableData={canViewWearableData} />
      </Card>

      <Card width="sm">
        {/* list of study contacts */}
        <CardContentRow>
          <Title>Study Contacts</Title>
        </CardContentRow>
        {studyContacts.map((sc: StudyContact, i) => {
          return (
            <CardContentRow key={i}>
              <div>
                <p><b>{sc.fullName}: {sc.role}</b></p>
                <p className="ml-4">{sc.email}</p>
                <p className="ml-4">{sc.phoneNumber}</p>
              </div>
            </CardContentRow>
          );
        })}
      </Card>
    </ViewContainer>
  );
};
