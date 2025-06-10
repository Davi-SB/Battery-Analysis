from scipy.stats import norm
import streamlit as st
import pandas as pd
import numpy as np
import os
from backend import rodar_fitting, calcular_arquitetura, executar_modelo_cpp

# --- SETUP INICIAL ---
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
    # Carrega o dataframe a partir do caminho especificado para o session_state, se ainda não tiver sido carregado
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
if filenames_df.empty: st.warning("O DataFrame está vazio")

# Declaração global
cel_voltage = -9999999
bat_voltage = -9999999
bat_cap     = -9999999

# --- INTERFACE DO USUÁRIO ---
st.write("")  # Espaçador
st.subheader("Selecione os filtros desejados")

def criar_selectbox_filtrado(df, coluna, st_element, label=None):
    if label is None: label = coluna
    opcoes = ["Não especificar"] + df[coluna].unique().tolist()
    selecao = st_element.selectbox(
        f"{label}:", options=opcoes,
        key=f"select_{coluna.replace(' ','_').replace('(','').replace(')','').replace('%','')}"
    )
    return df[df[coluna] == selecao] if selecao != "Não especificar" else df

col1, col2, col3 = st.columns([1, 1, 2])
df_filtered = filenames_df.copy()

with col1:
    with st.container(border=True, height=200):
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Institution', st)
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Form Factor', st)
    with st.container(border=True, height=200):
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Cathode', st)
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Temperature (°C)', st)
with col2:
    with st.container(border=True, height=200):
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Min SOC (%)', st)
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Max SOC (%)', st)
    with st.container(border=True, height=200):
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Charge Rate (C)', st)
        df_filtered = criar_selectbox_filtrado(df_filtered, 'Discharge Rate (C)', st)
