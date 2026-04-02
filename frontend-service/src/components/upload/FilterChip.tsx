import { memo } from 'react';
import type { FC } from 'react';

interface FilterChipProps {
  label: string;
  colorClass: string;
  dotClass: string;
  active: boolean;
  onClick: () => void;
}

const FilterChip: FC<FilterChipProps> = memo(({ label, colorClass, dotClass, active, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`chip${active ? ` chip-active ${colorClass}` : ''}`}
    aria-pressed={active}
  >
    <span
      className={`w-2 h-2 rounded-full flex-shrink-0 ${dotClass}`}
      aria-hidden="true"
    />
    {label}
  </button>
));

FilterChip.displayName = 'FilterChip';

export default FilterChip;
