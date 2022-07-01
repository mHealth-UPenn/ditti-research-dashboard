import * as React from "react";
import { Component } from "react";
import { AccountDetails, ResponseBody, ViewProps } from "../interfaces";
import TextField from "./fields/textField";
import { ReactComponent as Right } from "../icons/arrowRight.svg";
import "./accountMenu.css";
import { makeRequest } from "../utils";
import AsyncButton from "./buttons/asyncButton";

interface AccountMenuProps extends ViewProps {
  accountDetails: AccountDetails;
  hideMenu: () => void;
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

  post = async (): Promise<void> => {
    const { email, firstName, lastName, phoneNumber } = this.state;
    const body = {
      email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber
    };

    const opts = { method: "POST", body: JSON.stringify(body) };

    await makeRequest("/db/edit-account-details", opts)
      .then(this.handleSuccess)
      .catch(this.handleFailure);
  };

  setPassword = (): Promise<ResponseBody> => {
    const { setPassword, confirmPassword } = this.state;
    if (!(setPassword == confirmPassword)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPassword });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  };

  trySetPassword = async (): Promise<void> => {
    this.setPassword().then(this.handleSuccess, this.handleFailure);
  };

  handleSuccess = (res: ResponseBody) => {
    const { flashMessage } = this.props;
    flashMessage(<span>{res.msg}</span>, "success");
    this.setState({ edit: false, editPassword: false });
  };

  handleFailure = (res: ResponseBody) => {
    const { flashMessage } = this.props;

    const msg = (
      <span>
        <b>An unexpected error occured</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  };

  hide = () => {
    this.props.hideMenu();
    this.setState({
      ...this.props.accountDetails,
      edit: false,
      editPassword: false,
      setPassword: "",
      confirmPassword: ""
    });
  };

  logout = async (): Promise<void> => {
    await makeRequest("/iam/logout", { method: "POST" });
    location.reload();
  };

  render() {
    const { edit, editPassword, email, firstName, lastName, phoneNumber } =
      this.state;

    return (
      <div className="account-menu-container bg-white border-light-l">
        <div className="account-menu-content">
          <div className="account-menu-button">
            <span>
              <b>Account Details</b>
            </span>
            {edit ? (
              <AsyncButton onClick={this.post} text="Save" type="primary" />
            ) : (
              <button
                className="button-primary"
                onClick={() => this.setState({ edit: true })}
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
          <div className="account-menu-field">
            {edit ? (
              <TextField
                id="phoneNumber"
                label="Phone Number"
                prefill={phoneNumber}
                onKeyup={(text: string) => this.setState({ phoneNumber: text })}
              ></TextField>
            ) : (
              <span>
                <b>Phone Number</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{phoneNumber}
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
              <AsyncButton
                onClick={this.trySetPassword}
                text="Save"
                type="primary"
              />
            ) : (
              <button
                className="button-primary"
                onClick={() => this.setState({ editPassword: true })}
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
          <div
            className="border-light-b"
            style={{ marginBottom: "2rem" }}
          ></div>
          <div className="logout-button">
            <button className="button-danger" onClick={this.logout}>
              Logout
            </button>
          </div>
        </div>
        <div className="account-menu-footer bg-dark" onClick={this.hide}>
          <Right />
        </div>
      </div>
    );
  }
}

export default AccountMenu;
