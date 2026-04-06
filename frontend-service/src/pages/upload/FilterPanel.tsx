import { memo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass, faXmark } from '@fortawesome/free-solid-svg-icons';
import DateInput from '../../components/DateInput';
import FilterChip from '../../components/FilterChip';
import type { UploadStatus } from '../../types/upload';

const STATUS_CHIPS: { value: UploadStatus; label: string; colorClass: string; dotClass: string }[] = [
  { value: 'pending', label: 'Pendente', colorClass: 'chip-pending', dotClass: 'dot-pending' },
  { value: 'processing', label: 'Processando', colorClass: 'chip-processing', dotClass: 'dot-processing' },
  { value: 'completed', label: 'Concluído', colorClass: 'chip-completed', dotClass: 'dot-completed' },
  { value: 'failed', label: 'Falhou', colorClass: 'chip-failed', dotClass: 'dot-failed' },
];

interface FilterPanelProps {
  selectedStatuses: UploadStatus[];
  onChipToggle: (value: UploadStatus) => void;
  onClearStatuses: () => void;
  filenameInput: string;
  onFilenameChange: (value: string) => void;
  dateFrom: string;
  onDateFromChange: (value: string) => void;
  dateTo: string;
  onDateToChange: (value: string) => void;
}

const FilterPanel: FC<FilterPanelProps> = memo(({
  selectedStatuses,
  onChipToggle,
  onClearStatuses,
  filenameInput,
  onFilenameChange,
  dateFrom,
  onDateFromChange,
  dateTo,
  onDateToChange,
}) => (
  <div className="bg-surface border border-white/5 rounded-xl p-4 space-y-4">
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">
        Status
      </p>
      <div className="flex flex-wrap items-center gap-2">
        {STATUS_CHIPS.map((chip) => (
          <FilterChip
            key={chip.value}
            label={chip.label}
            colorClass={chip.colorClass}
            dotClass={chip.dotClass}
            active={selectedStatuses.includes(chip.value)}
            onClick={() => onChipToggle(chip.value)}
          />
        ))}

        {selectedStatuses.length > 0 && (
          <button
            type="button"
            onClick={onClearStatuses}
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium text-muted hover:text-white border border-white/5 hover:border-white/20 transition-all"
            aria-label="Limpar filtros de status"
          >
            <FontAwesomeIcon icon={faXmark} className="text-[10px]" aria-hidden="true" />
            Limpar
          </button>
        )}
      </div>
    </div>

    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-2">
        Filtros
      </p>
      <div className="flex flex-col sm:flex-row gap-3 items-end">
        <div className="flex-1 max-w-sm">
          <label className="text-muted text-xs block mb-1">Nome do arquivo</label>
          <div className="relative">
            <FontAwesomeIcon
              icon={faMagnifyingGlass}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-muted text-xs pointer-events-none"
              aria-hidden="true"
            />
            <input
              type="search"
              placeholder="Buscar..."
              value={filenameInput}
              onChange={(e) => onFilenameChange(e.target.value)}
              className="w-full filter-input rounded-lg pl-8 pr-3 py-1.5 text-sm placeholder-muted [color-scheme:dark]"
              aria-label="Buscar por nome do arquivo"
            />
          </div>
        </div>

        <DateInput value={dateFrom} onChange={onDateFromChange} label="Data início" />
        <DateInput value={dateTo} onChange={onDateToChange} label="Data fim" />
      </div>
    </div>
  </div>
));

FilterPanel.displayName = 'FilterPanel';

export default FilterPanel;
