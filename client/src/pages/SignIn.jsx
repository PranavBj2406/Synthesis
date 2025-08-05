import React, { useState } from "react";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
export default function SignIn() {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    }

    return newErrors;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = validateForm();

    if (Object.keys(newErrors).length === 0) {
      // Handle successful form submission
      console.log("Sign in data:", formData);
      // Add your sign-in logic here
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <div className="bg-gradient-to-b from-amber-100 via-white to-amber-200 min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      <motion.div
        className="absolute top-20 left-10 w-56 h-56 bg-gradient-to-br from-rose-500 to-amber-300 rounded-full opacity-20 blur-md "
        initial={{ scale: 0.8, opacity: 0, x: 0 }}
        animate={{ scale: 1, opacity: 0.2, x: 1000 }}
        transition={{ duration: 12, delay: 0.2, ease: "linear" }}
      />
      <motion.div
        className="absolute bottom-10 right-10 w-55 h-55 bg-gradient-to-br from-red-500 to-pink-300 rounded-full opacity-20 blur-md"
        initial={{ scale: 0.8, opacity: 0, x: 0 }}
        animate={{ scale: 1, opacity: 0.2, x: -1000 }}
        transition={{ duration: 20, delay: 0.2, ease: "linear" }}
      />
      <motion.div
        className="absolute top-50 left-4 w-24 h-24 bg-gradient-to-br from-orange-500 to-amber-950 rounded-full opacity-15 blur-lg"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 3, opacity: 0.4 }}
        transition={{ duration: 1.2, delay: 0.6 }}
      />
      <motion.div
        className="absolute bottom-10 right-1 w-24 h-24 bg-gradient-to-br from-orange-500 to-amber-950 rounded-full opacity-15 blur-lg"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 4, opacity: 0.4 }}
        transition={{ duration: 1.2, delay: 0.6 }}
      />

      <div className="w-full max-w-md relative z-10">
        {/* Header */}
        <div className="text-center mb-8">
          <p className="text-gray-600 font-semibold">
            Sign in to your Synthesis account
          </p>
        </div>

        {/* Sign In Card */}
        <div className="group">
          <div className="border-none rounded-2xl bg-gradient-to-bl from-amber-300 to-pink-500 shadow-lg   shadow-gray-500 transition-all duration-300">
            <div className="border-3 border-black rounded-2xl bg-white relative bottom-3 right-4 transition-all duration-300 p-8">
              <div className="space-y-6">
                {/* Email Field */}
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-semibold text-gray-700 mb-2 font-manrope"
                  >
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Mail className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl font-manrope focus:outline-none transition-all duration-300 placeholder:font-manrope placeholder:text-sm ${
                        errors.email
                          ? "border-red-400 focus:border-red-500"
                          : "border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
                      }`}
                      placeholder="Enter your email"
                    />
                  </div>
                  {errors.email && (
                    <p className="mt-1 text-sm text-red-500 font-medium">
                      {errors.email}
                    </p>
                  )}
                </div>

                {/* Password Field */}
                <div>
                  <label
                    htmlFor="password"
                    className="block text-sm font-semibold text-gray-700 mb-2 font-manrope"
                  >
                    Password
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Lock className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type={showPassword ? "text" : "password"}
                      id="password"
                      name="password"
                      value={formData.password}
                      onChange={handleInputChange}
                      className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl font-manrope focus:outline-none transition-all duration-300 placeholder:font-manrope placeholder:text-sm ${
                        errors.email
                          ? "border-red-400 focus:border-red-500"
                          : "border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
                      }`}
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-amber-600 transition-colors duration-200"
                    >
                      {showPassword ? (
                        <EyeOff className="h-5 w-5 text-gray-400" />
                      ) : (
                        <Eye className="h-5 w-5 text-gray-400" />
                      )}
                    </button>
                  </div>
                  {errors.password && (
                    <p className="mt-1 text-sm text-red-500 font-medium">
                      {errors.password}
                    </p>
                  )}
                </div>

                {/* Remember Me & Forgot Password */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <input
                      id="remember-me"
                      name="remember-me"
                      type="checkbox"
                      className="h-4 w-4 text-amber-500 focus:ring-amber-400 border-gray-300 rounded"
                    />
                    <label
                      htmlFor="remember-me"
                      className="ml-2 block text-sm text-gray-700 font-manrope"
                    >
                      Remember me
                    </label>
                  </div>
                  <a
                    href="#"
                    className="text-sm font-medium text-amber-600 hover:text-red-500 transition-colors duration-200 font-manrope"
                    onClick={(e) => e.preventDefault()}
                  >
                    Forgot password?
                  </a>
                </div>

                {/* Sign In Button */}
                <div className="group ml-2">
                  <div className="border-2 border-black rounded-xl bg-black ">
                    <button
                      type="button"
                      onClick={handleSubmit}
                      className="w-full border-2 border-black bg-gradient-to-r from-amber-500 via-pink-400 to-red-400 text-white font-semibold py-3 rounded-xl relative bottom-2 right-2 group-hover:bottom-0.5 group-hover:right-0.5 transition-all duration-300 ease-in-out font-manrope hover:text-black"
                    >
                      Sign In →
                    </button>
                  </div>
                </div>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500 font-manrope font-sem">
                      Or continue with
                    </span>
                  </div>
                </div>

                {/* Social Sign In */}
                <div className="flex gap-3 justify-center">
                  <button
                    type="button"
                    className="w-full inline-flex justify-center py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 hover:border-amber-300 transition-all duration-200 font-manrope"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24">
                      <path
                        fill="currentColor"
                        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                      />
                      <path
                        fill="currentColor"
                        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                      />
                      <path
                        fill="currentColor"
                        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                      />
                    </svg>
                    <span className="ml-2">Google</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sign Up Link */}
        <div className="text-center mt-6 font-bold">
          <p className="text-gray-600 font-manrope">
            Don't have an account?{" "}
            <Link
              to="/signup"
              className="font-semibold text-amber-600 hover:text-red-500 transition-colors duration-200"
            >
              Sign up here
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
