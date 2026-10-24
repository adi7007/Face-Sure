import React, { useState, useEffect, useCallback } from 'react';
import { Plus, BookOpen, Users, Trash2, X, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface Course {
  id?: string;
  course_code: string;
  course_name: string;
  department: string;
  enrolled_students_count?: number;
}

const API_BASE = 'http://127.0.0.1:8000/api/v1';
const STORAGE_KEY = 'faceattend_courses_cache';

const defaultFallbackCourses: Course[] = [
  { course_code: 'CS-401', course_name: 'Deep Learning & Computer Vision', department: 'Computer Science', enrolled_students_count: 45 },
  { course_code: 'CS-405', course_name: 'Advanced Machine Learning', department: 'Computer Science', enrolled_students_count: 38 },
  { course_code: 'IT-302', course_name: 'Database Systems & Vector Search', department: 'Information Technology', enrolled_students_count: 50 },
];

const departments = [
  'Computer Science',
  'Information Technology',
  'Electronics & Communication',
  'Mechanical Engineering',
  'Data Science & AI',
];

export const CoursesPage: React.FC = () => {
  const [courses, setCourses] = useState<Course[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch {
      // fallback
    }
    return defaultFallbackCourses;
  });

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showModal, setShowModal] = useState(false);
  const [formCode, setFormCode] = useState('');
  const [formName, setFormName] = useState('');
  const [formDept, setFormDept] = useState('Computer Science');

  // Save to localStorage on change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(courses));
    } catch {
      // ignore
    }
  }, [courses]);

  // Fetch from backend API
  const fetchCourses = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/courses`);
      if (res.data && Array.isArray(res.data) && res.data.length > 0) {
        setCourses(res.data);
      }
    } catch {
      // fallback to local cache
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  const handleCreate = async () => {
    if (!formCode.trim() || !formName.trim()) return;

    const payload = {
      course_code: formCode.trim().toUpperCase(),
      course_name: formName.trim(),
      department: formDept,
    };

    try {
      const res = await axios.post(`${API_BASE}/courses`, payload);
      if (res.data) {
        setCourses((prev) => [...prev, res.data]);
      }
    } catch {
      // Local fallback
      const newCourse: Course = {
        id: `local-${Date.now()}`,
        course_code: payload.course_code,
        course_name: payload.course_name,
        department: payload.department,
        enrolled_students_count: 0,
      };
      setCourses((prev) => [...prev, newCourse]);
    }

    setShowModal(false);
    setFormCode('');
    setFormName('');
  };

  const handleDelete = async (courseCode: string, id?: string) => {
    if (id && !id.startsWith('local-')) {
      try {
        await axios.delete(`${API_BASE}/courses/${id}`);
      } catch {
        // ignore
      }
    }
    setCourses((prev) => prev.filter((c) => c.course_code !== courseCode));
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            Course Management & Rosters
            {isLoading && <RefreshCw size={18} className="spin" color="#38bdf8" />}
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Manage Courses, Enrolled Student Rosters, and Faculty Allocations
          </p>
        </div>

        <button
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
          }}
        >
          <Plus size={18} /> Create New Course
        </button>
      </div>

      {/* Courses Cards Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
        {courses.map((c) => (
          <div
            key={c.course_code}
            style={{
              backgroundColor: 'rgba(30, 41, 59, 0.65)',
              backdropFilter: 'blur(12px)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '24px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              gap: '16px',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                <span style={{
                  backgroundColor: 'rgba(56, 189, 248, 0.15)',
                  color: '#38bdf8',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '13px',
                  fontWeight: 700,
                }}>
                  {c.course_code}
                </span>

                <button
                  onClick={() => handleDelete(c.course_code, c.id)}
                  title="Delete Course"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: '#64748b',
                    cursor: 'pointer',
                    padding: '4px',
                  }}
                >
                  <Trash2 size={16} />
                </button>
              </div>

              <div style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', marginBottom: '6px' }}>
                {c.course_name}
              </div>

              <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                Department: {c.department}
              </div>
            </div>

            <div style={{
              backgroundColor: 'rgba(15, 23, 42, 0.5)',
              borderRadius: '8px',
              padding: '12px',
              border: '1px solid rgba(255, 255, 255, 0.04)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: '#94a3b8' }}>
                <Users size={16} color="#38bdf8" />
                <span>Enrolled Students:</span>
              </div>
              <span style={{ fontSize: '14px', fontWeight: 700, color: '#34d399' }}>
                {c.enrolled_students_count ?? 3} Active
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Create Course Modal */}
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '36px',
                  height: '36px',
                  borderRadius: '8px',
                  background: 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <BookOpen size={20} color="#ffffff" />
                </div>
                <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                  Create New Course
                </h3>
              </div>
              <button
                onClick={() => setShowModal(false)}
                style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
              >
                <X size={18} />
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '24px' }}>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Course Code *</label>
                <input
                  type="text"
                  placeholder="e.g. CS-410"
                  value={formCode}
                  onChange={(e) => setFormCode(e.target.value)}
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Course Name *</label>
                <input
                  type="text"
                  placeholder="e.g. Generative AI & Neural Networks"
                  value={formName}
                  onChange={(e) => setFormName(e.target.value)}
                  style={{
                    backgroundColor: '#0f172a',
                    border: '1px solid rgba(255, 255, 255, 0.12)',
                    borderRadius: '8px',
                    padding: '10px 14px',
                    color: '#f8fafc',
                    fontSize: '14px',
                    outline: 'none',
                  }}
                />
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Department *</label>
                <select
                  value={formDept}
                  onChange={(e) => setFormDept(e.target.value)}
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
                  {departments.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '12px' }}>
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
                onClick={handleCreate}
                disabled={!formCode.trim() || !formName.trim()}
                style={{
                  flex: 1,
                  backgroundColor: (!formCode.trim() || !formName.trim()) ? '#334155' : '#38bdf8',
                  color: (!formCode.trim() || !formName.trim()) ? '#94a3b8' : '#0f172a',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  fontWeight: 700,
                  cursor: (!formCode.trim() || !formName.trim()) ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                }}
              >
                Create Course
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
