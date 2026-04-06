import streamlit as st
import pandas as pd
from datetime import date
import io

st.set_page_config(page_title="My Job Tracker - Privado", layout="wide")

# --- FUNÇÕES DE APOIO ---
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# --- INICIALIZAÇÃO DA SESSÃO ---
if 'meus_dados' not in st.session_state:
    st.session_state.meus_dados = pd.DataFrame(columns=[
        "Vaga", "Data", "Empresa", "Site Empresa", 
        "Cargo", "Plataforma", "Salario", "Link Vaga", 
        "Recrutador", "Contato Recrutador", "Descricao"
    ])

# --- SIDEBAR: PRIVACIDADE E ARQUIVOS ---
with st.sidebar:
    st.header("📂 Seus Dados")
    st.write("Seus dados não são salvos em nosso servidor. Para não perdê-los, baixe o arquivo ao final da sessão.")
    
    upload_file = st.file_uploader("Importar meu CSV", type="csv")
    if upload_file is not None:
        st.session_state.meus_dados = pd.read_csv(upload_file)
        st.success("Dados carregados!")

    csv = convert_df(st.session_state.meus_dados)
    st.download_button(
        label="💾 Baixar meu Banco de Dados",
        data=csv,
        file_name='minhas_vagas.csv',
        mime='text/csv',
    )

# --- INTERFACE PRINCIPAL ---
st.title("💼 Tracker de Candidaturas Privado")

with st.expander("➕ Registrar Nova Candidatura"):
    with st.form("form_vaga", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            vaga = st.text_input("Vaga*")
            empresa = st.text_input("Empresa")
            link_vaga = st.text_input("Link da Vaga")
        with col2:
            data_cand = st.date_input("Data", date.today())
            plataforma = st.selectbox("Plataforma", ["LinkedIn", "Gupy", "Glassdoor", "Outro"])
            salario = st.number_input("Salário", min_value=0.0)
        
        submitted = st.form_submit_button("Adicionar à Lista")
        
        if submitted and vaga:
            nova_linha = pd.DataFrame([{
                "Vaga": vaga, "Data": data_cand, "Empresa": empresa,
                "Plataforma": plataforma, "Salario": salario, "Link Vaga": link_vaga
            }])
            st.session_state.meus_dados = pd.concat([st.session_state.meus_dados, nova_linha], ignore_index=True)
            st.rerun()

# --- TABELA DE VISUALIZAÇÃO ---
st.subheader("Candidaturas Atuais")
st.dataframe(st.session_state.meus_dados, use_container_width=True)