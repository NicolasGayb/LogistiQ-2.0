import { useAuthContext } from '../../context/AuthContext';
import './Header.css';
import { FaBell, FaUserCircle } from 'react-icons/fa';

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  const { user, logout } = useAuthContext();

  return (
    <header className="header">
      <div className="header-left">
        <div className="header-logo">LogistiQ</div>
        {title && <h1 className="header-title">{title}</h1>}
      </div>

      <div className="header-right">
        <button className="header-icon-btn">
          <FaBell size={20} />
        </button>

        <div className="header-user">
          <FaUserCircle size={28} />
          <span className="header-username">{user?.name}</span>
          <div className="header-dropdown">
            <button onClick={logout}>Sair</button>
          </div>
        </div>
      </div>
    </header>
  );
}
