import React, { useEffect, useState } from "react";
import { makeRequest } from "./utils";
import { ResponseBody } from "./interfaces";
import { FullLoader } from "./components/loader";
import { useAuth } from "./hooks/useAuth";
import "./loginPage.css";

/**
 * ParticipantLoginPage component for Cognito authentication with database touch and loader
 */
const ParticipantLoginPage: React.FC = () => {
  const { cognitoLogin } = useAuth();
  const [loadingDb, setLoadingDb] = useState<boolean>(false);

  /**
   * Touches the server endpoint to check if the app is ready
   */
  const touch = async (id?: ReturnType<typeof setInterval>): Promise<string> => {
    try {
      const res: ResponseBody = await makeRequest("/touch");
      if (res.msg === "OK" && id) clearInterval(id);
      return res.msg;
    } catch (error) {
      return "Error";
    }
  };

  /**
   * Checks app's status on component mount
   */
  useEffect(() => {
    touch().then((msg: string) => {
      if (msg !== "OK") {
        setLoadingDb(true);
        const intervalId: ReturnType<typeof setInterval> = setInterval(() => touch(intervalId), 2000);
      }
    });
  }, []);

  const page = (
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
          <div className="cognito-login">
            <p>Continue to our secure sign in:</p>
            <div className="login-buttons">
              <button
                className="button button-large button-primary"
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

  return (
    <>
      {(loadingDb) && (
        <FullLoader
          loading={loadingDb}
          msg="Starting the database... This may take up to 6 minutes"
        />
      )}
      {(!loadingDb) && page}
    </>
  );
};

export default ParticipantLoginPage;
