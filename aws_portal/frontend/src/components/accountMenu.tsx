import * as React from "react";
import { Component } from "react";
import { AccountDetails } from "../interfaces";
import TextField from "./fields/textField";
import { ReactComponent as Right } from "../icons/arrowRight.svg";
import "./accountMenu.css";

interface AccountMenuProps {
  accountDetails: AccountDetails;
}

interface AccountMenuState extends AccountDetails {
  setPassword: string;
  confirmPassword: string;
  edit: boolean;
  editPassword: boolean;
}

class AccountMenu extends React.Component<AccountMenuProps, AccountMenuState> {
  constructor(props: AccountMenuProps) {
    super(props);
    this.state = {
      ...props.accountDetails,
      setPassword: "",
      confirmPassword: "",
      edit: false,
      editPassword: false
    };
  }

  render() {
    const { edit, editPassword, email, firstName, lastName } = this.state;

    return (
      <div className="account-menu-container bg-white border-light-l">
        <div className="account-menu-content">
          <div className="account-menu-button">
            <span>
              <b>Account Details</b>
            </span>
            {edit ? (
              <button
                className="button-primary"
                onClick={() => this.setState({ edit: !edit })}
              >
                Save
              </button>
            ) : (
              <button
                className="button-primary"
                onClick={() => this.setState({ edit: !edit })}
              >
                Edit
              </button>
            )}
          </div>
          <div className="account-menu-field">
            {edit ? (
              <TextField
                id="firstName"
                label="First Name"
                prefill={firstName}
                onKeyup={(text: string) => this.setState({ firstName: text })}
              ></TextField>
            ) : (
              <span>
                <b>First Name</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{firstName}
              </span>
            )}
          </div>
          <div className="account-menu-field">
            {edit ? (
              <TextField
                id="lastName"
                label="Last Name"
                prefill={lastName}
                onKeyup={(text: string) => this.setState({ lastName: text })}
              ></TextField>
            ) : (
              <span>
                <b>Last Name</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{lastName}
              </span>
            )}
          </div>
          <div className="account-menu-field">
            {edit ? (
              <TextField
                id="email"
                label="Email"
                prefill={email}
                onKeyup={(text: string) => this.setState({ email: text })}
              ></TextField>
            ) : (
              <span>
                <b>Email</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{email}
              </span>
            )}
          </div>
          <div
            className="border-light-b"
            style={{ marginBottom: "2rem" }}
          ></div>
          <div className="account-menu-button">
            <span>
              <b>Password</b>
            </span>
            {editPassword ? (
              <button
                className="button-primary"
                onClick={() => this.setState({ editPassword: !editPassword })}
              >
                Save
              </button>
            ) : (
              <button
                className="button-primary"
                onClick={() => this.setState({ editPassword: !editPassword })}
              >
                Change
              </button>
            )}
          </div>
          {editPassword ? (
            <React.Fragment>
              <div className="account-menu-field">
                <TextField
                  id="setPassword"
                  label="Enter a new password"
                  type="password"
                  onKeyup={(text: string) =>
                    this.setState({ setPassword: text })
                  }
                ></TextField>
              </div>
              <div className="account-menu-field">
                <TextField
                  id="confirmPassword"
                  label="Confirm your password"
                  type="password"
                  onKeyup={(text: string) =>
                    this.setState({ confirmPassword: text })
                  }
                ></TextField>
              </div>
            </React.Fragment>
          ) : null}
        </div>
        <div className="account-menu-footer bg-dark">
          <Right />
        </div>
      </div>
    );
  }
}

export default AccountMenu;
