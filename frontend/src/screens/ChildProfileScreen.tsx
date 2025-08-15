import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  Alert,
} from 'react-native';
import {
  Card,
  Title,
  Paragraph,
  Button,
  Text,
  ActivityIndicator,
  Divider,
} from 'react-native-paper';
import { useTheme } from '../contexts/ThemeContext';
import { Child, Account } from '../types';
import apiService from '../services/api';
import { RootStackParamList } from '../../App';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { format } from 'date-fns';

type ChildProfileScreenNavigationProp = StackNavigationProp<RootStackParamList, 'ChildProfile'>;
type ChildProfileScreenRouteProp = RouteProp<RootStackParamList, 'ChildProfile'>;

interface ChildProfileScreenProps {
  navigation: ChildProfileScreenNavigationProp;
  route: ChildProfileScreenRouteProp;
}

const ChildProfileScreen: React.FC<ChildProfileScreenProps> = ({ navigation, route }) => {
  const { childId } = route.params;
  const theme = useTheme();
  const [child, setChild] = useState<Child | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadChildProfile();
  }, [childId]);

  const loadChildProfile = async () => {
    try {
      setLoading(true);
      // For now, we'll simulate loading child data
      // In a real app, you'd fetch this from the API
      const mockChild: Child = {
        id: childId,
        name: 'Sample Child',
        birthdate: '2015-01-01',
        parent_id: 1,
        created_at: new Date().toISOString(),
        accounts: [
          {
            id: 1,
            account_type: 'checking',
            balance_cents: 2500,
            child_id: childId,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 2,
            account_type: 'savings',
            balance_cents: 5000,
            child_id: childId,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
      };
      setChild(mockChild);
    } catch (error) {
      console.error('Failed to load child profile:', error);
      Alert.alert('Error', 'Failed to load child profile. Please try again.');
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

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    content: {
      padding: theme.spacing.md,
    },
    profileCard: {
      marginBottom: theme.spacing.lg,
    },
    profileHeader: {
      alignItems: 'center',
      marginBottom: theme.spacing.md,
    },
    avatar: {
      width: 80,
      height: 80,
      borderRadius: 40,
      backgroundColor: theme.colors.primary,
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: theme.spacing.md,
    },
    avatarText: {
      fontSize: 32,
      color: theme.colors.background,
      fontWeight: 'bold',
    },
    childName: {
      fontSize: theme.typography.h1.fontSize,
      fontWeight: theme.typography.h1.fontWeight as any,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    childInfo: {
      fontSize: theme.typography.body.fontSize,
      color: theme.colors.textSecondary,
      marginBottom: theme.spacing.xs,
    },
    accountsSection: {
      marginBottom: theme.spacing.lg,
    },
    sectionTitle: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    accountCard: {
      marginBottom: theme.spacing.md,
      backgroundColor: theme.colors.surface,
    },
    accountHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: theme.spacing.sm,
    },
    accountType: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    accountIcon: {
      fontSize: 24,
      marginRight: theme.spacing.sm,
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
    accountActions: {
      flexDirection: 'row',
      justifyContent: 'space-between',
    },
    actionButton: {
      flex: 1,
      marginHorizontal: theme.spacing.xs,
    },
    statsContainer: {
      flexDirection: 'row',
      justifyContent: 'space-around',
      marginBottom: theme.spacing.lg,
    },
    statItem: {
      alignItems: 'center',
    },
    statValue: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.primary,
    },
    statLabel: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
      marginTop: theme.spacing.xs,
    },
  });

  if (loading) {
    return (
      <View style={styles.container}>
        <View style={styles.content}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </View>
    );
  }

  if (!child) {
    return (
      <View style={styles.container}>
        <View style={styles.content}>
          <Text>Child not found</Text>
        </View>
      </View>
    );
  }

  const totalBalance = child.accounts.reduce((sum, account) => sum + account.balance_cents, 0);
  const age = calculateAge(child.birthdate);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Profile Card */}
        <Card style={styles.profileCard}>
          <Card.Content>
            <View style={styles.profileHeader}>
              <View style={styles.avatar}>
                <Text style={styles.avatarText}>
                  {child.name.charAt(0).toUpperCase()}
                </Text>
              </View>
              <Text style={styles.childName}>{child.name}</Text>
              <Text style={styles.childInfo}>
                Age: {age} years old
              </Text>
              <Text style={styles.childInfo}>
                Birthday: {format(new Date(child.birthdate), 'MMMM dd, yyyy')}
              </Text>
            </View>
          </Card.Content>
        </Card>

        {/* Stats */}
        <Card style={styles.profileCard}>
          <Card.Content>
            <View style={styles.statsContainer}>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{formatCurrency(totalBalance)}</Text>
                <Text style={styles.statLabel}>Total Balance</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{child.accounts.length}</Text>
                <Text style={styles.statLabel}>Accounts</Text>
              </View>
              <View style={styles.statItem}>
                <Text style={styles.statValue}>{age}</Text>
                <Text style={styles.statLabel}>Years Old</Text>
              </View>
            </View>
          </Card.Content>
        </Card>

        {/* Accounts Section */}
        <View style={styles.accountsSection}>
          <Text style={styles.sectionTitle}>Accounts</Text>
          
          {child.accounts.map((account) => (
            <Card key={account.id} style={styles.accountCard}>
              <Card.Content>
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
                
                <Divider style={{ marginVertical: theme.spacing.sm }} />
                
                <View style={styles.accountActions}>
                  <Button
                    mode="outlined"
                    onPress={() => navigation.navigate('Account', { 
                      accountId: account.id, 
                      accountType: account.account_type 
                    })}
                    style={styles.actionButton}
                  >
                    View Details
                  </Button>
                  <Button
                    mode="contained"
                    onPress={() => navigation.navigate('Deposit', { 
                      accountId: account.id, 
                      accountType: account.account_type 
                    })}
                    style={styles.actionButton}
                  >
                    Make Deposit
                  </Button>
                </View>
              </Card.Content>
            </Card>
          ))}
        </View>
      </View>
    </ScrollView>
  );
};

export default ChildProfileScreen;
