import React from "react";
import Image1 from "../assets/Image1.png";
import Image2 from "../assets/Image2.png";
import Image3 from "../assets/Image3.png";
import Icon1 from "../assets/icons/icon1.png";
import Icon2 from "../assets/icons/icon2.png";
import Icon3 from "../assets/icons/icon3.png";
import Icon4 from "../assets/icons/icon4.png";
import Icon5 from "../assets/icons/icon5.png";
import Icon6 from "../assets/icons/icon6.png";
import Gif1 from "../assets/gif1.gif";
import {Link} from "react-router-dom";

export default function Landpg() {
  return (
    <div className="bg-gradient-to-b from-amber-100 via-white to-amber-200 min-h-screen mx-auto w-full px-12 ">
      <h1 className="pt-10 text-5xl font-bold font-manrope bg-gradient-to-r from-pink-500 via-red-400 to-amber-500 bg-clip-text text-transparent w-[550px]">
        Multimodal Synthetic{" "}
      </h1>
      <h1 className="font-bold text-4xl mt-2 font-manrope ">
        {" "}
        Healthcare Data Generator{" "}
      </h1>
      <h1 className="font-manrope text-xl font-bold mt-11">
        Accelerate Healthcare Innovation with Safe, Synthetic Data
      </h1>
      <div className="flex flex-row mt-4">
        <p className="w-[41%] text-justify ">
          <spam className="font-semibold text-lg">S</spam>eamlessly generate
          high-fidelity synthetic healthcare datasets spanning structured
          records like EHRs, complex medical imaging, and continuous sensor data
          all crafted to reflect real-world clinical diversity and intricacies.
          <br />
          <br />
          Designed to eliminate patient privacy risks, our platform empowers
          researchers, developers, and healthcare innovators to train AI models,
          validate products, and conduct clinical research in a fully compliant,
          privacy-first environment.<br></br>
          <br />
          In todays data-driven healthcare ecosystem, accessing large volumes of
          diverse, high-quality medical data is crucial — yet real patient data
          is often limited, restricted, or sensitive.
          <br />
          <br /> This is where our Multimodal Synthetic Healthcare Data
          Generator becomes a game-changer.<br></br>
        </p>
        <div>
          <img
            src={Image1}
            className="ml-10 w-[300px] h-[300px] rounded-2xl absolute top-40 right-20 rotate-[-30deg] hover:scale-95 duration-300 transform ease-in-out shadow-2xl shadow-black border-4 border-white "
          ></img>
          <img
            src={Image2}
            className="ml-10 w-[300px] h-[300px] rounded-2xl absolute bottom-[50px] right-40 rotate-[-10deg] hover:scale-95 duration-300 transform ease-in-out border-4 border-white  shadow-2xl shadow-amber-400  "
          ></img>
          <img
            src={Image3}
            className="ml-10 w-[300px] h-[300px] rounded-2xl absolute bottom-[200px] right-90 rotate-[45deg] hover:scale-95 duration-300 transform ease-in-out border-4 border-white  shadow-lg shadow-blue-500 "
          ></img>
        </div>
      </div>

      <div className=" w-full border mt-25" />

      <div className="mt-13">
        <spam className="font-manrope text-2xl  font-semibold">
          {" "}
          Why Use Synthesis
        </spam>
      </div>

      {/* block for containers*/}
      <div className="flex flex-col">
        <div className="flex flex-row mt-20  justify-center gap-28">
          {/* one contaiber */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img src={Icon1} alt="" className="scale-80 ml-1"></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-3 ">
                    Privacy & <br></br>Security
                  </spam>
                </div>

                <p className="font-manrope font-semibold text-sm ml-3 mt-3 ">
                  Ensures data safety using differential privacy with no real
                  identity exposure, enabling secure synthetic healthcare
                  generation..{" "}
                </p>
              </div>
            </div>
          </div>
          {/* second container */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img src={Icon2} alt="" className="scale-90 ml-1"></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-3 ">
                    Multimodal Data Generation
                  </spam>
                </div>
                <p className="font-manrope font-semibold text-sm ml-3 mt-3 ">
                  Create synthetic EHRs,Blood pressure, and wearable sensor data
                  to simulate real-world clinical scenarios.{" "}
                </p>
              </div>
            </div>
          </div>
          {/* third  container */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img src={Icon3} alt="" className="scale-85 ml-2 "></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-4  ">
                    Custom Scenario Simulation
                  </spam>
                </div>
                <p className="font-manrope font-semibold text-sm ml-3 mt-6 ">
                  Allow users to generate data based on: Specific diseases or
                  clinical conditions such as diabetes. Demographic
                  distributions like age,gender.
                </p>
              </div>
            </div>
          </div>
        </div>
        <div className="flex flex-row mt-20  justify-center gap-28">
          {/* one contaiber */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img
                    src={Icon4}
                    alt=""
                    className="scale-75 w-[100px] ml-2 mt-1 "
                  ></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-4 ml-0 ">
                    Model-Ready Integration
                  </spam>
                </div>
                <p className="font-manrope font-semibold text-sm ml-3 mt-1 ">
                  Built for seamless ML model training, validation, and export
                  with ready-to-use synthetic data for TensorFlow, PyTorch .
                </p>
              </div>
            </div>
          </div>
          {/* second container */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img src={Icon5} alt="" className="scale-90 ml-2 "></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-4  ">
                    Interactive Data Tuning Interface
                  </spam>
                </div>
                <p className="font-manrope font-semibold text-sm ml-3 mt-1 ">
                  Easily control dataset records and epocs value with a visual,
                  user-friendly interface for customizing synthetic data before
                  export.
                </p>
              </div>
            </div>
          </div>
          {/* third  container */}
          <div className="group">
            <div className="border-2 h-[225px] w-[345px] rounded-2xl bg-amber-500 shadow-lg shadow-gray-500 group-hover:shadow-xl group-hover:shadow-gray-500 transition-all duration-300">
              <div className="border-2 h-[220px] w-[340px] rounded-2xl relative bottom-4 right-5 bg-white group-hover:bottom-2 group-hover:right-2 transition-all duration-300">
                <div className="flex flex-row">
                  <img src={Icon6} alt="" className="scale-85 ml-2 "></img>
                  <spam className="flex items-center text-2xl font-bold font-manrope mt-4 ml-1 ">
                    Validation & Assurance Suite
                  </spam>
                </div>
                <p className="font-manrope font-semibold text-sm ml-3 mt-4 ">
                  Evaluate data fidelity, compare with real-world baselines, and
                  detect biases or anomalies in synthetic datasets
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
      {/* end of container */}
      <div className="flex flex-col justify-center items-center mt-20">
        <p className=" ml-5 h-[100px] font-semibold font-manrope text-4xl">
          {" "}
          Then why wait use Synthesis{" "}
        </p>
        <img src={Gif1} alt="" className="  "></img>


        {/* generate button */}
        <Link to="/Home">
          <div className="group mt-10 ml-6">
            <div className="border-2 border-black h-[50px] w-[140px] rounded-3xl bg-black">
              <div className="border-2 border-black h-[50px] w-[140px] bg-gradient-to-tl from-amber-500 via-pink-400 to-red-400 rounded-3xl flex items-center justify-center relative bottom-2 right-2 group-hover:bottom-1 group-hover:right-1 transition-all duration-300 ease-in-out">
                <span className="text-white font-manrope font-semibold text-lg group-hover:text-black transition duration-300">
                  Generate
                </span>
              </div>
            </div>
          </div>
        </Link>

    

      </div>
    </div>
  );
}
