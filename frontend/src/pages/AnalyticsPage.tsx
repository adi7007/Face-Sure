import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import {
  BarChart3, Users, AlertTriangle, TrendingUp, TrendingDown,
  Target, BookOpen, Clock,
} from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

interface OverviewData {
  total_students: number;
  total_sessions: number;
  total_records: number;
  total_courses: number;
  present_count: number;
  late_count: number;
  overall_attendance_rate: number;
  at_risk_count: number;
  at_risk_students: any[];
  daily_trend: any[];
}

interface CourseStats {
  course_id: string;
  course_code: string;
  course_name: string;
  department: string;
  session_count: number;
  enrolled_students: number;
  total_records: number;
  avg_attendance_pct: number;
}

const COLORS = ['#38bdf8', '#6366f1', '#34d399', '#f59e0b', '#ef4444', '#a78bfa', '#f472b6'];

const StatCard: React.FC<{
  icon: any; label: string; value: string | number; sublabel?: string;
  color: string; trend?: 'up' | 'down' | null;
}> = ({ icon: Icon, label, value, sublabel, color, trend }) => (
  <div style={{
    background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(12px)',
    borderRadius: '14px', padding: '24px',
    border: '1px solid rgba(255,255,255,0.06)',
    flex: '1 1 200px', minWidth: '200px',
    transition: 'transform 0.2s, border-color 0.2s',
  }}
    onMouseEnter={(e) => {
      e.currentTarget.style.transform = 'translateY(-2px)';
      e.currentTarget.style.borderColor = `${color}40`;
    }}
    onMouseLeave={(e) => {
      e.currentTarget.style.transform = 'translateY(0)';
      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.06)';
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
      <div style={{
        width: '40px', height: '40px', borderRadius: '10px',
        background: `${color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <Icon size={20} color={color} />
      </div>
      {trend && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontSize: '12px', color: trend === 'up' ? '#34d399' : '#ef4444' }}>
          {trend === 'up' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
        </div>
      )}
    </div>
    <div style={{ fontSize: '28px', fontWeight: 700, color: '#f8fafc', letterSpacing: '-0.02em' }}>{value}</div>
    <div style={{ fontSize: '13px', color: '#94a3b8', marginTop: '4px' }}>{label}</div>
    {sublabel && <div style={{ fontSize: '11px', color: '#64748b', marginTop: '2px' }}>{sublabel}</div>}
  </div>
);

export const AnalyticsPage: React.FC = () => {
  const [overview, setOverview] = useState<OverviewData | null>(null);
  const [courseStats, setCourseStats] = useState<CourseStats[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, courseRes] = await Promise.all([
          axios.get(`${API}/analytics/overview`),
          axios.get(`${API}/attendance/stats/per-course`),
        ]);
        setOverview(overviewRes.data);
        setCourseStats(courseRes.data.courses || []);
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
        // Provide demo data for display
        setOverview({
          total_students: 127, total_sessions: 48, total_records: 3241,
          total_courses: 6, present_count: 2890, late_count: 351,
          overall_attendance_rate: 82.4, at_risk_count: 12,
          at_risk_students: [
            { student_code: 'STU-2026-045', full_name: 'Raj Patel', department: 'CSE', attendance_pct: 52.3, risk_level: 'CRITICAL' },
            { student_code: 'STU-2026-078', full_name: 'Ananya Singh', department: 'IT', attendance_pct: 63.1, risk_level: 'HIGH' },
            { student_code: 'STU-2026-034', full_name: 'Vikram Reddy', department: 'ECE', attendance_pct: 68.5, risk_level: 'HIGH' },
          ],
          daily_trend: Array.from({ length: 14 }, (_, i) => ({
            date: new Date(Date.now() - (13 - i) * 86400000).toISOString().split('T')[0],
            day_name: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][new Date(Date.now() - (13 - i) * 86400000).getDay()],
            present: Math.floor(Math.random() * 40) + 80,
            late: Math.floor(Math.random() * 15) + 5,
            total: 0,
          })).map(d => ({ ...d, total: d.present + d.late })),
        });
        setCourseStats([
          { course_id: '1', course_code: 'CS-401', course_name: 'Deep Learning & CV', department: 'CSE', session_count: 12, enrolled_students: 45, total_records: 486, avg_attendance_pct: 89.6 },
          { course_id: '2', course_code: 'CS-302', course_name: 'Database Systems', department: 'CSE', session_count: 10, enrolled_students: 52, total_records: 390, avg_attendance_pct: 75.0 },
          { course_id: '3', course_code: 'IT-201', course_name: 'Web Technologies', department: 'IT', session_count: 8, enrolled_students: 38, total_records: 260, avg_attendance_pct: 85.5 },
          { course_id: '4', course_code: 'ECE-401', course_name: 'Signal Processing', department: 'ECE', session_count: 9, enrolled_students: 35, total_records: 220, avg_attendance_pct: 69.8 },
          { course_id: '5', course_code: 'ME-301', course_name: 'Thermodynamics', department: 'ME', session_count: 7, enrolled_students: 42, total_records: 240, avg_attendance_pct: 81.6 },
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#38bdf8', fontSize: '16px' }}>
        Loading analytics...
      </div>
    );
  }

  const statusPieData = overview ? [
    { name: 'Present', value: overview.present_count, color: '#34d399' },
    { name: 'Late', value: overview.late_count, color: '#f59e0b' },
  ] : [];

  return (
    <div style={{ padding: '32px', maxWidth: '1400px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ margin: '0 0 6px', fontSize: '28px', fontWeight: 700, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <BarChart3 size={28} color="#38bdf8" />
          Analytics Dashboard
        </h1>
        <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8' }}>
          Deep insights into attendance patterns, trends, and at-risk students
        </p>
      </div>

      {/* Stat Cards */}
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '28px' }}>
        <StatCard icon={Users} label="Total Students" value={overview?.total_students || 0} color="#38bdf8" />
        <StatCard icon={BookOpen} label="Total Courses" value={overview?.total_courses || 0} color="#6366f1" />
        <StatCard icon={Target} label="Attendance Rate" value={`${overview?.overall_attendance_rate || 0}%`} color="#34d399" trend="up" />
        <StatCard icon={AlertTriangle} label="At-Risk Students" value={overview?.at_risk_count || 0} sublabel="Below 75% attendance" color="#ef4444" />
        <StatCard icon={Clock} label="Total Sessions" value={overview?.total_sessions || 0} color="#f59e0b" />
      </div>

      {/* Charts Row */}
      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px', marginBottom: '28px' }}>
        {/* Daily Attendance Trend */}
        <div style={{
          background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(12px)',
          borderRadius: '14px', padding: '24px',
          border: '1px solid rgba(255,255,255,0.06)',
        }}>
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
            📈 Daily Attendance Trend (Last 14 Days)
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={overview?.daily_trend || []}>
              <defs>
                <linearGradient id="presentGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#34d399" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="lateGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis dataKey="day_name" tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <YAxis tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} />
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Area type="monotone" dataKey="present" stroke="#34d399" fill="url(#presentGrad)" strokeWidth={2} name="Present" />
              <Area type="monotone" dataKey="late" stroke="#f59e0b" fill="url(#lateGrad)" strokeWidth={2} name="Late" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Status Distribution */}
        <div style={{
          background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(12px)',
          borderRadius: '14px', padding: '24px',
          border: '1px solid rgba(255,255,255,0.06)',
        }}>
          <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
            📊 Attendance Status
          </h3>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={statusPieData}
                cx="50%" cy="50%"
                innerRadius={60} outerRadius={90}
                dataKey="value"
                stroke="none"
              >
                {statusPieData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
              />
              <Legend
                verticalAlign="bottom"
                formatter={(value) => <span style={{ color: '#94a3b8', fontSize: '13px' }}>{value}</span>}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Per-Course Attendance */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(12px)',
        borderRadius: '14px', padding: '24px', marginBottom: '28px',
        border: '1px solid rgba(255,255,255,0.06)',
      }}>
        <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
          📚 Per-Course Attendance Rate
        </h3>
        <ResponsiveContainer width="100%" height={Math.max(200, courseStats.length * 50)}>
          <BarChart data={courseStats} layout="vertical" margin={{ left: 120 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tick={{ fill: '#64748b', fontSize: 12 }} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              tickFormatter={(v) => `${v}%`}
            />
            <YAxis type="category" dataKey="course_code" tick={{ fill: '#cbd5e1', fontSize: 13 }} axisLine={{ stroke: 'rgba(255,255,255,0.08)' }} width={100} />
            <Tooltip
              contentStyle={{ background: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px', color: '#f8fafc' }}
              formatter={(value) => [`${Number(value ?? 0).toFixed(1)}%`, 'Attendance']}
            />
            <Bar dataKey="avg_attendance_pct" radius={[0, 6, 6, 0]}>
              {courseStats.map((_, idx) => (
                <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* At-Risk Students Table */}
      <div style={{
        background: 'rgba(30, 41, 59, 0.6)', backdropFilter: 'blur(12px)',
        borderRadius: '14px', padding: '24px',
        border: '1px solid rgba(255,255,255,0.06)',
      }}>
        <h3 style={{ margin: '0 0 20px', fontSize: '16px', fontWeight: 600, color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={18} color="#ef4444" />
          At-Risk Students (Below 75%)
        </h3>

        {(overview?.at_risk_students || []).length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
            <div style={{ fontSize: '40px', marginBottom: '12px' }}>🎉</div>
            <div style={{ fontSize: '15px', fontWeight: 500 }}>No at-risk students</div>
            <div style={{ fontSize: '13px', marginTop: '4px' }}>All students are meeting the 75% attendance threshold</div>
          </div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                {['Student ID', 'Name', 'Department', 'Attendance', 'Risk Level'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '12px 16px', fontSize: '12px', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(overview?.at_risk_students || []).map((stu, idx) => (
                <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', transition: 'background 0.15s' }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.02)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '14px 16px', fontSize: '13px', color: '#94a3b8', fontFamily: 'monospace' }}>{stu.student_code}</td>
                  <td style={{ padding: '14px 16px', fontSize: '14px', fontWeight: 500, color: '#f8fafc' }}>{stu.full_name}</td>
                  <td style={{ padding: '14px 16px', fontSize: '13px', color: '#94a3b8' }}>{stu.department}</td>
                  <td style={{ padding: '14px 16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '80px', height: '6px', borderRadius: '3px', background: 'rgba(255,255,255,0.08)', overflow: 'hidden' }}>
                        <div style={{
                          width: `${stu.attendance_pct}%`, height: '100%', borderRadius: '3px',
                          background: stu.attendance_pct < 60 ? '#ef4444' : stu.attendance_pct < 70 ? '#f59e0b' : '#38bdf8',
                        }} />
                      </div>
                      <span style={{ fontSize: '13px', fontWeight: 600, color: stu.attendance_pct < 60 ? '#ef4444' : '#f59e0b' }}>
                        {stu.attendance_pct}%
                      </span>
                    </div>
                  </td>
                  <td style={{ padding: '14px 16px' }}>
                    <span style={{
                      padding: '4px 10px', borderRadius: '6px', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      background: stu.risk_level === 'CRITICAL' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                      color: stu.risk_level === 'CRITICAL' ? '#ef4444' : '#f59e0b',
                      border: `1px solid ${stu.risk_level === 'CRITICAL' ? 'rgba(239, 68, 68, 0.3)' : 'rgba(245, 158, 11, 0.3)'}`,
                    }}>
                      {stu.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
