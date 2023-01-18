import * as React from "react";
import { Component } from "react";
import "./loginPage.css";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import Dashboard from "./components/dashboard";
import { Buffer } from "buffer";
import { makeRequest } from "./utils";
import { FullLoader } from "./components/loader";
import { ResponseBody } from "./interfaces";
import AsyncButton from "./components/buttons/asyncButton";

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
interface LoginPageState {
  flashMessages: { id: number; element: React.ReactElement }[];
  email: string;
  password: string;
  firstLogin: boolean;
  loggedIn: boolean;
  loading: boolean;
  loadingDb: boolean;
  setPassword: string;
  confirmPassword: string;
  fading: boolean;
}

class LoginPage extends React.Component<any, LoginPageState> {
  state = {
    flashMessages: [] as { id: number; element: React.ReactElement }[],
    email: "",
    password: "",
    firstLogin: false,
    loggedIn: false,
    loading: true,
    loadingDb: false,
    setPassword: "",
    confirmPassword: "",
    fading: false
  };

  componentDidMount() {

    // check the app's status
    this.touch().then((msg: string) => {

      // if the app is not ready
      if (msg != "OK") {

        // show the database loading screen and try again every two seconds
        this.setState({ loadingDb: true });
        const id: ReturnType<typeof setInterval> = setInterval(
          () => this.touch(id),
          2000
        );
      }
    });
  }

  /**
   * Check the app's status
   * @param id - The interval id if called from setInterval (optional)
   * @returns - The message returned from the touch endpoint
   */
  touch = async (id?: ReturnType<typeof setInterval>): Promise<string> => {
    return await makeRequest("/touch").then((res: ResponseBody) => {

      // if the app is ready
      if (res.msg == "OK") {

        // clear the interval if touch is being called by setInterval
        if (id) clearInterval(id);

        // check the user's login status
        this.checkLogIn();
      }

      return res.msg;
    });
  };

  /**
   * Check the user's login status
   */
  checkLogIn = () => {
    makeRequest("/iam/check-login")
      .then((res: ResponseBody) => {
        const set = { loading: false, loadingDb: false, fading: true };

        // if the user is logged in
        if (res.msg == "Login successful")
          this.setState({ ...set, firstLogin: false, loggedIn: true });

        // if this is the user's first login
        else if (res.msg == "First login")
          this.setState({ ...set, firstLogin: true, loggedIn: true });

        // if the user is not logged in
        else this.setState({ ...set, loggedIn: false });

        // let the loading screen fade out for 0.5 seconds
        setTimeout(() => this.setState({ fading: false }), 500);
      })
      .catch((res: ResponseBody) => {

        // if the user was logged in and their token expired
        if (res.msg == "Token has expired") {
          const msg = (
            <span>Your session has expired. Please log in again</span>
          );
          this.flashMessage(msg, "danger");
        }

        // let the loading screen fade out for 0.5 seconds
        this.setState({ loading: false, fading: true, loggedIn: false });
        setTimeout(() => this.setState({ fading: false }), 500);
      });
  };

  /**
   * Log the user in
   * @returns - A response from the login endpoint
   */
  logIn = (): Promise<ResponseBody> => {
    const { email, password } = this.state;
    const auth = Buffer.from(email + ":" + password).toString("base64");
    const headers = { Authorization: "Basic " + auth };
    const opts = { method: "POST", headers: headers };
    return makeRequest("/iam/login", opts);
  };

  tryLogIn = async (): Promise<void> => {
    await this.logIn().then(this.handleLogin, this.handleFailure);
  };

