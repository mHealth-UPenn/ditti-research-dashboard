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

interface LoginPageState {
  flashMessages: { id: number; element: React.ReactElement }[];
  email: string;
  password: string;
  firstLogin: boolean;
  loggedIn: boolean;
  loading: boolean;
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
    setPassword: "",
    confirmPassword: "",
    fading: false
  };

  componentDidMount() {
    this.checkHealthy().then((msg: string) => {
      if (msg != "OK") {
        const id: ReturnType<typeof setInterval> = setInterval(
          () => this.checkHealthy(id),
          2000
        );
      }
    });
  }

  checkHealthy = async (
    id?: ReturnType<typeof setInterval>
  ): Promise<string> => {
    return await makeRequest("/healthy").then((res: ResponseBody) => {
      console.log(res.msg);
      if (res.msg == "OK") {
        if (id) clearInterval(id);
        this.checkLogIn();
      }

      return res.msg;
    });
  };

  checkLogIn = () => {
    makeRequest("/iam/check-login")
      .then((res: ResponseBody) => {
        const set = { loading: false, fading: true };

        if (res.msg == "Login successful")
          this.setState({ ...set, firstLogin: false, loggedIn: true });
        else if (res.msg == "First login")
          this.setState({ ...set, firstLogin: true, loggedIn: true });
        else this.setState({ ...set, loggedIn: false });

        setTimeout(() => this.setState({ fading: false }), 500);
      })
      .catch((res: ResponseBody) => {
        if (res.msg == "Token has expired") {
          const msg = (
            <span>Your session has expired. Please log in again</span>
          );
          this.flashMessage(msg, "danger");
        }

        this.setState({ loading: false, fading: true, loggedIn: false });
        setTimeout(() => this.setState({ fading: false }), 500);
      });
  };

  logIn = (): Promise<ResponseBody> => {
    const { email, password } = this.state;
    const auth = Buffer.from(email + ":" + password).toString("base64");
    const headers = { Authorization: "Basic " + auth };
    const opts = { method: "POST", headers: headers };
    return makeRequest("/iam/login", opts);
  };

  tryLogIn = (): void => {
    this.logIn().then(this.handleLogin, this.handleFailure);
  };

  setPassword = (): Promise<ResponseBody> => {
    const { setPassword, confirmPassword } = this.state;
    if (!(setPassword == confirmPassword)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPassword });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  };

  trySetPassword = (): void => {
    this.setPassword().then(this.handleLogin, this.handleFailure);
  };

  handleLogin = (res: ResponseBody): void => {
    if (res.msg == "First login") this.setState({ firstLogin: true });
    else this.setState({ firstLogin: false, loggedIn: true });
  };

  handleFailure = (res: ResponseBody) => {
    const msg = <span>{res.msg ? res.msg : "Internal server error"}</span>;
    this.flashMessage(msg, "danger");
  };

  flashMessage = (msg: React.ReactElement, type: string): void => {
    const { flashMessages } = this.state;
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

    flashMessages.push({ id, element });
    this.setState({ flashMessages });
  };

  popMessage = (id: number): void => {
    let { flashMessages } = this.state;
    flashMessages = flashMessages.filter((fm) => fm.id != id);
    this.setState({ flashMessages });
  };

  render() {
    const {
      flashMessages,
      loading,
      email,
      password,
      fading,
      firstLogin,
      loggedIn,
      setPassword,
      confirmPassword
    } = this.state;

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
          <button className="button-primary button-lg" onClick={this.tryLogIn}>
            Sign In
          </button>
        </div>
      </React.Fragment>
    );

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
        {loading || fading ? (
          <FullLoader
            loading={loading}
            msg={"Starting the database... This may take up to 6 minutes"}
          />
        ) : null}
        <div>{loggedIn && !firstLogin ? <Dashboard /> : page}</div>
      </React.Fragment>
    );
  }
}

export default LoginPage;
