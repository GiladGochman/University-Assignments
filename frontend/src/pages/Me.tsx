import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../contexts/AuthContext";

export default function Me() {
  const auth = useContext(AuthContext);
  const navigate = useNavigate();

  if (!auth || !auth.user) {
    // אם המשתמש לא מחובר, מפנים ל-login
    navigate("/login");
    return null;
  }

  const handleLogout = () => {
    auth.logout();
    navigate("/login");
  };

  return (
    <div>
      <h1>Welcome, {auth.user.name}!</h1>
      <p>Email: {auth.user.email}</p>
      <p>Username: {auth.user.username}</p>

      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
