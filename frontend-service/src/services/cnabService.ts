import api from './api';
import type {
  StoreListResponse,
  TransactionListResponse,
  TransactionTypeResponse,
} from '../types/cnab';

export type {
  StoreResponse,
  TransactionTypeResponse,
  TransactionResponse,
  StoreListResponse,
  TransactionListResponse,
} from '../types/cnab';

export const cnabService = {
  async listStores(filters?: {
    name?: string;
    owner_name?: string;
  }): Promise<StoreListResponse> {
    const params: Record<string, string> = {};
    if (filters?.name) params.name = filters.name;
    if (filters?.owner_name) params.owner_name = filters.owner_name;
    const response = await api.get('/api/cnab/stores/', { params });
    return response.data;
  },

  async getStoreTransactions(
    storeId: string,
    filters?: {
      type?: string;
      nature?: string;
      date_from?: string;
      date_to?: string;
    },
  ): Promise<TransactionListResponse> {
    const params: Record<string, string> = {};
    if (filters?.type) params.type = filters.type;
    if (filters?.nature) params.nature = filters.nature;
    if (filters?.date_from) params.date_from = filters.date_from;
    if (filters?.date_to) params.date_to = filters.date_to;
    const response = await api.get(`/api/cnab/stores/${storeId}/transactions/`, { params });
    return response.data;
  },

  async getTransactionTypes(): Promise<TransactionTypeResponse[]> {
    const response = await api.get('/api/cnab/transaction-types/');
    return response.data;
  },
};
