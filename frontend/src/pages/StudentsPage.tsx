import { Plus } from 'lucide-react';

export const StudentsPage: React.FC = () => {
  const mockStudents = [
    { id: '1', studentId: 'STU-2026-001', name: 'Alex Johnson', dept: 'Computer Science', year: '4th Year', embeddings: 5 },
    { id: '2', studentId: 'STU-2026-002', name: 'Beatrix Kiddo', dept: 'Information Technology', year: '3rd Year', embeddings: 4 },
    { id: '3', studentId: 'STU-2026-003', name: 'Charlie Chen', dept: 'Computer Science', year: '4th Year', embeddings: 5 },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
            Student Management & Enrollment
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Manage Student Profiles and Biometric Facial Vector Registrations
          </p>
        </div>

        <button style={{
          backgroundColor: '#38bdf8',
          color: '#0f172a',
          border: 'none',
          borderRadius: '8px',
          padding: '10px 18px',
          fontWeight: 700,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <Plus size={18} /> Register New Student
        </button>
      </div>

      {/* Table Card */}
      <div style={{
        backgroundColor: 'rgba(30, 41, 59, 0.65)',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        borderRadius: '12px',
        padding: '20px'
      }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', color: '#f8fafc', fontSize: '14px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.1)', textAlign: 'left', color: '#94a3b8' }}>
              <th style={{ padding: '12px' }}>Student ID</th>
              <th style={{ padding: '12px' }}>Full Name</th>
              <th style={{ padding: '12px' }}>Department</th>
              <th style={{ padding: '12px' }}>Academic Year</th>
              <th style={{ padding: '12px' }}>ArcFace Templates</th>
              <th style={{ padding: '12px' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {mockStudents.map((s) => (
              <tr key={s.id} style={{ borderBottom: '1px solid rgba(255, 255, 255, 0.05)' }}>
                <td style={{ padding: '12px', fontWeight: 600, color: '#38bdf8' }}>{s.studentId}</td>
                <td style={{ padding: '12px' }}>{s.name}</td>
                <td style={{ padding: '12px', color: '#94a3b8' }}>{s.dept}</td>
                <td style={{ padding: '12px', color: '#94a3b8' }}>{s.year}</td>
                <td style={{ padding: '12px' }}>
                  <span style={{ backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#6366f1', padding: '4px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 600 }}>
                    {s.embeddings} Vectors (AES-256)
                  </span>
                </td>
                <td style={{ padding: '12px' }}>
                  <span style={{ color: '#34d399', fontWeight: 600 }}>Active</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
