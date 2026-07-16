import React from 'react';
import { useStore } from '../store/useStore';
import { Mic2, Activity, PlayCircle, Download, MoreVertical } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ModelDashboard() {
  const { voiceModels } = useStore();

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Voice Models</h1>
          <p className="text-gray-500 mt-1">Manage your trained AI voice clones.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {voiceModels.map(model => (
          <div key={model.id} className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 relative group">
            <div className="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity cursor-pointer">
              <MoreVertical className="w-5 h-5 text-gray-400 hover:text-black" />
            </div>
            
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 rounded-xl bg-gray-50 flex items-center justify-center border border-gray-100">
                <Mic2 className="w-6 h-6 text-gray-700" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 text-lg leading-tight mb-1">{model.name}</h3>
                <span className="text-xs font-medium text-gray-500 bg-gray-100 px-2 py-0.5 rounded-md">
                  {model.version}
                </span>
              </div>
            </div>

            <div className="space-y-4 mb-6">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">Status</span>
                {model.status === 'ready' ? (
                  <span className="text-green-600 font-medium flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span> Deployed
                  </span>
                ) : (
                  <span className="text-blue-600 font-medium flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span> Training
                  </span>
                )}
              </div>
              
              {model.status === 'ready' && (
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-500">Eval Score</span>
                  <span className="font-medium text-gray-900">{model.qualityScore} / 100</span>
                </div>
              )}
            </div>

            {model.status === 'ready' ? (
              <div className="grid grid-cols-2 gap-3 pt-4 border-t border-gray-100">
                <button className="flex items-center justify-center gap-2 py-2 rounded-lg bg-gray-50 hover:bg-gray-100 text-gray-900 font-medium text-sm transition-colors">
                  <PlayCircle className="w-4 h-4" /> Preview
                </button>
                <button className="flex items-center justify-center gap-2 py-2 rounded-lg bg-black text-white hover:bg-gray-900 font-medium text-sm transition-colors">
                  Use Model
                </button>
              </div>
            ) : (
              <div className="pt-4 border-t border-gray-100">
                <div className="flex justify-between text-xs mb-1.5">
                  <span className="text-gray-500 font-medium">Epoch 150/500</span>
                  <span className="text-blue-600 font-medium">30%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div className="bg-blue-500 h-1.5 rounded-full w-1/3 transition-all duration-1000"></div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
