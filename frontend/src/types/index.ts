export interface User {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface Child {
  id: number;
  name: string;
  birthdate: string;
  parent_id: number;
  created_at: string;
  accounts: Account[];
}

export interface Account {
  id: number;
  account_type: 'checking' | 'savings';
  balance_cents: number;
  child_id: number;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  amount_cents: number;
  transaction_type: string;
  idempotency_key: string;
  account_id: number;
  created_at: string;
}

export interface TransactionList {
  transactions: Transaction[];
  next_cursor?: string;
  has_more: boolean;
}

export interface BalanceUpdate {
  new_balance_cents: number;
  transaction: Transaction;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
}

export interface DepositData {
  amount_cents: number;
  transaction_type: string;
  idempotency_key: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}
