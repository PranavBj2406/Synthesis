import React from "react";
import { Navigate } from "react-router-dom";

export default function PrivateRoute({ children }) {
  const token = localStorage.getItem("token");

  // If no token, redirect to signin page
  if (!token) {
    return <Navigate to="/signin" replace />;
  }

  return children;
}
