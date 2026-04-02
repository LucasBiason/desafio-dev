import { useState, useEffect, useCallback, useMemo } from 'react';
import type { FC, ChangeEvent } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faSpinner,
  faHourglass,
  faCircleCheck,
  faCircleXmark,
  faBoxOpen,
  faMagnifyingGlass,
  faChevronUp,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faAnglesLeft,
  faAnglesRight,
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

// Status filter options shown in the dropdown
const STATUS_OPTIONS: { value: string; label: string }[] = [
  { value: '', label: 'Todos os status' },
  { value: 'pending', label: 'Pendente' },
  { value: 'processing', label: 'Processando' },
  { value: 'completed', label: 'Concluído' },
  { value: 'failed', label: 'Falhou' },
];

// Available page size choices for the table toolbar
const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

// Columns that support sorting
type SortKey = 'original_filename' | 'status' | 'total_transactions' | 'created_at';
type SortDir = 'asc' | 'desc';

// Format ISO date string to DD/MM/YYYY HH:MM
function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

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
        <div className={`h-3 bg-[#2a2a2a] rounded`} style={{ width: `${w}%` }} />
      </td>
    ))}
  </tr>
);

const History: FC = () => {
  // Data fetched from the API (filtered by status via backend)
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Status filter — triggers a backend refetch when changed
  const [statusFilter, setStatusFilter] = useState('');

  // Client-side text search across filename and status label
  const [searchQuery, setSearchQuery] = useState('');

  // Client-side sort state
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');

  // Client-side pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[1]);

  // Fetch all uploads for the selected status from the API
  // We use a large page_size (1000) so client-side search and pagination work on the full dataset
  const loadUploads = useCallback(async (status: string) => {
    try {
      setLoading(true);
      const data = await uploadService.list(1, 1000, status || undefined);
      setUploads(data.results);
    } catch {
      setUploads([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUploads(statusFilter);
    setCurrentPage(1);
    setSearchQuery('');
  }, [statusFilter, loadUploads]);

  // Apply text search filter client-side
  const filteredUploads = useMemo(() => {
    const q = searchQuery.trim().toLowerCase();
    if (!q) return uploads;
    return uploads.filter(
      (u) =>
        u.original_filename.toLowerCase().includes(q) ||
        STATUS_LABELS[u.status].toLowerCase().includes(q),
    );
  }, [uploads, searchQuery]);

  // Apply client-side sorting
  const sortedUploads = useMemo(() => {
    return [...filteredUploads].sort((a, b) => {
      let valA: string | number = a[sortKey] ?? '';
      let valB: string | number = b[sortKey] ?? '';

      if (sortKey === 'total_transactions') {
        valA = Number(valA);
        valB = Number(valB);
        return sortDir === 'asc' ? (valA as number) - (valB as number) : (valB as number) - (valA as number);
      }

      // String comparison for other columns
      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [filteredUploads, sortKey, sortDir]);

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

  const handleSearchChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  const handleStatusChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setStatusFilter(e.target.value);
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

  return (
    <Layout>
      <div className="space-y-6">
        {/* Page header */}
        <div>
          <h2 className="text-[#FFFFFF] text-xl font-semibold">Histórico de Uploads</h2>
          <p className="text-[#D8D8D8] text-sm mt-1">
            Consulte o histórico completo de uploads processados.
          </p>
        </div>

        {/* Status filter — above the table, triggers backend refetch */}
        <div className="flex items-center gap-3">
          <label htmlFor="status-filter" className="text-[#D8D8D8] text-sm shrink-0">
            Status:
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={handleStatusChange}
            className="bg-[#2a2a2a] border border-[#3a3a3a] text-[#FFFFFF] text-sm rounded-md px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-[#4FFA7B] cursor-pointer"
            aria-label="Filtrar por status"
          >
            {STATUS_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        {/* DataTable container */}
        <div className="bg-[#1e1e1e] border border-white/5 rounded-xl overflow-hidden">

          {/* Table toolbar: search on left, page size on right */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 py-3 border-b border-white/5">
            {/* Search input */}
            <div className="relative flex-1 max-w-xs">
              <span className="absolute inset-y-0 left-3 flex items-center pointer-events-none text-[#898989]">
                <FontAwesomeIcon icon={faMagnifyingGlass} className="text-xs" aria-hidden="true" />
              </span>
              <input
                type="search"
                placeholder="Buscar por arquivo ou status..."
                value={searchQuery}
                onChange={handleSearchChange}
                className="w-full bg-[#171616] border border-white/10 rounded-lg pl-8 pr-3 py-2 text-sm text-white placeholder-[#898989] focus:outline-none focus:ring-1 focus:ring-[#4FFA7B]"
                aria-label="Buscar uploads"
              />
            </div>

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
                        <p className="text-[#D8D8D8] font-medium">
                          Nenhum upload encontrado
                        </p>
                        <p className="text-[#898989] text-sm">
                          {searchQuery
                            ? 'Nenhum resultado para a busca realizada.'
                            : statusFilter
                            ? 'Nenhum upload com o status selecionado.'
                            : 'Importe um arquivo CNAB para começar.'}
                        </p>
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

export default History;
