import { memo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCalendarDays } from '@fortawesome/free-solid-svg-icons';

interface DateInputProps {
  value: string;
  onChange: (value: string) => void;
  label?: string;
  disabled?: boolean;
}

const DateInput: FC<DateInputProps> = memo(({ value, onChange, label, disabled }) => {
  const inputId = label ? `date-${label.toLowerCase().replace(/\s+/g, '-')}` : undefined;

  const handleIconClick = () => {
    if (inputId) {
      const el = document.getElementById(inputId) as HTMLInputElement | null;
      el?.showPicker?.();
    }
  };

  return (
    <div>
      {label && (
        <label htmlFor={inputId} className="text-muted text-xs block mb-1">
          {label}
        </label>
      )}
      <div className="relative">
        <input
          id={inputId}
          type="date"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          className="filter-input rounded-lg text-sm pl-3 pr-9 py-1.5 w-full [color-scheme:dark] [&::-webkit-calendar-picker-indicator]:hidden"
          aria-label={label}
        />
        <button
          type="button"
          tabIndex={-1}
          onClick={handleIconClick}
          className="absolute inset-y-0 right-0 flex items-center pr-3 text-muted hover:text-secondary transition-colors"
          aria-hidden="true"
        >
          <FontAwesomeIcon icon={faCalendarDays} className="text-xs" />
        </button>
      </div>
    </div>
  );
});

DateInput.displayName = 'DateInput';

export default DateInput;
