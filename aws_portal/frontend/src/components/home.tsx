import * as React from "react";
import { Component } from "react";
import "./home.css";
import { ReactComponent as Right } from "../icons/right.svg";

interface HomeProps {
  apps: {
    breadcrumbs: string[];
    name: string;
    id: number;
    view: React.ReactElement;
  }[];
  handleClick(name: string[], view: React.ReactElement): void;
}

// interface HomeState {}

class Home extends React.Component<any, HomeProps> {
  // state = { :  }
  render() {
    return (
      <div className="card-container">
        <div className="card-row">
          {this.props.apps.map(
            (
              a: {
                breadcrumbs: string[];
                name: string;
                id: number;
                view: React.ReactElement;
              },
              i: number
            ) => (
              <div
                key={i}
                className="card-s bg-white shadow"
                onClick={() => this.props.handleClick(a.breadcrumbs, a.view)}
              >
                <div className="app-name">
                  <span>{a.name}</span>
                </div>
                <div className="app-button link-svg">
                  <Right />
                </div>
              </div>
            )
          )}
        </div>
      </div>
    );
  }
}

export default Home;
