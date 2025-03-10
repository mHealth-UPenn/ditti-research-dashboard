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

import { RefObject } from "react";
import { useState } from "react";
import { AccountDetails, ResponseBody } from "../interfaces";
import TextField from "./fields/textField";
import { makeRequest } from "../utils";
import AsyncButton from "./buttons/asyncButton";
import Button from "./buttons/button";
import { useAuth } from "../hooks/useAuth";
import { useFlashMessageContext } from "../contexts/flashMessagesContext";

/**
 * accountDetails: the current user's data
 * hideMenu: a function to hide the user menu
 */
interface AccountMenuProps {
  prefill: AccountDetails;
  accountMenuRef: RefObject<HTMLDivElement>;
  hideMenu: () => void;
}

const AccountMenu = ({
  prefill,
  accountMenuRef,
}: AccountMenuProps) => {
  const [email, setEmail] = useState(prefill.email);
  const [firstName, setFirstName] = useState(prefill.firstName);
  const [lastName, setLastName] = useState(prefill.lastName);
  const [phoneNumber, setPhoneNumber] = useState(prefill.phoneNumber);
  const [passwordValue, setPasswordValue] = useState("");
  const [confirmPasswordValue, setConfirmPasswordValue] = useState("");
  const [edit, setEdit] = useState(false);
  const [editPassword, setEditPassword] = useState(false);

  const { iamLogout } = useAuth();
  const { flashMessage } = useFlashMessageContext();

  /**
   * Make a POST request with changes
   */
  const post = async () => {
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
  }

  /**
   * Set a user's password during their first login
   * @returns - A response from the set password endpoint
   */
  const setPassword = () => {
    // if the user's password doesn't match the confirm password field
    if (!(passwordValue === confirmPasswordValue)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPasswordValue });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  }

  const trySetPassword = () => setPassword().then(handleSuccess, handleFailure);

  /**
   * Handle a successful response
   * @param res - The response from the login endpoint
   */
  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");
    setEdit(false);
    setEditPassword(false);
  }

  /**
   * Handle a failed response
   * @param res - The response from the login endpoint
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message from the server or "Internal server error"
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {res.msg ? res.msg : "Internal server error"}
      </span>
    );

    flashMessage(msg, "danger");
    setEdit(false);
    setEditPassword(false);
  }

  return (
    <div
      ref={accountMenuRef}
      className="absolute right-0 top-16 w-0 max-w-[100vw] h-[calc(100vh-4rem)] overflow-scroll z-20 bg-white border-light border-l overflow-x-hidden [@media(min-width:383px)]:bg-red [@media(min-width:383px)]:transition-[width] [@media(min-width:383px)]:duration-500">
        <div className="p-8 w-[24rem]">
          <div className="flex items-center justify-between pb-6 mb-6 border-b border-light">
            <span>Account Details</span>
            {edit ? (
              <AsyncButton size="sm" onClick={post} rounded={true}>Save</AsyncButton>
            ) : (
              <Button
                variant="tertiary"
                size="sm"
                onClick={() => setEdit(true)}
                rounded={true}>
                  Edit
              </Button>
            )}
          </div>
          <div className="mb-4">
            {edit ? (
              <TextField
                id="firstName"
                label="First Name"
                value={firstName}
                onKeyup={setFirstName} />
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
                value={lastName}
                onKeyup={setLastName} />
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
                value={email}
                onKeyup={setEmail} />
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
                value={phoneNumber}
                onKeyup={setPhoneNumber} />
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
            <span>Change password</span>
            {editPassword ?
              <AsyncButton size="sm" onClick={trySetPassword} rounded={true}>Save</AsyncButton> :
              <Button
                variant="tertiary"
                size="sm"
                onClick={() => setEditPassword(true)}
                rounded={true}>
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
                  onKeyup={setPasswordValue}
                  value={passwordValue} />
              </div>
              <div className="mb-6">
                <TextField
                  id="confirmPassword"
                  label="Confirm your password"
                  type="password"
                  onKeyup={setConfirmPasswordValue}
                  value={confirmPasswordValue} />
              </div>
            </>
          }
          <div className="border-light border-b mb-6" />
          <div className="flex items-center justify-between">
            <span>Logout</span>
            <Button variant="danger" size="sm" onClick={iamLogout} rounded={true}>
              Logout
            </Button>
          </div>
        </div>
    </div>
  );
};

export default AccountMenu;
