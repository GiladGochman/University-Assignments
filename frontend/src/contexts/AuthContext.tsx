import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  JSX,
} from "react";
import axios from "axios";
import * as authService from "../services/auth";

export interface User {
  name: string;
  email: string;
  username: string;
}

interface AuthContextValue {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (
    user: Omit<User, "username"> & { username: string; password: string }
  ) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

interface Props {
  children: ReactNode;
}

export const AuthProvider = ({ children }: Props): JSX.Element => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(() => {
    const stored = localStorage.getItem("token");
    return stored ?? null;
  });

  //    When the provider mounts try to read localStorage if a token already exists

  useEffect(() => {
    if (!token) return;

    (async () => {
      try {
        const profile = await authService.me(token);
        setUser(profile);
      } catch {
        // Token is invalid, wipe it out.
        logout();
      }
    })();
  }, []);

  /**
   * Whenever the token changes, automatically attach/detach the
   * Authorization header to every axios request, so the rest of the
   * codebase doesn’t need to think about it.
   */
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`;
      localStorage.setItem("token", token);
    } else {
      delete axios.defaults.headers.common.Authorization;
      localStorage.removeItem("token");
    }
  }, [token]);

  const login = async (username: string, password: string) => {
    const {
      token: newToken,
      name,
      email,
    } = await authService.login(username, password);
    setToken(newToken);
    setUser({ name, email, username });
  };

  const register = async (
    data: Omit<User, "username"> & { username: string; password: string }
  ) => {
    await authService.createUser(data);
    // After registration, user is redirected to login page
  };

  const logout = () => {
    setToken(null);
    setUser(null);
  };

  const value: AuthContextValue = {
    user,
    token,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook
export const useAuth = (): AuthContextValue => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside <AuthProvider>");
  return ctx;
};
