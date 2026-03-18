import { FileInfo } from '../types';
import { Folder, File, Download, Trash2, Edit, Eye } from 'lucide-react';
import './FileList.css';

interface FileListProps {
  files: FileInfo[];
  onFileClick: (file: FileInfo) => void;
  onDownload: (file: FileInfo) => void;
  onDelete: (file: FileInfo) => void;
  onRename: (file: FileInfo) => void;
  onPreview: (file: FileInfo) => void;
}

const FileList = ({ files, onFileClick, onDownload, onDelete, onRename, onPreview }: FileListProps) => {
  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const getFileIcon = (file: FileInfo) => {
    if (file.type === 'directory') {
      return <Folder size={24} className="file-icon folder-icon" />;
    }
    return <File size={24} className="file-icon file-icon-default" />;
  };

  if (files.length === 0) {
    return (
      <div className="empty-state">
        <Folder size={64} className="empty-icon" />
        <h3>No hay archivos</h3>
        <p>Esta carpeta está vacía o no se encontraron resultados</p>
      </div>
    );
  }

  return (
    <div className="file-list">
      <div className="file-list-header">
        <div className="file-list-cell name-cell">Nombre</div>
        <div className="file-list-cell size-cell">Tamaño</div>
        <div className="file-list-cell modified-cell">Modificado</div>
        <div className="file-list-cell actions-cell">Acciones</div>
      </div>

      {files.map((file, index) => (
        <div key={index} className="file-list-row">
          <div
            className="file-list-cell name-cell clickable"
            onClick={() => onFileClick(file)}
          >
            {getFileIcon(file)}
            <span className="file-name">{file.name}</span>
          </div>

          <div className="file-list-cell size-cell">
            {file.type === 'directory' ? '-' : formatSize(file.size)}
          </div>

          <div className="file-list-cell modified-cell">
            {file.modified}
          </div>

          <div className="file-list-cell actions-cell">
            <div className="file-actions">
              {file.type === 'file' && (
                <>
                  <button
                    className="action-btn preview-btn"
                    onClick={() => onPreview(file)}
                    title="Vista Previa"
                  >
                    <Eye size={18} />
                  </button>
                  <button
                    className="action-btn download-btn"
                    onClick={() => onDownload(file)}
                    title="Descargar"
                  >
                    <Download size={18} />
                  </button>
                </>
              )}
              <button
                className="action-btn rename-btn"
                onClick={() => onRename(file)}
                title="Renombrar"
              >
                <Edit size={18} />
              </button>
              <button
                className="action-btn delete-btn"
                onClick={() => onDelete(file)}
                title="Eliminar"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FileList;
