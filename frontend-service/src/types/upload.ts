export type UploadStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface UploadResponse {
  id: string;
  original_filename: string;
  file_path: string;
  status: UploadStatus;
  total_transactions: number;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface UploadListResponse {
  count: number;
  page: number;
  page_size: number;
  pages: number;
  results: UploadResponse[];
}

export interface UploadFilters {
  status?: string;
  filename?: string;
  date_from?: string;
  date_to?: string;
}
