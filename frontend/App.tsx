import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'expo-status-bar';
import { PaperProvider } from 'react-native-paper';
import { AuthProvider } from './src/contexts/AuthContext';
import { ThemeProvider } from './src/contexts/ThemeContext';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import ChildProfileScreen from './src/screens/ChildProfileScreen';
import AccountScreen from './src/screens/AccountScreen';
import DepositScreen from './src/screens/DepositScreen';

// Types
export type RootStackParamList = {
  Login: undefined;
  Register: undefined;
  Dashboard: undefined;
  ChildProfile: { childId: number };
  Account: { accountId: number; accountType: string };
  Deposit: { accountId: number; accountType: string };
};

const Stack = createStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <PaperProvider>
      <ThemeProvider>
        <AuthProvider>
          <NavigationContainer>
            <StatusBar style="auto" />
            <Stack.Navigator
            initialRouteName="Login"
            screenOptions={{
              headerStyle: {
                backgroundColor: '#2196F3',
              },
              headerTintColor: '#fff',
              headerTitleStyle: {
                fontWeight: 'bold',
              },
            }}
          >
            <Stack.Screen
              name="Login"
              component={LoginScreen}
              options={{ title: 'Login' }}
            />
            <Stack.Screen
              name="Register"
              component={RegisterScreen}
              options={{ title: 'Register' }}
            />
            <Stack.Screen
              name="Dashboard"
              component={DashboardScreen}
              options={{ title: 'My Children' }}
            />
            <Stack.Screen
              name="ChildProfile"
              component={ChildProfileScreen}
              options={{ title: 'Child Profile' }}
            />
            <Stack.Screen
              name="Account"
              component={AccountScreen}
              options={{ title: 'Account' }}
            />
            <Stack.Screen
              name="Deposit"
              component={DepositScreen}
              options={{ title: 'Make Deposit' }}
            />
          </Stack.Navigator>
        </NavigationContainer>
      </AuthProvider>
    </ThemeProvider>
    </PaperProvider>
  );
}
