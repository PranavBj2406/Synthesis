import React, { useState } from "react";
import { Loader2, User, Database, Activity, BookOpen } from "lucide-react";

export default function Home() {
  const [age, setAge] = useState(42);
  const [gender, setGender] = useState("Male");
  const [diseaseType, setDiseaseType] = useState("Diabetes");
  const [recordCount, setRecordCount] = useState(1000);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState("generate");

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => setIsGenerating(false), 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-100 to-white">
      {/* Main content wrapper (matches header max-width) */}
      <div className="max-w-[1450px] mx-auto w-full px-4 py-10">
        {/* Tabs */}
        <div className="grid grid-cols-4 gap-2 mb-10 bg-emerald-50 p-2 rounded-xl w-full md:w-2/3">
          {[
            { value: "generate", label: "Generate data", icon: <Database className="w-4 h-4" /> },
            { value: "validation", label: "Validation", icon: <Activity className="w-4 h-4" /> },
            { value: "training", label: "Training", icon: <BookOpen className="w-4 h-4" /> },
            { value: "about", label: "About Data", icon: <User className="w-4 h-4" /> },
          ].map((tab) => (
            <button
              key={tab.value}
              onClick={() => setActiveTab(tab.value)}
              className={`flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-medium transition ${
                activeTab === tab.value
                  ? "bg-emerald-500 text-white shadow-md"
                  : "text-gray-600 hover:bg-emerald-100"
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>

        {/* Generate Tab Content */}
        {activeTab === "generate" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Form */}
            <div className="lg:col-span-2">
              <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6 space-y-8">
                <h2 className="text-2xl font-bold">Generate Synthetic Healthcare Data</h2>

                <div className="space-y-6">
                  <h3 className="text-lg font-semibold">Patient Characteristics</h3>

                  {/* Age */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <label className="font-medium">Age</label>
                      <span className="font-semibold text-emerald-600">{age}</span>
                    </div>
                    <input
                      type="range"
                      min="1"
                      max="100"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      className="w-full accent-emerald-600"
                    />
                  </div>

                  {/* Gender */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Gender</label>
                    <select
                      value={gender}
                      onChange={(e) => setGender(e.target.value)}
                      className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    >
                      <option>Male</option>
                      <option>Female</option>
                      <option>Other</option>
                    </select>
                  </div>

                  {/* Disease */}
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Disease type</label>
                    <select
                      value={diseaseType}
                      onChange={(e) => setDiseaseType(e.target.value)}
                      className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-emerald-500"
                    >
                      <option>Diabetes</option>
                      <option>Hypertension</option>
                      <option>Heart Disease</option>
                      <option>Cancer</option>
                      <option>Respiratory</option>
                    </select>
                  </div>

                  {/* Record Count */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <label className="font-medium">No. of Records to Generate</label>
                      <span className="font-semibold text-emerald-600">{recordCount}</span>
                    </div>
                    <input
                      type="range"
                      min="10"
                      max="10000"
                      step="10"
                      value={recordCount}
                      onChange={(e) => setRecordCount(e.target.value)}
                      className="w-full accent-emerald-600"
                    />
                  </div>
                </div>

                {/* Note */}
                <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-sm text-emerald-700">
                  <b>Note:</b> The quality of data depends on training epochs.
                </div>

                {/* Button */}
                <button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full bg-emerald-500 text-white py-3 rounded-lg font-semibold hover:bg-emerald-600 disabled:opacity-60"
                >
                  {isGenerating ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="w-5 h-5 animate-spin" /> Generating data...
                    </span>
                  ) : (
                    "Generate"
                  )}
                </button>
              </div>
            </div>

            {/* Preview */}
            <div>
              <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6 h-full flex items-center justify-center">
                {isGenerating ? (
                  <div className="flex flex-col items-center gap-3">
                    <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
                    <p className="text-sm text-gray-600">Generating data please wait...</p>
                  </div>
                ) : (
                  <div className="text-center text-gray-500">
                    <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm">Click Generate to create synthetic healthcare data</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
