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
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/buttons/button";
import { FullLoader } from "../components/loader";
import { useAuth } from "../hooks/useAuth";
import { useDbStatus } from "../hooks/useDbStatus";
import { useEnterKeyLogin } from "../hooks/useKeyboardEvent";
import "./loginPage.css";

/**
 * ParticipantLoginPage component for participant authentication.
 * Navigation after successful authentication is handled by the backend.
 * Already authenticated participants are redirected to the root dashboard.
 */
export const ParticipantLoginPage: React.FC = () => {
  const navigate = useNavigate();

  const { participantLogin, isParticipantAuthenticated } = useAuth();
  const loadingDb = useDbStatus();
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
  // useEffect(() => {
  //   const urlParams = new URLSearchParams(location.search);
  //   const elevatedParam = urlParams.get("elevated");
  //   setIsElevated(elevatedParam === "true");
  //   // Add state [isElevated, setIsElevated]
  //   // Add switch between participantLogin() and participantLogin({ elevated: true }) based on isElevated
  // }, [location.search]); // useLocation();

  return (
    <>
      <FullLoader
        loading={loadingDb}
        msg={loadingDb ? "Starting the database... This may take up to 6 minutes" : ""} />
      <div className="flex h-screen w-screen md:w-max mx-auto sm:px-12 xl:px-20 bg-extra-light">
        <div className="hidden sm:flex items-center mr-12 xl:mr-20">
          <img className="shadow-xl w-[10rem] xl:w-[12rem] rounded-xl" src={process.env.PUBLIC_URL + "/logo.png"} alt="Logo"></img>
        </div>
        <div className="relative flex flex-col justify-center bg-white mx-[auto] min-w-[24rem]">
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
