import { useState } from 'react';
import { Upload, X } from 'lucide-react';
import './Modal.css';

interface UploadModalProps {
  onClose: () => void;
  onUpload: (file: File) => void;
}

const UploadModal = ({ onClose, onUpload }: UploadModalProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(true);
  };

  const handleDragLeave = () => {
    setDragging(false);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };

  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Subir Archivo</h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div
              className={`upload-area ${dragging ? 'dragging' : ''}`}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
            >
              <Upload size={48} className="upload-icon" />
              <p className="upload-text">
                Arrastra un archivo aquí o haz clic para seleccionar
              </p>
              <input
                type="file"
                onChange={handleFileChange}
                className="file-input"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="file-label">
                Seleccionar archivo
              </label>
            </div>

            {selectedFile && (
              <div className="selected-file">
                <div className="selected-file-info">
                  <strong>{selectedFile.name}</strong>
                  <span>{formatSize(selectedFile.size)}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setSelectedFile(null)}
                  className="remove-file"
                >
                  <X size={18} />
                </button>
              </div>
            )}
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!selectedFile}
            >
              Subir
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UploadModal;
