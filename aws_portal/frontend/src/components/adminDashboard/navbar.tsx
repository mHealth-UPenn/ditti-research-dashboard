import * as React from "react";
import Accounts from "./accounts";
import Studies from "./studies";
import AccessGroups from "./accessGroups";
import Roles from "./roles";
import { ViewProps } from "../../interfaces";
import AboutSleepTemplates from "./aboutSleepTemplates";
import Link from "../links/link";

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
    <div className="flex items-center justify-left bg-white select-none">
      {/* if the view is active, highlight it using bg-dark */}
      {views.map((v, i) => (
        v.active ?
          <div
            key={i}
            className="flex px-4 lg:px-8 items-center justify-center h-full py-4 bg-dark text-center">
              {v.name}
          </div> :
          <div key={i} className="flex h-full">
            <Link
              className="flex items-center justify-center px-3 lg:px-4 xl:px-8 h-full w-full no-underline hover:bg-extra-light text-center"
              onClick={() => handleClick([v.name], v.view, true)}>
                {v.name}
            </Link>
          </div>
      ))}
    </div>
  );
};

export default Navbar;
