import * as React from "react";
import { Component } from "react";
import AppView from "./appView";
import "./homeView.css";

interface HomeViewProps {
  apps: { name: string; id: number }[];
  handleClick(name: string, view: React.ReactElement): void;
}

// interface HomeViewState {}

class HomeView extends React.Component<any, HomeViewProps> {
  // state = { :  }
  render() {
    return (
      <div className="card-container">
        <div className="card-row">
          {this.props.apps.map((a: { name: string; id: number }) => (
            <div key={"app-" + a.id} className="card-s bg-white shadow">
              <div className="app-name">
                <span>{a.name}</span>
              </div>
              <img
                className="app-button"
                src={process.env.PUBLIC_URL + "/icons/right.svg"}
                onClick={() => this.props.handleClick(a.name, <AppView />)}
              ></img>
            </div>
          ))}
        </div>
      </div>
    );
  }
}

export default HomeView;
