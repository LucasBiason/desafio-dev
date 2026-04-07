function getApiUrl(): string {
  const envUrl = import.meta.env.VITE_API_URL;
  if (envUrl) return envUrl;
  // Use BASE_URL so API calls work under subdirectory deployments (e.g. /cnab/)
  const base = import.meta.env.BASE_URL || '/';
  return base.endsWith('/') ? base.slice(0, -1) : base;
}

export const config = {
  apiUrl: getApiUrl(),
  environment: import.meta.env.MODE,
};
