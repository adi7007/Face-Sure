import { StopCircle } from 'lucide-react';

export const SessionsPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
          Attendance Sessions
        </h1>
        <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
          Open, Monitor, and Close Real-Time Attendance Verification Sessions
        </p>
      </div>

      <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>Active Session: CS-401 Lecture 12</div>
            <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>Started at 10:00 AM • Late Threshold: 15 mins</div>
          </div>
          <button style={{ backgroundColor: '#ef4444', color: '#ffffff', border: 'none', borderRadius: '8px', padding: '10px 18px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <StopCircle size={18} /> Close Session
          </button>
        </div>
      </div>
    </div>
  );
};
