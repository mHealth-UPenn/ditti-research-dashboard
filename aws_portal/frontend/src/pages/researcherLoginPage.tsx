import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import { FullLoader } from "../components/loader";
import Button from "../components/buttons/button";
import { Link } from "react-router-dom";
import "./loginPage.css";

/**
 * Login page for researchers using Cognito authentication
 */
const ResearcherLoginPage: React.FC = () => {
  const loadingDb = useDbStatus();
  const navigate = useNavigate();
  
  const {
    isResearcherAuthenticated,
    isResearcherLoading,
    researcherLogin
  } = useAuth();

  /**
   * Redirects authenticated researchers to the coordinator dashboard
   */
  useEffect(() => {
    if (isResearcherAuthenticated) {
      navigate("/coordinator");
    }
  }, [isResearcherAuthenticated, navigate]);

  // Show loading screen while authentication is in progress
  if (isResearcherLoading || loadingDb) {
    return <FullLoader loading={true} msg="Checking authentication..." />;
  }

  // The main component content
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
              <p>Researcher Dashboard</p>
            </div>
            <div className="flex flex-col xl:mx-16">
              <div className="flex justify-center">
                <p className="mb-4 whitespace-nowrap">Continue to our secure sign in:</p>
              </div>
              <div className="flex justify-center">
                <Button rounded={true} onClick={researcherLogin}>Sign in</Button>
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

export default ResearcherLoginPage; 