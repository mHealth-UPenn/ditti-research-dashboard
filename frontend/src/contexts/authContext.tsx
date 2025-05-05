/* Copyright 2025 The Trustees of the University of Pennsylvania
 *
 * Licensed under the Apache License, Version 2.0 (the "License"); you may]
 * not use this file except in compliance with the License. You may obtain a
 * copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 * License for the specific language governing permissions and limitations
 * under the License.
 */

import React, {
  createContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
  useMemo,
} from "react";
import { httpClient } from "../lib/http";
import {
  AuthContextValue,
  ParticipantAuthResponse,
  ResearcherAccountInfo,
  ResearcherAuthResponse,
} from "./authContext.types";

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined
);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [isParticipantAuthenticated, setIsParticipantAuthenticated] =
    useState<boolean>(false);
  const [isResearcherAuthenticated, setIsResearcherAuthenticated] =
    useState<boolean>(false);
  const [isFirstLogin, setIsFirstLogin] = useState<boolean>(false);
  const [isParticipantLoading, setIsParticipantLoading] =
    useState<boolean>(true);
  const [isResearcherLoading, setIsResearcherLoading] = useState<boolean>(true);
  const [dittiId, setDittiId] = useState<string | null>(null);
  const INITIAL_ACCOUNT_STATE = useMemo(
    () => ({
      msg: "",
      email: "",
      firstName: "",
      lastName: "",
      accountId: "",
      phoneNumber: undefined,
    }),
    []
  );
  const [accountInfo, setAccountInfo] = useState<ResearcherAccountInfo>(
    INITIAL_ACCOUNT_STATE
  );

  const resetAccountInfo = useCallback(() => {
    setAccountInfo(INITIAL_ACCOUNT_STATE);
  }, [INITIAL_ACCOUNT_STATE]);

  useEffect(() => {
    /**
     * Checks Participant authentication status on component mount.
     */
    const checkParticipantAuthStatus = async () => {
      setIsParticipantLoading(true);
      try {
        const res = await httpClient.request<ParticipantAuthResponse>(
          "/auth/participant/check-login",
          { method: "GET" }
        );
        if (res.msg === "Login successful") {
          setIsParticipantAuthenticated(true);
          setDittiId(res.dittiId);
        } else {
          setIsParticipantAuthenticated(false);
          setDittiId(null);
        }
      } catch (error) {
        console.error("Participant auth check failed:", error);
        setIsParticipantAuthenticated(false);
        setDittiId(null);
      } finally {
        setIsParticipantLoading(false);
      }
    };

    /**
     * Checks Researcher Cognito authentication status on component mount.
     */
    const checkResearcherAuthStatus = async () => {
      setIsResearcherLoading(true);
      try {
        const res = await httpClient.request<ResearcherAuthResponse>(
          "/auth/researcher/check-login",
          { method: "GET" }
        );
        if (res.msg === "Login successful") {
          setIsResearcherAuthenticated(true);
          setAccountInfo({
            msg: res.msg,
            email: res.email,
            firstName: res.firstName,
            lastName: res.lastName,
            accountId: res.accountId,
            phoneNumber: res.phoneNumber,
          });
          setIsFirstLogin(Boolean(res.isFirstLogin));
        } else {
          setIsResearcherAuthenticated(false);
          resetAccountInfo();
        }
      } catch (error) {
        console.error("Researcher auth check failed:", error);
        setIsResearcherAuthenticated(false);
        resetAccountInfo();
      } finally {
        setIsResearcherLoading(false);
      }
    };

    void checkParticipantAuthStatus();
    void checkResearcherAuthStatus();
  }, [resetAccountInfo]);

  /**
   * Redirects to Participant login page.
   */
  const participantLogin = useCallback(
    (options?: { elevated: boolean }): void => {
      // For elevated mode, make sure to pass it as a url param
      const baseUrl = `${import.meta.env.VITE_FLASK_SERVER as string}/auth/participant/login`;
      const url = options?.elevated ? `${baseUrl}?elevated=true` : baseUrl;
      window.location.href = url;
    },
    []
  );

  /**
   * Logs out the Participant user by redirecting to the logout endpoint.
   */
  const participantLogout = useCallback((): void => {
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER as string}/auth/participant/logout`;
    setIsParticipantAuthenticated(false);
    setDittiId(null);
  }, []);

  /**
   * Redirects to Researcher Cognito login page.
   */
  const researcherLogin = useCallback(
    (options?: { elevated: boolean }): void => {
      const baseUrl = `${import.meta.env.VITE_FLASK_SERVER as string}/auth/researcher/login`;
      const url = options?.elevated ? `${baseUrl}?elevated=true` : baseUrl;
      window.location.href = url;
    },
    []
  );

  /**
   * Logs out the Researcher from Cognito by redirecting to the logout endpoint.
   */
  const researcherLogout = useCallback((): void => {
    window.location.href = `${import.meta.env.VITE_FLASK_SERVER as string}/auth/researcher/logout`;
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
