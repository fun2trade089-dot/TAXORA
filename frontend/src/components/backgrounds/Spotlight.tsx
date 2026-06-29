import React, { useRef, useState, useCallback } from 'react';

interface SpotlightProps {
  children: React.ReactNode;
  className?: string;
  color?: string;
  radius?: number;
}

export default function Spotlight({ 
  children, 
  className = '', 
  color = 'rgba(14, 165, 233, 0.07)', // Soft sky-blue/cyan with very low opacity
  radius = 600 
}: SpotlightProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [opacity, setOpacity] = useState(0);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    
    // Calculate cursor position relative to the container boundaries
    setPosition({ 
      x: e.clientX - rect.left, 
      y: e.clientY - rect.top 
    });
  }, []);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden ${className}`}
    >
      {/* Spotlight highlight layer - pointer-events-none ensures it doesn't block interactions */}
      <div
        className="pointer-events-none absolute inset-0 transition-opacity duration-700 ease-out z-0"
        style={{
          opacity,
          background: `radial-gradient(${radius}px circle at ${position.x}px ${position.y}px, ${color}, transparent 80%)`,
        }}
      />
      
      {/* Content wrapper - forced above the spotlight layer */}
      <div className="relative z-10 w-full h-full">
        {children}
      </div>
    </div>
  );
}
