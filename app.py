import streamlit as st
import pandas as pd
import bcrypt
import smtplib
from email.mime.text import MIMEText
from datetime import date
import plotly.express as px
from sqlalchemy import text
import time
import re

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Job Tracker Cloud", layout="wide")

st.markdown("""
    <style>
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; border: 2px solid #f1f1f1; }
    ::-webkit-scrollbar-thumb:hover { background: #888; }
    .subtitle-text { color: #666; font-size: 0.9rem; margin-top: -5px; margin-bottom: 15px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- CONEXÃO COM BANCO ---
conn = st.connection("postgresql", type="sql", connect_args={"sslmode": "require"})

# --- FUNÇÕES DE SEGURANÇA ---
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email):
        return False, "Formato de e-mail inválido."
    return True, ""

# --- CONTROLE DE SESSÃO ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- TELAS DE AUTENTICAÇÃO ---
def tela_acesso():
    st.title("💼 Job Tracker Cloud")
    col1, _ = st.columns([1, 1])
    with col1:
        aba_login, aba_cadastro = st.tabs(["Login", "Criar Conta"])
        with aba_login:
            with st.form("login_form"):
                email_i = st.text_input("Email").strip().lower()
                senha_i = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    res = conn.query("SELECT id, senha_hash FROM usuarios WHERE email = :e", params={"e": email_i}, ttl=0)
                    if not res.empty and check_password(senha_i, res.iloc[0]['senha_hash']):
                        st.session_state.user_id = res.iloc[0]['id']
                        st.session_state.user_email = email_i
                        st.rerun()
                    else: st.error("Incorreto.")
        with aba_cadastro:
            with st.form("cadastro_form"):
                n_email = st.text_input("Novo Email").strip().lower()
                n_senha = st.text_input("Senha (mín. 8)", type="password")
                n_conf = st.text_input("Confirme", type="password")
                if st.form_submit_button("Cadastrar"):
                    v, msg = validar_email(n_email)
                    if not v: st.error(msg)
                    elif n_senha != n_conf: st.error("Senhas diferentes.")
                    elif len(n_senha) < 8: st.warning("Mínimo 8 caracteres.")
                    else:
                        try:
                            with conn.session as s:
                                s.execute(text("INSERT INTO usuarios (email, senha_hash) VALUES (:e, :s)"), {"e": n_email, "s": hash_password(n_senha)})
                                s.commit()
                            st.success("Criado!")
                        except: st.error("Erro no cadastro.")

# --- DASHBOARD ---
if st.session_state.user_id is None:
    tela_acesso()
else:
    # Sidebar
    with st.sidebar:
        st.header(f"👤 {st.session_state.user_email}")
        if st.button("Sair"):
            st.session_state.user_id = None
            st.rerun()
        st.divider()
        plats_df = conn.query("SELECT nome_plataforma FROM plataformas_usuario WHERE user_id = :uid", params={"uid": st.session_state.user_id}, ttl=0)
        lista_plats = plats_df['nome_plataforma'].tolist()
        nova_p = st.text_input("Nova Plataforma")
        if st.button("Adicionar"):
            if nova_p:
                with conn.session as s:
                    s.execute(text("INSERT INTO plataformas_usuario (user_id, nome_plataforma) VALUES (:uid, :n)"), {"uid": st.session_state.user_id, "n": nova_p})
                    s.commit()
                st.rerun()

    # Nova Vaga
    with st.expander("➕ Nova Candidatura"):
        with st.form("vaga_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            v = c1.text_input("Vaga*")
            e = c1.text_input("Empresa")
            d = c2.date_input("Data", date.today())
            p = c2.selectbox("Plataforma*", [""] + lista_plats)
            desc = st.text_area("Descrição", max_chars=3000)
            if st.form_submit_button("Salvar"):
                if v and p:
                    with conn.session as s:
                        s.execute(text("INSERT INTO candidaturas (user_id, vaga, data_cand, plataforma, empresa, descricao) VALUES (:uid, :v, :d, :p, :e, :desc)"),
                                  {"uid": st.session_state.user_id, "v": v, "d": d, "p": p, "e": e, "desc": desc})
                        s.commit()
                    st.success("Salvo!")
                    time.sleep(1)
                    st.rerun()

    # Listagem e Seleção
    st.subheader("📊 Minhas Aplicações")
    st.markdown('<p class="subtitle-text">Clique no quadrado ao lado da vaga para ver detalhes abaixo.</p>', unsafe_allow_html=True)
    
    df_vagas = conn.query("SELECT * FROM candidaturas WHERE user_id = :uid ORDER BY data_cand DESC", params={"uid": st.session_state.user_id}, ttl=0)
    
    if not df_vagas.empty:
        # Forma compatível com versões anteriores do Streamlit (st.dataframe com seleção)
        # Se a sua versão não suportar 'on_select', usamos o retorno direto do event
        event = st.dataframe(
            df_vagas[["vaga", "empresa", "data_cand", "plataforma"]], 
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")
        st.subheader("📝 Detalhes da Candidatura")

        # Captura a seleção de forma segura
        try:
            selecionado = event.selection.rows
            if selecionado:
                idx = selecionado[0]
                detalhes = df_vagas.iloc[idx]
                
                st.markdown(f"### {detalhes['vaga']} @ {detalhes['empresa']}")
                if detalhes['descricao']:
                    st.info(detalhes['descricao'])
                else:
                    st.warning("Sem descrição.")
                
                if st.button("🗑️ Excluir Candidatura"):
                    with conn.session as s:
                        s.execute(text("DELETE FROM candidaturas WHERE id = :id"), {"id": int(detalhes['id'])})
                        s.commit()
                    st.success("Removido!")
                    time.sleep(1)
                    st.rerun()
            else:
                st.write("Selecione uma vaga acima para ver os detalhes.")
        except:
            st.info("Clique na linha da tabela para carregar os detalhes.")

        # Gráficos
        st.divider()
        g1, g2 = st.columns(2)
        with g1:
            st.plotly_chart(px.pie(df_vagas, names='plataforma', title='Candidaturas por Plataforma', hole=0.4), use_container_width=True)
        with g2:
            df_vagas['data_cand'] = pd.to_datetime(df_vagas['data_cand'])
            st.plotly_chart(px.bar(df_vagas.groupby('data_cand').size().reset_index(name='qtd'), x='data_cand', y='qtd', title='Volume Diário'), use_container_width=True)