import * as React from "react";
import { Component } from "react";
import "./header.css";
import { makeRequest } from "../utils";
import { AccountDetails, ViewProps } from "../interfaces";
import AccountMenu from "./accountMenu";

/**
 * accountDetails: the current user's account information
 * loading: whether the user's account data is being retrieved and the account
 *          menu should be hidden
 * showMenu: whether to show the account menu
 */
interface HeaderState {
  accountDetails: AccountDetails;
  loading: boolean;
  showMenu: boolean;
}

class Header extends React.Component<ViewProps, HeaderState> {
  state = {
    accountDetails: {} as AccountDetails,
    loading: true,
    showMenu: false
  };

  componentDidMount() {

    // get the user's account information
    makeRequest("/db/get-account-details").then(
      (accountDetails: AccountDetails) =>
        this.setState({ accountDetails, loading: false })
    );
  }

  render() {
    const { handleClick, goBack, flashMessage } = this.props;
    const { accountDetails, loading, showMenu } = this.state;
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
              onClick={() => this.setState({ showMenu: !showMenu })}
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
            hideMenu={() => this.setState({ showMenu: false })}
          />
        ) : null}
      </React.Fragment>
    );
  }
}

export default Header;
