/* Ditti Research Dashboard
 * Copyright (C) 2025 the Trustees of the University of Pennsylvania
 *
 * Ditti Research Dashboard is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published
 * by the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * Ditti Research Dashboard is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "../utils";
import { ResponseBody } from "../interfaces";
import TextField from "../components/fields/textField";
import { FullLoader } from "../components/loader";
import AsyncButton from "../components/buttons/asyncButton";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import "./loginPage.css";

/**
 * LoginPage component for IAM authentication
 */
const LoginPage: React.FC = () => {
  const [flashMessages, setFlashMessages] = useState<{ id: number; element: React.ReactElement }[]>([]);
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [setPasswordField, setSetPasswordField] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");
  const loadingDb = useDbStatus();
  const navigate = useNavigate();

  const {
    isIamAuthenticated,
    firstLogin,
    isIamLoading,
    iamLogin,
    setFirstLogin
  } = useAuth();

  /**
   * Redirects authenticated IAM users to the Research Coordinator Dashboard
   */
  useEffect(() => {
    if (isIamAuthenticated && !firstLogin) {
      navigate("/coordinator");
    }
  }, [isIamAuthenticated, firstLogin, navigate]);

  /**
   * Attempts to log the IAM user in
   */
  const tryLogIn = async (): Promise<void> => {
    try {
      await iamLogin(email, password);
    } catch (error) {
      const errorMessage = (error as { msg?: string }).msg;
      const msg = <span>{errorMessage ? errorMessage : "Internal server error"}</span>;
      flashMessage(msg, "danger");
    }
  };

  /**
   * Sets a new password during the first login
   */
  const trySetPassword = async (): Promise<void> => {
    if (setPasswordField !== confirmPassword) {
      flashMessage(<span>Passwords do not match</span>, "danger");
      return;
    }
    const body = JSON.stringify({ password: setPasswordField });
    const opts = { method: "POST", body };
    try {
      const res: ResponseBody = await makeRequest("/iam/set-password", opts);
      if (res.msg === "Password set successfully") {
        setFirstLogin(false);
        navigate("/coordinator");
      } else {
        flashMessage(<span>{res.msg}</span>, "danger");
      }
    } catch (error) {
      const msg = <span>{(error as { msg?: string }).msg || "Internal server error"}</span>;
      flashMessage(msg, "danger");
    }
  };

  /**
   * Adds a flash message to be displayed on the screen
   */
  const flashMessage = (msg: React.ReactElement, type: string): void => {
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
    setFlashMessages([...flashMessages, { id, element }]);
  };

  /**
   * Removes a flash message by ID
   */
  const popMessage = (id: number): void => {
    setFlashMessages(flashMessages.filter((fm) => fm.id !== id));
  };

  const setPasswordFields = (
    <>
      <div className="login-field">
        <TextField
          id="set-password"
          type="password"
          placeholder="To log in, please enter a new password"
          onKeyup={(text: string) => setSetPasswordField(text)}
          onKeyDown={(e) => e.key === "Enter" && trySetPassword()}
          value={setPasswordField} />
      </div>
      <div className="login-field">
        <TextField
          id="confirm-password"
          type="password"
          placeholder="Confirm your password"
          onKeyup={(text: string) => setConfirmPassword(text)}
          onKeyDown={(e) => e.key === "Enter" && trySetPassword()}
          value={confirmPassword} />
      </div>
      <div className="login-buttons">
        <button className="button-primary button-lg" onClick={trySetPassword}>
          Set password
        </button>
      </div>
    </>
  );

  const loginFields = (
    <>
      <div className="login-field">
        <TextField
          id="login-email"
          placeholder="Email"
          onKeyup={(text: string) => setEmail(text)}
          onKeyDown={(e) => e.key === "Enter" && tryLogIn()}
          value={email} />
      </div>
      <div className="login-field">
        <TextField
          id="login-password"
          type="password"
          placeholder="Password"
          onKeyup={(text: string) => setPassword(text)}
          onKeyDown={(e) => e.key === "Enter" && tryLogIn()}
          value={password} />
      </div>
      <div className="login-buttons">
        <AsyncButton onClick={tryLogIn}>Sign in</AsyncButton>
      </div>
    </>
  );

  if (isIamAuthenticated && !firstLogin) {
    return <FullLoader loading={isIamLoading || loadingDb} msg="" />;
  }

  return (
    <>
      <FullLoader
        loading={isIamLoading || loadingDb}
        msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""} />
      <div className="flex h-screen w-screen md:w-max mx-auto sm:px-12 xl:px-20 bg-extra-light">
        <div className="hidden sm:flex items-center mr-12 xl:mr-20">
          <img className="shadow-xl w-[10rem] xl:w-[12rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
        </div>
        <div className="flex flex-grow items-center justify-center bg-white mx-[auto] max-w-[24rem] sm:max-w-[64rem]">
          <div className="flex flex-col mx-8 xl:mx-16">
            <div className="flex justify-center mb-8 sm:hidden">
              <div className="p-4 bg-extra-light rounded-xl shadow-lg">
                <img className="w-[6rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
              </div>
            </div>
            <div className="mb-16">
              <p className="text-4xl">Ditti</p>
              <p>Research Dashboard</p>
            </div>
            {/* For new sign in with AWS Cognito */}
            {/* <div className="flex flex-col xl:mx-16">
              <div className="flex justify-center">
                <p className="mb-4 whitespace-nowrap">Continue to our secure sign in:</p>
              </div>
              <div className="flex justify-center">
                <Button rounded={true}>Sign in</Button>
              </div>
            </div> */}
            <div className="">
              {flashMessages.map((fm) => fm.element)}
            </div>
            {firstLogin ? setPasswordFields : loginFields}
          </div>
        </div>
      </div>
    </>
  );
};

export default LoginPage;
