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

import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import { FullLoader } from "../components/loader";
import { useEnterKeyLogin } from "../hooks/useKeyboardEvent";
import { Button } from "../components/buttons/button";
import { Link } from "react-router-dom";
import "./loginPage.css";

/**
 * Login page for researchers using Cognito authentication.
 * Navigation after successful authentication is handled by the backend.
 * Already authenticated researchers are redirected to the coordinator dashboard.
 */
export const ResearcherLoginPage: React.FC = () => {
  const loadingDb = useDbStatus();
  const navigate = useNavigate();
  
  const {
    isResearcherAuthenticated,
    isResearcherLoading,
    researcherLogin
  } = useAuth();
  // Setup Enter key to trigger login when not loading
  useEnterKeyLogin(!loadingDb, researcherLogin);

  /**
   * Redirects already authenticated researchers to the coordinator dashboard
   */
  useEffect(() => {
    if (isResearcherAuthenticated) {
      navigate("/coordinator");
    }
  }, [isResearcherAuthenticated, navigate]);

  // Show loading screen while authentication is in progress
  if (isResearcherLoading) {
    return <FullLoader loading={true} msg="Checking authentication..." />;
  }

  return (
    <>
      <FullLoader
        loading={loadingDb}
        msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""} />
      <div className="flex h-screen w-screen md:w-max mx-auto sm:px-12 xl:px-20 bg-extra-light">
        <div className="hidden sm:flex items-center mr-12 xl:mr-20">
          <img className="shadow-xl w-[10rem] xl:w-[12rem] rounded-xl" src="/logo.png" alt="Logo"></img>
        </div>
        <div className="relative flex flex-col items-center justify-center bg-white mx-[auto] min-w-[24rem]">
          <div className="flex flex-col justify-center mx-8 xl:mx-16">
            <div className="flex justify-center mb-8 sm:hidden">
              <div className="p-4 bg-extra-light rounded-xl shadow-lg">
                <img className="w-[6rem] rounded-xl" src="/logo.png" alt="Logo"></img>
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
          <div className="absolute bottom-0 w-full flex flex-col items-center pb-24">
            <div className="mb-8">
              <Link className="link" to={{ pathname: "/terms-of-use" }}>Terms of Use</Link>
              <span>&nbsp;&nbsp;|&nbsp;&nbsp;</span>
              <Link className="link" to={{ pathname: "/privacy-policy" }}>Privacy Policy</Link>
            </div>
            <div className="text-xs text-center">
              Copyright © 2025<br />the Trustees of the University of Pennsylvania
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
