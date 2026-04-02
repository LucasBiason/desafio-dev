import type { FC } from 'react';
import { faBoxOpen } from '@fortawesome/free-solid-svg-icons';
import DataTable from '../../components/DataTable';
import type { Column } from '../../components/DataTable';
import StatusBadge from '../../components/StatusBadge';
import type { UploadResponse } from '../../types/upload';

function formatDate(iso: string): string {
  const d = new Date(iso);
  const pad = (n: number) => String(n).padStart(2, '0');
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

type UploadRow = UploadResponse & Record<string, unknown>;

const columns: Column<UploadRow>[] = [
  {
    key: 'original_filename',
    label: 'Arquivo',
    sortable: true,
    className: 'font-medium text-primary max-w-[200px] truncate',
  },
  {
    key: 'status',
    label: 'Status',
    sortable: true,
    render: (_, row) => <StatusBadge status={row.status} />,
  },
  {
    key: 'total_transactions',
    label: 'Transações',
    sortable: true,
    className: 'tabular-nums',
  },
  {
    key: 'error_message',
    label: 'Erro',
    render: (val) =>
      val ? (
        <span
          className="text-error truncate block max-w-[200px]"
          title={String(val)}
        >
          {String(val)}
        </span>
      ) : (
        <span className="text-muted">—</span>
      ),
  },
  {
    key: 'created_at',
    label: 'Data de Upload',
    sortable: true,
    render: (val) => formatDate(String(val)),
    className: 'tabular-nums whitespace-nowrap',
  },
];

interface UploadDataTableProps {
  uploads: UploadResponse[];
  loading: boolean;
  emptyStateMessage: string;
}

const UploadDataTable: FC<UploadDataTableProps> = ({ uploads, loading, emptyStateMessage }) => (
  <DataTable<UploadRow>
    data={uploads as UploadRow[]}
    columns={columns}
    loading={loading}
    emptyIcon={faBoxOpen}
    emptyMessage={emptyStateMessage}
    defaultSortKey="created_at"
    defaultSortDir="desc"
    rowKey={(row) => row.id}
  />
);

UploadDataTable.displayName = 'UploadDataTable';

export default UploadDataTable;
