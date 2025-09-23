import React, { useState } from "react";
import { Loader2, User, Database, Activity, BookOpen, Download, FileText, CheckCircle, AlertCircle } from "lucide-react";

export default function Home() {
  const [age, setAge] = useState(42);
  const [gender, setGender] = useState("Male");
  const [diseaseType, setDiseaseType] = useState("Diabetes");
  const [recordCount, setRecordCount] = useState(1000);
  const [epochs, setEpochs] = useState(100);
  const [batchSize, setBatchSize] = useState(32);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [activeTab, setActiveTab] = useState("generate");
  const [generatedData, setGeneratedData] = useState(null);
  const [trainingResults, setTrainingResults] = useState(null);
  const [error, setError] = useState(null);

  // API call for generating healthcare data
  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedData(null);

    try {
      const response = await fetch('http://localhost:5000/api/healthcare-gan/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          num_samples: parseInt(recordCount),
          model_type: 'patient_data',
          parameters: {
            age: parseInt(age),
            gender: gender,
            disease_type: diseaseType
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setGeneratedData(data);
    } catch (err) {
      setError(`Failed to generate data: ${err.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  // API call for training model
  const handleTrain = async () => {
    setIsTraining(true);
    setError(null);
    setTrainingResults(null);

    try {
      const response = await fetch('http://localhost:5000/api/healthcare-gan/train', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          dataset: 'healthcare_records',
          epochs: parseInt(epochs),
          batch_size: parseInt(batchSize),
          model_type: diseaseType.toLowerCase()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setTrainingResults(data);
    } catch (err) {
      setError(`Failed to train model: ${err.message}`);
    } finally {
      setIsTraining(false);
    }
  };

  // Download generated data as JSON
  const downloadData = () => {
    if (!generatedData) return;
    
    const dataStr = JSON.stringify(generatedData, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    
    const exportFileDefaultName = `healthcare_data_${new Date().toISOString().split('T')[0]}.json`;
    
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  // Render generated data results
  const renderDataResults = () => {
    if (!generatedData) return null;

    return (
      <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6 mt-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-500" />
            Generated Healthcare Data
          </h3>
          <button
            onClick={downloadData}
            className="flex items-center gap-2 px-3 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
          >
            <Download className="w-4 h-4" />
            Download JSON
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-emerald-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-emerald-600">{generatedData.num_samples || recordCount}</div>
            <div className="text-sm text-gray-600">Records Generated</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{generatedData.model_type || 'patient_data'}</div>
            <div className="text-sm text-gray-600">Model Type</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">{generatedData.generation_time || 'N/A'}s</div>
            <div className="text-sm text-gray-600">Generation Time</div>
          </div>
        </div>

        {/* Sample data preview */}
        {generatedData.data && generatedData.data.length > 0 && (
          <div>
            <h4 className="font-medium mb-3">Sample Generated Records (First 5)</h4>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto border-collapse">
                <thead>
                  <tr className="bg-gray-50">
                    {Object.keys(generatedData.data[0]).map((key) => (
                      <th key={key} className="border px-4 py-2 text-left text-sm font-medium text-gray-700">
                        {key.replace('_', ' ').toUpperCase()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {generatedData.data.slice(0, 5).map((record, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      {Object.values(record).map((value, idx) => (
                        <td key={idx} className="border px-4 py-2 text-sm text-gray-600">
                          {typeof value === 'number' ? value.toFixed(2) : value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {generatedData.data.length > 5 && (
              <p className="text-sm text-gray-500 mt-2">
                Showing 5 of {generatedData.data.length} records. Download full dataset using the button above.
              </p>
            )}
          </div>
        )}

        {/* Metadata */}
        {generatedData.metadata && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Generation Metadata</h4>
            <pre className="text-sm text-gray-600 overflow-x-auto">
              {JSON.stringify(generatedData.metadata, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  // Render training results
  const renderTrainingResults = () => {
    if (!trainingResults) return null;

    return (
      <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6 mt-6">
        <h3 className="text-lg font-semibold flex items-center gap-2 mb-4">
          <CheckCircle className="w-5 h-5 text-green-500" />
          Training Results
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{trainingResults.final_loss || 'N/A'}</div>
            <div className="text-sm text-gray-600">Final Loss</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{trainingResults.training_time || 'N/A'}s</div>
            <div className="text-sm text-gray-600">Training Time</div>
          </div>
        </div>

        {trainingResults.metrics && (
          <div className="p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Training Metrics</h4>
            <pre className="text-sm text-gray-600 overflow-x-auto">
              {JSON.stringify(trainingResults.metrics, null, 2)}
            </pre>
          </div>
        )}
      </div>
    );
  };

  // Error display component
  const renderError = () => {
    if (!error) return null;

    return (
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 mt-6">
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">Error</span>
        </div>
        <p className="text-red-600 mt-1">{error}</p>
      </div>
    );
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
            <div>
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
                              Generating...
                            </span>
                          ) : (
                            "Generate"
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Error Display */}
              {renderError()}
              
              {/* Results Display */}
              {renderDataResults()}
            </div>
          )}

          {/* Training Tab Content */}
          {activeTab === "training" && (
            <div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Form */}
                <div className="lg:col-span-2">
                  <h2 className="text-3xl font-bold font-manrope mb-3">
                    Model Training and Parameter Options
                  </h2>
                  <div className="space-y-3">
                    <h3 className="text-lg font-semibold mb-4">
                      Train the model based on epochs and Batch size
                    </h3>
                    <div className="bg-white border border-none rounded-xl shadow-lg p-6 space-y-6">
                      {/* Epochs */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <label className="font-medium">Number of Epochs</label>
                          <span className="font-semibold text-emerald-600">
                            {epochs}
                          </span>
                        </div>
                        <input
                          type="range"
                          min="10"
                          max="300"
                          value={epochs}
                          onChange={(e) => setEpochs(e.target.value)}
                          className="w-full accent-emerald-600"
                        />
                      </div>
                      
                      {/* Batch Size */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <label className="font-medium">
                            Batch Size
                          </label>
                          <span className="font-semibold text-emerald-600">
                            {batchSize}
                          </span>
                        </div>
                        <input
                          type="range"
                          min="8"
                          max="128"
                          step="1"
                          value={batchSize}
                          onChange={(e) => setBatchSize(e.target.value)}
                          className="w-full accent-emerald-600"
                        />
                        {/* Note */}
                        <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-sm text-emerald-700 mt-3">
                          <b>Note:</b> The value of Epochs cycle and records that is to be generated affects the time taken to train the model.
                          So train the model as per to requirements.
                        </div>

                        {/* Button */}
                        <button
                          onClick={handleTrain}
                          disabled={isTraining}
                          className="w-[140px] bg-gray-300 text-black text-bold py-2 rounded-full font-semibold hover:bg-gray-400 disabled:opacity-60 duration-500 ease-in-out shadow-black shadow-sm hover:shadow-md mt-3"
                        >
                          {isTraining ? (
                            <span className="flex items-center justify-center gap-2">
                              <Loader2 className="w-5 h-5 animate-spin" />{" "}
                              Training...
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
              
              {/* Error Display */}
              {renderError()}
              
              {/* Training Results Display */}
              {renderTrainingResults()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}