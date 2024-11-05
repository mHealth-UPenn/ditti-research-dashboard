import React, { useState, useEffect } from "react";
import { AudioTapDetails, Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import StudySubjects from "./studySubjects";
import "./studySummary.css";
import Subjects from "./subjects";
import SubjectsEdit from "./subjectsEdit";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import { format } from "date-fns";
import ViewContainer from "../containers/viewContainer";
import Card from "../cards/card";
import Title from "../cards/cardTitle";
import Subtitle from "../cards/cardSubtilte";
import Button from "../buttons/button";
import CardContentRow from "../cards/cardHeader";

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
 * getTaps: get tap data
 * studyId: the study's database primary key
 */
interface StudySummaryProps extends ViewProps {
  getTaps: () => TapDetails[];
  getAudioTaps: () => AudioTapDetails[];
  studyId: number;
}

const StudySummary: React.FC<StudySummaryProps> = ({
  flashMessage,
  getTaps,
  getAudioTaps,  // TODO: implement into excel download
  goBack,
  handleClick,
  studyId
}) => {
  const [canCreate, setCanCreate] = useState(false);
  const [canViewTaps, setCanViewTaps] = useState(false);
  const [studyContacts, setStudyContacts] = useState<StudyContact[]>([]);
  const [studyDetails, setStudyDetails] = useState<Study>({} as Study);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // check whether the user can enroll new subjects
    const promises: Promise<any>[] = [];
    promises.push(
      getAccess(2, "Create", "Users", studyId)
        .then(() => setCanCreate(true))
        .catch(() => setCanCreate(false))
    );

    promises.push(
      getAccess(2, "View", "Taps", studyId)
        .then(() => setCanViewTaps(true))
        .catch(() => setCanViewTaps(false))
    );

    // get other accounts that have access to this study
    promises.push(
      makeRequest(
        "/db/get-study-contacts?app=2&study=" + studyId
      ).then((contacts: StudyContact[]) => setStudyContacts(contacts))
    );

    // get this study's information
    promises.push(
      makeRequest(
        "/db/get-study-details?app=2&study=" + studyId
      ).then((details: Study) => setStudyDetails(details))
    );

    // when all promises resolve, hide the loader
    Promise.all(promises).then(() => setLoading(false));
  }, [studyId]);

  /**
   * Download all of the study's data in excel format
   */
  const downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const taps = getTaps();
    const id = studyDetails.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);

    // localize tap timestamps
    const data = taps.map((t) => {
      const time = t.time.getTime() - t.time.getTimezoneOffset() * 60000;
      return [t.dittiId, new Date(time)];
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 }
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

  const { dittiId, email, name } = studyDetails;

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
        getTaps={getTaps}
        getAudioTaps={getAudioTaps}
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
            <Title>{name}</Title>
            <Subtitle>Study email: {email}</Subtitle>
            <Subtitle>Ditti acronym: {dittiId}</Subtitle>
          </div>
          {canViewTaps && <Button onClick={downloadExcel}>Download Excel</Button>}
        </CardContentRow>

        <CardContentRow>
          <Title>Active Subjects</Title>
          <div className="flex">
            {canCreate &&
              <Button
                className="mr-2"
                onClick={handleClickEnrollSubject}>
                  Enroll subject +
              </Button>
            }
            <Button
              variant="secondary"
              onClick={handleClickViewAllSubjects}>
                View all subjects
            </Button>
          </div>
        </CardContentRow>

        <StudySubjects
          flashMessage={flashMessage}
          goBack={goBack}
          getTaps={getTaps}
          getAudioTaps={getAudioTaps}
          handleClick={handleClick}
          studyDetails={studyDetails}
          studyPrefix={dittiId}
          canViewTaps={canViewTaps} />
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

export default StudySummary;
