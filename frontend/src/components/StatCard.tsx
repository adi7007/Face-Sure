import React from 'react';
import type { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  color?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  color = '#38bdf8'
}) => {
  return (
    <div style={{
      backgroundColor: 'rgba(30, 41, 59, 0.65)',
      backdropFilter: 'blur(12px)',
      border: '1px solid rgba(255, 255, 255, 0.08)',
      borderRadius: '12px',
      padding: '20px',
      display: 'flex',
      alignItems: 'center',
      gap: '16px'
    }}>
      <div style={{
        width: '48px',
        height: '48px',
        borderRadius: '10px',
        backgroundColor: `${color}15`,
        border: `1px solid ${color}30`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: color
      }}>
        <Icon size={24} />
      </div>

      <div>
        <div style={{ fontSize: '12px', fontWeight: 500, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
          {title}
        </div>
        <div style={{ fontSize: '24px', fontWeight: 700, color: '#f8fafc', margin: '4px 0 2px 0' }}>
          {value}
        </div>
        {subtitle && (
          <div style={{ fontSize: '12px', color: color, fontWeight: 500 }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
