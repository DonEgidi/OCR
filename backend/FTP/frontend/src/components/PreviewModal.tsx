import { X, FileText, Image as ImageIcon, Film, Music, File } from 'lucide-react';
import { FileInfo } from '../types';
import './Modal.css';
import './PreviewModal.css';

interface PreviewModalProps {
  file: FileInfo;
  filePath: string;
  onClose: () => void;
}

const PreviewModal = ({ file, filePath, onClose }: PreviewModalProps) => {
  const getFileExtension = (filename: string): string => {
    return filename.split('.').pop()?.toLowerCase() || '';
  };

  const extension = getFileExtension(file.name);

  const isImage = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'].includes(extension);
  const isPDF = extension === 'pdf';
  const isVideo = ['mp4', 'webm', 'ogg', 'mov'].includes(extension);
  const isAudio = ['mp3', 'wav', 'ogg', 'm4a'].includes(extension);
  const isText = ['txt', 'md', 'json', 'xml', 'csv', 'log'].includes(extension);

  const previewUrl = `http://localhost:8000/files/view?file_path=${encodeURIComponent(filePath)}`;
  const downloadUrl = `http://localhost:8000/files/download?file_path=${encodeURIComponent(filePath)}`;

  const formatSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
  };

  const renderPreview = () => {
    if (isImage) {
      return (
        <div className="preview-content image-preview">
          <img src={previewUrl} alt={file.name} />
        </div>
      );
    }

    if (isPDF) {
      return (
        <div className="preview-content pdf-preview">
          <iframe src={previewUrl} title={file.name} />
        </div>
      );
    }

    if (isVideo) {
      return (
        <div className="preview-content video-preview">
          <video controls>
            <source src={previewUrl} type={`video/${extension}`} />
            Tu navegador no soporta el elemento de video.
          </video>
        </div>
      );
    }

    if (isAudio) {
      return (
        <div className="preview-content audio-preview">
          <div className="audio-icon">
            <Music size={64} />
          </div>
          <audio controls>
            <source src={previewUrl} type={`audio/${extension}`} />
            Tu navegador no soporta el elemento de audio.
          </audio>
        </div>
      );
    }

    if (isText && file.size < 1024 * 1024) { // Solo archivos de texto < 1MB
      return (
        <div className="preview-content text-preview">
          <iframe src={previewUrl} title={file.name} />
        </div>
      );
    }

    // Vista previa no disponible
    return (
      <div className="preview-content no-preview">
        <div className="no-preview-icon">
          {isText ? <FileText size={64} /> : <File size={64} />}
        </div>
        <h3>Vista previa no disponible</h3>
        <p>Este tipo de archivo no se puede previsualizar</p>
        <p className="file-type">.{extension.toUpperCase()}</p>
      </div>
    );
  };

  const getPreviewIcon = () => {
    if (isImage) return <ImageIcon size={20} />;
    if (isPDF) return <FileText size={20} />;
    if (isVideo) return <Film size={20} />;
    if (isAudio) return <Music size={20} />;
    return <File size={20} />;
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-preview" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            {getPreviewIcon()}
            Vista Previa
          </h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body preview-modal-body">
          <div className="preview-info">
            <div className="preview-info-item">
              <strong>Nombre:</strong> {file.name}
            </div>
            <div className="preview-info-item">
              <strong>Tamaño:</strong> {formatSize(file.size)}
            </div>
            <div className="preview-info-item">
              <strong>Tipo:</strong> .{extension.toUpperCase()}
            </div>
            <div className="preview-info-item">
              <strong>Modificado:</strong> {file.modified}
            </div>
          </div>

          {renderPreview()}
        </div>

        <div className="modal-footer">
          <a
            href={downloadUrl}
            download={file.name}
            className="btn btn-primary"
          >
            Descargar
          </a>
          <button className="btn btn-outline" onClick={onClose}>
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default PreviewModal;
