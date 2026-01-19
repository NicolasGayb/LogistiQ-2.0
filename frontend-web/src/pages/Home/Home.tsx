import styles from './Home.module.css';
import { Link } from 'react-router-dom';

export default function Home() {
  return (
    <div className={styles.home}>
      {/* Header */}
      <header className={styles.header}>
        <div className={styles.logo}>LogistiQ</div>
        <Link to="/login" className={styles.headerButton}>
          Acessar plataforma
        </Link>
      </header>

      {/* Hero */}
      <section className={styles.hero}>
        <h1>
          Gestão logística <br />
          simples, inteligente <br />
          e centralizada
        </h1>
        <p>
          O LogistiQ ajuda empresas a organizarem entregas, usuários e
          operações em um único lugar, com controle total e visibilidade.
        </p>

        <Link to="/login" className={styles.heroButton}>
          Começar agora
        </Link>
      </section>

      {/* Features */}
      <section className={styles.features}>
        <div className={styles.featureCard}>
          <h3>Controle total</h3>
          <p>Gerencie entregas, usuários e permissões com segurança.</p>
        </div>

        <div className={styles.featureCard}>
          <h3>Multi-perfis</h3>
          <p>Sistema adaptado para admins, gestores e operadores.</p>
        </div>

        <div className={styles.featureCard}>
          <h3>Dados em tempo real</h3>
          <p>Dashboards claros para decisões rápidas e eficientes.</p>
        </div>
      </section>

      {/* CTA final */}
      <section className={styles.cta}>
        <h2>Pronto para organizar sua operação?</h2>
        <Link to="/login" className={styles.ctaButton}>
          Entrar no LogistiQ
        </Link>
      </section>

      {/* Footer */}
      <footer className={styles.footer}>
        © 2026 LogistiQ. Todos os direitos reservados.
      </footer>
    </div>
  );
}
