import { type FC, memo } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  tooltip?: string;
  icon: IconDefinition;
  variant?: 'default' | 'success' | 'error' | 'warning';
}

const VARIANT_CONFIG: Record<NonNullable<StatCardProps['variant']>, {
  valueClass: string;
  iconBg: string;
  iconColor: string;
  cornerGradient: string;
}> = {
  default: {
    valueClass: 'text-primary',
    iconBg: 'stat-icon-bg-default',
    iconColor: 'text-accent',
    cornerGradient: 'stat-corner-default',
  },
  success: {
    valueClass: 'text-success',
    iconBg: 'stat-icon-bg-success',
    iconColor: 'text-success',
    cornerGradient: 'stat-corner-success',
  },
  error: {
    valueClass: 'text-error',
    iconBg: 'stat-icon-bg-error',
    iconColor: 'text-error',
    cornerGradient: 'stat-corner-error',
  },
  warning: {
    valueClass: 'text-warning',
    iconBg: 'stat-icon-bg-warning',
    iconColor: 'text-warning',
    cornerGradient: 'stat-corner-warning',
  },
};

const StatCard: FC<StatCardProps> = memo(({
  title,
  value,
  subtitle,
  tooltip,
  icon,
  variant = 'default',
}) => {
  const config = VARIANT_CONFIG[variant];

  return (
    <div className="surface-card relative overflow-hidden p-4 hover:border-hover transition-all group" title={tooltip}>
      {/* Corner gradient */}
      <div className={`absolute top-0 right-0 w-20 h-20 rounded-bl-full opacity-20 ${config.cornerGradient}`} />

      <div className="relative flex items-center gap-3">
        <div className={`${config.iconBg} rounded-lg p-2.5 flex-shrink-0`}>
          <FontAwesomeIcon icon={icon} size="sm" className={config.iconColor} />
        </div>
        <div className="flex-1 min-w-0">
          <p className={`text-2xl font-bold leading-tight ${config.valueClass}`}>
            {value}
          </p>
          <p className="text-muted text-xs truncate">{title}</p>
          {subtitle && (
            <p className="text-muted text-xs mt-0.5 opacity-60">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
});

StatCard.displayName = 'StatCard';

export default StatCard;
