import { memo } from 'react';
import type { FC } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const PAGE_TITLES: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/upload': 'Upload de Arquivo',
  '/stores': 'Lojas',
  '/history': 'Histórico',
};

const Header: FC = memo(() => {
  const { user } = useAuth();
  const location = useLocation();

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'CNAB Parser';

  return (
    <header className="sticky top-0 z-30 h-16 bg-[#3b4252] border-b border-[#434c5e] flex items-center justify-between px-6">
      <div>
        <h2 className="text-[#eceff4] text-base font-semibold leading-none">{pageTitle}</h2>
        <p className="text-[#d8dee9] text-xs mt-1">
          <span className="text-[#81a1c1]">CNAB Parser</span>
          <span className="mx-1 text-[#d8dee9]">/</span>
          <span className="text-[#eceff4]">{pageTitle}</span>
        </p>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-[#d8dee9] text-sm">
          Olá,{' '}
          <span className="text-[#88c0d0] font-medium">{user?.username ?? 'Usuário'}</span>
        </span>
      </div>
    </header>
  );
});

Header.displayName = 'Header';

export default Header;
