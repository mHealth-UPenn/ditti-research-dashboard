import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";
import { sub } from "date-fns";

interface StudiesViewProps extends ViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
}

interface StudiesViewState {
  studies: Study[];
  users: UserDetails[];
  loading: boolean;
}

class StudiesView extends React.Component<StudiesViewProps, StudiesViewState> {
  state = { studies: [], users: [], loading: true };

  componentDidMount() {
    const studies = makeRequest("/db/get-studies?app=2").then(
      (studies: Study[]) => this.setState({ studies, loading: false })
    );

    const users = makeRequest("/aws/get-users?app=2").then(
      (users: UserDetails[]) => this.setState({ users })
    );

    const taps = this.props.getTapsAsync();

    Promise.all([studies, taps, users]).then(() =>
      this.setState({ loading: false })
    );
  }

  handleClickStudy = (id: number): void => {
    const { flashMessage, getTaps, goBack, handleClick } = this.props;
    const study: Study = this.state.studies.filter((s: Study) => s.id == id)[0];

    const view = (
      <StudySummary
        flashMessage={flashMessage}
        handleClick={handleClick}
        getTaps={getTaps}
        goBack={goBack}
        studyId={study.id}
      />
    );

    if (study) handleClick([study.acronym], view, false);
  };

  render() {
    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            <div className="card-title">Studies</div>
            {this.state.loading ? (
              <SmallLoader />
            ) : (
              this.state.studies.map((s: Study) => {
                const lastWeek = this.props
                  .getTaps()
                  .filter(
                    (t) =>
                      t.time > sub(new Date(), { weeks: 1 }) &&
                      t.dittiId.startsWith(s.dittiId)
                  )
                  .map((t) => t.dittiId)
                  .filter((v, i, arr) => arr.indexOf(v) == i).length;

                const last24hrs = this.props
                  .getTaps()
                  .filter(
                    (t) =>
                      t.time > sub(new Date(), { weeks: 1 }) &&
                      t.dittiId.startsWith(s.dittiId)
                  )
                  .map((t) => t.dittiId)
                  .filter((v, i, arr) => arr.indexOf(v) == i).length;

                return (
                  <div key={s.id} className="border-light-b study-row">
                    <div
                      className={
                        "icon " + (last24hrs ? "icon-success" : "icon-gray")
                      }
                    ></div>
                    <div className="study-row-name">
                      <span
                        className="link"
                        onClick={() => this.handleClickStudy(s.id)}
                      >
                        {s.acronym}
                      </span>
                    </div>
                    <div className="study-row-summary">
                      <div className="study-row-summary-l">
                        <div>24 hours:</div>
                        <div>1 week:</div>
                      </div>
                      <div className="study-row-summary-r">
                        <div>{lastWeek} active subjects</div>
                        <div>{last24hrs} active subjects</div>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default StudiesView;
