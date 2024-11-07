import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "./utils";
import { ResponseBody } from "./interfaces";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import { FullLoader } from "./components/loader";
import AsyncButton from "./components/buttons/asyncButton";
import { useAuth } from "./hooks/useAuth";
import "./loginPage.css";

/**
 * LoginPage component
 */
const LoginPage: React.FC = () => {
  const [flashMessages, setFlashMessages] = useState<{ id: number; element: React.ReactElement }[]>([]);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [setPasswordField, setSetPasswordField] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [loadingDb, setLoadingDb] = useState<boolean>(false);
  const [fading, setFading] = useState<boolean>(false);

  const {
    isAuthenticated,
    firstLogin,
    isLoading,
    login,
    setFirstLogin,
    csrfToken,
    setCsrfToken,
  } = useAuth();
  const navigate = useNavigate();

  /**
   * Checks app's status on component mount
   */
  useEffect(() => {
    touch().then((msg: string) => {
      if (msg !== "OK") {
        setLoadingDb(true);
        const id: ReturnType<typeof setInterval> = setInterval(() => touch(id), 2000);
      }
    });
  }, []);

  /**
   * Triggers fade effect when loading changes
   */
  useEffect(() => {
    if (!isLoading && !loadingDb) {
      setFading(true);
      setTimeout(() => setFading(false), 500);
    }
  }, [isLoading, loadingDb]);

  /**
   * Touches the server endpoint to check if the app is ready
   */
  const touch = async (id?: ReturnType<typeof setInterval>): Promise<string> => {
    try {
      const res: ResponseBody = await makeRequest("/touch");
      if (res.msg === "OK" && id) clearInterval(id);
      return res.msg;
    } catch (error) {
      return "Error";
    }
  };

  /**
   * Attempts to log the user in
   */
  const tryLogIn = async (): Promise<void> => {
    try {
      await login(email, password);
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
        navigate("/");
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
      {(isLoading || loadingDb || fading) && (
        <FullLoader
          loading={isLoading || loadingDb}
          msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""}
        />
      )}
      {(!isAuthenticated || firstLogin) && page}
    </>
  );
};

export default LoginPage;
