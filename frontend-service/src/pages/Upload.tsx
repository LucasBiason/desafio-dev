import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import type { FC, DragEvent, ChangeEvent } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faCloudArrowUp,
  faFile,
  faCircleCheck,
  faCircleXmark,
  faSpinner,
  faHourglass,
  faBoxOpen,
  faMagnifyingGlass,
  faChevronUp,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faAnglesLeft,
  faAnglesRight,
  faXmark,
} from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import { uploadService } from '../services/uploadService';
import type { UploadResponse } from '../services/uploadService';

// Map API status values to Portuguese labels
const STATUS_LABELS: Record<UploadResponse['status'], string> = {
  pending: 'Pendente',
  processing: 'Processando',
  completed: 'Concluído',
  failed: 'Falhou',
};

// Tailwind classes for each status badge
const STATUS_BADGE_CLASSES: Record<UploadResponse['status'], string> = {
  pending: 'bg-[rgba(255,184,0,0.15)] text-[#FFB800]',
  processing: 'bg-[rgba(79,250,123,0.15)] text-[#4FFA7B]',
  completed: 'bg-[rgba(2,190,59,0.15)] text-[#02BE3B]',
  failed: 'bg-[rgba(255,68,68,0.15)] text-[#FF4444]',
};

// Icon for each status
const STATUS_ICONS: Record<UploadResponse['status'], typeof faHourglass> = {
  pending: faHourglass,
  processing: faSpinner,
  completed: faCircleCheck,
  failed: faCircleXmark,
};

// Status chip definitions: API value, label, and bycoders_ brand color
const STATUS_CHIPS: { value: UploadResponse['status']; label: string; color: string }[] = [
  { value: 'pending', label: 'Pendente', color: '#FFB800' },
  { value: 'processing', label: 'Processando', color: '#4FFA7B' },
  { value: 'completed', label: 'Concluído', color: '#02BE3B' },
  { value: 'failed', label: 'Falhou', color: '#FF4444' },
];

// Available page size choices for the table toolbar
const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

// Auto-refresh interval in milliseconds
const POLL_INTERVAL_MS = 10_000;

// Columns that support sorting
type SortKey = 'original_filename' | 'status' | 'total_transactions' | 'created_at';
type SortDir = 'asc' | 'desc';

// Format bytes into human-readable string
function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Format ISO date string to DD/MM/YYYY HH:MM
function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

// Chip component matching the portfolio multi-select pattern
interface ChipProps {
  label: string;
  color: string;
  active: boolean;
  onClick: () => void;
}

const Chip: FC<ChipProps> = ({ label, color, active, onClick }) => (
  <button
    type="button"
    onClick={onClick}
    className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium transition-all ${
      active
        ? 'text-white border'
        : 'bg-transparent text-[#D8D8D8] border border-white/10 hover:border-white/30 hover:text-white'
    }`}
    style={active ? { backgroundColor: `${color}30`, color, borderColor: `${color}50` } : {}}
    aria-pressed={active}
  >
    <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
    {label}
  </button>
);

interface StatusBadgeProps {
  status: UploadResponse['status'];
}

const StatusBadge: FC<StatusBadgeProps> = ({ status }) => (
  <span
    className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap ${STATUS_BADGE_CLASSES[status]}`}
  >
    <FontAwesomeIcon
      icon={STATUS_ICONS[status]}
      className={status === 'processing' ? 'animate-spin' : ''}
      aria-hidden="true"
    />
    {STATUS_LABELS[status]}
  </span>
);

interface SortIconProps {
  columnKey: SortKey;
  sortKey: SortKey;
  sortDir: SortDir;
}

// Renders the sort direction arrow for a column header
const SortIcon: FC<SortIconProps> = ({ columnKey, sortKey, sortDir }) => {
  if (columnKey !== sortKey) {
    return (
      <FontAwesomeIcon
        icon={faChevronDown}
        className="ml-1 text-[#3a3a3a] text-[10px]"
        aria-hidden="true"
      />
    );
  }
  return (
    <FontAwesomeIcon
      icon={sortDir === 'asc' ? faChevronUp : faChevronDown}
      className="ml-1 text-[#4FFA7B] text-[10px]"
      aria-hidden="true"
    />
  );
};

