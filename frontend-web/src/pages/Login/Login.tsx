import { useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import styles from './Login.module.css';
import illustration from './assets/login-illustration.svg';

export default function Login() {
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await login(email, password);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError('Email ou senha incorretos.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles['login-container']}>
      {/* Branding */}
      <div className={styles['login-branding']}>
        <img src={illustration} alt="Ilustração LogistiQ" />
        <div className={styles['login-branding-text']}>
          <h1>LogistiQ</h1>
          <p>Gerencie suas entregas e operações de forma inteligente.</p>
        </div>
      </div>

      {/* Formulário */}
      <div className={styles['login-form-wrapper']}>
        <form className={styles['login-form']} onSubmit={handleSubmit}>
          <h2>Bem-vindo de volta</h2>
          <p>Entre com sua conta para continuar</p>

          {error && <div className={styles['login-error']}>{error}</div>}

          <div className={styles['input-group']}>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
            />
          </div>

          <div className={styles['input-group']}>
            <label>Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="********"
              required
            />
          </div>

          <button className={styles['login-button']} type="submit" disabled={loading}>
            {loading ? 'Entrando...' : 'Entrar'}
          </button>

          <div className={styles['login-footer']}>
            © 2026 LogistiQ. Todos os direitos reservados.
          </div>
        </form>
      </div>
    </div>
  );
}
