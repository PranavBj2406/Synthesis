import React from "react";
import { motion } from "framer-motion";

const generateDots = (count) => {
  return Array.from({ length: count }, (_, i) => ({
    id: i,
    top: Math.random() * 100 + "vh",
    left: Math.random() * 100 + "vw",
  }));
};

export default function BackgroundDots({ count = 20 }) {
  const dots = generateDots(count);

  return (
    <div className="absolute top-0 left-0 w-full h-full overflow-hidden z-0">
      {dots.map((dot) => (
        <motion.div
          key={dot.id}
          className="w-3 h-5 rounded-full bg-amber-300 absolute blur-md"
          initial={{ top: dot.top, left: dot.left }}
          animate={{ 
            x: Math.random() * 300 - 150, 
            y: Math.random() * 300 - 150 
          }}
          transition={{ duration: 30, repeat: Infinity, repeatType: "mirror" }}
          style={{ top: dot.top, left: dot.left }}
        />
      ))}
    </div>
  );
}
