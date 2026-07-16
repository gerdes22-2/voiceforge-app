import React, { useState } from 'react';
import { UploadCloud, CheckCircle2, Play, Music, Mic, FileAudio } from 'lucide-react';
import { cn } from '../lib/utils';

const categories = ['Singing', 'Rap', 'Speech', 'Harmony', 'Falsetto', 'Sustained notes'];

export default function DatasetStudio() {
  const [samples] = useState([
    { id: 1, name: 'Lead_Vocal_Take1.wav', category: 'Singing', duration: '3:12', status: 'ready' },
    { id: 2, name: 'Adlibs_Rap.wav', category: 'Rap', duration: '1:05', status: 'ready' },
    { id: 3, name: 'High_Notes_Scale.wav', category: 'Falsetto', duration: '0:45', status: 'processing' },
  ]);

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Dataset Studio</h1>
          <p className="text-gray-500 mt-1">Upload and organize your voice samples for training.</p>
        </div>
        <button className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-900 transition-colors flex items-center gap-2">
          <UploadCloud className="w-4 h-4" />
          Upload Samples
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden mb-8">
            <div className="p-4 border-b border-gray-100 bg-gray-50 flex items-center justify-between">
              <h3 className="font-semibold text-gray-900">Uploaded Samples</h3>
              <span className="text-xs font-medium bg-gray-200 text-gray-700 px-2.5 py-1 rounded-full">{samples.length} files</span>
            </div>
            <div>
              {samples.map((sample, i) => (
                <div key={sample.id} className={cn("p-4 flex items-center justify-between hover:bg-gray-50 transition-colors group", i !== samples.length - 1 && "border-b border-gray-100")}>
                  <div className="flex items-center gap-4">
                    <button className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center text-gray-500 group-hover:bg-black group-hover:text-white transition-colors">
                      <Play className="w-4 h-4 ml-1" />
                    </button>
                    <div>
                      <h4 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                        {sample.name}
                        {sample.status === 'ready' && <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />}
                      </h4>
                      <p className="text-xs text-gray-500 mt-0.5">{sample.duration}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <select 
                      className="text-xs bg-gray-50 border border-gray-200 rounded-md px-2 py-1.5 outline-none focus:ring-1 focus:ring-black"
                      defaultValue={sample.category}
                    >
                      {categories.map(c => <option key={c} value={c}>{c}</option>)}
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div>
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 mb-6">
            <h3 className="font-semibold text-gray-900 mb-4">Dataset Quality</h3>
            
            <div className="flex items-end gap-2 mb-6">
              <span className="text-4xl font-bold tracking-tight text-green-600">92</span>
              <span className="text-gray-500 font-medium mb-1">/ 100</span>
            </div>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-gray-600 font-medium">Clarity & SNR</span>
                  <span className="text-gray-900">Excellent</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full w-11/12"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-gray-600 font-medium">Pitch Coverage</span>
                  <span className="text-gray-900">Good</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div className="bg-green-500 h-1.5 rounded-full w-4/5"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-gray-600 font-medium">Duration (min 15m)</span>
                  <span className="text-gray-900">22m 14s</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div className="bg-black h-1.5 rounded-full w-full"></div>
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-gray-100">
              <button className="w-full bg-black text-white font-medium py-3 rounded-xl hover:bg-gray-900 transition-colors flex items-center justify-center gap-2">
                <Mic className="w-4 h-4" />
                Start Training
              </button>
              <p className="text-xs text-center text-gray-500 mt-3">Estimated training time: 2h 15m</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
