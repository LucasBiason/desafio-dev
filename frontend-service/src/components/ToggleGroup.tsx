import type { FC } from 'react';

interface ToggleOption {
  value: string;
  label: string;
}

interface ToggleGroupProps {
  options: ToggleOption[];
  value: string;
  onChange: (value: string) => void;
}

const ToggleGroup: FC<ToggleGroupProps> = ({ options, value, onChange }) => (
  <div className="flex items-center gap-1 surface-card p-1">
    {options.map((option) => (
      <button
        key={option.value}
        type="button"
        onClick={() => onChange(option.value)}
        className={[
          'px-3 py-1 rounded text-xs font-medium transition-colors',
          value === option.value
            ? 'bg-accent/20 text-accent'
            : 'text-muted hover:text-secondary',
        ].join(' ')}
        aria-pressed={value === option.value}
      >
        {option.label}
      </button>
    ))}
  </div>
);

export default ToggleGroup;
