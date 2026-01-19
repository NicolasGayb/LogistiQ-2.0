import { useState, FormEvent } from "react";
import styles from "./Register.module.css";

export default function Register() {
  const [step, setStep] = useState<"choose" | "exists" | "notfound">("choose");
  const [companyCnpj, setCompanyCnpj] = useState("");
  const [companyExists, setCompanyExists] = useState<boolean | null>(null);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [companyName, setCompanyName] = useState("");

  const checkCompany = async () => {
    if (!companyCnpj) {
      setError("Por favor, insira o CNPJ da empresa.");
      return;
    }

    try {
      const res = await fetch(`http://localhost:8000/companies/cnpj/${companyCnpj}`);
      if (res.ok) {
        setCompanyExists(true);
        const data = await res.json();
        setCompanyName(data.name);
        setStep("exists");
      } else {
        setCompanyExists(false);
        setStep("notfound");
      }
    } catch {
      setCompanyExists(false);
      setStep("notfound");
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError("As senhas não coincidem");
      return;
    }
    setError("");
    try {
      const res = await fetch("http://localhost:8000/users/auto-create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name,
          email,
          password,
          confirm_password: confirmPassword,
          token
        }),
      });
      if (!res.ok) throw new Error("Erro ao criar usuário");
      alert("Cadastro realizado com sucesso!");
    } catch (err: any) {
      setError(err.message || "Erro desconhecido");
    }
  };

  return (
    <div className={styles.registerContainer}>
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

      {step === "exists" && (
        <form className={styles.registerForm} onSubmit={handleSubmit}>
          <h2>Cadastro de Usuário</h2>
          <p>Informe os dados abaixo</p>
          {error && <div className={styles.error}>{error}</div>}

          <div className={styles.inputGroup}>
            <label>CNPJ da Empresa</label>
            <input
              value={companyCnpj}
              onChange={(e) => setCompanyCnpj(e.target.value)}
              placeholder="00.000.000/0000-00"
              required
            />
            {companyExists === false && <span className={styles.error}>Empresa não encontrada</span>}
            {companyExists === true && <span className={styles.success}>Empresa encontrada!</span>}
            <button type="button" onClick={checkCompany}>Verificar</button>
            <p>Empresa: {companyName}</p>

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
            <input value={token} onChange={(e) => setToken(e.target.value)} required />
          </div>

          <button className={styles.submitButton} type="submit">Cadastrar</button>
        </form>
      )}

      {step === "notfound" && (
        <div className={styles.notFound}>
          <h2>Empresa não encontrada</h2>
          <p>Entre em contato pelo email <b>email@example.com</b> para solicitar acesso.</p>
        </div>
      )}
    </div>
  );
}