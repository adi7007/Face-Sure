import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { KioskPage } from './pages/KioskPage';
import { StudentsPage } from './pages/StudentsPage';
import { CoursesPage } from './pages/CoursesPage';
import { SessionsPage } from './pages/SessionsPage';
import { ReportsPage } from './pages/ReportsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="kiosk" element={<KioskPage />} />
          <Route path="students" element={<StudentsPage />} />
          <Route path="courses" element={<CoursesPage />} />
          <Route path="sessions" element={<SessionsPage />} />
          <Route path="reports" element={<ReportsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
