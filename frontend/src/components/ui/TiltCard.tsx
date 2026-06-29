import React, { useRef } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';

interface TiltCardProps {
  children: React.ReactNode;
  className?: string;
  rotateAmplitude?: number;
  glowColor?: string;
}

export default function TiltCard({
  children,
  className = '',
  rotateAmplitude = 12,
  glowColor = 'rgba(14, 165, 233, 0.15)' // Low-intensity cyan/blue glow
}: TiltCardProps) {
  const ref = useRef<HTMLDivElement>(null);

  // Track relative coordinates (0 to 1) inside container
  const mouseX = useMotionValue(0.5);
  const mouseY = useMotionValue(0.5);

  // Springs for smooth 3D tilting
  const rotateX = useSpring(
    useTransform(mouseY, [0, 1], [rotateAmplitude, -rotateAmplitude]),
    { damping: 25, stiffness: 180 }
  );
  const rotateY = useSpring(
    useTransform(mouseX, [0, 1], [-rotateAmplitude, rotateAmplitude]),
    { damping: 25, stiffness: 180 }
  );

  // Track coordinates (px) for glow light follow
  const glowX = useMotionValue(0);
  const glowY = useMotionValue(0);
  const glowOpacity = useSpring(useMotionValue(0), { damping: 20, stiffness: 120 });

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;

    const rect = ref.current.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;

    const xPct = (e.clientX - rect.left) / width;
    const yPct = (e.clientY - rect.top) / height;

    mouseX.set(xPct);
    mouseY.set(yPct);

    glowX.set(e.clientX - rect.left);
    glowY.set(e.clientY - rect.top);
    glowOpacity.set(1);
  };

  const handleMouseLeave = () => {
    rotateX.set(0);
    rotateY.set(0);
    mouseX.set(0.5);
    mouseY.set(0.5);
    glowOpacity.set(0);
  };

  return (
    <div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ perspective: 1000 }}
      className={`relative rounded-2xl ${className}`}
    >
      <motion.div
        className="w-full h-full rounded-[inherit] border border-slate-800/60 bg-slate-900/10 backdrop-blur-md p-8 relative overflow-hidden transition-colors duration-300 hover:bg-slate-900/30 hover:border-blue-500/20 shadow-xl"
        style={{
          rotateX,
          rotateY,
          transformStyle: 'preserve-3d'
        }}
      >
        {/* Glow backdrop layer - moves with cursor */}
        <motion.div
          className="pointer-events-none absolute -inset-px rounded-[inherit]"
          style={{
            opacity: glowOpacity,
            background: useTransform(
              [glowX, glowY],
              ([x, y]) => `radial-gradient(200px circle at ${x}px ${y}px, ${glowColor}, transparent 80%)`
            )
          }}
        />

        {/* 3D Depth Card Content container */}
        <div 
          className="relative z-10 w-full h-full flex flex-col items-start gap-4 select-none"
          style={{ transform: 'translateZ(30px)' }}
        >
          {children}
        </div>
      </motion.div>
    </div>
  );
}
