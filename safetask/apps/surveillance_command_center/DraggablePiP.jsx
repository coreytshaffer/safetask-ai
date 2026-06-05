import React, { useState, useRef, useEffect } from 'react';
import { X, Move } from 'lucide-react';

const DraggablePiP = ({ title, cameraName, timestamp, onClose }) => {
  const [position, setPosition] = useState({ x: 100, y: 100 });
  const [isDragging, setIsDragging] = useState(false);
  const dragOffset = useRef({ x: 0, y: 0 });

  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!isDragging) return;
      setPosition({
        x: e.clientX - dragOffset.current.x,
        y: e.clientY - dragOffset.current.y
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  const handleMouseDown = (e) => {
    setIsDragging(true);
    dragOffset.current = {
      x: e.clientX - position.x,
      y: e.clientY - position.y
    };
  };

  return (
    <div
      className={`absolute z-50 bg-[#1e1e1e]/80 backdrop-blur-md border border-gray-700/50 rounded-xl shadow-2xl flex flex-col overflow-hidden w-80 transition-shadow ${isDragging ? 'shadow-accent/20 cursor-grabbing' : 'cursor-grab'}`}
      style={{
        left: `${position.x}px`,
        top: `${position.y}px`
      }}
    >
      <div 
        className="flex justify-between items-center bg-gray-900/80 p-2 border-b border-gray-700/50 select-none"
        onMouseDown={handleMouseDown}
      >
        <div className="flex items-center gap-2 text-gray-300 font-semibold text-sm">
          <Move size={14} className="text-gray-500" />
          {title}
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
          <X size={16} />
        </button>
      </div>
      <div className="relative bg-black aspect-video flex items-center justify-center">
        {/* Placeholder for actual video feed */}
        <div className="text-gray-700 font-mono text-xs text-center">
          <div>FEED OFFLINE</div>
          <div className="mt-1 opacity-50">{cameraName}</div>
        </div>
        <div className="absolute bottom-2 right-2 text-[10px] font-mono text-red-500 bg-black/50 px-1 rounded">
          {timestamp}
        </div>
        <div className="absolute top-2 left-2 text-[10px] font-mono text-white bg-red-600 px-1 rounded font-bold animate-pulse">
          REC
        </div>
      </div>
    </div>
  );
};

export default DraggablePiP;