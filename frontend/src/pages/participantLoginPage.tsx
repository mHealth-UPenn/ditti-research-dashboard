import React, { useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/buttons/button";
import { FullLoader } from "../components/loader/loader";
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

  return (
    <>
      <FullLoader
        loading={loadingDb}
        msg={
          loadingDb
            ? "Starting the database... This may take up to 6 minutes"
            : ""
        }
      />
      <div
        className="mx-auto flex h-screen w-screen bg-extra-light sm:px-12
          md:w-max xl:px-20"
      >
        <div className="mr-12 hidden items-center sm:flex xl:mr-20">
          <img
            className="w-40 rounded-xl shadow-xl xl:w-48"
            src="/logo.png"
            alt="Logo"
          ></img>
        </div>
        <div
          className="relative mx-auto flex min-w-96 flex-col justify-center
            bg-white"
        >
          <div className="mx-8 flex flex-col xl:mx-16">
            <div className="mb-8 flex justify-center sm:hidden">
              <div className="rounded-xl bg-extra-light p-4 shadow-lg">
                <img
                  className="w-24 rounded-xl"
                  src="/logo.png"
                  alt="Logo"
                ></img>
              </div>
            </div>
            <div className="mb-16">
              <p className="text-4xl">Ditti</p>
              <p>Participant Dashboard</p>
            </div>
            <div className="flex flex-col xl:mx-16">
              <div className="flex justify-center">
                <p className="mb-4 whitespace-nowrap">
                  Continue to our secure sign in:
                </p>
              </div>
              <div className="flex justify-center">
                <Button rounded={true} onClick={participantLogin}>
                  Sign in
                </Button>
              </div>
            </div>
          </div>
          <div
            className="absolute bottom-0 flex w-full flex-col items-center
              pb-24"
          >
            <div className="mb-8">
              <Link className="link" to={{ pathname: "/terms-of-use" }}>
                Terms of Use
              </Link>
              <span>&nbsp;&nbsp;|&nbsp;&nbsp;</span>
              <Link className="link" to={{ pathname: "/privacy-policy" }}>
                Privacy Policy
              </Link>
            </div>
            <div className="text-center text-xs">
              Copyright © 2025
              <br />
              the Trustees of the University of Pennsylvania
            </div>
          </div>
        </div>
      </div>
    </>
  );
};
