import React from 'react';
import { FileSpreadsheet, Download } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#f8fafc' }}>
          Reports & Export
        </h1>
        <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#94a3b8' }}>
          Generate Course Attendance Summaries and Export CSV / Excel / PDF Files
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <FileSpreadsheet size={32} color="#34d399" />
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>Export CSV Report</div>
          <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0 }}>Raw attendance records with timestamps and QMF confidence metrics.</p>
          <button style={{ backgroundColor: 'rgba(52, 211, 153, 0.15)', color: '#34d399', border: '1px solid rgba(52, 211, 153, 0.3)', padding: '10px', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Download size={16} /> Download CSV
          </button>
        </div>

        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <FileSpreadsheet size={32} color="#38bdf8" />
          <div style={{ fontSize: '16px', fontWeight: 700, color: '#f8fafc' }}>Export Excel Spreadsheet</div>
          <p style={{ fontSize: '13px', color: '#94a3b8', margin: 0 }}>Formatted attendance sheet with student summaries and statistics.</p>
          <button style={{ backgroundColor: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', border: '1px solid rgba(56, 189, 248, 0.3)', padding: '10px', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Download size={16} /> Download Excel
          </button>
        </div>
      </div>
    </div>
  );
};
