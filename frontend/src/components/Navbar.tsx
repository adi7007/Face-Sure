import React, { useState, useEffect, useRef } from 'react';
import { Bell, Activity, Database, CheckCircle2, X, Info, AlertTriangle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface Notification {
  id: string;
  type: 'success' | 'warning' | 'info' | 'error';
  title: string;
  message: string;
  time: string;
  read: boolean;
}

const fallbackNotifications: Notification[] = [
  {
    id: '1',
    type: 'info',
    title: 'System Online',
    message: 'FaceAttend QMF-Score recognition engine is active',
    time: 'Just now',
    read: false,
  },
];

export const Navbar: React.FC = () => {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState<Notification[]>(fallbackNotifications);
  const panelRef = useRef<HTMLDivElement>(null);

  // Fetch real alerts from API
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const res = await axios.get(`${API}/analytics/at-risk?threshold=75`);
        if (res.data?.students?.length > 0) {
          const alertNotifs: Notification[] = res.data.students.slice(0, 5).map((s: any, i: number) => ({
            id: `risk-${i}`,
            type: s.risk_level === 'CRITICAL' ? 'error' as const : 'warning' as const,
            title: `${s.risk_level} Risk: ${s.full_name}`,
            message: `${s.student_code} — ${s.attendance_pct}% attendance (${s.department})`,
            time: 'Active',
            read: false,
          }));
          setNotifications(alertNotifs);
        }
      } catch {
        // Keep fallback notifications
      }
    };
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60000); // Refresh every 60s
    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter((n) => !n.read).length;

  // Close on click outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (panelRef.current && !panelRef.current.contains(e.target as Node)) {
        setShowNotifications(false);
      }
    };
    if (showNotifications) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showNotifications]);

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const dismissNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const getNotifIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return <CheckCircle size={16} color="#34d399" />;
      case 'warning': return <AlertTriangle size={16} color="#f59e0b" />;
      case 'error': return <AlertTriangle size={16} color="#ef4444" />;
      case 'info': return <Info size={16} color="#38bdf8" />;
    }
  };

  const getNotifBorderColor = (type: Notification['type']) => {
    switch (type) {
      case 'success': return 'rgba(52, 211, 153, 0.25)';
      case 'warning': return 'rgba(245, 158, 11, 0.25)';
      case 'error': return 'rgba(239, 68, 68, 0.25)';
      case 'info': return 'rgba(56, 189, 248, 0.25)';
    }
  };

  return (
    <header style={{
      height: '64px',
      backgroundColor: '#0f172a',
      borderBottom: '1px solid rgba(255,255,255,0.08)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 28px',
    }}>
      {/* Title */}
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

        {/* GPU Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', color: '#94a3b8' }}>
          <Activity size={16} color="#a855f7" />
          <span>GPU: <strong style={{ color: '#a855f7' }}>GTX 1650 (CUDA)</strong></span>
        </div>

        {/* Notification Bell */}
        <div ref={panelRef} style={{ position: 'relative' }}>
          <button
            id="notification-bell"
            onClick={() => setShowNotifications(!showNotifications)}
            style={{
              background: showNotifications ? 'rgba(56, 189, 248, 0.15)' : 'rgba(255,255,255,0.05)',
              border: showNotifications ? '1px solid rgba(56, 189, 248, 0.3)' : '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              padding: '8px',
              color: '#f8fafc',
              cursor: 'pointer',
              position: 'relative',
              transition: 'all 0.2s ease',
            }}
          >
            <Bell size={18} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute',
                top: '-4px',
                right: '-4px',
                backgroundColor: '#ef4444',
                color: '#ffffff',
                fontSize: '10px',
                fontWeight: 700,
                width: '18px',
                height: '18px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '2px solid #0f172a',
              }}>
                {unreadCount}
              </span>
            )}
          </button>

          {/* Notification Dropdown Panel */}
          {showNotifications && (
            <div style={{
              position: 'absolute',
              top: 'calc(100% + 8px)',
              right: 0,
              width: '380px',
              maxHeight: '480px',
              backgroundColor: '#1e293b',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '12px',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.5)',
              zIndex: 1000,
              overflow: 'hidden',
              animation: 'fadeIn 0.15s ease-out',
            }}>
              {/* Panel Header */}
              <div style={{
                padding: '16px 18px',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
              }}>
                <div>
                  <div style={{ fontSize: '15px', fontWeight: 700, color: '#f8fafc' }}>Notifications</div>
                  {unreadCount > 0 && (
                    <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>
                      {unreadCount} unread
                    </div>
                  )}
                </div>
                {unreadCount > 0 && (
                  <button
                    onClick={markAllRead}
                    style={{
                      background: 'none',
                      border: 'none',
                      color: '#38bdf8',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      padding: '4px 8px',
                      borderRadius: '4px',
                    }}
                  >
                    Mark all read
                  </button>
                )}
              </div>

              {/* Notification List */}
              <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
                {notifications.length === 0 ? (
                  <div style={{
                    padding: '40px 20px',
                    textAlign: 'center',
                    color: '#94a3b8',
                    fontSize: '14px',
                  }}>
                    <Bell size={32} style={{ marginBottom: '8px', opacity: 0.4 }} />
                    <div>No notifications</div>
                  </div>
                ) : (
                  notifications.map((notif) => (
                    <div
                      key={notif.id}
                      style={{
                        padding: '14px 18px',
                        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                        borderLeft: `3px solid ${getNotifBorderColor(notif.type)}`,
                        backgroundColor: notif.read ? 'transparent' : 'rgba(56, 189, 248, 0.04)',
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'flex-start',
                        transition: 'background-color 0.2s ease',
                      }}
                    >
                      <div style={{ marginTop: '2px', flexShrink: 0 }}>
                        {getNotifIcon(notif.type)}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{
                          fontSize: '13px',
                          fontWeight: notif.read ? 500 : 700,
                          color: '#f8fafc',
                          marginBottom: '2px',
                        }}>
                          {notif.title}
                        </div>
                        <div style={{
                          fontSize: '12px',
                          color: '#94a3b8',
                          lineHeight: '1.4',
                        }}>
                          {notif.message}
                        </div>
                        <div style={{
                          fontSize: '11px',
                          color: '#64748b',
                          marginTop: '4px',
                        }}>
                          {notif.time}
                        </div>
                      </div>
                      <button
                        onClick={() => dismissNotification(notif.id)}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: '#64748b',
                          cursor: 'pointer',
                          padding: '2px',
                          flexShrink: 0,
                        }}
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-4px); }
          to { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </header>
  );
};
