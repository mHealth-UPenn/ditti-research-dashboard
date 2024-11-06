import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Buffer } from "buffer";
import { makeRequest } from "./utils";
import { ResponseBody } from "./interfaces";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import { FullLoader } from "./components/loader";
import AsyncButton from "./components/buttons/asyncButton";
import "./loginPage.css";


/**
 * flashMessages: messages to show above the login form fields
 * email: input in the email login field
 * password: input in the password login field
 * firstLogin: whether the user is logging in for the first time
 * loggedIn: whether the user is logged in
 * loading: whether to show the loading screen
 * loadingDb: whether the database is starting up
 * setPassword: input in the set password field during a user's first login
 * confirmPassword: input in the confirm password field during a user's first login
 * fading: whether to show the loading screen's 0.5 second fade-out
 */
const LoginPage: React.FC = () => {
  const [flashMessages, setFlashMessages] = useState<{ id: number; element: React.ReactElement }[]>([]);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [loggedIn, setLoggedIn] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingDb, setLoadingDb] = useState<boolean>(false);
  const [setPasswordField, setSetPasswordField] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [fading, setFading] = useState<boolean>(false);

  const navigate = useNavigate();

  useEffect(() => {
    // Check the app's status
    touch().then((msg: string) => {
      // If the app is not ready
      if (msg !== "OK") {
        // Show the database loading screen and try again every two seconds
        setLoadingDb(true);
        const id: ReturnType<typeof setInterval> = setInterval(() => touch(id), 2000);
      }
    });
  }, []);

  /**
   * Check the app's status
   * @param id - The interval id if called from setInterval (optional)
   * @returns - The message returned from the touch endpoint
   */
  const touch = async (id?: ReturnType<typeof setInterval>): Promise<string> => {
    return await makeRequest("/touch").then((res: ResponseBody) => {
      // If the app is ready
      if (res.msg === "OK") {
        // Clear the interval if touch is being called by setInterval
        if (id) clearInterval(id);
        // Check the user's login status
        checkLogIn();
      }
      return res.msg;
    });
  };

  /**
   * Check the user's login status
   */
  const checkLogIn = () => {
    makeRequest("/iam/check-login")
      .then((res: ResponseBody) => {
        if (res.msg === "Login successful") {
          setFirstLogin(false);
          setLoggedIn(true);
          navigate("/"); // Redirect to main app
        } 
        else if (res.msg === "First login") {
          setFirstLogin(true);
          setLoggedIn(true);
        } 
        else {
          setLoggedIn(false);
          localStorage.removeItem("jwt");
        }

        // Let the loading screen fade out for 0.5 seconds
        setLoading(false);
        setFading(true);
        setTimeout(() => setFading(false), 500);
      })
      .catch((res: ResponseBody) => {
        localStorage.removeItem("jwt");

        // If the user's token has expired
        if (res.msg === "Token has expired") {
          const msg = <span>Your session has expired. Please log in again</span>;
          flashMessage(msg, "danger");
        }

        // Let the loading screen fade out for 0.5 seconds
        setLoading(false);
        setFading(true);
        setLoggedIn(false);
        setTimeout(() => setFading(false), 500);
      });
  };

  /**
   * Log the user in
   * @returns - A response from the login endpoint
   */
  const logIn = (): Promise<ResponseBody> => {
    const auth = Buffer.from(email + ":" + password).toString("base64");
    const headers = { Authorization: "Basic " + auth };
    const opts = { method: "POST", headers: headers };
    return makeRequest("/iam/login", opts);
  };

  const tryLogIn = async (): Promise<void> => {
    await logIn().then(handleLogin, handleFailure);
  };

  /**
   * Set a user's password during their first login
   * @returns - A response from the set password endpoint
   */
  const setPasswordFunc = (): Promise<ResponseBody> => {
    // If the user's password doesn't match the confirm password field
    if (setPasswordField !== confirmPassword) throw new Error("Passwords do not match");
    const body = JSON.stringify({ password: setPasswordField });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  };

  const trySetPassword = (): void => {
    setPasswordFunc().then(handleLogin, handleFailure);
  };

  /**
   * Handle the response after logging the user in
   * @param res - The response from the login endpoint
   */
  const handleLogin = (res: ResponseBody): void => {
    if (res.msg === "First login") {
      setFirstLogin(true);
    } else {
      setFirstLogin(false);
      setLoggedIn(true);
      navigate("/"); // Redirect to main app
    }
  };

  /**
   * Handle an error after logging the user in
   * @param res - The response from the login endpoint
   */
  const handleFailure = (res: ResponseBody) => {
    // Flash the message from the server or "Internal server error"
    const msg = <span>{res.msg ? res.msg : "Internal server error"}</span>;
    flashMessage(msg, "danger");
  };

  /**
   * Show a message above the login fields
   * @param msg - The content of the message
   * @param type - The type of message (success, info, danger, etc.)
   */
  const flashMessage = (msg: React.ReactElement, type: string): void => {
    // set the element's key to 0 or the last message's key + 1
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

    // add the message to the page
    setFlashMessages([...flashMessages, { id, element }]);
  };

  /**
   * Remove a message from the page
   * @param id - The id of the message to remove
   */
  const popMessage = (id: number): void => {
    setFlashMessages(flashMessages.filter((fm) => fm.id !== id));
  };

  // The login form fields to be shown on a user's first login
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

  // Regular login form fields
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

  // The login page layout
  const page = (
    <div className="flex h-screen lg:mx-[6rem] xl:mx-[10rem] 2xl:mx-[20rem] bg-light">
      <div className="login-image-container">
        <img className="hidden lg:flex login-image" src={`${process.env.PUBLIC_URL}/logo.png`} alt="Logo" />
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
      {/* if the loading screen is showing or completing a 0.5 second fade-out */}
      {(loading || fading) && (
        <FullLoader
          loading={loading}
          msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""}
        />
      )}

      {/* Show login page if not logged in or it's the first login */}
      {!(loggedIn && !firstLogin) && page}
    </>
  );
};

export default LoginPage;
