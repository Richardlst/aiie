import { createContext, useContext, useEffect, useState } from "react";
import { AuthData, TokenData } from "../types/auth";
import { jwtDecode } from "jwt-decode";

interface IAuthContext {
  authData: AuthData | null;
  login: (accessToken: string) => void;
  logout: () => void;
}

export const AuthContext = createContext<IAuthContext>({
  authData: null,
  login: () => {},
  logout: () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [authData, setAuthData] = useState<AuthData | null>(null);

  useEffect(() => {
    // Clear all authentication data on app startup
    // This forces all users to log in when the app opens
    localStorage.removeItem("authData");
    setAuthData(null);
  }, []);

  const login = (accessToken: string) => {
    const decodedToken: TokenData = jwtDecode(accessToken);
    const newAuthData: AuthData = {
      tokenData: decodedToken,
      accessToken: accessToken,
    };
    setAuthData(newAuthData);
    localStorage.setItem("authData", JSON.stringify(newAuthData));
  };

  const logout = () => {
    setAuthData(null);
    localStorage.removeItem("authData");
  };

  return (
    <AuthContext.Provider value={{ authData, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const { authData, login, logout } = useContext(AuthContext);
  return { authData, login, logout };
};
