export interface StoreResponse {
  id: string;
  name: string;
  owner_name: string;
  owner_cpf: string;
  balance: string;
  total_income: string;
  total_expense: string;
  transaction_count: number;
}

export interface TransactionTypeResponse {
  id: string;
  code: number;
  description: string;
  nature: string;
  sign: string;
}

export interface TransactionResponse {
  id: string;
  transaction_type: TransactionTypeResponse;
  amount: string;
  card: string;
  occurred_at: string;
  occurred_time: string;
  store: { id: string; name: string; owner_name: string; owner_cpf: string } | null;
}

export interface StoreListResponse {
  count: number;
  results: StoreResponse[];
}

export interface TransactionListResponse {
  count: number;
  results: TransactionResponse[];
}
