import * as React from "react";
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

const Navbar: React.FC<NavbarProps> = ({ active, handleClick, flashMessage, goBack }) => {
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
  views.forEach(v => {
    if (v.name === active) {
      v.active = true;
    }
  });

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
          onClick={() => handleClick([v.name], v.view, true)}
        >
          {v.name}
        </div>
      ))}
    </div>
  );
};

export default Navbar;
