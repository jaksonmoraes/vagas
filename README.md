# vagas
Este repositório destina-se a disponibilizar um local onde o usuário pode ter um controle sobre as vagas as quais se candidatou.
# 💼 Job Tracker - Gerenciador de Candidaturas (Privacy Focused)

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white)

Este é um sistema desenvolvido para auxiliar profissionais na organização e rastreio de candidaturas a vagas de emprego. O projeto foi construído com foco em **agilidade**, **análise de dados futura** e, principalmente, **privacidade do usuário**.

## 🛡️ Privacidade e LGPD (General Data Protection Regulation)

Diferente de sistemas convencionais, este rastreador foi arquitetado sob o princípio de **Privacy by Design**:

* **Zero Data Storage:** O sistema não possui banco de dados persistente no servidor. Nenhuma informação inserida é salva ou acessada pelo administrador do projeto.
* **Controle do Usuário:** Todos os dados residem na memória temporária da sessão do navegador. O usuário é o único detentor de suas informações.
* **Portabilidade:** O sistema permite que o usuário baixe seu próprio banco de dados em formato `.csv` e o recarregue em sessões futuras, garantindo total autonomia sobre seus dados pessoais e profissionais.

---

## 🚀 Funcionalidades

* **Registro Completo:** Nome da vaga, empresa, cargo, salário, plataforma e links de acompanhamento.
* **Gestão de Contatos:** Campo dedicado para nome e contato do recrutador.
* **Visualização em Tempo Real:** Tabela dinâmica para consulta rápida das candidaturas ativas.
* **Importação/Exportação:** Salve seu progresso localmente e retome quando quiser.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface:** Streamlit (Framework Web para Ciência de Dados)
* **Manipulação de Dados:** Pandas
* **Deployment:** Streamlit Community Cloud

---

## 💻 Como Rodar o Projeto Localmente

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/jaksonmoraes/vagas.git](https://github.com/jaksonmoraes/vagas.git)
    cd vagas
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python -m venv venv
    # Windows
    .\venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Execute a aplicação:**
    ```bash
    streamlit run app.py
    ```

---

## 📈 Próximos Passos (Roadmap)
- [ ] Implementação de Dashboard de análise (Gráficos de taxas de conversão por plataforma).
- [ ] Filtros por status da candidatura (Em andamento, Entrevista, Finalizado).
- [ ] Cálculo de tempo médio de resposta das empresas.

---

**Desenvolvido por [Jakson Moraes](https://www.linkedin.com/in/SEU-PERFIL-AQUI/)**