import { useAuth } from '../../context/AuthContext';
import './Header.css';

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header>
      <span>{user?.name}</span>
      <button onClick={logout}>Sair</button>
    </header>
  );
}
