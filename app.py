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

def send_recovery_email(to_email):
    msg = MIMEText(f"Olá! Você solicitou a recuperação de acesso ao Job Tracker.\nPara resetar sua senha, use o código temporário: RECOVERY2026")
    msg['Subject'] = 'Recuperação de Acesso - Job Tracker'
    msg['From'] = st.secrets["email_auth"]["smtp_user"]
    msg['To'] = to_email.strip().lower()
    try:
        with smtplib.SMTP(st.secrets["email_auth"]["smtp_server"], st.secrets["email_auth"]["smtp_port"]) as server:
            server.starttls()
            server.login(st.secrets["email_auth"]["smtp_user"], st.secrets["email_auth"]["smtp_pass"])
            server.send_message(msg)
        return True
    except:
        return False

def validar_email(email):
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email) is not None

# --- CONTROLE DE SESSÃO ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

# --- TELAS DE AUTENTICAÇÃO ---
def tela_acesso():
    st.title("💼 Job Tracker Cloud")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        aba_login, aba_cadastro, aba_recuperar = st.tabs(["Login", "Criar Conta", "Recuperar"])
        
        with aba_login:
            with st.form("login_form"):
                email_input = st.text_input("Email").strip().lower()
                senha_input = st.text_input("Senha", type="password")
                
                if st.form_submit_button("Entrar"):
                    res = conn.query(
                        "SELECT id, senha_hash FROM usuarios WHERE email = :e",
                        params={"e": email_input},
                        ttl=0
                    )
                    
                    if not res.empty and check_password(senha_input, res.iloc[0]['senha_hash']):
                        st.session_state.user_id = res.iloc[0]['id']
                        st.session_state.user_email = email_input
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

        with aba_cadastro:
            with st.form("cadastro_form"):
                n_email = st.text_input("Novo Email").strip().lower()
                n_senha = st.text_input("Senha (mín. 8 caracteres)", type="password")
                n_confirma = st.text_input("Confirme a Senha", type="password")
                
                if st.form_submit_button("Cadastrar"):
                    if not validar_email(n_email):
                        st.error("Por favor, insira um e-mail válido.")
                    elif n_senha != n_confirma:
                        st.error("As senhas não coincidem.")
                    elif len(n_senha) < 8:
                        st.warning("A senha deve ter pelo menos 8 caracteres.")
                    else:
                        senha_h = hash_password(n_senha)
                        try:
                            with conn.session as s:
                                s.execute(
                                    text("INSERT INTO usuarios (email, senha_hash) VALUES (:e, :s)"),
                                    {"e": n_email, "s": senha_h}
                                )
                                s.commit()
                            st.success("Conta criada! Faça login.")
                        except Exception as e:
                            if "unique constraint" in str(e).lower():
                                st.error("Este email já está em uso.")
                            else:
                                st.error("Erro ao processar cadastro no banco de dados.")
        
        with aba_recuperar:
            r_email = st.text_input("Email para recuperação").strip().lower()
            if st.button("Enviar E-mail"):
                if r_email:
                    if send_recovery_email(r_email):
                        st.success("E-mail de recuperação enviado!")
                    else:
                        st.error("Erro no serviço de e-mail.")
                else:
                    st.warning("Informe o e-mail cadastrado.")

# --- DASHBOARD PRINCIPAL (LOGADO) ---
if st.session_state.user_id is None:
    tela_acesso()
