import React, { createContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { makeRequest } from "./utils";
import { AuthContextType } from "./interfaces";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isCognitoAuthenticated, setIsCognitoAuthenticated] = useState<boolean>(false);
  const [isResearcherAuthenticated, setIsResearcherAuthenticated] = useState<boolean>(false);
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [isCognitoLoading, setIsCognitoLoading] = useState<boolean>(true);
  const [isResearcherLoading, setIsResearcherLoading] = useState<boolean>(true);
  const [dittiId, setDittiId] = useState<string | null>(null);
  const [accountInfo, setAccountInfo] = useState<any>(null);
  const navigate = useNavigate();

  useEffect(() => {
    /**
     * Checks Cognito authentication status on component mount.
     */
    const checkCognitoAuthStatus = async () => {
      try {
        const res = await makeRequest("/cognito/check-login", { method: "GET" });
        if (res.msg === "Login successful") {
          setIsCognitoAuthenticated(true);
          setDittiId(res.dittiId);
        }
      } catch {
        setIsCognitoAuthenticated(false);
      } finally {
        setIsCognitoLoading(false);
      }
    };

    /**
     * Checks Researcher Cognito authentication status on component mount.
     */
    const checkResearcherAuthStatus = async () => {
      try {
        const res = await makeRequest("/researcher_cognito/check-login", { method: "GET" });
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

    checkCognitoAuthStatus();
    checkResearcherAuthStatus();
  }, []);

  /**
   * Redirects to Cognito login page.
   */
  const cognitoLogin = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/cognito/login`;
  }, []);

  /**
   * Logs out the Cognito user by redirecting to the logout endpoint.
   */
  const cognitoLogout = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/cognito/logout`;
    setIsCognitoAuthenticated(false);
    setDittiId(null);
  }, []);

  /**
   * Redirects to Researcher Cognito login page.
   */
  const researcherLogin = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/researcher_cognito/login`;
  }, [navigate]);

  /**
   * Logs out the Researcher from Cognito by redirecting to the logout endpoint.
   */
  const researcherLogout = useCallback((): void => {
    window.location.href = `${process.env.REACT_APP_FLASK_SERVER}/researcher_cognito/logout`;
    setIsResearcherAuthenticated(false);
    setAccountInfo(null);
  }, [navigate]);

  return (
    <AuthContext.Provider
      value={{
        isCognitoAuthenticated,
        isResearcherAuthenticated,
        isCognitoLoading,
        isResearcherLoading,
        firstLogin,
        dittiId,
        accountInfo,
        cognitoLogin,
        cognitoLogout,
        researcherLogin,
        researcherLogout,
        setFirstLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
