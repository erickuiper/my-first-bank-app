import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { apiService } from '../services/api';
import { DepositData } from '../types';
import { formatCurrency } from '../utils/currency';

const DepositScreen: React.FC = () => {
  const { accountId, accountType } = useParams<{ accountId: string; accountType: string }>();
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const theme = useTheme();
  
  // Mock current balance for demo
  const currentBalance = 2500; // $25.00 in cents

  const handleDeposit = async () => {
    const amountCents = Math.round(parseFloat(amount) * 100);
    
    if (isNaN(amountCents) || amountCents <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    if (amountCents < 100) { // $1.00 minimum
      alert('Minimum deposit amount is $1.00');
      return;
    }

    if (amountCents > 1000000) { // $10,000.00 maximum
      alert('Maximum deposit amount is $10,000.00');
      return;
    }

    setIsLoading(true);
    try {
      const depositData: DepositData = {
        amount_cents: amountCents,
        idempotency_key: `deposit_${accountId}_${Date.now()}_${Math.random()}`,
      };

      // For now, we'll simulate the deposit
      // In a real app, you'd call the actual API
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      
      const newBalance = currentBalance + amountCents;
      
      alert(
        `Successfully deposited ${formatCurrency(amountCents)} to the ${accountType} account.\nNew balance: ${formatCurrency(newBalance)}`
      );
      
      // Navigate back to the account screen
      navigate(`/account/${accountId}/${accountType}`);
    } catch (error: any) {
      alert(
        'Deposit Failed: ' + (error.response?.data?.detail || 'An error occurred while processing the deposit')
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    navigate(`/account/${accountId}/${accountType}`);
  };

  return (
    <div style={{ 
      backgroundColor: theme.colors.background, 
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ 
        backgroundColor: 'white', 
        borderRadius: '12px', 
        padding: '40px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        maxWidth: '500px',
        margin: '0 auto'
      }}>
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <h1 style={{ 
            color: theme.colors.primary, 
            fontSize: '28px', 
            fontWeight: 'bold',
            margin: '0 0 8px 0'
          }}>
            Make a Deposit
          </h1>
          <p style={{ 
            color: theme.colors.textSecondary, 
            fontSize: '16px',
            margin: 0
          }}>
            Add virtual money to the {accountType} account
          </p>
        </div>

        <div style={{
          backgroundColor: theme.colors.primary,
          color: 'white',
          padding: '20px',
          borderRadius: '8px',
          marginBottom: '24px',
          textAlign: 'center'
        }}>
          <h2 style={{ margin: '0 0 8px 0', fontSize: '18px' }}>
            Current Balance
          </h2>
          <p style={{ 
            fontSize: '32px', 
            fontWeight: 'bold', 
            margin: 0 
          }}>
            {formatCurrency(currentBalance)}
          </p>
        </div>

        <div style={{ marginBottom: '24px' }}>
          <label style={{
            display: 'block',
            marginBottom: '8px',
            color: theme.colors.text,
            fontWeight: 'bold'
          }}>
            Deposit Amount ($)
          </label>
          <input
            type="number"
            step="0.01"
            min="1.00"
            max="10000.00"
            placeholder="Enter amount (e.g., 10.50)"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
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
          <p style={{
            color: theme.colors.textSecondary,
            fontSize: '14px',
            margin: '8px 0 0 0'
          }}>
            Minimum: $1.00 | Maximum: $10,000.00
          </p>
        </div>

        <div style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '24px'
        }}>
          <button
            onClick={handleBack}
            disabled={isLoading}
            style={{
              flex: 1,
              backgroundColor: 'transparent',
              color: theme.colors.primary,
              border: `1px solid ${theme.colors.primary}`,
              borderRadius: '8px',
              padding: '12px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: isLoading ? 'not-allowed' : 'pointer'
            }}
          >
            Cancel
          </button>
          <button
            onClick={handleDeposit}
            disabled={isLoading || !amount}
            style={{
              flex: 2,
              backgroundColor: theme.colors.primary,
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              padding: '12px',
              fontSize: '16px',
              fontWeight: 'bold',
              cursor: (isLoading || !amount) ? 'not-allowed' : 'pointer',
              opacity: (isLoading || !amount) ? 0.7 : 1
            }}
          >
            {isLoading ? 'Processing...' : 'Make Deposit'}
          </button>
        </div>

        <div style={{
          backgroundColor: theme.colors.background,
          padding: '16px',
          borderRadius: '8px',
          border: `1px solid ${theme.colors.border}`
        }}>
          <h3 style={{
            color: theme.colors.text,
            margin: '0 0 12px 0',
            fontSize: '16px'
          }}>
            💡 How it works:
          </h3>
          <ul style={{
            color: theme.colors.textSecondary,
            fontSize: '14px',
            margin: 0,
            paddingLeft: '20px'
          }}>
            <li>This is a virtual banking app for educational purposes</li>
            <li>No real money is involved</li>
            <li>Deposits are instant and help children learn about money management</li>
            <li>You can track all transactions in the account history</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default DepositScreen;
