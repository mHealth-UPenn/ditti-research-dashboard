/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { useState, useEffect } from "react";
import { Study } from "../../types/api";
import { downloadExcelFromUrl, getAccess } from "../../utils";
import { httpClient } from "../../lib/http";
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
      httpClient
        .request<
          StudyContactModel[]
        >(`/db/get-study-contacts?app=3&study=${String(studyId)}`)
        .then((contacts) => {
          setStudyContacts(contacts);
        })
    );

    promises.push(
      httpClient
        .request<Study>(`/db/get-study-details?app=3&study=${String(studyId)}`)
        .then((details) => {
          setStudyDetails(details);
        })
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
