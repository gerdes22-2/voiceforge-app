import React, { useState } from 'react';
import { Sliders } from 'lucide-react';

export default function MasteringEngine() {
  const [eq, setEq] = useState(0);
  const [compression, setCompression] = useState(50);
  const [loudness, setLoudness] = useState(-14);

  return (
    <div className="bg-white p-6 rounded-xl border border-gray-100 shadow-sm mt-8">
      <div className="flex items-center gap-2 mb-6">
        <Sliders className="w-5 h-5 text-gray-900" />
        <h2 className="text-lg font-semibold text-gray-900">Mastering Engine</h2>
      </div>
      
      <div className="space-y-6">
        <div>
          <label className="text-sm font-medium text-gray-700">EQ (Low Shelf)</label>
          <input type="range" className="w-full accent-black" min="-12" max="12" value={eq} onChange={e => setEq(Number(e.target.value))} />
        </div>
        <div>
          <label className="text-sm font-medium text-gray-700">Compression</label>
          <input type="range" className="w-full accent-black" min="0" max="100" value={compression} onChange={e => setCompression(Number(e.target.value))} />
        </div>
        <div>
          <label className="text-sm font-medium text-gray-700">Loudness (LUFS)</label>
          <input type="range" className="w-full accent-black" min="-24" max="-6" value={loudness} onChange={e => setLoudness(Number(e.target.value))} />
        </div>
      </div>
    </div>
  );
}
