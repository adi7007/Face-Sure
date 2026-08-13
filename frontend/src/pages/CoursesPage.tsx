import { Plus } from 'lucide-react';

export const CoursesPage: React.FC = () => {
  const courses = [
    { code: 'CS-401', name: 'Deep Learning & Computer Vision', dept: 'Computer Science', students: 45 },
    { code: 'CS-405', name: 'Advanced Machine Learning', dept: 'Computer Science', students: 38 },
    { code: 'IT-302', name: 'Database Systems & Vector Search', dept: 'Information Technology', students: 50 },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
            Course Management
          </h1>
          <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
            Manage Courses, Instructors, and Student Rosters
          </p>
        </div>
        <button style={{ backgroundColor: '#38bdf8', color: '#0f172a', border: 'none', borderRadius: '8px', padding: '10px 18px', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Plus size={18} /> Create Course
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        {courses.map((c) => (
          <div key={c.code} style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '20px' }}>
            <div style={{ fontSize: '14px', fontWeight: 700, color: '#38bdf8' }}>{c.code}</div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc', margin: '4px 0 8px 0' }}>{c.name}</div>
            <div style={{ fontSize: '13px', color: '#94a3b8' }}>Department: {c.dept}</div>
            <div style={{ fontSize: '13px', color: '#34d399', marginTop: '12px', fontWeight: 600 }}>Enrolled: {c.students} Students</div>
          </div>
        ))}
      </div>
    </div>
  );
};
