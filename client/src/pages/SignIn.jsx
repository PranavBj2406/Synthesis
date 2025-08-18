import React, { useState, useEffect } from "react";
import { Eye, EyeOff, Mail, Lock } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";

const API_BASE_URL = 'http://localhost:5000';

// API Service
const apiService = {
  async signin(loginData) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(loginData),
      });
      
      const data = await response.json();
      return { success: response.ok, data, status: response.status };
    } catch (error) {
      return { 
        success: false, 
        data: { message: 'Network error. Please try again.' },
        status: 0 
      };
    }
  },

  async fetchProfile(token) {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      return { success: response.ok, data, status: response.status };
    } catch (error) {
      return { 
        success: false, 
        data: { message: 'Failed to fetch profile' },
        status: 0 
      };
    }
  },

  async logout(token) {
    try {
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    }
  }
};

// Toast Notification Component
const Toast = ({ message, type, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 4000);
    return () => clearTimeout(timer);
  }, [onClose]);

  const bgColor = type === 'error' ? 'bg-red-500' : 'bg-green-500';

  return (
    <div className={`fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-pulse`}>
      {message}
    </div>
  );
};

// Main SignIn Component with default export
export default function SignIn({ onSignInSuccess }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    login: '', // Changed to match API expectation
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
    
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.login.trim()) {
      newErrors.login = 'Email or username is required';
    }

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validateForm();

    if (Object.keys(newErrors).length === 0) {
      setLoading(true);
      setErrors({});
      
      const result = await apiService.signin({
        login: formData.login.trim(),
        password: formData.password,
      });

      if (result.success && result.data.success) {
        const { token, ...userData } = result.data.data;
        
        // Store auth data
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(userData));
        
        // Set up API headers for future requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        
        setToast({ message: 'Login successful!', type: 'success' });
        
        // Handle success - either use callback or navigate directly
        if (onSignInSuccess) {
          setTimeout(() => {
            onSignInSuccess(userData, token);
          }, 1000);
        } else {
          // Default behavior: navigate to dashboard
          setTimeout(() => {
            navigate('/dashboard');
          }, 1000);
        }
      } else {
        const errorMessage = result.data?.message || 'Login failed. Please try again.';
        setToast({ message: errorMessage, type: 'error' });
        
        if (result.status === 401) {
          setErrors({ login: 'Invalid credentials' });
        }
      }
      setLoading(false);
    } else {
      setErrors(newErrors);
    }
  };

  return (
    <div className="bg-gradient-to-b from-amber-100 via-white to-amber-200 min-h-screen flex items-center justify-center px-4 relative overflow-hidden">
      {/* Toast notification */}
      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}

      {/* Animated background elements */}
      <motion.div
        className="absolute top-20 left-10 w-56 h-56 bg-gradient-to-br from-rose-500 to-amber-300 rounded-full opacity-20 blur-md"
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
          <div className="border-none rounded-2xl bg-gradient-to-bl from-amber-300 to-pink-500 shadow-lg shadow-gray-500 transition-all duration-300">
            <form onSubmit={handleSubmit} className="border-3 border-black rounded-2xl bg-white relative bottom-3 right-4 transition-all duration-300 p-8">
              <div className="space-y-6">
                {/* Email/Login Field */}
                <div>
                  <label
                    htmlFor="login"
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
                      id="login"
                      name="login"
                      value={formData.login}
                      onChange={handleInputChange}
                      disabled={loading}
                      className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl font-manrope font-semibold focus:outline-none transition-all duration-300 placeholder:font-manrope placeholder:text-sm placeholder:font-semibold  ${
                        errors.login
                          ? "border-red-400 focus:border-red-500"
                          : "border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
                      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                      placeholder="Enter your email"
                    />
                  </div>
                  {errors.login && (
                    <p className="mt-1 text-sm text-red-500 font-medium">
                      {errors.login}
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
                      disabled={loading}
                      className={`w-full pl-10 pr-4 py-3 border-2 rounded-xl font-manrope font-semibold focus:outline-none transition-all duration-300 placeholder:font-manrope placeholder:text-sm placeholder:font-semibold  ${
                        errors.password
                          ? "border-red-400 focus:border-red-500"
                          : "border-gray-200 focus:border-amber-400 focus:ring-2 focus:ring-amber-200"
                      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                      placeholder="Enter your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      disabled={loading}
                      className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-amber-600 transition-colors duration-200 disabled:opacity-50"
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
                      id="rememberMe"
                      name="rememberMe"
                      type="checkbox"
                      checked={formData.rememberMe}
                      onChange={handleInputChange}
                      disabled={loading}
                      className="h-4 w-4 text-amber-500 focus:ring-amber-400 border-gray-300 rounded disabled:opacity-50"
                    />
                    <label
                      htmlFor="rememberMe"
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
                  <div className="border-2 border-black rounded-xl bg-black">
                    <button
                      type="submit"
                      disabled={loading}
                      className={`w-full border-2 border-black bg-gradient-to-r from-amber-500 via-pink-400 to-red-400 text-white font-semibold py-3 rounded-xl relative bottom-2 right-2 group-hover:bottom-0.5 group-hover:right-0.5 transition-all duration-300 ease-in-out font-manrope hover:text-black ${
                        loading ? 'opacity-50 cursor-not-allowed' : ''
                      }`}
                    >
                      {loading ? 'Signing In...' : 'Sign In →'}
                    </button>
                  </div>
                </div>

                {/* Divider */}
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300"></div>
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500 font-manrope font-semibold">
                      Or continue with
                    </span>
                  </div>
                </div>

                {/* Social Sign In */}
                <div className="flex gap-3 justify-center">
                  <button
                    type="button"
                    disabled={loading}
                    className={`w-full inline-flex justify-center py-3 px-4 border-2 border-gray-200 rounded-xl shadow-sm bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 hover:border-amber-300 transition-all duration-200 font-manrope ${
                      loading ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
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
            </form>
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