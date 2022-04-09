import * as React from "react";
import { Component } from "react";
import "./header.css";
import { ReactComponent as Profile } from "../icons/profile.svg";

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
          <div className="header-profile-icon">
            <Profile />
          </div>
        </div>
      </div>
    );
  }
}

export default Header;
