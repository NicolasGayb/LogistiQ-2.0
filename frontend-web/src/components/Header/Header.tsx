import { useAuthContext } from '../../context/AuthContext';
import { useEffect, useState } from 'react';
import { logoutService } from '../../services/authService';
import './Header.css';
import { FaBell, FaUserCircle } from 'react-icons/fa';
import api from '../../api/client';

interface HeaderProps {
  title?: string;
}

export function Header({ title }: HeaderProps) {
  const { user, logout } = useAuthContext();
  const [imgError, setImgError] = useState(false);

  // Reseta o estado de erro de imagem quando o usuário muda
  useEffect(() => {
    setImgError(false);
  }, [user?.id]);

  const avatarUrl = user?.id 
    ? `${api.defaults.baseURL}/users/${user.id}/avatar` 
    : null;

  const handleLogout = async () => {
    await logoutService();

    if (logout) logout();

    localStorage.removeItem('access_token');
    window.location.href = '/login';
  };

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
          {avatarUrl && !imgError ? (
            <img
              src={avatarUrl}
              alt={`${user?.name}'s avatar`}
              className="header-avatar"
              onError={() => setImgError(true)}
            />
          ) : (
            <FaUserCircle size={28} />
          )}
          <span className="header-username">{user?.name}</span>
          <div className="header-dropdown">
            <button onClick={handleLogout}>Sair</button>
          </div>
        </div>
      </div>
    </header>
  );
}
