import api from './api';
import type { UploadResponse, UploadListResponse, UploadFilters } from '../types/upload';

export const uploadService = {
  async upload(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/upload/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  async list(
    page = 1,
    pageSize = 10,
    filters?: UploadFilters,
  ): Promise<UploadListResponse> {
    const params: Record<string, string | number> = { page, page_size: pageSize };
    if (filters?.status) params.status = filters.status;
    if (filters?.filename) params.filename = filters.filename;
    if (filters?.date_from) params.date_from = filters.date_from;
    if (filters?.date_to) params.date_to = filters.date_to;
    const response = await api.get('/api/upload/uploads/', { params });
    const data = response.data;
    // Calculate derived pagination fields from backend count
    return {
      ...data,
      page,
      page_size: pageSize,
      pages: Math.ceil(data.count / pageSize),
    };
  },

  async get(id: string): Promise<UploadResponse> {
    const response = await api.get(`/api/upload/uploads/${id}`);
    return response.data;
  },
};

export type { UploadResponse, UploadListResponse, UploadFilters };
