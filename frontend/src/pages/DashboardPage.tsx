import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Users, BookOpen, CalendarCheck, ShieldCheck, Cpu } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import axios from 'axios';

interface DashboardData {
  total_students: number;
  present_count: number;
  absent_count: number;
  attendance_percentage: number;
  active_session: {
    id: string | null;
    course_code: string | null;
    course_name: string | null;
    status: string;
  };
  recent_records: Array<{
    id: string;
    student_id: string;
    name: string;
    marked_at: string;
    status: string;
    confidence: number;
    quality: number;
    liveness: number;
  }>;
}

export const DashboardPage: React.FC = () => {
  const [data, setData] = useState<DashboardData>({
    total_students: 0,
    present_count: 0,
    absent_count: 0,
    attendance_percentage: 0,
    active_session: { id: null, course_code: null, course_name: null, status: 'NONE' },
    recent_records: [],
  });

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const res = await axios.get('http://127.0.0.1:8000/api/v1/attendance/dashboard-summary');
        if (res.data) {
          setData(res.data);
        }
      } catch (e) {
        // Fallback demo state
      }
    };
    fetchDashboard();
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Page Title Header */}
      <div>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
          System Dashboard
        </h1>
        <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
          Real-Time Facial Recognition & Attendance Analytics Platform
        </p>
      </div>

      {/* Metrics Row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
        gap: '20px'
      }}>
        <StatCard title="Total Enrolled" value={data.total_students} subtitle="Active Student Roster" icon={Users} color="#38bdf8" />
        <StatCard title="Present Students" value={data.present_count} subtitle={`${data.absent_count} absent today`} icon={CalendarCheck} color="#34d399" />
        <StatCard title="Attendance Rate" value={`${data.attendance_percentage}%`} subtitle="Classroom Attendance" icon={BookOpen} color="#6366f1" />
        <StatCard title="Avg Liveness Score" value="—" subtitle="Available from verified attendance records" icon={ShieldCheck} color="#a855f7" />
      </div>

      {/* Main Grid Section */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Active Session Panel */}
        <div style={{
          backgroundColor: 'rgba(30, 41, 59, 0.65)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '12px',
          padding: '24px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
              Active Attendance Session
            </h3>
            <span style={{
              backgroundColor: 'rgba(52, 211, 153, 0.15)',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              color: '#34d399',
              padding: '4px 12px',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: 600
            }}>
              {data.active_session?.status === 'ACTIVE' ? 'LIVE' : 'NO ACTIVE SESSION'} • {data.active_session?.course_code || '—'}
            </span>
          </div>

          <div style={{
            backgroundColor: 'rgba(15, 23, 42, 0.6)',
            borderRadius: '10px',
            padding: '20px',
            border: '1px solid rgba(255, 255, 255, 0.05)',
            marginBottom: '20px'
          }}>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
              {data.active_session?.course_code || 'No active session'}{data.active_session?.course_name ? `: ${data.active_session.course_name}` : ''}
            </div>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>
              Instructor: Dr. Alan Turing • Session Window: Active
            </div>
            
            {/* Progress Bar */}
            <div style={{ marginTop: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>
                <span>Verified Students: {data.present_count} Logged</span>
                <span style={{ color: '#34d399', fontWeight: 600 }}>{data.attendance_percentage}% Logged</span>
              </div>
              <div style={{ height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${data.attendance_percentage}%`, height: '100%', backgroundColor: '#34d399', borderRadius: '4px' }}></div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <Link to="/kiosk" style={{
              flex: 1,
              backgroundColor: '#38bdf8',
              color: '#0f172a',
              textDecoration: 'none',
              padding: '12px',
              borderRadius: '8px',
              textAlign: 'center',
              fontWeight: 700,
              fontSize: '14px'
            }}>
              Open Live Webcam Kiosk
            </Link>
            <Link to="/sessions" style={{
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              color: '#f8fafc',
              textDecoration: 'none',
              padding: '12px 20px',
              borderRadius: '8px',
              textAlign: 'center',
              fontWeight: 600,
              fontSize: '14px'
            }}>
              Manage Sessions
            </Link>
          </div>
        </div>

        {/* AI & Research Pipeline Status */}
        <div style={{
          backgroundColor: 'rgba(30, 41, 59, 0.65)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '12px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Cpu size={18} color="#38bdf8" />
            QMF-Score Engine Status
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Detector Model</span>
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>OpenCV Cascade / Haar</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Embedder Model</span>
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>ArcFace (512D Vector)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Liveness Classifier</span>
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>MiniFASNet Passive FAS</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Dynamic Threshold Tau(Q)</span>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>Adaptive Enabled</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Duplicate Prevention</span>
              <span style={{ color: '#34d399', fontWeight: 600 }}>App & DB Enforced</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
