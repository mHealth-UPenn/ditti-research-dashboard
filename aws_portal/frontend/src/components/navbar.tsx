import * as React from "react";
import { Component } from "react";
import "./navbar.css";

interface NavbarProps {
  breadcrumbs: { name: string; view: React.ElementType }[];
  handleClick: (view: React.ElementType) => void;
}

class Navbar extends React.Component<NavbarProps, any> {
  render() {
    const { breadcrumbs } = this.props;

    return (
      <div className="bg-white border-dark-b navbar-container">
        <img src={process.env.PUBLIC_URL + "/icons/back.svg"}></img>
        <div className="navbar-content">
          {breadcrumbs.map((b) => (
            <span onClick={() => this.props.handleClick(b.view)}>
              {b.name}&nbsp;&nbsp;/&nbsp;&nbsp;
            </span>
          ))}
        </div>
      </div>
    );
  }
}

export default Navbar;
