import React, { createContext, useState, useEffect, ReactNode, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { Buffer } from "buffer";
import { makeRequest } from "./utils";
import { AuthContextType } from "./interfaces";
import { APP_ENV } from "./environment";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isIamAuthenticated, setIsIamAuthenticated] = useState<boolean>(false);
  const [isCognitoAuthenticated, setIsCognitoAuthenticated] = useState<boolean>(false);
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [isIamLoading, setIsIamLoading] = useState<boolean>(true);
  const [isCognitoLoading, setIsCognitoLoading] = useState<boolean>(true);
  const [csrfToken, setCsrfToken] = useState<string>(localStorage.getItem("csrfToken") || "");
  const [dittiId, setDittiId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    /**
     * Checks IAM authentication status on component mount.
     */
    const checkIamAuthStatus = async () => {
      if (APP_ENV === "demo") {
        setIsIamAuthenticated(true);
        setIsIamLoading(false);
        return;
      }

      try {
        const jwt = localStorage.getItem("jwt");
        if (jwt) {
          const res = await makeRequest("/iam/check-login", { method: "GET" });
          setIsIamAuthenticated(res.msg === "Login successful");
        } else {
          setIsIamAuthenticated(false);
        }
      } catch {
        setIsIamAuthenticated(false);
      } finally {
        setIsIamLoading(false);
      }
    };

    /**
     * Checks Cognito authentication status on component mount.
     */
    const checkCognitoAuthStatus = async () => {
      if (APP_ENV === "demo") {
        setIsCognitoAuthenticated(true);
        setIsCognitoLoading(false);
        setDittiId("demo001");
        return;
      }

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

    checkIamAuthStatus();
    checkCognitoAuthStatus();
  }, []);

  /**
   * Logs in the user by making a request with basic authentication.
   * @param email - The user's email
   * @param password - The user's password
   */
  const iamLogin = useCallback(async (email: string, password: string): Promise<void> => {
    const auth = Buffer.from(`${email}:${password}`).toString("base64");
    const headers = { Authorization: `Basic ${auth}` };
    const opts = { method: "POST", headers };

    try {
      const res = await makeRequest("/iam/login", opts);
      if (res.jwt) {
        localStorage.setItem("jwt", res.jwt);
        if (res.csrfAccessToken) {
          setCsrfToken(res.csrfAccessToken);
          localStorage.setItem("csrfToken", res.csrfAccessToken);
        }
        setIsIamAuthenticated(true);
        if (res.msg === "First login") {
          setFirstLogin(true);
        } else {
          setFirstLogin(false);
          navigate("/coordinator");
        }
      }
    } catch (error) {
      setIsIamAuthenticated(false);
      throw error;
    }
  }, [navigate]);

  /**
   * Logs out the IAM user by clearing stored tokens and redirecting to login.
   */
  const iamLogout = useCallback((): void => {
    localStorage.removeItem("jwt");
    setIsIamAuthenticated(false);
    setDittiId(null);
    navigate("/coordinator/login");
  }, [navigate]);

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

  return (
    <AuthContext.Provider
      value={{
        isIamAuthenticated,
        isCognitoAuthenticated,
        isIamLoading,
        isCognitoLoading,
        firstLogin,
        csrfToken,
        dittiId,
        iamLogin,
        iamLogout,
        cognitoLogin,
        cognitoLogout,
        setFirstLogin,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
