import React from "react";
import { Player } from "@lottiefiles/react-lottie-player";
import { Link } from "react-router-dom";
import { FaGoogle } from "react-icons/fa";
import { FaUserAlt } from "react-icons/fa";
import { useState } from "react";
import { IoMdAlert } from "react-icons/io";

// api base url
const VITE_API_BASE_URL = "http://localhost:5000";

const apiService = {
  async SignUp(userData) {
    const response = await fetch(`${VITE_API_BASE_URL}/api/auth/signup`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(userData),
    });
    return response.json();
  },
};

export default function SignUp() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [passwordValid, setPasswordValid] = useState(null); // null = untouched, true = valid, false = invalid
  const [passwordError, setPasswordError] = useState("");

  // status state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  // Password validation function
  const validatePassword = (password) => {
    const errors = [];
    if (password.length < 8) errors.push("at least 8 characters");
    if (!/[A-Z]/.test(password)) errors.push("an uppercase letter");
    if (!/[a-z]/.test(password)) errors.push("a lowercase letter");
    if (!/[0-9]/.test(password)) errors.push("a number");
    if (!/[^A-Za-z0-9]/.test(password)) errors.push("a special character");
    return errors;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    setMessage(""); // clear message when user types

    if (name === "password") {
      const errors = validatePassword(value);
      if (value.length === 0) {
        setPasswordValid(null);
        setPasswordError("");
      } else if (errors.length === 0) {
        setPasswordValid(true);
        setPasswordError("");
      } else {
        setPasswordValid(false);
        setPasswordError(
          `Password must contain ${errors.join(", ")}.`
        );
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();


    if (!formData.username || !formData.email || !formData.password) {
      setMessage("Please fill in all required fields");
      return;
    }
    // Password validation before submit
    const errors = validatePassword(formData.password);
    if (errors.length > 0) {
      setPasswordValid(false);
      setPasswordError(`Password must contain ${errors.join(", ")}.`);
      setMessage("Password does not meet requirements");
      return;
    }

    setIsSubmitting(true);
    setMessage("");

    try {
      const result = await apiService.SignUp(formData);

      if (result.success) {
        // Store JWT token
        if (typeof window !== "undefined") {
          window.localStorage?.setItem("authToken", result.data.token);
          window.localStorage?.setItem("user", JSON.stringify(result.data));
        }

        setMessage("Account created successfully!");
        console.log("User registered:", result.data);

        // Reset form
        setFormData({ username: "", email: "", password: "" });
      } else {
        setMessage(result.message || "Registration failed");
      }
    } catch (error) {
      setMessage("Network error. Please check your backend server.");
      console.error("Signup error:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className=" flex flex-row min-h-screen  ">
      {/* left container */}
      <div className="flex items-center justify-center  w-1/2  z-5 bg-gradient-to-b from-amber-100 to-amber-200">
        <div className=" w-3/4 h-auto border-black rounded-3xl shadow-lg shadow-gray-600  bg-black  ">
          <div className="w-full h-full  relative bg-amber-50 rounded-2xl bottom-5  right-6 border-3 border-black z-2 px-5 py-5 ">
            <p className="text-4xl font-semibold font-manrope">
              Welcome to{" "}
              <span className=" bg-gradient-to-r from-pink-500 via-red-400 to-amber-500 bg-clip-text text-transparent">
                Synthesis
              </span>
            </p>
            <h1 className="text-2xl font-manrope font-semibold text-gray-500 mt-3">
              Sign up
            </h1>

            {/* Form starts here */}
            <form onSubmit={handleSubmit}>
              <h1 className="mt-5 text-lg font-manrope font-semibold ">
                Username
              </h1>
              <div className="h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5">
                <input
                  className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                  placeholder="enter your username."
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </div>

              <h1 className="mt-5 text-lg font-manrope font-semibold ">
                Email
              </h1>
              <div className="h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5">
                <input
                  className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                  placeholder="enter your email address."
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </div>

              <div className="flex flex-row items-center gap-2 mt-4">
                <h1 className="text-lg font-manrope font-semibold">Password</h1>
                <IoMdAlert
                  className={`text-2xl cursor-pointer duration-700 ease-in-out ${passwordValid === false ? "text-red-600" : "text-gray-600 hover:text-amber-800"}`}
                  title={
                    "Password must contain at least 8 characters, an uppercase letter, a lowercase letter, a number, and a special character."
                  }
                />
              </div>
              <div className={`h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5 ${passwordValid === false ? "border-red-500" : passwordValid === true ? "border-black" : ""}`}>
                <input
                  className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                  placeholder="enter password"
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isSubmitting}
                />
              </div>
              {passwordValid === false && (
                <div className="mt-2 text-red-600 text-sm font-manrope font-semibold">
                  {passwordError}
                </div>
              )}

              {message && (
                <div className="mt-4 text-red-600 font-manrope font-semibold">
                  {message}
                </div>
              )}

              <div className="flex flex-row justify-start gap-6 mt-10">
                <div className="w-1/3 border-2 rounded-md ml-2 bg-black ">
                  <button
                    type="submit"
                    className="w-full h-[50px] border-2 border-black rounded-md font-manrope font-bold  text-white bg-blue-500 relative right-2 bottom-2 hover:relative hover:bottom-1 hover:right-1 duration-300 ease-in-out hover:bg-blue-400"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? "Signing Up..." : "Sign Up"}
                  </button>
                </div>

                <span className="flex justify-center items-center mt-1 p-1 font-manrope font-semibold ">
                  or
                </span>

                <div className="w-auto border-2 rounded-md ml-2 bg-black ">
                  <button
                    type="button"
                    className="w-auto p-3 h-[50px] border-2 border-black rounded-md font-manrope font-bold  text-white bg-purple-700 relative right-2 bottom-2 hover:relative hover:bottom-1 hover:right-1 duration-300 ease-in-out hover:bg-purple-600 flex flex-row justify-center items-center gap-3"
                  >
                    <FaGoogle className="scale-110" /> Sign Up with google
                  </button>
                </div>
              </div>
            </form>
            {/* Form ends here */}

            <div className="mt-5 border-t-2  " />

            <div className="mt-5">
              <p className="text-sm font-manrope font-bold">
                Already have an account?{" "}
                <Link
                  to="/signin"
                  className="ml-1 text-purple-600 hover:text-black duration-500"
                >
                  Sign In.
                </Link>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* right side container */}
      <div className="flex justify-center items-center w-1/2 z-0 bg-gradient-to-b from-amber-100 to-amber-200 relative">
        {/* Custom background shape */}
        <svg
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 z-0"
          width="650"
          height="600"
          viewBox="0 0 650 600"
          fill="none"
          style={{ filter: "blur(16px)" }}
        >
          <defs>
            <radialGradient id="bgGradient" cx="50%" cy="50%" r="80%">
              <stop offset="0%" stopColor="#fbbf24" stopOpacity="0.7" />
              <stop offset="60%" stopColor="#f472b6" stopOpacity="0.5" />
              <stop offset="100%" stopColor="#f87171" stopOpacity="0.3" />
            </radialGradient>
          </defs>
          <path
            d="
              M 100 400
              Q 180 200 350 150
              Q 500 120 600 250
              Q 650 350 500 500
              Q 350 600 200 500
              Q 80 450 100 400
              Z
            "
            fill="url(#bgGradient)"
          />
        </svg>
        <div className="flex justify-center items-center border-none rounded-full relative bottom-5 z-10">
          <Player
            src="https://assets.lottiefiles.com/packages/lf20_kkflmtur.json"
            background="transparent"
            speed={1}
            style={{ width: "550px", height: "550px" }}
            loop
            autoplay
          />
        </div>
      </div>
    </div>
  );
}
