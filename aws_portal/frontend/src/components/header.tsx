import * as React from "react";
import { Component } from "react";
import "./header.css";

interface HeaderProps {
  name: string;
  email: string;
}

class Header extends React.Component<HeaderProps, any> {
  render() {
    const { name, email } = this.props;

    return (
      <div className="bg-dark header-container">
        <div className="header-brand">
          <span>AWS Data Portal</span>
        </div>
        <div className="header-profile">
          <span>
            {name}&nbsp;&nbsp;|&nbsp;&nbsp;{email}
          </span>
          <img
            className="header-profile-icon"
            src={process.env.PUBLIC_URL + "/icons/profile.svg"}
          ></img>
        </div>
      </div>
    );
  }
}

export default Header;
