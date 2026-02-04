import { useState, useEffect, useRef } from 'react';
import { User, Lock, Bell, Building, Save, LogOut, CheckCircle, AlertTriangle } from 'lucide-react';
import api from '../../api/client';
import { Card } from '../../components/Card/Card';
import { Button } from '../../components/Button/Button';

// Importa o arquivo CSS específico para a página de configurações
import './SettingsPage.css';

// Tipagem dos dados do usuário
interface UserSettings {
  id: string;
  name: string;
  email: string;
  role: string;
  notification_stock_alert?: boolean;
  notification_weekly_summary?: boolean;
  theme_preference?: string;
  avatar_url?: string;
  company?: {
    name: string;
    cnpj: string;
    stock_alert_limit?: number;
  };
}

// Página de Configurações
export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [userData, setUserData] = useState<UserSettings | null>(null);

  // Estados dos Formulários
  const [profileForm, setProfileForm] = useState({ name: '', email: '' });
  const [prefsForm, setPrefsForm] = useState({ stockAlert: true, weeklySummary: true, theme: 'auto' });
  const [passForm, setPassForm] = useState({ current: '', new: '', confirm: '' });
  const [companyForm, setCompanyForm] = useState({ name: '', cnpj: '', alertLimit: 10 });

  // Estado das fotos de perfil
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Estado para controlar a atualização das imagens de avatar
  const [avatarHash, setAvatarHash] = useState(Date.now());

  // --- Efeitos ---

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const response = await api.get('/users/me'); 
      const u = response.data;
      setUserData(u);
      
      setProfileForm({ name: u.name, email: u.email });
      setPrefsForm({
        stockAlert: u.notification_stock_alert ?? true,
        weeklySummary: u.notification_weekly_summary ?? true,
        theme: u.theme_preference ?? 'auto'
      });
      
      if (u.company) {
        setCompanyForm({
          name: u.company.name,
          cnpj: u.company.cnpj,
          alertLimit: u.company.stock_alert_limit ?? 10
        });
      }
    } catch (error) {
      console.error("Erro ao carregar perfil:", error);
    }
  };

  // --- Handlers ---
// Manipula mudança de arquivo de avatar
const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAvatarFile(file);
      // Salva uma pré-visualização da imagem selecionada para mostrar ao usuário antes do upload
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl(objectUrl);
    }
  };

