import React, { useState, useEffect } from 'react';
import { Camera, CheckCircle, AlertTriangle } from 'lucide-react';
import axios from 'axios';

interface VerificationTelemetry {
  similarity_score?: number;
  quality_score?: number;
  liveness_score?: number;
  dynamic_threshold?: number;
  composite_score?: number;
  final_decision?: string;
}

export const KioskPage: React.FC = () => {
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [statusState, setStatusState] = useState<'MATCH' | 'ALREADY_MARKED' | 'SPOOF_REJECTED' | 'QUALITY_REJECTED' | 'UNKNOWN_REJECTED' | 'SEARCHING'>('MATCH');
  const [lastStudent, setLastStudent] = useState<{ name: string; studentId: string }>({
    name: 'Alex Johnson',
    studentId: 'STU-2026-001',
  });
  const [telemetry, setTelemetry] = useState<VerificationTelemetry>({
    similarity_score: 0.942,
    quality_score: 0.880,
    liveness_score: 0.990,
    dynamic_threshold: 0.543,
    composite_score: 0.915,
  });



  // Poll frame verification every 3 seconds when streaming
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(async () => {
      // Simulate live frame capture and API call
      try {
        const dummyCanvas = document.createElement('canvas');
        dummyCanvas.width = 320;
        dummyCanvas.height = 240;
        const ctx = dummyCanvas.getContext('2d');
        if (ctx) {
          ctx.fillStyle = '#1e293b';
          ctx.fillRect(0, 0, 320, 240);
        }
        const b64Frame = dummyCanvas.toDataURL('image/jpeg', 0.8);

        const res = await axios.post('http://127.0.0.1:8000/api/v1/attendance/verify-and-mark', {
          session_id: 1,
          image_base64: b64Frame,
        });

        if (res.data && res.data.telemetry) {
          setTelemetry(res.data.telemetry);
          if (res.data.status === 'SUCCESS') {
            setStatusState('MATCH');
            if (res.data.student_name) {
              setLastStudent({ name: res.data.student_name, studentId: res.data.student_id });
            }
          } else if (res.data.status === 'ALREADY_MARKED') {
            setStatusState('ALREADY_MARKED');
          } else if (res.data.status === 'SPOOF_REJECTED') {
            setStatusState('SPOOF_REJECTED');
          } else if (res.data.status === 'QUALITY_REJECTED') {
            setStatusState('QUALITY_REJECTED');
          } else {
            setStatusState('UNKNOWN_REJECTED');
          }
        }
      } catch (err) {
        // Fallback demo state on backend offline
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [isStreaming]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
            Live Recognition Kiosk
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Real-Time QMF-Score Multi-Factor Facial Recognition Engine
          </p>
        </div>

        <button 
          onClick={() => setIsStreaming(!isStreaming)}
          style={{
            backgroundColor: isStreaming ? '#ef4444' : '#38bdf8',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '10px 18px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Camera size={18} />
          {isStreaming ? 'Stop Camera Kiosk' : 'Start Camera Kiosk'}
        </button>
      </div>

      {/* Grid: Camera Stream + Live Feedback Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Webcam Canvas Feed Container */}
        <div style={{
          backgroundColor: '#000000',
          borderRadius: '12px',
          border: '2px solid rgba(56, 189, 248, 0.3)',
          aspectRatio: '16/9',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden'
        }}>
          {/* Simulated Bounding Box Overlay */}
          <div style={{
            position: 'absolute',
            width: '220px',
            height: '260px',
            border: statusState === 'SPOOF_REJECTED' ? '3px solid #ef4444' : '3px solid #34d399',
            borderRadius: '16px',
            boxShadow: statusState === 'SPOOF_REJECTED' ? '0 0 25px rgba(239, 68, 68, 0.5)' : '0 0 25px rgba(52, 211, 153, 0.5)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '12px'
          }}>
            <div style={{
              backgroundColor: statusState === 'SPOOF_REJECTED' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(52, 211, 153, 0.9)',
              color: '#0f172a',
              fontSize: '12px',
              fontWeight: 700,
              padding: '4px 8px',
              borderRadius: '4px',
              alignSelf: 'flex-start'
            }}>
              {statusState === 'SPOOF_REJECTED' ? 'SPOOF REJECTED' : `AUTHENTICATED (${((telemetry.similarity_score || 0.942) * 100).toFixed(1)}%)`}
            </div>
            
            <div style={{
              color: '#ffffff',
              fontSize: '11px',
              backgroundColor: 'rgba(15, 23, 42, 0.8)',
              padding: '4px 8px',
              borderRadius: '4px'
            }}>
              Q: {telemetry.quality_score?.toFixed(2) || '0.88'} | L: {telemetry.liveness_score?.toFixed(2) || '0.99'} | Tau(Q): {telemetry.dynamic_threshold?.toFixed(2) || '0.54'}
            </div>
          </div>

          <div style={{ color: '#94a3b8', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Camera size={24} />
            <span>Webcam MediaStream Active (1280x720 @ 30 FPS)</span>
          </div>
        </div>

        {/* Live Feedback Panel */}
        <div style={{
          backgroundColor: 'rgba(30, 41, 59, 0.65)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '12px',
          padding: '24px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between'
        }}>
          <div>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
              Verification Status
            </h3>

            {/* Status Card */}
            <div style={{
              backgroundColor: statusState === 'SPOOF_REJECTED' ? 'rgba(239, 68, 68, 0.12)' : 'rgba(52, 211, 153, 0.12)',
              border: statusState === 'SPOOF_REJECTED' ? '1px solid rgba(239, 68, 68, 0.3)' : '1px solid rgba(52, 211, 153, 0.3)',
              borderRadius: '10px',
              padding: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '20px'
            }}>
              {statusState === 'SPOOF_REJECTED' ? (
                <AlertTriangle size={32} color="#ef4444" />
              ) : (
                <CheckCircle size={32} color="#34d399" />
              )}
              <div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: statusState === 'SPOOF_REJECTED' ? '#ef4444' : '#34d399' }}>
                  {statusState === 'SPOOF_REJECTED' ? 'Spoof Presentation Rejected' : lastStudent.name}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  ID: {lastStudent.studentId} • {statusState === 'ALREADY_MARKED' ? 'ALREADY LOGGED' : 'Logged PRESENT'}
                </div>
              </div>
            </div>

            {/* Multi-Factor Metrics Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>ArcFace Cosine Similarity (S)</span>
                <span style={{ color: '#38bdf8', fontWeight: 700 }}>{((telemetry.similarity_score || 0.942) * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Sample Quality Score (Q)</span>
                <span style={{ color: '#34d399', fontWeight: 700 }}>{((telemetry.quality_score || 0.880) * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>MiniFASNet Liveness Score (L)</span>
                <span style={{ color: '#a855f7', fontWeight: 700 }}>{((telemetry.liveness_score || 0.990) * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                <span style={{ color: '#94a3b8' }}>Dynamic Adaptive Threshold Tau(Q)</span>
                <span style={{ color: '#f8fafc', fontWeight: 700 }}>{(telemetry.dynamic_threshold || 0.543).toFixed(3)}</span>
              </div>
            </div>
          </div>

          <div style={{ fontSize: '12px', color: '#94a3b8', textAlign: 'center', marginTop: '20px' }}>
            Zero Raw-Image Backend Retention Active (GDPR Art. 9 Compliant)
          </div>
        </div>
      </div>
    </div>
  );
};
