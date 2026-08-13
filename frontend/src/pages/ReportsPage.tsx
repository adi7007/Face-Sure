import React from 'react';
import { FileSpreadsheet, Download } from 'lucide-react';

export const ReportsPage: React.FC = () => {
  const handleDownloadCSV = () => {
    window.open('http://127.0.0.1:8000/api/v1/reports/export-csv', '_blank');
  };

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

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
        <div style={{ backgroundColor: 'rgba(30, 41, 59, 0.65)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '12px', padding: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <FileSpreadsheet size={36} color="#34d399" />
          <div>
            <div style={{ fontSize: '18px', fontWeight: 700, color: '#f8fafc' }}>Export CSV Report</div>
            <p style={{ fontSize: '13px', color: '#94a3b8', margin: '4px 0 0 0' }}>Raw attendance records with student IDs, timestamps, and multi-factor QMF telemetry.</p>
          </div>
          <button 
            onClick={handleDownloadCSV}
            style={{
              backgroundColor: 'rgba(52, 211, 153, 0.15)',
              color: '#34d399',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              padding: '12px',
              borderRadius: '8px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            <Download size={18} /> Download CSV Telemetry Report
          </button>
        </div>
      </div>
    </div>
  );
};
