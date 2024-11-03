import React, { createRef, useEffect, useState } from "react";
import "./header.css";
import { makeRequest } from "../utils";
import { AccountDetails, ViewProps } from "../interfaces";
import AccountMenu from "./accountMenu";
import SettingsIcon from '@mui/icons-material/Settings';
import CloseIcon from '@mui/icons-material/Close';

/**
 * The Header component now functions as a functional component.
 */
const Header: React.FC<ViewProps> = ({ handleClick, goBack, flashMessage }) => {
  const [accountDetails, setAccountDetails] = useState<AccountDetails>({} as AccountDetails);
  const [loading, setLoading] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);
  const accountMenuRef = createRef<HTMLDivElement>();

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

  const handleOpenMenu = () => {
    if (accountMenuRef.current) {
      accountMenuRef.current.style.right = "0";
      setShowMenu(true);
    }
  }

  const handleCloseMenu = () => {
    if (accountMenuRef.current) {
      accountMenuRef.current.style.right = "-24rem";
      setShowMenu(false);
    }
  }

  return (
    <>
      {/* the header */}
      <div className="bg-[#33334d] text-white flex items-center justify-between flex-shrink-0 h-16">
        <div className="text-2xl ml-8">
          <span>AWS Data Portal</span>
        </div>
        <div className="flex items-center mr-8">
          <span className="absolute right-[6.5rem]">
            {name ? name : ""}&nbsp;&nbsp;|&nbsp;&nbsp;{email ? email : ""}
          </span>

          {/* clicking on this icon shows the account menu */}
          {
            showMenu ?
            <div
              className="flex items-center justify-center w-[2.5rem] h-[2.5rem] hover:border-2 rounded-[2rem] cursor-pointer"
              onClick={handleCloseMenu}>
                <CloseIcon />
            </div> :
            <div
              className="flex items-center justify-center w-[2.5rem] h-[2.5rem] hover:border-2 rounded-[2rem] cursor-pointer"
              onClick={handleOpenMenu}>
                <SettingsIcon />
            </div>
          }
        </div>
      </div>

      {/* the account menu */}
      <AccountMenu
        accountDetails={accountDetails}
        handleClick={handleClick}
        goBack={goBack}
        flashMessage={flashMessage}
        accountMenuRef={accountMenuRef}
        hideMenu={() => setShowMenu(false)} />
    </>
  );
};

export default Header;
