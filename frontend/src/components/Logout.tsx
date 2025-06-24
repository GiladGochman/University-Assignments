import React from 'react';
import {useAuth} from '../contexts/AuthContext';
const Logout:React.FC = () => {
  const {dispatch} = useAuth();
  return <button data-testid="logout" onClick={()=>dispatch({type:'LOGOUT'})}>Logout</button>;
};
export default Logout;