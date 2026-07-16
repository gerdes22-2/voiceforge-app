import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProjectCreation from './pages/ProjectCreation';
import DatasetStudio from './pages/DatasetStudio';
import ModelDashboard from './pages/ModelDashboard';
import ConversionStudio from './pages/ConversionStudio';
import { useStore } from './store/useStore';

function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user } = useStore();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        
        <Route path="/" element={<RequireAuth><Layout /></RequireAuth>}>
          <Route index element={<Dashboard />} />
          <Route path="projects/new" element={<ProjectCreation />} />
          <Route path="dataset" element={<DatasetStudio />} />
          <Route path="models" element={<ModelDashboard />} />
          <Route path="conversion" element={<ConversionStudio />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
