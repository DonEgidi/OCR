export interface FileInfo {
  name: string;
  type: 'file' | 'directory';
  size: number;
  modified: string;
  permissions: string;
}

export interface UploadResponse {
  message: string;
  filename: string;
  destination_path: string;
  size_bytes: number;
  size_mb: number;
}

export interface ApiResponse {
  message: string;
  [key: string]: any;
}

export interface SearchFilters {
  query: string;
  extension: string;
  minSize: string;
  maxSize: string;
}
