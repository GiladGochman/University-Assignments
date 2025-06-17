import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createUser } from "../services/auth";

export default function CreateUser() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      console.log("Creating user with:", { name, email, username, password });

      await createUser({ name, email, username, password });
      console.log("User created successfully");

      navigate("/");
    } catch (err) {
      console.error("Failed to create user:", err);
    }
  };

  return (
    <form data-testid="create_user_form" onSubmit={handleSubmit}>
      <input
        data-testid="create_user_form_name"
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />
      <input
        data-testid="create_user_form_email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        data-testid="create_user_form_username"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        data-testid="create_user_form_password"
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button data-testid="create_user_form_create_user" type="submit">
        Create User
      </button>
    </form>
  );
}
