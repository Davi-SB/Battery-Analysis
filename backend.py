from scipy.stats import norm
import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import math

def rodar_fitting(caminho_arquivo):
    st.info(f"Iniciando o fitting para o arquivo: {caminho_arquivo}...")
    
    try:
        df = pd.read_csv(caminho_arquivo)
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado em: {caminho_arquivo}")
        return None, None

    # Capacidade nominal (máxima global)
    nominal_capacity = df['Discharge_Capacity (Ah)'].max()

    # Para cada ciclo, extrai a maior capacidade
    cycles_capacity = df.groupby('Cycle_Index')['Discharge_Capacity (Ah)'].max().reset_index()
    cycles_capacity.columns = ['Cycle_Index', 'Max_Discharge_Capacity']
    cycles_capacity['SOH_discharge'] = (cycles_capacity['Max_Discharge_Capacity'] / nominal_capacity)

    # Seleciona as features de interesse e agrupa por ciclo
    df_grouped = df[['Cycle_Index', 'Cell_Temperature (C)']].groupby('Cycle_Index', as_index=False).mean()

    # Adição do SOH calculado
    df_grouped['SOH_discharge'] = cycles_capacity['SOH_discharge']

    # Define thresholds de SOH de 100% a 1%
    thresholds = np.arange(1.00, 0.00, -0.01)

    soh = df_grouped['SOH_discharge'].values
    cycles = df_grouped['Cycle_Index'].values

    # Inverte para que o SOH fique crescente para a interpolação
    xp = soh[::-1]
    fp = cycles[::-1]
    
    # Filtra thresholds para o intervalo de SOH real dos dados
    valid_thresholds = thresholds[(thresholds >= xp.min()) & (thresholds <= xp.max())]

    # np.interp estima os ciclos para cada threshold de SOH
    estimated_cycles = np.interp(valid_thresholds, xp, fp)

    df_estimates = pd.DataFrame({
        'SOH_threshold': valid_thresholds,
        'estimated_cycle': estimated_cycles
    })
    df_estimates['SOH_threshold'] = df_estimates['SOH_threshold'].astype(float).round(2)

    # Calcula o NCD1% (Number of Cycles Drop para cada 1% de SOH)
    df_estimates['NCD1%'] = df_estimates['estimated_cycle'].diff()

    # Prepara os dados de NCD1% para o fitting
    data = df_estimates["NCD1%"].dropna().values
    
    if len(data) < 2:
        st.warning("Não há dados de NCD1% suficientes para realizar o fitting.")
        return None, None

    # Faz o fitting para encontrar os parâmetros da distribuição normal
    mean, std = norm.fit(data)

    st.success(f"Fitting concluído: μ={mean:.2f}, σ={std:.2f}")
    
    return mean, std

# falta implementar
def calcular_arquitetura(v_bat, C_bat, v_cel, C_cel):
    st.info("Calculando a arquitetura da célula...")

    n_series   = math.ceil(v_bat / v_cel)
    n_parallel = math.ceil(C_bat / C_cel)
    total      = n_series * n_parallel
    
    return (n_series, n_parallel, total)

# falta implementar
def executar_modelo_cpp(num_p=4, num_s=2, pmin=0, sohm=70, architecture='sp', output_dir=''):
    # num_p é o número de células em paralelo
    # num_s é o número de células em série
    # pmin é o número de células em paralelo que o sistema suporta no mínimo
    # sohm é o valor mínimo de soh pra declarar a falha da célula
    # architecture é a arquitetura da bateria (sp ou ps)
    
    output_csv_path = "mtta_results.csv"
    comando = [
        "mtta_simulation.exe", "--np", str(num_p), "--ns", str(num_s), "--pmin", str(pmin),
        "--sohm", str(sohm), "--architecture", str(architecture), "--output-dir", str(output_dir)
    ]
    st.info(f"Executando o comando: `{' '.join(comando)}`")
    log_placeholder = st.empty()
    log_placeholder.code("Iniciando a simulação...")
    log_estatico, linha_progresso_recente = [], ""
    try:
        processo = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', bufsize=1)
        for linha in iter(processo.stdout.readline, ''):
            linha_limpa = linha.replace('\r', '')
            if linha_limpa.strip().startswith('[') and '%' in linha_limpa:
                linha_progresso_recente = linha_limpa
            else:
                log_estatico.append(linha_limpa)
            output_para_exibir = "".join(log_estatico) + linha_progresso_recente
            log_placeholder.code(output_para_exibir)
        processo.wait()
        stderr_output = processo.stderr.read()
        log_placeholder.empty()
        if processo.returncode == 0:
            st.success("Modelo C++ ('mtta_simulation.exe') executado com sucesso!")
            return output_csv_path
        else:
            st.error("Ocorreu um erro ao executar o modelo C++.")
            st.code(f"Código de Erro: {processo.returncode}\n{stderr_output}")
            return output_csv_path # retorna mesmo assim pra caso retorno != 0 não seja um erro fatal
    except FileNotFoundError:
        log_placeholder.empty()
        st.warning("⚠️ **Executável não encontrado!** Usando dados simulados.")
        pd.DataFrame({'index': range(10), 'MTTA': sorted(np.random.normal(loc=1200, scale=80, size=10))}).to_csv(output_csv_path, index=False)
        return output_csv_path
    except Exception as e:
        log_placeholder.empty()
        st.error(f"Uma exceção inesperada ocorreu: {e}")
        return None
