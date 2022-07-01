import * as React from "react";
import { Component } from "react";
import "./header.css";
import { ReactComponent as Profile } from "../icons/profile.svg";
import { makeRequest } from "../utils";
import { AccountDetails } from "../interfaces";

interface HeaderState {
  accountDetails: AccountDetails;
}

class Header extends React.Component<any, HeaderState> {
  state = { accountDetails: {} as AccountDetails };

  componentDidMount() {
    makeRequest("/db/get-account-details").then(
      (accountDetails: AccountDetails) => this.setState({ accountDetails })
    );
  }

  render() {
    const { email, firstName, lastName } = this.state.accountDetails;
    const name = firstName + " " + lastName;
    const initials = (
      (firstName ? firstName[0] : "") + (lastName ? lastName[0] : "")
    ).toUpperCase();

    return (
      <div className="bg-dark header-container">
        <div className="header-brand">
          <span>AWS Data Portal</span>
        </div>
        <div className="header-profile">
          <span>
            {name}&nbsp;&nbsp;|&nbsp;&nbsp;{email}
          </span>
          <div className="header-profile-icon">
            <span>{initials}</span>
          </div>
        </div>
      </div>
    );
  }
}

export default Header;
