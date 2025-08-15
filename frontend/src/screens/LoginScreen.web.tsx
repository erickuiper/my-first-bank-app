import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';

const LoginScreen: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();
  const theme = useTheme();
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }

    try {
      setIsLoading(true);
      setError('');

      // For now, we'll simulate a login
      // In a real app, you'd call the actual login function
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      // Navigate to dashboard on success
      navigate('/dashboard');
    } catch (error) {
      setError('Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      backgroundColor: theme.colors.background,
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '12px',
        padding: '40px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        width: '100%',
        maxWidth: '400px'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{
            color: theme.colors.primary,
            fontSize: '28px',
            fontWeight: 'bold',
            margin: '0 0 8px 0'
          }}>
            Welcome Back!
          </h1>
          <p style={{
            color: theme.colors.textSecondary,
            fontSize: '16px',
            margin: 0
          }}>
            Sign in to your account
          </p>
        </div>

        {error && (
          <div style={{
            backgroundColor: theme.colors.error,
            color: 'white',
            padding: '12px',
            borderRadius: '8px',
            marginBottom: '16px',
            textAlign: 'center'
          }}>
            {error}
          </div>
        )}

        <div style={{ marginBottom: '16px' }}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: '100%',
              border: `1px solid ${theme.colors.border}`,
              borderRadius: '8px',
              padding: '12px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
            disabled={isLoading}
          />
        </div>

        <div style={{ marginBottom: '24px' }}>
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: '100%',
              border: `1px solid ${theme.colors.border}`,
              borderRadius: '8px',
              padding: '12px',
              fontSize: '16px',
              boxSizing: 'border-box'
            }}
            disabled={isLoading}
          />
        </div>

        <button
          onClick={handleLogin}
          disabled={isLoading}
          style={{
            width: '100%',
            backgroundColor: theme.colors.primary,
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            padding: '12px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            opacity: isLoading ? 0.7 : 1
          }}
        >
          {isLoading ? 'Signing In...' : 'Sign In'}
        </button>

        <div style={{
          textAlign: 'center',
          marginTop: '24px',
          color: theme.colors.textSecondary
        }}>
          Don't have an account?{' '}
          <Link
            to="/register"
            style={{
              color: theme.colors.primary,
              textDecoration: 'none',
              fontWeight: 'bold'
            }}
          >
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
