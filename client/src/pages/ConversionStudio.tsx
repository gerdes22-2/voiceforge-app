import React, { useState } from 'react';
import { useStore } from '../store/useStore';
import { Play, Settings2, Download, Mic2, Activity, SlidersHorizontal, Share2, Star, CheckCircle2 } from 'lucide-react';
import { cn } from '../lib/utils';
import AudioPlayer from '../components/AudioPlayer';

export default function ConversionStudio() {
  const { voiceModels, addJob } = useStore();
  const readyModels = voiceModels.filter(m => m.status === 'ready');
  const [selectedModel, setSelectedModel] = useState(readyModels[0]?.id || '');
  
  const [pitch, setPitch] = useState(0);
  const [strength, setStrength] = useState(80);
  const [protection, setProtection] = useState(33);

  const [hasConverted, setHasConverted] = useState(false);
  const [isConverting, setIsConverting] = useState(false);
  const [rating, setRating] = useState(0);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);

  const handleConvert = () => {
    setIsConverting(true);
    setFeedbackSubmitted(false);
    setRating(0);
    addJob({
      id: Date.now().toString(),
      type: 'Voice Conversion Pipeline',
      status: 'running',
      progress: 0,
      stage: 'Stem Separation'
    });
    
    // Simulate pipeline progression
    setTimeout(() => {
      setHasConverted(true);
      setIsConverting(false);
    }, 3000);
  };

  const handleRating = (r: number) => {
    setRating(r);
    setFeedbackSubmitted(true);
    // In a real app, send data to backend here.
  };

  return (
    <div className="max-w-6xl mx-auto pb-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-gray-900">Conversion Studio</h1>
          <p className="text-gray-500 mt-1">Transform your source audio into your custom AI voice.</p>
        </div>
        
        {hasConverted && (
          <div className="flex gap-3">
            <button className="bg-white border border-gray-200 text-gray-900 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center gap-2">
              <Share2 className="w-4 h-4" /> Share
            </button>
            <button className="bg-black text-white px-4 py-2 rounded-lg font-medium hover:bg-gray-900 transition-colors flex items-center gap-2">
              <Download className="w-4 h-4" /> Export Mix
            </button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          
          {hasConverted ? (
            <div className="space-y-6">
              <h3 className="text-lg font-bold text-gray-900">Final Results</h3>
              <AudioPlayer title="Final Master Mix" subtitle="Instrumental + AI Vocal" />
              
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Mic2 className="w-4 h-4 text-gray-500" /> Isolated AI Vocal
                  </h4>
                  <button className="w-full bg-gray-50 hover:bg-gray-100 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors">
                    <Play className="w-4 h-4" /> Preview Stem
                  </button>
                </div>
                <div className="bg-white border border-gray-100 rounded-xl p-4 shadow-sm">
                  <h4 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                    <Activity className="w-4 h-4 text-gray-500" /> Instrumental
                  </h4>
                  <button className="w-full bg-gray-50 hover:bg-gray-100 py-2 rounded-lg flex items-center justify-center gap-2 text-sm font-medium transition-colors">
                    <Play className="w-4 h-4" /> Preview Stem
                  </button>
                </div>
              </div>

              <div className="bg-white border border-gray-100 rounded-xl p-6 shadow-sm mt-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-2">How close is this to your real voice?</h3>
                {!feedbackSubmitted ? (
                  <div className="flex items-center gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        onClick={() => handleRating(star)}
                        className={cn("p-1 transition-all", rating >= star ? "text-yellow-400" : "text-gray-300 hover:text-yellow-400 hover:scale-110")}
                      >
                        <Star className="w-8 h-8 fill-current" />
                      </button>
                    ))}
                  </div>
                ) : (
                  <div className="text-sm text-green-600 font-medium flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> Thank you! Your feedback helps improve your voice model.
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200 p-12 flex flex-col items-center justify-center text-center min-h-[400px]">
              <div className="w-16 h-16 rounded-2xl bg-white shadow-sm flex items-center justify-center mb-6">
                <Settings2 className="w-8 h-8 text-gray-400" />
              </div>
              <h2 className="text-xl font-bold text-gray-900 mb-2">Ready to Convert</h2>
              <p className="text-gray-500 max-w-md mx-auto mb-8">
                Your source audio is uploaded. Select your voice model and adjust the parameters on the right to begin the conversion pipeline.
              </p>
              <button 
                onClick={handleConvert}
                disabled={isConverting}
                className={cn(
                  "bg-black text-white px-8 py-3.5 rounded-xl font-medium flex items-center gap-2 transition-all shadow-md hover:shadow-lg",
                  isConverting && "opacity-75 cursor-wait"
                )}
              >
                {isConverting ? (
                  <><Activity className="w-5 h-5 animate-pulse" /> Processing Pipeline...</>
                ) : (
                  <><Play className="w-5 h-5 fill-current" /> Start Conversion</>
                )}
              </button>
            </div>
          )}
        </div>

        <div>
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-6 sticky top-6">
            <div className="flex items-center gap-2 mb-6">
              <SlidersHorizontal className="w-5 h-5 text-gray-900" />
              <h3 className="font-semibold text-gray-900 text-lg">Parameters</h3>
            </div>

            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-900 mb-3">Voice Model</label>
                <select 
                  className="w-full px-3 py-2.5 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-black focus:border-black outline-none font-medium text-gray-900"
                  value={selectedModel}
                  onChange={e => setSelectedModel(e.target.value)}
                  disabled={hasConverted || isConverting}
                >
                  {readyModels.map(m => (
                    <option key={m.id} value={m.id}>{m.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Pitch Shift</label>
                  <span className="text-sm text-gray-500 font-medium">{pitch > 0 ? `+${pitch}` : pitch}</span>
                </div>
                <input 
                  type="range" min="-12" max="12" 
                  value={pitch} onChange={e => setPitch(parseInt(e.target.value))}
                  disabled={hasConverted || isConverting}
                  className="w-full accent-black"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>-12</span>
                  <span>0</span>
                  <span>+12</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Voice Strength (Index Rate)</label>
                  <span className="text-sm text-gray-500 font-medium">{strength}%</span>
                </div>
                <input 
                  type="range" min="0" max="100" 
                  value={strength} onChange={e => setStrength(parseInt(e.target.value))}
                  disabled={hasConverted || isConverting}
                  className="w-full accent-black"
                />
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Higher values strongly enforce the target voice identity, but may reduce emotional dynamics.
                </p>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <label className="text-sm font-medium text-gray-700">Consonant Protection</label>
                  <span className="text-sm text-gray-500 font-medium">{protection}%</span>
                </div>
                <input 
                  type="range" min="0" max="50" 
                  value={protection} onChange={e => setProtection(parseInt(e.target.value))}
                  disabled={hasConverted || isConverting}
                  className="w-full accent-black"
                />
                <p className="text-xs text-gray-500 mt-1.5 leading-relaxed">
                  Protects voiceless consonants (s, t, p, k) from breathing artifacts.
                </p>
              </div>
            </div>
            
            {hasConverted && (
               <div className="mt-8 pt-6 border-t border-gray-100">
                  <button 
                    onClick={() => setHasConverted(false)}
                    className="w-full bg-gray-50 text-gray-900 border border-gray-200 font-medium py-2.5 rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    Adjust & Re-convert
                  </button>
               </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
