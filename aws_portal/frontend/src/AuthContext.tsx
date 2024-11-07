import React, { createContext, useState, useEffect, ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { Buffer } from "buffer";
import { makeRequest } from "./utils";
import { AuthContextType } from "./interfaces";

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider component that wraps children with authentication context.
 */
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [firstLogin, setFirstLogin] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [csrfToken, setCsrfToken] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    /**
     * Checks authentication status on component mount.
     */
    const checkAuthStatus = async () => {
      try {
        const jwt = localStorage.getItem("jwt");
        if (jwt) {
          // Verify login status with a server request
          const res = await makeRequest("/iam/check-login", { method: "GET" });
          if (res.msg === "Login successful") {
            setIsAuthenticated(true);
            setFirstLogin(false);
          } else if (res.msg === "First login") {
            setIsAuthenticated(true);
            setFirstLogin(true);
          } else {
            setIsAuthenticated(false);
            localStorage.removeItem("jwt");
          }
        } else {
          setIsAuthenticated(false);
        }
      } catch (error) {
        setIsAuthenticated(false);
        localStorage.removeItem("jwt");
      } finally {
        setIsLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  /**
   * Logs in the user by making a request with basic authentication.
   * @param email - The user's email
   * @param password - The user's password
   */
  const login = async (email: string, password: string): Promise<void> => {
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
        setIsAuthenticated(true);
        if (res.msg === "First login") {
          setFirstLogin(true);
        } else {
          setFirstLogin(false);
          navigate("/");
        }
      }
    } catch (error) {
      setIsAuthenticated(false);
      throw error;
    }
  };

  /**
   * Logs out the user by clearing stored tokens and redirecting to login.
   */
  const logout = (): void => {
    localStorage.removeItem("jwt");
    setIsAuthenticated(false);
    navigate("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        isLoading,
        firstLogin,
        csrfToken,
        login,
        logout,
        setFirstLogin,
        setCsrfToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
