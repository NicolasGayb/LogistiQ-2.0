import { useState } from "react";
import { AxiosError } from "axios"; // Importando tipo para tratamento de erro
import api from "../../api/client.ts"; // Importa nossa configuração centralizada
import styles from "./Register.module.css";

export default function Register() {
  // Estados de controle de fluxo da tela
  const [step, setStep] = useState<"choose" | "exists" | "notfound">("choose");
  
  // Estados do formulário
  const [companyCnpj, setCompanyCnpj] = useState("");
  const [companyExists, setCompanyExists] = useState<boolean | null>(null);
  const [companyName, setCompanyName] = useState("");
  
  // Estados do cadastro de usuário
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [token, setToken] = useState("");
  
  // Feedback para o usuário
  const [error, setError] = useState("");

  /**
   * Verifica se a empresa existe pelo CNPJ.
   * Usa o método GET da nossa API configurada.
   */
  const checkCompany = async () => {
    // 1. Validação básica
    if (!companyCnpj) {
      setError("Por favor, insira o CNPJ da empresa.");
      return;
    }

    try {
      setError(""); // Limpa erros anteriores
      
      // 2. Chamada à API
      // O Axios retorna os dados dentro da propriedade .data
      const response = await api.get(`/companies/cnpj/${companyCnpj}`);

      // 3. Sucesso: Empresa encontrada
      setCompanyExists(true);
      setCompanyName(response.data.name);
      setStep("exists");

    } catch (err) {
      // 4. Erro: Empresa não encontrada ou erro de servidor
      setCompanyExists(false);
      setStep("notfound");
      console.error("Erro ao buscar empresa:", err);
    }
  };

  /**
   * Envia os dados para criar o usuário vinculado à empresa.
   * Usa o método POST da API.
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // 1. Validação de Senha
    if (password !== confirmPassword) {
      setError("As senhas não coincidem");
      return;
    }

    setError(""); // Limpa erros

    try {
      // 2. Envio dos dados
      // O endpoint /users/auto-create espera exatamente estes campos
      await api.post("/users/auto-create", {
        name,
        email,
        password,
        confirm_password: confirmPassword,
        token
      });

      // 3. Sucesso
      alert("Cadastro realizado com sucesso! Você será redirecionado para o login.");
      window.location.href = "/login"; // Redireciona para a tela de login

    } catch (err) {
      // 4. Tratamento de Erro
      // Tenta pegar a mensagem específica que o Backend enviou (ex: "Token inválido")
      const error = err as AxiosError<{ detail: string }>;
      const msg = error.response?.data?.detail || "Ocorreu um erro ao criar o usuário.";
      
      setError(msg);
    }
  };

  return (
    <div className={styles.registerContainer}>
      {/* --- PASSO 1: ESCOLHA --- */}
      {step === "choose" && (
        <div className={styles.chooseStep}>
          <h2>Bem-vindo!</h2>
          <p>Você já tem empresa cadastrada?</p>
          <div className={styles.buttons}>
            <button onClick={() => setStep("exists")}>Sim</button>
            <button onClick={() => setStep("notfound")}>Não</button>
          </div>
        </div>
      )}

      {/* --- PASSO 2: FORMULÁRIO DE CADASTRO --- */}
      {step === "exists" && (
        <form className={styles.registerForm} onSubmit={handleSubmit}>
          <h2>Cadastro de Usuário</h2>
          <p>Informe os dados abaixo</p>
          
          {/* Exibição de Erros Globais */}
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.inputGroup}>
            <label>CNPJ da Empresa</label>
            <div style={{ display: 'flex', gap: '10px' }}>
                <input
                value={companyCnpj}
                onChange={(e) => setCompanyCnpj(e.target.value)}
                placeholder="00.000.000/0000-00"
                required
                />
                <button type="button" onClick={checkCompany} style={{width: 'auto', padding: '0 15px'}}>
                    Verificar
                </button>
            </div>
            
            {/* Feedback visual da busca de empresa */}
            {companyExists === false && <span className={styles.error} style={{fontSize: '0.9rem'}}>Empresa não encontrada</span>}
            {companyExists === true && <span className={styles.success} style={{fontSize: '0.9rem'}}>Empresa encontrada!</span>}
            {companyName && <p style={{marginTop: '5px', fontSize: '0.9rem', color: '#666'}}>Empresa: <b>{companyName}</b></p>}
          </div>

          <div className={styles.inputGroup}>
            <label>Nome</label>
            <input value={name} onChange={(e) => setName(e.target.value)} required />
          </div>

          <div className={styles.inputGroup}>
            <label>Email</label>
            <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>

          <div className={styles.inputGroup}>
            <label>Senha</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>

          <div className={styles.inputGroup}>
            <label>Confirmar Senha</label>
            <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required />
          </div>

          <div className={styles.inputGroup}>
            <label>Token da Empresa</label>
            <input 
                value={token} 
                onChange={(e) => setToken(e.target.value)} 
                placeholder="Token fornecido pelo admin da empresa"
                required 
            />
          </div>

          <button className={styles.submitButton} type="submit">Cadastrar</button>
        </form>
      )}

      {/* --- PASSO 3: EMPRESA NÃO ENCONTRADA --- */}
      {step === "notfound" && (
        <div className={styles.notFound}>
          <h2>Empresa não encontrada</h2>
          <p>Entre em contato pelo email <b>suporte@logistiq.com</b> para solicitar acesso.</p>
          <button onClick={() => setStep("choose")} className={styles.secondaryButton}>Voltar</button>
        </div>
      )}
    </div>
  );
}