import React, { useState } from "react";
import {
  Loader2,
  User,
  Database,
  Activity,
  BookOpen,
  Download,
  FileText,
  CheckCircle,
  AlertCircle,
} from "lucide-react";
import { 
  PieChart, 
  Pie, 
  BarChart, 
  Bar, 
  LineChart, 
  Line, 
  ScatterChart, 
  Scatter, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';

export default function Home() {
  const [recordCount, setRecordCount] = useState(1000);
  const [epochs, setEpochs] = useState(100);
  const [batchSize, setBatchSize] = useState(32);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [activeTab, setActiveTab] = useState("generate");
  const [generatedData, setGeneratedData] = useState(null);
  const [trainingResults, setTrainingResults] = useState(null);
  const [error, setError] = useState(null);
  const [diabetesRatio, setDiabetesRatio] = useState(0.5);
  const [hypertensionRatio, setHypertensionRatio] = useState(0.7);

  // Render data visualizations
const renderDataVisualizations = () => {
  if (!generatedData?.data?.preview?.sample_patients) return null;

  const data = generatedData.data.preview.sample_patients.map(p => p.tabular_data);
  const totalGenerated = generatedData.data.num_generated;
  const patients = generatedData.data.preview.sample_patients;

  if (!Array.isArray(data) || data.length === 0) return null;

  return (
    <div className="mt-8 space-y-8">
      <h3 className="text-2xl font-bold">Generated Patient Data</h3>
      
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
        <b>Note:</b> Showing {data.length} sample records out of {totalGenerated} total generated records. Full dataset saved to CSV file.
      </div>
      
      <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6">
        <h4 className="text-lg font-semibold mb-4">Tabular Patient Records</h4>
        <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
          <table className="min-w-full table-auto border-collapse">
            <thead className="sticky top-0 bg-gray-100 z-10">
              <tr>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Patient ID</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Age</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">BMI</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Avg RBS</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">HbA1c</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">BP Reading</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Resp. Rate</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Heart Rate</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">SpO2</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Diabetes</th>
                <th className="border border-gray-300 px-4 py-2 text-left text-sm font-semibold">Hypertension</th>
              </tr>
            </thead>
            <tbody>
              {data.map((record, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.patient_id}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.age}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.bmi?.toFixed(1)}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.average_rbs?.toFixed(1)}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.hba1c?.toFixed(2)}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.hypertension}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.respiratory_rate}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.heart_rate}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm">{record.spo2?.toFixed(1)}</td>
                  <td className="border border-gray-300 px-4 py-2 text-sm text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${record.diabetes === 1 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                      {record.diabetes === 1 ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="border border-gray-300 px-4 py-2 text-sm text-center">
                    <span className={`px-2 py-1 rounded-full text-xs font-semibold ${record.bp_status === 1 ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}`}>
                      {record.bp_status === 1 ? 'Yes' : 'No'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-gray-500 mt-4">
          📁 Full dataset saved to: <code className="bg-gray-100 px-2 py-1 rounded text-xs">{generatedData.data.tabular_file}</code>
        </p>
      </div>

      <div className="bg-white border border-emerald-200 rounded-xl shadow-md p-6">
        <h4 className="text-xl font-bold mb-6">Time Series Data - RBS Values Over Time (All Patients)</h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {patients.map((patient, idx) => {
            if (!patient.timeseries_sample || patient.timeseries_sample.length === 0) return null;
            
            const chartData = patient.timeseries_sample.map(point => ({
              time: point.timestamp.split('T')[1].slice(0, 5),
              rbs: point.rbs_value
            }));

            const isDiabetic = patient.tabular_data.diabetes === 1;

            return (
              <div key={idx} className="border border-gray-200 rounded-lg p-3 bg-gray-50">
                <div className="mb-2">
                  <h5 className="text-sm font-semibold">{patient.patient_id}</h5>
                  <p className="text-xs text-gray-600">
                    Age: {patient.tabular_data.age} | 
                    <span className={isDiabetic ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'}>
                      {isDiabetic ? ' Diabetic' : ' Non-Diabetic'}
                    </span>
                  </p>
                </div>
                <ResponsiveContainer width="100%" height={150}>
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis 
                      dataKey="time" 
                      tick={{ fontSize: 10 }}
                      interval={2}
                    />
                    <YAxis 
                      tick={{ fontSize: 10 }}
                      domain={[0, 'auto']}
                    />
                    <Tooltip 
                      contentStyle={{ fontSize: 12 }}
                      labelFormatter={(value) => `Time: ${value}`}
                      formatter={(value) => [`${value.toFixed(1)} mg/dL`, 'RBS']}
                    />
                    <Line 
                      type="monotone" 
                      dataKey="rbs" 
                      stroke={isDiabetic ? '#ef4444' : '#10b981'}
                      strokeWidth={2}
                      dot={false}
                      activeDot={{ r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};


  // API call for generating healthcare data
  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);
    setGeneratedData(null);

    try {
      const response = await fetch(
        "http://localhost:5000/api/healthcare-gan/generate",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            num_samples: parseInt(recordCount),
            diabetes_ratio: parseFloat(diabetesRatio) || 0.5, // FIXED: Use actual API params
            hypertension_ratio: parseFloat(hypertensionRatio) || 0.7, // FIXED: Use actual API params
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
       console.log("API Response:", data);
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
      const response = await fetch(
        "http://localhost:5000/api/healthcare-gan/train",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            time_series_path: "cleaned_merged_data.csv",
            tabular_path: "cleaned_tabular_data.csv",
            epochs: parseInt(epochs),
          }),
        }
      );

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
    const dataUri =
      "data:application/json;charset=utf-8," + encodeURIComponent(dataStr);

    const exportFileDefaultName = `healthcare_data_${
      new Date().toISOString().split("T")[0]
    }.json`;

    const linkElement = document.createElement("a");
    linkElement.setAttribute("href", dataUri);
    linkElement.setAttribute("download", exportFileDefaultName);
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
            <div className="text-2xl font-bold text-emerald-600">
              {generatedData.num_samples || recordCount}
            </div>
            <div className="text-sm text-gray-600">Records Generated</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {generatedData.model_type || "patient_data"}
            </div>
            <div className="text-sm text-gray-600">Model Type</div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {generatedData.generation_time || "N/A"}s
            </div>
            <div className="text-sm text-gray-600">Generation Time</div>
          </div>
        </div>

        {/* Sample data preview */}
        {generatedData.data && generatedData.data.length > 0 && (
          <div>
            <h4 className="font-medium mb-3">
              Sample Generated Records (First 5)
            </h4>
            <div className="overflow-x-auto">
              <table className="min-w-full table-auto border-collapse">
                <thead>
                  <tr className="bg-gray-50">
                    {Object.keys(generatedData.data[0]).map((key) => (
                      <th
                        key={key}
                        className="border px-4 py-2 text-left text-sm font-medium text-gray-700"
                      >
                        {key.replace("_", " ").toUpperCase()}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {generatedData.data.slice(0, 5).map((record, index) => (
                    <tr key={index} className="hover:bg-gray-50">
                      {Object.values(record).map((value, idx) => (
                        <td
                          key={idx}
                          className="border px-4 py-2 text-sm text-gray-600"
                        >
                          {typeof value === "number" ? value.toFixed(2) : value}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {generatedData.data.length > 5 && (
              <p className="text-sm text-gray-500 mt-2">
                Showing 5 of {generatedData.data.length} records. Download full
                dataset using the button above.
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
            <div className="text-2xl font-bold text-green-600">
              {trainingResults.final_loss || "N/A"}
            </div>
            <div className="text-sm text-gray-600">Final Loss</div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {trainingResults.training_time || "N/A"}s
            </div>
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
                      {/* Diabetes Ratio */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <label className="font-medium">Diabetes Ratio</label>
                          <span className="font-semibold text-emerald-600">
                            {diabetesRatio.toFixed(1)}
                          </span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={diabetesRatio}
                          onChange={(e) =>
                            setDiabetesRatio(Number(e.target.value))
                          }
                          className="w-full accent-emerald-600"
                        />
                      </div>

                      {/* Hypertension Ratio */}
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <label className="font-medium">
                            Hypertension Ratio
                          </label>
                          <span className="font-semibold text-emerald-600">
                            {hypertensionRatio.toFixed(1)}
                          </span>
                        </div>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.1"
                          value={hypertensionRatio}
                          onChange={(e) =>
                            setHypertensionRatio(Number(e.target.value))
                          }
                          className="w-full accent-emerald-600"
                        />
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
                          max="1000"
                          step="10"
                          value={recordCount}
                          onChange={(e) => setRecordCount(Number(e.target.value))}
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

              {/* Result table */ }
              {renderDataVisualizations()}

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
                          <label className="font-medium">
                            Number of Epochs
                          </label>
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
                          <label className="font-medium">Batch Size</label>
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
                          <b>Note:</b> The value of Epochs cycle and records
                          that is to be generated affects the time taken to
                          train the model. So train the model as per to
                          requirements.
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
