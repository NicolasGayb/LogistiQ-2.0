import { useEffect } from 'react';
import { ShieldAlert, Lock } from 'lucide-react';
import './Maintenance.css';

export default function MaintenancePage() {
  
  // Ao carregar a tela, garantimos que o usuário "comum" seja deslogado
  // para evitar que ele fique com um token inválido preso no cache.
  useEffect(() => {
    // Limpa dados de sessão (exceto talvez alguma config de tema se tiver)
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    sessionStorage.clear();
  }, []);

  const handleAdminLogin = () => {
    // Redirecionamento forçado para limpar estados do React
    window.location.href = '/login';
  };

  return (
    <div className="maintenance-container">
      <div className="maintenance-card">
        
        {/* Ícone Animado */}
        <div className="icon-wrapper">
          <ShieldAlert size={48} className="icon-maintenance" />
        </div>

        {/* Textos */}
        <h1 className="maintenance-title">Sistema em Manutenção</h1>
        
        <p className="maintenance-text">
          Estamos realizando atualizações críticas no <strong>LogistiQ</strong> para melhorar sua experiência.
          <br /><br />
          O acesso está temporariamente restrito apenas a administradores do sistema para configuração de versão.
        </p>

        {/* Botão de Ação */}
        <button onClick={handleAdminLogin} className="btn-maintenance">
          <Lock size={18} />
          Sou Administrador do Sistema (Entrar)
        </button>

        {/* Rodapé */}
        <div className="maintenance-footer">
          LogistiQ v2.1.0 &bull; Status: <strong>Maintenance Mode</strong>
        </div>
      </div>
    </div>
  );
}