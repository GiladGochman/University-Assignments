import React, { useState, useContext } from 'react';
import axios from '../axiosConfig';
import { useNavigate } from 'react-router-dom';
import AuthContext from '../contexts/AuthContext';

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const { dispatch } = useContext(AuthContext);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await axios.post('/login', { username, password });
      const { token, name, email } = response.data;
      console.log('login response:', response.data);

      dispatch({
        type: 'LOGIN',
        payload: {
          user: { name, email, username },
          token,
        },
      });

      navigate('/');
    } catch (err) {
      setError('Invalid credentials. Please try again.');
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        data-testid="login_form_username"
        type="text"
        value={username}
        placeholder="Username"
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        data-testid="login_form_password"
        type="password"
        value={password}
        placeholder="Password"
        onChange={(e) => setPassword(e.target.value)}
      />
      <button data-testid="login_form_login" type="submit">Login</button>
      {error && <p>{error}</p>}
    </form>
  );
};

export default Login;
