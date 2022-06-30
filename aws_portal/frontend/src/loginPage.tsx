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
    makeRequest("/iam/check-login").then((res: ResponseBody) => {
      const set = { loading: false, fading: true };

      if (res.msg == "First login")
        this.setState({ ...set, firstLogin: true, loggedIn: true });
      else if (res.msg == "Login successful")
        this.setState({ ...set, firstLogin: false, loggedIn: true });
      else this.setState({ ...set, loggedIn: false });

      setTimeout(() => this.setState({ fading: false }), 500);
    });
  }

  logIn = (): Promise<ResponseBody> => {
    const { email, password } = this.state;
    const auth = Buffer.from(email + ":" + password).toString("base64");
    const headers = { Authorization: "Basic " + auth };
    const opts = { method: "POST", headers: headers };
    return makeRequest("/iam/login", opts);
  };

  tryLogIn = (): void => {
    this.logIn().then(this.handleLogin, this.handleException);
  };

  setPassword = (): Promise<ResponseBody> => {
    const { setPassword, confirmPassword } = this.state;
    if (!(setPassword == confirmPassword)) throw "Passwords do not match";
    const body = JSON.stringify({ password: setPassword });
    const opts = { method: "POST", body: body };
    return makeRequest("/iam/set-password", opts);
  };

  trySetPassword = (): void => {
    this.setPassword().then(this.handleLogin, this.handleException);
  };

  handleLogin = (res: ResponseBody): void => {
    if (res.msg == "First login") this.setState({ firstLogin: true });
    else this.setState({ firstLogin: false, loggedIn: true });
  };

  handleException = (res: ResponseBody): void => {
    console.log(res.msg);
  };

  render() {
    const {
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
            {firstLogin ? setPasswordFields : loginFields}
          </div>
        </div>
      </div>
    );

    return (
      <React.Fragment>
        {loading || fading ? <FullLoader loading={loading} /> : null}
        <div>{loggedIn && !firstLogin ? <Dashboard /> : page}</div>
      </React.Fragment>
    );
  }
}

export default LoginPage;
