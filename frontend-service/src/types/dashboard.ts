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

export interface AdvancedKPIs {
  cash_flow: string;
  avg_ticket: string;
  total_transactions: number;
  max_expense: {
    amount: string;
    store_name: string;
    type_description: string;
    occurred_at: string;
  } | null;
}

export interface TransactionDetail extends Record<string, unknown> {
  id: string;
  occurred_at: string;
  occurred_time: string;
  type_description: string;
  nature: string;
  sign: string;
  amount: string;
  card: string;
  store_name: string;
  owner_name: string;
  cpf: string;
}

export interface TransactionDetailResponse {
  count: number;
  results: TransactionDetail[];
}
