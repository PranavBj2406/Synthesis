import React from "react";
import { Player } from "@lottiefiles/react-lottie-player";
import { Link } from "react-router-dom";
import { FaGoogle } from "react-icons/fa";

export default function SignUp() {
  return (
    <div className=" flex flex-row min-h-screen  ">
      {/* left container */}
      <div className="flex items-center justify-center  w-1/2  z-5 bg-gradient-to-b from-amber-100 to-amber-200">
        <div className=" w-3/4 h-auto border-black rounded-3xl shadow-lg shadow-gray-600  bg-black  ">
          <div className="w-full h-full  relative bg-amber-50 rounded-2xl bottom-5  right-6 border-3 border-black z-2 px-5 py-5 ">
            <p className="text-4xl font-semibold font-manrope">
              Welcome to{" "}
              <spam className=" bg-gradient-to-r from-pink-500 via-red-400 to-amber-500 bg-clip-text text-transparent">
                Synthesis
              </spam>
            </p>
            <h1 className="text-2xl font-manrope font-semibold text-gray-500 mt-3">
              Sign up
            </h1>

            <h1 className="mt-5 text-lg font-manrope font-semibold ">
              Username
            </h1>
            <div className="h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5">
              <input
                className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                placeholder="enter your username."
                type="text"
              ></input>
            </div>

            <h1 className="mt-5 text-lg font-manrope font-semibold ">Email</h1>
            <div className="h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5">
              <input
                className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                placeholder="enter your email address."
                type="text"
              ></input>
            </div>

            <h1 className="mt-5 text-lg font-manrope font-semibold ">
              Password
            </h1>
            <div className="h-12 w-[323px] border-2 bg-gradient-to-r from-orange-500 via-red-500 to-pink-700 rounded-xl ml-2 mt-5">
              <input
                className="flex justify-start items-center border-2 mt-2 font-manrope text-sm font-semibold bg-white h-11 px-3 rounded-md w-[320px] focus:outline-none relative right-2 bottom-4 "
                placeholder="enter password"
                type="password"
              ></input>
            </div>

            <div className="flex flex-row justify-start gap-6 mt-10">
              <div className="w-1/3 border-2 rounded-md ml-2 bg-black ">
                <button className="w-full h-[50px] border-2 border-black rounded-md font-manrope font-bold  text-white bg-blue-500 relative right-2 bottom-2 hover:relative hover:bottom-1 hover:right-1 duration-300 ease-in-out hover:bg-blue-400">
                  Sign Up
                </button>
              </div>

              <spam className="flex justify-center items-center mt-1 p-1 font-manrope font-semibold ">
                or
              </spam>

              <div className="w-auto border-2 rounded-md ml-2 bg-black ">
                <button className="w-auto p-3 h-[50px] border-2 border-black rounded-md font-manrope font-bold  text-white bg-purple-700 relative right-2 bottom-2 flex flex-row justify-center items-center gap-3">
                  <FaGoogle className="scale-110" /> Sign Up with google
                </button>
              </div>
            </div>

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
      <div className="flex justify-center items-center w-1/2 z-0 bg-gradient-to-b from-amber-100 to-amber-200 ">
        <div className="flex justify-center items-center border-none rounded-full relative bottom-5  ">
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
