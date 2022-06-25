import * as React from "react";
import { Component } from "react";
import { ResponseBody, Study } from "../../interfaces";
import { makeRequest } from "../../utils";
import { SmallLoader } from "../loader";
import "./studies.css";

interface StudiesViewProps {
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
    makeRequest("/db/get-studies?app=2").then(
      this.setStudies,
      this.handleFailure
    );
  }

  setStudies = (studies: Study[]): void => {
    this.setState({ studies, loading: false });
  };

  handleFailure = (res: ResponseBody): void => {
    console.log(res.msg);
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
                    <span className="link">{s.acronym}</span>
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
