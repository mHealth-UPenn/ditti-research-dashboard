import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { getAccess, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import StudySubjects from "./studySubjects";
import "./studySummary.css";
import Subjects from "./subjects";
import SubjectsEdit from "./subjectsEdit";
import { Workbook } from "exceljs";
import { saveAs } from "file-saver";
import { format } from "date-fns";

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
  studyId: number;
}

/**
 * canCreate: whether the user can enroll new users
 * studyContacts: other study contacts
 * studyDetails: this study's information
 * loading: whether to show the loader
 */
interface StudySummaryState {
  canCreate: boolean;
  studyContacts: StudyContact[];
  studyDetails: Study;
  loading: boolean;
}

class StudySummary extends React.Component<
  StudySummaryProps,
  StudySummaryState
> {
  state = {
    canCreate: false,
    studyContacts: [],
    studyDetails: {} as Study,
    loading: true
  };

  componentDidMount() {
    const { studyId } = this.props;

    // check whether the user can enroll new subjets
    const create = getAccess(2, "Create", "Users", studyId)
      .then(() => this.setState({ canCreate: true }))
      .catch(() => this.setState({ canCreate: false }));

    // get other accounts that have access to this study
    const studyContacts = makeRequest(
      "/db/get-study-contacts?app=2&study=" + studyId
    ).then((studyContacts: StudyContact[]) => this.setState({ studyContacts }));

    // get this study's information
    const studyDetails = makeRequest(
      "/db/get-study-details?app=2&study=" + studyId
    ).then((studyDetails: Study) => this.setState({ studyDetails }));

    // when all promises resolve, hide the loader
    Promise.all([create, studyContacts, studyDetails]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Download all of the study's data in excel format
   */
  downloadExcel = async (): Promise<void> => {
    const workbook = new Workbook();
    const sheet = workbook.addWorksheet("Sheet 1");
    const taps = this.props.getTaps();
    const id = this.state.studyDetails.acronym;
    const fileName = format(new Date(), `'${id}_'yyyy-MM-dd'_'HH:mm:ss`);

    // localize tap timestamps
    const data = taps.map((t) => {
      return [t.dittiId, new Date(t.time), t.timeZone];
    });

    sheet.columns = [
      { header: "Ditti ID", width: 10 },
      { header: "Taps", width: 20 },
      { header: "Time zone", width: 20 }
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

  render() {
    const { flashMessage, getTaps, goBack, handleClick, studyId } = this.props;
    const { canCreate, loading, studyContacts, studyDetails } = this.state;
    const { dittiId, email, name } = studyDetails;

    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            {loading ? (
              <SmallLoader />
            ) : (
              <div>

                {/* study information */}
                <div className="card-header">
                  <div className="card-title flex-space">
                    <span>{name}</span>

                    {/* download as excel button */}
                    <button
                      className="button-primary button-lg"
                      onClick={this.downloadExcel}
                      style={{ flexShrink: 0, width: "12rem" }}
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

                {/* list of active study subjects */}
                <div className="study-subjects">
                  <div className="study-subjects-header">
                    <div className="study-subjects-title">Active Subjects</div>
                    <div className="study-subjects-buttons">

                      {/* if the user has permissions to create add the enroll button */}
                      {canCreate ? (
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
                              />
                            )
                          }
                        >
                          Enroll subject +
                        </button>
                      ) : null}

                      {/* the view all subjects button */}
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
                              getTaps={getTaps}
                            />
                          )
                        }
                      >
                        View all subjects
                      </button>
                    </div>
                  </div>

                  {/* list of active subjects */}
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

            {/* list of study contacts */}
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
