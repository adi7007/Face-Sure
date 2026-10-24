import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { KioskPage } from './pages/KioskPage';
import { StudentsPage } from './pages/StudentsPage';
import { CoursesPage } from './pages/CoursesPage';
import { SessionsPage } from './pages/SessionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { AnalyticsPage } from './pages/AnalyticsPage';
import { StudentPortalPage } from './pages/StudentPortalPage';

/**
 * Protected route wrapper — redirects to /login if not authenticated.
 */
const ProtectedRoute: React.FC<{ children: React.ReactNode; allowedRoles?: string[] }> = ({
  children,
  allowedRoles,
}) => {
  const { isAuthenticated, isLoading, hasRole } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100vh', background: '#0f172a', color: '#38bdf8',
        fontSize: '16px', fontWeight: 500,
      }}>
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !hasRole(...allowedRoles)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public route */}
          <Route path="/login" element={<LoginPage />} />

          {/* Protected routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<DashboardPage />} />
            <Route path="kiosk" element={<KioskPage />} />
            <Route path="students" element={
              <ProtectedRoute allowedRoles={['ADMIN', 'INSTRUCTOR']}>
                <StudentsPage />
              </ProtectedRoute>
            } />
            <Route path="courses" element={
              <ProtectedRoute allowedRoles={['ADMIN', 'INSTRUCTOR']}>
                <CoursesPage />
              </ProtectedRoute>
            } />
            <Route path="sessions" element={
              <ProtectedRoute allowedRoles={['ADMIN', 'INSTRUCTOR']}>
                <SessionsPage />
              </ProtectedRoute>
            } />
            <Route path="reports" element={
              <ProtectedRoute allowedRoles={['ADMIN']}>
                <ReportsPage />
              </ProtectedRoute>
            } />
            <Route path="analytics" element={
              <ProtectedRoute allowedRoles={['ADMIN', 'INSTRUCTOR']}>
                <AnalyticsPage />
              </ProtectedRoute>
            } />
            <Route path="my-attendance" element={<StudentPortalPage />} />
          </Route>

          {/* Catch-all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
