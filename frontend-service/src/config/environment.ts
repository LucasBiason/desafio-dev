function getApiUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl;
  // Use relative URLs — Nginx handles proxying to backend services
  return '';
}

export const config = {
  apiUrl: getApiUrl(),
  environment: import.meta.env.MODE,
};
