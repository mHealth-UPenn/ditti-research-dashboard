import * as React from "react";
import { Component } from "react";
import { ResponseBody, Study, TapDetails, User } from "../../interfaces";
import { mapTaps, makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";
import { sub } from "date-fns";
import { dummyData } from "../dummyData";

interface StudiesViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface StudiesViewState {
  studies: Study[];
  mappedTaps: { dittiId: string; time: Date }[];
  loading: boolean;
}

class StudiesView extends React.Component<StudiesViewProps, StudiesViewState> {
  state = {
    studies: [],
    mappedTaps: [],
    loading: true
  };

  componentDidMount() {
    const studies = makeRequest("/db/get-studies?app=2").then(
      (studies: Study[]) => this.setState({ studies })
    );

    const _1week = sub(new Date(), { weeks: 1 }).toISOString();
    const users = makeRequest(
      `/aws/scan?app=2&key=User&query=exp_time>>"${_1week}"`
    ).then((activeUsers: User[]) => {
      const mappedTaps = mapTaps(dummyData, activeUsers);
      this.setState({ mappedTaps });
    });

    const taps = this.props.getTapsAsync();
    const promises = [studies, taps, users];

    Promise.all(promises).then(() => {
      this.setState({ loading: false });
    });
  }

  handleClickStudy = (id: number): void => {
    const { getTaps, handleClick } = this.props;
    const study: Study = this.state.studies.filter((s: Study) => s.id == id)[0];
    const view = (
      <StudySummary
        getTaps={getTaps}
        handleClick={handleClick}
        studyId={study.id}
      />
    );
    if (study) handleClick([study.acronym], view, false);
  };

  render() {
    const { loading, studies } = this.state;

    return (
      <div className="card-container">
        <div className="card-row">
          <div className="card-m bg-white shadow">
            <div className="card-title">Studies</div>
            {loading ? (
              <SmallLoader />
            ) : (
              studies.map((s: Study) => {
                const lastWeek = this.state.mappedTaps
                  .filter(
                    (t: { dittiId: string; time: Date }) =>
                      t.time > sub(new Date(), { weeks: 1 }) &&
                      t.dittiId.startsWith(s.dittiId)
                  )
                  .map((t: { dittiId: string; time: Date }) => t.dittiId)
                  .filter((v, i, arr) => arr.indexOf(v) == i).length;

                const last24hrs = this.state.mappedTaps
                  .filter(
                    (t: { dittiId: string; time: Date }) =>
                      t.time > sub(new Date(), { weeks: 1 }) &&
                      t.dittiId.startsWith(s.dittiId)
                  )
                  .map((t: { dittiId: string; time: Date }) => t.dittiId)
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
