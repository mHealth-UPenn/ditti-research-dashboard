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

import React, { createContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "../utils";
import { AuthContextType } from "../interfaces";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isParticipantAuthenticated, setIsParticipantAuthenticated] = useState<boolean>(false);
  const [isResearcherAuthenticated, setIsResearcherAuthenticated] = useState<boolean>(false);
  const [isFirstLogin, setIsFirstLogin] = useState<boolean>(false);
  const [isParticipantLoading, setIsParticipantLoading] = useState<boolean>(true);
  const [isResearcherLoading, setIsResearcherLoading] = useState<boolean>(true);
  const [dittiId, setDittiId] = useState<string | null>(null);
  const INITIAL_ACCOUNT_STATE: AuthContextType["accountInfo"] = {
    msg: "",
    email: "",
    firstName: "",
    lastName: "",
    accountId: "",
    phoneNumber: undefined
  };
  const [accountInfo, setAccountInfo] = useState<AuthContextType["accountInfo"]>(INITIAL_ACCOUNT_STATE);
  const navigate = useNavigate();

  const resetAccountInfo = useCallback(() => {
    setAccountInfo(INITIAL_ACCOUNT_STATE);
  }, []);

  useEffect(() => {
    /**
     * Checks Participant authentication status on component mount.
     */
    const checkParticipantAuthStatus = async () => {
      try {
        const res = await makeRequest("/auth/participant/check-login", { method: "GET" });
        if (res.msg === "Login successful") {
          setIsParticipantAuthenticated(true);
          setDittiId(res.dittiId);
        }
      } catch {
        setIsParticipantAuthenticated(false);
      } finally {
        setIsParticipantLoading(false);
      }
    };

    /**
     * Checks Researcher Cognito authentication status on component mount.
     */
    const checkResearcherAuthStatus = async () => {
      try {
        const res = await makeRequest("/auth/researcher/check-login", { method: "GET" });
        if (res.msg === "Login successful") {
          setIsResearcherAuthenticated(true);
          setAccountInfo({
            msg: res.msg,
            email: res.email,
            firstName: res.firstName,
            lastName: res.lastName,
            accountId: res.accountId,
            phoneNumber: res.phoneNumber
          });
          
          // Set isFirstLogin state directly from the response
          setIsFirstLogin(Boolean(res.isFirstLogin));
        }
      } catch {
        setIsResearcherAuthenticated(false);
        resetAccountInfo();
      } finally {
        setIsResearcherLoading(false);
      }
    };

    checkParticipantAuthStatus();
    checkResearcherAuthStatus();
  }, [resetAccountInfo]);

  /**
   * Redirects to Participant login page.
   */
  const participantLogin = useCallback((): void => {
    // For elevated mode, make sure to pass it as a url param
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER}/auth/participant/login`;
  }, []);

  /**
   * Logs out the Participant user by redirecting to the logout endpoint.
   */
  const participantLogout = useCallback((): void => {
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER}/auth/participant/logout`;
    setIsParticipantAuthenticated(false);
    setDittiId(null);
  }, []);

  /**
   * Redirects to Researcher Cognito login page.
   */
  const researcherLogin = useCallback((): void => {
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER}/auth/researcher/login`;
  }, [navigate]);

  /**
   * Logs out the Researcher from Cognito by redirecting to the logout endpoint.
   */
  const researcherLogout = useCallback((): void => {
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER}/auth/researcher/logout`;
    setIsResearcherAuthenticated(false);
    resetAccountInfo();
  }, [resetAccountInfo]);

  return (
    <AuthContext.Provider
      value={{
        isParticipantAuthenticated,
        isResearcherAuthenticated,
        isParticipantLoading,
        isResearcherLoading,
        isFirstLogin,
        dittiId,
        accountInfo,
        participantLogin,
        participantLogout,
        researcherLogin,
        researcherLogout,
        setIsFirstLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
