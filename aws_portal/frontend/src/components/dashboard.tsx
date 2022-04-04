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
  view: React.ReactElement;
}

class Dashboard extends React.Component<any, DashboardState> {
  state = {
    view: <React.Fragment />
  };

  getView = (view: React.ReactElement) => {
    this.setState({ view: view });
  };

  render() {
    const studies = [
      { name: "MSBI", id: 1 },
      { name: "ART OSA", id: 2 }
    ];

    const apps = [
      { name: "Ditti App", id: 1 },
      { name: "Admin Dashboard", id: 2 }
    ];

    const home = <HomeView apps={apps} />;
    const breadcrumbs = [
      { name: "Home", view: home },
      { name: "Ditti App", view: <AppView /> }
    ];

    return (
      <main className="bg-light dashboard-container">
        <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
        <div style={{ display: "flex", flexGrow: 1 }}>
          <StudiesMenu studies={studies} />
          <div className="dashboard-content">
            <Navbar breadcrumbs={breadcrumbs} handleClick={this.getView} />
            {this.state.view}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
