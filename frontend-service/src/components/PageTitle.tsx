import type { FC } from 'react';

interface PageTitleProps {
  title: string;
  subtitle?: string;
}

const PageTitle: FC<PageTitleProps> = ({ title, subtitle }) => (
  <div>
    <h2 className="page-title">{title}</h2>
    {subtitle && <p className="page-subtitle">{subtitle}</p>}
  </div>
);

export default PageTitle;
