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

export interface DashboardParams {
  year?: number;
  month?: number;
}

export const dashboardService = {
  async getSummary(params?: DashboardParams): Promise<DashboardSummary> {
    const queryParams: Record<string, number> = {};
    if (params?.year) queryParams.year = params.year;
    if (params?.month) queryParams.month = params.month;
    const response = await api.get('/api/cnab/dashboard/summary', { params: queryParams });
    return response.data;
  },
  async getBalanceByStore(params?: DashboardParams): Promise<ChartData> {
    const queryParams: Record<string, number> = {};
    if (params?.year) queryParams.year = params.year;
    if (params?.month) queryParams.month = params.month;
    const response = await api.get('/api/cnab/dashboard/balance-by-store', { params: queryParams });
    return response.data;
  },
  async getTransactionsByType(params?: DashboardParams): Promise<ChartData> {
    const queryParams: Record<string, number> = {};
    if (params?.year) queryParams.year = params.year;
    if (params?.month) queryParams.month = params.month;
    const response = await api.get('/api/cnab/dashboard/transactions-by-type', { params: queryParams });
    return response.data;
  },
  async getTransactionsTimeline(params?: DashboardParams): Promise<ChartData> {
    const queryParams: Record<string, number> = {};
    if (params?.year) queryParams.year = params.year;
    if (params?.month) queryParams.month = params.month;
    const response = await api.get('/api/cnab/dashboard/uploads-timeline', { params: queryParams });
    return response.data;
  },
};
