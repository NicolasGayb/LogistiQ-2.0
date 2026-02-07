import { useNavigate } from 'react-router-dom';

export default function Forbidden() {
  const navigate = useNavigate();

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <h1>403</h1>
      <h2>Acesso negado</h2>

      <p>
        Você não tem permissão para acessar esta página.
      </p>

      <button onClick={() => navigate(-1)}>
        Voltar
      </button>
    </div>
  );
}