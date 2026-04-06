import { useState } from 'react';
import type { FC, FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileLines, faSpinner, faCircleExclamation, faTriangleExclamation } from '@fortawesome/free-solid-svg-icons';
import { useAuth } from '../hooks/useAuth';

const Login: FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const sessionExpired = searchParams.get('session_expired') === 'true';

  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
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
    <div
      className="min-h-screen flex items-center justify-center px-4 py-12"
      style={{
        background: 'linear-gradient(135deg, #171616 0%, #0d0d0d 50%, #171616 100%)',
      }}
    >
      <div className="w-full max-w-md">
        {/* Logo and title */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl mb-4"
            style={{
              background: 'rgba(30, 30, 30, 0.6)',
              backdropFilter: 'blur(12px)',
              WebkitBackdropFilter: 'blur(12px)',
              border: '1px solid rgba(58, 58, 58, 0.3)',
            }}
          >
            <FontAwesomeIcon icon={faFileLines} size="2x" className="text-[#4FFA7B]" aria-hidden="true" />
          </div>

          <h1
            className="text-3xl font-bold tracking-tight mb-2"
            style={{
              background: 'linear-gradient(135deg, #4FFA7B, #02BE3B)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text',
            }}
          >
            CNAB Parser
          </h1>

          <p className="text-sm" style={{ color: '#D8D8D8' }}>
            Importação e análise de transações CNAB
          </p>
        </div>

        {/* Session expired warning */}
        {sessionExpired && (
          <div
            className="mb-4 px-4 py-3 rounded-xl text-sm flex items-start gap-2"
            role="alert"
            aria-live="polite"
            style={{
              background: 'rgba(255, 184, 0, 0.1)',
              border: '1px solid rgba(255, 184, 0, 0.4)',
              color: '#FFB800',
            }}
          >
            <FontAwesomeIcon icon={faTriangleExclamation} size="sm" className="mt-0.5 shrink-0" aria-hidden="true" />
            <span>Sua sessão expirou. Faça login novamente.</span>
          </div>
        )}

        {/* Error alert */}
        {error && (
          <div
            className="mb-4 px-4 py-3 rounded-xl text-sm flex items-start gap-2"
            role="alert"
            aria-live="assertive"
            style={{
              background: 'rgba(255, 68, 68, 0.1)',
              border: '1px solid rgba(255, 68, 68, 0.4)',
              color: '#FF4444',
            }}
          >
            <FontAwesomeIcon icon={faCircleExclamation} size="sm" className="mt-0.5 shrink-0" aria-hidden="true" />
            <span>{error}</span>
          </div>
        )}

        {/* Login form card */}
        <div
          className="rounded-2xl p-6"
          style={{
            background: 'rgba(30, 30, 30, 0.6)',
            backdropFilter: 'blur(12px)',
            WebkitBackdropFilter: 'blur(12px)',
            border: '1px solid rgba(58, 58, 58, 0.3)',
          }}
        >
          <form onSubmit={handleSubmit} noValidate className="space-y-5">
            {/* Username field */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium mb-1.5"
                style={{ color: '#D8D8D8' }}
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
                className="w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors focus:outline-none"
                style={{
                  background: 'rgba(42, 42, 42, 0.5)',
                  border: '1px solid #3a3a3a',
                  color: '#FFFFFF',
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#4FFA7B';
                  e.currentTarget.style.boxShadow = '0 0 0 1px #4FFA7B';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#3a3a3a';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              />
            </div>

            {/* Password field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium mb-1.5"
                style={{ color: '#D8D8D8' }}
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
                className="w-full px-3.5 py-2.5 rounded-xl text-sm transition-colors focus:outline-none"
                style={{
                  background: 'rgba(42, 42, 42, 0.5)',
                  border: '1px solid #3a3a3a',
                  color: '#FFFFFF',
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = '#4FFA7B';
                  e.currentTarget.style.boxShadow = '0 0 0 1px #4FFA7B';
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = '#3a3a3a';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              />
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 px-4 rounded-xl text-sm font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"
              style={{
                backgroundColor: loading ? '#02BE3B80' : '#02BE3B',
                color: '#FFFFFF',
                cursor: loading ? 'not-allowed' : 'pointer',
              }}
              onMouseEnter={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#029E32';
              }}
              onMouseLeave={(e) => {
                if (!loading) e.currentTarget.style.backgroundColor = '#02BE3B';
              }}
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
        <p className="text-center mt-6 text-xs" style={{ color: '#3a3a3a' }}>
          v0.1.0
        </p>
      </div>
    </div>
  );
};

export default Login;
