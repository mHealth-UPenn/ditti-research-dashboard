import * as React from "react";
import { Component } from "react";
import "./home.css";
import { ReactComponent as Right } from "../icons/right.svg";
import { makeRequest } from "../utils";
import { ResponseBody, TapDetails, ViewProps } from "../interfaces";
import StudiesView from "./dittiApp/studies";
import Accounts from "./adminDashboard/accounts";
import { SmallLoader } from "./loader";

interface HomeProps extends ViewProps {
  getTapsAsync: () => Promise<TapDetails[]>;
  getTaps: () => TapDetails[];
}

interface HomeState {
  apps: {
    breadcrumbs: string[];
    name: string;
    view: React.ReactElement;
  }[];
  loading: boolean;
}

class Home extends React.Component<HomeProps, HomeState> {
  state = {
    apps: [
      {
        breadcrumbs: ["Ditti App"],
        name: "Ditti App Dashboard",
        view: (
          <StudiesView
            getTapsAsync={this.props.getTapsAsync}
            getTaps={this.props.getTaps}
            handleClick={this.props.handleClick}
            goBack={this.props.goBack}
            flashMessage={this.props.flashMessage}
          />
        )
      },
      {
        breadcrumbs: ["Admin Dashboard", "Accounts"],
        name: "Admin Dashboard",
        view: (
          <Accounts
            handleClick={this.props.handleClick}
            goBack={this.props.goBack}
            flashMessage={this.props.flashMessage}
          />
        )
      }
    ],
    loading: true
  };

  componentDidMount() {
    const admin = makeRequest("/iam/get-access?app=1").then(
      (res: ResponseBody) => {
        if (res.msg != "Authorized") {
          let apps = this.state.apps;

          apps = apps.filter((app) => app.name != "Admin Dashboard");
          this.setState({ apps });
        }
      }
    );

    const ditti = makeRequest("/iam/get-access?app=2").then(
      (res: ResponseBody) => {
        if (res.msg != "Authorized") {
          let apps = this.state.apps;

          apps = apps.filter((app) => app.name != "Ditti App Dashboard");
          this.setState({ apps });
        }
      }
    );

    Promise.all([admin, ditti]).then(() => this.setState({ loading: false }));
  }

  getApps() {
    return this.state.apps.map((app, i) => (
      <div
        key={i}
        className="card-s hover-pointer bg-white shadow"
        onClick={() => this.props.handleClick(app.breadcrumbs, app.view)}
      >
        <div className="app-name">
          <span>{app.name}</span>
        </div>
        <div className="app-button link-svg">
          <Right />
        </div>
      </div>
    ));
  }

  render() {
    return (
      <div className="card-container">
        <div className="card-row">
          {this.state.loading ? (
            <div className="card-s bg-white shadow">
              <SmallLoader />
            </div>
          ) : (
            this.getApps()
          )}
        </div>
      </div>
    );
  }
}

export default Home;
