/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import { createRef, useEffect, useState } from "react";
import { AccountMenu } from "./accountMenu";
import SettingsIcon from '@mui/icons-material/Settings';
import CloseIcon from '@mui/icons-material/Close';
import { useAuth } from "../hooks/useAuth";
import { AccountModel } from "../types/models";

/**
 * The Header component now functions as a functional component.
 */
export const Header = () => {
  const [accountDetails, setAccountDetails] = useState<AccountModel>({} as AccountModel);
  const [loading, setLoading] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);
  const accountMenuRef = createRef<HTMLDivElement>();
  const { isResearcherAuthenticated, accountInfo } = useAuth();

  useEffect(() => {
    // If using researcher auth, use account info from Cognito
    if (isResearcherAuthenticated && accountInfo) {
      setAccountDetails({
        firstName: accountInfo.firstName,
        lastName: accountInfo.lastName,
        email: accountInfo.email,
        phoneNumber: accountInfo.phoneNumber || ""
      });
      setLoading(false);
    }
  }, [isResearcherAuthenticated, accountInfo]);

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
            accountMenuRef={accountMenuRef}
            hideMenu={() => handleCloseMenu()} />
        </>
      }
    </>
  );
};
