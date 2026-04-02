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
    <header className="sticky top-0 z-30 h-16 bg-[#1e1e1e] border-b border-[#2a2a2a] flex items-center justify-between px-6">
      <div>
        <h2 className="text-[#FFFFFF] text-base font-semibold leading-none">{pageTitle}</h2>
        <p className="text-[#D8D8D8] text-xs mt-1">
          <span className="text-[#4FFA7B]">CNAB Parser</span>
          <span className="mx-1 text-[#D8D8D8]">/</span>
          <span className="text-[#FFFFFF]">{pageTitle}</span>
        </p>
      </div>

      <div className="flex items-center gap-3">
        <span className="text-[#D8D8D8] text-sm">
          Olá,{' '}
          <span className="text-[#4FFA7B] font-medium">{user?.username ?? 'Usuário'}</span>
        </span>
      </div>
    </header>
  );
});

Header.displayName = 'Header';

export default Header;
