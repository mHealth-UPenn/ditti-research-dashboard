import * as React from "react";
import { Component } from "react";
import Accounts from "./accounts";
import "./adminDashboard.css";

// interface AdminDashboardProps {}

interface AdminDashboardState {
  views: { active: boolean; name: string; view: React.ReactElement }[];
}

class AdminDashboardView extends React.Component<any, AdminDashboardState> {
  state = {
    views: [
      { active: true, name: "Accounts", view: <Accounts /> },
      { active: false, name: "Studies", view: <Accounts /> },
      { active: false, name: "Access Groups", view: <Accounts /> },
      { active: false, name: "Apps", view: <Accounts /> }
    ]
  };

  setView = (view: React.ReactElement) => {
    console.log(view);
  };

  render() {
    const { views } = this.state;

    return (
      <div className="page-container">
        <div className="page-header bg-white border-dark-b">
          {views.map((v) => (
            <div
              className={
                "page-header-button" +
                (v.active ? " bg-dark" : " link-no-underline")
              }
              onClick={() => this.setView(v.view)}
            >
              {v.name}
            </div>
          ))}
        </div>
        <div className="page-content bg-white">Content!</div>
      </div>
    );
  }
}

export default AdminDashboardView;
