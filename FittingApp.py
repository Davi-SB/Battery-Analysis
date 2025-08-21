import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm, kstest
import matplotlib.pyplot as plt
import seaborn as sns
import os

def select_file():
    st.sidebar.header("Seleção de Arquivo")
    base_path = 'Battery_Archive_Data'
    
    try:
        folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        selected_folder = st.sidebar.selectbox("Escolha uma pasta:", folders)

        if selected_folder:
            folder_path = os.path.join(base_path, selected_folder)
            files = [f for f in os.listdir(folder_path) if f.endswith('timeseries.csv') or f.endswith('timeseries_data.csv')]
            
            if not files:
                st.sidebar.warning("Nenhum arquivo 'timeseries.csv' encontrado nesta pasta.")
                return None
                
            selected_file = st.sidebar.selectbox("Escolha um arquivo .csv:", files)
            
            if selected_file:
                return os.path.join(folder_path, selected_file)
    except FileNotFoundError:
        st.error(f"O diretório '{base_path}' não foi encontrado. Certifique-se de que ele existe no mesmo local que o seu script.")
        return None

    return None

def process_data(file_path):
    try:
        df = pd.read_csv(file_path)
        
        # Filtros e preparação inicial
        required_cols = ["Cycle_Index", "Test_Time (s)", "Current (A)", "Voltage (V)", "Discharge_Capacity (Ah)", "Cell_Temperature (C)"]
        df = df[required_cols]
        df_discharge = df[df['Current (A)'] < 0].copy()
        #df_discharge = df_discharge[df_discharge['Cell_Temperature (C)'] >= 1]

        # Cálculo do SOH
        nominal_capacity = df_discharge['Discharge_Capacity (Ah)'].max()
        if nominal_capacity == 0: return df_discharge, None

        cycles_capacity = df_discharge.groupby('Cycle_Index')['Discharge_Capacity (Ah)'].max().reset_index()
        cycles_capacity.columns = ['Cycle_Index', 'Max_Discharge_Capacity']
        cycles_capacity['SOH_discharge'] = cycles_capacity['Max_Discharge_Capacity'] / nominal_capacity

        # Interpolação e cálculo do NCD1%
        thresholds = np.arange(1.00, 0.00, -0.01)
        soh = cycles_capacity['SOH_discharge'].values
        cycles = cycles_capacity['Cycle_Index'].values
        
        xp = soh[::-1]
        fp = cycles[::-1]
        
        valid = (thresholds >= xp.min()) & (thresholds <= xp.max())
        thresholds = thresholds[valid]
        
        estimated_cycles = np.interp(thresholds, xp, fp)
        
        df_estimates = pd.DataFrame({'SOH_threshold': thresholds, 'estimated_cycle': estimated_cycles})
        df_estimates['NCD1%'] = df_estimates['estimated_cycle'].diff()
        
        ncd1_data = df_estimates['NCD1%'].dropna().values
        
        return df_discharge, ncd1_data

    except Exception as e:
        st.error(f"Ocorreu um erro ao processar o arquivo: {e}")
        return None, None

