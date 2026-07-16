import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { UploadCloud, Music, Mic, ArrowRight, Plus } from 'lucide-react';
import { cn } from '../lib/utils';

export default function ProjectCreation() {
  const [name, setName] = useState('');
  const [step, setStep] = useState(1);
  const { addProject } = useStore();
  const navigate = useNavigate();

  const handleCreate = () => {
    addProject({
      id: Date.now().toString(),
      name: name || 'Untitled Project',
      status: 'active',
      createdAt: new Date().toISOString().split('T')[0]
    });
    navigate('/conversion');
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-gray-900">Create New Project</h1>
        <p className="text-gray-500 mt-1">Start a new voice conversion session.</p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-8">
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Project Name</label>
              <input 
                type="text" 
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-black focus:border-black outline-none transition-all text-lg"
                placeholder="e.g. Summer Hit Remix"
                value={name}
                onChange={e => setName(e.target.value)}
              />
            </div>
            
            <div className="pt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">Source Audio</label>
              <div className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer group">
                <div className="w-12 h-12 rounded-full bg-white shadow-sm flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <UploadCloud className="w-6 h-6 text-gray-600" />
                </div>
                <h4 className="font-medium text-gray-900 mb-1">Upload Source Song</h4>
                <p className="text-sm text-gray-500 text-center max-w-sm">
                  Upload a complete song (Suno output, MP3, WAV). We will automatically separate the stems.
                </p>
              </div>
            </div>

            <div className="flex justify-end pt-6 border-t border-gray-100">
              <button 
                onClick={() => setStep(2)}
                className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-900 transition-colors flex items-center gap-2"
              >
                Next Step
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Choose Voice Model</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="border border-black rounded-xl p-4 bg-gray-50 cursor-pointer relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-16 h-16 bg-black text-white rounded-bl-full flex items-center justify-center transform translate-x-4 -translate-y-4">
                    <Mic className="w-4 h-4 ml-2 mt-2" />
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-1">Studio Lead</h4>
                  <p className="text-sm text-gray-500">Your custom trained model</p>
                  <div className="mt-4 flex items-center gap-2">
                    <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-md font-medium">Ready</span>
                    <span className="text-xs text-gray-400">Score: 94.5</span>
                  </div>
                </div>
                <div className="border border-gray-200 rounded-xl p-4 hover:border-gray-300 cursor-pointer transition-colors flex flex-col items-center justify-center text-center">
                  <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center mb-2">
                    <Plus className="w-5 h-5 text-gray-600" />
                  </div>
                  <h4 className="font-medium text-gray-900">Train New Model</h4>
                  <p className="text-xs text-gray-500 mt-1">Go to Dataset Studio</p>
                </div>
              </div>
            </div>

            <div className="flex justify-between pt-6 border-t border-gray-100">
              <button 
                onClick={() => setStep(1)}
                className="text-gray-500 hover:text-black font-medium transition-colors"
              >
                Back
              </button>
              <button 
                onClick={handleCreate}
                className="bg-black text-white px-6 py-2.5 rounded-lg font-medium hover:bg-gray-900 transition-colors flex items-center gap-2"
              >
                Create Project
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
