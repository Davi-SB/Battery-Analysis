from scipy.stats import norm
import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import os
from backend import rodar_fitting, calcular_arquitetura, executar_modelo_cpp

# --- 1. SETUP INICIAL E CARREGAMENTO DE DADOS COM SESSION STATE ---
st.set_page_config(
    page_title="Previsão Baterias",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={}
)


col_logo, col_header = st.columns([1, 10])
col_logo.write("")  # Espaçador
col_logo.image("logo.png")
col_header.title("Previsão de falha de Baterias")

def inicializar_dados():
    """
    Carrega o dataframe a partir do caminho especificado para o session_state, 
    apenas se ainda não tiver sido carregado.
    """
    if 'df_dados' not in st.session_state:
        caminho_arquivo = "Metadata-analysis/HeadersOutput/filenames.csv"
        st.toast(f"Carregando dados de `{caminho_arquivo}`...")
        try:
            st.session_state.df_dados = pd.read_csv(caminho_arquivo)
        except FileNotFoundError:
            st.error(f"**Erro: Arquivo não encontrado!** Verifique se o caminho `{caminho_arquivo}` está correto a partir do diretório onde você executa o Streamlit.")
            st.session_state.df_dados = pd.DataFrame()

# Executa a inicialização dos dados no início do script
inicializar_dados()
filenames_df = st.session_state.df_dados

# --- 2. INTERFACE DO USUÁRIO ---
st.write("")  # Espaçador
st.subheader("Selecione os filtros desejados")
if not filenames_df.empty:
    def criar_selectbox_filtrado(df, coluna, st_element):
        opcoes = ["Não especificar"] + df[coluna].unique().tolist()
        selecao = st_element.selectbox(
            f"{coluna}:", options=opcoes,
            key=f"select_{coluna.replace(' ','_').replace('(','').replace(')','').replace('%','')}"
        )
        return df[df[coluna] == selecao] if selecao != "Não especificar" else df

    col1, col2, col3 = st.columns([1, 1, 2])
    df_filtrado = filenames_df.copy()

    with col1:
        with st.container(border=True, height=200):
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Institution', st)
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Form Factor', st)
        with st.container(border=True, height=200):
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Cathode', st)
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Temperature (°C)', st)
    with col2:
        with st.container(border=True, height=200):
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Min SOC (%)', st)
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Max SOC (%)', st)
        with st.container(border=True, height=200):
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Charge Rate (C)', st)
            df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Discharge Rate (C)', st)
    with col3:
        with st.container(border=True, height=150):
            st.write("**Definir Tensão Nominal**")
            subA_col1, subA_col2 = st.columns(2)
            with subA_col1:
                tensao_nominal = st.number_input("Tensão Nominal Bateria (V):", min_value=0.01, value=12.0, step=0.5, format="%.2f")
            with subA_col2:
                cel_tensao = st.number_input("Tensão da Célula (V):", min_value=0.01, value=5.0, step=0.5, format="%.2f")
            
        with st.container(border=True, height=420):
            st.write("**Definir Capacidade Nominal**")
            subB_col1, subB_col2 = st.columns(2)
            with subB_col1:
                modo_capacidade = st.radio("Modo de entrada:", ["Capacidade", "Corrente e Tempo"], key="modo_capacidade", horizontal=False)
                if modo_capacidade == "Capacidade":
                    df_filtrado = criar_selectbox_filtrado(df_filtrado, 'Capacity (Ah)', st)
                else:
                    #subC_col1, subC_col2 = st.columns(2)
                    corrente = st.number_input("Corrente Bateria (A)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                    tempo = st.number_input("Tempo (h)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                    capacidade_calculada = corrente * tempo
                    capacidades_disponiveis = df_filtrado['Capacity (Ah)'].unique()
                    if len(capacidades_disponiveis) > 0:
                        idx_mais_proximo = (np.abs(capacidades_disponiveis - capacidade_calculada)).argmin()
                        capacidade_mais_proxima = capacidades_disponiveis[idx_mais_proximo]
                        st.info(f"Calculado: {capacidade_calculada:.2f} Ah. Usando a mais próxima: **{capacidade_mais_proxima} Ah**")
                        df_filtrado = df_filtrado[df_filtrado['Capacity (Ah)'] == capacidade_mais_proxima]
                    else:
                        st.warning("Nenhuma capacidade disponível para os filtros atuais.")
                        
            with subB_col2:
                modo_capacidade_cel = st.radio("Modo de entrada:", ["Capacidade", "Corrente e Tempo"], key="modo_capacidade_cel", horizontal=False)
                if modo_capacidade_cel == "Capacidade":
                    cel_cap = st.number_input("Capacidade Celula:", min_value=0.01, value=5.0, step=0.5, format="%.2f")
                else:
                    #subC_col1, subC_col2 = st.columns(2)
                    corrente = st.number_input("Corrente Célula (A)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                    tempo = st.number_input("Tempo (h) ", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                    capacidade_calculada_cel = corrente * tempo

    # --- Expander com Resultados Filtrados (em tempo real) ---
    st.write("") # Espaçador
    if not df_filtrado.empty:
        st.success(f"**{len(df_filtrado)}** combinação(ões) encontrada(s) com os filtros atuais.")
        with st.expander("Clique para ver as combinações encontradas"):
            st.dataframe(df_filtrado)
    else:
        st.warning("Nenhuma combinação encontrada com os filtros atuais.")
    
    st.write("")
    gerar_button = st.button("Gerar Análise", type="primary", use_container_width=True)
    st.divider()

    # --- 3. LÓGICA PRINCIPAL E EXIBIÇÃO DE RESULTADOS ---
    if gerar_button:
        if not df_filtrado.empty:
            if len(df_filtrado) > 1:
                st.info(f"Análise iniciada usando a primeira das {len(df_filtrado)} combinações encontradas.")
            
            linha_selecionada = df_filtrado.iloc[0]
            media, desvio_padrao = rodar_fitting(f"Battery_Archive_Data_NoSubDirs/{linha_selecionada['Full Filename']}")
            
            arquitetura_celula = calcular_arquitetura(linha_selecionada)
            resultado_cpp_csv = executar_modelo_cpp()

            if resultado_cpp_csv and os.path.exists(resultado_cpp_csv):
                st.header("Resultados da Análise")
                res_col1, res_col2 = st.columns([1, 2])
                with res_col1:
                    st.subheader("Arquitetura da Bateria")
                    st.info(arquitetura_celula)
                
                mtta_df = pd.read_csv(resultado_cpp_csv).sort_values(by='MTTA').reset_index(drop=True)
                n = len(mtta_df)
                mtta_df['prob_acumulada'] = np.arange(n) / (n - 1) if n > 1 else 1.0
                with res_col2:
                    st.subheader("Gráfico de Probabilidade Acumulada (do Modelo C++)")
                    st.line_chart(mtta_df, x='MTTA', y='prob_acumulada', height=400)
                with st.expander("Ver dados de MTTA gerados pelo modelo C++"):
                    st.dataframe(mtta_df)
        else:
            st.error("**Nenhuma combinação encontrada.**")
else:
    st.warning("O DataFrame está vazio")