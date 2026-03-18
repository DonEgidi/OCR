import { Home, ChevronRight } from 'lucide-react';
import './Breadcrumb.css';

interface BreadcrumbProps {
  path: string;
  onNavigate: (path: string) => void;
}

const Breadcrumb = ({ path, onNavigate }: BreadcrumbProps) => {
  const parts = path.split('/').filter(Boolean);

  const handleClick = (index: number) => {
    if (index === -1) {
      onNavigate('/');
    } else {
      const newPath = '/' + parts.slice(0, index + 1).join('/');
      onNavigate(newPath);
    }
  };

  return (
    <div className="breadcrumb">
      <button
        className="breadcrumb-item"
        onClick={() => handleClick(-1)}
      >
        <Home size={18} />
        <span>Inicio</span>
      </button>

      {parts.map((part, index) => (
        <div key={index} className="breadcrumb-segment">
          <ChevronRight size={18} className="breadcrumb-separator" />
          <button
            className="breadcrumb-item"
            onClick={() => handleClick(index)}
          >
            {part}
          </button>
        </div>
      ))}
    </div>
  );
};

export default Breadcrumb;
