import React from "react";
import { Link } from "react-router-dom";
import { FaArrowRight } from "react-icons/fa";

export default function Header() {
  return (
    <header className="bg-gradient-to-b from-amber-200 to-amber-100 border border-none h-24 flex items-center z-10 relative w-full ">
      <div className="flex justify-between items-center max-w-[1450px] mx-auto w-full px-4">
        <div className="flex-shrink-0">
          <h1>
            <Link to="/">
              <span className=" font-manrope text-4xl font-bold flex items-start bg-gradient-to-br from-pink-500  to-yellow-400 bg-clip-text text-transparent hover:bg-gradient-to-bl hover:from-yellow-400 hover:to-pink-500 duration-700">
                SYNTHESIS
              </span>
            </Link>
          </h1>
        </div>
        
        <nav className="flex-grow flex justify-end">
          <ul className="flex gap-8 items-center">
            <Link to="/signUp">
              <li className="relative text-base font-semibold text-black hover:text-gray-500 duration-300 hover:after:content-['•'] hover:after:absolute hover:after:bottom-[-10px] hover:after:left-1/2 hover:after:-translate-x-1/2 hover:after:text-lg hover:after:leading-none">SignUp</li>
            </Link>
            {/* <Link to="/about">
              <li className="relative text-base font-medium text-black hover:text-gray-500 duration-300 hover:after:content-['•'] hover:after:absolute hover:after:bottom-[-10px] hover:after:left-1/2 hover:after:-translate-x-1/2 hover:after:text-lg hover:after:leading-none">About Us</li>
            </Link> */}
            <Link to="/signin">
              <div className="flex items-center">
                <li className="flex font-semibold text-md border h-10 w-40 items-center justify-center rounded-full border-black shadow-md shadow-gray-700 gap-x-2 hover:scale-110 duration-300 transform ease-out hover:shadow-lg hover:bg-gradient-to-r hover:from-amber-300 hover:to-pink-500 bg-gradient-to-r from-pink-500 to-amber-400 hover:text-white">
                  Get Started
                  <FaArrowRight className="text-sm mt-0.5" />
                </li>
              </div>
            </Link>
          </ul>
        </nav>
      </div>
    </header>
  );
}