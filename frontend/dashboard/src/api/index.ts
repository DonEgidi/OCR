import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
});

export const ocrApi = {
  uploadDocument: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  getDocuments: () => api.get('/documents'),
  getDocument: (id: string) => api.get(`/documents/${id}`),
  getDocumentOriginalUrl: (id: string) => `${api.defaults.baseURL}/documents/${id}/original`,
  reprocessDocument: (id: string) => api.post(`/documents/${id}/reprocess`),
};

export const keyApi = {
  getKeys: () => api.get('/keys'),
  addKey: (keyValue: string) => api.post('/keys', { key_value: keyValue }),
  reactivateKey: (id: number) => api.post(`/keys/reactivate/${id}`),
  reportError: (keyId: number) => api.post(`/keys/report-error/${keyId}`),
};

export default api;
