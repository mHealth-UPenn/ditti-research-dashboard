import { Link } from "react-router-dom";
import { useNavbar } from "../hooks/useNavbar";
import React from "react";

export const Navbar = () => {
  const { breadcrumbs } = useNavbar();

  return (
    <div
      className="z-10 flex h-16 shrink-0 select-none items-center bg-white
        shadow"
    >
      <div className="flex h-12 items-center pl-12">
        {breadcrumbs.map((b, i) => {
          // If this is the last breadcrumb or if there is no link associated with it
          if (i === breadcrumbs.length - 1 || b.link === null) {
            // Don't make the breadcrumb clickable
            return (
              <div key={i} className="flex items-center">
                <span>{b.name}&nbsp;&nbsp;/&nbsp;&nbsp;</span>
              </div>
            );
          } else {
            return (
              <React.Fragment key={i}>
                <div
                  className="flex cursor-pointer items-center text-link
                    hover:text-link-hover"
                >
                  <Link to={b.link}>
                    <span>{b.name}</span>
                  </Link>
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
};
