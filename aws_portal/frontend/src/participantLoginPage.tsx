import React from "react";
import { useAuth } from "./hooks/useAuth";
import "./loginPage.css";

/**
 * ParticipantLoginPage component for Cognito authentication
 */
const ParticipantLoginPage: React.FC = () => {
  const { cognitoLogin } = useAuth();

  return (
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
          <h3>Participant Portal</h3>
          <div className="login-flash-message-container" />
          <div className="cognito-login">
            <p>Continue to our secure sign in:</p>
            <div className="login-buttons">
              <button
                className={"button button-large button-primary"}
                onClick={cognitoLogin}
              >
                Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParticipantLoginPage;
