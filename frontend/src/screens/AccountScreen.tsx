import React, { useState, useEffect } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  RefreshControl,
  FlatList,
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
import { Transaction, TransactionList } from '../types';
import apiService from '../services/api';
import { RootStackParamList } from '../../App';
import { StackNavigationProp } from '@react-navigation/stack';
import { RouteProp } from '@react-navigation/native';
import { format } from 'date-fns';

type AccountScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Account'>;
type AccountScreenRouteProp = RouteProp<RootStackParamList, 'Account'>;

interface AccountScreenProps {
  navigation: AccountScreenNavigationProp;
  route: AccountScreenRouteProp;
}

const AccountScreen: React.FC<AccountScreenProps> = ({ navigation, route }) => {
  const { accountId, accountType } = route.params;
  const theme = useTheme();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [nextCursor, setNextCursor] = useState<string | undefined>();

  useEffect(() => {
    loadTransactions();
  }, [accountId]);

  const loadTransactions = async (cursor?: string) => {
    try {
      if (cursor) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }

      const data: TransactionList = await apiService.getTransactions(accountId, 20, cursor);

      if (cursor) {
        setTransactions(prev => [...prev, ...data.transactions]);
      } else {
        setTransactions(data.transactions);
      }

      setHasMore(data.has_more);
      setNextCursor(data.next_cursor);
    } catch (error) {
      console.error('Failed to load transactions:', error);
      Alert.alert('Error', 'Failed to load transactions. Please try again.');
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadTransactions();
    setRefreshing(false);
  };

  const loadMore = async () => {
    if (hasMore && !loadingMore && nextCursor) {
      await loadTransactions(nextCursor);
    }
  };

  const formatCurrency = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM dd, yyyy HH:mm');
  };

  const getTransactionIcon = (type: string) => {
    return type === 'deposit' ? '💰' : '💸';
  };

  const renderTransaction = ({ item }: { item: Transaction }) => (
    <Card style={styles.transactionCard}>
      <Card.Content>
        <View style={styles.transactionHeader}>
          <View style={styles.transactionInfo}>
            <Text style={styles.transactionType}>
              {item.transaction_type.charAt(0).toUpperCase() +
               item.transaction_type.slice(1)}
            </Text>
            <Text style={styles.transactionDate}>
              {formatDate(item.created_at)}
            </Text>
          </View>
          <View style={styles.transactionAmount}>
            <Text style={styles.amountText}>
              {getTransactionIcon(item.transaction_type)}
            </Text>
            <Text style={[
              styles.amountValue,
              { color: item.transaction_type === 'deposit' ? theme.colors.success : theme.colors.error }
            ]}>
              {item.transaction_type === 'deposit' ? '+' : '-'}{formatCurrency(item.amount_cents)}
            </Text>
          </View>
        </View>
      </Card.Content>
    </Card>
  );

  const renderFooter = () => {
    if (!loadingMore) return null;
    return (
      <View style={styles.loadingFooter}>
        <ActivityIndicator size="small" color={theme.colors.primary} />
        <Text style={styles.loadingText}>Loading more...</Text>
      </View>
    );
  };

  const styles = StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: theme.colors.background,
    },
    content: {
      padding: theme.spacing.md,
    },
    headerCard: {
      marginBottom: theme.spacing.lg,
    },
    headerContent: {
      alignItems: 'center',
    },
    accountType: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    accountBalance: {
      fontSize: theme.typography.h1.fontSize,
      fontWeight: theme.typography.h1.fontWeight as any,
      color: theme.colors.primary,
      marginBottom: theme.spacing.md,
    },
    accountId: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
    },
    actionsContainer: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      marginBottom: theme.spacing.lg,
    },
    actionButton: {
      flex: 1,
      marginHorizontal: theme.spacing.xs,
    },
    sectionTitle: {
      fontSize: theme.typography.h2.fontSize,
      fontWeight: theme.typography.h2.fontWeight as any,
      color: theme.colors.text,
      marginBottom: theme.spacing.md,
    },
    transactionCard: {
      marginBottom: theme.spacing.sm,
      backgroundColor: theme.colors.surface,
    },
    transactionHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    transactionInfo: {
      flex: 1,
    },
    transactionType: {
      fontSize: theme.typography.h3.fontSize,
      fontWeight: theme.typography.h3.fontWeight as any,
      color: theme.colors.text,
      marginBottom: theme.spacing.xs,
    },
    transactionDate: {
      fontSize: theme.typography.caption.fontSize,
      color: theme.colors.textSecondary,
    },
    transactionAmount: {
      alignItems: 'flex-end',
    },
    amountText: {
      fontSize: 20,
      marginBottom: theme.spacing.xs,
    },
    amountValue: {
      fontSize: theme.typography.h3.fontSize,
      fontWeight: theme.typography.h3.fontWeight as any,
    },
    loadingFooter: {
      flexDirection: 'row',
      justifyContent: 'center',
      alignItems: 'center',
      padding: theme.spacing.md,
    },
    loadingText: {
      marginLeft: theme.spacing.sm,
      color: theme.colors.textSecondary,
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

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* Account Header */}
        <Card style={styles.headerCard}>
          <Card.Content style={styles.headerContent}>
            <Text style={styles.accountType}>
              {accountType.charAt(0).toUpperCase() + accountType.slice(1)} Account
            </Text>
            <Text style={styles.accountBalance}>
              {formatCurrency(transactions.reduce((sum, t) =>
                t.transaction_type === 'deposit' ? sum + t.amount_cents : sum - t.amount_cents, 0
              ))}
            </Text>
            <Text style={styles.accountId}>Account ID: {accountId}</Text>
          </Card.Content>
        </Card>

        {/* Action Buttons */}
        <View style={styles.actionsContainer}>
          <Button
            mode="outlined"
            onPress={() => navigation.goBack()}
            style={styles.actionButton}
          >
            Back
          </Button>
          <Button
            mode="contained"
            onPress={() => navigation.navigate('Deposit', {
              accountId,
              accountType,
              currentBalance: transactions.reduce((sum, t) =>
                t.transaction_type === 'deposit' ? sum + t.amount_cents : sum - t.amount_cents, 0
              )
            })}
            style={styles.actionButton}
          >
            Make Deposit
          </Button>
        </View>

        {/* Transactions Section */}
        <Text style={styles.sectionTitle}>Transaction History</Text>

        {transactions.length === 0 ? (
          <View style={styles.emptyState}>
            <Text style={styles.emptyText}>
              No transactions yet.{'\n'}
              Make your first deposit to get started!
            </Text>
          </View>
        ) : (
          <FlatList
            data={transactions}
            renderItem={renderTransaction}
            keyExtractor={(item) => item.id.toString()}
            scrollEnabled={false}
            ListFooterComponent={renderFooter}
            onEndReached={loadMore}
            onEndReachedThreshold={0.1}
          />
        )}
      </ScrollView>
    </View>
  );
};

export default AccountScreen;
