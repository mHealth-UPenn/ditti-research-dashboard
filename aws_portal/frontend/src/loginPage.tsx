import React, { createRef, useEffect, useState } from "react";
import "./loginPage.css";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import Dashboard from "./components/dashboard";
import { Buffer } from "buffer";
import { makeRequest } from "./utils";
import { FullLoader } from "./components/loader";
import { IFlashMessage, ResponseBody } from "./interfaces";
import AsyncButton from "./components/buttons/asyncButton";
import FlashMessage, { FlashMessageVariant } from "./components/flashMessage/flashMessage";
import Form from "./components/containers/forms/form";
import Button from "./components/buttons/button";


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
  const [flashMessages, setFlashMessages] = useState<IFlashMessage[]>([]);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [loggedIn, setLoggedIn] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);
  const [loadingDb, setLoadingDb] = useState<boolean>(false);
  const [setPasswordField, setSetPasswordField] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const [fading, setFading] = useState<boolean>(false);

  useEffect(() => {
    flashMessages.forEach(flashMessage => {
      const closeDiv = flashMessage.closeRef.current;
      if (closeDiv && !closeDiv.onclick) {
        closeDiv.onclick = () => popMessage(flashMessage.id);
      }

      const containerDiv = flashMessage.containerRef.current;
      if (containerDiv) {
        setTimeout(() => containerDiv.style.opacity = "0", 3000);
        setTimeout(() => popMessage(flashMessage.id), 5000)
      }
    });
  }, [flashMessages]);

  useEffect(() => {
    // check the app's status
    touch().then((msg: string) => {
      // if the app is not ready
      if (msg !== "OK") {
        // show the database loading screen and try again every two seconds
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
      // if the app is ready
      if (res.msg === "OK") {
        // clear the interval if touch is being called by setInterval
        if (id) clearInterval(id);
        // check the user's login status
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
        const set = { loading: false, loadingDb: false, fading: true };

        // if the user is logged in
        if (res.msg === "Login successful") {
          setFirstLogin(false);
          setLoggedIn(true);
        } 
        // if this is the user's first login
        else if (res.msg === "First login") {
          setFirstLogin(true);
          setLoggedIn(true);
        } 
        // if the user is not logged in
        else {
          setLoggedIn(false);
          if (localStorage.getItem("jwt")) localStorage.removeItem("jwt");
        }

        // let the loading screen fade out for 0.5 seconds
        setLoading(false);
        setFading(true);
        setTimeout(() => setFading(false), 500);
      })
      .catch((res: ResponseBody) => {
        if (localStorage.getItem("jwt")) localStorage.removeItem("jwt");

        // if the user was logged in and their token expired
        if (res.msg === "Token has expired") {
          const msg = <span>Your session has expired. Please log in again</span>;
          flashMessage(msg, "danger");
        }

        // let the loading screen fade out for 0.5 seconds
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
    // if the user's password doesn't match the confirm password field
    if (!(setPasswordField === confirmPassword)) throw "Passwords do not match";
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
    // if this is the user's first login
    if (res.msg === "First login") setFirstLogin(true);
    else {
      setFirstLogin(false);
      setLoggedIn(true);
    }
  };

  /**
   * Handle an error after logging the user in
   * @param res - The response from the login endpoint
   */
  const handleFailure = (res: ResponseBody) => {
    // flash the message from the server or "Internal server error"
    const msg = <span>{res.msg ? res.msg : "Internal server error"}</span>;
    flashMessage(msg, "danger");
  };

  /**
   * Show a message above the login fields
   * @param msg - The content of the message
   * @param type - The type of message (success, info, danger, etc.)
   */
  const flashMessage = (msg: React.ReactElement, type: FlashMessageVariant): void => {
    // set the element's key to 0 or the last message's key + 1
    const id = flashMessages.length ? flashMessages[flashMessages.length - 1].id + 1 : 0;
    const containerRef = createRef<HTMLDivElement>();
    const closeRef = createRef<HTMLDivElement>();

    const element = 
      <FlashMessage key={id} variant={type} containerRef={containerRef} closeRef={closeRef}>
        {msg}
      </FlashMessage>;

    // add the message to the page
    setFlashMessages(prevFlashMessages => [...prevFlashMessages, { id, element, containerRef, closeRef }]);
  };

  /**
   * Remove a message from the page
   * @param id - The id of the message to remove
   */
  const popMessage = (id: number): void => {
    setFlashMessages(prevFlashMessages => prevFlashMessages.filter((fm) => fm.id !== id));
  };

  // the login form fields to be shown on a user's first login
  const setPasswordFields = (
    <>
      <div className="login-field">
        <TextField
          id="set-password"
          type="password"
          placeholder="To log in, please enter a new password"
          onKeyup={(text: string) => setSetPasswordField(text)}
          value={setPasswordField}>
            <Key />
        </TextField>
      </div>
      <div className="login-field">
        <TextField
          id="confirm-password"
          type="password"
          placeholder="Confirm your password"
          onKeyup={(text: string) => setConfirmPassword(text)}
          value={confirmPassword}>
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

  // regular login form fields
  const loginFields = (
    <>
      <div className="login-field">
        <TextField
          id="login-email"
          placeholder="Email"
          onKeyup={(text: string) => setEmail(text)}
          value={email}>
            <Person />
        </TextField>
      </div>
      <div className="login-field">
        <TextField
          id="login-password"
          type="password"
          placeholder="Password"
          onKeyup={(text: string) => setPassword(text)}
          value={password}>
            <Key />
        </TextField>
      </div>
      <div className="login-buttons">
        <AsyncButton text="Sign In" type="primary" onClick={tryLogIn} />
      </div>
    </>
  );

  if (loading || fading) {
    return (
      <FullLoader
        loading={loading}
        msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""} />
    );
  }

  if (loggedIn && !firstLogin) {
    return <Dashboard />;
  }

  return (
    <div className="flex h-screen w-screen md:w-max mx-auto sm:px-12 xl:px-20 bg-light">
      <div className="hidden sm:flex items-center mr-12 xl:mr-20">
        <img className="w-[10rem] xl:w-[12rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
      </div>
      <div className="flex flex-grow items-center justify-center bg-white mx-[auto] max-w-[24rem] sm:max-w-[64rem]">
        <div className="flex flex-col mx-8 xl:mx-16">
          <div className="flex justify-center mb-8 sm:hidden">
            <div className="p-4 bg-light rounded-xl">
              <img className="w-[6rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
            </div>
          </div>
          <div className="mb-16">
            <p className="text-4xl">Penn Ditti</p>
            <p>Research Coordinator Dashboard</p>
          </div>
          {/* For new sign in with AWS Cognito */}
          {/* <div className="flex flex-col xl:mx-16">
            <div className="flex justify-center">
              <p className="mb-4 whitespace-nowrap">Continue to our secure sign in:</p>
            </div>
            <div className="flex justify-center">
              <Button>Sign in</Button>
            </div>
          </div> */}
          <div className="">
            {flashMessages.map((fm) => fm.element)}
          </div>
          {firstLogin ? setPasswordFields : loginFields}
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
