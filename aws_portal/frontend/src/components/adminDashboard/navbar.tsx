import * as React from "react";
import { Component } from "react";
import Accounts from "./accounts";
import Studies from "./studies";
import AccessGroups from "./accessGroups";
import Roles from "./roles";
import { ViewProps } from "../../interfaces";
import AboutSleepTemplates from "./aboutSleepTemplates";

/**
 * active: the active view
 */
interface NavbarProps extends ViewProps {
  active: string;
}

/**
 * views: an array of admin views, their names, and whether any are the active view
 */
interface NavbarState {
  views: { active: boolean; name: string; view: React.ReactElement }[];
}

class Navbar extends React.Component<NavbarProps, NavbarState> {
  constructor(props: NavbarProps) {
    super(props);

    const { flashMessage, goBack, handleClick } = props;
    const { active } = props;
    const views = [
      {
        active: false,
        name: "Accounts",
        view: (
          <Accounts
            handleClick={handleClick}
            flashMessage={flashMessage}
            goBack={goBack}
          />
        )
      },
      {
        active: false,
        name: "Studies",
        view: (
          <Studies
            handleClick={handleClick}
            flashMessage={flashMessage}
            goBack={goBack}
          />
        )
      },
      {
        active: false,
        name: "Roles",
        view: (
          <Roles
            handleClick={handleClick}
            flashMessage={flashMessage}
            goBack={goBack}
          />
        )
      },
      {
        active: false,
        name: "Access Groups",
        view: (
          <AccessGroups
            handleClick={handleClick}
            flashMessage={flashMessage}
            goBack={goBack}
          />
        )
      },
      {
        active: false,
        name: "About Sleep Templates",
        view: (
          <AboutSleepTemplates
            handleClick={handleClick}
            flashMessage={flashMessage}
            goBack={goBack}
          />
        )
      }
    ];

    // set the current view as active
    for (const v of views) {
      if (v.name === active) {
        v.active = true;
        break;
      }
    }

    this.state = { views: views };
  }

  render() {
    const { views } = this.state;

    return (
      <div className="page-header bg-white border-dark-b">

        {/* if the view is active, highlight it using bg-dark */}
        {views.map((v, i) => (
          <div
            key={i}
            className={
              "page-header-button" +
              (v.active ? " bg-dark" : " link-no-underline")
            }
            onClick={() => this.props.handleClick([v.name], v.view, true)}
          >
            {v.name}
          </div>
        ))}
      </div>
    );
  }
}

export default Navbar;
