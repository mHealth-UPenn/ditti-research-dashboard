import { useState, useEffect } from "react";
import { Study } from "../../types/api";
import { downloadExcelFromUrl, getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader/loader";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { Card } from "../cards/card";
import { Title } from "../text/title";
import { Subtitle } from "../text/subtitle";
import { Button } from "../buttons/button";
import { CardContentRow } from "../cards/cardContentRow";
import { APP_ENV } from "../../environment";
import { WearableStudySubjects } from "./wearableStudySubjects";
import { useCoordinatorStudySubjects } from "../../hooks/useCoordinatorStudySubjects";
import { Link, useSearchParams } from "react-router-dom";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { StudyContactModel } from "../../types/models";

export function WearableStudySummary() {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;

  const [canCreate, setCanCreate] = useState(false);
  const [canViewWearableData, setCanViewWearableData] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContactModel[]>([]);
  const [studyDetails, setStudyDetails] = useState<Study>({} as Study);
  const [loading, setLoading] = useState(true);

  const { flashMessage } = useFlashMessages();

  // Get permissions and study information on load
  useEffect(() => {
    const promises: Promise<void>[] = [];
    promises.push(
      getAccess(3, "Create", "Participants", studyId)
        .then(() => {
          setCanCreate(true);
        })
        .catch(() => {
          setCanCreate(false);
        })
    );

    promises.push(
      getAccess(3, "View", "Wearable Data", studyId)
        .then(() => {
          setCanViewWearableData(true);
        })
        .catch(() => {
          setCanViewWearableData(false);
        })
    );

    promises.push(
      makeRequest("/db/get-study-contacts?app=3&study=" + String(studyId)).then(
        (contacts: unknown) => {
          setStudyContacts(contacts as StudyContactModel[]);
        }
      )
    );

    promises.push(
      makeRequest("/db/get-study-details?app=3&study=" + String(studyId)).then(
        (details: unknown) => {
          setStudyDetails(details as Study);
        }
      )
    );

    Promise.all(promises)
      .then(() => {
        setLoading(false);
      })
      .catch(console.error);
  }, [studyId]);

  // Download all of the study's data in excel format.
  const downloadExcel = async (): Promise<void> => {
    const url = `/admin/fitbit_data/download/study/${String(studyId)}?app=3`;
    const res = await downloadExcelFromUrl(url);
    if (res) {
      flashMessage(<span>{res}</span>, "danger");
    }
  };

  const { dittiId, email, name, acronym } = studyDetails;
  const { studySubjectLoading } = useCoordinatorStudySubjects();

  if (loading || studySubjectLoading) {
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
        {/* Study information and Excel download button */}
        <CardContentRow>
          <div className="flex flex-col">
            <Title>{acronym}</Title>
            <Subtitle>{name}</Subtitle>
            <Subtitle>Study email: {email}</Subtitle>
            <Subtitle>Ditti acronym: {dittiId}</Subtitle>
          </div>
          {canViewWearableData && (
            <Button
              onClick={() => void downloadExcel()}
              variant="secondary"
              rounded={true}
            >
              Download Excel
            </Button>
          )}
        </CardContentRow>

        {/* Buttons for enrolling and viewing participants */}
        <CardContentRow>
          <Title>Active Subjects</Title>
          <div className="flex">
            {(canCreate || APP_ENV === "demo") && (
              <Link
                to={`/coordinator/wearable/participants/enroll?sid=${String(studyId)}`}
              >
                <Button className="mr-2" rounded={true}>
                  Enroll subject +
                </Button>
              </Link>
            )}
            <Link
              to={`/coordinator/wearable/participants?sid=${String(studyId)}`}
            >
              <Button variant="secondary" rounded={true}>
                View all subjects
              </Button>
            </Link>
          </div>
        </CardContentRow>

        {/* The list of participants in this study */}
        <WearableStudySubjects
          studyDetails={studyDetails}
          canViewWearableData={canViewWearableData}
        />
      </Card>

      {/* The list of study contacts */}
      <Card width="sm">
        {/* list of study contacts */}
        <CardContentRow>
          <Title>Study Contacts</Title>
        </CardContentRow>
        {studyContacts.map((sc: StudyContactModel, i) => {
          return (
            <CardContentRow key={i}>
              <div>
                <p className="mb-0">
                  <b>
                    {sc.fullName}: {sc.role}
                  </b>
                </p>
                <p className="mb-0 ml-4">{sc.email}</p>
                <p className="mb-0 ml-4">{sc.phoneNumber}</p>
              </div>
            </CardContentRow>
          );
        })}
      </Card>
    </ViewContainer>
  );
}
