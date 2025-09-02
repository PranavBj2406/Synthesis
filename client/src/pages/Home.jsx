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
    <div className="min-h-screen bg-gradient-to-t from-emerald-50 to-white font-manrope">
      {/* Main content wrapper (matches header max-width) */}
      <div className="max-w-[1450px] mx-auto w-full px-4 py-6">
        <p className="text-xl font-bold font-manrope mb-2">
          <span className="text-emerald-500 ">Hello</span> User 🙂
        </p>
        <p className="text-sm font-bold font-manrope mb-3">
          Welcome to Synthesis , a Multimodal Synthetic Healthcare <br></br>{" "}
          Data generator, generate,validate and train model as per to <br></br>
          your requirements and accelerate development
        </p>
        {/* Tabs */}
        <div className="border-none rounded-2xl p-7 bg-gradient-to-br from-gray-300/20 to-gray-300/40  shadow-md ">
          <div className="grid grid-cols-4 mb-5 bg-emerald-200 p-2 rounded-xl shadow-md shadow-gray w-full md:w-[600px] ">
            {[
              {
                value: "generate",
                label: "Generate data",
                icon: <Database className="w-4 h-4" />,
              },
              {
                value: "validation",
                label: "Validation",
                icon: <Activity className="w-4 h-4" />,
              },
              {
                value: "training",
                label: "Training",
                icon: <BookOpen className="w-4 h-4" />,
              },
              {
                value: "about",
                label: "About Data",
                icon: <User className="w-4 h-4" />,
              },
            ].map((tab) => (
              <button
                key={tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={`flex items-center justify-center gap-2 py-2 rounded-lg text-sm font-bold  transition ${
                  activeTab === tab.value
                    ? "bg-emerald-500 text-white shadow-md"
                    : "text-gray-700 hover:bg-emerald-100"
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
                <h2 className="text-3xl font-bold font-manrope mb-3">
                  Generate Synthetic Healthcare Data
                </h2>
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold mb-4">
                    Patient Characteristics
                  </h3>
                  <div className="bg-white border border-none rounded-xl shadow-lg p-6 space-y-6">
                    {/* Age */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <label className="font-medium">Age</label>
                        <span className="font-semibold text-emerald-600">
                          {age}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="18"
                        max="90"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="w-full accent-emerald-600"
                      />
                    </div>

                    {/* Gender */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Gender</label>
                      <div className="relative">
                        <select
                          value={gender}
                          onChange={(e) => setGender(e.target.value)}
                          className="w-1/4 border border-gray-300 rounded-lg px-3 py-2 pr-8 
             bg-white text-gray-700 font-semibold text-sm md:text-sm
             focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 
             appearance-none mt-1 "
                        >
                          <option className="font-semibold text-sm md:text-base">
                            Male
                          </option>
                          <option className="font-semibold text-sm md:text-base">
                            Female
                          </option>
                          <option className="font-semibold text-sm md:text-base">
                            Other
                          </option>
                        </select>
                    
                      </div>
                    </div>

                    {/* Disease */}
                    <div className="space-y-2">
                      <label className="text-sm font-medium">
                        Disease type<br></br>
                      </label>
                      <select
                        value={diseaseType}
                        onChange={(e) => setDiseaseType(e.target.value)}
                        className="w-1/4 border border-gray-300 rounded-lg px-3 py-2 pr-8 
             bg-white text-gray-700 font-semibold text-sm md:text-sm
             focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 
             appearance-none mt-2"
                      >
                       <option className="font-semibold text-sm md:text-base">Diabetes</option>
                        <option className="font-semibold text-sm md:text-base">Heart Disease</option>
                        <option className="font-semibold text-sm md:text-base">Respiratory</option>
                        <option className="font-semibold text-sm md:text-base">Neurological</option>
                       <option className="font-semibold text-sm md:text-base">Others</option>
                      </select>
                    </div>

                    {/* Record Count */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <label className="font-medium">
                          No. of Records to Generate
                        </label>
                        <span className="font-semibold text-emerald-600">
                          {recordCount}
                        </span>
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
                      {/* Note */}
                      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-sm text-emerald-700 mt-5 w-1/2">
                        <b>Note:</b> The quality of data depends on training
                        epochs.
                      </div>

                      {/* Button */}
                      <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className="w-[140px] bg-gray-300/80 text-black text-bold py-2 rounded-full font-semibold hover:bg-gray-400 disabled:opacity-60 duration-500 ease-in-out shadow-black shadow-sm hover:shadow-md mt-4"
                      >
                        {isGenerating ? (
                          <span className="flex items-center justify-center gap-2">
                            <Loader2 className="w-5 h-5 animate-spin" />{" "}
                            Generating data...
                          </span>
                        ) : (
                          "Generate"
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Preview */}
              {/* <div>
                <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6 h-full flex items-center justify-center">
                  {isGenerating ? (
                    <div className="flex flex-col items-center gap-3">
                      <Loader2 className="w-8 h-8 animate-spin text-emerald-600" />
                      <p className="text-sm text-gray-600">
                        Generating data please wait...
                      </p>
                    </div>
                  ) : (
                    <div className="text-center text-gray-500">
                      <Database className="w-12 h-12 mx-auto mb-4 opacity-50" />
                      <p className="text-sm">
                        Click Generate to create synthetic healthcare data
                      </p>
                    </div>
                  )}
                </div>
              </div> */}
            </div>
          )}
          {/* Training Tab Content */}
          {activeTab === "training" && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Form */}
              <div className="lg:col-span-2">
                <h2 className="text-3xl font-bold font-manrope mb-3">
                  Model Training and Parameter Options
                </h2>
                <div className="space-y-3">
                  <h3 className="text-lg font-semibold mb-4">
                    Train the model based on epocs and Batch size
                  </h3>
                  <div className="bg-white border border-none rounded-xl shadow-lg p-6 space-y-6">
                    {/* Age */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <label className="font-medium">Number of Epocs</label>
                        <span className="font-semibold text-emerald-600">
                          {age}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="10"
                        max="300"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        className="w-full accent-emerald-600"
                      />
                    </div>
                    {/* Record Count */}
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <label className="font-medium">
                          Batch Size
                        </label>
                        <span className="font-semibold text-emerald-600">
                          {recordCount}
                        </span>
                      </div>
                      <input
                        type="range"
                        min="8"
                        max="128"
                        step="1"
                        value={recordCount}
                        onChange={(e) => setRecordCount(e.target.value)}
                        className="w-full accent-emerald-600"
                      />
                      {/* Note */}
                      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-sm text-emerald-700 mt-3">
                        <b>Note:</b>The value of Epocs cycle and records that is to be generated effects the time taken to train the model.
                        .So train the model as per to
                        requirements
                      </div>

                      {/* Button */}
                      <button
                        onClick={handleGenerate}
                        disabled={isGenerating}
                        className="w-[140px] bg-gray-300 text-black text-bold py-2 rounded-full font-semibold hover:bg-gray-400 disabled:opacity-60 duration-500 ease-in-out shadow-black shadow-sm hover:shadow-md mt-3"
                      >
                        {isGenerating ? (
                          <span className="flex items-center justify-center gap-2">
                            <Loader2 className="w-5 h-5 animate-spin" />{" "}
                            Traning Model...
                          </span>
                        ) : (
                          "Train Model"
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
