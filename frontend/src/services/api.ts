import type { ScanResult, DashboardStats, HealthStatus, ChatMessage, Citation } from '../types';

const API_BASE = (import.meta.env.VITE_API_BASE_URL || '') + '/api/v1';

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let errorMsg = `HTTP Error ${res.status}`;
    try {
      const errJson = await res.json();
      errorMsg = errJson.detail || errJson.message || errorMsg;
    } catch {
      // ignore
    }
    throw new Error(errorMsg);
  }
  return res.json();
}

export const api = {
  async submitScan(url: string): Promise<ScanResult> {
    const res = await fetch(`${API_BASE}/scan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    return handleResponse<ScanResult>(res);
  },

  async getScan(id: string): Promise<ScanResult> {
    const res = await fetch(`${API_BASE}/scan/${id}`);
    return handleResponse<ScanResult>(res);
  },

  async listScans(search?: string, riskLevel?: string, limit = 50, offset = 0): Promise<{ items: ScanResult[]; total: number }> {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (riskLevel && riskLevel !== 'ALL') params.append('risk_level', riskLevel);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());

    const res = await fetch(`${API_BASE}/scans?${params.toString()}`);
    return handleResponse<{ items: ScanResult[]; total: number }>(res);
  },

  async deleteScan(id: string): Promise<void> {
    const res = await fetch(`${API_BASE}/scans/${id}`, { method: 'DELETE' });
    if (!res.ok && res.status !== 204) {
      throw new Error(`Failed to delete scan: HTTP ${res.status}`);
    }
  },

  async getDashboardStats(): Promise<DashboardStats> {
    const res = await fetch(`${API_BASE}/stats`);
    return handleResponse<DashboardStats>(res);
  },

  async getHealth(): Promise<HealthStatus> {
    const res = await fetch(`${API_BASE}/health`);
    return handleResponse<HealthStatus>(res);
  },

  async seedSampleData(): Promise<{ message: string; scan_ids: string[] }> {
    const res = await fetch(`${API_BASE}/seed`, { method: 'POST' });
    return handleResponse<{ message: string; scan_ids: string[] }>(res);
  },

  async askAssistant(scanId: string, question: string): Promise<{ answer: string; grounded: boolean; citations: Citation[]; model_used: string }> {
    const res = await fetch(`${API_BASE}/scan/${scanId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    return handleResponse<{ answer: string; grounded: boolean; citations: Citation[]; model_used: string }>(res);
  },

  async getChatHistory(scanId: string): Promise<ChatMessage[]> {
    const res = await fetch(`${API_BASE}/scan/${scanId}/chat`);
    return handleResponse<ChatMessage[]>(res);
  },
};
