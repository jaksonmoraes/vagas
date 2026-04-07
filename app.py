import streamlit as st
import pandas as pd
import bcrypt
import smtplib
from email.mime.text import MIMEText
from datetime import date
import plotly.express as px
from sqlalchemy import text

# --- CONFIGURAÇÃO E ESTILO ---
st.set_page_config(page_title="Job Tracker Cloud", layout="wide")

st.markdown("""
    <style>
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; border: 2px solid #f1f1f1; }
    ::-webkit-scrollbar-thumb:hover { background: #888; }
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
    msg = MIMEText(f"Olá! Você solicitou a recuperação de acesso ao Job Tracker.\nPara resetar sua senha, entre em contato com o administrador ou use o código temporário: RECOVERY2026")
    msg['Subject'] = 'Recuperação de Acesso - Job Tracker'
    msg['From'] = st.secrets["email_auth"]["smtp_user"]
    msg['To'] = to_email
    try:
        with smtplib.SMTP(st.secrets["email_auth"]["smtp_server"], st.secrets["email_auth"]["smtp_port"]) as server:
            server.starttls()
            server.login(st.secrets["email_auth"]["smtp_user"], st.secrets["email_auth"]["smtp_pass"])
            server.send_message(msg)
        return True
    except Exception as e:
        return False

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
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    res = conn.query(f"SELECT id, senha_hash FROM usuarios WHERE email = '{email}'", ttl=0)
                    if not res.empty and check_password(senha, res.iloc[0]['senha_hash']):
                        st.session_state.user_id = res.iloc[0]['id']
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

        with aba_cadastro:
            with st.form("cadastro_form"):
                n_email = st.text_input("Novo Email")
                n_senha = st.text_input("Senha (mín. 8 caracteres)", type="password")
                if st.form_submit_button("Cadastrar"):
                    if len(n_senha) < 8:
                        st.warning("A senha deve ter pelo menos 8 caracteres.")
                    else:
                        senha_h = hash_password(n_senha)
                        try:
                            with conn.session as s:
                                s.execute(text("INSERT INTO usuarios (email, senha_hash) VALUES (:e, :s)"), {"e": n_email, "s": senha_h})
                                s.commit()
                            st.success("Conta criada! Faça login.")
                        except Exception as e:
                            # Aqui pegamos o erro real do banco
                            if "unique constraint" in str(e).lower():
                                st.error("Este email já está em uso.")
                            else:
                                st.error(f"Erro de conexão com o banco: {str(e)[:100]}")

# --- DASHBOARD PRINCIPAL (LOGADO) ---
if st.session_state.user_id is None:
    tela_acesso()
else:
    # Sidebar: Gestão de Plataformas no Banco
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
                        s.execute(text("INSERT INTO plataformas_usuario (user_id, nome_plataforma) VALUES (:uid, :nome)"), 
                                 {"uid": st.session_state.user_id, "nome": nova_p})
                        s.commit()
                    st.rerun()
                except:
                    st.warning("Plataforma já cadastrada.")
        
        # Lista plataformas do usuário
        plats_df = conn.query(f"SELECT nome_plataforma FROM plataformas_usuario WHERE user_id = '{st.session_state.user_id}'", ttl=0)
        lista_plats = plats_df['nome_plataforma'].tolist()
        for p in lista_plats:
            c_p1, c_p2 = st.columns([4, 1])
            c_p1.write(f"• {p}")
            if c_p2.button("🗑️", key=f"del_{p}"):
                with conn.session as s:
                    s.execute(text("DELETE FROM plataformas_usuario WHERE user_id = :uid AND nome_plataforma = :nome"), 
                             {"uid": st.session_state.user_id, "nome": p})
                    s.commit()
                st.rerun()

    # Formulário de Cadastro de Vaga
    with st.expander("➕ Nova Candidatura", expanded=False):
        # Usamos o clear_on_submit=True para ajudar na limpeza visual
        with st.form("add_vaga", clear_on_submit=True):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                f_vaga = st.text_input("Vaga*")
                f_empresa = st.text_input("Empresa")
                f_site = st.text_input("Site Empresa")
            with col_v2:
                f_data = st.date_input("Data", date.today())
                # Garantimos que a lista de plataformas não quebre se estiver vazia
                f_plat = st.selectbox("Plataforma*", [""] + (lista_plats if 'lista_plats' in locals() else []))
                f_salario = st.number_input("Salário", min_value=0.0)
            
            f_link = st.text_input("Link da Vaga")
            f_recru = st.text_input("Recrutador")
            f_contato = st.text_input("Contato")
            f_desc = st.text_area("Descrição", max_chars=1500)
            
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
                        # O PULO DO GATO: Aguarda um breve momento e reinicia a página
                        import time
                        time.sleep(1)
                        st.rerun() 
                        
                    except Exception as e:
                        st.error(f"Erro ao salvar: {e}")
                else:
                    st.error("Vaga e Plataforma são campos obrigatórios.")

    # Tabela de Dados (Filtrada por Usuário)
    st.subheader("📊 Minhas Aplicações")
    df_vagas = conn.query(f"SELECT * FROM candidaturas WHERE user_id = '{st.session_state.user_id}' ORDER BY data_cand DESC", ttl=0)


    # --- INSERIR O CÓDIGO DO SELECTBOX AQUI (Entre a tabela e o gráfico) ---

if not df_vagas.empty:
    st.markdown("---")
    st.subheader("📝 Detalhes da Candidatura")
    
    # Criamos a lista de opções combinando Vaga e Empresa para facilitar a leitura
    opcoes_vagas = df_vagas.apply(
        lambda x: f"{x['vaga']} @ {x['empresa'] if x.get('empresa') else 'Não Informada'}", 
        axis=1
    ).tolist()
    
    # O selectbox para o usuário escolher qual descrição quer ler
    escolha = st.selectbox("Selecione uma vaga para ver os detalhes:", opcoes_vagas)
    
    # Pegamos o índice da escolha para buscar a descrição correta no DataFrame
    idx = opcoes_vagas.index(escolha)
    detalhes = df_vagas.iloc[idx]
    
    # Exibição elegante da descrição
    if detalhes['descricao']:
        st.info(f"**Descrição da vaga:**\n\n{detalhes['descricao']}")
    else:
        st.warning("Esta candidatura não possui uma descrição detalhada.")
    
    st.markdown("---")

# --- FIM DO TRECHO ---

    
    if not df_vagas.empty:
        # Reordenação para exibição
        cols_order = ["vaga", "data_cand", "plataforma", "empresa", "descricao", "link_vaga", "recrutador", "contato_recrutador", "site_empresa"]
        st.data_editor(df_vagas[cols_order], use_container_width=True)
        
        # Gráficos
        st.divider()
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