import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Plus,
  Search,
  Edit3,
  Trash2,
  X,
  UserPlus,
  Camera,
  CameraOff,
  Eye,
  ShieldCheck,
  CheckCircle2,
  Users,
  Upload,
  RefreshCw,
  BookOpen,
  Mail,
  Building,
  GraduationCap,
  Sparkles,
} from 'lucide-react';
import axios from 'axios';

interface Student {
  id: string;
  student_id: string;
  full_name: string;
  email: string;
  department: string;
  academic_year: string;
  is_active: boolean;
  embedding_count: number;
  created_at?: string;
  photo_url?: string | null;
}

const API_BASE = 'http://127.0.0.1:8000/api/v1';

const departments = [
  'Computer Science',
  'Information Technology',
  'Electronics & Communication',
  'Mechanical Engineering',
  'Civil Engineering',
  'Data Science & AI',
];

const academicYears = ['1st Year', '2nd Year', '3rd Year', '4th Year', 'Postgraduate'];

// ——— Modal Overlay ———
const ModalOverlay: React.FC<{ children: React.ReactNode; onClose: () => void }> = ({ children, onClose }) => (
  <div
    onClick={(e) => {
      if (e.target === e.currentTarget) onClose();
    }}
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
      overflowY: 'auto',
    }}
  >
    {children}
  </div>
);

