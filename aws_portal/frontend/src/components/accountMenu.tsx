import * as React from "react";
import { useState, useCallback } from "react";
import { AccountDetails, ResponseBody, ViewProps } from "../interfaces";
import TextField from "./fields/textField";
import { ReactComponent as Right } from "../icons/arrowRight.svg";
import "./accountMenu.css";
import { makeRequest } from "../utils";
import { useAuth } from "../hooks/useAuth";
import AsyncButton from "./buttons/asyncButton";

/**
 * accountDetails: the current user's data
 * hideMenu: a function to hide the user menu
 */
interface AccountMenuProps extends ViewProps {
  accountDetails: AccountDetails;
  hideMenu: () => void;
}

const AccountMenu: React.FC<AccountMenuProps> = (props) => {
  const [state, setState] = useState({
    ...props.accountDetails,
    setPassword: "",
    confirmPassword: "",
    edit: false,
    editPassword: false,
  });

  const { iamLogout } = useAuth();

  /**
   * Make a POST request with changes
   */
  const post = useCallback(async (): Promise<void> => {
    const { email, firstName, lastName, phoneNumber } = state;
    const body = {
      email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber,
    };

    const opts = { method: "POST", body: JSON.stringify(body) };

    await makeRequest("/db/edit-account-details", opts)
      .then(handleSuccess)
      .catch(handleFailure);
  }, [state]);

  /**
   * Set a user's password during their first login
   * @returns - A response from the set password endpoint
   */
  const setPassword = useCallback((): Promise<ResponseBody> => {
    const { setPassword, confirmPassword } = state;

    // if the user's password doesn't match the confirm password field
    if (!(setPassword === confirmPassword)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPassword });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  }, [state]);

  const trySetPassword = useCallback(async (): Promise<void> => {
    setPassword().then(handleSuccess, handleFailure);
  }, [setPassword]);

  /**
   * Handle a successful response
   * @param res - The response from the login endpoint
   */
  const handleSuccess = useCallback((res: ResponseBody) => {
    const { flashMessage } = props;
    flashMessage(<span>{res.msg}</span>, "success");
    setState((prevState) => ({ ...prevState, edit: false, editPassword: false }));
  }, [props]);

  /**
   * Handle a failed response
   * @param res - The response from the login endpoint
   */
  const handleFailure = useCallback((res: ResponseBody) => {
    const { flashMessage } = props;

    // flash the message from the server or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
  }, [props]);

  /**
   * Hide the account menu
   */
  const hide = useCallback(() => {
    props.hideMenu();
    setState({
      ...props.accountDetails,
      edit: false,
      editPassword: false,
      setPassword: "",
      confirmPassword: "",
    });
  }, [props]);

  const { edit, editPassword, email, firstName, lastName, phoneNumber } = state;

  return (
    <div className="account-menu-container bg-white border-light-l">
      <div className="account-menu-content">
        <div className="account-menu-button">
          <span>
            <b>Account Details</b>
          </span>
          {edit ? (
            <AsyncButton onClick={post} text="Save" type="primary" />
          ) : (
            <button
              className="button-primary"
              onClick={() => setState((prevState) => ({ ...prevState, edit: true }))}
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
              onKeyup={(text: string) => setState((prevState) => ({ ...prevState, firstName: text }))}
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
              onKeyup={(text: string) => setState((prevState) => ({ ...prevState, lastName: text }))}
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
              onKeyup={(text: string) => setState((prevState) => ({ ...prevState, email: text }))}
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
              onKeyup={(text: string) => setState((prevState) => ({ ...prevState, phoneNumber: text }))}
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
              onClick={trySetPassword}
              text="Save"
              type="primary"
            />
          ) : (
            <button
              className="button-primary"
              onClick={() => setState((prevState) => ({ ...prevState, editPassword: true }))}
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
                  setState((prevState) => ({ ...prevState, setPassword: text }))
                }
              ></TextField>
            </div>
            <div className="account-menu-field">
              <TextField
                id="confirmPassword"
                label="Confirm your password"
                type="password"
                onKeyup={(text: string) =>
                  setState((prevState) => ({ ...prevState, confirmPassword: text }))
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
          <button className="button-danger" onClick={iamLogout}>
            Logout
          </button>
        </div>
      </div>
      <div className="account-menu-footer bg-dark" onClick={hide}>
        <Right />
      </div>
    </div>
  );
};

export default AccountMenu;
