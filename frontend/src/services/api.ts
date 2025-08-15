import axios, { AxiosInstance, AxiosResponse, AxiosRequestConfig } from 'axios';
import {
  AuthResponse,
  LoginCredentials,
  RegisterData,
  Child,
  Account,
  TransactionList,
  BalanceUpdate,
  DepositData,
  ApiError,
} from '../types';

// Environment-aware API base URL
const getApiBaseUrl = () => {
  // Check if we're in production (Heroku)
  if (window.location.hostname.includes('herokuapp.com')) {
    // You'll need to update this with your actual Heroku app URL
    return 'https://your-backend-app-name.herokuapp.com/api/v1';
  }
  
  // Check if we're in development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:8000/api/v1';
  }
  
  // Default to localhost for other environments
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getApiBaseUrl();

// Log the API URL being used (helpful for debugging)
console.log(`🌐 Using API base URL: ${API_BASE_URL}`);

// Web-compatible storage using localStorage
const storage = {
  async getItem(key: string): Promise<string | null> {
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },
  async setItem(key: string, value: string): Promise<void> {
    try {
      localStorage.setItem(key, value);
    } catch {
      // Ignore errors in web environment
    }
  },
  async deleteItem(key: string): Promise<void> {
    try {
      localStorage.removeItem(key);
    } catch {
      // Ignore errors in web environment
    }
  }
};

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      async (config: any) => {
        const token = await storage.getItem('auth_token');
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: any) => {
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: any) => {
        if (error.response?.status === 401) {
          // Token expired or invalid, clear it
          await storage.deleteItem('auth_token');
          // You might want to redirect to login here
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  async login(data: LoginCredentials): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/login', data);
    return response.data;
  }

  // Children
  async createChild(data: { name: string; birthdate: string }): Promise<Child> {
    const response = await this.api.post<Child>('/children/', data);
    return response.data;
  }

  async getChildren(): Promise<Child[]> {
    const response = await this.api.get<Child[]>('/children/');
    return response.data;
  }

  // Accounts
  async makeDeposit(accountId: number, data: DepositData): Promise<BalanceUpdate> {
    const response = await this.api.post<BalanceUpdate>(
      `/accounts/${accountId}/deposit`,
      data
    );
    return response.data;
  }

  async getTransactions(
    accountId: number,
    limit: number = 20,
    cursor?: string
  ): Promise<TransactionList> {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (cursor) {
      params.append('cursor', cursor);
    }

    const response = await this.api.get<TransactionList>(
      `/accounts/${accountId}/transactions?${params.toString()}`
    );
    return response.data;
  }

  // Utility methods
  async setAuthToken(token: string): Promise<void> {
    await storage.setItem('auth_token', token);
  }

  async getAuthToken(): Promise<string | null> {
    return await storage.getItem('auth_token');
  }

  async clearAuthToken(): Promise<void> {
    await storage.deleteItem('auth_token');
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await storage.getItem('auth_token');
    return token !== null;
  }
}

export const apiService = new ApiService();
export default apiService;

export const setAuthToken = async (token: string): Promise<void> => {
  await storage.setItem('auth_token', token);
};

export const getAuthToken = async (): Promise<string | null> => {
  return await storage.getItem('auth_token');
};

export const clearAuthToken = async (): Promise<void> => {
  await storage.deleteItem('auth_token');
};

export const hasAuthToken = async (): Promise<boolean> => {
  return await storage.getItem('auth_token') !== null;
};