// Skeleton row shown during loading
const SkeletonRow: FC = () => (
  <tr className="border-b border-white/5 animate-pulse">
    {[60, 80, 50, 120, 100].map((w, i) => (
      <td key={i} className="px-4 py-3">
        <div className="h-3 bg-[#2a2a2a] rounded" style={{ width: `${w}%` }} />
      </td>
    ))}
  </tr>
);

const Upload: FC = () => {
  // Upload zone state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // DataTable state
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[1]);

  // Multi-select status chip filter
  const [selectedStatuses, setSelectedStatuses] = useState<UploadResponse['status'][]>([]);

  // Filename filter with debounce (input value vs applied value)
  const [filenameInput, setFilenameInput] = useState('');
  const [filenameFilter, setFilenameFilter] = useState('');

  // Date range filters
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  // Debounce filename input: apply after 300ms of inactivity
  useEffect(() => {
    const timer = setTimeout(() => setFilenameFilter(filenameInput), 300);
    return () => clearTimeout(timer);
  }, [filenameInput]);

  // Fetch uploads from backend using all active filters
  const loadUploads = useCallback(
    async (statuses: UploadResponse['status'][], filename: string, from: string, to: string) => {
      try {
        setLoading(true);
        const data = await uploadService.list(1, 1000, {
          status: statuses.length > 0 ? statuses.join(',') : undefined,
          filename: filename || undefined,
          date_from: from || undefined,
          date_to: to || undefined,
        });
        setUploads(data.results);
      } catch {
        setUploads([]);
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  // Refetch whenever any filter changes, and reset to page 1
  useEffect(() => {
    setCurrentPage(1);
    loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
  }, [selectedStatuses, filenameFilter, dateFrom, dateTo, loadUploads]);

  // Auto-refresh polling to catch status transitions (pending -> processing -> completed)
  useEffect(() => {
    const interval = setInterval(() => {
      loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadUploads, selectedStatuses, filenameFilter, dateFrom, dateTo]);

  // Toggle a status chip: add if absent, remove if already selected
  const handleChipToggle = (value: UploadResponse['status']) => {
    setSelectedStatuses((prev) =>
      prev.includes(value) ? prev.filter((s) => s !== value) : [...prev, value],
    );
  };

  // Clear all status chips at once
  const handleClearStatuses = () => {
    setSelectedStatuses([]);
  };

  // Apply client-side sorting on the results returned by the backend
  const sortedUploads = useMemo(() => {
    return [...uploads].sort((a, b) => {
      let valA: string | number = a[sortKey] ?? '';
      let valB: string | number = b[sortKey] ?? '';

      if (sortKey === 'total_transactions') {
        valA = Number(valA);
        valB = Number(valB);
        return sortDir === 'asc'
          ? (valA as number) - (valB as number)
          : (valB as number) - (valA as number);
      }

      // String comparison for other columns
      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [uploads, sortKey, sortDir]);

  // Pagination calculations derived from sorted data
  const totalFiltered = sortedUploads.length;
  const totalPages = Math.max(1, Math.ceil(totalFiltered / pageSize));
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalFiltered);
  const pageRows = sortedUploads.slice(startIndex, endIndex);

  // Compute visible page buttons (max 5 around current page)
  const pageNumbers = useMemo(() => {
    const range: number[] = [];
    const delta = 2;
    const left = Math.max(1, safePage - delta);
    const right = Math.min(totalPages, safePage + delta);
    for (let i = left; i <= right; i++) range.push(i);
    return range;
  }, [safePage, totalPages]);

  const handleSortColumn = (key: SortKey) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  // Shared header cell renderer for sortable columns
  const SortableHeader: FC<{ label: string; colKey: SortKey }> = ({ label, colKey }) => (
    <th
      scope="col"
      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] cursor-pointer hover:text-white select-none transition-colors"
      onClick={() => handleSortColumn(colKey)}
      aria-sort={sortKey === colKey ? (sortDir === 'asc' ? 'ascending' : 'descending') : 'none'}
    >
      <span className="inline-flex items-center gap-1">
        {label}
        <SortIcon columnKey={colKey} sortKey={sortKey} sortDir={sortDir} />
      </span>
    </th>
  );

  // Upload zone handlers
  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    handleFileChange(file);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files?.[0] ?? null;
    handleFileChange(file);
  };

  const handleZoneClick = () => {
    fileInputRef.current?.click();
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      await uploadService.upload(selectedFile);
      setSuccessMessage(`Arquivo "${selectedFile.name}" enviado com sucesso!`);
      setSelectedFile(null);
      // Reset the hidden file input so the same file can be selected again
      if (fileInputRef.current) fileInputRef.current.value = '';
      // Refresh the DataTable to show the new upload
      await loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
    } catch {
      setErrorMessage('Ocorreu um erro ao enviar o arquivo. Tente novamente.');
    } finally {
      setUploading(false);
    }
  };

  // Determine which empty-state message to show based on active filters
  const emptyStateMessage = useMemo(() => {
    if (selectedStatuses.length > 0 || filenameFilter || dateFrom || dateTo) {
      return 'Nenhum resultado para os filtros selecionados.';
    }
    return 'Importe um arquivo CNAB para começar.';
  }, [selectedStatuses, filenameFilter, dateFrom, dateTo]);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h2 className="text-[#FFFFFF] text-xl font-semibold">Upload de Arquivo CNAB</h2>
          <p className="text-[#D8D8D8] text-sm mt-1">
            Importe arquivos CNAB para processar transações.
          </p>
        </div>

        {/* Drop zone card */}
        <div className="bg-[#1e1e1e] border border-[#2a2a2a] rounded-xl p-5">
          {/* Hidden file input — accepts .txt and .cnab */}
          <input
            ref={fileInputRef}
            type="file"
            accept=".txt,.cnab"
            className="hidden"
            aria-hidden="true"
            onChange={handleInputChange}
          />

          {/* Drag and drop area */}
          <div
            role="button"
            tabIndex={0}
            aria-label="Área de drag and drop para selecionar arquivo CNAB"
            onClick={handleZoneClick}
            onKeyDown={(e) => e.key === 'Enter' && handleZoneClick()}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={[
              'flex flex-col items-center justify-center text-center p-10 rounded-lg border-2 border-dashed cursor-pointer transition-colors',
              isDragOver
                ? 'border-[#4FFA7B] bg-[rgba(79,250,123,0.08)]'
                : 'border-[#2a2a2a] hover:border-[#3a3a3a] bg-[#171616]',
            ].join(' ')}
          >
            <FontAwesomeIcon
              icon={faCloudArrowUp}
              className={`text-5xl mb-4 ${isDragOver ? 'text-[#4FFA7B]' : 'text-[#3a3a3a]'}`}
            />
            <p className="text-[#D8D8D8] font-medium">
              Arraste um arquivo CNAB aqui ou clique para selecionar
            </p>
            <p className="text-[#D8D8D8] text-xs mt-1">Formatos aceitos: .txt, .cnab</p>
          </div>

          {/* File preview and upload button — shown once a file is selected */}
          {selectedFile && !uploading && !successMessage && (
            <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-[#171616] rounded-lg border border-[#2a2a2a]">
              <div className="flex items-center gap-3 min-w-0">
                <FontAwesomeIcon icon={faFile} className="text-[#4FFA7B] shrink-0" />
                <div className="min-w-0">
                  <p className="text-[#FFFFFF] text-sm font-medium truncate">{selectedFile.name}</p>
                  <p className="text-[#D8D8D8] text-xs">{formatBytes(selectedFile.size)}</p>
                </div>
              </div>
              <button
                onClick={handleUpload}
                className="shrink-0 px-4 py-2 bg-[#02BE3B] hover:bg-[#029E32] text-[#FFFFFF] text-sm font-medium rounded-md transition-colors"
                aria-label={`Enviar arquivo ${selectedFile.name}`}
              >
                Enviar
              </button>
            </div>
          )}

          {/* Uploading state */}
          {uploading && (
            <div className="mt-4 flex items-center gap-3 p-4 bg-[#171616] rounded-lg border border-[#2a2a2a]">
              <FontAwesomeIcon icon={faSpinner} className="text-[#4FFA7B] animate-spin" />
              <p className="text-[#D8D8D8] text-sm">Enviando...</p>
            </div>
          )}

          {/* Success feedback */}
          {successMessage && (
            <div className="mt-4 flex items-center gap-3 p-4 bg-[rgba(2,190,59,0.1)] rounded-lg border border-[rgba(2,190,59,0.3)]">
              <FontAwesomeIcon icon={faCircleCheck} className="text-[#02BE3B] shrink-0" />
              <p className="text-[#02BE3B] text-sm">{successMessage}</p>
            </div>
          )}

          {/* Error feedback */}
          {errorMessage && (
            <div className="mt-4 flex items-center gap-3 p-4 bg-[rgba(255,68,68,0.1)] rounded-lg border border-[rgba(255,68,68,0.3)]">
              <FontAwesomeIcon icon={faCircleXmark} className="text-[#FF4444] shrink-0" />
              <p className="text-[#FF4444] text-sm">{errorMessage}</p>
            </div>
          )}
        </div>

        {/* History section title */}
        <h3 className="text-[#FFFFFF] text-base font-semibold">Histórico de Uploads</h3>

        {/* Filter panel: status chips + additional filters */}
        <div className="bg-[#1e1e1e] border border-white/5 rounded-xl p-4 space-y-4">
          {/* Status chip row */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[#898989] mb-2">
              Status
            </p>
            <div className="flex flex-wrap items-center gap-2">
              {STATUS_CHIPS.map((chip) => (
                <Chip
                  key={chip.value}
                  label={chip.label}
                  color={chip.color}
                  active={selectedStatuses.includes(chip.value)}
                  onClick={() => handleChipToggle(chip.value)}
                />
              ))}

              {/* Clear button: only visible when at least one chip is active */}
              {selectedStatuses.length > 0 && (
                <button
                  type="button"
                  onClick={handleClearStatuses}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium text-[#898989] hover:text-white border border-white/5 hover:border-white/20 transition-all"
                  aria-label="Limpar filtros de status"
                >
                  <FontAwesomeIcon icon={faXmark} className="text-[10px]" aria-hidden="true" />
                  Limpar
                </button>
              )}
            </div>
          </div>

          {/* Additional filters row: filename search + date range */}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-[#898989] mb-2">
              Filtros
            </p>
            <div className="flex flex-col sm:flex-row gap-3">
              {/* Filename search with debounce */}
              <div className="relative flex-1 max-w-sm">
                <span className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-[#898989]">
                  <FontAwesomeIcon icon={faMagnifyingGlass} className="text-xs" aria-hidden="true" />
                </span>
                <input
                  type="search"
                  placeholder="Nome do arquivo..."
                  value={filenameInput}
                  onChange={(e) => setFilenameInput(e.target.value)}
                  className="w-full bg-[#171616] border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-sm text-white placeholder-[#898989] focus:outline-none focus:ring-1 focus:ring-[#4FFA7B]"
                  aria-label="Buscar por nome do arquivo"
                />
              </div>

              {/* Date from */}
              <input
                type="date"
                value={dateFrom}
                onChange={(e) => setDateFrom(e.target.value)}
                className="bg-[#171616] border border-white/10 rounded-lg text-sm text-white px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-[#4FFA7B] [color-scheme:dark]"
                aria-label="Data início"
                title="Data início"
              />

              {/* Date to */}
              <input
                type="date"
                value={dateTo}
                onChange={(e) => setDateTo(e.target.value)}
                className="bg-[#171616] border border-white/10 rounded-lg text-sm text-white px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-[#4FFA7B] [color-scheme:dark]"
                aria-label="Data fim"
                title="Data fim"
              />
            </div>
          </div>
        </div>

        {/* DataTable container */}
        <div className="bg-[#1e1e1e] border border-white/5 rounded-xl overflow-hidden">

          {/* Table toolbar: page size selector on the right */}
          <div className="flex items-center justify-end gap-3 px-4 py-3 border-b border-white/5">
            {/* Page size selector */}
            <div className="flex items-center gap-2 shrink-0">
              <span className="text-[#898989] text-xs">Exibir</span>
              <select
                value={pageSize}
                onChange={handlePageSizeChange}
                className="bg-[#171616] border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-[#4FFA7B] cursor-pointer"
                aria-label="Itens por página"
              >
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <option key={size} value={size}>
                    {size}
                  </option>
                ))}
              </select>
              <span className="text-[#898989] text-xs">por página</span>
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full" aria-label="Histórico de uploads">
              <thead>
                <tr className="border-b border-white/5 bg-[#171616]/50">
                  <SortableHeader label="Arquivo" colKey="original_filename" />
                  <SortableHeader label="Status" colKey="status" />
                  <SortableHeader label="Transações" colKey="total_transactions" />
                  {/* Error column is not sortable */}
                  <th
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] select-none"
                  >
                    Erro
                  </th>
                  <SortableHeader label="Data de Upload" colKey="created_at" />
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  // Show skeleton rows while fetching
                  Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
                ) : pageRows.length === 0 ? (
                  // Empty state spanning all columns
                  <tr>
                    <td colSpan={5} className="px-4 py-16 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <FontAwesomeIcon
                          icon={faBoxOpen}
                          className="text-[#D8D8D8] text-4xl opacity-30"
                          aria-hidden="true"
                        />
                        <p className="text-[#D8D8D8] font-medium">Nenhum upload encontrado</p>
                        <p className="text-[#898989] text-sm">{emptyStateMessage}</p>
                      </div>
                    </td>
                  </tr>
                ) : (
                  pageRows.map((upload) => (
                    <tr
                      key={upload.id}
                      className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors"
                    >
                      {/* Filename */}
                      <td
                        className="px-4 py-3 text-sm text-[#FFFFFF] font-medium max-w-[200px] truncate"
                        title={upload.original_filename}
                      >
                        {upload.original_filename}
                      </td>

                      {/* Status badge */}
                      <td className="px-4 py-3">
                        <StatusBadge status={upload.status} />
                      </td>

                      {/* Transaction count */}
                      <td className="px-4 py-3 text-sm text-[#D8D8D8] tabular-nums">
                        {upload.total_transactions}
                      </td>

                      {/* Error message — truncated with title tooltip */}
                      <td
                        className="px-4 py-3 text-sm text-[#FF4444] max-w-[200px] truncate"
                        title={upload.error_message ?? undefined}
                      >
                        {upload.error_message ? (
                          <span className="truncate block">{upload.error_message}</span>
                        ) : (
                          <span className="text-[#898989]">—</span>
                        )}
                      </td>

                      {/* Upload date */}
                      <td className="px-4 py-3 text-sm text-[#D8D8D8] tabular-nums whitespace-nowrap">
                        {formatDate(upload.created_at)}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Table footer: record count on left, pagination on right */}
          {!loading && (
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 py-3 border-t border-white/5">
              {/* Record range summary */}
              <p className="text-xs text-[#898989]">
                {totalFiltered === 0
                  ? 'Nenhum registro encontrado'
                  : `Exibindo ${startIndex + 1}–${endIndex} de ${totalFiltered} registro${totalFiltered !== 1 ? 's' : ''}`}
              </p>

              {/* Page navigation buttons */}
              {totalPages > 1 && (
                <div className="flex items-center gap-1" role="navigation" aria-label="Paginação">
                  {/* First page */}
                  <button
                    onClick={() => setCurrentPage(1)}
                    disabled={safePage === 1}
                    className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label="Primeira página"
                  >
                    <FontAwesomeIcon icon={faAnglesLeft} className="text-xs" aria-hidden="true" />
                  </button>

                  {/* Previous page */}
                  <button
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={safePage === 1}
                    className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label="Página anterior"
                  >
                    <FontAwesomeIcon icon={faChevronLeft} className="text-xs" aria-hidden="true" />
                  </button>

                  {/* Numbered page buttons */}
                  {pageNumbers.map((num) => (
                    <button
                      key={num}
                      onClick={() => setCurrentPage(num)}
                      className={[
                        'w-8 h-8 flex items-center justify-center rounded-lg text-xs transition-colors',
                        num === safePage
                          ? 'bg-[#02BE3B] text-white font-semibold'
                          : 'text-[#898989] hover:text-white hover:bg-white/5',
                      ].join(' ')}
                      aria-label={`Página ${num}`}
                      aria-current={num === safePage ? 'page' : undefined}
                    >
                      {num}
                    </button>
                  ))}

                  {/* Next page */}
                  <button
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={safePage === totalPages}
                    className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label="Próxima página"
                  >
                    <FontAwesomeIcon icon={faChevronRight} className="text-xs" aria-hidden="true" />
                  </button>

                  {/* Last page */}
                  <button
                    onClick={() => setCurrentPage(totalPages)}
                    disabled={safePage === totalPages}
                    className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                    aria-label="Última página"
                  >
                    <FontAwesomeIcon icon={faAnglesRight} className="text-xs" aria-hidden="true" />
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Upload;
