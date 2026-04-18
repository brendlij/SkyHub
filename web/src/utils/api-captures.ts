import { httpClient } from './http-client';
import type { CaptureDetailResponse, CaptureListResponse } from '@/types';

export const capturesApi = {
  // Get all captures
  async getAllCaptures(): Promise<CaptureListResponse[]> {
    return httpClient.get('/api/captures/');
  },

  // Get captures for a specific date
  async getCapturesByDate(date: string): Promise<CaptureListResponse> {
    return httpClient.get(`/api/captures/${date}`);
  },

  // Get captures for a specific date and time period
  async getCapturesByDateAndPeriod(
    date: string,
    period: 'morning' | 'afternoon' | 'evening' | 'night'
  ): Promise<CaptureListResponse> {
    return httpClient.get(`/api/captures/${date}/${period}`);
  },

  // Get captures by node
  async getCapturesByNode(nodeId: string): Promise<CaptureDetailResponse[]> {
    return httpClient.get(`/api/nodes/${nodeId}/captures`);
  },

  // Get specific capture
  async getCapture(captureId: string): Promise<CaptureDetailResponse> {
    return httpClient.get(`/api/captures/${captureId}`);
  },

  // Download capture image
  async downloadCapture(captureId: string): Promise<Blob> {
    const url = `http://localhost:8000/api/captures/${captureId}/download`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to download capture: ${response.statusText}`);
    }
    return response.blob();
  },

  // Get capture thumbnail
  async getThumbnail(captureId: string): Promise<Blob> {
    const url = `http://localhost:8000/api/captures/${captureId}/thumbnail`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to get thumbnail: ${response.statusText}`);
    }
    return response.blob();
  },

  // Delete capture
  async deleteCapture(captureId: string): Promise<void> {
    return httpClient.delete(`/api/captures/${captureId}`);
  },

  // Get capture stats
  async getStats(params?: {
    start_date?: string;
    end_date?: string;
    node_id?: string;
  }): Promise<{
    total_captures: number;
    total_size_mb: number;
    date_range: {
      start: string;
      end: string;
    };
  }> {
    return httpClient.get('/api/captures/stats', params);
  },
};
