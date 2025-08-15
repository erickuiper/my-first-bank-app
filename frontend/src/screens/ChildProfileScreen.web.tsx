import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { Child, Account } from '../types';
import apiService from '../services/api';
import { format } from 'date-fns';

const ChildProfileScreen: React.FC = () => {
  const { childId } = useParams<{ childId: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  const [child, setChild] = useState<Child | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (childId) {
      loadChildProfile(parseInt(childId));
    }
  }, [childId]);

  const loadChildProfile = async (id: number) => {
    try {
      setLoading(true);
      // For now, we'll simulate loading child data
      // In a real app, you'd fetch this from the API
      const mockChild: Child = {
        id: id,
        name: 'Sample Child',
        birthdate: '2015-01-01',
        parent_id: 1,
        created_at: new Date().toISOString(),
        accounts: [
          {
            id: 1,
            account_type: 'checking',
            balance_cents: 2500,
            child_id: id,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            account_type: 'savings',
            balance_cents: 5000,
            child_id: id,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      };
      setChild(mockChild);
    } catch (error) {
      console.error('Failed to load child profile:', error);
      alert('Failed to load child profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getAccountIcon = (type: string) => {
    return type === 'checking' ? '💳' : '🏦';
  };

  const calculateAge = (birthdate: string) => {
    const today = new Date();
    const birth = new Date(birthdate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();

    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }

    return age;
  };

  const handleAccountPress = (account: Account) => {
    navigate(`/account/${account.id}/${account.account_type}`);
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

  if (!child) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: theme.colors.background
      }}>
        <div>Child not found</div>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: theme.colors.background,
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ color: theme.colors.primary, marginBottom: '10px' }}>
          {child.name}'s Profile
        </h1>
        <p style={{ color: theme.colors.text, marginBottom: '20px' }}>
          Age: {calculateAge(child.birthdate)} years old
        </p>
        <p style={{ color: theme.colors.text, marginBottom: '20px' }}>
          Birthdate: {format(new Date(child.birthdate), 'MMMM dd, yyyy')}
        </p>
      </div>

      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: theme.colors.primary, marginBottom: '20px' }}>
          Accounts
        </h2>
        {child.accounts.map((account) => (
          <div
            key={account.id}
            style={{
              border: '1px solid #e0e0e0',
              borderRadius: '8px',
              padding: '15px',
              marginBottom: '15px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
            onClick={() => handleAccountPress(account)}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#f5f5f5';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'white';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
              <span style={{ fontSize: '24px', marginRight: '10px' }}>
                {getAccountIcon(account.account_type)}
              </span>
              <h3 style={{
                color: theme.colors.primary,
                margin: 0,
                textTransform: 'capitalize'
              }}>
                {account.account_type} Account
              </h3>
            </div>
            <p style={{
              color: theme.colors.text,
              fontSize: '18px',
              fontWeight: 'bold',
              margin: 0
            }}>
              Balance: {formatCurrency(account.balance_cents)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ChildProfileScreen;
