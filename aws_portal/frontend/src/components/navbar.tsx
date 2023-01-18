import * as React from "react";
import { Component } from "react";
import "./navbar.css";
import { ReactComponent as Back } from "../icons/left.svg";

/**
 * breadcrumbs: the breadcrumbs to display on the navbar
 * handleBack: a function for when the user clicks back
 * handleClick: a function for when the user clicks on a breadcrumb
 * hasHistory: whether there is any history
 */
interface NavbarProps {
  breadcrumbs: { name: string; view: React.ReactElement }[];
  handleBack: () => void;
  handleClick: (name: string[], view: React.ReactElement) => void;
  hasHistory: boolean;
}

class Navbar extends React.Component<NavbarProps, any> {
  render() {
    const { breadcrumbs, handleBack, handleClick, hasHistory } = this.props;

    return (
      <div className="bg-white border-dark-b navbar-container">

        {/* the back button */}
        <div className={hasHistory ? "link-svg" : ""} onClick={handleBack}>
          <Back />
        </div>
        
        {/* the breadcrumbs */}
        <div className="navbar-content">
          {breadcrumbs.map((b, i, arr) => {

            // if this is the last breadcrumb or if there is no view associated with it
            if (i === arr.length - 1 || b.view.type === React.Fragment) {

              // don't make the breadcrumb clickable
              return (
                <div key={i}>
                  <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>
                </div>
              );
            } else {
              return (
                <React.Fragment key={i}>
                  <div
                    className="link-no-underline"
                    onClick={() => handleClick([b.name], b.view)}
                  >
                    <span>{b.name}</span>
                  </div>
                  <div>
                    <span>&nbsp;&nbsp;/&nbsp;&nbsp;</span>
                  </div>
                </React.Fragment>
              );
            }
          })}
        </div>
      </div>
    );
  }
}

export default Navbar;
