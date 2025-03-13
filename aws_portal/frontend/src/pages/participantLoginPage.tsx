import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { FullLoader } from "../components/loader";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import { useEnterKeyLogin } from "../hooks/useKeyboardEvent";
import "./loginPage.css";
import Button from "../components/buttons/button";
import { Link } from "react-router-dom";

/**
 * ParticipantLoginPage component for participant authentication.
 * Navigation after successful authentication is handled by the backend.
 * Already authenticated participants are redirected to the root dashboard.
 */
const ParticipantLoginPage: React.FC = () => {
  const [isElevated, setIsElevated] = useState(false);
  const navigate = useNavigate();

  const { participantLogin, isParticipantAuthenticated } = useAuth();
  const loadingDb = useDbStatus();
  const location = useLocation();
  // Setup Enter key to trigger login when not loading
  useEnterKeyLogin(!loadingDb, participantLogin);

  /**
   * Redirects already authenticated participants to the root dashboard
   */
  useEffect(() => {
    if (isParticipantAuthenticated) {
      navigate("/");
    }
  }, [isParticipantAuthenticated, navigate]);

  // Parse URL parameters for elevated mode
  useEffect(() => {
    const urlParams = new URLSearchParams(location.search);
    const elevatedParam = urlParams.get("elevated");
    setIsElevated(elevatedParam === "true");
  }, [location.search]);

  // Unused because this functionality is currently disabled
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const handleParticipantLogin = () => {
    if (isElevated) {
      participantLogin({ elevated: true });
    } else {
      participantLogin();
    }
  };

  return (
    <>
      <FullLoader
        loading={loadingDb}
        msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""} />
      <div className="flex h-screen w-screen md:w-max mx-auto sm:px-12 xl:px-20 bg-extra-light">
        <div className="hidden sm:flex items-center mr-12 xl:mr-20">
          <img className="shadow-xl w-[10rem] xl:w-[12rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
        </div>
        <div className="flex flex-col flex-grow items-center justify-center bg-white mx-[auto] max-w-[24rem] sm:max-w-[64rem]">
          <div className="flex-grow" />
          <div className="flex flex-col mx-8 xl:mx-16">
            <div className="flex justify-center mb-8 sm:hidden">
              <div className="p-4 bg-extra-light rounded-xl shadow-lg">
                <img className="w-[6rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
              </div>
            </div>
            <div className="mb-16">
              <p className="text-4xl">Ditti</p>
              <p>Participant Dashboard</p>
            </div>
            <div className="flex flex-col xl:mx-16">
              <div className="flex justify-center">
                <p className="mb-4 whitespace-nowrap">Continue to our secure sign in:</p>
              </div>
              <div className="flex justify-center">
                <Button rounded={true} onClick={participantLogin}>Sign in</Button>
              </div>
            </div>
          </div>
          <div className="flex items-center flex-grow">
            <Link className="link" to={{ pathname: "/terms-of-use" }}>Terms of Use</Link>
            <span>&nbsp;&nbsp;|&nbsp;&nbsp;</span>
            <Link className="link" to={{ pathname: "/privacy-policy" }}>Privacy Policy</Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default ParticipantLoginPage;
