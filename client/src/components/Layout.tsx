import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useStore } from '../store/useStore';
import { Mic2, LayoutDashboard, FolderPlus, Database, Settings2, LogOut, Music } from 'lucide-react';
import { cn } from '../lib/utils';
import JobMonitor from './JobMonitor';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/projects/new', icon: FolderPlus, label: 'New Project' },
  { to: '/dataset', icon: Database, label: 'Dataset Studio' },
  { to: '/models', icon: Mic2, label: 'Voice Models' },
  { to: '/conversion', icon: Settings2, label: 'Conversion Studio' },
];

export default function Layout() {
  const { user, logout } = useStore();
  const navigate = useNavigate();

  if (!user) return <Outlet />;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50 text-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 flex items-center gap-3 border-b border-gray-100">
          <div className="w-8 h-8 rounded-lg bg-black flex items-center justify-center">
            <Music className="w-5 h-5 text-white" />
          </div>
          <span className="font-semibold text-lg tracking-tight">VoiceForge</span>
        </div>
        
        <div className="p-4 flex-1">
          <div className="mb-6 px-3">
            <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">Menu</p>
            <nav className="space-y-1">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => cn(
                    "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive ? "bg-gray-100 text-black" : "text-gray-600 hover:bg-gray-50 hover:text-black"
                  )}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        </div>

        <div className="p-4 border-t border-gray-100">
          <div className="flex items-center justify-between mb-4 px-3">
            <div className="text-sm">
              <p className="font-medium text-gray-900 truncate">{user.name}</p>
              <p className="text-xs text-gray-500 truncate">{user.organization}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 w-full rounded-md text-sm font-medium text-red-600 hover:bg-red-50 transition-colors"
          >
            <LogOut className="w-4 h-4" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden relative">
        <div className="flex-1 overflow-y-auto p-8 pb-32">
          <Outlet />
        </div>
        
        {/* Floating Job Monitor */}
        <div className="fixed bottom-6 right-6 z-50">
          <JobMonitor />
        </div>
      </main>
    </div>
  );
}
