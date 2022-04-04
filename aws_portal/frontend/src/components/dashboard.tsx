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
  view: React.ElementType;
}

class Dashboard extends React.Component<any, DashboardState> {
  state = {
    view: HomeView
  };

  getView = (view: React.ElementType) => {
    this.setState({ view: view });
  };

  render() {
    const studies = [
      { name: "MSBI", id: 1 },
      { name: "ART OSA", id: 2 }
    ];

    const breadcrumbs = [
      { name: "Home", view: HomeView },
      { name: "Ditti App", view: AppView }
    ];

    return (
      <main className="bg-light dashboard-container">
        <Header name="John Smith" email="john.smith@pennmedicine.upenn.edu" />
        <div style={{ display: "flex", flexGrow: 1 }}>
          <StudiesMenu studies={studies} />
          <div
            style={{ display: "flex", flexDirection: "column", flexGrow: 1 }}
          >
            <Navbar breadcrumbs={breadcrumbs} handleClick={this.getView} />
            {<this.state.view />}
          </div>
        </div>
      </main>
    );
  }
}

export default Dashboard;
