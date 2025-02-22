/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { useState, useEffect } from "react";
import { Study } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import StudySubjects from "./studySubjects";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import { format } from "date-fns";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Title from "../text/title";
import Subtitle from "../text/subtitle";
import Button from "../buttons/button";
import CardContentRow from "../cards/cardContentRow";
import { useDittiDataContext } from "../../contexts/dittiDataContext";
import { APP_ENV } from "../../environment";
import { Link } from "react-router-dom";
import { useStudiesContext } from "../../contexts/studiesContext";

/**
 * Information for study contacts
 */
interface StudyContact {
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
}

const StudySummary = () => {
  const [canCreate, setCanCreate] = useState(false);
  const [canViewTaps, setCanViewTaps] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContact[]>([]);
  const [loading, setLoading] = useState(true);

  const { studiesLoading, study } = useStudiesContext();
  const { dataLoading, taps, audioTaps } = useDittiDataContext();

  useEffect(() => {
    if (study) {
      // check whether the user can enroll new subjects
      const promises: Promise<any>[] = [];
      promises.push(
        getAccess(2, "Create", "Participants", study.id)
          .then(() => setCanCreate(true))
          .catch(() => setCanCreate(false))
      );

      promises.push(
        getAccess(2, "View", "Taps", study.id)
          .then(() => setCanViewTaps(true))
          .catch(() => setCanViewTaps(false))
      );

      // get other accounts that have access to this study
      promises.push(
        makeRequest(
          "/db/get-study-contacts?app=2&study=" + study.id
        ).then((contacts: StudyContact[]) => setStudyContacts(contacts))
      );

      // when all promises resolve, hide the loader
      Promise.all(promises).then(() => setLoading(false));
    }
  }, [study]);

  /**
   * Download all of the study's data in excel format
   */
  const downloadExcel = async (): Promise<void> => {
    if (!study) {
      return;
    }

    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const id = study.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);

    const tapsData = taps.filter(t =>
      // Retrieve taps from only the current study
      t.dittiId.startsWith(study.dittiId)
    ).map(t => {
      return [t.dittiId, t.time, t.timezone, "", ""];
    });

    const audioTapsData = audioTaps.filter(t =>
      // Retrieve taps from only the current study
      t.dittiId.startsWith(study.dittiId)
    ).map(t => {
      return [t.dittiId, t.time, t.timezone, t.action, t.audioFileTitle];
    });

    const data = tapsData.concat(audioTapsData).sort((a, b) => {
      if (a[1] > b[1]) return 1;
      else if (a[1] < b[1]) return -1;
      else return 0;
    }).sort((a, b) => {
      if (a[0] > b[0]) return 1;
      else if (a[0] < b[0]) return -1;
      else return 0;
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 },
      { header: "Timezone", width: 30 },
      { header: "Audio Tap Action", width: 15 },
      { header: "Audio File Title", width: 20 },
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";

    // add data to the workbook
    sheet.addRows(data);

    // write the workbook to a blob
    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      // download the blob
      saveAs(blob, fileName + ".xlsx");
    });
  };

  if (loading || studiesLoading || dataLoading) {
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
          {canViewTaps &&
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
              <Link to={`/coordinator/ditti/participants/enroll?sid=${study?.id}`}>
                <Button
                  className="mr-2"
                  rounded={true}>
                    Enroll subject +
                </Button>
              </Link>
            }
            <Link to={`/coordinator/ditti/participants?sid=${study?.id}`}>
              <Button
                variant="secondary"
                rounded={true}>
                  View all subjects
              </Button>
            </Link>
          </div>
        </CardContentRow>

        <StudySubjects study={study || {} as Study} canViewTaps={canViewTaps} />
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
};

export default StudySummary;
