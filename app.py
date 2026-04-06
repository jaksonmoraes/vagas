import streamlit as st
import pandas as pd
from datetime import date

st.set_page_config(page_title="My Job Tracker", layout="wide")

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
            st.session_state.temp_plataforma = "" # Limpa o campo após adicionar
        else:
            st.warning(f"A plataforma '{nova_p}' já está cadastrada.")

def remover_plataforma(nome):
    st.session_state.plataformas.remove(nome)

# --- SIDEBAR (GESTÃO DE PLATAFORMAS) ---
with st.sidebar:
    st.header("⚙️ Configurações")
    st.subheader("Cadastrar Plataformas")
    st.info("Digite o nome da plataforma (ex: LinkedIn) e aperte Enter.")
    
    # Campo de digitação com trigger automático
    st.text_input("Nova plataforma:", key="temp_plataforma", on_change=adicionar_plataforma)
    
    if st.session_state.plataformas:
        st.write("---")
        st.write("**Plataformas Ativas:**")
        for p in st.session_state.plataformas:
            cols = st.columns([4, 1])
            cols[0].write(f"• {p}")
            if cols[1].button("−", key=f"del_{p}"):
                remover_plataforma(p)
                st.rerun()
    else:
        st.warning("Nenhuma plataforma cadastrada ainda.")

    st.divider()
    csv = st.session_state.meus_dados.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Baixar Dados (CSV)", data=csv, file_name='minhas_vagas.csv', mime='text/csv')

# --- FORMULÁRIO DE REGISTRO ---
st.title("💼 Tracker de Candidaturas")

with st.expander("➕ Registrar Nova Candidatura", expanded=True):
    with st.form("form_vaga", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            vaga = st.text_input("Vaga (Nome e Cargo)*")
            empresa = st.text_input("Empresa")
            site_empresa = st.text_input("Site da Empresa (URL)")
        with c2:
            data_cand = st.date_input("Data da Candidatura", date.today())
            # O Selectbox agora consome a lista da sidebar
            plataforma_sel = st.selectbox("Selecionar Plataforma*", options=[""] + st.session_state.plataformas)
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)

        link_vaga = st.text_input("Link da Vaga")
        recrutador = st.text_input("Nome do Recrutador")
        contato = st.text_input("Contato (Email/Tel)")
        descricao = st.text_area("Descrição da Vaga", max_chars=1500)
        
        submitted = st.form_submit_button("Salvar Candidatura")
        
        if submitted:
            if not vaga:
                st.error("O campo 'Vaga' é obrigatório.")
            elif not plataforma_sel:
                st.error("Você precisa selecionar uma plataforma. Se a lista estiver vazia, cadastre uma na barra lateral à esquerda.")
            else:
                nova_linha = pd.DataFrame([{
                    "Vaga": vaga, "Data": data_cand, "Empresa": empresa,
                    "Site Empresa": site_empresa, "Plataforma": plataforma_sel, 
                    "Salario": salario, "Link Vaga": link_vaga,
                    "Recrutador": recrutador, "Contato Recrutador": contato, "Descricao": descricao
                }])
                st.session_state.meus_dados = pd.concat([st.session_state.meus_dados, nova_linha], ignore_index=True)
                st.success(f"Candidatura para '{vaga}' salva!")
                st.rerun()

# --- VISUALIZAÇÃO DOS DADOS ---
st.subheader("📊 Suas Candidaturas")

if not st.session_state.meus_dados.empty:
    st.data_editor(
        st.session_state.meus_dados,
        column_config={
            "Site Empresa": st.column_config.LinkColumn("Site Empresa"),
            "Link Vaga": st.column_config.LinkColumn("Link Vaga"),
        },
        use_container_width=True,
        num_rows="dynamic"
    )
else:
    st.info("Nenhuma vaga registrada. Use o formulário acima para começar.")