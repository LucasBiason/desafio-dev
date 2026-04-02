import React, { useState, useRef, memo } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faCloudArrowUp,
  faFile,
  faSpinner,
  faCircleCheck,
  faCircleXmark,
} from '@fortawesome/free-solid-svg-icons';
import { uploadService } from '../../services/uploadService';

interface DropZoneProps {
  onUploadSuccess: () => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const DropZone: React.FC<DropZoneProps> = memo(({ onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File | null) => {
    setSelectedFile(file);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileChange(e.target.files?.[0] ?? null);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileChange(e.dataTransfer.files?.[0] ?? null);
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
      if (fileInputRef.current) fileInputRef.current.value = '';
      onUploadSuccess();
    } catch {
      setErrorMessage('Ocorreu um erro ao enviar o arquivo. Tente novamente.');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="bg-surface border border-input rounded-xl p-5">
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.cnab"
        className="hidden"
        aria-hidden="true"
        onChange={handleInputChange}
      />

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
          'flex flex-col items-center justify-center text-center p-10 rounded-lg cursor-pointer transition-colors',
          isDragOver
            ? 'dropzone-active'
            : 'dropzone-idle',
        ].join(' ')}
      >
        <FontAwesomeIcon
          icon={faCloudArrowUp}
          className={`text-5xl mb-4 ${isDragOver ? 'text-accent' : 'text-hover'}`}
        />
        <p className="text-secondary font-medium">
          Arraste um arquivo CNAB aqui ou clique para selecionar
        </p>
        <p className="text-secondary text-xs mt-1">Formatos aceitos: .txt, .cnab</p>
      </div>

      {selectedFile && !uploading && !successMessage && (
        <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 p-4 bg-page rounded-lg border border-input">
          <div className="flex items-center gap-3 min-w-0">
            <FontAwesomeIcon icon={faFile} className="text-accent shrink-0" />
            <div className="min-w-0">
              <p className="text-primary text-sm font-medium truncate">{selectedFile.name}</p>
              <p className="text-secondary text-xs">{formatBytes(selectedFile.size)}</p>
            </div>
          </div>
          <button
            onClick={handleUpload}
            className="shrink-0 btn-primary text-sm rounded-md"
            aria-label={`Enviar arquivo ${selectedFile.name}`}
          >
            Enviar
          </button>
        </div>
      )}

      {uploading && (
        <div className="mt-4 flex items-center gap-3 p-4 bg-page rounded-lg border border-input">
          <FontAwesomeIcon icon={faSpinner} className="text-accent animate-spin" />
          <p className="text-secondary text-sm">Enviando...</p>
        </div>
      )}

      {successMessage && (
        <div className="mt-4 flex items-center gap-3 p-4 rounded-lg alert-success">
          <FontAwesomeIcon icon={faCircleCheck} className="shrink-0" />
          <p className="text-sm">{successMessage}</p>
        </div>
      )}

      {errorMessage && (
        <div className="mt-4 flex items-center gap-3 p-4 rounded-lg alert-error">
          <FontAwesomeIcon icon={faCircleXmark} className="shrink-0" />
          <p className="text-sm">{errorMessage}</p>
        </div>
      )}
    </div>
  );
});

DropZone.displayName = 'DropZone';

export default DropZone;
