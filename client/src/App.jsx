import React from "react";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import Landpg from "./pages/Landpg";
import Home from "./pages/Home";
import SignIn from "./pages/SignIn";
import SignUp from "./pages/SignUp";
import Header from "./components/Header";
import Header2 from "./components/Header2";
import About from "./pages/About";
import PrivateRoute from "./components/PrivateRoute";
import Profile from "./pages/Profile";

function AppContent() {
  const location = useLocation();

  // List of private routes where Header2 should appear
  const header2Routes = ["/home","/profile"];

  const showHeader2 = header2Routes.some((route) =>
    location.pathname.startsWith(route)
  );

  return (
    <>
      {showHeader2 ? <Header2 /> : <Header />}

      <Routes>
        <Route path="/" element={<Landpg />} />
        <Route path="/home" element={<PrivateRoute><Home /></PrivateRoute>} /> 
        <Route path="/profile" element={<PrivateRoute><Profile /></PrivateRoute>} /> 
        <Route path="/signin" element={<SignIn />} />
        <Route path="/signup" element={<SignUp />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}


