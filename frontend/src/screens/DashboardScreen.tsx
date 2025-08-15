import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  Alert,
  Text,
  TouchableOpacity,
} from 'react-native';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import { Child, Account } from '../types';
import apiService from '../services/api';
import { RootStackParamList } from '../../App';
import { StackNavigationProp } from '@react-navigation/stack';
import { format } from 'date-fns';

type DashboardScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Dashboard'>;

interface DashboardScreenProps {
  navigation: DashboardScreenNavigationProp;
}

const DashboardScreen: React.FC<DashboardScreenProps> = ({ navigation }) => {
  const { logout } = useAuth();
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
      const data = await apiService.getChildren();
      setChildren(data);
    } catch (error) {
      console.error('Failed to load children:', error);
      Alert.alert('Error', 'Failed to load children. Please try again.');
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
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', onPress: logout, style: 'destructive' },
      ]
    );
  };

  const formatCurrency = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getAccountIcon = (type: string) => {
    return type === 'checking' ? '💳' : '🏦';
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    header: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderBottomWidth: 1,
      borderBottomColor: theme.colors.border,
    },
    headerTitle: {
      fontSize: theme.typography.h1.fontSize,
      fontWeight: theme.typography.h1.fontWeight as any,
      color: theme.colors.primary,
    },
    logoutButton: {
      marginLeft: theme.spacing.md,
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderWidth: 1,
      borderColor: theme.colors.primary,
      borderRadius: 4,
    },
    logoutButtonText: {
      color: theme.colors.primary,
      fontSize: 14,
      fontWeight: '500',
    },
    content: {
      flex: 1,
      padding: theme.spacing.md,
    },
    emptyState: {
      flex: 1,
      justifyContent: 'center',
      alignItems: 'center',
      padding: theme.spacing.xl,
    },
    emptyText: {
      fontSize: theme.typography.body.fontSize,
      color: theme.colors.textSecondary,
      textAlign: 'center',
      marginBottom: theme.spacing.md,
    },
    childCard: {
      marginBottom: theme.spacing.md,
      backgroundColor: theme.colors.surface,
      borderRadius: 8,
      padding: 16,
      elevation: 2,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 1 },
      shadowOpacity: 0.1,
      shadowRadius: 2,
    },
    childHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: theme.spacing.sm,
    },
    childName: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.text,
    },
    childAge: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
    },
    accountsContainer: {
      marginTop: theme.spacing.sm,
    },
    accountCard: {
      marginBottom: theme.spacing.sm,
      backgroundColor: theme.colors.surface,
      borderRadius: 6,
      padding: 12,
      borderWidth: 1,
      borderColor: theme.colors.border,
    },
    accountHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    accountType: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    accountIcon: {
      fontSize: 20,
      marginRight: theme.spacing.xs,
    },
    accountName: {
      fontSize: theme.typography.h3.fontSize,
      fontWeight: theme.typography.h3.fontWeight as any,
      color: theme.colors.text,
    },
    balance: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.primary,
    },
    button: {
      paddingHorizontal: 16,
      paddingVertical: 8,
      borderRadius: 4,
      alignItems: 'center',
    },
    buttonText: {
      color: 'white',
      fontSize: 14,
      fontWeight: '500',
    },
    buttonOutlined: {
      backgroundColor: 'transparent',
      borderWidth: 1,
      borderColor: theme.colors.primary,
    },
    buttonOutlinedText: {
      color: theme.colors.primary,
    },
    fab: {
      position: 'absolute',
      margin: theme.spacing.md,
      right: 0,
      bottom: 0,
      backgroundColor: theme.colors.primary,
      width: 56,
      height: 56,
      borderRadius: 28,
      justifyContent: 'center',
      alignItems: 'center',
      elevation: 6,
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 3 },
      shadowOpacity: 0.3,
      shadowRadius: 4,
    },
    fabText: {
      color: 'white',
      fontSize: 24,
      fontWeight: 'bold',
    },
  });

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.headerTitle}>My Children</Text>
          <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
            <Text style={styles.logoutButtonText}>Logout</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.emptyState}>
          <Text style={{ color: theme.colors.primary }}>Loading...</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>My Children</Text>
        <TouchableOpacity onPress={handleLogout} style={styles.logoutButton}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </View>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {children.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>
              You haven't added any children yet.{'\n'}
              Tap the + button to create your first child profile.
            </Text>
          </View>
        ) : (
          children.map((child) => (
            <View key={child.id} style={styles.childCard}>
              <View style={styles.childHeader}>
                <View>
                  <Text style={styles.childName}>{child.name}</Text>
                  <Text style={styles.childAge}>
                    {format(new Date(child.birthdate), 'MMM dd, yyyy')}
                  </Text>
                </View>
                <TouchableOpacity
                  style={[styles.button, { backgroundColor: theme.colors.primary }]}
                  onPress={() => navigation.navigate('ChildProfile', { childId: child.id })}
                >
                  <Text style={styles.buttonText}>View Profile</Text>
                </TouchableOpacity>
              </View>

              <View style={styles.accountsContainer}>
                {child.accounts.map((account) => (
                  <View key={account.id} style={styles.accountCard}>
                    <View style={styles.accountHeader}>
                      <View style={styles.accountType}>
                        <Text style={styles.accountIcon}>
                          {getAccountIcon(account.account_type)}
                        </Text>
                        <Text style={styles.accountName}>
                          {account.account_type.charAt(0).toUpperCase() + 
                           account.account_type.slice(1)} Account
                        </Text>
                      </View>
                      <Text style={styles.balance}>
                        {formatCurrency(account.balance_cents)}
                      </Text>
                    </View>
                    <TouchableOpacity
                      style={[styles.button, styles.buttonOutlined, { marginTop: theme.spacing.sm }]}
                      onPress={() => navigation.navigate('Account', { 
                        accountId: account.id, 
                        accountType: account.account_type 
                      })}
                    >
                      <Text style={[styles.buttonText, styles.buttonOutlinedText]}>
                        View Details
                      </Text>
                    </TouchableOpacity>
                  </View>
                ))}
              </View>
            </View>
          ))
        )}
      </ScrollView>

      <TouchableOpacity
        style={styles.fab}
        onPress={() => {
          // TODO: Navigate to add child screen
          Alert.alert('Coming Soon', 'Add child functionality will be implemented soon!');
        }}
      >
        <Text style={styles.fabText}>+</Text>
      </TouchableOpacity>
    </View>
  );
};

export default DashboardScreen;
