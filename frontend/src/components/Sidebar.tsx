import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { 
  LayoutDashboard, 
  Camera, 
  Users, 
  BookOpen, 
  CalendarCheck, 
  FileSpreadsheet, 
  ShieldCheck, 
  LogOut,
  BarChart3,
  GraduationCap,
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const { user, logout, hasRole } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  // Build nav items based on role
  const navItems: Array<{ path: string; label: string; icon: any }> = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/kiosk', label: 'Live Kiosk', icon: Camera },
  ];

  // Admin/Instructor-only items
  if (hasRole('ADMIN', 'INSTRUCTOR')) {
    navItems.push(
      { path: '/students', label: 'Students', icon: Users },
      { path: '/courses', label: 'Courses', icon: BookOpen },
      { path: '/sessions', label: 'Attendance Sessions', icon: CalendarCheck },
      { path: '/analytics', label: 'Analytics', icon: BarChart3 },
    );
  }

  // Admin-only
  if (hasRole('ADMIN')) {
    navItems.push(
      { path: '/reports', label: 'Reports & Export', icon: FileSpreadsheet },
    );
  }

  // Student-only
  if (hasRole('STUDENT')) {
    navItems.push(
      { path: '/my-attendance', label: 'My Attendance', icon: GraduationCap },
    );
  }

  // Role badge color
  const roleBadgeColor = {
    ADMIN: '#38bdf8',
    INSTRUCTOR: '#a78bfa',
    STUDENT: '#34d399',
  }[user?.role || 'STUDENT'];

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
              end={item.path === '/'}
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
          <div style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>
            {user?.fullName || 'Guest'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '2px' }}>
            <span style={{
              fontSize: '10px', fontWeight: 700, color: roleBadgeColor,
              background: `${roleBadgeColor}20`,
              padding: '2px 6px', borderRadius: '4px',
              textTransform: 'uppercase', letterSpacing: '0.04em',
            }}>
              {user?.role || 'GUEST'}
            </span>
          </div>
        </div>
        <button
          onClick={handleLogout}
          title="Sign Out"
          style={{
            background: 'none',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '6px',
            transition: 'all 0.15s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.color = '#ef4444';
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.color = '#94a3b8';
            e.currentTarget.style.background = 'none';
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  );
};
