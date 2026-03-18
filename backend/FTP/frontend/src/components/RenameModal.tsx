import { useState } from 'react';
import { Edit, X } from 'lucide-react';
import './Modal.css';

interface RenameModalProps {
  currentName: string;
  onClose: () => void;
  onRename: (newName: string) => void;
}

const RenameModal = ({ currentName, onClose, onRename }: RenameModalProps) => {
  const [newName, setNewName] = useState(currentName);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (newName.trim() && newName !== currentName) {
      onRename(newName.trim());
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal modal-small" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>
            <Edit size={24} />
            Renombrar
          </h2>
          <button className="modal-close" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <div className="form-group">
              <label htmlFor="new-name">Nuevo nombre</label>
              <input
                type="text"
                id="new-name"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
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
              disabled={!newName.trim() || newName === currentName}
            >
              Renombrar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RenameModal;
