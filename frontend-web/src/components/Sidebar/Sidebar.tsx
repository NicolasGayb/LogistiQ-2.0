import { NavLink } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { menuByRole } from '../../navigation/menuByRole';
import './Sidebar.css';

export function Sidebar() {
  const { user } = useAuth();

  if (!user) return null;

  const menu = menuByRole[user.role] ?? [];

  return (
    <aside className="sidebar">
      <div className="sidebar-title">LogistiQ</div>

      <nav className="sidebar-menu">
        {menu.map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `sidebar-item ${isActive ? 'active' : ''}`
            }
          >
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        © {new Date().getFullYear()}
      </div>
    </aside>
  );
}
