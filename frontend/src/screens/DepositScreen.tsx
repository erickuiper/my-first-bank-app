import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  ScrollView,
  KeyboardAvoidingView,
  Platform,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { useTheme } from '../contexts/ThemeContext';
import { apiService } from '../services/api';
import { DepositData } from '../types';
import { formatCurrency } from '../utils/currency';

interface DepositScreenProps {
  route: {
    params: {
      accountId: number;
      accountType: string;
      currentBalance: number;
    };
  };
  navigation: any;
}

const DepositScreen: React.FC<DepositScreenProps> = ({ route, navigation }) => {
  const { accountId, accountType, currentBalance } = route.params;
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { theme } = useTheme();

  const handleDeposit = async () => {
    const amountCents = Math.round(parseFloat(amount) * 100);

    if (isNaN(amountCents) || amountCents <= 0) {
      Alert.alert('Error', 'Please enter a valid amount');
      return;
    }

    if (amountCents < 100) { // $1.00 minimum
      Alert.alert('Error', 'Minimum deposit amount is $1.00');
      return;
    }

    if (amountCents > 1000000) { // $10,000.00 maximum
      Alert.alert('Error', 'Maximum deposit amount is $10,000.00');
      return;
    }

    setIsLoading(true);
    try {
      const depositData: DepositData = {
        amount_cents: amountCents,
        transaction_type: 'deposit',
        idempotency_key: `deposit_${accountId}_${Date.now()}_${Math.random()}`,
      };

      const result = await apiService.makeDeposit(accountId, depositData);

      Alert.alert(
        'Success!',
        `Successfully deposited ${formatCurrency(amountCents)} to the ${accountType} account.\nNew balance: ${formatCurrency(result.new_balance_cents)}`,
        [
          {
            text: 'OK',
            onPress: () => navigation.goBack(),
          },
        ]
      );
    } catch (error: any) {
      Alert.alert(
        'Deposit Failed',
        error.response?.data?.detail || 'An error occurred while processing the deposit'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContainer}>
        <View style={styles.content}>
          <View style={[styles.card, { backgroundColor: theme.colors.surface }]}>
            <View style={styles.cardContent}>
              <Text style={[styles.title, { color: theme.colors.primary }]}>
                Make a Deposit
              </Text>
              <Text style={[styles.subtitle, { color: theme.colors.textSecondary }]}>
                Add virtual money to the {accountType} account
              </Text>

              <View style={styles.balanceContainer}>
                <Text style={[styles.balanceLabel, { color: theme.colors.textSecondary }]}>
                  Current Balance:
                </Text>
                <Text style={[styles.balanceAmount, { color: theme.colors.primary }]}>
                  {formatCurrency(currentBalance)}
                </Text>
              </View>

              <TextInput
                placeholder="Amount ($)"
                value={amount}
                onChangeText={setAmount}
                style={[styles.input, { borderColor: theme.colors.border }]}
                keyboardType="decimal-pad"
                editable={!isLoading}
              />

              <Text style={[styles.helperText, { color: theme.colors.textSecondary }]}>
                Enter amount between $1.00 and $10,000.00
              </Text>

              <TouchableOpacity
                onPress={handleDeposit}
                style={[styles.button, { backgroundColor: theme.colors.primary }]}
                disabled={isLoading || !amount.trim()}
              >
                <Text style={styles.buttonText}>
                  {isLoading ? 'Processing...' : 'Deposit Funds'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollContainer: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  content: {
    padding: 20,
  },
  card: {
    elevation: 4,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  cardContent: {
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 24,
  },
  balanceContainer: {
    alignItems: 'center',
    marginBottom: 24,
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  balanceLabel: {
    fontSize: 14,
    marginBottom: 4,
  },
  balanceAmount: {
    fontSize: 24,
    fontWeight: 'bold',
  },
  input: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 12,
    marginBottom: 8,
    fontSize: 16,
  },
  helperText: {
    fontSize: 12,
    textAlign: 'center',
    marginBottom: 24,
    fontStyle: 'italic',
  },
  button: {
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default DepositScreen;