def plot_overview(df):
    fig, axs = plt.subplots(2, 2, figsize=(14, 8))
    axs = axs.flatten()

    features = ["Current (A)", "Voltage (V)", "Discharge_Capacity (Ah)", "Cell_Temperature (C)"]
    cycles = df["Cycle_Index"].unique()
    cycles.sort()
    
    num_cycles_to_plot = 5
    if len(cycles) > num_cycles_to_plot:
        plot_cycles = cycles[::len(cycles) // num_cycles_to_plot]
    else:
        plot_cycles = cycles

    for i, feature in enumerate(features):
        ax = axs[i]
        for cycle in plot_cycles:
            df_cycle = df[df["Cycle_Index"] == cycle].copy()
            df_cycle['Tempo_Relativo (s)'] = df_cycle["Test_Time (s)"] - df_cycle["Test_Time (s)"].min()
            ax.plot(df_cycle['Tempo_Relativo (s)'], df_cycle[feature], alpha=0.7, label=f'Ciclo {int(cycle)}', linewidth=2.0)
        
        ax.set_title(f'{feature} ao longo dos ciclos')
        ax.set_xlabel('Tempo Relativo (s)')
        ax.set_ylabel(feature)
        ax.grid(True)
        ax.legend(loc='best')

    plt.tight_layout()
    return fig

def plot_ncd_boxplot(data):
    fig, ax = plt.subplots(figsize=(12, 2))
    
    sns.boxplot(x=data, ax=ax, orient='h', linewidth=1, zorder=2, color='C0')
    
    for patch in ax.patches:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, 0.3))

    sns.scatterplot(x=data, y=np.zeros_like(data), ax=ax, s=60, color='C0', alpha=0.7, zorder=1)
    
    ax.set_yticks([])
    ax.set_xlabel("NCD1%")
    ax.tick_params(which='major', labelsize=12)
    ax.set_title("Distribuição de NCD1%", fontsize=18)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    
    return fig

def create_cdf_plot(data):
    fig, ax = plt.subplots(figsize=(9, 4))
    
    data_sorted = np.sort(data)
    n = len(data_sorted)
    
    mean, std = norm.fit(data_sorted)
    teo_norm = norm.cdf(data_sorted, loc=mean, scale=std)
    
    cdf_emp = np.arange(1, n + 1) / n
    ax.plot(data_sorted, cdf_emp, marker='o', linestyle='-', label="CDF NCD1%", zorder=3, alpha=0.7)
    
    ax.plot(data_sorted, teo_norm, linestyle='--', label=f"CDF Normal fit\n(μ={mean:.2f}, σ={std:.2f})")
    
    ax.set_xlabel("NCD1%")
    ax.set_ylabel("Probabilidade Acumulada")
    ax.set_title("NCD1% e Curva Normal Aproximada")
    ax.legend()
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    
    return fig

def perform_ks_test(data):
    mean, std = norm.fit(data)
    statistic, p_value = kstest(rvs=np.sort(data), cdf='norm', args=(mean, std))
    
    alpha = 0.05
    hypothesis_result = "Hipótese aceita." if p_value >= alpha else "Hipótese rejeitada."
    
    return f"""
    ### Resultados do Teste de Kolmogorov-Smirnov (KS)
    - **Estatística KS:** `{statistic:.4f}`
    - **p-value:** `{p_value:.4f}`
    - **alpha:** `{alpha}`
    - **Conclusão:** `{hypothesis_result}` (Como p-value > alpha, não há evidências para rejeitar a hipótese de que os dados seguem uma distribuição normal).
    """

def main():
    st.set_page_config(layout="wide")
    st.title("Análise de Bateria: Degradação e Teste de Normalidade")

    file_path = select_file()

    if file_path:
        st.write(f"**Arquivo Selecionado:** `{file_path}`")
        
        df_overview, ncd1_data = process_data(file_path)
        
        if df_overview is not None and not df_overview.empty:
            st.header("Visão Geral do Dataset (Ciclos de Descarga)")
            overview_plot = plot_overview(df_overview)
            st.pyplot(overview_plot)
        else:
            st.warning("Não foi possível gerar a visão geral do dataset.")

        if ncd1_data is not None and len(ncd1_data) > 1:
            st.header("Análise da Degradação (NCD1%)")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Distribuição de NCD1%")
                boxplot = plot_ncd_boxplot(ncd1_data)
                st.pyplot(boxplot)

            with col2:
                st.subheader("Gráfico de Distribuição Cumulativa (CDF)")
                cdf_plot = create_cdf_plot(ncd1_data)
                st.pyplot(cdf_plot)
            
            st.subheader("Teste de Normalidade")
            ks_results = perform_ks_test(ncd1_data)
            st.markdown(ks_results)
        else:
            st.warning("Não há dados de degradação suficientes no arquivo para realizar a análise completa.")

if __name__ == "__main__":
    main()