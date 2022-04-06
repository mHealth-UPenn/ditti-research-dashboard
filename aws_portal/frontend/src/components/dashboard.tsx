import * as React from "react";
import { Component } from "react";
import AppView from "./views/appView";
import Header from "./header";
import HomeView from "./views/homeView";
import Navbar from "./navbar";
import StudiesMenu from "./studiesMenu";
import "./dashboard.css";

// interface DashboardProps {}

interface DashboardState {
  apps: { name: string; id: number }[];
  breadcrumbs: { name: string; view: React.ReactElement }[];
  studies: { name: string; id: number }[];
  view: React.ReactElement;
}

class Dashboard extends React.Component<any, DashboardState> {
  constructor(props: any) {
    super(props);
    console.log(this.getApps());

    const apps = this.getApps();
    const studies = this.getStudies();
    const view = <HomeView apps={apps} />;

    this.state = {
      apps: apps,
      breadcrumbs: [{ name: "Home", view: view }],
      studies: studies,
      view: view
    };
  }

  getApps = () => {
    return [
      { name: "Ditti App", id: 1 },
      { name: "Admin Dashboard", id: 2 }
    ];
  };

  getStudies = () => {
    return [
      { name: "MSBI", id: 1 },
      { name: "ART OSA", id: 2 }
    ];
  };

  setView = (view: React.ReactElement) => {
    this.setState({ view: view });
  };

  render() {
    const { breadcrumbs, studies, view } = this.state;
    console.log(breadcrumbs, studies, view);

    return (
      <main className="bg-light dashboard-container">
        <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
        <div style={{ display: "flex", flexGrow: 1 }}>
          <StudiesMenu studies={studies} />
          <div className="dashboard-content">
            <Navbar breadcrumbs={breadcrumbs} handleClick={this.setView} />
            {view}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
