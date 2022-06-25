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

interface LoginPageState {
  email: string;
  password: string;
  loggedIn: boolean;
  loading: boolean;
  fading: boolean;
}

class LoginPage extends React.Component<any, LoginPageState> {
  state = {
    email: "",
    password: "",
    loggedIn: false,
    loading: true,
    fading: false
  };

  async componentDidMount() {
    const loggedIn = await this.checkLogin();
    this.setState({ loading: false, fading: true, loggedIn });
    setTimeout(() => this.setState({ fading: false }), 500);
  }

  logIn = (): Promise<string> => {
    const { email, password } = this.state;
    const auth = Buffer.from(email + ":" + password).toString("base64");
    const headers = { Authorization: "Basic " + auth };
    const opts = { method: "POST", headers: headers };
    return makeRequest("/iam/login", opts);
  };

  tryLogIn = (): void => {
    this.logIn().then(this.handleLogin, this.handleException);
  };

  handleLogin = (): void => {
    this.setState({ loggedIn: true });
  };

  handleException = (res: any): void => {
    console.log(res.msg);
  };

  checkLogin = async (): Promise<boolean> => {
    return await makeRequest("/iam/check-login")
      .then((res) => res.msg == "User is logged in")
      .catch(() => false);
  };

  render() {
    const { loading, fading, loggedIn } = this.state;
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
            <div className="login-field border-light">
              <TextField
                id="login-email"
                type=""
                placeholder="Email"
                prefill=""
                label=""
                onKeyup={(text: string) => this.setState({ email: text })}
                feedback="Invalid email address"
              >
                <Person />
              </TextField>
            </div>
            <div className="login-field border-light">
              <TextField
                id="login-password"
                type="password"
                placeholder="Password"
                prefill=""
                label=""
                onKeyup={(text: string) => this.setState({ password: text })}
                feedback="Invalid password"
              >
                <Key />
              </TextField>
            </div>
            <div className="login-buttons">
              <button
                className="button-primary button-lg"
                onClick={this.tryLogIn}
              >
                Sign In
              </button>
              <span>Forgot password?</span>
            </div>
          </div>
        </div>
      </div>
    );

    return (
      <React.Fragment>
        {loading || fading ? <FullLoader loading={loading} /> : null}
        <div>{loggedIn ? <Dashboard /> : page}</div>
      </React.Fragment>
    );
  }
}

export default LoginPage;
