import { create } from 'zustand';
import { projectApi, modelApi } from '../lib/api';

export interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  organization: string;
}

export interface Project {
  id: string;
  name: string;
  status: string;
  createdAt: string;
}

export interface VoiceModel {
  id: string;
  name: string;
  status: 'training' | 'ready' | 'failed' | 'approved' | 'rejected';
  qualityScore?: number;
  version: string;
}

export interface Job {
  id: string;
  type: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  stage: string;
  estimatedTime?: string;
}

interface AppState {
  user: User | null;
  projects: Project[];
  voiceModels: VoiceModel[];
  activeJobs: Job[];
  
  login: (user: User) => void;
  logout: () => void;
  fetchProjects: () => Promise<void>;
  addProject: (project: Project) => Promise<void>;
  updateJob: (id: string, updates: Partial<Job>) => void;
  addJob: (job: Job) => void;
}

export const useStore = create<AppState>((set, get) => ({
  user: null, // Start unauthenticated
  projects: [
    { id: '1', name: 'Midnight Run', status: 'active', createdAt: '2026-07-10' },
    { id: '2', name: 'Summer Vibes', status: 'completed', createdAt: '2026-07-12' },
  ],
  voiceModels: [
    { id: 'v1', name: 'Studio Lead (My Voice)', status: 'ready', qualityScore: 94.5, version: 'v1.2' },
    { id: 'v2', name: 'Rap Style Aggressive', status: 'training', version: 'v1.0' },
  ],
  activeJobs: [],

  login: (user) => set({ user }),
  logout: () => set({ user: null }),
  
  fetchProjects: async () => {
    try {
      const res = await projectApi.getProjects();
      set({ projects: res.data });
    } catch (error) {
      console.warn("Backend not reachable, using mock projects.");
      // Keep existing mock projects
    }
  },

  addProject: async (project) => {
    try {
      const res = await projectApi.createProject(project);
      set((state) => ({ projects: [...state.projects, res.data] }));
    } catch (error) {
      console.warn("Backend not reachable, adding mock project locally.");
      set((state) => ({ projects: [...state.projects, project] }));
    }
  },
  
  addJob: (job) => set((state) => ({ activeJobs: [...state.activeJobs, job] })),
  updateJob: (id, updates) => set((state) => ({
    activeJobs: state.activeJobs.map(j => j.id === id ? { ...j, ...updates } : j)
  })),
}));

