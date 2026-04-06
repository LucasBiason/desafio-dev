import React, { useState, useMemo } from 'react';
import type { ReactNode } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import type { IconDefinition } from '@fortawesome/free-solid-svg-icons';
import {
  faBoxOpen,
  faChevronUp,
  faChevronDown,
  faChevronLeft,
  faChevronRight,
  faAnglesLeft,
  faAnglesRight,
} from '@fortawesome/free-solid-svg-icons';

export interface Column<T> {
  key: string;
  label: string;
  sortable?: boolean;
  render?: (value: unknown, row: T) => ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  emptyIcon?: IconDefinition;
  emptyMessage?: string;
  pageSizeOptions?: number[];
  defaultSortKey?: string;
  defaultSortDir?: 'asc' | 'desc';
  rowKey?: (row: T) => string;
}

type SortDir = 'asc' | 'desc';

const DEFAULT_PAGE_SIZE_OPTIONS = [5, 10, 20, 50];

interface SortIconProps {
  columnKey: string;
  sortKey: string;
  sortDir: SortDir;
}

const SortIcon: React.FC<SortIconProps> = ({ columnKey, sortKey, sortDir }) => {
  if (columnKey !== sortKey) {
    return (
      <FontAwesomeIcon
        icon={faChevronDown}
        className="ml-1 sort-icon-inactive text-[10px]"
        aria-hidden="true"
      />
    );
  }
  return (
    <FontAwesomeIcon
      icon={sortDir === 'asc' ? faChevronUp : faChevronDown}
      className="ml-1 sort-icon-active text-[10px]"
      aria-hidden="true"
    />
  );
};

function isNumeric(value: unknown): boolean {
  if (typeof value === 'number') return true;
  if (typeof value === 'string' && value.trim() !== '') {
    return !isNaN(Number(value));
  }
  return false;
}

function compareValues(a: unknown, b: unknown, dir: SortDir): number {
  if (isNumeric(a) && isNumeric(b)) {
    const numA = Number(a);
    const numB = Number(b);
    return dir === 'asc' ? numA - numB : numB - numA;
  }

  const strA = String(a ?? '').toLowerCase();
  const strB = String(b ?? '').toLowerCase();
  if (strA < strB) return dir === 'asc' ? -1 : 1;
  if (strA > strB) return dir === 'asc' ? 1 : -1;
  return 0;
}

