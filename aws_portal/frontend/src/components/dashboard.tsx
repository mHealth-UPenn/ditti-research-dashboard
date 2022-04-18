import * as React from "react";
import { Component } from "react";
import AdminDashboard from "./adminDashboard/adminDashboard";
import StudiesView from "./dittiApp/studies";
import Header from "./header";
import Home from "./home";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";

// interface DashboardProps {}

interface DashboardState {
  apps: { name: string; id: number; view: React.ReactElement }[];
  breadcrumbs: { name: string; view: React.ReactElement }[];
  history: { name: string; view: React.ReactElement }[][];
  studies: { name: string; id: number }[];
  view: React.ReactElement;
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
      view: view
    };
  }

  getApps = () => {
    return [
      { name: "Ditti App", id: 1, view: <StudiesView /> },
      { name: "Admin Dashboard", id: 2, view: <AdminDashboard /> }
    ];
  };

  getStudies = () => {
    return [
      { name: "MSBI", id: 1 },
      { name: "ART OSA", id: 2 }
    ];
  };

  updateHistory = (name: string, view: React.ReactElement) => {
    const { breadcrumbs, history } = this.state;
    history.push(breadcrumbs.slice(0));
    this.setState({ history });

    let i = 0;
    for (const b of this.state.breadcrumbs) {
      if (b.name === name) {
        let breadcrumbs = this.state.breadcrumbs;
        breadcrumbs = breadcrumbs.slice(0, i + 1);
        this.setState({ breadcrumbs });
        break;
      } else if (i === this.state.breadcrumbs.length - 1) {
        const breadcrumbs = this.state.breadcrumbs;
        breadcrumbs.push({ name: name, view: view });
        this.setState({ breadcrumbs });
        break;
      }

      i++;
    }
  };

  setView = (name: string, view: React.ReactElement) => {
    this.updateHistory(name, view);
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
        <div style={{ display: "flex", flexGrow: 1 }}>
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