export const StudentsPage: React.FC = () => {
  const [students, setStudents] = useState<Student[]>([]);

  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDeptFilter, setSelectedDeptFilter] = useState('ALL');

  // Registration / Edit Modal
  const [showModal, setShowModal] = useState(false);
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  // Detail / Profile Modal
  const [profileStudent, setProfileStudent] = useState<Student | null>(null);

  // Registration Form State
  const [formStudentId, setFormStudentId] = useState('');
  const [formFullName, setFormFullName] = useState('');
  const [formEmail, setFormEmail] = useState('');
  const [formDept, setFormDept] = useState('Computer Science');
  const [formYear, setFormYear] = useState('4th Year');
  const [capturedPhotos, setCapturedPhotos] = useState<string[]>([]);
  const [isCapturing, setIsCapturing] = useState<boolean>(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [dataError, setDataError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Fetch from backend API on mount
  const fetchStudents = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/students`);
      setStudents(Array.isArray(res.data) ? res.data : []);
      setDataError(null);
    } catch {
      setStudents([]);
      setDataError('Unable to load students from PostgreSQL. Check the API connection and sign-in state.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStudents();
  }, [fetchStudents]);

  // Start Camera for photo enrollment
  const startCamera = async () => {
    setCameraError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' },
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsCapturing(true);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Unknown camera error';
      setCameraError(`Camera Error: ${msg}. Check browser permissions.`);
      setIsCapturing(false);
    }
  };

  // Stop Camera
  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setIsCapturing(false);
  };

  // Capture frame from webcam
  const snapPhoto = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas || video.readyState < 2) return;

    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Mirror image for natural selfie photo
    ctx.translate(canvas.width, 0);
    ctx.scale(-1, 1);
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const b64 = canvas.toDataURL('image/jpeg', 0.9);
    setCapturedPhotos((prev) => [...prev, b64].slice(0, 5));
  };

  // File upload handler
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    Array.from(files).forEach((file) => {
      const reader = new FileReader();
      reader.onload = () => {
        if (reader.result && typeof reader.result === 'string') {
          setCapturedPhotos((prev) => [...prev, reader.result as string].slice(0, 5));
        }
      };
      reader.readAsDataURL(file);
    });
  };

  const removePhoto = (index: number) => {
    setCapturedPhotos((prev) => prev.filter((_, i) => i !== index));
  };

  const resetForm = () => {
    stopCamera();
    setFormFullName('');
    setFormStudentId('');
    setFormEmail('');
    setFormDept('Computer Science');
    setFormYear('4th Year');
    setCapturedPhotos([]);
    setEditingStudent(null);
    setCameraError(null);
    setFormError(null);
  };

  const openCreateModal = () => {
    resetForm();
    // Auto-generate next student ID
    const maxNum = students.reduce((max, s) => {
      const match = s.student_id.match(/STU-\d{4}-(\d+)/);
      return match ? Math.max(max, parseInt(match[1])) : max;
    }, 0);
    const nextId = `STU-2026-${String(maxNum + 1).padStart(3, '0')}`;
    setFormStudentId(nextId);
    setFormEmail(`stu.2026.${String(maxNum + 1).padStart(3, '0')}@project.edu`);
    setShowModal(true);
  };

  const openEditModal = (student: Student) => {
    resetForm();
    setEditingStudent(student);
    setFormStudentId(student.student_id);
    setFormFullName(student.full_name);
    setFormEmail(student.email);
    setFormDept(student.department);
    setFormYear(student.academic_year);
    setShowModal(true);
  };

  const handleSubmit = async () => {
    if (!formFullName.trim() || !formStudentId.trim() || !formEmail.trim() || !formDept || !formYear) {
      setFormError('Student ID, name, email, department, and academic year are required.');
      return;
    }

    setIsSubmitting(true);
    setFormError(null);
    try {
      if (editingStudent) {
        const payload = {
          full_name: formFullName,
          email: formEmail,
          department: formDept,
          academic_year: formYear,
        };
        await axios.put(`${API_BASE}/students/${editingStudent.id}`, payload);
      } else {
        const payload = {
          student_id: formStudentId,
          full_name: formFullName,
          email: formEmail,
          department: formDept,
          academic_year: formYear,
          photos_base64: capturedPhotos.length > 0 ? capturedPhotos : undefined,
        };
        await axios.post(`${API_BASE}/students`, payload);
      }

      await fetchStudents();
      setShowModal(false);
      resetForm();
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.detail || error.response?.data?.message || 'Registration could not be saved.')
        : 'Registration could not be saved.';
      setFormError(String(message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await axios.delete(`${API_BASE}/students/${id}`);
      await fetchStudents();
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.detail || error.response?.data?.message || 'Student could not be deleted.')
        : 'Student could not be deleted.';
      setDataError(String(message));
      return;
    }
    setShowDeleteConfirm(null);
    if (profileStudent?.id === id) setProfileStudent(null);
  };

  const toggleStatus = async (student: Student) => {
    const nextStatus = !student.is_active;
    try {
      await axios.put(`${API_BASE}/students/${student.id}`, { is_active: nextStatus });
      await fetchStudents();
    } catch (error) {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.detail || error.response?.data?.message || 'Student status could not be updated.')
        : 'Student status could not be updated.';
      setDataError(String(message));
    }
  };

  // Filter students
  const filteredStudents = students.filter((s) => {
    const matchesSearch =
      s.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.student_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.department.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.email.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesDept = selectedDeptFilter === 'ALL' || s.department === selectedDeptFilter;
    return matchesSearch && matchesDept;
  });

  const totalVectors = students.reduce((acc, s) => acc + (s.embedding_count || 0), 0);
  const activeCount = students.filter((s) => s.is_active).length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '10px' }}>
            Student Management & Biometric Directory
            {isLoading && <RefreshCw size={18} className="spin" color="#38bdf8" />}
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Manage Student Profiles, ArcFace 512D Vector Templates, and Enrolled Rosters
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={fetchStudents}
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
            <RefreshCw size={16} /> Sync Database
          </button>

          <button
            id="register-student-btn"
            onClick={openCreateModal}
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
            <Plus size={18} /> Register New Student
          </button>
        </div>
      </div>

      {dataError && (
        <div role="alert" style={{ backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '10px', padding: '12px 16px', color: '#fca5a5', fontSize: '13px' }}>
          {dataError}
        </div>
      )}

      {/* Aggregate Stats Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(56, 189, 248, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#38bdf8' }}>
            <Users size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Total Registered</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>{students.length} Students</div>
            <div style={{ fontSize: '11px', color: '#34d399' }}>{activeCount} Active Status</div>
          </div>
        </div>

        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(99, 102, 241, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#6366f1' }}>
            <ShieldCheck size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Biometric Templates</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>{totalVectors} Vectors</div>
            <div style={{ fontSize: '11px', color: '#a855f7' }}>AES-256 Encrypted (pgvector)</div>
          </div>
        </div>

        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '18px', display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', backgroundColor: 'rgba(52, 211, 153, 0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#34d399' }}>
            <CheckCircle2 size={22} />
          </div>
          <div>
            <div style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase', fontWeight: 600 }}>Enrollment Quality</div>
            <div style={{ fontSize: '22px', fontWeight: 700, color: '#f8fafc' }}>—</div>
            <div style={{ fontSize: '11px', color: '#38bdf8' }}>Validated per biometric template</div>
          </div>
        </div>
      </div>

      {/* Search & Department Filters Bar */}
      <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap' }}>
        <div style={{
          flex: 1,
          minWidth: '260px',
          backgroundColor: 'rgba(30, 41, 59, 0.65)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '10px',
          padding: '10px 16px',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <Search size={18} color="#94a3b8" />
          <input
            id="student-search"
            type="text"
            placeholder="Search by name, student roll ID, department, or email..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              border: 'none',
              color: '#f8fafc',
              fontSize: '14px',
              outline: 'none',
            }}
          />
          {searchQuery && (
            <button onClick={() => setSearchQuery('')} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer' }}>
              <X size={14} />
            </button>
          )}
        </div>

        <select
          value={selectedDeptFilter}
          onChange={(e) => setSelectedDeptFilter(e.target.value)}
          style={{
            backgroundColor: '#1e293b',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '10px',
            padding: '10px 16px',
            color: '#f8fafc',
            fontSize: '14px',
            outline: 'none',
          }}
        >
          <option value="ALL">All Departments ({students.length})</option>
          {departments.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>

      {/* Students Data Table */}
      <div style={{
        backgroundColor: 'rgba(30, 41, 59, 0.65)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '12px',
        overflow: 'hidden',
      }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ fontSize: '15px', fontWeight: 600, color: '#f8fafc' }}>
            Registered Student Directory ({filteredStudents.length} Profiles)
          </div>
          <div style={{ fontSize: '12px', color: '#94a3b8' }}>
            Click on any student row or <Eye size={12} style={{ display: 'inline', margin: '0 2px' }} /> to view detailed profile
          </div>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#f8fafc', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8', backgroundColor: 'rgba(15, 23, 42, 0.4)' }}>
              <th style={{ padding: '14px 18px' }}>Student ID</th>
              <th style={{ padding: '14px 18px' }}>Full Name</th>
              <th style={{ padding: '14px 18px' }}>Department</th>
              <th style={{ padding: '14px 18px' }}>Academic Year</th>
              <th style={{ padding: '14px 18px' }}>Face Templates</th>
              <th style={{ padding: '14px 18px' }}>Status</th>
              <th style={{ padding: '14px 18px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStudents.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '48px 20px', textAlign: 'center', color: '#94a3b8' }}>
                  <Users size={36} style={{ marginBottom: '10px', opacity: 0.4 }} />
                  <div>No student records found in PostgreSQL.</div>
                  <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                    Click "Register New Student" to enroll the first student.
                  </div>
                  <button onClick={openCreateModal} style={{ marginTop: '14px', backgroundColor: '#38bdf8', color: '#0f172a', border: 'none', borderRadius: '7px', padding: '8px 12px', fontWeight: 700, cursor: 'pointer' }}>
                    Register New Student
                  </button>
                </td>
              </tr>
            ) : (
              filteredStudents.map((s) => (
                <tr
                  key={s.id}
                  style={{
                    borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                    cursor: 'pointer',
                    transition: 'background-color 0.15s ease',
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = 'rgba(56, 189, 248, 0.04)')}
                  onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = 'transparent')}
                  onClick={() => setProfileStudent(s)}
                >
                  <td style={{ padding: '14px 18px', fontWeight: 600, color: '#38bdf8' }}>
                    {s.student_id}
                  </td>
                  <td style={{ padding: '14px 18px' }}>
                    <div style={{ fontWeight: 600, color: '#f8fafc' }}>{s.full_name}</div>
                    <div style={{ fontSize: '12px', color: '#94a3b8' }}>{s.email}</div>
                  </td>
                  <td style={{ padding: '14px 18px', color: '#94a3b8' }}>{s.department}</td>
                  <td style={{ padding: '14px 18px', color: '#94a3b8' }}>{s.academic_year}</td>
                  <td style={{ padding: '14px 18px' }}>
                    <span style={{
                      backgroundColor: s.embedding_count > 0 ? 'rgba(99, 102, 241, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: s.embedding_count > 0 ? '#818cf8' : '#f59e0b',
                      padding: '4px 10px',
                      borderRadius: '6px',
                      fontSize: '12px',
                      fontWeight: 600,
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px',
                    }}>
                      <ShieldCheck size={12} />
                      {s.embedding_count > 0 ? `${s.embedding_count} ArcFace Vectors` : 'No Vectors'}
                    </span>
                  </td>
                  <td style={{ padding: '14px 18px' }} onClick={(e) => e.stopPropagation()}>
                    <button
                      onClick={() => toggleStatus(s)}
                      style={{
                        background: s.is_active ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                        border: `1px solid ${s.is_active ? 'rgba(52, 211, 153, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                        color: s.is_active ? '#34d399' : '#ef4444',
                        fontWeight: 600,
                        cursor: 'pointer',
                        fontSize: '12px',
                        padding: '4px 10px',
                        borderRadius: '20px',
                      }}
                    >
                      {s.is_active ? 'Active' : 'Inactive'}
                    </button>
                  </td>
                  <td style={{ padding: '14px 18px', textAlign: 'right' }} onClick={(e) => e.stopPropagation()}>
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => setProfileStudent(s)}
                        title="View detailed student profile"
                        style={{
                          background: 'rgba(56, 189, 248, 0.1)',
                          border: '1px solid rgba(56, 189, 248, 0.25)',
                          borderRadius: '6px',
                          padding: '6px 10px',
                          color: '#38bdf8',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '4px',
                          fontSize: '12px',
                          fontWeight: 600,
                        }}
                      >
                        <Eye size={14} /> View
                      </button>
                      <button
                        onClick={() => openEditModal(s)}
                        title="Edit profile"
                        style={{
                          background: 'rgba(255, 255, 255, 0.08)',
                          border: '1px solid rgba(255, 255, 255, 0.12)',
                          borderRadius: '6px',
                          padding: '6px 8px',
                          color: '#f8fafc',
                          cursor: 'pointer',
                        }}
                      >
                        <Edit3 size={14} />
                      </button>
                      <button
                        onClick={() => setShowDeleteConfirm(s.id)}
                        title="Delete student"
                        style={{
                          background: 'rgba(239, 68, 68, 0.1)',
                          border: '1px solid rgba(239, 68, 68, 0.2)',
                          borderRadius: '6px',
                          padding: '6px 8px',
                          color: '#ef4444',
                          cursor: 'pointer',
                        }}
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* ——— Registration Modal with Camera Capture & File Upload ——— */}
      {showModal && (
        <ModalOverlay onClose={() => { setShowModal(false); resetForm(); }}>
          <div style={{
            backgroundColor: '#1e293b',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '16px',
            padding: '28px',
            width: '620px',
            maxWidth: '95vw',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)',
          }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}>
                  <UserPlus size={20} color="#ffffff" />
                </div>
                <div>
                  <h3 style={{ margin: 0, fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
                    {editingStudent ? 'Edit Student Profile' : 'Register New Student & Enroll Face'}
                  </h3>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                    Capture live webcam face angles or upload photos for ArcFace 512D embeddings
                  </div>
                </div>
              </div>
              <button
                onClick={() => { setShowModal(false); resetForm(); }}
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

            {formError && (
              <div role="alert" style={{ marginBottom: '16px', backgroundColor: 'rgba(239, 68, 68, 0.12)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '8px', padding: '10px 12px', color: '#fca5a5', fontSize: '13px' }}>
                {formError}
              </div>
            )}

            {/* Profile Fields */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', marginBottom: '20px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Student Roll ID *</label>
                  <input
                    type="text"
                    value={formStudentId}
                    onChange={(e) => setFormStudentId(e.target.value)}
                    placeholder="STU-2026-004"
                    disabled={!!editingStudent}
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
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Full Name *</label>
                  <input
                    type="text"
                    value={formFullName}
                    onChange={(e) => setFormFullName(e.target.value)}
                    placeholder="e.g. David Miller"
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
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Email Address</label>
                <input
                  type="email"
                  value={formEmail}
                  onChange={(e) => setFormEmail(e.target.value)}
                  placeholder="student@project.edu"
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

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
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

                <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                  <label style={{ fontSize: '13px', fontWeight: 600, color: '#94a3b8' }}>Academic Year *</label>
                  <select
                    value={formYear}
                    onChange={(e) => setFormYear(e.target.value)}
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
                    {academicYears.map((y) => (
                      <option key={y} value={y}>{y}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Biometric Face Photo Enrollment Section */}
            <div style={{
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '12px',
              padding: '18px',
              marginBottom: '20px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Camera size={18} color="#38bdf8" />
                  <span style={{ fontSize: '14px', fontWeight: 700, color: '#f8fafc' }}>
                    Facial Photo Enrollment (ArcFace Vector Generation)
                  </span>
                </div>
                <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                  {capturedPhotos.length} / 5 angles captured
                </span>
              </div>

              {cameraError && (
                <div style={{ backgroundColor: 'rgba(239,68,68,0.15)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: '8px', padding: '10px', color: '#ef4444', fontSize: '12px', marginBottom: '12px' }}>
                  {cameraError}
                </div>
              )}

              {/* Live Camera Viewfinder */}
              <div style={{
                position: 'relative',
                backgroundColor: '#000000',
                borderRadius: '10px',
                aspectRatio: '16/9',
                maxHeight: '220px',
                overflow: 'hidden',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                border: '1px solid rgba(56, 189, 248, 0.25)',
                marginBottom: '12px',
              }}>
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  style={{
                    width: '100%',
                    height: '100%',
                    objectFit: 'cover',
                    display: isCapturing ? 'block' : 'none',
                    transform: 'scaleX(-1)',
                  }}
                />
                <canvas ref={canvasRef} style={{ display: 'none' }} />

                {/* Guides when capturing */}
                {isCapturing && (
                  <div style={{
                    position: 'absolute',
                    width: '120px',
                    height: '140px',
                    border: '2px dashed #38bdf8',
                    borderRadius: '16px',
                    pointerEvents: 'none',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}>
                    <span style={{ fontSize: '10px', color: '#38bdf8', backgroundColor: 'rgba(0,0,0,0.6)', padding: '2px 6px', borderRadius: '4px' }}>
                      Align Face Here
                    </span>
                  </div>
                )}

                {!isCapturing && (
                  <div style={{ color: '#94a3b8', fontSize: '13px', textAlign: 'center', padding: '20px' }}>
                    <Camera size={32} style={{ marginBottom: '6px', opacity: 0.5 }} />
                    <div>Live camera is idle. Click "Open Camera" below or upload files.</div>
                  </div>
                )}
              </div>

              {/* Camera / Upload Action Buttons */}
              <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '12px' }}>
                <button
                  type="button"
                  onClick={isCapturing ? stopCamera : startCamera}
                  style={{
                    backgroundColor: isCapturing ? 'rgba(239,68,68,0.2)' : 'rgba(56, 189, 248, 0.15)',
                    color: isCapturing ? '#ef4444' : '#38bdf8',
                    border: `1px solid ${isCapturing ? 'rgba(239,68,68,0.4)' : 'rgba(56, 189, 248, 0.3)'}`,
                    borderRadius: '8px',
                    padding: '8px 14px',
                    fontSize: '13px',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  {isCapturing ? <CameraOff size={16} /> : <Camera size={16} />}
                  {isCapturing ? 'Close Camera' : 'Open Camera'}
                </button>

                {isCapturing && (
                  <button
                    type="button"
                    onClick={snapPhoto}
                    disabled={capturedPhotos.length >= 5}
                    style={{
                      backgroundColor: '#34d399',
                      color: '#0f172a',
                      border: 'none',
                      borderRadius: '8px',
                      padding: '8px 16px',
                      fontSize: '13px',
                      fontWeight: 700,
                      cursor: capturedPhotos.length >= 5 ? 'not-allowed' : 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '6px',
                    }}
                  >
                    <Sparkles size={16} /> Snap Angle Photo ({capturedPhotos.length}/5)
                  </button>
                )}

                <label style={{
                  backgroundColor: 'rgba(255, 255, 255, 0.08)',
                  color: '#f8fafc',
                  border: '1px solid rgba(255, 255, 255, 0.12)',
                  borderRadius: '8px',
                  padding: '8px 14px',
                  fontSize: '13px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}>
                  <Upload size={16} /> Upload Photo(s)
                  <input
                    type="file"
                    accept="image/*"
                    multiple
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                </label>
              </div>

              {/* Thumbnails of Captured Photos */}
              {capturedPhotos.length > 0 && (
                <div>
                  <div style={{ fontSize: '12px', color: '#94a3b8', marginBottom: '6px' }}>Enrolled Angle Crops:</div>
                  <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '4px' }}>
                    {capturedPhotos.map((photo, idx) => (
                      <div key={idx} style={{ position: 'relative', width: '70px', height: '70px', borderRadius: '8px', overflow: 'hidden', border: '2px solid #34d399', flexShrink: 0 }}>
                        <img src={photo} alt={`Crop ${idx + 1}`} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        <button
                          onClick={() => removePhoto(idx)}
                          style={{
                            position: 'absolute',
                            top: '2px',
                            right: '2px',
                            backgroundColor: 'rgba(0,0,0,0.7)',
                            border: 'none',
                            color: '#ef4444',
                            borderRadius: '50%',
                            width: '18px',
                            height: '18px',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            padding: 0,
                          }}
                        >
                          <X size={12} />
                        </button>
                        <div style={{ position: 'absolute', bottom: '0', insetInline: 0, backgroundColor: 'rgba(15,23,42,0.8)', fontSize: '9px', textAlign: 'center', color: '#34d399' }}>
                          512D Vec
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                type="button"
                onClick={() => { setShowModal(false); resetForm(); }}
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
                type="button"
                onClick={handleSubmit}
                disabled={isSubmitting || !formFullName.trim() || !formStudentId.trim()}
                style={{
                  flex: 1,
                  backgroundColor: (!formFullName.trim() || !formStudentId.trim()) ? '#334155' : '#38bdf8',
                  color: (!formFullName.trim() || !formStudentId.trim()) ? '#94a3b8' : '#0f172a',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  fontWeight: 700,
                  cursor: (!formFullName.trim() || !formStudentId.trim() || isSubmitting) ? 'not-allowed' : 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px',
                }}
              >
                {isSubmitting && <RefreshCw size={16} className="spin" />}
                {editingStudent ? 'Save Profile Changes' : 'Register & Save to Database'}
              </button>
            </div>
          </div>
        </ModalOverlay>
      )}

      {/* ——— Detailed Student Profile View Modal ——— */}
      {profileStudent && (
        <ModalOverlay onClose={() => setProfileStudent(null)}>
          <div style={{
            backgroundColor: '#1e293b',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            borderRadius: '16px',
            padding: '28px',
            width: '580px',
            maxWidth: '95vw',
            maxHeight: '90vh',
            overflowY: 'auto',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)',
          }}>
            {/* Header / Avatar */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '20px' }}>
              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                <div style={{
                  width: '64px',
                  height: '64px',
                  borderRadius: '14px',
                  background: profileStudent.photo_url
                    ? `url(${profileStudent.photo_url}) center/cover`
                    : 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '22px',
                  fontWeight: 700,
                  color: '#ffffff',
                  border: '2px solid rgba(56, 189, 248, 0.4)',
                }}>
                  {!profileStudent.photo_url && profileStudent.full_name.charAt(0)}
                </div>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: '#f8fafc' }}>
                      {profileStudent.full_name}
                    </h2>
                    <span style={{
                      backgroundColor: profileStudent.is_active ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                      color: profileStudent.is_active ? '#34d399' : '#ef4444',
                      padding: '2px 8px',
                      borderRadius: '12px',
                      fontSize: '11px',
                      fontWeight: 600,
                    }}>
                      {profileStudent.is_active ? 'Active Profile' : 'Inactive'}
                    </span>
                  </div>
                  <div style={{ fontSize: '13px', color: '#38bdf8', fontWeight: 600, marginTop: '2px' }}>
                    {profileStudent.student_id}
                  </div>
                  <div style={{ fontSize: '12px', color: '#94a3b8' }}>
                    Registered: {profileStudent.created_at ? new Date(profileStudent.created_at).toLocaleDateString() : 'Active Roster'}
                  </div>
                </div>
              </div>

              <button
                onClick={() => setProfileStudent(null)}
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

            {/* Info Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '20px' }}>
              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.5)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#94a3b8' }}>
                  <Building size={14} color="#38bdf8" /> Department
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>
                  {profileStudent.department}
                </div>
              </div>

              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.5)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#94a3b8' }}>
                  <GraduationCap size={14} color="#a855f7" /> Academic Year
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>
                  {profileStudent.academic_year}
                </div>
              </div>

              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.5)', padding: '12px 16px', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)', gridColumn: 'span 2' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: '#94a3b8' }}>
                  <Mail size={14} color="#34d399" /> Institutional Email
                </div>
                <div style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginTop: '4px' }}>
                  {profileStudent.email}
                </div>
              </div>
            </div>

            {/* Biometric Identity Security Card */}
            <div style={{
              backgroundColor: 'rgba(15, 23, 42, 0.7)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              borderRadius: '10px',
              padding: '16px',
              marginBottom: '20px',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                <div style={{ fontSize: '13px', fontWeight: 700, color: '#818cf8', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <ShieldCheck size={16} /> ArcFace 512D Biometric Embeddings
                </div>
                <span style={{ fontSize: '11px', color: '#34d399', backgroundColor: 'rgba(52,211,153,0.15)', padding: '2px 8px', borderRadius: '10px', fontWeight: 600 }}>
                  pgvector HNSW Indexed
                </span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '12px' }}>
                <div style={{ color: '#94a3b8' }}>
                  Enrolled Templates: <strong style={{ color: '#f8fafc' }}>{profileStudent.embedding_count} Vectors</strong>
                </div>
                <div style={{ color: '#94a3b8' }}>
                  Cosine Match Threshold: <strong style={{ color: '#38bdf8' }}>τ(Q) = 0.543</strong>
                </div>
                <div style={{ color: '#94a3b8' }}>
                  Raw Image Storage: <strong style={{ color: '#34d399' }}>Zero-Retention (GDPR)</strong>
                </div>
                <div style={{ color: '#94a3b8' }}>
                  Vector Encryption: <strong style={{ color: '#a855f7' }}>AES-256 GCM</strong>
                </div>
              </div>
            </div>

            {/* Attendance details are sourced from the attendance API, not placeholder records. */}
            <div style={{ marginBottom: '20px' }}>
              <div style={{ fontSize: '14px', fontWeight: 600, color: '#f8fafc', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <BookOpen size={16} color="#38bdf8" /> Attendance History
              </div>
              <div style={{ backgroundColor: 'rgba(15, 23, 42, 0.4)', border: '1px solid rgba(255,255,255,0.06)', borderRadius: '8px', padding: '12px', color: '#94a3b8', fontSize: '12px' }}>
                Open an attendance session to view verified records. No attendance statistics are fabricated in this profile.
              </div>
            </div>

            {/* Footer actions */}
            <div style={{ display: 'flex', gap: '10px' }}>
              <button
                onClick={() => {
                  const toEdit = profileStudent;
                  setProfileStudent(null);
                  openEditModal(toEdit);
                }}
                style={{
                  flex: 1,
                  backgroundColor: '#38bdf8',
                  color: '#0f172a',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '10px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                }}
              >
                <Edit3 size={16} /> Edit Student
              </button>

              <button
                onClick={() => {
                  const id = profileStudent.id;
                  setProfileStudent(null);
                  setShowDeleteConfirm(id);
                }}
                style={{
                  backgroundColor: 'rgba(239, 68, 68, 0.15)',
                  color: '#ef4444',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px',
                  padding: '10px 16px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  fontSize: '13px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                }}
              >
                <Trash2 size={16} /> Delete
              </button>
            </div>
          </div>
        </ModalOverlay>
      )}

      {/* ——— Delete Confirmation Modal ——— */}
      {showDeleteConfirm && (
        <ModalOverlay onClose={() => setShowDeleteConfirm(null)}>
          <div style={{
            backgroundColor: '#1e293b',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '16px',
            padding: '28px',
            width: '420px',
            maxWidth: '90vw',
            boxShadow: '0 25px 60px rgba(0, 0, 0, 0.6)',
            textAlign: 'center',
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}>
              <Trash2 size={24} color="#ef4444" />
            </div>
            <h3 style={{ margin: '0 0 8px', fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>
              Delete Student Profile?
            </h3>
            <p style={{ margin: '0 0 24px', fontSize: '14px', color: '#94a3b8' }}>
              This will permanently delete this student profile and remove all associated 512D ArcFace facial embeddings from PostgreSQL.
            </p>
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                onClick={() => setShowDeleteConfirm(null)}
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
                onClick={() => handleDelete(showDeleteConfirm)}
                style={{
                  flex: 1,
                  backgroundColor: '#ef4444',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '12px',
                  fontWeight: 700,
                  cursor: 'pointer',
                  fontSize: '14px',
                }}
              >
                Delete Student
              </button>
            </div>
          </div>
        </ModalOverlay>
      )}

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .spin {
          animation: spin 1s linear infinite;
        }
      `}</style>
    </div>
  );
};
