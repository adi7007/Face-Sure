import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Navbar } from './Navbar';

export const Layout: React.FC = () => {
  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#0f172a' }}>
      <Sidebar />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
        <Navbar />
        <main style={{ flex: 1, padding: '28px', backgroundColor: '#0f172a' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
