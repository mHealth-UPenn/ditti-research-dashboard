import React, { createRef, useEffect, useState } from "react";
import { makeRequest } from "../utils";
import { AccountDetails, ViewProps } from "../interfaces";
import AccountMenu from "./accountMenu";
import SettingsIcon from '@mui/icons-material/Settings';
import CloseIcon from '@mui/icons-material/Close';
import { APP_ENV } from "../environment";
import DataFactory from "../dataFactory";

/**
 * The Header component now functions as a functional component.
 */
const Header: React.FC<ViewProps> = ({ handleClick, goBack, flashMessage }) => {
  const [accountDetails, setAccountDetails] = useState<AccountDetails>({} as AccountDetails);
  const [loading, setLoading] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);
  const accountMenuRef = createRef<HTMLDivElement>();

  let dataFactory: DataFactory | null = null;
  if (APP_ENV === "demo") {
    dataFactory = new DataFactory();
    dataFactory.init();
  }

  useEffect(() => {
    if (APP_ENV === "demo" && dataFactory) {
      setAccountDetails(dataFactory.accountDetails)
      setLoading(false)
      return;
    }
    // get the user's account information
    makeRequest("/db/get-account-details").then((accountDetails: AccountDetails) => {
      setAccountDetails(accountDetails);
      setLoading(false);
    });
  }, []);

  const { email, firstName, lastName } = accountDetails;
  const name = firstName + " " + lastName;

  const handleOpenMenu = () => {
    if (accountMenuRef.current) {
      accountMenuRef.current.style.width = "24rem";
      setShowMenu(true);
    }
  }

  const handleCloseMenu = () => {
    if (accountMenuRef.current) {
      accountMenuRef.current.style.width = "0";
      setShowMenu(false);
    }
  }

  return (
    <>
      {/* the header */}
      <div className="bg-secondary text-white flex items-center justify-between flex-shrink-0 h-16">
        <div className="flex flex-col text-2xl ml-8">
          <span className="mr-2">Ditti</span>
          <span className="text-sm whitespace-nowrap overflow-hidden">Research Dashboard</span>
        </div>
        <div className="flex items-center mr-8">
          <span className="hidden mr-6 md:flex">
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
      {!loading &&
        <>
          {showMenu &&
            <div
              className="absolute w-[calc(100vw-4.5rem)] h-screen z-20 bg-transparent"
              onClick={handleCloseMenu} />
          }
          <AccountMenu
            prefill={accountDetails}
            handleClick={handleClick}
            goBack={goBack}
            flashMessage={flashMessage}
            accountMenuRef={accountMenuRef}
            hideMenu={() => setShowMenu(false)} />
        </>
      }
    </>
  );
};

export default Header;
