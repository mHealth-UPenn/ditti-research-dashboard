import * as React from "react";
import { Component } from "react";
import "./navbar.css";
import { ReactComponent as Back } from "../icons/back.svg";

interface NavbarProps {
  breadcrumbs: { name: string; view: React.ReactElement }[];
  handleBack: () => void;
  handleClick: (name: string, view: React.ReactElement) => void;
  hasHistory: boolean;
}

class Navbar extends React.Component<NavbarProps, any> {
  render() {
    const { breadcrumbs, handleBack, handleClick, hasHistory } = this.props;

    return (
      <div className="bg-white border-dark-b navbar-container">
        <div className={hasHistory ? "link-svg" : ""} onClick={handleBack}>
          <Back />
        </div>
        <div className="navbar-content">
          {breadcrumbs.map((b, i, arr) => {
            if (i === arr.length - 1) {
              return <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>;
            } else {
              return (
                <span>
                  <span
                    className="link-no-underline"
                    onClick={() => handleClick(b.name, b.view)}
                  >
                    {b.name}
                  </span>
                  <span>&nbsp;&nbsp;/&nbsp;&nbsp;</span>
                </span>
              );
            }
          })}
        </div>
      </div>
    );
  }
}

export default Navbar;
