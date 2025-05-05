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
import { Study, ResponseBody } from "../../types/api";
import { httpClient } from "../../lib/http";
import { SmallLoader } from "../loader/loader";
import { StudySubjects } from "./studySubjects";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import { format } from "date-fns";
import { ViewContainer } from "../containers/viewContainer/viewContainer";
import { Card } from "../cards/card";
import { Title } from "../text/title";
import { Subtitle } from "../text/subtitle";
import { Button } from "../buttons/button";
import { CardContentRow } from "../cards/cardContentRow";
import { useDittiData } from "../../hooks/useDittiData";
import { APP_ENV } from "../../environment";
import { Link } from "react-router-dom";
import { useStudies } from "../../hooks/useStudies";
import { StudyContactModel } from "../../types/models";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useApiHandler } from "../../hooks/useApiHandler";

export const StudySummary = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canViewTaps, setCanViewTaps] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContactModel[]>([]);

  const { studiesLoading, study } = useStudies();
  const { dataLoading, taps, audioTaps } = useDittiData();
  const { flashMessage } = useFlashMessages();

  const {
    safeRequest: safeFetchComponentData,
    isLoading: isLoadingComponentData,
  } = useApiHandler<{
    permissions: { create: boolean; viewTaps: boolean };
    contacts: StudyContactModel[];
  }>({
    errorMessage: "Failed to load study permissions or contacts.",
    showDefaultSuccessMessage: false,
  });

  useEffect(() => {
    if (study) {
      const initialFetch = async () => {
        const fetchedData = await safeFetchComponentData(async () => {
          const checkPermission = async (
            appId: number,
            action: string,
            resource: string,
            studyId: number
          ): Promise<boolean> => {
            const url = `/auth/researcher/get-access?app=${String(appId)}&action=${action}&resource=${resource}&study=${String(studyId)}`;
            try {
              const res = await httpClient.request<ResponseBody>(url);
              return res.msg === "Authorized";
            } catch {
              return false;
            }
          };

          const dittiAppId = 2; // Ditti App = 2
          const createPerm = checkPermission(
            dittiAppId,
            "Create",
            "Participants",
            study.id
          );
          const viewTapsPerm = checkPermission(
            dittiAppId,
            "View",
            "Taps",
            study.id
          );
          const contactsReq = httpClient.request<StudyContactModel[]>(
            `/db/get-study-contacts?app=${String(dittiAppId)}&study=${String(study.id)}`
          );

          const [canCreateRes, canViewTapsRes, contactsRes] = await Promise.all(
            [createPerm, viewTapsPerm, contactsReq]
          );

          return {
            permissions: { create: canCreateRes, viewTaps: canViewTapsRes },
            contacts: contactsRes,
          };
        });

        if (fetchedData) {
          setCanCreate(fetchedData.permissions.create);
          setCanViewTaps(fetchedData.permissions.viewTaps);
          setStudyContacts(fetchedData.contacts);
        } else {
          // Reset state on error (error message shown by hook)
          setCanCreate(false);
          setCanViewTaps(false);
          setStudyContacts([]);
        }
      };
      void initialFetch();
    }
  }, [study, safeFetchComponentData]);

  /**
   * Download all of the study's data in excel format
   */
  const downloadExcel = () => {
    if (!study) {
      return;
    }

    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = study.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);

    const tapsData = taps
      .filter((t) =>
        // Retrieve taps from only the current study
        t.dittiId.startsWith(study.dittiId)
      )
      .map((t) => {
        return [t.dittiId, t.time, t.timezone, "", ""];
      });

    const audioTapsData = audioTaps
      .filter((t) =>
        // Retrieve taps from only the current study
        t.dittiId.startsWith(study.dittiId)
      )
      .map((t) => {
        return [t.dittiId, t.time, t.timezone, t.action, t.audioFileTitle];
      });

    const data = tapsData
      .concat(audioTapsData)
      .sort((a, b) => {
        // Ensure dates are compared correctly
        const dateA = a[1] instanceof Date ? a[1].getTime() : 0;
        const dateB = b[1] instanceof Date ? b[1].getTime() : 0;
        return dateA - dateB;
      })
      .sort((a, b) => {
        // Sort by Ditti ID as secondary key
        const idA = typeof a[0] === "string" ? a[0] : "";
        const idB = typeof b[0] === "string" ? b[0] : "";
        return idA.localeCompare(idB);
      });

    sheet.columns = [
      { header: "Ditti ID", width: 10, key: "dittiId" },
      {
        header: "Taps",
        width: 20,
        key: "time",
        style: { numFmt: "mm/dd/yyyy hh:mm:ss" },
      },
      { header: "Timezone", width: 30, key: "timezone" },
      { header: "Audio Tap Action", width: 15, key: "action" },
      { header: "Audio File Title", width: 20, key: "audioFileTitle" },
    ];

    // Add data to the workbook
    sheet.addRows(data);

    // write the workbook to a blob
    void workbook.xlsx
      .writeBuffer()
      .then((buffer) => {
        const blob = new Blob([buffer], {
          type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        });
        // download the blob
        saveAs(blob, `${fileName}.xlsx`);
      })
      // Explicitly type the caught error as unknown
      .catch((err: unknown) => {
        console.error("Error generating Excel file:", err);
        // Use flashMessage directly for client-side error
        const message = err instanceof Error ? err.message : "Unknown error";
        flashMessage(
          <span>Failed to generate Excel file: {message}</span>,
          "danger"
        );
      });
  };

  // Combine all loading states
  const combinedLoading =
    isLoadingComponentData || studiesLoading || dataLoading;

  if (combinedLoading) {
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
            <Title>{study?.acronym}</Title>
            <Subtitle>{study?.name}</Subtitle>
            <Subtitle>Study email: {study?.email}</Subtitle>
            <Subtitle>Ditti acronym: {study?.dittiId}</Subtitle>
          </div>
          {canViewTaps && (
            <Button onClick={downloadExcel} variant="secondary" rounded={true}>
              Download Excel
            </Button>
          )}
        </CardContentRow>

        <CardContentRow>
          <Title>Active Subjects</Title>
          <div className="flex">
            {(canCreate || APP_ENV === "demo") && (
              <Link
                to={`/coordinator/ditti/participants/enroll?sid=${study?.id ? String(study.id) : ""}`}
              >
                <Button className="mr-2" rounded={true}>
                  Enroll subject +
                </Button>
              </Link>
            )}
            <Link
              to={`/coordinator/ditti/participants?sid=${study?.id ? String(study.id) : ""}`}
            >
              <Button variant="secondary" rounded={true}>
                View all subjects
              </Button>
            </Link>
          </div>
        </CardContentRow>

        <StudySubjects
          study={study ?? ({} as Study)}
          canViewTaps={canViewTaps}
        />
      </Card>

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
};
