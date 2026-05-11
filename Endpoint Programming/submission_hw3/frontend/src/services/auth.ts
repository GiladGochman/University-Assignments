// services/auth.ts
export const createUser = async (data: {
  name: string;
  email: string;
  username: string;
  password: string;
}) => {
  const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to create user");
  }

  return await response.json();
};
