import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import StudySubjects from "./studySubjects";
import "./studySummary.css";
import Subjects from "./subjects";
import SubjectsEdit from "./subjectsEdit";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import { format } from "date-fns";

interface StudyContact {
  fullName: string;
  email: string;
  phoneNumber: string;
  role: string;
}

interface StudySummaryProps extends ViewProps {
  getTaps: () => TapDetails[];
  studyId: number;
}

interface StudySummaryState {
  studyContacts: StudyContact[];
  studyDetails: Study;
  loading: boolean;
}

class StudySummary extends React.Component<
  StudySummaryProps,
  StudySummaryState
> {
  state = {
    studyContacts: [],
    studyDetails: {} as Study,
    loading: true
  };

  componentDidMount() {
    const { studyId } = this.props;

    const studyContacts = makeRequest(
      "/db/get-study-contacts?app=2&study=" + studyId
    ).then((studyContacts: StudyContact[]) => this.setState({ studyContacts }));

    const studyDetails = makeRequest(
      "/db/get-study-details?app=2&study=" + studyId
    ).then((studyDetails: Study) => this.setState({ studyDetails }));

    Promise.all([studyContacts, studyDetails]).then(() =>
      this.setState({ loading: false })
    );
  }

  downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const taps = this.props.getTaps();
    const id = this.state.studyDetails.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);
    const data = taps.map((t) => {
      const time = t.time.getTime() - t.time.getTimezoneOffset() * 60000;
      return [t.dittiId, new Date(time)];
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 }
    ];

    sheet.getColumn("B").numFmt = "DD/MM/YYYY HH:mm:ss";
    sheet.addRows(data);

    workbook.xlsx.writeBuffer().then((data) => {
      const blob = new Blob([data], {
        type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      });

      saveAs(blob, fileName + ".xlsx");
    });
  };

  render() {
    const { flashMessage, getTaps, goBack, handleClick, studyId } = this.props;
    const { loading, studyContacts, studyDetails } = this.state;
    const { dittiId, email, name } = studyDetails;

    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            {loading ? (
              <SmallLoader />
            ) : (
              <div>
                <div className="card-header">
                  <div className="card-title flex-space">
                    <span>{name}</span>
                    <button
                      className="button-primary button-lg"
                      onClick={this.downloadExcel}
                      style={{ width: "12rem" }}
                    >
                      Download Excel
                    </button>
                  </div>
                  <span>
                    Study email: <b>{email}</b>
                  </span>
                  <br />
                  <span>
                    Ditti acronym: <b>{dittiId}</b>
                  </span>
                </div>
                <div className="study-subjects">
                  <div className="study-subjects-header">
                    <div className="study-subjects-title">Active Subjects</div>
                    <div className="study-subjects-buttons">
                      <button
                        className="button-primary"
                        onClick={() =>
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
                            />,
                            false
                          )
                        }
                      >
                        Enroll subject +
                      </button>
                      <button
                        className="button-secondary"
                        onClick={() =>
                          handleClick(
                            ["Subjects"],
                            <Subjects
                              flashMessage={flashMessage}
                              goBack={goBack}
                              handleClick={handleClick}
                              studyDetails={this.state.studyDetails}
                            />,
                            false
                          )
                        }
                      >
                        View all subjects
                      </button>
                    </div>
                  </div>
                  <div className="study-subjects-list">
                    <StudySubjects
                      flashMessage={flashMessage}
                      goBack={goBack}
                      getTaps={getTaps}
                      handleClick={handleClick}
                      studyDetails={studyDetails}
                      studyPrefix={dittiId}
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
          <div className="card-s bg-white shadow">
            <div className="card-title">Study Contacts</div>
            {loading ? (
              <SmallLoader />
            ) : (
              <div>
                {studyContacts.map((sc: StudyContact, i) => {
                  return (
                    <div key={i}>
                      <span>
                        <b>
                          {sc.fullName}: {sc.role}
                        </b>
                      </span>
                      <br />
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      {sc.email}
                      <br />
                      &nbsp;&nbsp;&nbsp;&nbsp;
                      {sc.phoneNumber}
                      <br />
                      <br />
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default StudySummary;
