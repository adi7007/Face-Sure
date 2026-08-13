import React from 'react';
import { Bell, Activity, Database, CheckCircle2 } from 'lucide-react';

export const Navbar: React.FC = () => {
  return (
    <header style={{
      height: '64px',
      backgroundColor: '#0f172a',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 28px'
    }}>
      {/* Title / Search */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>
          Facial Recognition Attendance System
        </h2>
      </div>

      {/* System Status Indicators */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        {/* Backend Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#94a3b8' }}>
          <CheckCircle2 size={16} color="#34d399" />
          <span>API: <strong style={{ color: '#34d399' }}>Healthy</strong></span>
        </div>

        {/* Database Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#94a3b8' }}>
          <Database size={16} color="#38bdf8" />
          <span>pgvector: <strong style={{ color: '#38bdf8' }}>Ready</strong></span>
        </div>

        {/* CUDA Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#94a3b8' }}>
          <Activity size={16} color="#a855f7" />
          <span>GPU: <strong style={{ color: '#a855f7' }}>GTX 1650 (CUDA)</strong></span>
        </div>

        {/* Notification Bell */}
        <button style={{
          background: 'rgba(255,255,255,0.05)',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: '8px',
          padding: '8px',
          color: '#f8fafc',
          cursor: 'pointer'
        }}>
          <Bell size={18} />
        </button>
      </div>
    </header>
  );
};
