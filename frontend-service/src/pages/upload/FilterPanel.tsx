import { memo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMagnifyingGlass, faXmark } from '@fortawesome/free-solid-svg-icons';
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
  <div className="bg-[#1e1e1e] border border-white/5 rounded-xl p-4 space-y-4">
    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-[#898989] mb-2">
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
            className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium text-[#898989] hover:text-white border border-white/5 hover:border-white/20 transition-all"
            aria-label="Limpar filtros de status"
          >
            <FontAwesomeIcon icon={faXmark} className="text-[10px]" aria-hidden="true" />
            Limpar
          </button>
        )}
      </div>
    </div>

    <div>
      <p className="text-xs font-semibold uppercase tracking-wider text-[#898989] mb-2">
        Filtros
      </p>
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 max-w-sm">
          <span className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-[#898989]">
            <FontAwesomeIcon icon={faMagnifyingGlass} className="text-xs" aria-hidden="true" />
          </span>
          <input
            type="search"
            placeholder="Nome do arquivo..."
            value={filenameInput}
            onChange={(e) => onFilenameChange(e.target.value)}
            className="w-full filter-input rounded-lg pl-8 pr-3 py-1.5 text-sm placeholder-[#898989] [color-scheme:dark]"
            aria-label="Buscar por nome do arquivo"
          />
        </div>

        <input
          type="date"
          value={dateFrom}
          onChange={(e) => onDateFromChange(e.target.value)}
          className="filter-input rounded-lg text-sm px-3 py-1.5 [color-scheme:dark]"
          aria-label="Data início"
          title="Data início"
        />

        <input
          type="date"
          value={dateTo}
          onChange={(e) => onDateToChange(e.target.value)}
          className="filter-input rounded-lg text-sm px-3 py-1.5 [color-scheme:dark]"
          aria-label="Data fim"
          title="Data fim"
        />
      </div>
    </div>
  </div>
));

FilterPanel.displayName = 'FilterPanel';

export default FilterPanel;
