import { memo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faHourglass,
  faSpinner,
  faCircleCheck,
  faCircleXmark,
} from '@fortawesome/free-solid-svg-icons';
import type { UploadStatus } from '../../types/upload';

const BADGE_CLASS: Record<UploadStatus, string> = {
  pending: 'badge badge-pending',
  processing: 'badge badge-processing',
  completed: 'badge badge-completed',
  failed: 'badge badge-failed',
};

const STATUS_LABELS: Record<UploadStatus, string> = {
  pending: 'Pendente',
  processing: 'Processando',
  completed: 'Concluído',
  failed: 'Falhou',
};

const STATUS_ICONS: Record<UploadStatus, typeof faHourglass> = {
  pending: faHourglass,
  processing: faSpinner,
  completed: faCircleCheck,
  failed: faCircleXmark,
};

interface StatusBadgeProps {
  status: UploadStatus;
}

const StatusBadge: FC<StatusBadgeProps> = memo(({ status }) => (
  <span className={BADGE_CLASS[status]}>
    <FontAwesomeIcon
      icon={STATUS_ICONS[status]}
      className={status === 'processing' ? 'animate-spin' : ''}
      aria-hidden="true"
    />
    {STATUS_LABELS[status]}
  </span>
));

StatusBadge.displayName = 'StatusBadge';

export default StatusBadge;
