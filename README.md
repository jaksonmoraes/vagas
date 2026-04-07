# 💼 Minhas Vagas

O **Minhas Vagas** é um dashboard interativo desenvolvido em Python com Streamlit para o gerenciamento centralizado de candidaturas a vagas de emprego. O sistema permite cadastrar, visualizar e analisar o histórico de aplicações, agora utilizando persistência em banco de dados relacional e recursos avançados de segurança.

## 🚀 Novidades desta Versão
- **Banco de Dados Relacional:** Migração de CSV para PostgreSQL (via SQLAlchemy) para maior integridade e escalabilidade dos dados.
- **Segurança Reforçada:** Implementação de hashing de senhas com `bcrypt` e validação de e-mails com Regex.
- **UX Interativa:** Seleção dinâmica de candidaturas diretamente na tabela para visualização de detalhes.
- **Persistência de Plataformas:** Cadastro personalizado de plataformas de vagas por usuário.

## 🛠️ Tecnologias Utilizadas
- **Python 3.10+**
- **Streamlit:** Interface web e dashboard.
- **SQLAlchemy:** ORM para comunicação com o PostgreSQL.
- **PostgreSQL:** Banco de dados relacional.
- **Pandas:** Manipulação de dados e integração com tabelas.
- **Plotly Express:** Visualizações gráficas de desempenho.
- **Bcrypt:** Criptografia de senhas.

## 📋 Funcionalidades
- **Autenticação:** Sistema de Login e Cadastro com validação de formato de e-mail e confirmação de senha.
- **Gestão de Candidaturas:** Cadastro completo incluindo Vaga, Empresa, Link, Recrutador, Contato, Salário Pretendido e Descrição Detalhada.
- **Visualização Inteligente:**
  - Tabela interativa com `on_select` para carregar detalhes sem trocar de tela.
  - Gráfico de pizza por plataforma de vaga.
  - Gráfico de barras de volume de candidaturas diárias.
- **Gestão de Plataformas:** Adição e remoção de plataformas (LinkedIn, Gupy, etc.) diretamente via Sidebar.

## ⚙️ Configuração (Secrets)
Para rodar este projeto, é necessário configurar o arquivo `.streamlit/secrets.toml` com as credenciais do banco e do serviço de e-mail:

```toml
[connections.postgresql]
dialect = "postgresql"
host = "seu-host"
user = "seu-usuario"
password = "sua-senha"
database = "seu-banco"
port = 5432

[email_auth]
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "seu-email@gmail.com"
smtp_pass = "sua-senha-de-app"


🏗️ Estrutura do Banco (SQL)
O sistema espera as tabelas usuarios, plataformas_usuario e candidaturas.
Dica: Certifique-se de aplicar a CONSTRAINT de formato de e-mail no banco para garantir a integridade dos dados.

-- Exemplo de constraint de e-mail aplicada
ALTER TABLE usuarios ADD CONSTRAINT email_check 
CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-zA-Z]{2,}$');


✒️ Autor
**Jakson Moraes - GitHub**
