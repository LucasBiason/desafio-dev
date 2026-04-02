import React, { memo } from 'react';
import type { FC } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faGauge, faCloudArrowUp, faStore, faRightFromBracket } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../hooks/useAuth';

interface NavItemProps {
  to: string;
  label: string;
  icon: React.ReactElement;
}

const NavItem: FC<NavItemProps> = ({ to, label, icon }) => (
  <NavLink
    to={to}
    className={({ isActive }) =>
      [
        'flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-colors',
        isActive
          ? 'nav-item-active'
          : 'nav-item-inactive',
      ].join(' ')
    }
  >
    {icon}
    <span>{label}</span>
  </NavLink>
);

const Sidebar: FC = memo(() => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar-bg fixed top-0 left-0 h-full w-64 flex flex-col z-40">
      <div className="px-6 py-5 border-b border-input">
        <h1 className="text-accent text-lg font-semibold tracking-wide">CNAB Parser</h1>
        <p className="text-secondary text-xs mt-0.5">Gestão de transações</p>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <NavItem
          to="/dashboard"
          label="Dashboard"
          icon={<FontAwesomeIcon icon={faGauge} size="lg" />}
        />
        <NavItem
          to="/upload"
          label="Upload"
          icon={<FontAwesomeIcon icon={faCloudArrowUp} size="lg" />}
        />
        <NavItem
          to="/stores"
          label="Lojas"
          icon={<FontAwesomeIcon icon={faStore} size="lg" />}
        />
      </nav>

      <div className="px-4 py-4 border-t border-input">
        <div className="flex items-center gap-3 mb-3">
          <div className="avatar-circle w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold shrink-0">
            {user?.username?.charAt(0).toUpperCase() ?? 'U'}
          </div>
          <div className="min-w-0">
            <p className="text-primary text-sm font-medium truncate">{user?.username ?? 'Usuário'}</p>
            <p className="text-secondary text-xs truncate">{user?.email ?? ''}</p>
          </div>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-2 w-full px-3 py-2 text-sm text-secondary hover:text-error hover:bg-input rounded-md transition-colors"
          aria-label="Sair da conta"
        >
          <FontAwesomeIcon icon={faRightFromBracket} size="sm" />
          <span>Sair</span>
        </button>
      </div>
    </aside>
  );
});

Sidebar.displayName = 'Sidebar';

export default Sidebar;
