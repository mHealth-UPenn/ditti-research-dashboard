import * as React from "react";
import { Component } from "react";
import { Study, TapDetails, ViewProps } from "../interfaces";
import { makeRequest } from "../utils";
import StudySummary from "./dittiApp/studySummary";
import { SmallLoader } from "./loader";
import "./studiesMenu.css";

interface StudiesMenuProps extends ViewProps {
  getTaps: () => TapDetails[];
  setView: (name: string, view: React.ReactElement) => void;
}

interface StudiesMenuState {
  studies: Study[];
  loading: boolean;
}

class StudiesMenu extends React.Component<StudiesMenuProps, StudiesMenuState> {
  state = { studies: [], loading: true };

  componentDidMount() {
    makeRequest("/db/get-studies?app=2").then((studies: Study[]) =>
      this.setState({ studies, loading: false })
    );
  }

  render() {
    const { flashMessage, handleClick, getTaps, goBack } = this.props;
    const { studies, loading } = this.state;

    return (
      <div className="bg-white studies-menu-container border-dark-r">
        <div className="studies-menu-header border-dark-b">
          <span>Studies</span>
        </div>
        <div className="studies-menu-content">
          {loading ? (
            <SmallLoader />
          ) : (
            <ul>
              {studies.map((s: Study, i: number) => (
                <li
                  key={i}
                  className="link"
                  id={"study-menu-" + s.id}
                  onClick={() =>
                    this.props.setView(
                      s.acronym,
                      <StudySummary
                        flashMessage={flashMessage}
                        handleClick={handleClick}
                        getTaps={getTaps}
                        goBack={goBack}
                        studyId={s.id}
                      />
                    )
                  }
                >
                  {s.acronym}
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    );
  }
}

export default StudiesMenu;
