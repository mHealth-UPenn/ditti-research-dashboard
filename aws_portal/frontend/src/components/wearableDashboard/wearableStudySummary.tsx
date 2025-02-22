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

import { useState, useEffect } from "react";
import { Study } from "../../interfaces";
import { downloadExcelFromUrl, getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import CardContentRow from "../cards/cardContentRow";
import { APP_ENV } from "../../environment";
import WearableStudySubjects from "./wearableStudySubjects";
import { useCoordinatorStudySubjectContext } from "../../contexts/coordinatorStudySubjectContext";
import { Link, useSearchParams } from "react-router-dom";
import { useFlashMessageContext } from "../../contexts/flashMessagesContext";


/**
 * Information for study contacts.
 * @property fullName: The contact's full name.
 * @property email: The contact's email.
 * @property phoneNumber: The contact's phone number.
 * @property role: The contact's role.
 */
interface StudyContact {
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
}


export default function WearableStudySummary() {
  const [searchParams] = useSearchParams();
  const sid = searchParams.get("sid");
  const studyId = sid ? parseInt(sid) : 0;

  const [canCreate, setCanCreate] = useState(false);
  const [canViewWearableData, setCanViewWearableData] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContact[]>([]);
  const [studyDetails, setStudyDetails] = useState<Study>({} as Study);
  const [loading, setLoading] = useState(true);

  const { flashMessage } = useFlashMessageContext();

  // Get permissions and study information on load
  useEffect(() => {
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(3, "Create", "Participants", studyId)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    promises.push(
      getAccess(3, "View", "Wearable Data", studyId)
        .then(() => setCanViewWearableData(true))
        .catch(() => setCanViewWearableData(false))
    );

    promises.push(
      makeRequest(
        "/db/get-study-contacts?app=3&study=" + studyId
      ).then((contacts: StudyContact[]) => setStudyContacts(contacts))
    );

    promises.push(
      makeRequest(
        "/db/get-study-details?app=3&study=" + studyId
      ).then((details: Study) => setStudyDetails(details))
    );

    Promise.all(promises).then(() => setLoading(false));
  }, [studyId]);


  // Download all of the study's data in excel format.
  const downloadExcel = async (): Promise<void> => {
    const url = `/admin/fitbit_data/download/study/${studyId}?app=3`;
    const res = await downloadExcelFromUrl(url);
    if (res) {
      flashMessage(<span>{res}</span>, "danger");
    }
  };

  const { dittiId, email, name, acronym } = studyDetails;
  const { studySubjectLoading } = useCoordinatorStudySubjectContext();

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
          {canViewWearableData &&
            <Button
              onClick={downloadExcel}
              variant="secondary"
              rounded={true}>
                Download Excel
            </Button>}
        </CardContentRow>

        {/* Buttons for enrolling and viewing participants */}
        <CardContentRow>
          <Title>Active Subjects</Title>
          <div className="flex">
            {(canCreate || APP_ENV === "demo") &&
              <Link to={`/coordinator/wearable/participants/enroll?sid=${studyId}`}>
                <Button
                  className="mr-2"
                  rounded={true}>
                    Enroll subject +
                </Button>
              </Link>
            }
            <Link to={`/coordinator/wearable/participants?sid=${studyId}`}>
              <Button
                variant="secondary"
                rounded={true}>
                  View all subjects
              </Button>
            </Link>
          </div>
        </CardContentRow>

        {/* The list of participants in this study */}
        <WearableStudySubjects
          studyDetails={studyDetails}
          canViewWearableData={canViewWearableData} />
      </Card>

      {/* The list of study contacts */}
      <Card width="sm">
        {/* list of study contacts */}
        <CardContentRow>
          <Title>Study Contacts</Title>
        </CardContentRow>
        {studyContacts.map((sc: StudyContact, i) => {
          return (
            <CardContentRow key={i}>
              <div>
                <p className="mb-0"><b>{sc.fullName}: {sc.role}</b></p>
                <p className="ml-4 mb-0">{sc.email}</p>
                <p className="ml-4 mb-0">{sc.phoneNumber}</p>
              </div>
            </CardContentRow>
          );
        })}
      </Card>
    </ViewContainer>
  );
}