function DataTable<T extends Record<string, unknown>>({
  data,
  columns,
  loading = false,
  emptyIcon,
  emptyMessage,
  pageSizeOptions = DEFAULT_PAGE_SIZE_OPTIONS,
  defaultSortKey,
  defaultSortDir = 'asc',
  rowKey,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string>(defaultSortKey ?? '');
  const [sortDir, setSortDir] = useState<SortDir>(defaultSortDir);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(pageSizeOptions[1] ?? pageSizeOptions[0] ?? 10);

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => compareValues(a[sortKey], b[sortKey], sortDir));
  }, [data, sortKey, sortDir]);

  const totalFiltered = sortedData.length;
  const totalPages = Math.max(1, Math.ceil(totalFiltered / pageSize));
  const safePage = Math.min(currentPage, totalPages);
  const startIndex = (safePage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalFiltered);
  const pageRows = sortedData.slice(startIndex, endIndex);

  const pageNumbers = useMemo(() => {
    const range: number[] = [];
    const delta = 2;
    const left = Math.max(1, safePage - delta);
    const right = Math.min(totalPages, safePage + delta);
    for (let i = left; i <= right; i++) range.push(i);
    return range;
  }, [safePage, totalPages]);

  const handleSortColumn = (key: string) => {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
    setCurrentPage(1);
  };

  const handlePageSizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setPageSize(Number(e.target.value));
    setCurrentPage(1);
  };

  const skeletonColumnCount = columns.length;

  const resolvedEmptyIcon = emptyIcon ?? faBoxOpen;

  return (
    <div className="bg-surface border border-white/5 rounded-xl overflow-hidden">
      <div className="flex items-center justify-end gap-3 px-4 py-3 border-b border-white/5">
        <div className="flex items-center gap-2 shrink-0">
          <span className="text-muted text-xs">Exibir</span>
          <select
            value={pageSize}
            onChange={handlePageSizeChange}
            className="filter-input rounded-lg px-2 py-1.5 text-xs cursor-pointer"
            aria-label="Itens por página"
          >
            {pageSizeOptions.map((size) => (
              <option key={size} value={size}>
                {size}
              </option>
            ))}
          </select>
          <span className="text-muted text-xs">por página</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-white/5 bg-page-dim">
              {columns.map((col) =>
                col.sortable ? (
                  <th
                    key={col.key}
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted cursor-pointer hover:text-white select-none transition-colors"
                    onClick={() => handleSortColumn(col.key)}
                    aria-sort={
                      sortKey === col.key
                        ? sortDir === 'asc'
                          ? 'ascending'
                          : 'descending'
                        : 'none'
                    }
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      <SortIcon
                        columnKey={col.key}
                        sortKey={sortKey}
                        sortDir={sortDir}
                      />
                    </span>
                  </th>
                ) : (
                  <th
                    key={col.key}
                    scope="col"
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-muted select-none"
                  >
                    {col.label}
                  </th>
                )
              )}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              Array.from({ length: 5 }).map((_, rowIndex) => (
                <tr key={rowIndex} className="border-b border-white/5 animate-pulse">
                  {Array.from({ length: skeletonColumnCount }).map((_, colIndex) => (
                    <td key={colIndex} className="px-4 py-3">
                      <div
                        className={`h-3 skeleton rounded ${
                          colIndex % 3 === 0
                            ? 'w-[60%]'
                            : colIndex % 3 === 1
                            ? 'w-[80%]'
                            : 'w-[50%]'
                        }`}
                      />
                    </td>
                  ))}
                </tr>
              ))
            ) : pageRows.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="px-4 py-16 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <FontAwesomeIcon
                      icon={resolvedEmptyIcon}
                      className="text-secondary text-4xl opacity-30"
                      aria-hidden="true"
                    />
                    <p className="text-secondary font-medium">Nenhum registro encontrado</p>
                    {emptyMessage && (
                      <p className="text-muted text-sm">{emptyMessage}</p>
                    )}
                  </div>
                </td>
              </tr>
            ) : (
              pageRows.map((row, rowIndex) => {
                const key = rowKey ? rowKey(row) : String(rowIndex);
                return (
                  <tr
                    key={key}
                    className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors"
                  >
                    {columns.map((col) => {
                      const value = row[col.key];
                      return (
                        <td
                          key={col.key}
                          className={`px-4 py-3 text-sm text-secondary${col.className ? ` ${col.className}` : ''}`}
                          title={
                            col.className?.includes('truncate') && typeof value === 'string'
                              ? value
                              : undefined
                          }
                        >
                          {col.render ? col.render(value, row) : String(value ?? '')}
                        </td>
                      );
                    })}
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {!loading && (
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 px-4 py-3 border-t border-white/5">
          <p className="text-xs text-muted">
            {totalFiltered === 0
              ? 'Nenhum registro encontrado'
              : `Exibindo ${startIndex + 1}–${endIndex} de ${totalFiltered} registro${totalFiltered !== 1 ? 's' : ''}`}
          </p>

          {totalPages > 1 && (
            <div className="flex items-center gap-1" role="navigation" aria-label="Paginação">
              <button
                onClick={() => setCurrentPage(1)}
                disabled={safePage === 1}
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Primeira página"
              >
                <FontAwesomeIcon icon={faAnglesLeft} className="text-xs" aria-hidden="true" />
              </button>

              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={safePage === 1}
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
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
                      ? 'page-btn-active'
                      : 'page-btn hover:bg-white/5',
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
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
                aria-label="Próxima página"
              >
                <FontAwesomeIcon icon={faChevronRight} className="text-xs" aria-hidden="true" />
              </button>

              <button
                onClick={() => setCurrentPage(totalPages)}
                disabled={safePage === totalPages}
                className="w-8 h-8 flex items-center justify-center text-muted hover:text-white hover:bg-white/5 rounded-lg transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
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
}

export default DataTable;