else:
    # Sidebar: Gestão de Plataformas
    with st.sidebar:
        st.header(f"👤 {st.session_state.user_email}")
        if st.button("Sair"):
            st.session_state.user_id = None
            st.rerun()
        
        st.divider()
        st.subheader("Minhas Plataformas")
        nova_p = st.text_input("Adicionar Plataforma")
        if st.button("Adicionar"):
            if nova_p:
                try:
                    with conn.session as s:
                        s.execute(
                            text("INSERT INTO plataformas_usuario (user_id, nome_plataforma) VALUES (:uid, :nome)"), 
                            {"uid": st.session_state.user_id, "nome": nova_p}
                        )
                        s.commit()
                    st.rerun()
                except:
                    st.warning("Plataforma já cadastrada.")
        
        plats_df = conn.query(
            "SELECT nome_plataforma FROM plataformas_usuario WHERE user_id = :uid", 
            params={"uid": st.session_state.user_id},
            ttl=0
        )
        lista_plats = plats_df['nome_plataforma'].tolist()
        
        for p in lista_plats:
            c_p1, c_p2 = st.columns([4, 1])
            c_p1.write(f"• {p}")
            if c_p2.button("🗑️", key=f"del_{p}"):
                with conn.session as s:
                    s.execute(
                        text("DELETE FROM plataformas_usuario WHERE user_id = :uid AND nome_plataforma = :nome"), 
                        {"uid": st.session_state.user_id, "nome": p}
                    )
                    s.commit()
                st.rerun()

    # Formulário de Cadastro de Vaga
    with st.expander("➕ Nova Candidatura", expanded=False):
        with st.form("add_vaga", clear_on_submit=True):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                f_vaga = st.text_input("Vaga*")
                f_empresa = st.text_input("Empresa")
                f_site = st.text_input("Site Empresa")
            with col_v2:
                f_data = st.date_input("Data", date.today())
                f_plat = st.selectbox("Plataforma*", [""] + (lista_plats if lista_plats else []))
                f_salario = st.number_input("Salário", min_value=0.0)
            
            f_link = st.text_input("Link da Vaga")
            f_recru = st.text_input("Recrutador")
            f_contato = st.text_input("Contato")
            f_desc = st.text_area("Descrição", max_chars=3000)
            
            if st.form_submit_button("Salvar no Banco"):
                if f_vaga and f_plat:
                    try:
                        with conn.session as s:
                            query_ins = text("""INSERT INTO candidaturas 
                                (user_id, vaga, data_cand, plataforma, empresa, descricao, link_vaga, recrutador, contato_recrutador, site_empresa, salario) 
                                VALUES (:uid, :v, :d, :p, :e, :desc, :l, :r, :c, :s_e, :sal)""")
                            s.execute(query_ins, {
                                "uid": st.session_state.user_id, "v": f_vaga, "d": f_data, "p": f_plat, "e": f_empresa, 
                                "desc": f_desc, "l": f_link, "r": f_recru, "c": f_contato, "s_e": f_site, "sal": f_salario
                            })
                            s.commit()
                        st.success("Vaga salva com sucesso!")
                        time.sleep(1)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"Erro ao salvar candidatura.")
                else:
                    st.error("Vaga e Plataforma são campos obrigatórios.")

    # Tabela de Dados e Detalhes
    st.subheader("📊 Minhas Aplicações")
    st.markdown('<p class="subtitle-text">Clique sobre uma vaga na tabela para ver sua descrição e requisitos abaixo.</p>', unsafe_allow_html=True)
    
    df_vagas = conn.query(
        "SELECT * FROM candidaturas WHERE user_id = :uid ORDER BY data_cand DESC", 
        params={"uid": st.session_state.user_id},
        ttl=0
    )
    
    if not df_vagas.empty:
        # 1. TABELA INTERATIVA
        event = st.dataframe(
            df_vagas[["vaga", "empresa", "data_cand", "plataforma"]], 
            use_container_width=True,
            hide_index=True
        )
        
        # 2. BLOCO DE DETALHES (Dinamizado pelo clique na tabela)
        st.markdown("---")
        st.subheader("📝 Detalhes da Candidatura")
        
        selecionado = event.selection.rows if hasattr(event, 'selection') else []
        
        if selecionado:
            idx = selecionado[0]
            detalhes = df_vagas.iloc[idx]
            
            st.markdown(f"### {detalhes['vaga']} @ {detalhes['empresa'] if detalhes['empresa'] else 'N/A'}")
            
            d_col1, d_col2, d_col3 = st.columns(3)
            d_col1.write(f"📅 **Data:** {detalhes['data_cand']}")
            d_col1.write(f"🖥️ **Plataforma:** {detalhes['plataforma']}")
            
            d_col2.write(f"👤 **Recrutador:** {detalhes['recrutador'] if detalhes['recrutador'] else 'N/A'}")
            d_col2.write(f"📞 **Contato:** {detalhes['contato_recrutador'] if detalhes['contato_recrutador'] else 'N/A'}")
            
            sal_val = detalhes['salario'] if pd.notnull(detalhes['salario']) else 0.0
            d_col3.write(f"💰 **Salário:** R$ {sal_val:,.2f}")
            if detalhes['link_vaga']: d_col3.markdown(f"🔗 [Link da Vaga]({detalhes['link_vaga']})")
            if detalhes['site_empresa']: d_col3.markdown(f"🌐 [Site Empresa]({detalhes['site_empresa']})")

            st.markdown("**Descrição e Requisitos:**")
            if detalhes['descricao']:
                st.info(detalhes['descricao'])
            else:
                st.warning("Nenhuma descrição cadastrada.")
            
            if st.button("🗑️ Excluir esta Candidatura"):
                with conn.session as s:
                    s.execute(text("DELETE FROM candidaturas WHERE id = :id"), {"id": int(detalhes['id'])})
                    s.commit()
                st.success("Excluída!")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Selecione uma vaga na tabela acima para visualizar os detalhes completos.")

        # 3. GRÁFICOS
        st.markdown("---")
        st.subheader("📈 Análise de Candidaturas")
        g1, g2 = st.columns(2)
        with g1:
            fig_p = px.pie(df_vagas, names='plataforma', title='Por Plataforma', hole=0.4)
            st.plotly_chart(fig_p, use_container_width=True)
        with g2:
            df_vagas['data_cand'] = pd.to_datetime(df_vagas['data_cand'])
            df_timeline = df_vagas.groupby('data_cand').size().reset_index(name='qtd')
            fig_t = px.bar(df_timeline, x='data_cand', y='qtd', title='Candidaturas por Dia')
            st.plotly_chart(fig_t, use_container_width=True)
    else:
        st.info("Nenhuma candidatura encontrada. Comece cadastrando uma acima!")