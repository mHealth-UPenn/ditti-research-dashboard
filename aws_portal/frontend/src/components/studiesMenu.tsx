import * as React from "react";
import { Component } from "react";
import { Study } from "../interfaces";
import { makeRequest } from "../utils";
import { SmallLoader } from "./loader";
import "./studiesMenu.css";

interface StudiesMenuState {
  studies: Study[];
  loading: boolean;
}

class StudiesMenu extends React.Component<any, StudiesMenuState> {
  state = { studies: [], loading: true };

  componentDidMount() {
    makeRequest("/db/get-studies?app=2").then((studies: Study[]) =>
      this.setState({ studies, loading: false })
    );
  }

  render() {
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
                <li key={i} className="link" id={"study-menu-" + s.id}>
                  {s.name}
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
