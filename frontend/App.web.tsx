import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './src/contexts/AuthContext';
import { ThemeProvider } from './src/contexts/ThemeContext';

// Screens
import LoginScreen from './src/screens/LoginScreen.web';
import RegisterScreen from './src/screens/RegisterScreen.web';
import DashboardScreen from './src/screens/DashboardScreen.web';
import ChildProfileScreen from './src/screens/ChildProfileScreen.web';
import AccountScreen from './src/screens/AccountScreen.web';
import DepositScreen from './src/screens/DepositScreen.web';

// Types
export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  ChildProfile: { childId: number };
  Account: { accountId: number; accountType: string };
  Deposit: { accountId: number; accountType: string };
};

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <div className="app">
            <Routes>
              <Route path="/" element={<Navigate to="/login" replace />} />
              <Route path="/login" element={<LoginScreen />} />
              <Route path="/register" element={<RegisterScreen />} />
              <Route path="/dashboard" element={<DashboardScreen />} />
              <Route path="/child-profile/:childId" element={<ChildProfileScreen />} />
              <Route path="/account/:accountId/:accountType" element={<AccountScreen />} />
              <Route path="/deposit/:accountId/:accountType" element={<DepositScreen />} />
            </Routes>
          </div>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}
