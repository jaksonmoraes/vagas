import streamlit as st
import pandas as pd
from datetime import date
from turtle import st


import plotly.express as px

st.set_page_config(page_title="My Job Tracker", layout="wide")

# --- INJEÇÃO DE CSS PARA BARRA DE ROLAGEM ---
st.markdown("""
    <style>
    ::-webkit-scrollbar { width: 10px; height: 10px; }
    ::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: #ccc; border-radius: 10px; border: 2px solid #f1f1f1; }
    ::-webkit-scrollbar-thumb:hover { background: #888; }
    * { scrollbar-width: thin; scrollbar-color: #ccc #f1f1f1; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DA SESSÃO ---
if 'meus_dados' not in st.session_state:
    st.session_state.meus_dados = pd.DataFrame(columns=[
        "Vaga", "Data", "Plataforma", "Empresa", "Descricao", 
        "Link Vaga", "Recrutador", "Contato Recrutador", "Site Empresa"
    ])

if 'plataformas' not in st.session_state:
    st.session_state.plataformas = []

# --- FUNÇÕES DE APOIO ---
def adicionar_plataforma():
    nova_p = st.session_state.temp_plataforma.strip()
    if nova_p and nova_p not in st.session_state.plataformas:
        st.session_state.plataformas.append(nova_p)
        st.session_state.temp_plataforma = ""

def remover_plataforma(nome):
    st.session_state.plataformas.remove(nome)

@st.dialog("Detalhes da Vaga")
def mostrar_modal_descricao(titulo, texto):
    st.subheader(titulo)
    st.write(texto if texto else "Sem descrição.")
    if st.button("Fechar"):
        st.rerun()

# --- SIDEBAR (IMPORTAR/EXPORTAR E PLATAFORMAS) ---
with st.sidebar:
    st.header("⚙️ Gestão de Dados")
    
    # NOVO: Seção de Importação
    st.subheader("📥 Importar Dados")
    arquivo_upload = st.file_uploader("Suba seu arquivo vagas.csv", type="csv")
    
    if arquivo_upload is not None:
        try:
            df_importado = pd.read_csv(arquivo_upload)
            # Verifica se as colunas batem para evitar erros
            colunas_necessarias = ["Vaga", "Data", "Plataforma", "Empresa"]
            if all(col in df_importado.columns for col in colunas_necessarias):
                st.session_state.meus_dados = df_importado
                # Atualiza a lista de plataformas baseada no arquivo importado
                plataformas_do_arquivo = df_importado['Plataforma'].unique().tolist()
                for p in plataformas_do_arquivo:
                    if p not in st.session_state.plataformas:
                        st.session_state.plataformas.append(p)
                st.success("Dados carregados com sucesso!")
            else:
                st.error("O arquivo não parece ter o formato correto.")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")

    st.divider()

    # Gestão de Plataformas
    st.subheader("Cadastrar Plataformas")
    st.text_input("Nova plataforma:", key="temp_plataforma", on_change=adicionar_plataforma)
    if st.session_state.plataformas:
        for p in st.session_state.plataformas:
            cols = st.columns([4, 1])
            cols[0].write(f"• {p}")
            if cols[1].button("−", key=f"del_{p}"):
                remover_plataforma(p)
                st.rerun()
    
    st.divider()
    
    # Exportação
    st.subheader("📤 Exportar Dados")
    csv = st.session_state.meus_dados.to_csv(index=False).encode('utf-8')
    st.download_button("💾 Baixar CSV Atualizado", data=csv, file_name='vagas.csv', mime='text/csv')

# --- FORMULÁRIO DE CADASTRO (PRESERVADO) ---
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
            plataforma_sel = st.selectbox("Selecionar Plataforma*", options=[""] + st.session_state.plataformas)
            salario = st.number_input("Salário (R$)", min_value=0.0, step=100.0)

        link_vaga = st.text_input("Link da Vaga")
        recrutador = st.text_input("Nome do Recrutador")
        contato = st.text_input("Contato (Email/Tel)")
        descricao = st.text_area("Descrição da Vaga", max_chars=1500)
        
        submitted = st.form_submit_button("Salvar Candidatura")
        
        if submitted:
            if not vaga or not plataforma_sel:
                st.error("Campos Vaga e Plataforma são obrigatórios.")
            else:
                nova_linha = pd.DataFrame([{
                    "Vaga": vaga, "Data": data_cand, "Plataforma": plataforma_sel,
                    "Empresa": empresa, "Descricao": descricao, "Link Vaga": link_vaga,
                    "Recrutador": recrutador, "Contato Recrutador": contato, "Site Empresa": site_empresa
                }])
                st.session_state.meus_dados = pd.concat([st.session_state.meus_dados, nova_linha], ignore_index=True)
                st.success(f"Candidatura para '{vaga}' salva!")
                st.rerun()

# --- VISUALIZAÇÃO DOS DADOS (REORDENADO) ---
st.subheader("📊 Suas Candidaturas")

if not st.session_state.meus_dados.empty:
    # A ordem das colunas abaixo segue exatamente o que você solicitou
    ordem_colunas = ["Vaga", "Data", "Plataforma", "Empresa", "Descricao", "Link Vaga", "Recrutador", "Contato Recrutador", "Site Empresa"]
    
    st.data_editor(
        st.session_state.meus_dados[ordem_colunas],
        column_config={
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Link Vaga": st.column_config.LinkColumn("Link Vaga"),
            "Site Empresa": st.column_config.LinkColumn("Site Empresa"),
            "Descricao": st.column_config.TextColumn("Descrição (Prévia)", width="small")
        },
        use_container_width=True,
        num_rows="dynamic",
        key="editor_vagas"
    )

    # Botão para abrir o Modal de Foco
    st.info("💡 Selecione uma vaga para visualizar a descrição completa em foco:")
    vaga_idx = st.selectbox("Vaga selecionada:", 
                            options=range(len(st.session_state.meus_dados)),
                            format_func=lambda x: f"{st.session_state.meus_dados.iloc[x]['Vaga']} @ {st.session_state.meus_dados.iloc[x]['Empresa']}")
    
    if st.button("🔍 Ver Descrição em Foco"):
        vaga_info = st.session_state.meus_dados.iloc[vaga_idx]
        mostrar_modal_descricao(vaga_info['Vaga'], vaga_info['Descricao'])

# --- ANÁLISE DE DADOS (GRÁFICOS) ---
if not st.session_state.meus_dados.empty:
    st.divider()
    st.subheader("📈 Estatísticas")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        df_p = st.session_state.meus_dados['Plataforma'].value_counts().reset_index()
        fig1 = px.pie(df_p, values='count', names='Plataforma', title='Vagas por Plataforma', hole=0.4)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_g2:
        df_t = st.session_state.meus_dados.groupby('Data').size().reset_index(name='Qtd')
        fig2 = px.bar(df_t, x='Data', y='Qtd', title='Candidaturas por Período')
        st.plotly_chart(fig2, use_container_width=True)