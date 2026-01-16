# LogistiQ API

Versão do README:v1.0.0

API do sistema **LogistiQ**, uma plataforma de gestão logística com controle de usuários por empresa e autenticação via JWT.

Este repositório contém **todo o ecossistema do LogistiQ**, incluindo:

* **Backend** da aplicação, desenvolvido em **FastAPI**
* **Frontend Web**, desenvolvido em **React**
* **Frontend Mobile**, desenvolvido em **React Native**

O projeto foi estruturado para facilitar a integração entre as camadas, mantendo padrões de autenticação, navegação por roles e isolamento de dados por empresa.

---

## 🚀 Tecnologias utilizadas

* Python 3.11+
* FastAPI
* SQLAlchemy
* PostgreSQL
* JWT (OAuth2 Password Flow)
* Pytest

---

## 🔐 Autenticação

A autenticação é feita via **JWT** utilizando o fluxo OAuth2 com senha.

### Login

```http
POST /auth/login
```

* Retorna um `access_token` no formato **Bearer**
* O token deve ser enviado no header das requisições protegidas:

```http
Authorization: Bearer <token>
```

### Usuário autenticado

```http
GET /auth/me
```

* Retorna os dados do usuário logado
* Inclui informações de role e empresa (quando aplicável)

---

## 🧑‍💼 Controle de acesso (Roles)

O sistema possui controle de acesso baseado em papéis (**roles**), garantindo que cada usuário visualize e manipule apenas os dados permitidos.

Exemplos de roles:

* `SYSTEM_ADMIN`
* `ADMIN`
* `USER`

As permissões são validadas tanto no token quanto nos endpoints protegidos.

---

## 🏢 Isolamento por empresa

Os dados da aplicação são isolados por empresa. Usuários vinculados a uma empresa só podem acessar informações relacionadas a ela.

Esse isolamento é garantido no backend, evitando vazamento de dados entre organizações.

---

## 📂 Estrutura do repositório

O projeto utiliza um **monorepo**, concentrando backend e frontends no mesmo repositório, mantendo padrões compartilhados e facilitando a evolução integrada.

```
logistiq/
├── backend/            # API FastAPI (auth, regras de negócio, banco de dados)
├── frontend-web/       # Aplicação Web em React
├── frontend-mobile/    # Aplicação Mobile em React Native
├── README.md
```

Cada camada é independente, mas todas compartilham o mesmo modelo de autenticação, roles e isolamento por empresa.

---

## 🔄 Fluxo geral da aplicação

1. O usuário realiza login pelo **frontend web ou mobile**
2. A API retorna um **token JWT**
3. O frontend utiliza o endpoint `GET /users/me` para obter:

   * dados do usuário
   * role
   * empresa vinculada
4. A navegação e permissões da interface são definidas com base no **role do usuário**
5. Todas as requisições protegidas utilizam o token JWT no header

Esse fluxo garante consistência entre as plataformas e centraliza as regras de acesso no backend.

---

## ▶️ Como rodar o projeto

1. Clone o repositório
2. Crie um ambiente virtual
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente
5. Execute a aplicação:

```bash
uvicorn app.main:app --reload
```

A documentação interativa estará disponível em:

```
http://localhost:8000/docs
```

---

## 🧪 Testes

Os testes automatizados garantem o correto funcionamento das regras de negócio e autenticação.

Para executar:

```bash
pytest
```

---

## 🧠 Decisões técnicas

* **FastAPI** foi escolhido pela produtividade, tipagem clara e excelente suporte a documentação automática (Swagger/OpenAPI).
* **JWT com OAuth2 Password Flow** centraliza autenticação e autorização, permitindo integração simples entre web e mobile.
* **Controle por roles** garante que regras de acesso fiquem no backend, evitando lógica sensível no frontend.
* **Isolamento por empresa** é tratado como regra de negócio essencial, prevenindo vazamento de dados entre organizações.
* A estrutura em **monorepo** facilita a evolução conjunta das camadas e a padronização de fluxos.

---

## 📌 Observações

* Esta API é utilizada pelos frontends **Web (React)** e **Mobile (React Native)** do projeto LogistiQ.
* O projeto segue uma arquitetura organizada por domínios, facilitando manutenção e evolução.

---

## 📄 Licença

Projeto desenvolvido para fins educacionais e de portfólio.