  /**
   * Set a user's password during their first login
   * @returns - A response from the set password endpoint
   */
  setPassword = (): Promise<ResponseBody> => {
    const { setPassword, confirmPassword } = this.state;

    // if the user's password doesn't match the confirm password field
    if (!(setPassword == confirmPassword)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPassword });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  };

  trySetPassword = (): void => {
    this.setPassword().then(this.handleLogin, this.handleFailure);
  };

  /**
   * Handle the response after logging the user in
   * @param res - The response from the login endpoint
   */
  handleLogin = (res: ResponseBody): void => {

    // if this is the user's first login
    if (res.msg == "First login") this.setState({ firstLogin: true });
    else this.setState({ firstLogin: false, loggedIn: true });
  };

  /**
   * Handle an error after logging the user in
   * @param res - The response from the login endpoint
   */
  handleFailure = (res: ResponseBody) => {

    // flash the message from the server or "Internal server error"
    const msg = <span>{res.msg ? res.msg : "Internal server error"}</span>;
    this.flashMessage(msg, "danger");
  };

  /**
   * Show a message above the login fields
   * @param msg - The content of the message
   * @param type - The type of message (success, info, danger, etc.)
   */
  flashMessage = (msg: React.ReactElement, type: string): void => {
    const { flashMessages } = this.state;

    // set the element's key to 0 or the last message's key + 1
    const id = flashMessages.length
      ? flashMessages[flashMessages.length - 1].id + 1
      : 0;

    const element = (
      <div key={id} className={"shadow flash-message flash-message-" + type}>
        <div className="flash-message-content">
          <span>{msg}</span>
        </div>
        <div
          className="flash-message-close"
          onClick={() => this.popMessage(id)}
        >
          <span>x</span>
        </div>
      </div>
    );

    // add the message to the page
    flashMessages.push({ id, element });
    this.setState({ flashMessages });
  };

  /**
   * Remove a message from the page
   * @param id - The id of the message to remove
   */
  popMessage = (id: number): void => {
    let { flashMessages } = this.state;
    flashMessages = flashMessages.filter((fm) => fm.id != id);
    this.setState({ flashMessages });
  };

  render() {
    const {
      flashMessages,
      loading,
      loadingDb,
      email,
      password,
      fading,
      firstLogin,
      loggedIn,
      setPassword,
      confirmPassword
    } = this.state;

    // the login form fields to be shown on a user's first login
    const setPasswordFields = (
      <React.Fragment>
        <div className="login-field">
          <TextField
            id="set-password"
            type="password"
            placeholder="To log in, please enter a new password"
            onKeyup={(text: string) => this.setState({ setPassword: text })}
            value={setPassword}
          >
            <Key />
          </TextField>
        </div>
        <div className="login-field">
          <TextField
            id="confirm-password"
            type="password"
            placeholder="Confirm your password"
            onKeyup={(text: string) => this.setState({ confirmPassword: text })}
            value={confirmPassword}
          >
            <Key />
          </TextField>
        </div>
        <div className="login-buttons">
          <button
            className="button-primary button-lg"
            onClick={this.trySetPassword}
          >
            Set password
          </button>
        </div>
      </React.Fragment>
    );

    // regular login form fields
    const loginFields = (
      <React.Fragment>
        <div className="login-field">
          <TextField
            id="login-email"
            placeholder="Email"
            onKeyup={(text: string) => this.setState({ email: text })}
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
            onKeyup={(text: string) => this.setState({ password: text })}
            value={password}
          >
            <Key />
          </TextField>
        </div>
        <div className="login-buttons">
          <AsyncButton text="Sign In" type="primary" onClick={this.tryLogIn} />
        </div>
      </React.Fragment>
    );

    // the login page
    const page = (
      <div className="login-container bg-light">
        <div className="login-image-container">
          <img
            className="login-image"
            src={process.env.PUBLIC_URL + "/logo.png"}
          ></img>
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
      <React.Fragment>

        {/* if the loading screen is showing or completing a 0.5 second fade-out */}
        {loading || fading ? (
          <FullLoader
            loading={loading}
            msg={
              loadingDb
                ? "Starting the database... This may take up to 6 minutes"
                : ""
            }
          />
        ) : null}

        {/* if the user is logged in, show the dashboard, else show the login page */}
        <div>{loggedIn && !firstLogin ? <Dashboard /> : page}</div>
      </React.Fragment>
    );
  }
}

export default LoginPage;
