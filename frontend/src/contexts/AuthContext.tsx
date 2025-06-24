import React, { createContext, useReducer, useContext, ReactNode } from 'react';
import axios from '../axiosConfig';

interface User { name:string; email:string; username:string }
interface State { user: User|null; token: string|null }
type Action =
  | { type:'LOGIN'; payload:{user:User;token:string} }
  | { type:'LOGOUT' };

const ctx = createContext<{ state:State; dispatch:React.Dispatch<Action> }>({
  state:{user:null,token:null}, dispatch:()=>{}
});

const reducer = (s:State,a:Action):State => {
  switch(a.type){
    case 'LOGIN':
      axios.defaults.headers.common['Authorization'] = `Bearer ${a.payload.token}`;
      return { user:a.payload.user, token:a.payload.token };
    case 'LOGOUT':
      delete axios.defaults.headers.common['Authorization'];
      return { user:null, token:null };
    default: return s;
  }
}

export const AuthProvider = ({children}:{children:ReactNode}) => {
  const [state,dispatch] = useReducer(reducer,{user:null,token:null});
  return <ctx.Provider value={{state,dispatch}}>{children}</ctx.Provider>;
};
// eslint-disable-next-line react-refresh/only-export-components
export const useAuth = () => {
  const c = useContext(ctx);
  if(!c) throw new Error('useAuth outside AuthProvider');
  return c;
};