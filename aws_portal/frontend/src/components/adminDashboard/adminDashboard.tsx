import * as React from "react";
import { Component } from "react";
import "./adminDashboard.css";

// interface AdminDashboardProps {}

interface AdminDashboardState {
  views: { active: boolean; name: string }[];
}

class AdminDashboard extends React.Component<any, AdminDashboardState> {
  state = {
    views: [
      { active: true, name: "Accounts" },
      { active: false, name: "Studies" },
      { active: false, name: "Access Groups" },
      { active: false, name: "Apps" }
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
            >
              {v.name}
            </div>
          ))}
        </div>
        <div className="page-content bg-white">{this.props.children}</div>
      </div>
    );
  }
}

export default AdminDashboard;
