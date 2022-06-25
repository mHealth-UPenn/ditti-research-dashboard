import * as React from "react";
import { Component } from "react";
import { ResponseBody, Study, TapDetails } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";
import StudySummary from "./studySummary";

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
  loading: boolean;
}

class StudiesView extends React.Component<StudiesViewProps, StudiesViewState> {
  state = {
    studies: [],
    loading: true
  };

  componentDidMount() {
    const studies = makeRequest("/db/get-studies?app=2").then(
      (studies: Study[]) => this.setState({ studies })
    );

    const taps = this.props.getTapsAsync();
    const promises = [studies, taps];

    Promise.all(promises).then(() => this.setState({ loading: false }));
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
          <div className="card-l bg-white shadow">
            <div className="card-title">Studies</div>
            {loading ? (
              <SmallLoader />
            ) : (
              studies.map((s: Study) => (
                <div key={s.id} className="border-light-b study-row">
                  <div className="study-row-name">
                    <span
                      className="link"
                      onClick={() => this.handleClickStudy(s.id)}
                    >
                      {s.acronym}
                    </span>
                  </div>
                  <div className="study-row-summary">Summary Info</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    );
  }
}

export default StudiesView;
