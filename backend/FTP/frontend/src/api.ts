import axios from 'axios';
import { FileInfo, UploadResponse, ApiResponse } from './types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ftpApi = {
  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Listar archivos
  listFiles: async (path: string = '/'): Promise<FileInfo[]> => {
    const response = await api.get('/files/list', {
      params: { path },
    });
    return response.data;
  },

  // Subir archivo
  uploadFile: async (file: File, destinationPath: string = '/'): Promise<UploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/files/upload', formData, {
      params: { destination_path: destinationPath },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Descargar archivo
  downloadFile: async (filePath: string): Promise<Blob> => {
    const response = await api.get('/files/download', {
      params: { file_path: filePath },
      responseType: 'blob',
    });
    return response.data;
  },

  // Eliminar archivo o directorio
  deleteFile: async (filePath: string): Promise<ApiResponse> => {
    const response = await api.delete('/files/delete', {
      params: { file_path: filePath },
    });
    return response.data;
  },

  // Mover archivo
  moveFile: async (sourcePath: string, destinationPath: string): Promise<ApiResponse> => {
    const response = await api.post('/files/move', {
      source_path: sourcePath,
      destination_path: destinationPath,
    });
    return response.data;
  },

  // Renombrar archivo
  renameFile: async (oldPath: string, newPath: string): Promise<ApiResponse> => {
    const response = await api.post('/files/rename', {
      old_path: oldPath,
      new_path: newPath,
    });
    return response.data;
  },

  // Crear directorio
  createDirectory: async (directoryPath: string): Promise<ApiResponse> => {
    const response = await api.post('/files/mkdir', {
      directory_path: directoryPath,
    });
    return response.data;
  },

  // Obtener información de archivo
  getFileInfo: async (filePath: string) => {
    const response = await api.get('/files/info', {
      params: { file_path: filePath },
    });
    return response.data;
  },

  // Buscar archivos
  searchFiles: async (
    path: string = '/',
    query: string = '',
    extension?: string,
    minSize?: number,
    maxSize?: number
  ): Promise<FileInfo[]> => {
    const params: any = { path, query };
    if (extension) params.extension = extension;
    if (minSize !== undefined) params.min_size = minSize;
    if (maxSize !== undefined) params.max_size = maxSize;

    const response = await api.get('/files/search', { params });
    return response.data;
  },
};
