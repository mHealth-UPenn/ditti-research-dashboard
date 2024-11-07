import * as React from "react";
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

const Navbar: React.FC<NavbarProps> = ({ breadcrumbs, handleBack, handleClick, hasHistory }) => {
  return (
    <div className="bg-white flex items-center h-16 flex-shrink-0 select-none z-10 shadow">

      {/* the back button */}
      <div className={"h-10 mx-8 flex items-center" + (hasHistory ? " link-svg cursor-pointer" : "")} onClick={handleBack}>
        <Back width={40} height={40} />
      </div>

      {/* the breadcrumbs */}
      <div className="flex items-center h-12">
        {breadcrumbs.map((b, i, arr) => {

          // if this is the last breadcrumb or if there is no view associated with it
          if (i === arr.length - 1 || b.view.type === React.Fragment) {

            // don't make the breadcrumb clickable
            return (
              <div key={i} className="flex items-center">
                <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>
              </div>
            );
          } else {
            return (
              <React.Fragment key={i}>
                <div
                  className="flex items-center text-link hover:text-link-hover cursor-pointer"
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

export default Navbar;