// Salva perfil e preferências juntos
const handleSaveProfile = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('name', profileForm.name);
      formData.append('email', profileForm.email);

      formData.append('notification_stock_alert', String(prefsForm.stockAlert));
      formData.append('notification_weekly_summary', String(prefsForm.weeklySummary));
      formData.append('theme_preference', prefsForm.theme);
      
      // Se houver arquivo novo, adiciona
      if (avatarFile) {
        formData.append('avatar', avatarFile);
      }

      // Importante: Ao enviar FormData, o axios/fetch ajusta o Content-Type automaticamente
      await api.put('/users/me/profile', formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      alert('Perfil atualizado com sucesso!');

      setAvatarHash(Date.now()); // Atualiza o hash para forçar reload da imagem
      setAvatarFile(null);
      setPreviewUrl(null);
      fetchUserData(); 
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao atualizar perfil.');
    } finally {
      setLoading(false);
    }
  };

  const handleSavePassword = async () => {
    if (passForm.new !== passForm.confirm) {
      return alert('A nova senha e a confirmação não conferem.');
    }
    setLoading(true);
    try {
      await api.put('/users/me/change-password', {
        current_password: passForm.current,
        new_password: passForm.new,
        confirm_password: passForm.confirm
      });
      alert('Senha alterada! Por favor, faça login novamente.');
      setPassForm({ current: '', new: '', confirm: '' });
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao alterar senha. Verifique sua senha atual.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCompany = async () => {
    setLoading(true);
    try {
      await api.put('/users/me/company', {
        name: companyForm.name,
        stock_alert_limit: Number(companyForm.alertLimit)
      });
      alert('Dados da empresa atualizados!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Erro ao atualizar empresa.');
    } finally {
      setLoading(false);
    }
  };
  const tabs = [
    { id: 'profile', label: 'Meu Perfil', icon: User },
    { id: 'security', label: 'Segurança', icon: Lock },
    { id: 'preferences', label: 'Preferências', icon: Bell },
    { id: 'company', label: 'Dados da Empresa', icon: Building, adminOnly: true },
  ];

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1 className="settings-title">Configurações</h1>
        <p className="settings-subtitle">Gerencie suas preferências e dados da conta.</p>
      </div>

      <div className="settings-grid">
        
        {/* --- Sidebar --- */}
        <div className="settings-sidebar">
          <nav className="settings-nav">
            {tabs.map(tab => {
              if (tab.adminOnly && userData?.role === 'OPERATOR') return null;
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`nav-button ${activeTab === tab.id ? 'active' : ''}`}
                >
                  <Icon size={18} />
                  {tab.label}
                </button>
              );
            })}
          </nav>
          
          <div className="settings-sidebar-card">
            <div className="settings-sidebar-avatar">
              {userData?.id ? (
                <img 
                  src={`${api.defaults.baseURL}/users/${userData.id}/avatar?t=${avatarHash}`} 
                  alt="Avatar"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    if (e.currentTarget.parentElement) {
                      e.currentTarget.parentElement.innerText = userData.name?.charAt(0) || 'User';
                    }
                  }}
                />
              ) : (
                userData?.name?.charAt(0) || 'User'
              )}
            </div>
            
            <div className="settings-sidebar-info">
              <p className="font-bold">{userData?.name}</p>
              <span>{userData?.company?.name}</span>
            </div>
          </div>
        </div>

        {/* --- Conteúdo --- */}
        <div className="settings-content">
          
          {/* ABA: PERFIL */}
          {activeTab === 'profile' && (
            <Card title="Informações Pessoais">
              <div className="form-section">
                <input 
                  type='file'
                  ref={fileInputRef}
                  className='hidden'
                  style={{ display: 'none' }}
                  accept='image/png, image/jpeg' 
                  onChange={handleFileChange} 
                />

                <div className="info-box">
                    <div className="settings-sidebar-avatar" style={{
                      background: previewUrl ? 'transparent' : '#cbd5e1',
                      color: '#64748b',
                      overflow: 'hidden'
                    }}>
                      {previewUrl ? (
                            <img src={previewUrl} alt="Preview" className="w-full h-full object-cover" />
                        ) : userData?.avatar_url ? ( 
                            <img 
                            src={`${api.defaults.baseURL}/users/${userData.id}/avatar?t=${avatarHash}`} 
                            alt="Profile" 
                            className="w-full h-full object-cover"
                            onError={(e) => {
                              // Se a imagem falhar ao carregar, esconde a tag img para mostrar a inicial do nome
                              e.currentTarget.style.display = 'none';
                              e.currentTarget.parentElement?.classList.remove('bg-transparent');
                              e.currentTarget.parentElement?.classList.add('bg-slate-300');
                            }} />
                        ) : (
                            userData?.name?.charAt(0)
                        )}
                    </div>
                    <div>
                        <strong>Foto de Perfil</strong>
                        <p style={{fontSize: '0.8rem', opacity: 0.8}}>Aceitamos arquivos JPG ou PNG.</p>
                    </div>
                    <button onClick={() => fileInputRef.current?.click()} className="btn-upload">
                      Alterar Foto
                    </button>
                </div>

                <div className="form-group">
                  <label>Nome Completo</label>
                  <input 
                    className="form-input"
                    value={profileForm.name}
                    onChange={e => setProfileForm({...profileForm, name: e.target.value})}
                  />
                </div>
                <div className="form-group">
                  <label>E-mail</label>
                  <input 
                    type="email"
                    className="form-input"
                    value={profileForm.email}
                    onChange={e => setProfileForm({...profileForm, email: e.target.value})}
                  />
                </div>

                <div className="form-actions">
                  <Button onClick={handleSaveProfile} disabled={loading}>
                    <Save size={18} style={{marginRight: 8}} /> Salvar
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* ABA: SEGURANÇA */}
          {activeTab === 'security' && (
            <Card title="Segurança da Conta">
              <div className="form-section">
                <div className="form-group">
                    <label>Senha Atual</label>
                    <input type="password" className="form-input"
                      value={passForm.current}
                      onChange={e => setPassForm({...passForm, current: e.target.value})}
                    />
                </div>
                <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem'}}>
                    <div className="form-group">
                        <label>Nova Senha</label>
                        <input type="password" className="form-input"
                          value={passForm.new}
                          onChange={e => setPassForm({...passForm, new: e.target.value})}
                        />
                    </div>
                    <div className="form-group">
                        <label>Confirmar Senha</label>
                        <input type="password" className="form-input"
                          value={passForm.confirm}
                          onChange={e => setPassForm({...passForm, confirm: e.target.value})}
                        />
                    </div>
                </div>

                <div className="form-actions between">
                  <button onClick={() => alert('Funcionalidade disponível em breve!')} className="text-danger">
                    <LogOut size={16} style={{marginRight: 5}}/> Desconectar outros dispositivos
                  </button>
                  <Button onClick={handleSavePassword} disabled={loading}>Atualizar Senha</Button>
                </div>
              </div>
            </Card>
          )}

          {/* ABA: PREFERÊNCIAS (Com Switch CSS Puro) */}
          {activeTab === 'preferences' && (
            <Card title="Preferências do Sistema">
              <div className="form-section">
                
                <div className="toggle-item">
                  <div className="toggle-info">
                    <AlertTriangle size={20} color="#94a3b8" />
                    <div className="toggle-text">
                      <h4>Alertas de Estoque Baixo</h4>
                      <p>Receber e-mail quando atingir o limite mínimo.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" 
                      checked={prefsForm.stockAlert}
                      onChange={e => setPrefsForm({...prefsForm, stockAlert: e.target.checked})}
                    />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="toggle-item">
                  <div className="toggle-info">
                    <CheckCircle size={20} color="#94a3b8" />
                    <div className="toggle-text">
                        <h4>Resumo Semanal</h4>
                        <p>Relatório de movimentações toda segunda-feira.</p>
                    </div>
                  </div>
                  <label className="switch">
                    <input type="checkbox" 
                      checked={prefsForm.weeklySummary}
                      onChange={e => setPrefsForm({...prefsForm, weeklySummary: e.target.checked})}
                    />
                    <span className="slider"></span>
                  </label>
                </div>

                <div className="form-group" style={{marginTop: '1rem', borderTop: '1px solid #eee', paddingTop: '1rem'}}>
                  <label>Tema da Interface</label>
                  <select className="form-input" style={{maxWidth: '200px'}}
                    value={prefsForm.theme}
                    onChange={e => setPrefsForm({...prefsForm, theme: e.target.value})}
                  >
                    <option value="light">Claro</option>
                    <option value="dark">Escuro</option>
                    <option value="auto">Automático</option>
                  </select>
                </div>

                <div className="form-actions">
                   <Button onClick={handleSaveProfile} disabled={loading}>Salvar Preferências</Button>
                </div>
              </div>
            </Card>
          )}

          {/* ABA: EMPRESA */}
          {activeTab === 'company' && (
            <Card title="Dados da Organização">
              <div className="form-section">
                <div className="info-box">
                    <Building size={20} />
                    <div>
                      <strong>Sobre dados fiscais</strong>
                      <p style={{fontSize: '0.85rem'}}>O CNPJ e Razão Social não podem ser alterados aqui.</p>
                    </div>
                </div>

                <div className="form-group">
                    <label>Nome Fantasia</label>
                    <input className="form-input"
                      value={companyForm.name}
                      onChange={e => setCompanyForm({...companyForm, name: e.target.value})}
                    />
                </div>
                <div className="form-group">
                    <label>CNPJ</label>
                    <input className="form-input" disabled value={companyForm.cnpj} />
                </div>
                
                <div className="form-group">
                    <label>Limite de Alerta (Unidades)</label>
                    <div style={{display: 'flex', alignItems: 'center', gap: '0.5rem'}}>
                        <input type="number" className="form-input" style={{width: '120px'}}
                            value={companyForm.alertLimit}
                            onChange={e => setCompanyForm({...companyForm, alertLimit: Number(e.target.value)})}
                        />
                        <span style={{color: '#64748b', fontSize: '0.9rem'}}>unidades</span>
                    </div>
                </div>

                <div className="form-actions">
                  <Button onClick={handleSaveCompany} disabled={loading}>Atualizar Empresa</Button>
                </div>
              </div>
            </Card>
          )}

        </div>
      </div>
    </div>
  );
}