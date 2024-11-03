import React, { RefObject } from "react";
import { useState, useCallback } from "react";
import { AccountDetails, ResponseBody, ViewProps } from "../interfaces";
import TextField from "./fields/textField";
import { ReactComponent as Right } from "../icons/arrowRight.svg";
import "./accountMenu.css";
import { makeRequest } from "../utils";
import AsyncButton from "./buttons/asyncButton";
import Button from "./buttons/button";

/**
 * accountDetails: the current user's data
 * hideMenu: a function to hide the user menu
 */
interface AccountMenuProps extends ViewProps {
  accountDetails: AccountDetails;
  accountMenuRef: RefObject<HTMLDivElement>;
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

  /**
   * Logout the user
   */
  const logout = useCallback(async (): Promise<void> => {
    localStorage.removeItem("jwt");
    // refresh the window to show the login page
    location.reload();
  }, []);

  const { edit, editPassword, email, firstName, lastName, phoneNumber } = state;

  return (
    <div
      ref={props.accountMenuRef}
      className="absolute right-[-24rem] top-16 w-[24rem] h-[calc(100vh-4rem)] overflow-scroll z-20 bg-white border-light border-l transition-all duration-500">
        <div className="p-8">
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-light">
            <p>Account Details</p>
            {edit ? (
              <AsyncButton size="sm" onClick={post}>Save</AsyncButton>
            ) : (
              <Button
                variant="primary"
                size="sm"
                onClick={() => setState((prevState) => ({ ...prevState, edit: true }))}>
                  Edit
              </Button>
            )}
          </div>
          <div className="mb-4">
            {edit ? (
              <TextField
                id="firstName"
                label="First Name"
                prefill={firstName}
                onKeyup={(text: string) => setState((prevState) => ({ ...prevState, firstName: text }))} />
            ) : (
              <span>
                <b>First Name</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{firstName}
              </span>
            )}
          </div>
          <div className="mb-4">
            {edit ? (
              <TextField
                id="lastName"
                label="Last Name"
                prefill={lastName}
                onKeyup={(text: string) => setState((prevState) => ({ ...prevState, lastName: text }))} />
            ) : (
              <span>
                <b>Last Name</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{lastName}
              </span>
            )}
          </div>
          <div className="mb-4">
            {edit ? (
              <TextField
                id="email"
                label="Email"
                prefill={email}
                onKeyup={(text: string) => setState((prevState) => ({ ...prevState, email: text }))} />
            ) : (
              <span>
                <b>Email</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{email}
              </span>
            )}
          </div>
          <div className="mb-6">
            {edit ? (
              <TextField
                id="phoneNumber"
                label="Phone Number"
                prefill={phoneNumber}
                onKeyup={(text: string) => setState((prevState) => ({ ...prevState, phoneNumber: text }))} />
            ) : (
              <span>
                <b>Phone Number</b>
                <br />
                &nbsp;&nbsp;&nbsp;&nbsp;{phoneNumber}
              </span>
            )}
          </div>
          <div className="border-b border-light mb-6" />
          <div className="flex items-center justify-between mb-6">
            <p>Change password</p>
            {editPassword ?
              <AsyncButton size="sm" onClick={trySetPassword}>Save</AsyncButton> :
              <Button
                variant="primary"
                size="sm"
                onClick={() => setState((prevState) => ({ ...prevState, editPassword: true }))} >
                  Change
              </Button>
            }
          </div>
          {editPassword &&
            <>
              <div className="mb-4">
                <TextField
                  id="setPassword"
                  label="Enter a new password"
                  type="password"
                  onKeyup={(text: string) =>
                    setState((prevState) => ({ ...prevState, setPassword: text }))
                  } />
              </div>
              <div className="mb-6">
                <TextField
                  id="confirmPassword"
                  label="Confirm your password"
                  type="password"
                  onKeyup={(text: string) =>
                    setState((prevState) => ({ ...prevState, confirmPassword: text }))
                  } />
              </div>
            </>
          }
          <div className="border-light border-b mb-6" />
          <div className="flex items-center justify-between">
            <p>Logout</p>
            <Button variant="danger" size="sm" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
    </div>
  );
};

export default AccountMenu;
