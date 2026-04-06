import api from './api';
import type {
  AdvancedKPIs,
  AvailableFilters,
  ChartData,
  DashboardFilters,
  DashboardSummary,
  TransactionDetailResponse,
} from '../types/dashboard';

export type {
  AdvancedKPIs,
  AvailableFilters,
  ChartData,
  DashboardFilters,
  DashboardSummary,
  TransactionDetail,
  TransactionDetailResponse,
} from '../types/dashboard';

export const dashboardService = {
  async getAvailableFilters(): Promise<AvailableFilters> {
    const response = await api.get('/api/dashboard/available-filters');
    return response.data;
  },

  async getSummary(params?: DashboardFilters): Promise<DashboardSummary> {
    const response = await api.get('/api/dashboard/summary', { params });
    return response.data;
  },

  async getBalanceByStore(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/dashboard/balance-by-store', { params });
    return response.data;
  },

  async getTransactionsByType(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/dashboard/transactions-by-type', { params });
    return response.data;
  },

  async getTransactionsTimeline(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/dashboard/uploads-timeline', { params });
    return response.data;
  },

  async getAdvancedKpis(params?: DashboardFilters): Promise<AdvancedKPIs> {
    const response = await api.get('/api/dashboard/advanced-kpis', { params });
    return response.data;
  },

  async getTransactionsByHour(params?: DashboardFilters): Promise<ChartData> {
    const response = await api.get('/api/dashboard/transactions-by-hour', { params });
    return response.data;
  },

  async getTransactionsDetail(
    page: number,
    pageSize: number,
    params?: DashboardFilters,
    nature?: string,
    ordering?: string,
  ): Promise<TransactionDetailResponse> {
    const response = await api.get('/api/dashboard/transactions-detail', {
      params: { ...params, page, page_size: pageSize, nature: nature || undefined, ordering: ordering || undefined },
    });
    return response.data;
  },
};
