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
 * Account menu props interface
 */
interface AccountMenuProps {
  prefill: AccountDetails;
  accountMenuRef: RefObject<HTMLDivElement>;
  hideMenu: () => void;
}

/**
 * Password error type to handle validation
 */
type PasswordError = 
  | "PASSWORDS_DONT_MATCH" 
  | "CURRENT_PASSWORD_REQUIRED" 
  | null;

/**
 * Account Menu component for managing user account details and password
 */
const AccountMenu = ({
  prefill,
  accountMenuRef,
  hideMenu,
}: AccountMenuProps) => {
  // Account details state
  const [email, setEmail] = useState(prefill.email);
  const [firstName, setFirstName] = useState(prefill.firstName);
  const [lastName, setLastName] = useState(prefill.lastName);
  const [phoneNumber, setPhoneNumber] = useState(prefill.phoneNumber || "");
  
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
  const { flashMessage } = useFlashMessageContext();

  /**
   * Make a POST request with account detail changes
   */
  const post = async () => {
    // Validate required fields
    if (!firstName.trim()) {
      flashMessage(<span>First name is required</span>, "danger");
      return;
    }
    
    if (!lastName.trim()) {
      flashMessage(<span>Last name is required</span>, "danger");
      return;
    }
    
    if (!email.trim()) {
      flashMessage(<span>Email is required</span>, "danger");
      return;
    }
    
    // Phone number is optional, so no validation needed
    
    const body = {
      email,
      first_name: firstName,
      last_name: lastName,
      phone_number: phoneNumber, // This will be empty if not provided
    };

    const opts = { 
      method: "POST", 
      body: JSON.stringify(body),
      headers: {
        "Content-Type": "application/json"
      }
    };
    
    await makeRequest("/db/edit-account-details", opts)
      .then(handleSuccess)
      .catch(handleFailure);
  }

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
   * @returns A response from the change password endpoint
   */
  const setPassword = async () => {
    // Clear any previous errors
    setPasswordError(null);
    
    // Validate password
    const error = validatePassword();
    if (error) {
      setPasswordError(error);
      throw getErrorMessage(error);
    }
    
    // Prepare request body - both passwords are always required
    // Cognito requires the previous password for all password changes
    const body: Record<string, string> = {
      newPassword: passwordValue,
      previousPassword: currentPassword
    };
    
    // Set up request options
    const opts: RequestInit = { 
      method: "POST", 
      body: JSON.stringify(body),
      credentials: "include", // Ensure cookies are sent with the request
      headers: {
        "Content-Type": "application/json"
      }
    };
    
    return makeRequest("/auth/researcher/change-password", opts);
  }

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
  const trySetPassword = () => setPassword().then(handleSuccess, handleFailure);

  /**
   * Handle a successful response
   * @param res - The response from the API
   */
  const handleSuccess = (res: ResponseBody) => {
    flashMessage(<span>{res.msg}</span>, "success");
    resetForm();
    hideMenu();
  }

  /**
   * Handle a failed response
   * @param res - The error response from the API
   */
  const handleFailure = (res: ResponseBody | Error) => {
    // Format error message
    const errorMessage = res instanceof Error ? res.message : (res.msg || "Internal server error");
    
    const msg = (
      <span>
        <b>An unexpected error occurred</b>
        <br />
        {errorMessage}
      </span>
    );

    flashMessage(msg, "danger");
    
    // Only reset edit states, not the password fields to allow user to fix errors
    setEdit(false);
    setEditPassword(false);
  }

  /**
   * Reset form state and clear sensitive data
   */
  const resetForm = () => {
    setEdit(false);
    setEditPassword(false);
    clearSensitiveData();
  }

  /**
   * Clear all sensitive data fields
   */
  const clearSensitiveData = () => {
    setCurrentPassword("");
    setPasswordValue("");
    setConfirmPasswordValue("");
    setPasswordError(null);
  }

  /**
   * Get error feedback message for password fields
   */
  const getPasswordErrorFeedback = (errorType: PasswordError): string => {
    return errorType ? getErrorMessage(errorType) : "";
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
                  id="currentPassword"
                  label="Current password"
                  type="password"
                  onKeyup={setCurrentPassword}
                  value={currentPassword}
                  feedback={passwordError === "CURRENT_PASSWORD_REQUIRED" ? getPasswordErrorFeedback(passwordError) : ""} />
              </div>
              <div className="mb-4">
                <TextField
                  id="newPassword"
                  label="Enter a new password"
                  type="password"
                  onKeyup={setPasswordValue}
                  value={passwordValue}
                  description=""
                  feedback={passwordError === "PASSWORDS_DONT_MATCH" ? getPasswordErrorFeedback(passwordError) : ""} />
              </div>
              <div className="mb-6">
                <TextField
                  id="confirmPassword"
                  label="Confirm your password"
                  type="password"
                  onKeyup={setConfirmPasswordValue}
                  value={confirmPasswordValue}
                  feedback={passwordError === "PASSWORDS_DONT_MATCH" ? getPasswordErrorFeedback(passwordError) : ""} />
              </div>
            </>
          }
          <div className="border-light border-b mb-6" />
          <div className="flex items-center justify-between">
            <span>Logout</span>
            <Button variant="danger" size="sm" onClick={researcherLogout} rounded={true}>
              Logout
            </Button>
          </div>
        </div>
    </div>
  );
};

export default AccountMenu;
