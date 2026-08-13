import React, { useState } from 'react';
import { Camera, CheckCircle } from 'lucide-react';

export const KioskPage: React.FC = () => {
  const [isStreaming, setIsStreaming] = useState<boolean>(true);
  const [lastRecognition] = useState<{
    name: string;
    studentId: string;
    confidence: number;
    quality: number;
    liveness: number;
    status: 'MATCH' | 'SPOOF' | 'SEARCHING';
  }>({
    name: 'Alex Johnson',
    studentId: 'STU-2026-001',
    confidence: 0.942,
    quality: 0.88,
    liveness: 0.99,
    status: 'MATCH'
  });

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
            border: '3px solid #34d399',
            borderRadius: '16px',
            boxShadow: '0 0 25px rgba(52, 211, 153, 0.5)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
            padding: '12px'
          }}>
            <div style={{
              backgroundColor: 'rgba(52, 211, 153, 0.9)',
              color: '#0f172a',
              fontSize: '12px',
              fontWeight: 700,
              padding: '4px 8px',
              borderRadius: '4px',
              alignSelf: 'flex-start'
            }}>
              AUTHENTICATED (94.2%)
            </div>
            
            <div style={{
              color: '#ffffff',
              fontSize: '11px',
              backgroundColor: 'rgba(15, 23, 42, 0.8)',
              padding: '4px 8px',
              borderRadius: '4px'
            }}>
              Q: 0.88 | L: 0.99 | Tau(Q): 0.54
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
              backgroundColor: 'rgba(52, 211, 153, 0.12)',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              borderRadius: '10px',
              padding: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '20px'
            }}>
              <CheckCircle size={32} color="#34d399" />
              <div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: '#34d399' }}>
                  {lastRecognition.name}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                  ID: {lastRecognition.studentId} • Logged PRESENT
                </div>
              </div>
            </div>

            {/* Multi-Factor Metrics Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>ArcFace Cosine Similarity</span>
                <span style={{ color: '#38bdf8', fontWeight: 700 }}>{(lastRecognition.confidence * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Sample Quality Score</span>
                <span style={{ color: '#34d399', fontWeight: 700 }}>{(lastRecognition.quality * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>MiniFASNet Liveness Score</span>
                <span style={{ color: '#a855f7', fontWeight: 700 }}>{(lastRecognition.liveness * 100).toFixed(1)}%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                <span style={{ color: '#94a3b8' }}>Dynamic Threshold Tau(Q)</span>
                <span style={{ color: '#f8fafc', fontWeight: 700 }}>0.543</span>
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
