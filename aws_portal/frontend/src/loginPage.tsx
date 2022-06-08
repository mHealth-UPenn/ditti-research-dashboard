import * as React from "react";
import { Component } from "react";
import "./loginPage.css";
import TextField from "./components/fields/textField";
import { ReactComponent as Person } from "./icons/person.svg";
import { ReactComponent as Key } from "./icons/key.svg";
import Dashboard from "./components/dashboard";

interface LoginPageState {
  loggedIn: boolean;
}

class LoginPage extends React.Component<any, LoginPageState> {
  state = {
    loggedIn: false
  };

  componentDidMount() {
    fetch(process.env.REACT_APP_FLASK_SERVER + "/healthy")
      .then((res) => res.json())
      .then((res) => console.log(res));
  }

  logIn = () => {
    this.setState({ loggedIn: true });
  };

  render() {
    return this.state.loggedIn ? (
      <Dashboard />
    ) : (
      <main>
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
                  onKeyup={(text) => null}
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
                  onKeyup={(text) => null}
                  feedback="Invalid password"
                />
              </div>
              <div className="login-buttons">
                <button
                  className="button-primary"
                  onClick={this.logIn}
                  style={{ padding: "1rem" }}
                >
                  Sign In
                </button>
                <span>Forgot password?</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    );
  }
}

export default LoginPage;
