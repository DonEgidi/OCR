import { useState } from 'react';
import { FolderPlus, X } from 'lucide-react';
import './Modal.css';

interface CreateFolderModalProps {
  onClose: () => void;
  onCreate: (folderName: string) => void;
}

const CreateFolderModal = ({ onClose, onCreate }: CreateFolderModalProps) => {
  const [folderName, setFolderName] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (folderName.trim()) {
      onCreate(folderName.trim());
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-small" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <FolderPlus size={24} />
            Nueva Carpeta
          </h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label htmlFor="folder-name">Nombre de la carpeta</label>
              <input
                type="text"
                id="folder-name"
                value={folderName}
                onChange={(e) => setFolderName(e.target.value)}
                placeholder="Mi carpeta"
                autoFocus
                className="form-input"
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn btn-outline" onClick={onClose}>
              Cancelar
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={!folderName.trim()}
            >
              Crear
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateFolderModal;
