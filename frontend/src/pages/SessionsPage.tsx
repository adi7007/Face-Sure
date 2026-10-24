import React, { useState, useEffect, useCallback } from 'react';
import { Plus, StopCircle, PlayCircle, X, CalendarCheck, CheckCircle2, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface Session {
  id: string;
  courseCode: string;
  courseName: string;
  date: string;
  startTime: string;
  lateThreshold: number;
  status: 'active' | 'closed' | 'scheduled';
  presentCount: number;
  totalStudents: number;
}

interface CourseOption {
  code: string;
  name: string;
  id?: string;
}

const API_BASE = 'http://127.0.0.1:8000/api/v1';
const STORAGE_KEY = 'faceattend_sessions_cache';
const COURSES_CACHE_KEY = 'faceattend_courses_cache';

const defaultFallbackSessions: Session[] = [
  {
    id: '1',
    courseCode: 'CS-401',
    courseName: 'Deep Learning & Computer Vision',
    date: new Date().toISOString().split('T')[0],
    startTime: '10:00 AM',
    lateThreshold: 15,
    status: 'active',
    presentCount: 42,
    totalStudents: 50,
  },
  {
    id: '2',
    courseCode: 'CS-405',
    courseName: 'Advanced Machine Learning',
    date: new Date().toISOString().split('T')[0],
    startTime: '2:00 PM',
    lateThreshold: 10,
    status: 'scheduled',
    presentCount: 0,
    totalStudents: 38,
  },
  {
    id: '3',
    courseCode: 'IT-302',
    courseName: 'Database Systems & Vector Search',
    date: new Date(Date.now() - 86400000).toISOString().split('T')[0],
    startTime: '9:00 AM',
    lateThreshold: 15,
    status: 'closed',
    presentCount: 46,
    totalStudents: 50,
  },
];

const defaultCourses: CourseOption[] = [
  { code: 'CS-401', name: 'Deep Learning & Computer Vision' },
  { code: 'CS-405', name: 'Advanced Machine Learning' },
  { code: 'IT-302', name: 'Database Systems & Vector Search' },
];

export const SessionsPage: React.FC = () => {
  // Load sessions from localStorage or use defaults
  const [sessions, setSessions] = useState<Session[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {
      // fallback
    }
    return defaultFallbackSessions;
  });

  const [courses, setCourses] = useState<CourseOption[]>(() => {
    try {
      const saved = localStorage.getItem(COURSES_CACHE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          return parsed.map((c: Record<string, string>) => ({
            code: c.course_code || c.code,
            name: c.course_name || c.name,
            id: c.id,
          }));
        }
      }
    } catch {
      // fallback
    }
    return defaultCourses;
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showModal, setShowModal] = useState(false);
  const [formCourse, setFormCourse] = useState('');
  const [formDate, setFormDate] = useState(new Date().toISOString().split('T')[0]);
  const [formTime, setFormTime] = useState('');
  const [formThreshold, setFormThreshold] = useState('15');

  // Sync sessions to localStorage
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
    } catch {
      // ignore
    }
  }, [sessions]);

  // Fetch courses from backend for the dropdown
  const fetchCourses = useCallback(async () => {
    try {
      const res = await axios.get(`${API_BASE}/courses`);
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        const mapped = res.data.map((c: Record<string, string>) => ({
          code: c.course_code,
          name: c.course_name,
          id: c.id,
        }));
        setCourses(mapped);
      }
    } catch {
      // fallback to cache / defaults
    }
  }, []);

  // Fetch sessions from backend
  const fetchSessions = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/sessions`);
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        // Map backend response to our Session shape
        const mapped: Session[] = res.data.map((s: Record<string, unknown>) => ({
          id: String(s.id),
          courseCode: (s.course_code as string) || 'N/A',
          courseName: (s.course_name as string) || (s.title as string) || 'Untitled Session',
          date: s.start_time ? new Date(s.start_time as string).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
          startTime: s.start_time ? new Date(s.start_time as string).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
          lateThreshold: (s.late_threshold_minutes as number) || 15,
          status: ((s.status as string) || '').toLowerCase() === 'active' ? 'active'
            : ((s.status as string) || '').toLowerCase() === 'completed' ? 'closed'
            : 'scheduled',
          presentCount: (s.present_count as number) || 0,
          totalStudents: (s.total_students as number) || 50,
        }));
        setSessions(mapped);
      }
    } catch {
      // Use local cache
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCourses();
    fetchSessions();
  }, [fetchCourses, fetchSessions]);

  const handleCreateSession = async () => {
    const course = courses.find((c) => c.code === formCourse);
    if (!course || !formDate || !formTime) return;

    // Build frontend session object
    const newSession: Session = {
      id: String(Date.now()),
      courseCode: course.code,
      courseName: course.name,
      date: formDate,
      startTime: formTime,
      lateThreshold: parseInt(formThreshold) || 15,
      status: 'scheduled',
      presentCount: 0,
      totalStudents: 50,
    };

    // Try to persist to backend
    try {
      if (course.id) {
        const payload = {
          course_id: course.id,
          title: `${course.code}: ${course.name}`,
          late_threshold_minutes: parseInt(formThreshold) || 15,
        };
        const res = await axios.post(`${API_BASE}/sessions`, payload);
        if (res.data) {
          newSession.id = String(res.data.id);
          newSession.status = 'active';
        }
      }
    } catch {
      // Local fallback — session stays with local ID
    }

    setSessions((prev) => [newSession, ...prev]);
    setShowModal(false);
    setFormCourse('');
    setFormTime('');
    setFormThreshold('15');
  };

  const startSession = async (id: string) => {
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: 'active' as const } : s))
    );
    // Backend doesn't have a dedicated "start" endpoint — it starts on creation
  };

  const closeSession = async (id: string) => {
    // Try backend first
    try {
      await axios.post(`${API_BASE}/sessions/${id}/stop`);
    } catch {
      // ignore — update locally regardless
    }
    setSessions((prev) =>
      prev.map((s) => (s.id === id ? { ...s, status: 'closed' as const } : s))
    );
  };

  const getStatusBadge = (status: Session['status']) => {
    const configs = {
      active: { bg: 'rgba(52, 211, 153, 0.15)', border: 'rgba(52, 211, 153, 0.3)', color: '#34d399', label: '● LIVE' },
      scheduled: { bg: 'rgba(56, 189, 248, 0.15)', border: 'rgba(56, 189, 248, 0.3)', color: '#38bdf8', label: '◷ Scheduled' },
      closed: { bg: 'rgba(148, 163, 184, 0.15)', border: 'rgba(148, 163, 184, 0.2)', color: '#94a3b8', label: '✓ Closed' },
    };
    const c = configs[status];
    return (
      <span style={{
        backgroundColor: c.bg,
        border: `1px solid ${c.border}`,
        color: c.color,
        padding: '4px 12px',
        borderRadius: '20px',
        fontSize: '12px',
        fontWeight: 600,
      }}>
        {c.label}
      </span>
    );
  };

  const activeSessions = sessions.filter((s) => s.status === 'active');
  const otherSessions = sessions.filter((s) => s.status !== 'active');

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            Attendance Sessions
            {isLoading && <RefreshCw size={18} className="spin" color="#38bdf8" />}
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Open, Monitor, and Close Real-Time Attendance Verification Sessions
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => { fetchSessions(); fetchCourses(); }}
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
              color: '#f8fafc',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              borderRadius: '8px',
              padding: '10px 16px',
              fontWeight: 600,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <RefreshCw size={16} /> Sync
          </button>

          <button
            id="create-session-btn"
            onClick={() => setShowModal(true)}
            style={{
              backgroundColor: '#38bdf8',
              color: '#0f172a',
              border: 'none',
              borderRadius: '8px',
              padding: '10px 18px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              boxShadow: '0 4px 14px rgba(56, 189, 248, 0.3)',
              transition: 'all 0.2s ease',
            }}
          >
            <Plus size={18} /> Create Session
          </button>
        </div>
      </div>

      {/* Summary Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(52, 211, 153, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#34d399' }}>
            <PlayCircle size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Active Sessions</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>{activeSessions.length}</div>
          </div>
        </div>

        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(56, 189, 248, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#38bdf8' }}>
            <CalendarCheck size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Total Sessions</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>{sessions.length}</div>
          </div>
        </div>

        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(148, 163, 184, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#94a3b8' }}>
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Completed</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>{sessions.filter(s => s.status === 'closed').length}</div>
          </div>
        </div>
      </div>

      {/* Active Sessions */}
      {activeSessions.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {activeSessions.map((session) => (
            <div key={session.id} style={{
              backgroundColor: 'rgba(30, 41, 59, 0.65)',
              border: '1px solid rgba(52, 211, 153, 0.25)',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: '0 0 20px rgba(52, 211, 153, 0.08)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                    <span style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                      {session.courseCode}: {session.courseName}
                    </span>
                    {getStatusBadge(session.status)}
                  </div>
                  <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                    Started at {session.startTime} • Late Threshold: {session.lateThreshold} mins • {session.date}
                  </div>
                </div>
                <button
                  onClick={() => closeSession(session.id)}
                  style={{
                    backgroundColor: '#ef4444',
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
                  <StopCircle size={18} /> Close Session
                </button>
              </div>

              {/* Progress */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>
                  <span>Verified: {session.presentCount} / {session.totalStudents} students</span>
                  <span style={{ color: '#34d399', fontWeight: 600 }}>
                    {session.totalStudents > 0 ? ((session.presentCount / session.totalStudents) * 100).toFixed(1) : 0}%
                  </span>
                </div>
                <div style={{ height: '8px', backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{
                    width: `${session.totalStudents > 0 ? (session.presentCount / session.totalStudents) * 100 : 0}%`,
                    height: '100%',
                    backgroundColor: '#34d399',
                    borderRadius: '4px',
                    transition: 'width 0.5s ease',
                  }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* All Sessions Table */}
      <div style={{
        backgroundColor: 'rgba(30, 41, 59, 0.65)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
            All Sessions ({sessions.length})
          </h3>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>
            Data synced with PostgreSQL
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#f8fafc', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8', backgroundColor: 'rgba(15, 23, 42, 0.4)' }}>
              <th style={{ padding: '14px 18px' }}>Course</th>
              <th style={{ padding: '14px 18px' }}>Date</th>
              <th style={{ padding: '14px 18px' }}>Time</th>
              <th style={{ padding: '14px 18px' }}>Attendance</th>
              <th style={{ padding: '14px 18px' }}>Status</th>
              <th style={{ padding: '14px 18px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.length === 0 ? (
              <tr>
                <td colSpan={6} style={{ padding: '48px 20px', textAlign: 'center', color: '#94a3b8' }}>
                  <CalendarCheck size={36} style={{ marginBottom: '10px', opacity: 0.4 }} />
                  <div>No sessions found.</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                    Click "Create Session" to start a new attendance session.
                  </div>
                </td>
              </tr>
            ) : (
              [...activeSessions, ...otherSessions].map((s) => (
                <tr key={s.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <td style={{ padding: '14px 18px' }}>
                    <div style={{ fontWeight: 600, color: '#38bdf8' }}>{s.courseCode}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>{s.courseName}</div>
                  </td>
                  <td style={{ padding: '14px 18px', color: '#94a3b8' }}>{s.date}</td>
                  <td style={{ padding: '14px 18px', color: '#94a3b8' }}>{s.startTime}</td>
                  <td style={{ padding: '14px 18px' }}>
                    <span style={{ fontWeight: 600 }}>{s.presentCount}</span>
                    <span style={{ color: '#94a3b8' }}> / {s.totalStudents}</span>
                  </td>
                  <td style={{ padding: '14px 18px' }}>{getStatusBadge(s.status)}</td>
                  <td style={{ padding: '14px 18px', textAlign: 'right' }}>
                    {s.status === 'scheduled' && (
                      <button
                        onClick={() => startSession(s.id)}
                        style={{
                          background: 'rgba(52, 211, 153, 0.1)',
                          border: '1px solid rgba(52, 211, 153, 0.2)',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          color: '#34d399',
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          fontSize: '13px',
                          fontWeight: 600,
                        }}
                      >
                        <PlayCircle size={14} /> Start
                      </button>
                    )}
                    {s.status === 'active' && (
                      <button
                        onClick={() => closeSession(s.id)}
                        style={{
                          background: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.2)',
                          borderRadius: '6px',
                          padding: '6px 12px',
                          color: '#ef4444',
                          cursor: 'pointer',
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          fontSize: '13px',
                          fontWeight: 600,
                        }}
                      >
                        <StopCircle size={14} /> Close
                      </button>
                    )}
                    {s.status === 'closed' && (
                      <span style={{ fontSize: '12px', color: '#64748b', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                        <CheckCircle2 size={14} /> Completed
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ——— Create Session Modal ——— */}
      {showModal && (
        <div
          onClick={(e) => { if (e.target === e.currentTarget) setShowModal(false); }}
          style={{
            position: 'fixed',
            inset: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.75)',
            backdropFilter: 'blur(8px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 2000,
            padding: '20px',
            animation: 'fadeIn 0.15s ease-out',
          }}
        >
          <div style={{
            backgroundColor: '#1e293b',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '16px',
            padding: '28px',
            width: '460px',
            maxWidth: '90vw',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)',
          }}>
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #34d399 0%, #38bdf8 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <CalendarCheck size={20} color="#ffffff" />
                </div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                  Create New Session
                </h3>
              </div>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  background: 'rgba(255,255,255,0.05)',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '6px',
                  padding: '6px',
                  color: '#94a3b8',
                  cursor: 'pointer',
                }}
              >
                <X size={16} />
              </button>
            </div>

            {/* Form */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Course *</label>
                <select
                  value={formCourse}
                  onChange={(e) => setFormCourse(e.target.value)}
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                >
                  <option value="">Select course...</option>
                  {courses.map((c) => (
                    <option key={c.code} value={c.code}>{c.code} — {c.name}</option>
                  ))}
                </select>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Date *</label>
                  <input
                    type="date"
                    value={formDate}
                    onChange={(e) => setFormDate(e.target.value)}
                    style={{
                      backgroundColor: '#0f172a',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#f8fafc',
                      fontSize: '14px',
                      outline: 'none',
                      colorScheme: 'dark',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Start Time *</label>
                  <input
                    type="time"
                    value={formTime}
                    onChange={(e) => setFormTime(e.target.value)}
                    style={{
                      backgroundColor: '#0f172a',
                      border: '1px solid rgba(255, 255, 255, 0.12)',
                      borderRadius: '8px',
                      padding: '10px 14px',
                      color: '#f8fafc',
                      fontSize: '14px',
                      outline: 'none',
                      colorScheme: 'dark',
                    }}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>
                  Late Threshold <span style={{ color: '#64748b' }}>(minutes)</span>
                </label>
                <input
                  type="number"
                  value={formThreshold}
                  onChange={(e) => setFormThreshold(e.target.value)}
                  min="5"
                  max="60"
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                    width: '120px',
                  }}
                />
              </div>
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', marginTop: '24px' }}>
              <button
                onClick={() => setShowModal(false)}
                style={{
                  flex: 1,
                  backgroundColor: 'rgba(255,255,255,0.08)',
                  color: '#f8fafc',
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '8px',
                  padding: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleCreateSession}
                disabled={!formCourse || !formDate || !formTime}
                style={{
                  flex: 1,
                  backgroundColor: (!formCourse || !formDate || !formTime) ? '#334155' : '#38bdf8',
                  color: (!formCourse || !formDate || !formTime) ? '#94a3b8' : '#0f172a',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  fontWeight: 700,
                  cursor: (!formCourse || !formDate || !formTime) ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  transition: 'all 0.2s ease',
                }}
              >
                Create Session
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>
    </div>
  );
};
