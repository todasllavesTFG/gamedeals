import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { LogIn } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = location.state?.from?.pathname || '/';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex items-center justify-center min-h-[70vh] px-4">
      <div className="w-full max-w-md bg-surface border border-border rounded-2xl p-8 space-y-6">
        <div className="text-center space-y-1">
          <h1 className="font-display text-2xl font-bold text-text">Iniciar sesión</h1>
          <p className="text-text-muted text-sm">Accede a tu cuenta de GameDeals</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="tu@email.com"
              className="w-full px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-text placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
            />
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-text-muted">Contraseña</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              className="w-full px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-text placeholder:text-text-muted focus:outline-none focus:border-accent transition-colors"
            />
          </div>

          {error && (
            <p className="text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-accent text-bg font-semibold text-sm transition-all hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <LogIn className="w-4 h-4" />
            {loading ? 'Entrando…' : 'Entrar'}
          </button>
        </form>

        <p className="text-center text-sm text-text-muted">
          ¿No tienes cuenta?{' '}
          <Link to="/register" className="text-accent hover:underline font-medium">
            Regístrate
          </Link>
        </p>
      </div>
    </div>
  );
}
