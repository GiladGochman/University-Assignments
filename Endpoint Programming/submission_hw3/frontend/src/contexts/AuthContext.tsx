import React, { createContext, useReducer, useEffect, ReactNode, useContext } from 'react';
import axios from 'axios';

interface User {
  name: string;
  email: string;
  username: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
}

type AuthAction =
  | { type: 'LOGIN'; payload: { user: User; token: string } }
  | { type: 'LOGOUT' };

const AuthContext = createContext<{
  state: AuthState;
  dispatch: React.Dispatch<AuthAction>;
}>({
  state: { user: null, token: null },
  dispatch: () => {},
});

const authReducer = (state: AuthState, action: AuthAction): AuthState => {
  switch (action.type) {
    case 'LOGIN':
      axios.defaults.headers.common['Authorization'] = `Bearer ${action.payload.token}`;
      localStorage.setItem('user-token', JSON.stringify(action.payload));
      return {
        user: action.payload.user,
        token: action.payload.token,
      };
    case 'LOGOUT':
      delete axios.defaults.headers.common['Authorization'];
      localStorage.removeItem('user-token');
      return { user: null, token: null };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    token: null,
  });

  // Load user from localStorage on first load
  useEffect(() => {
    const saved = localStorage.getItem('user-token');
    if (saved) {
      const parsed = JSON.parse(saved);
      axios.defaults.headers.common['Authorization'] = `Bearer ${parsed.token}`;
      dispatch({ type: 'LOGIN', payload: parsed });
    }
  }, []);

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthContext;
