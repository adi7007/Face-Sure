import { Users, BookOpen, CalendarCheck, ShieldCheck, Cpu } from 'lucide-react';
import { StatCard } from '../components/StatCard';

export const DashboardPage: React.FC = () => {
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
        <StatCard title="Total Students" value="150" subtitle="+12 registered this term" icon={Users} color="#38bdf8" />
        <StatCard title="Active Courses" value="4" subtitle="Computer Science & IT" icon={BookOpen} color="#6366f1" />
        <StatCard title="Attendance Rate" value="94.2%" subtitle="+2.4% vs baseline" icon={CalendarCheck} color="#34d399" />
        <StatCard title="Avg Liveness Score" value="0.984" subtitle="MiniFASNet Passive FAS" icon={ShieldCheck} color="#a855f7" />
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
              LIVE • CS-401
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
              CS-401: Deep Learning & Computer Vision
            </div>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>
              Instructor: Dr. Alan Turing • Session Window: 10:00 AM - 11:30 AM
            </div>
            
            {/* Progress Bar */}
            <div style={{ marginTop: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>
                <span>Verified Students: 42 / 45</span>
                <span style={{ color: '#34d399', fontWeight: 600 }}>93.3% Logged</span>
              </div>
              <div style={{ height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: '93.3%', height: '100%', backgroundColor: '#34d399', borderRadius: '4px' }}></div>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'flex', gap: '12px' }}>
            <a href="/kiosk" style={{
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
            </a>
            <a href="/sessions" style={{
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
            </a>
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
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>RetinaFace ResNet-50</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Embedder Model</span>
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>ArcFace (512D Vector)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Liveness Classifier</span>
              <span style={{ color: '#f8fafc', fontWeight: 600 }}>MiniFASNetV2 SE</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
              <span style={{ color: '#94a3b8' }}>Dynamic Threshold \tau(Q)</span>
              <span style={{ color: '#38bdf8', fontWeight: 600 }}>Adaptive Enabled</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Avg Frame Latency</span>
              <span style={{ color: '#34d399', fontWeight: 600 }}>41.2 ms (24.2 FPS)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
