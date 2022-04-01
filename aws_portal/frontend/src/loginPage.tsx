import * as React from "react";
import { Component } from "react";
import { Link } from "react-router-dom";
import "./loginPage.css";
import TextField from "./components/fields/textField";

interface LoginPageProps {}

interface LoginPageState {}

class LoginPage extends React.Component<LoginPageProps, LoginPageState> {
  // state = { :  }
  render() {
    return (
      <main>
        <div className="login-container">
          <div className="login-image-container">
            <img
              className="login-image"
              src={process.env.PUBLIC_URL + "/logo.png"}
            ></img>
          </div>
          <div className="login-menu">
            <div className="login-menu-content">
              <h1>Geriatric Sleep Research Lab</h1>
              <h3>AWS Data Portal</h3>
              <TextField
                id="login-email"
                img={
                  <img src={process.env.PUBLIC_URL + "/icons/person.svg"}></img>
                }
                type=""
                placeholder="Email"
                prefill=""
                label=""
                feedback="Invalid email address"
              />
              <TextField
                id="login-password"
                img={
                  <img src={process.env.PUBLIC_URL + "/icons/key.svg"}></img>
                }
                type="password"
                placeholder="Password"
                prefill=""
                label=""
                feedback="Invalid password"
              />
              <div className="login-buttons">
                <button className="button-primary">Sign In</button>
                <Link to="/">Sign In</Link>
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
