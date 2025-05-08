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

import { useState } from "react";
import { ResponseBody } from "../../types/api";
import { TextField } from "../fields/textField";
import { formatPhoneNumber } from "../../utils";
import { useHttpClient } from "../../lib/HttpClientContext";
import { AsyncButton } from "../buttons/asyncButton";
import { Button } from "../buttons/button";
import { useAuth } from "../../hooks/useAuth";
import { useFlashMessages } from "../../hooks/useFlashMessages";
import { AccountMenuProps, PasswordError } from "./accountMenu.types";
import { HttpError } from "../../lib/http.types";

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
  const { request } = useHttpClient();

  // Handle phone number change with formatting
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
   * Make a POST request with account detail changes
   */
  const post = async () => {
    // Validate required fields
    if (!firstName.trim()) {
      flashMessage(
        <span>
          <b>First name is required</b>
        </span>,
        "danger"
      );
      return;
    }

    if (!lastName.trim()) {
      flashMessage(
        <span>
          <b>Last name is required</b>
        </span>,
        "danger"
      );
      return;
    }

    if (!email.trim()) {
      flashMessage(
        <span>
          <b>Email is required</b>
        </span>,
        "danger"
      );
      return;
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
        return;
      }
    }

    const body = {
      app: 2,
      email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber, // Will be properly formatted or empty string
    };

    const opts = {
      method: "POST",
      data: body,
    };

    await request<ResponseBody>("/db/edit-account-details", opts)
      .then(handleSuccess)
      .catch(handleFailure);
  };

  /**
   * Validate password requirements
   * @returns A password error or null if validation passes
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
   * Change an existing password
   * @returns A response from the change password endpoint or null if validation fails
   */
  const setPassword = async () => {
    // Clear any previous errors
    setPasswordError(null);

    // Validate password
    const error = validatePassword();
    if (error) {
      setPasswordError(error);
      // Display the validation error directly through the flash message
      // instead of throwing an error
      flashMessage(<span>{getErrorMessage(error)}</span>, "danger");
      // Return null to indicate validation failed without throwing an error
      return null;
    }

    // Prepare request body - both passwords are always required
    // Cognito requires the previous password for all password changes
    const body: Record<string, string> = {
      newPassword: passwordValue,
      previousPassword: currentPassword,
    };

    // Set up request options
    const opts = {
      method: "POST",
      data: body,
    };

    return request<ResponseBody>("/auth/researcher/change-password", opts);
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
   * Attempt to set the password and handle success/failure
   */
  const trySetPassword = async () => {
    try {
      // Since setPassword now returns null on validation error, handle that case
      const result = await setPassword();
      if (result) {
        // Only handle success if we got a proper response
        handleSuccess(result);
      }
    } catch (error) {
      // Handle any errors, including LIMIT_EXCEEDED
      handleFailure(error);
    }
  };

  /**
   * Handle a successful response
   * @param res - The response from the API
   */
  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");
    resetForm();
    hideMenu();
  };

  /**
   * Handle a failed response from the server API (not local validation)
   * @param error - The error from the API
   */
  const handleFailure = (error: unknown) => {
    let displayMessage = "An unexpected error occurred.";
    let backendCode: string | undefined = undefined;
    let isAuthError = false;
    let isClientSideError = false; // Flag for non-HTTP/backend errors

    try {
      if (error instanceof HttpError && error.apiError) {
        displayMessage = error.message; // Start with the HttpError/Axios message

        if (error.apiError.data) {
          // Prefer the specific message from the backend response body if available
          if (error.apiError.data.msg) {
            displayMessage = error.apiError.data.msg;
          }
          if (error.apiError.data.code) {
            backendCode = error.apiError.data.code;
          }
        }

        // Determine if it's an authentication error based on backend code or HTTP status
        isAuthError =
          (!!backendCode &&
            (backendCode.includes("AUTH_") ||
              backendCode === "SESSION_EXPIRED" ||
              backendCode === "FORBIDDEN")) ||
          error.apiError.status === 401 ||
          error.apiError.status === 403;
      } else if (error instanceof Error) {
        // It's a standard JavaScript Error
        displayMessage = error.message;
        isClientSideError = true;
      } else {
        // It's something else entirely
        console.error("Caught non-Error throwable in handleFailure:", error);
        // displayMessage remains the default
      }

      let msgElement: React.ReactElement;

      if (isAuthError) {
        msgElement = (
          <span>
            <b>Authentication Error</b>
            <br />
            {displayMessage}
          </span>
        );
      } else if (backendCode) {
        // Use the direct message for specific, non-auth backend errors
        msgElement = <span>{displayMessage}</span>;
      } else {
        // Fallback for generic HttpErrors, client-side Errors, or unknown throwables
        const errorTitle = isClientSideError
          ? "Error"
          : "An unexpected error occurred";
        msgElement = (
          <span>
            <b>{errorTitle}</b>
            <br />
            {displayMessage}
          </span>
        );
      }

      flashMessage(msgElement, "danger");

      console.error("API call failed or error occurred:", error);
    } catch (handlerError) {
      console.error("Error in error handler:", handlerError);
      flashMessage(<span>An error occurred. Please try again.</span>, "danger");
    } finally {
      if (editPassword) {
        // Stay in password edit mode if the error occurred there
      } else {
        setEdit(false); // Exit general edit mode on failure
      }
    }
  };

  /**
   * Reset the form state to initial values without submitting any changes
   */
  const resetForm = () => {
    // Reset account details to prefill values
    setFirstName(prefill.firstName);
    setLastName(prefill.lastName);
    setEmail(prefill.email);
    setPhoneNumber(prefill.phoneNumber ?? "");
    setPhoneNumberError("");

    // Reset password fields
    setCurrentPassword("");
    setPasswordValue("");
    setConfirmPasswordValue("");
    setPasswordError(null);

    // Exit edit modes
    setEdit(false);
    setEditPassword(false);
  };

  /**
   * Get error feedback message for password fields
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
