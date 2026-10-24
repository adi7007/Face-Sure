import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Camera, CameraOff, CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react';
import axios from 'axios';

interface VerificationTelemetry {
  similarity_score?: number;
  quality_score?: number;
  liveness_score?: number;
  dynamic_threshold?: number;
  composite_score?: number;
  final_decision?: string;
}

interface ExplainableDecision {
  identity_match?: { score: number; verdict: string; detail: string };
  liveness?: { score: number; verdict: string; detail: string };
  quality?: { score: number; verdict: string; detail: string };
  duplicate_check?: { verdict: string; detail: string };
  time_status?: { verdict: string; detail: string };
  final_decision?: string;
  composite_qmf_score?: number;
  dynamic_threshold?: number;
}

type StatusState = 'MATCH' | 'ALREADY_MARKED' | 'SPOOF_REJECTED' | 'QUALITY_REJECTED' | 'UNKNOWN_REJECTED' | 'NO_ENROLLED_STUDENTS' | 'SEARCHING' | 'IDLE' | 'ERROR';

export const KioskPage: React.FC = () => {
  const [isStreaming, setIsStreaming] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [statusState, setStatusState] = useState<StatusState>('IDLE');
  const [lastStudent, setLastStudent] = useState<{ name: string; studentId: string; email: string; attendanceStatus?: string } | null>(null);
  const [telemetry, setTelemetry] = useState<VerificationTelemetry>({});
  const [explainableDecision, setExplainableDecision] = useState<ExplainableDecision | null>(null);
  const [verificationMessage, setVerificationMessage] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const verificationInFlightRef = useRef(false);
  const scanVersionRef = useRef(0);

  // Start camera
  const startCamera = useCallback(async () => {
    setCameraError(null);
    scanVersionRef.current += 1;
    setLastStudent(null);
    setTelemetry({});
    setExplainableDecision(null);
    setVerificationMessage(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'user',
        },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsStreaming(true);
      setStatusState('SEARCHING');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Unknown error';
      if (message.includes('NotAllowed') || message.includes('Permission')) {
        setCameraError('Camera permission denied. Please allow camera access in your browser settings.');
      } else if (message.includes('NotFound') || message.includes('DevicesNotFound')) {
        setCameraError('No camera found. Please connect a webcam.');
      } else {
        setCameraError(`Camera error: ${message}`);
      }
      setIsStreaming(false);
    }
  }, []);

  // Stop camera
  const stopCamera = useCallback(() => {
    scanVersionRef.current += 1;
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsStreaming(false);
    setStatusState('IDLE');
    setLastStudent(null);
    setTelemetry({});
    setExplainableDecision(null);
    setVerificationMessage(null);
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, []);

  // Capture a frame from the video element
  const captureFrame = useCallback((): string | null => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return null;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    if (!ctx) return null;

    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg', 0.8);
  }, []);

  // Poll frame verification every 3 seconds when streaming
  useEffect(() => {
    if (!isStreaming) return;

    const interval = setInterval(async () => {
      if (verificationInFlightRef.current) return;
      const frame = captureFrame();
      if (!frame) return;

      const scanVersion = ++scanVersionRef.current;
      verificationInFlightRef.current = true;

      try {
        // A new frame invalidates every previous identity before its result arrives.
        setStatusState('SEARCHING');
        setLastStudent(null);
        setTelemetry({});
        setExplainableDecision(null);
        setVerificationMessage(null);
        const res = await axios.post('http://127.0.0.1:8000/api/v1/attendance/verify-and-mark', {
          image_base64: frame,
        });

        if (scanVersion !== scanVersionRef.current) return;

        if (res.data) {
          if (res.data.telemetry) setTelemetry(res.data.telemetry);
          if (res.data.explainable_decision) setExplainableDecision(res.data.explainable_decision);
          if (res.data.status === 'SUCCESS' && res.data.student_name && res.data.student_id && res.data.student_email) {
            setStatusState('MATCH');
            setLastStudent({ name: res.data.student_name, studentId: res.data.student_id, email: res.data.student_email, attendanceStatus: res.data.attendance_status });
          } else if (res.data.status === 'ALREADY_MARKED' && res.data.student_name && res.data.student_id && res.data.student_email) {
            setStatusState('ALREADY_MARKED');
            setLastStudent({ name: res.data.student_name, studentId: res.data.student_id, email: res.data.student_email });
          } else if (res.data.status === 'NO_ENROLLED_STUDENTS') {
            setLastStudent(null);
            setStatusState('NO_ENROLLED_STUDENTS');
            setVerificationMessage(res.data.message || 'No biometric templates are enrolled.');
          } else if (res.data.status === 'SPOOF_REJECTED') {
            setLastStudent(null);
            setStatusState('SPOOF_REJECTED');
            setVerificationMessage(res.data.message || 'Presentation attack detected.');
          } else if (res.data.status === 'QUALITY_REJECTED') {
            setLastStudent(null);
            setStatusState('QUALITY_REJECTED');
            setVerificationMessage(res.data.message || 'Face sample quality is too low.');
          } else {
            setLastStudent(null);
            setStatusState('UNKNOWN_REJECTED');
            setVerificationMessage(res.data.message || 'Face was not verified.');
          }
        }
      } catch (error) {
        if (scanVersion !== scanVersionRef.current) return;
        setLastStudent(null);
        setStatusState('ERROR');
        const message = axios.isAxiosError(error)
          ? (error.response?.data?.detail || error.response?.data?.message || 'Verification service is unavailable.')
          : 'Verification service is unavailable.';
        setVerificationMessage(String(message));
      } finally {
        verificationInFlightRef.current = false;
      }
    }, 3000);

    return () => {
      scanVersionRef.current += 1;
      clearInterval(interval);
    };
  }, [isStreaming, captureFrame]);

  const getStatusConfig = () => {
    switch (statusState) {
      case 'MATCH':
        return { color: '#34d399', bg: 'rgba(52, 211, 153, 0.12)', border: 'rgba(52, 211, 153, 0.3)', icon: CheckCircle, label: 'Verified & Logged', borderGlow: '0 0 25px rgba(52, 211, 153, 0.5)' };
      case 'ALREADY_MARKED':
        return { color: '#38bdf8', bg: 'rgba(56, 189, 248, 0.12)', border: 'rgba(56, 189, 248, 0.3)', icon: CheckCircle, label: 'Already Logged', borderGlow: '0 0 25px rgba(56, 189, 248, 0.5)' };
      case 'SPOOF_REJECTED':
        return { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.12)', border: 'rgba(239, 68, 68, 0.3)', icon: XCircle, label: 'Spoof Rejected', borderGlow: '0 0 25px rgba(239, 68, 68, 0.5)' };
      case 'QUALITY_REJECTED':
        return { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', border: 'rgba(245, 158, 11, 0.3)', icon: AlertTriangle, label: 'Low Quality — Retry', borderGlow: '0 0 25px rgba(245, 158, 11, 0.5)' };
      case 'UNKNOWN_REJECTED':
        return { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.12)', border: 'rgba(239, 68, 68, 0.3)', icon: XCircle, label: 'Unknown Face', borderGlow: '0 0 25px rgba(239, 68, 68, 0.5)' };
      case 'NO_ENROLLED_STUDENTS':
        return { color: '#f59e0b', bg: 'rgba(245, 158, 11, 0.12)', border: 'rgba(245, 158, 11, 0.3)', icon: AlertTriangle, label: 'No Enrolled Templates', borderGlow: 'none' };
      case 'ERROR':
        return { color: '#ef4444', bg: 'rgba(239, 68, 68, 0.12)', border: 'rgba(239, 68, 68, 0.3)', icon: XCircle, label: 'Verification Unavailable', borderGlow: 'none' };
      case 'SEARCHING':
        return { color: '#a855f7', bg: 'rgba(168, 85, 247, 0.12)', border: 'rgba(168, 85, 247, 0.3)', icon: Clock, label: 'Scanning...', borderGlow: '0 0 25px rgba(168, 85, 247, 0.5)' };
      default:
        return { color: '#94a3b8', bg: 'rgba(148, 163, 184, 0.12)', border: 'rgba(148, 163, 184, 0.3)', icon: Camera, label: 'Camera Off', borderGlow: 'none' };
    }
  };

  const status = getStatusConfig();
  const StatusIcon = status.icon;

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
          onClick={isStreaming ? stopCamera : startCamera}
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
            gap: '8px',
            transition: 'all 0.2s ease',
          }}
        >
          {isStreaming ? <CameraOff size={18} /> : <Camera size={18} />}
          {isStreaming ? 'Stop Camera Kiosk' : 'Start Camera Kiosk'}
        </button>
      </div>

      {/* Camera Error */}
      {cameraError && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.12)',
          border: '1px solid rgba(239, 68, 68, 0.3)',
          borderRadius: '10px',
          padding: '14px 18px',
          color: '#ef4444',
          fontSize: '14px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <AlertTriangle size={18} />
          {cameraError}
        </div>
      )}

      {/* Grid: Camera Stream + Live Feedback Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Webcam Video Feed */}
        <div style={{
          backgroundColor: '#000000',
          borderRadius: '12px',
          border: `2px solid ${isStreaming ? status.border : 'rgba(56, 189, 248, 0.15)'}`,
          aspectRatio: '16/9',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          boxShadow: isStreaming ? status.borderGlow : 'none',
          transition: 'all 0.3s ease',
        }}>
          {/* Live Video Element */}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              display: isStreaming ? 'block' : 'none',
              transform: 'scaleX(-1)',
            }}
          />

          {/* Hidden canvas for frame capture */}
          <canvas ref={canvasRef} style={{ display: 'none' }} />

          {/* Overlay when streaming */}
          {isStreaming && (
            <div style={{
              position: 'absolute',
              inset: 0,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              padding: '16px',
              pointerEvents: 'none',
            }}>
              {/* Top-left: status badge */}
              <div style={{
                backgroundColor: `${status.color}e6`,
                color: '#0f172a',
                fontSize: '12px',
                fontWeight: 700,
                padding: '5px 10px',
                borderRadius: '6px',
                alignSelf: 'flex-start',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
              }}>
                <StatusIcon size={14} />
                {status.label}
                {statusState === 'MATCH' && telemetry.similarity_score && ` (${(telemetry.similarity_score * 100).toFixed(1)}%)`}
              </div>

              {/* Bottom: telemetry bar */}
              {telemetry.quality_score !== undefined && (
                <div style={{
                  color: '#ffffff',
                  fontSize: '11px',
                  backgroundColor: 'rgba(15, 23, 42, 0.85)',
                  padding: '6px 10px',
                  borderRadius: '6px',
                  alignSelf: 'flex-start',
                }}>
                  Q: {telemetry.quality_score?.toFixed(2)} | L: {telemetry.liveness_score?.toFixed(2)} | τ(Q): {telemetry.dynamic_threshold?.toFixed(2)}
                </div>
              )}
            </div>
          )}

          {/* Placeholder when camera is off */}
          {!isStreaming && (
            <div style={{
              color: '#94a3b8',
              fontSize: '14px',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '12px',
            }}>
              <Camera size={48} strokeWidth={1.5} />
              <span>Click <strong>"Start Camera Kiosk"</strong> to begin</span>
              <span style={{ fontSize: '12px', color: '#64748b' }}>Your browser will request camera permission</span>
            </div>
          )}
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
          justifyContent: 'space-between',
        }}>
          <div>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
              Verification Status
            </h3>

            {/* Status Card */}
            <div style={{
              backgroundColor: status.bg,
              border: `1px solid ${status.border}`,
              borderRadius: '10px',
              padding: '16px',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              marginBottom: '20px',
              transition: 'all 0.3s ease',
            }}>
              <StatusIcon size={32} color={status.color} />
              <div>
                <div style={{ fontSize: '16px', fontWeight: 700, color: status.color }}>
                  {statusState === 'IDLE' ? 'Awaiting Camera' :
                   statusState === 'SEARCHING' ? 'Scanning for Faces...' :
                   statusState === 'MATCH' && lastStudent ? lastStudent.name :
                   statusState === 'ALREADY_MARKED' && lastStudent ? lastStudent.name :
                   status.label}
                </div>
                <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '2px' }}>
                   {statusState === 'IDLE' ? 'Start the camera to begin recognition' :
                    statusState === 'SEARCHING' ? 'Processing live video frames...' :
                    statusState === 'MATCH' && lastStudent ? `ID: ${lastStudent.studentId} • ${lastStudent.email} • Logged ${lastStudent.attendanceStatus || 'PRESENT'}` :
                    statusState === 'ALREADY_MARKED' && lastStudent ? `ID: ${lastStudent.studentId} • ${lastStudent.email} • ALREADY LOGGED` :
                    statusState === 'SPOOF_REJECTED' ? 'Presentation attack detected' :
                    statusState === 'QUALITY_REJECTED' ? 'Face too blurry or poorly lit' :
                    verificationMessage || 'Face not recognized in database'}
                </div>
              </div>
            </div>

            {/* Multi-Factor Metrics Breakdown */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '13px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>ArcFace Cosine Similarity (S)</span>
                <span style={{ color: '#38bdf8', fontWeight: 700 }}>
                  {telemetry.similarity_score ? `${(telemetry.similarity_score * 100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>Sample Quality Score (Q)</span>
                <span style={{ color: '#34d399', fontWeight: 700 }}>
                  {telemetry.quality_score ? `${(telemetry.quality_score * 100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#94a3b8' }}>MiniFASNet Liveness Score (L)</span>
                <span style={{ color: '#a855f7', fontWeight: 700 }}>
                  {telemetry.liveness_score ? `${(telemetry.liveness_score * 100).toFixed(1)}%` : '—'}
                </span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingTop: '8px', borderTop: '1px solid rgba(255,255,255,0.06)' }}>
                <span style={{ color: '#94a3b8' }}>Dynamic Adaptive Threshold τ(Q)</span>
                <span style={{ color: '#f8fafc', fontWeight: 700 }}>
                  {telemetry.dynamic_threshold ? telemetry.dynamic_threshold.toFixed(3) : '—'}
                </span>
              </div>
            </div>

            {/* Explainable AI Decision Breakdown */}
            {explainableDecision && statusState === 'MATCH' && (
              <div style={{
                marginTop: '20px', padding: '16px', borderRadius: '10px',
                background: 'rgba(15, 23, 42, 0.5)',
                border: '1px solid rgba(56, 189, 248, 0.15)',
              }}>
                <div style={{ fontSize: '12px', fontWeight: 700, color: '#38bdf8', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Explainable Decision
                </div>
                {[
                  { label: 'Identity Match', data: explainableDecision.identity_match, icon: '🎯' },
                  { label: 'Liveness', data: explainableDecision.liveness, icon: '🛡️' },
                  { label: 'Quality', data: explainableDecision.quality, icon: '📷' },
                  { label: 'Duplicate Check', data: explainableDecision.duplicate_check, icon: '🔍' },
                  { label: 'Time Status', data: explainableDecision.time_status, icon: '⏰' },
                ].map(({ label, data, icon }) => {
                  if (!data) return null;
                  const verdict = data.verdict;
                  const isPass = verdict === 'PASS' || verdict === 'CLEAR' || verdict === 'PRESENT';
                  const isWarn = verdict === 'LATE';
                  return (
                    <div key={label} style={{
                      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                      padding: '6px 0', borderBottom: '1px solid rgba(255,255,255,0.04)',
                    }}>
                      <span style={{ fontSize: '12px', color: '#94a3b8' }}>{icon} {label}</span>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {'score' in data && (data as any).score !== undefined && (
                          <span style={{ fontSize: '12px', fontWeight: 600, color: '#38bdf8' }}>
                            {(data as any).score}%
                          </span>
                        )}
                        <span style={{
                          fontSize: '10px', fontWeight: 700, padding: '2px 8px', borderRadius: '4px',
                          background: isPass ? 'rgba(52, 211, 153, 0.15)' : isWarn ? 'rgba(245, 158, 11, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                          color: isPass ? '#34d399' : isWarn ? '#f59e0b' : '#ef4444',
                        }}>
                          {verdict}
                        </span>
                      </div>
                    </div>
                  );
                })}
                {/* Final Decision Row */}
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  marginTop: '8px', paddingTop: '8px',
                  borderTop: '1px solid rgba(56, 189, 248, 0.15)',
                }}>
                  <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>Final Decision</span>
                  <span style={{
                    fontSize: '12px', fontWeight: 700, padding: '3px 10px', borderRadius: '6px',
                    background: explainableDecision.final_decision === 'PRESENT' ? 'rgba(52, 211, 153, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: explainableDecision.final_decision === 'PRESENT' ? '#34d399' : '#f59e0b',
                  }}>
                    {explainableDecision.final_decision}
                  </span>
                </div>
              </div>
            )}
          </div>

          <div style={{ fontSize: '12px', color: '#94a3b8', textAlign: 'center', marginTop: '20px' }}>
            Zero Raw-Image Backend Retention Active (GDPR Art. 9 Compliant)
          </div>
        </div>
      </div>
    </div>
  );
};
