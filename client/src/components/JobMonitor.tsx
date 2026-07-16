import React from 'react';
import { useStore } from '../store/useStore';
import { Loader2, CheckCircle2, AlertCircle, Play } from 'lucide-react';
import { cn } from '../lib/utils';

export default function JobMonitor() {
  const { activeJobs } = useStore();

  if (activeJobs.length === 0) return null;

  return (
    <div className="w-80 bg-white border border-gray-200 shadow-xl rounded-xl overflow-hidden flex flex-col">
      <div className="bg-gray-50 px-4 py-3 border-b border-gray-100 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Active Tasks</h3>
        <span className="flex h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
      </div>
      <div className="max-h-60 overflow-y-auto p-2 space-y-2">
        {activeJobs.map(job => (
          <div key={job.id} className="p-3 bg-white border border-gray-100 rounded-lg shadow-sm">
            <div className="flex justify-between items-start mb-2">
              <span className="text-xs font-medium text-gray-900 truncate max-w-[150px]">{job.type}</span>
              <span className="text-xs text-gray-500">{job.progress}%</span>
            </div>
            
            <div className="w-full bg-gray-100 rounded-full h-1.5 mb-2 overflow-hidden">
              <div 
                className={cn(
                  "h-1.5 rounded-full transition-all duration-500",
                  job.status === 'failed' ? "bg-red-500" :
                  job.status === 'completed' ? "bg-green-500" : "bg-black"
                )}
                style={{ width: `${job.progress}%` }}
              ></div>
            </div>
            
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 text-gray-500">
                {job.status === 'running' && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                {job.status === 'completed' && <CheckCircle2 className="w-3.5 h-3.5 text-green-500" />}
                {job.status === 'failed' && <AlertCircle className="w-3.5 h-3.5 text-red-500" />}
                {job.status === 'pending' && <Play className="w-3.5 h-3.5 text-gray-400" />}
                <span className="capitalize">{job.stage}</span>
              </div>
              {job.estimatedTime && (
                <span className="text-gray-400">~{job.estimatedTime}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
