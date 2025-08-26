import { useState, useEffect } from "react";
import { Edit, Mail, User, Calendar, LogOut } from "lucide-react";
import { Lock } from "lucide-react";
import profileAvatar from "../assets/profileIcon2.svg";

export default function Profile({ onUpdateProfile, onLogout }) {
  const [isEditing, setIsEditing] = useState(false);
  const [userProfile, setUserProfile] = useState({
    username: "",
    email: "",
    memberSince: "",
  });
  const [formData, setFormData] = useState({ username: "", email: "" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  // Base API URL
  const API_BASE_URL = "http://localhost:5000/api";

  // Function to get auth token from localStorage or wherever you store it
  const getAuthToken = () => {
    return localStorage.getItem("token") || sessionStorage.getItem("token");
  };

  // Fetch user profile on component mount
  useEffect(() => {
    fetchUserProfile();
  }, []);

  const fetchUserProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = getAuthToken();
      console.log("Auth token:", token ? "Found" : "Not found");

      if (!token) {
        throw new Error("No authentication token found");
      }

      console.log("Making request to:", `${API_BASE_URL}/auth/profile`);

      const response = await fetch(`${API_BASE_URL}/auth/profile`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      console.log("Response status:", response.status);
      console.log(
        "Response headers:",
        Object.fromEntries(response.headers.entries())
      );

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);

        if (response.status === 401) {
          throw new Error("Session expired. Please login again.");
        }
        throw new Error(
          `Failed to fetch profile: ${response.status} - ${errorText}`
        );
      }

      const data = await response.json();
      console.log("Raw API response:", data);

      // Extract data from the API response structure
      const userData = data.data || data; // Get the data object from response

      const profile = {
        username:
          userData.username ||
          userData.name ||
          userData.full_name ||
          "Unknown User",
        email: userData.email || "No email",
        memberSince:
          userData.memberSince ||
          userData.member_since ||
          userData.created_at ||
          userData.createdAt ||
          "Unknown",
      };

      // Format the date if it's in ISO format
      if (
        profile.memberSince !== "Unknown" &&
        profile.memberSince.includes("T")
      ) {
        const date = new Date(profile.memberSince);
        profile.memberSince = date.toLocaleDateString("en-US", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
      }

      console.log("Processed profile data:", profile);

      setUserProfile(profile);
      setFormData({
        username: profile.username,
        email: profile.email,
      });
    } catch (error) {
      console.error("Error fetching user profile:", error);
      setError(error.message);

      // If unauthorized, redirect to login or clear tokens
      if (
        error.message.includes("Session expired") ||
        error.message.includes("No authentication token")
      ) {
        localStorage.removeItem("token");
        sessionStorage.removeItem("token");
        // You might want to redirect to login page here
        // window.location.href = '/login';
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setError(null);

      const token = getAuthToken();
      if (!token) {
        throw new Error("No authentication token found");
      }

      // If you have an update profile endpoint, use it
      // Otherwise, just update local state
      if (onUpdateProfile) {
        await onUpdateProfile(formData);
      }

      // Update local state
      setUserProfile((prev) => ({
        ...prev,
        username: formData.username,
        email: formData.email,
      }));

      setIsEditing(false);
      console.log("Profile updated successfully");
    } catch (error) {
      console.error("Error updating profile:", error);
      setError(error.message);
    }
  };

  const handleLogout = async () => {
    try {
      setIsLoggingOut(true);
      setError(null);

      const token = getAuthToken();

      // Call logout endpoint
      const response = await fetch(`${API_BASE_URL}/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      // Clear tokens regardless of response (in case server is down)
      localStorage.removeItem("token");
      sessionStorage.removeItem("token");

      if (response.ok) {
        console.log("Logout successful");
      } else {
        console.warn(
          "Logout endpoint returned error, but tokens cleared locally"
        );
      }

      // Call parent component's logout handler if provided
      if (onLogout) {
        onLogout();
      } else {
        // Default behavior - redirect to login
        window.location.href = "/login";
      }
    } catch (error) {
      console.error("Error during logout:", error);

      // Even if logout fails, clear tokens and redirect
      localStorage.removeItem("token");
      sessionStorage.removeItem("token");

      if (onLogout) {
        onLogout();
      } else {
        window.location.href = "/login";
      }
    } finally {
      setIsLoggingOut(false);
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="space-y-8 mt-10 font-manrope">
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="text-lg text-gray-600">Loading profile...</div>
          <div className="text-sm text-gray-500">
            Check browser console for debug info
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error && !userProfile.username) {
    return (
      <div className="space-y-8 mt-10 font-manrope">
        <div className="flex flex-col items-center justify-center h-64 space-y-4">
          <div className="text-lg text-red-600">Error: {error}</div>
          <button
            onClick={fetchUserProfile}
            className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 mt-10 font-manrope">
      {/* Error message */}
      {error && (
        <div className="mx-auto w-2/3 p-4 bg-red-100 border border-red-300 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* Profile Header */}
      <div className="rounded-2xl p-8 bg-slate-100/60 shadow-lg animate-fade-in border-none flex w-2/3 h-64 mx-auto">
        <div className="flex flex-col justify-start md:flex-row items-center gap-6">
          {/* Avatar */}
          <div className="relative">
            <div className="w-32 h-32 md:w-48 md:h-48 rounded-full overflow-hidden ring-4 ring-primary/20 shadow-lg">
              <img
                src={profileAvatar}
                alt={userProfile.username}
                className="w-full h-full object-cover"
              />
            </div>
            <span className="absolute -bottom-2 -right-2 bg-green-100 text-green-800 text-xs font-medium px-2 py-1 rounded-md shadow">
              Active
            </span>
          </div>

          {/* User Info */}
          <div className="flex-1 text-center md:text-left space-y-2">
            <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
              {userProfile.username}
            </h1>
            <p className="text-lg text-gray-500">{userProfile.email}</p>
            <div className="flex flex-wrap gap-2 justify-center md:justify-start">
              <span className="px-2 py-1 text-sm rounded-full border border-green-400 text-green-600 font-manrope font-bold">
                Member since {userProfile.memberSince}
              </span>
              <span className="px-2 py-1 text-sm rounded-full font-semibold bg-amber-300/40 text-black">
                Verified Account
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Parent div comprising of profile info and security settings */}
      <div className="w-[1050px] mx-auto px-4 space-y-8 flex flex-row">
        {/* Profile Info */}
        <div className="rounded-2xl bg-slate-100/40 shadow-xl p-6 w-[60%]">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-xl font-semibold">Profile Information</h2>
              <p className="text-sm text-gray-500">
                Manage your account details and preferences
              </p>
            </div>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="flex items-center gap-2 px-3 py-1.5 border border-primary/20 rounded-md text-sm hover:bg-primary/5 transition"
            >
              <Edit className="w-4 h-4" />
              {isEditing ? "Cancel" : "Edit"}
            </button>
          </div>

          <div className="space-y-4">
            {/* Username */}
            <div className="space-y-1">
              <label
                htmlFor="username"
                className="flex items-center gap-2 text-sm font-medium text-gray-700"
              >
                <User className="w-4 h-4 text-primary text-green-600" />
                Username
              </label>
              {isEditing ? (
                <input
                  id="username"
                  value={formData.username}
                  onChange={(e) =>
                    setFormData((prev) => ({
                      ...prev,
                      username: e.target.value,
                    }))
                  }
                  className="w-full border rounded-md px-3 py-2 focus:border-primary focus:ring focus:ring-primary/20 outline-none"
                />
              ) : (
                <p className="px-3 py-2 bg-gray-100 rounded-md font-manrope font-semibold text-sm">
                  {userProfile.username}
                </p>
              )}
            </div>

            {/* Email */}
            <div className="space-y-1">
              <label
                htmlFor="email"
                className="flex items-center gap-2 text-sm font-medium text-gray-700"
              >
                <Mail className="w-4 h-4 text-primary text-green-600" />
                Email Address
              </label>
              {isEditing ? (
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) =>
                    setFormData((prev) => ({ ...prev, email: e.target.value }))
                  }
                  className="w-full border rounded-md px-3 py-2 focus:border-primary focus:ring focus:ring-primary/20 outline-none"
                />
              ) : (
                <p className="px-3 py-2 bg-gray-100 rounded-md font-manrope font-semibold text-sm">
                  {userProfile.email}
                </p>
              )}
            </div>

            {/* Member Since */}
            <div className="space-y-1">
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Calendar className="w-4 h-4 text-primary text-green-600" />
                Member Since
              </label>
              <p className="px-3 py-2 bg-gray-100 rounded-md font-manrope font-semibold text-sm">
                {userProfile.memberSince}
              </p>
            </div>
          </div>

          {/* Save/Cancel Buttons */}
          {isEditing && (
            <div className="flex gap-3 pt-6">
              <button
                onClick={handleSave}
                className="px-4 py-2 rounded-md bg-primary text-white hover:bg-primary/90 transition"
              >
                Save Changes
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 rounded-md border border-gray-300 hover:bg-gray-50 transition"
              >
                Cancel
              </button>
            </div>
          )}
        </div>

        {/* Security panel */}
        <div className="w-[40%] flex flex-col">
          <div className=" ml-4 rounded-2xl bg-slate-100/40 shadow-xl p-6 h-fit">
            <div className="flex items-center gap-2 text-lg">
              <Lock className="w-4 h-4 text-primary text-green-600" />
              <h1 className="font-semibold">Security Settings</h1>
            </div>
            <p className="text-sm mt-3 font-semibold text-green-600">
              Keep your account secure by updating your password regularly
            </p>

            <button className="mt-4 w-1/2 px-3 py-3 bg-primary text-white bg-yellow-500 border-none shadow-md border-amber-500 text-sm font-bold rounded-md transition hover:bg-yellow-400 duration-300 ease-in-out hover:scale-105">
              Update Password
            </button>
          </div>

          <div className="ml-4 rounded-2xl bg-slate-100/40 shadow-xl p-6 h-[35%] mt-4">
            <div className="flex items-center gap-2 text-lg">
              <LogOut className="w-4 h-4 text-red-500" />
              <h1 className="font-semibold">Logout</h1>
            </div>
            <button
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="mt-4 w-1/2 px-3 py-3  bg-red-500 text-white border-none shadow-md text-sm font-bold rounded-md transition hover:bg-red-400 duration-300 ease-in-out hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed  gap-2"
            >
            
              {isLoggingOut ? "Logging out..." : "Logout"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
