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

export interface DashboardFilters {
  store_id?: string;
  owner_name?: string;
  date_from?: string;
  date_to?: string;
}

export interface AvailableFilters {
  stores: { id: string; name: string; owner_name: string }[];
  owners: string[];
  date_range: { min_date: string; max_date: string };
}

export const dashboardService = {
  async getAvailableFilters(): Promise<AvailableFilters> {
    const response = await api.get('/api/cnab/dashboard/available-filters');
    return response.data;
  },

  async getSummary(params?: DashboardFilters): Promise<DashboardSummary> {
    const response = await api.get('/api/cnab/dashboard/summary', { params });
    return response.data;
  },

  async getBalanceByStore(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/balance-by-store', { params });
    return response.data;
  },

  async getTransactionsByType(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/transactions-by-type', { params });
    return response.data;
  },

  async getTransactionsTimeline(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/cnab/dashboard/uploads-timeline', { params });
    return response.data;
  },
};
