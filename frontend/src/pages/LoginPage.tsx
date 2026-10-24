import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { ShieldCheck, Eye, EyeOff, LogIn, AlertCircle, Loader2 } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [usernameOrEmail, setUsernameOrEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      await login(usernameOrEmail, password);
      navigate('/', { replace: true });
    } catch (err: any) {
      console.error('Login error:', err);
      const msg = err.response?.data?.detail
        || err.response?.data?.message
        || err.message
        || 'Invalid credentials. Please try again.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 40%, #0f172a 100%)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Animated Background Orbs */}
      <div style={{
        position: 'absolute', width: '500px', height: '500px', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(56, 189, 248, 0.15) 0%, transparent 70%)',
        top: '-150px', right: '-100px', animation: 'float 8s ease-in-out infinite',
      }} />
      <div style={{
        position: 'absolute', width: '400px', height: '400px', borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 70%)',
        bottom: '-100px', left: '-80px', animation: 'float 10s ease-in-out infinite reverse',
      }} />

      {/* Login Card */}
      <div style={{
        width: '100%', maxWidth: '440px', padding: '48px 40px',
        background: 'rgba(30, 41, 59, 0.85)',
        backdropFilter: 'blur(24px)', WebkitBackdropFilter: 'blur(24px)',
        borderRadius: '20px',
        border: '1px solid rgba(255, 255, 255, 0.08)',
        boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.6), 0 0 60px rgba(56, 189, 248, 0.06)',
        position: 'relative', zIndex: 1,
      }}>
        {/* Brand Header */}
        <div style={{ textAlign: 'center', marginBottom: '36px' }}>
          <div style={{
            width: '56px', height: '56px', borderRadius: '14px',
            background: 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
            display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
            marginBottom: '16px',
            boxShadow: '0 8px 24px rgba(56, 189, 248, 0.25)',
          }}>
            <ShieldCheck size={30} color="#fff" />
          </div>
          <h1 style={{
            margin: '0 0 6px', fontSize: '26px', fontWeight: 700, color: '#f8fafc',
            letterSpacing: '-0.02em',
          }}>
            FaceAttend
          </h1>
          <p style={{ margin: 0, fontSize: '14px', color: '#94a3b8', fontWeight: 500 }}>
            AI-Powered Attendance Management
          </p>
        </div>

        {/* Error Message */}
        {error && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: '10px',
            padding: '12px 16px', borderRadius: '10px', marginBottom: '20px',
            background: 'rgba(239, 68, 68, 0.12)',
            border: '1px solid rgba(239, 68, 68, 0.25)',
            color: '#fca5a5', fontSize: '13px',
          }}>
            <AlertCircle size={16} style={{ flexShrink: 0 }} />
            <span>{error}</span>
          </div>
        )}

        {/* Login Form */}
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>
              Username or Email
            </label>
            <input
              id="login-username"
              type="text"
              value={usernameOrEmail}
              onChange={(e) => setUsernameOrEmail(e.target.value)}
              placeholder="admin@project.edu"
              required
              style={{
                width: '100%', padding: '12px 16px', fontSize: '14px',
                background: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '10px', color: '#f8fafc', outline: 'none',
                transition: 'border-color 0.2s, box-shadow 0.2s',
                boxSizing: 'border-box',
              }}
              onFocus={(e) => {
                e.target.style.borderColor = 'rgba(56, 189, 248, 0.5)';
                e.target.style.boxShadow = '0 0 0 3px rgba(56, 189, 248, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>

          <div style={{ marginBottom: '28px' }}>
            <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: '#94a3b8', marginBottom: '8px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="login-password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                style={{
                  width: '100%', padding: '12px 48px 12px 16px', fontSize: '14px',
                  background: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '10px', color: '#f8fafc', outline: 'none',
                  transition: 'border-color 0.2s, box-shadow 0.2s',
                  boxSizing: 'border-box',
                }}
                onFocus={(e) => {
                  e.target.style.borderColor = 'rgba(56, 189, 248, 0.5)';
                  e.target.style.boxShadow = '0 0 0 3px rgba(56, 189, 248, 0.1)';
                }}
                onBlur={(e) => {
                  e.target.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                  e.target.style.boxShadow = 'none';
                }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)',
                  background: 'none', border: 'none', color: '#64748b', cursor: 'pointer', padding: '4px',
                }}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          {/* Submit Button */}
          <button
            id="login-submit"
            type="submit"
            disabled={isSubmitting || !usernameOrEmail || !password}
            style={{
              width: '100%', padding: '14px', fontSize: '15px', fontWeight: 600,
              background: isSubmitting ? 'rgba(56, 189, 248, 0.4)' : 'linear-gradient(135deg, #38bdf8 0%, #6366f1 100%)',
              color: '#fff', border: 'none', borderRadius: '10px',
              cursor: isSubmitting ? 'not-allowed' : 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px',
              transition: 'all 0.2s',
              boxShadow: isSubmitting ? 'none' : '0 4px 14px rgba(56, 189, 248, 0.25)',
              opacity: (!usernameOrEmail || !password) ? 0.5 : 1,
            }}
          >
            {isSubmitting ? (
              <>
                <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
                Authenticating...
              </>
            ) : (
              <>
                <LogIn size={18} />
                Sign In
              </>
            )}
          </button>
        </form>

        {/* Demo Credentials */}
        <div style={{
          marginTop: '28px', padding: '16px', borderRadius: '10px',
          background: 'rgba(56, 189, 248, 0.06)',
          border: '1px solid rgba(56, 189, 248, 0.12)',
        }}>
          <p style={{ margin: '0 0 8px', fontSize: '12px', fontWeight: 600, color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Demo Credentials
          </p>
          <p style={{ margin: '0', fontSize: '13px', color: '#94a3b8', lineHeight: 1.6 }}>
            <strong style={{ color: '#cbd5e1' }}>Admin:</strong> admin@project.edu / Admin@123456<br />
          </p>
        </div>
      </div>

      {/* Keyframe animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px) scale(1); }
          50% { transform: translateY(-20px) scale(1.05); }
        }
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
