// services/auth.ts
import axios from "axios";

// Define the structure of the response we expect from the login endpoint
export interface LoginResponse {
  token: string;
  name: string;
  email: string;
  username: string;
}

// Login function
export const login = async (
  username: string,
  password: string
): Promise<LoginResponse> => {
  const response = await axios.post(
    `${import.meta.env.VITE_BACKEND_URL}/login`,
    {
      username,
      password,
    }
  );

  if (response.status !== 200) {
    throw new Error("Login failed");
  }

  return response.data;
};

// Create user (register)
export const createUser = async (data: {
  name: string;
  email: string;
  username: string;
  password: string;
}): Promise<void> => {
  const response = await axios.post(
    `${import.meta.env.VITE_BACKEND_URL}/users`,
    data
  );

  if (response.status !== 201) {
    throw new Error("Failed to create user");
  }
};

// "me" function to get current user details from the backend
export const me = async (
  token: string
): Promise<{
  name: string;
  email: string;
  username: string;
}> => {
  const response = await axios.get(`${import.meta.env.VITE_BACKEND_URL}/me`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  if (response.status !== 200) {
    throw new Error("Failed to fetch user details");
  }

  return response.data;
};
