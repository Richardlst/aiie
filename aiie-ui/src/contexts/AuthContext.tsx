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
    const local_authData = localStorage.getItem("authData");
    if (local_authData) {
      setAuthData(JSON.parse(local_authData));
    }
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
