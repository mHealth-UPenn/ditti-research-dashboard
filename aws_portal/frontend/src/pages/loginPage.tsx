import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "../utils";
import { ResponseBody } from "../interfaces";
import TextField from "../components/fields/textField";
import { ReactComponent as Person } from "../icons/person.svg";
import { ReactComponent as Key } from "../icons/key.svg";
import { FullLoader } from "../components/loader";
import AsyncButton from "../components/buttons/asyncButton";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import "./loginPage.css";

/**
 * LoginPage component for IAM authentication
 */
const LoginPage: React.FC = () => {
  const [flashMessages, setFlashMessages] = useState<{ id: number; element: React.ReactElement }[]>([]);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [setPasswordField, setSetPasswordField] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [fading, setFading] = useState<boolean>(false);
  const loadingDb = useDbStatus();
  const navigate = useNavigate();

  const {
    isIamAuthenticated,
    firstLogin,
    isIamLoading,
    iamLogin,
    setFirstLogin
  } = useAuth();

  /**
   * Triggers fade effect when loading changes
   */
  useEffect(() => {
    if (!isIamLoading && !loadingDb) {
      setFading(true);
      setTimeout(() => setFading(false), 500);
    }
  }, [isIamLoading, loadingDb]);

  /**
   * Redirects authenticated IAM users to the Research Coordinator Dashboard
   */
  useEffect(() => {
    if (isIamAuthenticated && !firstLogin) {
      navigate("/coordinator");
    }
  }, [isIamAuthenticated, firstLogin, navigate]);

  /**
   * Attempts to log the IAM user in
   */
  const tryLogIn = async (): Promise<void> => {
    try {
      await iamLogin(email, password);
    } catch (error) {
      const errorMessage = (error as { msg?: string }).msg;
      const msg = <span>{errorMessage ? errorMessage : "Internal server error"}</span>;
      flashMessage(msg, "danger");
    }
  };

  /**
   * Sets a new password during the first login
   */
  const trySetPassword = async (): Promise<void> => {
    if (setPasswordField !== confirmPassword) {
      flashMessage(<span>Passwords do not match</span>, "danger");
      return;
    }
    const body = JSON.stringify({ password: setPasswordField });
    const opts = { method: "POST", body };
    try {
      const res: ResponseBody = await makeRequest("/iam/set-password", opts);
      if (res.msg === "Password set successfully") {
        setFirstLogin(false);
        navigate("/coordinator");
      } else {
        flashMessage(<span>{res.msg}</span>, "danger");
      }
    } catch (error) {
      const msg = <span>{(error as { msg?: string }).msg || "Internal server error"}</span>;
      flashMessage(msg, "danger");
    }
  };

  /**
   * Adds a flash message to be displayed on the screen
   */
  const flashMessage = (msg: React.ReactElement, type: string): void => {
    const id = flashMessages.length ? flashMessages[flashMessages.length - 1].id + 1 : 0;
    const element = (
      <div key={id} className={`shadow flash-message flash-message-${type}`}>
        <div className="flash-message-content">
          <span>{msg}</span>
        </div>
        <div className="flash-message-close" onClick={() => popMessage(id)}>
          <span>x</span>
        </div>
      </div>
    );
    setFlashMessages([...flashMessages, { id, element }]);
  };

  /**
   * Removes a flash message by ID
   */
  const popMessage = (id: number): void => {
    setFlashMessages(flashMessages.filter((fm) => fm.id !== id));
  };

  const setPasswordFields = (
    <>
      <div className="login-field">
        <TextField
          id="set-password"
          type="password"
          placeholder="To log in, please enter a new password"
          onKeyup={(text: string) => setSetPasswordField(text)}
          onKeyDown={(e) => e.key === "Enter" && trySetPassword()}
          value={setPasswordField}
        >
          <Key />
        </TextField>
      </div>
      <div className="login-field">
        <TextField
          id="confirm-password"
          type="password"
          placeholder="Confirm your password"
          onKeyup={(text: string) => setConfirmPassword(text)}
          onKeyDown={(e) => e.key === "Enter" && trySetPassword()}
          value={confirmPassword}
        >
          <Key />
        </TextField>
      </div>
      <div className="login-buttons">
        <button className="button-primary button-lg" onClick={trySetPassword}>
          Set password
        </button>
      </div>
    </>
  );

  const loginFields = (
    <>
      <div className="login-field">
        <TextField
          id="login-email"
          placeholder="Email"
          onKeyup={(text: string) => setEmail(text)}
          onKeyDown={(e) => e.key === "Enter" && tryLogIn()}
          value={email}
        >
          <Person />
        </TextField>
      </div>
      <div className="login-field">
        <TextField
          id="login-password"
          type="password"
          placeholder="Password"
          onKeyup={(text: string) => setPassword(text)}
          onKeyDown={(e) => e.key === "Enter" && tryLogIn()}
          value={password}
        >
          <Key />
        </TextField>
      </div>
      <div className="login-buttons">
        <AsyncButton text="Sign In" type="primary" onClick={tryLogIn} />
      </div>
    </>
  );

  const page = (
    <div className="flex h-screen lg:mx-[6rem] xl:mx-[10rem] 2xl:mx-[20rem] bg-light">
      <div className="login-image-container">
        <img
          className="hidden lg:flex login-image"
          src={`${process.env.PUBLIC_URL}/logo.png`}
          alt="Logo"
        />
      </div>
      <div className="login-menu bg-white">
        <div className="login-menu-content">
          <h1>Geriatric Sleep Research Lab</h1>
          <h3>AWS Data Portal</h3>
          <div className="login-flash-message-container">
            {flashMessages.map((fm) => fm.element)}
          </div>
          {firstLogin ? setPasswordFields : loginFields}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {(isIamLoading || loadingDb || fading) && (
        <FullLoader
          loading={isIamLoading || loadingDb}
          msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""}
        />
      )}
      {(!isIamAuthenticated || firstLogin) && page}
    </>
  );
};

export default LoginPage;
