import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="My Job Tracker - Privado", layout="wide")

# --- INICIALIZAÇÃO DA SESSÃO ---
if 'meus_dados' not in st.session_state:
    st.session_state.meus_dados = pd.DataFrame(columns=[
        "Vaga", "Data", "Empresa", "Site Empresa", 
        "Plataforma", "Salario", "Link Vaga", 
        "Recrutador", "Contato Recrutador", "Descricao"
    ])

if 'plataformas' not in st.session_state:
    st.session_state.plataformas = []

# --- FUNÇÕES DE APOIO ---
def adicionar_plataforma():
    nova_p = st.session_state.temp_plataforma.strip()
    if nova_p:
        if nova_p not in st.session_state.plataformas:
            st.session_state.plataformas.append(nova_p)
            st.session_state.temp_plataforma = "" # Limpa o campo
        else:
            st.warning(f"A plataforma '{nova_p}' já está cadastrada.")

def remover_plataforma(nome):
    st.session_state.plataformas.remove(nome)

# --- SIDEBAR: GESTÃO E ARQUIVOS ---
with st.sidebar:
    st.header("📂 Configurações e Dados")
    
    # Gestão Dinâmica de Plataformas
    st.subheader("Minhas Plataformas")
    st.text_input("Nova plataforma (Enter para salvar)", key="temp_plataforma", on_change=adicionar_plataforma)
    
    for p in st.session_state.plataformas:
        cols = st.columns([4, 1])
        cols[0].write(p)
        if cols[1].button("−", key=f"del_{p}"):
            remover_plataforma(p)
            st.rerun()

    st.divider()
    csv = st.session_state.meus_dados.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Baixar Banco de Dados", data=csv, file_name='vagas.csv', mime='text/csv')

# --- INTERFACE PRINCIPAL ---
st.title("💼 Tracker de Candidaturas")

with st.expander("➕ Registrar Nova Candidatura", expanded=True):
    with st.form("form_vaga", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            vaga = st.text_input("Vaga (Nome e Cargo)*")
            empresa = st.text_input("Empresa")
            # Campo Editável de Site da Empresa com Placeholder
            site_empresa = st.text_input("Site da Empresa", placeholder="Digite aqui (ex: https://...)")
            
        with col2:
            data_cand = st.date_input("Data", date.today())
            # Seleção baseada nas plataformas criadas pelo usuário
            plataforma_sel = st.selectbox("Selecionar Plataforma", [""] + st.session_state.plataformas)
            salario = st.number_input("Salário", min_value=0.0, step=100.0)

        link_vaga = st.text_input("Link da Vaga")
        
        # Campos bloqueados para digitação (disabled)
        st.text_input("Recrutador", value="Campo bloqueado", disabled=True)
        st.text_input("Contato Recrutador", value="Campo bloqueado", disabled=True)
        descricao = st.text_area("Descrição da Vaga", max_chars=1500, placeholder="Campo bloqueado para digitação manual", disabled=True)
        
        submitted = st.form_submit_button("Salvar Candidatura")
        
        if submitted:
            if not vaga:
                st.error("O campo 'Vaga' é obrigatório.")
            elif not plataforma_sel:
                st.error("Selecione ou cadastre uma plataforma na barra lateral.")
            else:
                nova_linha = pd.DataFrame([{
                    "Vaga": vaga, "Data": data_cand, "Empresa": empresa,
                    "Site Empresa": site_empresa, "Plataforma": plataforma_sel, 
                    "Salario": salario, "Link Vaga": link_vaga,
                    "Recrutador": "N/A", "Contato Recrutador": "N/A", "Descricao": ""
                }])
                st.session_state.meus_dados = pd.concat([st.session_state.meus_dados, nova_linha], ignore_index=True)
                st.success("Candidatura registrada!")
                st.rerun()

# --- VISUALIZAÇÃO ---
st.subheader("📊 Candidaturas Atuais")
# Criando uma visualização onde o link da empresa é clicável na tabela
df_view = st.session_state.meus_dados.copy()
st.data_editor(
    df_view,
    column_config={
        "Site Empresa": st.column_config.LinkColumn("Site Empresa", placeholder="Digite aqui"),
        "Link Vaga": st.column_config.LinkColumn("Link Vaga"),
    },
    use_container_width=True,
    disabled=["Vaga", "Data", "Empresa", "Plataforma", "Salario", "Recrutador", "Contato Recrutador", "Descricao"]
)