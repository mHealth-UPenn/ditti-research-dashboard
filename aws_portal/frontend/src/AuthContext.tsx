import React, { createContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "./utils";
import { AuthContextType } from "./interfaces";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isParticipantAuthenticated, setIsParticipantAuthenticated] = useState<boolean>(false);
  const [isResearcherAuthenticated, setIsResearcherAuthenticated] = useState<boolean>(false);
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [isParticipantLoading, setIsParticipantLoading] = useState<boolean>(true);
  const [isResearcherLoading, setIsResearcherLoading] = useState<boolean>(true);
  const [dittiId, setDittiId] = useState<string | null>(null);
  const [accountInfo, setAccountInfo] = useState<any>(null);
  const navigate = useNavigate();

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
            email: res.email,
            firstName: res.firstName,
            lastName: res.lastName,
            accountId: res.accountId
          });
        }
      } catch {
        setIsResearcherAuthenticated(false);
        setAccountInfo(null);
      } finally {
        setIsResearcherLoading(false);
      }
    };

    checkParticipantAuthStatus();
    checkResearcherAuthStatus();
  }, []);

  /**
   * Redirects to Participant login page.
   */
  const participantLogin = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/auth/participant/login`;
  }, []);

  /**
   * Logs out the Participant user by redirecting to the logout endpoint.
   */
  const participantLogout = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/auth/participant/logout`;
    setIsParticipantAuthenticated(false);
    setDittiId(null);
  }, []);

  /**
   * Redirects to Researcher Cognito login page.
   */
  const researcherLogin = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/auth/researcher/login`;
  }, [navigate]);

  /**
   * Logs out the Researcher from Cognito by redirecting to the logout endpoint.
   */
  const researcherLogout = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/auth/researcher/logout`;
    setIsResearcherAuthenticated(false);
    setAccountInfo(null);
  }, [navigate]);

  return (
    <AuthContext.Provider
      value={{
        isParticipantAuthenticated,
        isResearcherAuthenticated,
        isParticipantLoading,
        isResearcherLoading,
        firstLogin,
        dittiId,
        accountInfo,
        participantLogin,
        participantLogout,
        researcherLogin,
        researcherLogout,
        setFirstLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
