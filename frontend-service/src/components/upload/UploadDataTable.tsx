import { useState, useMemo, memo } from 'react';
import type { FC, ChangeEvent } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faBoxOpen,
  faChevronUp,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faAnglesLeft,
  faAnglesRight,
} from '@fortawesome/free-solid-svg-icons';
import StatusBadge from './StatusBadge';
import type { UploadResponse } from '../../types/upload';

type SortKey = 'original_filename' | 'status' | 'total_transactions' | 'created_at';
type SortDir = 'asc' | 'desc';

const PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface SortIconProps {
  columnKey: SortKey;
  sortKey: SortKey;
  sortDir: SortDir;
}

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

const SKELETON_WIDTHS = ['w-[60%]', 'w-[80%]', 'w-[50%]', 'w-[120px]', 'w-[100px]'];

const SkeletonRow: FC = () => (
  <tr className="border-b border-white/5 animate-pulse">
    {SKELETON_WIDTHS.map((wClass, i) => (
      <td key={i} className="px-4 py-3">
        <div className={`h-3 bg-[#2a2a2a] rounded ${wClass}`} />
      </td>
    ))}
  </tr>
);

interface UploadDataTableProps {
  uploads: UploadResponse[];
  loading: boolean;
  emptyStateMessage: string;
}

const UploadDataTable: FC<UploadDataTableProps> = memo(({ uploads, loading, emptyStateMessage }) => {
  const [sortKey, setSortKey] = useState<SortKey>('created_at');
  const [sortDir, setSortDir] = useState<SortDir>('desc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(PAGE_SIZE_OPTIONS[1]);

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

      valA = String(valA).toLowerCase();
      valB = String(valB).toLowerCase();
      if (valA < valB) return sortDir === 'asc' ? -1 : 1;
      if (valA > valB) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });
  }, [uploads, sortKey, sortDir]);

  const totalFiltered = sortedUploads.length;
  const totalPages = Math.max(1, Math.ceil(totalFiltered / pageSize));
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalFiltered);
  const pageRows = sortedUploads.slice(startIndex, endIndex);

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
    <div className="bg-[#1e1e1e] border border-white/5 rounded-xl overflow-hidden">
      <div className="flex items-center justify-end gap-3 px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-[#898989] text-xs">Exibir</span>
          <select
            value={pageSize}
            onChange={handlePageSizeChange}
            className="filter-input rounded-lg px-2 py-1.5 text-xs cursor-pointer"
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

      <div className="overflow-x-auto">
        <table className="w-full" aria-label="Histórico de uploads">
          <thead>
            <tr className="border-b border-white/5 bg-[#171616]/50">
              <SortableHeader label="Arquivo" colKey="original_filename" />
              <SortableHeader label="Status" colKey="status" />
              <SortableHeader label="Transações" colKey="total_transactions" />
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
              Array.from({ length: 5 }).map((_, i) => <SkeletonRow key={i} />)
            ) : pageRows.length === 0 ? (
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
                  <td
                    className="px-4 py-3 text-sm text-[#FFFFFF] font-medium max-w-[200px] truncate"
                    title={upload.original_filename}
                  >
                    {upload.original_filename}
                  </td>

                  <td className="px-4 py-3">
                    <StatusBadge status={upload.status} />
                  </td>

                  <td className="px-4 py-3 text-sm text-[#D8D8D8] tabular-nums">
                    {upload.total_transactions}
                  </td>

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

                  <td className="px-4 py-3 text-sm text-[#D8D8D8] tabular-nums whitespace-nowrap">
                    {formatDate(upload.created_at)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {!loading && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 py-3 border-t border-white/5">
          <p className="text-xs text-[#898989]">
            {totalFiltered === 0
              ? 'Nenhum registro encontrado'
              : `Exibindo ${startIndex + 1}–${endIndex} de ${totalFiltered} registro${totalFiltered !== 1 ? 's' : ''}`}
          </p>

          {totalPages > 1 && (
            <div className="flex items-center gap-1" role="navigation" aria-label="Paginação">
              <button
                onClick={() => setCurrentPage(1)}
                disabled={safePage === 1}
                className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Primeira página"
              >
                <FontAwesomeIcon icon={faAnglesLeft} className="text-xs" aria-hidden="true" />
              </button>

              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
                className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Página anterior"
              >
                <FontAwesomeIcon icon={faChevronLeft} className="text-xs" aria-hidden="true" />
              </button>

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

              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={safePage === totalPages}
                className="w-8 h-8 flex items-center justify-center text-[#898989] hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Próxima página"
              >
                <FontAwesomeIcon icon={faChevronRight} className="text-xs" aria-hidden="true" />
              </button>

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
  );
});

UploadDataTable.displayName = 'UploadDataTable';

export default UploadDataTable;
