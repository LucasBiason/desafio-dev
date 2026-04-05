import { type FC, memo } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: IconDefinition;
  variant?: 'default' | 'success' | 'error' | 'warning';
}

const variantValueClass: Record<NonNullable<StatCardProps['variant']>, string> = {
  default: 'text-primary',
  success: 'text-success',
  error: 'text-error',
  warning: 'text-warning',
};

const variantIconClass: Record<NonNullable<StatCardProps['variant']>, string> = {
  default: 'stat-card-icon-default',
  success: 'stat-card-icon-success',
  error: 'stat-card-icon-error',
  warning: 'stat-card-icon-warning',
};

const StatCard: FC<StatCardProps> = memo(({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
}) => {
  return (
    <div className="surface-card p-5 flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <span className="text-muted text-xs font-semibold uppercase tracking-wider">
          {title}
        </span>
        <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${variantIconClass[variant]}`}>
          <FontAwesomeIcon icon={icon} />
        </div>
      </div>
      <div>
        <span className={`text-2xl font-bold ${variantValueClass[variant]}`}>
          {value}
        </span>
        {subtitle && (
          <p className="text-muted text-xs mt-1">{subtitle}</p>
        )}
      </div>
    </div>
  );
});

StatCard.displayName = 'StatCard';

export default StatCard;
