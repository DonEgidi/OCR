import { HardDrive } from 'lucide-react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-logo">
          <HardDrive size={32} />
          <h1>FTP File Manager</h1>
        </div>
        <div className="header-subtitle">
          Gestión de archivos FTP
        </div>
      </div>
    </header>
  );
};

export default Header;
