import { useState, useEffect } from 'react';
import { FileInfo, SearchFilters } from './types';
import { ftpApi } from './api';
import Header from './components/Header';
import Breadcrumb from './components/Breadcrumb';
import SearchBar from './components/SearchBar';
import FileList from './components/FileList';
import UploadModal from './components/UploadModal';
import CreateFolderModal from './components/CreateFolderModal';
import RenameModal from './components/RenameModal';
import PreviewModal from './components/PreviewModal';
import './App.css';

function App() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [currentPath, setCurrentPath] = useState<string>('/');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [selectedFile, setSelectedFile] = useState<FileInfo | null>(null);
  const [showUploadModal, setShowUploadModal] = useState<boolean>(false);
  const [showCreateFolderModal, setShowCreateFolderModal] = useState<boolean>(false);
  const [showRenameModal, setShowRenameModal] = useState<boolean>(false);
  const [showPreviewModal, setShowPreviewModal] = useState<boolean>(false);
  const [searchMode, setSearchMode] = useState<boolean>(false);
  const [searchFilters, setSearchFilters] = useState<SearchFilters>({
    query: '',
    extension: '',
    minSize: '',
    maxSize: '',
  });

  useEffect(() => {
    loadFiles(currentPath);
  }, [currentPath]);

  const loadFiles = async (path: string) => {
    setLoading(true);
    setError('');
    setSearchMode(false);
    try {
      const data = await ftpApi.listFiles(path);
      setFiles(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar archivos');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (filters: SearchFilters) => {
    setLoading(true);
    setError('');
    setSearchMode(true);
    setSearchFilters(filters);
    
    try {
      const minSize = filters.minSize ? parseInt(filters.minSize) * 1024 * 1024 : undefined;
      const maxSize = filters.maxSize ? parseInt(filters.maxSize) * 1024 * 1024 : undefined;
      
      const data = await ftpApi.searchFiles(
        currentPath,
        filters.query,
        filters.extension || undefined,
        minSize,
        maxSize
      );
      setFiles(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error en la búsqueda');
    } finally {
      setLoading(false);
    }
  };

  const handleClearSearch = () => {
    setSearchFilters({
      query: '',
      extension: '',
      minSize: '',
      maxSize: '',
    });
    loadFiles(currentPath);
  };

  const handleNavigate = (path: string) => {
    setCurrentPath(path);
  };

  const handleFileClick = (file: FileInfo) => {
    if (file.type === 'directory') {
      const newPath = `${currentPath}/${file.name}`.replace('//', '/');
      setCurrentPath(newPath);
    } else {
      setSelectedFile(file);
    }
  };

  const handleDownload = async (file: FileInfo) => {
    try {
      const filePath = `${currentPath}/${file.name}`.replace('//', '/');
      const blob = await ftpApi.downloadFile(filePath);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al descargar archivo');
    }
  };

  const handleDelete = async (file: FileInfo) => {
    if (!confirm(`¿Estás seguro de eliminar "${file.name}"?`)) return;

    try {
      const filePath = `${currentPath}/${file.name}`.replace('//', '/');
      await ftpApi.deleteFile(filePath);
      loadFiles(currentPath);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al eliminar');
    }
  };

  const handleRename = (file: FileInfo) => {
    setSelectedFile(file);
    setShowRenameModal(true);
  };

  const handlePreview = (file: FileInfo) => {
    setSelectedFile(file);
    setShowPreviewModal(true);
  };

  const handleRenameSubmit = async (newName: string) => {
    if (!selectedFile) return;

    try {
      const oldPath = `${currentPath}/${selectedFile.name}`.replace('//', '/');
      const newPath = `${currentPath}/${newName}`.replace('//', '/');
      await ftpApi.renameFile(oldPath, newPath);
      setShowRenameModal(false);
      setSelectedFile(null);
      loadFiles(currentPath);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al renombrar');
    }
  };

  const handleUpload = async (file: File) => {
    try {
      await ftpApi.uploadFile(file, currentPath);
      setShowUploadModal(false);
      loadFiles(currentPath);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al subir archivo');
    }
  };

  const handleCreateFolder = async (folderName: string) => {
    try {
      const folderPath = `${currentPath}/${folderName}`.replace('//', '/');
      await ftpApi.createDirectory(folderPath);
      setShowCreateFolderModal(false);
      loadFiles(currentPath);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al crear carpeta');
    }
  };

  return (
    <div className="app">
      <Header />
      
      <div className="container">
        <div className="toolbar">
          <Breadcrumb path={currentPath} onNavigate={handleNavigate} />
          
          <div className="actions">
            <button className="btn btn-primary" onClick={() => setShowUploadModal(true)}>
              Subir Archivo
            </button>
            <button className="btn btn-secondary" onClick={() => setShowCreateFolderModal(true)}>
              Nueva Carpeta
            </button>
            {searchMode && (
              <button className="btn btn-outline" onClick={handleClearSearch}>
                Limpiar Búsqueda
              </button>
            )}
          </div>
        </div>

        <SearchBar onSearch={handleSearch} filters={searchFilters} />

        {error && (
          <div className="error-message">
            {error}
            <button onClick={() => setError('')}>×</button>
          </div>
        )}

        {loading ? (
          <div className="loading">Cargando...</div>
        ) : (
          <FileList
            files={files}
            onFileClick={handleFileClick}
            onDownload={handleDownload}
            onDelete={handleDelete}
            onRename={handleRename}
            onPreview={handlePreview}
          />
        )}
      </div>

      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onUpload={handleUpload}
        />
      )}

      {showCreateFolderModal && (
        <CreateFolderModal
          onClose={() => setShowCreateFolderModal(false)}
          onCreate={handleCreateFolder}
        />
      )}

      {showRenameModal && selectedFile && (
        <RenameModal
          currentName={selectedFile.name}
          onClose={() => {
            setShowRenameModal(false);
            setSelectedFile(null);
          }}
          onRename={handleRenameSubmit}
        />
      )}

      {showPreviewModal && selectedFile && (
        <PreviewModal
          file={selectedFile}
          filePath={`${currentPath}/${selectedFile.name}`.replace('//', '/')}
          onClose={() => {
            setShowPreviewModal(false);
            setSelectedFile(null);
          }}
        />
      )}
    </div>
  );
}

export default App;
