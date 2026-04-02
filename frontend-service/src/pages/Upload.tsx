import { useState, useEffect, useCallback, useMemo } from 'react';
import type { FC } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRotate } from '@fortawesome/free-solid-svg-icons';
import Layout from '../components/Layout';
import DropZone from '../components/upload/DropZone';
import FilterPanel from '../components/upload/FilterPanel';
import UploadDataTable from '../components/upload/UploadDataTable';
import { uploadService } from '../services/uploadService';
import type { UploadResponse, UploadStatus } from '../types/upload';

// Auto-refresh interval in milliseconds
const POLL_INTERVAL_MS = 600_000; // 10 minutes

const Upload: FC = () => {
  const [uploads, setUploads] = useState<UploadResponse[]>([]);
  const [loading, setLoading] = useState(true);

  // Multi-select status chip filter
  const [selectedStatuses, setSelectedStatuses] = useState<UploadStatus[]>([]);

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

  const loadUploads = useCallback(
    async (statuses: UploadStatus[], filename: string, from: string, to: string) => {
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
    loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
  }, [selectedStatuses, filenameFilter, dateFrom, dateTo, loadUploads]);

  // Auto-refresh polling to catch status transitions
  useEffect(() => {
    const interval = setInterval(() => {
      loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
    }, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadUploads, selectedStatuses, filenameFilter, dateFrom, dateTo]);

  const handleChipToggle = (value: UploadStatus) => {
    setSelectedStatuses((prev) =>
      prev.includes(value) ? prev.filter((s) => s !== value) : [...prev, value],
    );
  };

  const handleClearStatuses = () => {
    setSelectedStatuses([]);
  };

  const handleUploadSuccess = useCallback(() => {
    loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo);
  }, [loadUploads, selectedStatuses, filenameFilter, dateFrom, dateTo]);

  const emptyStateMessage = useMemo(() => {
    if (selectedStatuses.length > 0 || filenameFilter || dateFrom || dateTo) {
      return 'Nenhum resultado para os filtros selecionados.';
    }
    return 'Importe um arquivo CNAB para começar.';
  }, [selectedStatuses, filenameFilter, dateFrom, dateTo]);

  return (
    <Layout>
      <div className="space-y-6">
        <div>
          <h2 className="text-[#FFFFFF] text-xl font-semibold">Upload de Arquivo CNAB</h2>
          <p className="text-[#D8D8D8] text-sm mt-1">
            Importe arquivos CNAB para processar transações.
          </p>
        </div>

        <DropZone onUploadSuccess={handleUploadSuccess} />

        <div className="flex items-center justify-between">
          <h3 className="text-[#FFFFFF] text-base font-semibold">Histórico de Uploads</h3>
          <button
            type="button"
            onClick={() => loadUploads(selectedStatuses, filenameFilter, dateFrom, dateTo)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-[#D8D8D8] bg-[#2a2a2a] border border-white/10 rounded-lg hover:text-white hover:border-white/30 transition-all"
          >
            <FontAwesomeIcon icon={faRotate} />
            Recarregar
          </button>
        </div>

        <FilterPanel
          selectedStatuses={selectedStatuses}
          onChipToggle={handleChipToggle}
          onClearStatuses={handleClearStatuses}
          filenameInput={filenameInput}
          onFilenameChange={setFilenameInput}
          dateFrom={dateFrom}
          onDateFromChange={setDateFrom}
          dateTo={dateTo}
          onDateToChange={setDateTo}
        />

        <UploadDataTable
          uploads={uploads}
          loading={loading}
          emptyStateMessage={emptyStateMessage}
        />
      </div>
    </Layout>
  );
};

export default Upload;
