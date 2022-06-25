import * as React from "react";
import { Component } from "react";
import { Study, StudySubject, TapDetails } from "../../interfaces";
import TextField from "../fields/textField";
import SubjectsEdit from "./subjectsEdit";

interface SubjectVisualsProps {
  getTaps: () => TapDetails[];
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
  studyDetails: Study;
  subject: StudySubject;
}

// interface SubjectVisualsState {}

class SubjectVisuals extends React.Component<SubjectVisualsProps, any> {
  render() {
    const { dittiId, expiresOn } = this.props.subject;
    const { studyDetails } = this.props;

    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            <div className="subject-header">
              <div className="card-title">{dittiId}</div>
              <div className="subject-hedaer-info">
                <div>
                  Expires on: <b>{expiresOn}</b>
                </div>
                <button
                  className="button-secondary button-lg"
                  onClick={() =>
                    this.props.handleClick(
                      ["Edit"],
                      <SubjectsEdit
                        dittiId={dittiId}
                        studyId={studyDetails.id}
                        studyEmail={studyDetails.email}
                        studyPrefix={studyDetails.dittiId}
                      />,
                      false
                    )
                  }
                >
                  Edit Details
                </button>
              </div>
            </div>
            <div className="subject-display-container">
              <div className="subjet-display-title">Visual Summary</div>
              <div className="subject-display-controls">
                <div>
                  <TextField id="start" label="Start:" type="datetime-local" />
                </div>
                <div>
                  <TextField id="end" label="Stop:" type="datetime-local" />
                </div>
              </div>
              <div className="subject-display">Display</div>
            </div>
            <button className="button-primary button-lg">Download CSV</button>
          </div>
          <div className="card-s bg-white shadow">
            <div className="card-title">7-day summary</div>
          </div>
        </div>
      </div>
    );
  }
}

export default SubjectVisuals;
