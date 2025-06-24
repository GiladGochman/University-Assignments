import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useNotes } from "../contexts/NotesContext";

export default function Login() {
  const { login } = useNotes(); 
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const success = await login(username, password);

    if (success) {
      navigate("/");
    } else {
      alert("Login failed. Please check your credentials.");
    }
  };

  return (
    <form data-testid="login_form" onSubmit={handleSubmit}>
      <input
        data-testid="login_form_username"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        data-testid="login_form_password"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button data-testid="login_form_login" type="submit">
        Login
      </button>
    </form>
  );
}
