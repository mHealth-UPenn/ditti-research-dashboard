import * as React from "react";
import { Component } from "react";
import "./dashboard.css";

// interface DashboardProps {}

// interface DashboardState {}

class Dashboard extends React.Component<any, any> {
  // state = { :  }
  render() {
    return (
      <div className="bg-light dashboard-container">{this.props.children}</div>
    );
  }
}

export default Dashboard;
