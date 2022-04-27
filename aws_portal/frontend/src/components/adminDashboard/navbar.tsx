import * as React from "react";
import { Component } from "react";
import Accounts from "./accounts";
import Studies from "./studies";
import AccessGroups from "./accessGroups";
import Apps from "./apps";

interface NavbarProps {
  active: string;
  handleClick: (
    name: string[],
    view: React.ReactElement,
    replace: boolean
  ) => void;
}

interface NavbarState {
  views: { active: boolean; name: string; view: React.ReactElement }[];
}

class Navbar extends React.Component<NavbarProps, NavbarState> {
  constructor(props: NavbarProps) {
    super(props);

    const { active } = props;
    const views = [
      {
        active: false,
        name: "Accounts",
        view: <Accounts handleClick={props.handleClick} />
      },
      {
        active: false,
        name: "Studies",
        view: <Studies handleClick={props.handleClick} />
      },
      {
        active: false,
        name: "Access Groups",
        view: <AccessGroups handleClick={props.handleClick} />
      },
      {
        active: false,
        name: "Apps",
        view: <Apps handleClick={props.handleClick} />
      }
    ];

    for (const v of views) {
      if (v.name === active) {
        v.active = true;
        break;
      }
    }

    this.state = { views: views };
  }

  render() {
    const { handleClick } = this.props;
    const { views } = this.state;

    return (
      <div className="page-header bg-white border-dark-b">
        {views.map((v) => (
          <div
            className={
              "page-header-button" +
              (v.active ? " bg-dark" : " link-no-underline")
            }
            onClick={() => handleClick([v.name], v.view, true)}
          >
            {v.name}
          </div>
        ))}
      </div>
    );
  }
}

export default Navbar;
