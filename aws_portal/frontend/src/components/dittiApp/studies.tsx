import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, UserDetails, ViewProps } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";
import { sub } from "date-fns";

/**
 * getTapsAsync: queries AWS for tap data
 * getTaps: get tap data locally after querying AWS
 */
interface StudiesViewProps extends ViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
}

/**
 * studies: all studies the user has access to
 * users: this is unused
 * loading: whether to show the loader
 */
interface StudiesViewState {
  studies: Study[];
  users: UserDetails[];
  loading: boolean;
}

class StudiesView extends React.Component<StudiesViewProps, StudiesViewState> {
  state = { studies: [], users: [], loading: true };

  componentDidMount() {

    // get all studies that the user has access to
    const studies = makeRequest("/db/get-studies?app=2").then(
      (studies: Study[]) => this.setState({ studies, loading: false })
    );

    const users = makeRequest("/aws/get-users?app=2").then(
      (users: UserDetails[]) => this.setState({ users })
    );

    // get all tap data 
    const taps = this.props.getTapsAsync();

    // when all promises resolve, hide the loader
    Promise.all([studies, taps, users]).then(() =>
      this.setState({ loading: false })
    );
  }

  /**
   * Handle when a user clicks on a study
   * @param id - the study's database primary key
   */
  handleClickStudy = (id: number): void => {
    const { flashMessage, getTaps, goBack, handleClick } = this.props;

    // get the study
    const study: Study = this.state.studies.filter((s: Study) => s.id == id)[0];

    // set the view
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

              // for each study the user has access to
              this.state.studies.map((s: Study) => {

                // count the number of taps that were recorded in the last 7 days
                const lastWeek = this.props
                  .getTaps()
                  .filter(
                    (t) =>
                      t.time > sub(new Date(), { weeks: 1 }) &&
                      t.dittiId.startsWith(s.dittiId)
                  )
                  .map((t) => t.dittiId)
                  .filter((v, i, arr) => arr.indexOf(v) == i).length;

                // count the number of taps that were recorded in the last 24 hours
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

                    {/* active tapping icon */}
                    <div
                      className={
                        "icon " + (last24hrs ? "icon-success" : "icon-gray")
                      }
                    ></div>

                    {/* link to study summary */}
                    <div className="study-row-name">
                      <span
                        className="link"
                        onClick={() => this.handleClickStudy(s.id)}
                      >
                        {s.acronym}
                      </span>
                    </div>

                    {/* display the number of taps in the last 7 days and 24 hours */}
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
