import { useState, useEffect, useRef, useCallback } from 'react';
import type { FC, DragEvent } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faCloudArrowUp,
  faFile,
  faCircleCheck,
  faCircleXmark,
  faSpinner,
  faHourglass,
  faBoxOpen,
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

// Auto-refresh interval in milliseconds
const POLL_INTERVAL_MS = 10_000;

// Number of recent uploads shown in the mini-table
const RECENT_PAGE_SIZE = 5;

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

// Skeleton row shown while loading the recent uploads table
const SkeletonRow: FC = () => (
  <tr className="border-b border-white/5 animate-pulse">
    {[70, 80, 50, 100].map((w, i) => (
      <td key={i} className="px-4 py-3">
        <div className="h-3 bg-[#2a2a2a] rounded" style={{ width: `${w}%` }} />
      </td>
    ))}
  </tr>
);

const Upload: FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [recentUploads, setRecentUploads] = useState<UploadResponse[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingRecent, setLoadingRecent] = useState(true);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Fetch the most recent uploads for the mini-table
  const loadRecentUploads = useCallback(async () => {
    try {
      const data = await uploadService.list(1, RECENT_PAGE_SIZE);
      setRecentUploads(data.results);
      setTotalCount(data.count);
    } catch {
      // Silent failure — recent uploads section is non-critical
    } finally {
      setLoadingRecent(false);
    }
  }, []);

  // Initial fetch
  useEffect(() => {
    loadRecentUploads();
  }, [loadRecentUploads]);

  // Auto-refresh polling to catch status changes (pending -> processing -> completed)
  useEffect(() => {
    const interval = setInterval(() => {
      loadRecentUploads();
    }, POLL_INTERVAL_MS);

    return () => clearInterval(interval);
  }, [loadRecentUploads]);

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
      await loadRecentUploads();
    } catch {
      setErrorMessage('Ocorreu um erro ao enviar o arquivo. Tente novamente.');
    } finally {
      setUploading(false);
    }
  };

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

        {/* Drop zone card — unchanged */}
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

        {/* Recent uploads mini-table */}
        <div>
          {/* Section header with count badge and link to full history */}
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-[#FFFFFF] text-base font-semibold">Uploads Recentes</h3>
              {!loadingRecent && totalCount > 0 && (
                <span className="bg-[#2a2a2a] text-[#D8D8D8] text-xs font-medium px-2 py-0.5 rounded-full">
                  {totalCount}
                </span>
              )}
            </div>
          </div>

          {/* DataTable-style container */}
          <div className="bg-[#1e1e1e] border border-white/5 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full" aria-label="Uploads recentes">
                <thead>
                  <tr className="border-b border-white/5 bg-[#171616]/50">
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] select-none"
                    >
                      Arquivo
                    </th>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] select-none"
                    >
                      Status
                    </th>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] select-none"
                    >
                      Transações
                    </th>
                    <th
                      scope="col"
                      className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-[#898989] select-none"
                    >
                      Data
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {loadingRecent ? (
                    // Skeleton rows while fetching
                    Array.from({ length: RECENT_PAGE_SIZE }).map((_, i) => (
                      <SkeletonRow key={i} />
                    ))
                  ) : recentUploads.length === 0 ? (
                    // Empty state
                    <tr>
                      <td colSpan={4} className="px-4 py-12 text-center">
                        <div className="flex flex-col items-center gap-3">
                          <FontAwesomeIcon
                            icon={faBoxOpen}
                            className="text-[#D8D8D8] text-3xl opacity-30"
                            aria-hidden="true"
                          />
                          <p className="text-[#D8D8D8] font-medium text-sm">
                            Nenhum upload encontrado
                          </p>
                          <p className="text-[#898989] text-xs">
                            Importe um arquivo CNAB para começar.
                          </p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    recentUploads.map((upload) => (
                      <tr
                        key={upload.id}
                        className="border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors"
                      >
                        {/* Filename */}
                        <td
                          className="px-4 py-3 text-sm text-[#FFFFFF] font-medium max-w-[180px] truncate"
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

            {/* Footer with link to full history */}
            {!loadingRecent && (
              <div className="px-4 py-3 border-t border-white/5 flex justify-end">
                <Link
                  to="/history"
                  className="text-[#4FFA7B] hover:text-[#02BE3B] text-sm font-medium transition-colors"
                >
                  Ver histórico completo →
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Upload;
