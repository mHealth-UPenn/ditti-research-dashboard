import * as React from "react";
import { Component } from "react";
import "./loginPage.css";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import Dashboard from "./components/dashboard";
import { Buffer } from "buffer";
import { unmountComponentAtNode } from "react-dom";

interface LoaderProps {
  loading: boolean;
}

class Loader extends React.Component<LoaderProps, any> {
  render() {
    const loadingStyle = {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100vh",
      position: "absolute",
      width: "100vw"
    } as React.StyleHTMLAttributes<HTMLDivElement>;

    const fadingStyle = {
      alignItems: "center",
      backgroundColor: "white",
      display: "flex",
      justifyContent: "center",
      height: "100vh",
      opacity: 0,
      position: "absolute",
      transition: "opacity 500ms ease-in",
      width: "100vw"
    } as React.StyleHTMLAttributes<HTMLDivElement>;

    return (
      <div id="loader" style={this.props.loading ? loadingStyle : fadingStyle}>
        <div className="lds-ring">
          <div></div>
          <div></div>
          <div></div>
          <div></div>
        </div>
      </div>
    );
  }
}

const getCookie = (name: string): string => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);

  if (parts.length === 2) {
    const cookie = parts.pop()?.split(";")?.shift();
    return cookie ? cookie : "";
  } else {
    return "";
  }
};

const makeRequest = (url: string, opts?: any): Promise<any> => {
  if (opts && opts.method == "POST")
    opts.headers["X-CSRF-TOKEN"] = getCookie("csrf_access_token");

  return fetch(process.env.REACT_APP_FLASK_SERVER + url, opts ? opts : {}).then(
    async (res) => {
      if (res.status != 200) throw new Error(await res.json());
      else return res.json();
    }
  );
};

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

  handleException = (msg: string): void => {
    console.log(msg);
  };

  checkLogin = async (): Promise<boolean> => {
    const res = await makeRequest("/iam/check-login");
    return res.msg == "User is logged in";
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
                svg={<Person />}
                type=""
                placeholder="Email"
                prefill=""
                label=""
                onKeyup={(text: string) => this.setState({ email: text })}
                feedback="Invalid email address"
              />
            </div>
            <div className="login-field border-light">
              <TextField
                id="login-password"
                svg={<Key />}
                type="password"
                placeholder="Password"
                prefill=""
                label=""
                onKeyup={(text: string) => this.setState({ password: text })}
                feedback="Invalid password"
              />
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
        {loading || fading ? <Loader loading={loading} /> : null}
        <div>{loggedIn ? <Dashboard /> : page}</div>
      </React.Fragment>
    );
  }
}

export default LoginPage;
