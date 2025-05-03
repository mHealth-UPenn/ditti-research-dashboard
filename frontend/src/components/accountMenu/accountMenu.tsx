/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import { useState, useCallback } from "react";
import { ResponseBody } from "../../types/api";
import { TextField } from "../fields/textField";
import { formatPhoneNumber } from "../../utils";
import { httpClient } from "../../lib/http";
import { AsyncButton } from "../buttons/asyncButton";
import { Button } from "../buttons/button";
import { useAuth } from "../../hooks/useAuth";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { useApiHandler } from "../../hooks/useApiHandler";
import { AccountMenuProps, PasswordError } from "./accountMenu.types";

/**
 * Account Menu component for managing user account details and password
 */
export const AccountMenu = ({
  prefill,
  accountMenuRef,
  hideMenu,
}: AccountMenuProps) => {
  // Account details state
  const [email, setEmail] = useState(prefill.email);
  const [firstName, setFirstName] = useState(prefill.firstName);
  const [lastName, setLastName] = useState(prefill.lastName);
  const [phoneNumber, setPhoneNumber] = useState(prefill.phoneNumber ?? "");
  const [phoneNumberError, setPhoneNumberError] = useState<string>("");

  // Password state
  const [currentPassword, setCurrentPassword] = useState("");
  const [passwordValue, setPasswordValue] = useState("");
  const [confirmPasswordValue, setConfirmPasswordValue] = useState("");
  const [passwordError, setPasswordError] = useState<PasswordError>(null);

  // UI state
  const [edit, setEdit] = useState(false);
  const [editPassword, setEditPassword] = useState(false);

  // Hooks
  const { researcherLogout } = useAuth();
  const { flashMessage } = useFlashMessages();

  // Setup API handler with success/error callbacks
  const { safeRequest } = useApiHandler<ResponseBody>({
    onSuccess: (res) => {
      flashMessage(<span>{res.msg}</span>, "success");
      resetForm(); // Reset form and hide menu on success
    },
    onError: () => {
      // Hook handles general error messages.
      // Component-specific logic on error:
      if (editPassword) {
        // Keep password edit open if change fails
      } else {
        setEdit(false); // Reset details edit state on failure
      }
    },
  });

  // Format and validate phone number input
  const handlePhoneNumberChange = (value: string) => {
    const formattedNumber = formatPhoneNumber(value);
    setPhoneNumber(formattedNumber);

    // Validate the phone number format
    if (formattedNumber && !/^\+[1-9]\d*$/.test(formattedNumber)) {
      setPhoneNumberError(
        "Phone number must start with + followed by country code and digits"
      );
    } else {
      setPhoneNumberError("");
    }
  };

  /**
   * Resets the form state to initial prefill values and closes the menu.
   */
  const resetForm = useCallback(() => {
    setFirstName(prefill.firstName);
    setLastName(prefill.lastName);
    setEmail(prefill.email);
    setPhoneNumber(prefill.phoneNumber ?? "");
    setPhoneNumberError("");

    setCurrentPassword("");
    setPasswordValue("");
    setConfirmPasswordValue("");
    setPasswordError(null);

    setEdit(false);
    setEditPassword(false);
    hideMenu();
  }, [prefill, hideMenu]);

  /**
   * Validates and submits account detail changes.
   */
  const post = (): Promise<void> => {
    // --- Input Validation ---
    if (!firstName.trim()) {
      flashMessage(
        <span>
          <b>First name is required</b>
        </span>,
        "danger"
      );
      return Promise.resolve();
    }

    if (!lastName.trim()) {
      flashMessage(
        <span>
          <b>Last name is required</b>
        </span>,
        "danger"
      );
      return Promise.resolve();
    }

    if (!email.trim()) {
      flashMessage(
        <span>
          <b>Email is required</b>
        </span>,
        "danger"
      );
      return Promise.resolve();
    }

    // Validate phone number format if provided
    if (phoneNumber.trim()) {
      // International phone numbers should start with + followed by at least 1 digit for country code
      const phoneRegex = /^\+[1-9]\d*$/;
      if (!phoneRegex.test(phoneNumber)) {
        flashMessage(
          <span>
            <b>Invalid phone number format</b> - Phone number must start with +
            followed by country code and digits
          </span>,
          "danger"
        );
        return Promise.resolve();
      }
    }

    return safeRequest(async () => {
      const body = {
        app: 2,
        email,
        first_name: firstName,
        last_name: lastName,
        phone_number: phoneNumber,
      };
      return httpClient.request<ResponseBody>("/db/edit-account-details", {
        method: "POST",
        data: body,
      });
    }).then(() => undefined); // Adapt return type for AsyncButton
  };

  /**
   * Validates password fields.
   * @returns A password error code or null if validation passes.
   */
  const validatePassword = (): PasswordError => {
    // Check if passwords match
    if (passwordValue !== confirmPasswordValue) {
      return "PASSWORDS_DONT_MATCH";
    }

    // Always require current password for any password change
    // Cognito will validate this credential
    if (!currentPassword) {
      return "CURRENT_PASSWORD_REQUIRED";
    }

    return null;
  };

  /**
   * Validates and submits password change request.
   */
  const trySetPassword = (): Promise<void> => {
    setPasswordError(null);

    // Validate password
    const error = validatePassword();
    if (error) {
      setPasswordError(error);
      // Display the validation error directly through the flash message
      // instead of throwing an error
      flashMessage(<span>{getErrorMessage(error)}</span>, "danger");
      return Promise.resolve();
    }

    return safeRequest(async () => {
      const body: Record<string, string> = {
        newPassword: passwordValue,
        previousPassword: currentPassword,
      };
      return httpClient.request<ResponseBody>(
        "/auth/researcher/change-password",
        {
          method: "POST",
          data: body,
        }
      );
    }).then(() => undefined); // Adapt return type for AsyncButton
  };

  /**
   * Get readable error message from password error code
   */
  const getErrorMessage = (error: PasswordError): string => {
    switch (error) {
      case "PASSWORDS_DONT_MATCH":
        return "Passwords do not match";
      case "CURRENT_PASSWORD_REQUIRED":
        return "Current password is required";
      default:
        return "Unknown error";
    }
  };

  /**
   * Gets error feedback message for password input fields based on validation state.
   */
  const getPasswordErrorFeedback = (errorType: PasswordError): string => {
    return errorType ? getErrorMessage(errorType) : "";
  };

  return (
    <div
      ref={accountMenuRef}
      className="[@media(min-width:383px)]:bg-red absolute right-0 top-16 z-20
        h-[calc(100vh-4rem)] w-0 max-w-[100vw] overflow-scroll overflow-x-hidden
        border-l border-light bg-white
        [@media(min-width:383px)]:transition-[width]
        [@media(min-width:383px)]:duration-500"
    >
      <div className="w-96 p-8">
        <div
          className="mb-6 flex items-center justify-between border-b
            border-light pb-6"
        >
          <span>Account Details</span>
          {edit ? (
            <AsyncButton size="sm" onClick={post} rounded={true}>
              Save
            </AsyncButton>
          ) : (
            <Button
              variant="tertiary"
              size="sm"
              onClick={() => {
                setEdit(true);
              }}
              rounded={true}
            >
              Edit
            </Button>
          )}
        </div>
        <div className="mb-4">
          {edit ? (
            <div>
              <TextField
                id="email"
                label="Email"
                value={email}
                disabled={true}
              />

              <TextField
                id="first-name"
                label="First Name"
                value={firstName}
                onKeyup={setFirstName}
              />

              <TextField
                id="last-name"
                label="Last Name"
                value={lastName}
                onKeyup={setLastName}
              />

              <TextField
                id="phone-number"
                label="Phone Number"
                value={phoneNumber}
                onKeyup={handlePhoneNumberChange}
                feedback={phoneNumberError}
              />
            </div>
          ) : (
            <div>
              <div className="mb-4">
                <span>
                  <b>First Name</b>
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;{firstName}
                </span>
              </div>
              <div className="mb-4">
                <span>
                  <b>Last Name</b>
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;{lastName}
                </span>
              </div>
              <div className="mb-4">
                <span>
                  <b>Email</b>
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;{email}
                </span>
              </div>
              <div className="mb-4">
                <span>
                  <b>Phone Number</b>
                  <br />
                  &nbsp;&nbsp;&nbsp;&nbsp;{phoneNumber || "Not provided"}
                </span>
              </div>
            </div>
          )}
        </div>
        <div className="mb-6 border-b border-light" />
        <div className="mb-6 flex items-center justify-between">
          <span>Change password</span>
          {editPassword ? (
            <AsyncButton size="sm" onClick={trySetPassword} rounded={true}>
              Save
            </AsyncButton>
          ) : (
            <Button
              variant="tertiary"
              size="sm"
              onClick={() => {
                setEditPassword(true);
              }}
              rounded={true}
            >
              Change
            </Button>
          )}
        </div>
        {editPassword && (
          <>
            <div className="mb-4">
              <TextField
                id="currentPassword"
                label="Current password"
                type="password"
                onKeyup={setCurrentPassword}
                value={currentPassword}
                feedback={
                  passwordError === "CURRENT_PASSWORD_REQUIRED"
                    ? getPasswordErrorFeedback(passwordError)
                    : ""
                }
              />
            </div>
            <div className="mb-4">
              <TextField
                id="newPassword"
                label="Enter a new password"
                type="password"
                onKeyup={setPasswordValue}
                value={passwordValue}
                description=""
                feedback={
                  passwordError === "PASSWORDS_DONT_MATCH"
                    ? getPasswordErrorFeedback(passwordError)
                    : ""
                }
              />
            </div>
            <div className="mb-6">
              <TextField
                id="confirmPassword"
                label="Confirm your password"
                type="password"
                onKeyup={setConfirmPasswordValue}
                value={confirmPasswordValue}
                feedback={
                  passwordError === "PASSWORDS_DONT_MATCH"
                    ? getPasswordErrorFeedback(passwordError)
                    : ""
                }
              />
            </div>
          </>
        )}
        <div className="mb-6 border-b border-light" />
        <div className="flex items-center justify-between">
          <span>Logout</span>
          <Button
            variant="danger"
            size="sm"
            onClick={researcherLogout}
            rounded={true}
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
};
