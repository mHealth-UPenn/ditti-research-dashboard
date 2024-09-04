import React, { useEffect, useState } from "react";
import "./header.css";
import { makeRequest } from "../utils";
import { AccountDetails, ViewProps } from "../interfaces";
import AccountMenu from "./accountMenu";

/**
 * The Header component now functions as a functional component.
 */
const Header: React.FC<ViewProps> = ({ handleClick, goBack, flashMessage }) => {
  const [accountDetails, setAccountDetails] = useState<AccountDetails>({} as AccountDetails);
  const [loading, setLoading] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);

  useEffect(() => {
    // get the user's account information
    makeRequest("/db/get-account-details").then((accountDetails: AccountDetails) => {
      setAccountDetails(accountDetails);
      setLoading(false);
    });
  }, []);

  const { email, firstName, lastName } = accountDetails;
  const name = firstName + " " + lastName;
  const initials = (
    (firstName ? firstName[0] : "") + (lastName ? lastName[0] : "")
  ).toUpperCase();

  return (
    <React.Fragment>
      {/* the header */}
      <div className="bg-dark header-container">
        <div className="header-brand">
          <span>AWS Data Portal</span>
        </div>
        <div className="header-profile">
          <span>
            {name ? name : ""}&nbsp;&nbsp;|&nbsp;&nbsp;{email ? email : ""}
          </span>

          {/* clicking on this icon shows the account menu */}
          <div
            className="header-profile-icon"
            onClick={() => setShowMenu(!showMenu)}
          >
            <span>{initials}</span>
          </div>
        </div>
      </div>

      {/* the account menu */}
      {!loading && showMenu ? (
        <AccountMenu
          accountDetails={accountDetails}
          handleClick={handleClick}
          goBack={goBack}
          flashMessage={flashMessage}
          hideMenu={() => setShowMenu(false)}
        />
      ) : null}
    </React.Fragment>
  );
};

export default Header;
