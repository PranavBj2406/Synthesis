import React from "react";
import { Link } from "react-router-dom";
import { FaArrowRight } from "react-icons/fa";
import { CircleUserRound } from "lucide-react";
import profile from "../assets/profile icon.svg";

export default function Header2() {
  return (
    <header className="bg-gradient-to-br from-emerald-100 to-white border border-none h-28 flex items-center z-10 relative w-full ">
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

        <nav className="flex justify-end p-4">
          <div className="relative group">
           <Link to="/profile" className="">
                <img
                  src={profile}
                  alt=""
                  className="w-[50px]  rounded-full transition-all duration-300 ease-in-out group-hover:shadow-md group-hover:shadow-emerald-500 group-hover:ring-4 group-hover:ring-emerald-400 group-hover:scale-110"
                ></img>
              </Link>
          </div>
        </nav>
      </div>
    </header>
  );
}
