import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2 } from 'lucide-react';
import { cn } from '../lib/utils';

interface AudioPlayerProps {
  title: string;
  subtitle: string;
  src?: string;
}

export default function AudioPlayer({ title, subtitle, src }: AudioPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);

  // Mock progress simulation
  React.useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setProgress(p => (p >= 100 ? 0 : p + 0.5));
      }, 100);
    }
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="bg-black text-white p-6 rounded-2xl shadow-xl flex flex-col md:flex-row items-center gap-6">
      <div className="flex-1 flex items-center gap-6 w-full">
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          className="w-14 h-14 rounded-full bg-white text-black flex items-center justify-center hover:scale-105 transition-transform shrink-0"
        >
          {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6 ml-1" />}
        </button>
        <div className="flex-1 overflow-hidden">
          <h3 className="font-bold text-lg truncate">{title}</h3>
          <p className="text-gray-400 text-sm truncate">{subtitle}</p>
        </div>
      </div>
      
      <div className="flex-1 w-full flex items-center gap-4">
        <span className="text-xs text-gray-400 font-medium tabular-nums">0:{(progress * 1.8).toFixed(0).padStart(2, '0')}</span>
        
        {/* Mock Waveform */}
        <div className="flex-1 h-8 flex items-center gap-0.5 relative cursor-pointer overflow-hidden opacity-80 hover:opacity-100 transition-opacity">
          {Array.from({ length: 50 }).map((_, i) => {
            const h = Math.max(10, Math.sin(i * 0.5) * 40 + 50);
            const isPast = (i / 50) * 100 <= progress;
            return (
              <div 
                key={i} 
                className={cn(
                  "flex-1 rounded-full transition-colors", 
                  isPast ? "bg-white" : "bg-gray-700"
                )}
                style={{ height: `${h}%` }}
              />
            );
          })}
        </div>
        
        <span className="text-xs text-gray-400 font-medium tabular-nums">3:00</span>
      </div>
      
      <div className="w-full md:w-auto flex items-center gap-3 shrink-0">
        <Volume2 className="w-5 h-5 text-gray-400" />
        <div className="w-24 h-1.5 bg-gray-700 rounded-full cursor-pointer">
          <div className="w-3/4 h-full bg-white rounded-full"></div>
        </div>
      </div>
    </div>
  );
}
