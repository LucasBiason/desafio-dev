import api from './api';

export interface DashboardSummary {
  total_stores: number;
  total_transactions: number;
  total_income: string;
  total_expense: string;
  overall_balance: string;
}

export interface ChartData {
  labels: string[];
  data: number[];
  colors?: string[];
}

export const dashboardService = {
  async getSummary(): Promise<DashboardSummary> {
    const response = await api.get('/api/cnab/dashboard/summary');
    return response.data;
  },
  async getBalanceByStore(): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/balance-by-store');
    return response.data;
  },
  async getTransactionsByType(): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/transactions-by-type');
    return response.data;
  },
  async getTransactionsTimeline(): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/uploads-timeline');
    return response.data;
  },
};
