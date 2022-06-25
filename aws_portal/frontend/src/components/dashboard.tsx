import * as React from "react";
import { Component } from "react";
import Accounts from "./adminDashboard/accounts";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";
import { Tap, TapDetails } from "../interfaces";
import { makeRequest } from "../utils";

// interface DashboardProps {}

interface DashboardState {
  apps: {
    breadcrumbs: string[];
    name: string;
    id: number;
    view: React.ReactElement;
  }[];
  breadcrumbs: { name: string; view: React.ReactElement }[];
  history: { name: string; view: React.ReactElement }[][];
  studies: { name: string; id: number }[];
  view: React.ReactElement;
  taps: TapDetails[];
}

class Dashboard extends React.Component<any, DashboardState> {
  constructor(props: any) {
    super(props);

    const apps = this.getApps();
    const studies = this.getStudies();
    const view = <Home apps={apps} handleClick={this.setView} />;

    this.state = {
      apps: apps,
      breadcrumbs: [{ name: "Home", view: view }],
      studies: studies,
      history: [],
      view: view,
      taps: []
    };
  }

  getApps = () => {
    return [
      {
        breadcrumbs: ["Ditti App"],
        name: "Ditti App",
        id: 1,
        view: (
          <StudiesView
            getTapsAsync={this.getTapsAsync}
            getTaps={this.getTaps}
            handleClick={this.setView}
          />
        )
      },
      {
        breadcrumbs: ["Admin Dashboard", "Accounts"],
        name: "Admin Dashboard",
        id: 2,
        view: <Accounts handleClick={this.setView} />
      }
    ];
  };

  getStudies = () => {
    return [
      { name: "MSBI", id: 1 },
      { name: "ART OSA", id: 2 }
    ];
  };

  getTapsAsync = async (): Promise<TapDetails[]> => {
    let { taps } = this.state;

    if (!taps.length) {
      taps = await makeRequest("/aws/get-taps?app=2").then((res: Tap[]) => {
        return res.map((tap: Tap) => {
          return {
            tapUserId: tap.tapUserId,
            time: tap.time
          };
        });
      });

      this.setState({ taps });
    }

    return taps;
  };

  getTaps = (): TapDetails[] => {
    return this.state.taps;
  };

  setView = (name: string[], view: React.ReactElement, replace?: boolean) => {
    const { breadcrumbs, history } = this.state;
    history.push(breadcrumbs.slice(0));
    this.setState({ history });
    if (replace) breadcrumbs.pop();

    let i = 0;
    for (const b of this.state.breadcrumbs) {
      if (b.name === name[0]) {
        let breadcrumbs = this.state.breadcrumbs;
        breadcrumbs = breadcrumbs.slice(0, i + 1);
        this.setState({ breadcrumbs });
        break;
      } else if (i === this.state.breadcrumbs.length - 1) {
        const breadcrumbs = this.state.breadcrumbs;

        for (const i in name) {
          breadcrumbs.push({
            name: name[i],
            view: parseInt(i) === name.length - 1 ? view : <React.Fragment />
          });
        }
        this.setState({ breadcrumbs });
        break;
      }

      i++;
    }

    this.setState({ view });
  };

  goBack = () => {
    const { history } = this.state;
    const breadcrumbs = history.pop();

    if (breadcrumbs) {
      const view = breadcrumbs[breadcrumbs.length - 1].view;
      this.setState({ history });
      this.setState({ breadcrumbs });
      this.setState({ view });
    }
  };

  render() {
    const { breadcrumbs, history, studies, view } = this.state;

    return (
      <main className="bg-light dashboard-container">
        <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
        <div
          style={{
            display: "flex",
            flexGrow: 1,
            maxHeight: "calc(100vh - 4rem)"
          }}
        >
          <StudiesMenu studies={studies} />
          <div className="dashboard-content">
            <Navbar
              breadcrumbs={breadcrumbs}
              handleBack={this.goBack}
              handleClick={this.setView}
              hasHistory={history.length > 0}
            />
            {view}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
