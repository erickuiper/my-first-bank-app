import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { Account, Transaction } from '../types';
import apiService from '../services/api';
import { format } from 'date-fns';

const AccountScreen: React.FC = () => {
  const { accountId, accountType } = useParams<{ accountId: string; accountType: string }>();
  const navigate = useNavigate();
  const theme = useTheme();
  const [account, setAccount] = useState<Account | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (accountId) {
      loadAccountData(parseInt(accountId));
    }
  }, [accountId]);

  const loadAccountData = async (id: number) => {
    try {
      setLoading(true);
      // Mock data for now
      const mockAccount: Account = {
        id: id,
        account_type: (accountType as 'checking' | 'savings') || 'checking',
        balance_cents: 2500,
        child_id: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      const mockTransactions: Transaction[] = [
        {
          id: 1,
          account_id: id,
          amount_cents: 1000,
          transaction_type: 'deposit',
          idempotency_key: 'mock_key_1',
          created_at: new Date().toISOString(),
        },
        {
          id: 2,
          account_id: id,
          amount_cents: -500,
          transaction_type: 'withdrawal',
          idempotency_key: 'mock_key_2',
          created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        },
      ];

      setAccount(mockAccount);
      setTransactions(mockTransactions);
    } catch (error) {
      console.error('Failed to load account data:', error);
      alert('Failed to load account data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const handleMakeDeposit = () => {
    if (account) {
      navigate(`/deposit/${account.id}/${account.account_type}`);
    }
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

  if (!account) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        backgroundColor: theme.colors.background 
      }}>
        <div>Account not found</div>
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
          {account.account_type.charAt(0).toUpperCase() + account.account_type.slice(1)} Account
        </h1>
        <p style={{ color: theme.colors.text, marginBottom: '20px' }}>
          Account ID: {account.id}
        </p>
        <div style={{ 
          backgroundColor: theme.colors.primary, 
          color: 'white', 
          padding: '20px', 
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          <h2 style={{ margin: '0 0 10px 0' }}>Current Balance</h2>
          <p style={{ fontSize: '32px', fontWeight: 'bold', margin: 0 }}>
            {formatCurrency(account.balance_cents)}
          </p>
        </div>
        <button
          onClick={handleMakeDeposit}
          style={{
            backgroundColor: theme.colors.primary,
            color: 'white',
            border: 'none',
            padding: '12px 24px',
            borderRadius: '6px',
            fontSize: '16px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Make Deposit
        </button>
      </div>

      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        padding: '20px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: theme.colors.primary, marginBottom: '20px' }}>
          Recent Transactions
        </h2>
        {transactions.length === 0 ? (
          <p style={{ color: theme.colors.text, textAlign: 'center' }}>
            No transactions yet
          </p>
        ) : (
          transactions.map((transaction) => (
            <div 
              key={transaction.id}
              style={{
                border: '1px solid #e0e0e0',
                borderRadius: '6px',
                padding: '15px',
                marginBottom: '15px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <p style={{ 
                  color: theme.colors.text, 
                  fontWeight: 'bold',
                  margin: '0 0 5px 0'
                }}>
                  {transaction.transaction_type.charAt(0).toUpperCase() + transaction.transaction_type.slice(1)}
                </p>
                <p style={{ 
                  color: '#666', 
                  fontSize: '14px',
                  margin: 0
                }}>
                  {format(new Date(transaction.created_at), 'MMM dd, yyyy')}
                </p>
              </div>
              <div style={{
                color: transaction.amount_cents > 0 ? '#4caf50' : '#f44336',
                fontWeight: 'bold',
                fontSize: '18px'
              }}>
                {transaction.amount_cents > 0 ? '+' : ''}{formatCurrency(transaction.amount_cents)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AccountScreen;
