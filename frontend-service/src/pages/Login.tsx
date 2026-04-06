import React, { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileLines, faSpinner, faCircleExclamation, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../hooks/useAuth';

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const sessionExpired = searchParams.get('session_expired') === 'true';

  const handleSubmit = async (e: React.SyntheticEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login({ username, password });
      navigate('/dashboard');
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string; message?: string } } };
      const message =
        axiosError.response?.data?.detail ??
        axiosError.response?.data?.message ??
        'Credenciais inválidas. Verifique seu usuário e senha.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-page">
      <div className="w-full max-w-md">
        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4 glass-circle">
            <FontAwesomeIcon icon={faFileLines} size="2x" className="text-accent" aria-hidden="true" />
          </div>

          <h1 className="text-3xl font-bold tracking-tight mb-2 gradient-text">
            CNAB Parser
          </h1>

          <p className="text-sm text-secondary">
            Importação e análise de transações CNAB
          </p>
        </div>

        {/* Session expired warning */}
        {sessionExpired && (
          <div
            className="mb-4 px-4 py-3 rounded-xl text-sm flex items-start gap-2 alert-warning"
            role="alert"
            aria-live="polite"
          >
            <FontAwesomeIcon icon={faTriangleExclamation} size="sm" className="mt-0.5 shrink-0" aria-hidden="true" />
            <span>Sua sessão expirou. Faça login novamente.</span>
          </div>
        )}

        {/* Error alert */}
        {error && (
          <div
            className="mb-4 px-4 py-3 rounded-xl text-sm flex items-start gap-2 alert-error"
            role="alert"
            aria-live="assertive"
          >
            <FontAwesomeIcon icon={faCircleExclamation} size="sm" className="mt-0.5 shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {/* Login form card */}
        <div className="glass-card rounded-2xl p-6">
          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Username field */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium mb-1.5 text-secondary"
              >
                Usuário
              </label>
              <input
                id="username"
                type="text"
                autoComplete="username"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Digite seu usuário"
                disabled={loading}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm form-input"
              />
            </div>

            {/* Password field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium mb-1.5 text-secondary"
              >
                Senha
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Digite sua senha"
                disabled={loading}
                className="w-full px-3.5 py-2.5 rounded-xl text-sm form-input"
              />
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl text-sm font-semibold btn-submit focus:outline-none focus:ring-2 focus:ring-offset-2"
            >
              {loading ? (
                <>
                  <FontAwesomeIcon icon={faSpinner} spin size="sm" className="mr-2 inline-block" aria-hidden="true" />
                  Entrando...
                </>
              ) : (
                'Entrar'
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center mt-6 text-xs text-dim">
          v0.1.0
        </p>
      </div>
    </div>
  );
};

export default Login;
