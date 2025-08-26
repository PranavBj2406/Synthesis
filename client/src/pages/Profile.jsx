
import { useState } from "react";
import { Edit, Mail, User, Calendar } from "lucide-react";
import profileAvatar from "../assets/profileIcon2.svg";

export default function Profile({ username, email, memberSince, onUpdateProfile }) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({ username, email });

  const handleSave = () => {
    onUpdateProfile(formData);
    setIsEditing(false);
  };

  return (
    <div className="space-y-8 mt-10 font-manrope">
      {/* Profile Header */}
      <div className="rounded-2xl p-8 bg-white shadow-lg animate-fade-in border-none flex w-1/2 h-64 mx-auto  ">
        <div className="flex flex-col justify-start md:flex-row items-center gap-6">
          {/* Avatar */}
          <div className="relative">
            <div className="w-32 h-32 md:w-48 md:h-48 rounded-full overflow-hidden ring-4 ring-primary/20 shadow-lg">
              <img
                src={profileAvatar}
                alt={username}
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
              {username}
            </h1>
            <p className="text-lg text-gray-500">{email}</p>
            <div className="flex flex-wrap gap-2 justify-center md:justify-start">
              <span className="px-2 py-1 text-sm rounded-full border border-green-400  text-green-600 font-manrope font-semibold">
                Member since {memberSince}
              </span>
              <span className="px-2 py-1 text-sm rounded-full font-semibold bg-blue-100 text-blue-700">
                Verified Account
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Info */}
      <div className="rounded-2xl bg-white shadow p-6">
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
              <User className="w-4 h-4 text-primary" />
              Username
            </label>
            {isEditing ? (
              <input
                id="username"
                value={formData.username}
                onChange={(e) =>
                  setFormData((prev) => ({ ...prev, username: e.target.value }))
                }
                className="w-full border rounded-md px-3 py-2 focus:border-primary focus:ring focus:ring-primary/20 outline-none"
              />
            ) : (
              <p className="px-3 py-2 bg-gray-100 rounded-md font-medium">
                {username}
              </p>
            )}
          </div>

          {/* Email */}
          <div className="space-y-1">
            <label
              htmlFor="email"
              className="flex items-center gap-2 text-sm font-medium text-gray-700"
            >
              <Mail className="w-4 h-4 text-primary" />
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
              <p className="px-3 py-2 bg-gray-100 rounded-md font-medium">
                {email}
              </p>
            )}
          </div>

          {/* Member Since */}
          <div className="space-y-1">
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700">
              <Calendar className="w-4 h-4 text-primary" />
              Member Since
            </label>
            <p className="px-3 py-2 bg-gray-100 rounded-md text-gray-600">
              {memberSince}
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
    </div>
  );
};
