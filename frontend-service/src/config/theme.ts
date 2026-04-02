export const colors = {
  bg: {
    primary: '#171616',
    surface: '#1e1e1e',
    input: '#2a2a2a',
    hover: '#3a3a3a',
  },
  text: {
    primary: '#FFFFFF',
    secondary: '#D8D8D8',
    muted: '#898989',
  },
  accent: {
    primary: '#4FFA7B',
    button: '#02BE3B',
    buttonHover: '#029E32',
  },
  status: {
    pending: { bg: 'rgba(255,184,0,0.15)', text: '#FFB800', label: 'Pendente' },
    processing: { bg: 'rgba(79,250,123,0.15)', text: '#4FFA7B', label: 'Processando' },
    completed: { bg: 'rgba(2,190,59,0.15)', text: '#02BE3B', label: 'Concluído' },
    failed: { bg: 'rgba(255,68,68,0.15)', text: '#FF4444', label: 'Falhou' },
  },
  error: '#FF4444',
  warning: '#FFB800',
  success: '#02BE3B',
} as const;

export type UploadStatus = keyof typeof colors.status;
