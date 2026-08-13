import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Camera, 
  Users, 
  BookOpen, 
  CalendarCheck, 
  FileSpreadsheet, 
  ShieldCheck, 
  LogOut 
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/kiosk', label: 'Live Kiosk', icon: Camera },
    { path: '/students', label: 'Students', icon: Users },
    { path: '/courses', label: 'Courses', icon: BookOpen },
    { path: '/sessions', label: 'Attendance Sessions', icon: CalendarCheck },
    { path: '/reports', label: 'Reports & Export', icon: FileSpreadsheet },
  ];

  return (
    <aside style={{
      width: '260px',
      backgroundColor: '#1e293b',
      borderRight: '1px solid rgba(255,255,255,0.08)',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh'
    }}>
      {/* Brand Header */}
      <div style={{
        padding: '24px 20px',
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        borderBottom: '1px solid rgba(255,255,255,0.08)'
      }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '8px',
          background: 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff'
        }}>
          <ShieldCheck size={22} />
        </div>
        <div>
          <h1 style={{ margin: 0, fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>
            FaceAttend
          </h1>
          <span style={{ fontSize: '11px', color: '#38bdf8', fontWeight: 600 }}>
            QMF-Score AI v0.1
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav style={{ padding: '16px 12px', flex: 1, display: 'flex', flexDirection: 'column', gap: '6px' }}>
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.path}
              to={item.path}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                borderRadius: '8px',
                color: isActive ? '#38bdf8' : '#94a3b8',
                backgroundColor: isActive ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
                border: isActive ? '1px solid rgba(56, 189, 248, 0.25)' : '1px solid transparent',
                textDecoration: 'none',
                fontSize: '14px',
                fontWeight: isActive ? 600 : 500,
                transition: 'all 0.15s ease'
              })}
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid rgba(255,255,255,0.08)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>Admin User</div>
          <div style={{ fontSize: '11px', color: '#94a3b8' }}>admin@project.edu</div>
        </div>
        <button style={{
          background: 'none',
          border: 'none',
          color: '#94a3b8',
          cursor: 'pointer',
          padding: '6px'
        }}>
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};