with col3:
    with st.container(border=True, height=150):
        st.write("**Definir Tensão Nominal**")
        subA_col1, subA_col2 = st.columns(2)
        with subA_col1:
            # Tensão da célula congelada em 3.6V
            cel_voltage = st.number_input("Tensão da Célula (V) [fixo]:", min_value=0.01, value=3.6, step=0.000001, format="%.2f")
            cel_voltage = 3.6
        with subA_col2:
            bat_voltage = st.number_input("Tensão Nominal Bateria (V):", min_value=cel_voltage, value=18.0, step=0.5, format="%.2f")
        
    with st.container(border=True, height=420):
        st.write("**Definir Capacidade Nominal**")
        subB_col1, subB_col2 = st.columns(2)
        with subB_col1:
            modo_capacidade_cel = st.radio("Modo de entrada:", ["Capacidade", "Corrente e Tempo"], key="modo_capacidade_cel", horizontal=False)
            if modo_capacidade_cel == "Capacidade":
                df_filtered = criar_selectbox_filtrado(df_filtered, 'Capacity (Ah)', st, label="Capacidade Célula (Ah)")
            else:
                #subC_col1, subC_col2 = st.columns(2)
                corrente = st.number_input("Corrente Célula (A)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                tempo = st.number_input("Tempo (h)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                capacidade_calculada = corrente * tempo
                capacidades_disponiveis = df_filtered['Capacity (Ah)'].unique()
                if len(capacidades_disponiveis) > 0:
                    idx_mais_proximo = (np.abs(capacidades_disponiveis - capacidade_calculada)).argmin()
                    capacidade_mais_proxima = capacidades_disponiveis[idx_mais_proximo]
                    st.info(f"Calculado: {capacidade_calculada:.2f} Ah. Usando a mais próxima: **{capacidade_mais_proxima} Ah**")
                    df_filtered = df_filtered[df_filtered['Capacity (Ah)'] == capacidade_mais_proxima]
                else:
                    st.warning("Nenhuma capacidade disponível para os filtros atuais.")
                    
        with subB_col2:
            modo_capacidade_bat = st.radio("Modo de entrada:", ["Capacidade", "Corrente e Tempo"], key="modo_capacidade_bat", horizontal=False)
            if modo_capacidade_bat == "Capacidade":
                bat_cap = st.number_input("Capacidade Bateria (Ah):", min_value=0.01, value=5.0, step=0.5, format="%.2f")
            else:
                #subC_col1, subC_col2 = st.columns(2)
                corrente = st.number_input("Corrente Bateria (A)", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                tempo = st.number_input("Tempo (h) ", min_value=0.01, value=1.0, step=0.5, format="%.2f")
                bat_cap = corrente * tempo
                st.write("")
                st.info(f"Calculado: {bat_cap:.2f} Ah")

# --- Expander com Resultados Filtrados (em tempo real) ---
st.write("") # Espaçador
if not df_filtered.empty:
    st.success(f"**{len(df_filtered)}** combinação(ões) encontrada(s) com os filtros atuais.")
    with st.expander("Clique para ver as combinações encontradas"):
        st.dataframe(df_filtered)
else:
    st.warning("Nenhuma combinação encontrada com os filtros atuais.")

st.write("")
gerar_button = st.button("Gerar Análise", type="primary", use_container_width=True)
st.divider()

# --- 3. LÓGICA PRINCIPAL E EXIBIÇÃO DE RESULTADOS ---
if gerar_button:
    if not df_filtered.empty:
        if len(df_filtered) > 1:
            st.info(f"Análise iniciada usando a primeira das {len(df_filtered)} combinações encontradas.")
        
        linha_selecionada = df_filtered.iloc[0]
        media, desvio_padrao = rodar_fitting(f"Battery_Archive_Data_NoSubDirs/{linha_selecionada['Full Filename']}")
        
        n_series, n_paralel, total_cels = calcular_arquitetura(
            v_bat=bat_voltage,
            v_cel=cel_voltage,
            C_bat=bat_cap,
            C_cel=linha_selecionada['Capacity (Ah)']
        )
        resultado_cpp_csv = executar_modelo_cpp(
            num_s=n_series,
            num_p=n_paralel,
            pmin=0,
            sohm=70,
            architecture='sp',
            output_dir=""
        )

        mtta_df = pd.read_csv(resultado_cpp_csv).sort_values(by='MTTA').reset_index(drop=True)
        n       = len(mtta_df)
        mtta_df['prob_acumulada'] = np.arange(0, n) / (n - 1) if n > 1 else 1.0
        
        if resultado_cpp_csv and os.path.exists(resultado_cpp_csv):
            st.header("Resultados da Análise:")
            res_col1, res_col2 = st.columns([1, 2])
            
            with res_col1:
                with st.container(border=True):
                    # 1. Arquitetura da Bateria
                    st.subheader("Arquitetura da Bateria")
                    st.write(f"Células em Série (ns): **{n_series}**")
                    st.write(f"Células em Paralelo (np): **{n_paralel}**")
                    st.write(f"Total de Células: **{total_cels}**")
                    st.success(f"Configuração Final: {n_series}S{n_paralel}P")
                                        # 2. Célula Base Utilizada na Simulação
                    st.subheader("Célula Base Selecionada")
                    # Assumindo que 'linha_selecionada' e 'cel_voltage' estão disponíveis
                    st.write(f"Cátodo: **{linha_selecionada['Cathode']}**")
                    st.write(f"Formato: **{linha_selecionada['Form Factor']}**")
                    st.write(f"Capacidade: **{linha_selecionada['Capacity (Ah)']:.2f} Ah**")
                    st.write(f"Tensão da Célula: **{cel_voltage:.2f} V**")

            with res_col2:  
                with st.container(border=True, height=500):        
                    st.subheader("Gráfico de Probabilidade Acumulada (do Modelo C++)")
                    st.line_chart(mtta_df, x='MTTA', y='prob_acumulada', height=430)
                
            with st.expander("Ver dados de MTTA gerados pelo modelo C++"):
                st.dataframe(mtta_df)
    else:
        st.error("**Nenhuma combinação encontrada.**")