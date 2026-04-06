import { memo } from 'react';
import type { FC } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/upload': 'Upload de Arquivos',
  '/stores': 'Lojas',
};

const Header: FC = memo(() => {
  const { user } = useAuth();
  const location = useLocation();

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'CNAB Parser';

  return (
    <header className="header-bar sticky top-0 z-30 h-16 flex items-center justify-between px-6">
      <div>
        <h2 className="text-primary text-base font-semibold leading-none">{pageTitle}</h2>
        <p className="text-secondary text-xs mt-1">
          <span className="text-accent">CNAB Parser</span>
          <span className="mx-1 text-secondary">/</span>
          <span className="text-primary">{pageTitle}</span>
        </p>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-secondary text-sm">
          Olá,{' '}
          <span className="text-accent font-medium">{user?.username ?? 'Usuário'}</span>
        </span>
      </div>
    </header>
  );
});

Header.displayName = 'Header';

export default Header;
