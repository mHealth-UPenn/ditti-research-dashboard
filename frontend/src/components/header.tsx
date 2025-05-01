import { createRef, useEffect, useState } from "react";
import { AccountMenu } from "./accountMenu/accountMenu";
import SettingsIcon from "@mui/icons-material/Settings";
import CloseIcon from "@mui/icons-material/Close";
import { useAuth } from "../hooks/useAuth";
import { AccountModel } from "../types/models";

/**
 * The Header component now functions as a functional component.
 */
export const Header = () => {
  const [accountDetails, setAccountDetails] = useState<AccountModel>(
    {} as AccountModel
  );
  const [loading, setLoading] = useState<boolean>(true);
  const [showMenu, setShowMenu] = useState<boolean>(false);
  const accountMenuRef = createRef<HTMLDivElement>();
  const { isResearcherAuthenticated, accountInfo } = useAuth();

  useEffect(() => {
    // If using researcher auth, use account info from Cognito
    if (isResearcherAuthenticated) {
      setAccountDetails({
        firstName: accountInfo.firstName,
        lastName: accountInfo.lastName,
        email: accountInfo.email,
        phoneNumber: accountInfo.phoneNumber ?? "",
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
  };

  const handleCloseMenu = () => {
    if (accountMenuRef.current) {
      accountMenuRef.current.style.width = "0";
      setShowMenu(false);
    }
  };

  return (
    <>
      {/* the header */}
      <div
        className="flex h-16 shrink-0 items-center justify-between bg-secondary
          text-white"
      >
        <div className="ml-8 flex flex-col text-2xl">
          <span className="mr-2">Ditti</span>
          <span className="overflow-hidden whitespace-nowrap text-sm">
            Research Dashboard
          </span>
        </div>
        <div className="mr-8 flex items-center">
          <span className="mr-6 hidden md:flex">
            {name ? name : ""}&nbsp;&nbsp;|&nbsp;&nbsp;{email ? email : ""}
          </span>

          {/* clicking on this icon shows the account menu */}
          {showMenu ? (
            <div
              className="flex size-10 cursor-pointer items-center justify-center
                rounded-[2rem] hover:border-2"
              onClick={handleCloseMenu}
            >
              <CloseIcon />
            </div>
          ) : (
            <div
              className="flex size-10 cursor-pointer items-center justify-center
                rounded-[2rem] hover:border-2"
              onClick={handleOpenMenu}
            >
              <SettingsIcon />
            </div>
          )}
        </div>
      </div>

      {/* the account menu */}
      {!loading && (
        <>
          {showMenu && (
            <div
              className="bg-transparent absolute z-20 h-screen
                w-[calc(100vw-4.5rem)]"
              onClick={handleCloseMenu}
            />
          )}
          <AccountMenu
            prefill={accountDetails}
            accountMenuRef={accountMenuRef}
            hideMenu={() => {
              handleCloseMenu();
            }}
          />
        </>
      )}
    </>
  );
};
