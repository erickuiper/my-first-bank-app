import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Child, Account } from '../types';
import apiService from '../services/api';
import { format } from 'date-fns';

const DashboardScreen: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();
  const theme = useTheme();
  const [children, setChildren] = useState<Child[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadChildren();
  }, []);

  const loadChildren = async () => {
    try {
      setLoading(true);
      // For now, we'll simulate loading children data
      // In a real app, you'd fetch this from the API
      const mockChildren: Child[] = [
        {
          id: 1,
          name: 'Emma',
          birthdate: '2015-03-15',
          parent_id: 1,
          created_at: new Date().toISOString(),
          accounts: [
            {
              id: 1,
              account_type: 'checking',
              balance_cents: 2500,
              child_id: 1,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
            {
              id: 2,
              account_type: 'savings',
              balance_cents: 5000,
              child_id: 1,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ],
        },
        {
          id: 2,
          name: 'Liam',
          birthdate: '2018-07-22',
          parent_id: 1,
          created_at: new Date().toISOString(),
          accounts: [
            {
              id: 3,
              account_type: 'checking',
              balance_cents: 1500,
              child_id: 2,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            },
          ],
        },
      ];
      setChildren(mockChildren);
    } catch (error) {
      console.error('Failed to load children:', error);
      alert('Failed to load children. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadChildren();
    setRefreshing(false);
  };

  const handleLogout = () => {
    if (confirm('Are you sure you want to logout?')) {
      logout();
      navigate('/login');
    }
  };

  const formatCurrency = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getAccountIcon = (type: string) => {
    return type === 'checking' ? '💳' : '🏦';
  };

  const handleChildPress = (child: Child) => {
    navigate(`/child-profile/${child.id}`);
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: theme.colors.background 
      }}>
        <div>Loading...</div>
      </div>
    );
  }

  return (
    <div style={{ 
      backgroundColor: theme.colors.background, 
      minHeight: '100vh'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '16px',
        backgroundColor: theme.colors.surface,
        borderBottom: `1px solid ${theme.colors.border}`,
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{
          fontSize: '24px',
          fontWeight: 'bold',
          color: theme.colors.primary,
          margin: 0
        }}>
          My Children
        </h1>
        <button
          onClick={handleLogout}
          style={{
            padding: '8px 16px',
            border: `1px solid ${theme.colors.primary}`,
            borderRadius: '4px',
            backgroundColor: 'transparent',
            color: theme.colors.primary,
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          Logout
        </button>
      </div>

      {/* Content */}
      <div style={{ padding: '20px' }}>
        {children.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            color: theme.colors.textSecondary
          }}>
            <p>No children added yet.</p>
            <p>Add your first child to get started!</p>
          </div>
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px'
          }}>
            {children.map((child) => (
              <div
                key={child.id}
                style={{
                  backgroundColor: 'white',
                  borderRadius: '12px',
                  padding: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease'
                }}
                onClick={() => handleChildPress(child)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
                }}
              >
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  marginBottom: '16px'
                }}>
                  <div style={{
                    width: '50px',
                    height: '50px',
                    borderRadius: '25px',
                    backgroundColor: theme.colors.primary,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'white',
                    fontSize: '20px',
                    fontWeight: 'bold',
                    marginRight: '12px'
                  }}>
                    {child.name.charAt(0)}
                  </div>
                  <div>
                    <h2 style={{
                      color: theme.colors.primary,
                      margin: '0 0 4px 0',
                      fontSize: '20px'
                    }}>
                      {child.name}
                    </h2>
                    <p style={{
                      color: theme.colors.textSecondary,
                      margin: 0,
                      fontSize: '14px'
                    }}>
                      Age: {Math.floor((new Date().getTime() - new Date(child.birthdate).getTime()) / (1000 * 60 * 60 * 24 * 365.25))} years old
                    </p>
                  </div>
                </div>

                <div style={{ marginBottom: '16px' }}>
                  <h3 style={{
                    color: theme.colors.text,
                    margin: '0 0 12px 0',
                    fontSize: '16px'
                  }}>
                    Accounts ({child.accounts.length})
                  </h3>
                  {child.accounts.map((account) => (
                    <div
                      key={account.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        marginBottom: '8px',
                        padding: '8px',
                        backgroundColor: theme.colors.background,
                        borderRadius: '6px'
                      }}
                    >
                      <span style={{ fontSize: '20px', marginRight: '8px' }}>
                        {getAccountIcon(account.account_type)}
                      </span>
                      <span style={{
                        color: theme.colors.text,
                        fontSize: '14px',
                        textTransform: 'capitalize',
                        marginRight: '8px'
                      }}>
                        {account.account_type}
                      </span>
                      <span style={{
                        color: theme.colors.primary,
                        fontWeight: 'bold',
                        marginLeft: 'auto'
                      }}>
                        {formatCurrency(account.balance_cents)}
                      </span>
                    </div>
                  ))}
                </div>

                <div style={{
                  textAlign: 'center',
                  color: theme.colors.primary,
                  fontSize: '14px',
                  fontWeight: 'bold'
                }}>
                  Tap to view profile →
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardScreen;
