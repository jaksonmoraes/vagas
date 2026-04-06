import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

# ... (Mantenha seu set_page_config, CSS da barra de rolagem e inicialização de sessão aqui) ...

# --- FUNÇÃO DO MODAL (DIÁLOGO) ---
@st.dialog("Descrição da Vaga")
def mostrar_descricao(texto):
    st.write(texto)
    if st.button("Fechar"):
        st.rerun()

# --- INTERFACE PRINCIPAL ---
# ... (Mantenha seu formulário de cadastro aqui) ...

# --- VISUALIZAÇÃO DOS DADOS REORDENADOS ---
st.subheader("📊 Suas Candidaturas")

if not st.session_state.meus_dados.empty:
    # 1. REORDENAÇÃO DAS COLUNAS
    ordem_colunas = [
        "Vaga", "Data", "Plataforma", "Empresa", "Descricao", 
        "Link Vaga", "Recrutador", "Contato Recrutador", "Site Empresa"
    ]
    
    # Garantir que o DF siga a ordem para exibição
    df_ordenado = st.session_state.meus_dados[ordem_colunas]

    # 2. TABELA EDITÁVEL
    st.data_editor(
        df_ordenado,
        column_config={
            "Vaga": st.column_config.TextColumn("Vaga", width="medium"),
            "Data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "Plataforma": "Plataforma",
            "Empresa": "Empresa",
            "Descricao": st.column_config.TextColumn("Descrição (Visualização resumida)", width="small"),
            "Link Vaga": st.column_config.LinkColumn("Link da Vaga"),
            "Recrutador": "Recrutador",
            "Contato Recrutador": "Contato",
            "Site Empresa": st.column_config.LinkColumn("Site da Empresa"),
        },
        use_container_width=True,
        num_rows="dynamic",
        key="editor_vagas"
    )

    # 3. MODAL DE FOCO (Workaround para focar na descrição)
    st.write("---")
    st.info("💡 Para ler a descrição completa em foco, selecione a vaga abaixo:")
    
    # Criamos um seletor para abrir o modal de forma limpa
    vaga_para_ver = st.selectbox(
        "Visualizar detalhes de:", 
        options=range(len(st.session_state.meus_dados)),
        format_func=lambda x: f"{st.session_state.meus_dados.iloc[x]['Vaga']} - {st.session_state.meus_dados.iloc[x]['Empresa']}"
    )
    
    if st.button("🔍 Abrir Detalhes em Foco"):
        texto_completo = st.session_state.meus_dados.iloc[vaga_para_ver]['Descricao']
        mostrar_descricao(texto_completo if texto_completo else "Nenhuma descrição cadastrada.")

# --- GRÁFICOS (Mantenha seu código de gráficos aqui) ---


# ... (seu código anterior da tabela)

# --- SEÇÃO DE ANÁLISE DE DADOS ---
if not st.session_state.meus_dados.empty:
    st.divider()
    st.subheader("📈 Análise de Candidaturas")
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Gráfico de Pizza: Vagas por Plataforma
        df_contagem = st.session_state.meus_dados['Plataforma'].value_counts().reset_index()
        df_contagem.columns = ['Plataforma', 'Total']
        
        fig = px.pie(df_contagem, values='Total', names='Plataforma', 
                     title='Distribuição por Plataforma',
                     hole=0.3, # Gráfico de rosca fica mais moderno
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        # Gráfico de Barras: Vagas ao longo do tempo
        df_tempo = st.session_state.meus_dados.groupby('Data').size().reset_index(name='Quantidade')
        fig2 = px.bar(df_tempo, x='Data', y='Quantidade', 
                      title='Candidaturas por Dia',
                      color_discrete_sequence=['#FF4B4B'])
        st.plotly_chart(fig2, use_container_width=True)