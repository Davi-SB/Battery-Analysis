from scipy.stats import norm
from tqdm import tqdm
import pandas as pd
import numpy as np
import os

# Metadata-analysis/
PATH_DESCRIPTION_FILE = 'Metadata-analysis/HeadersOutput/headers_description.txt'
PATH_LIST_FILE = 'Metadata-analysis/HeadersOutput/z - filenames.txt'
PATH_CSV_FILE = 'Metadata-analysis/HeadersOutput/filenames.csv'
BASE_DIR = 'Battery_Archive_Data'

def get_subfolders(base_dir):
    return [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

def find_csv_files(folder_path, keyword):
    return [f for f in os.listdir(folder_path) if keyword in f and f.endswith('.csv')]

def get_header(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readline().strip()

def write_description(out_file, folder_name, section_title, files, base_dir):
    out_file.write(f"-- {section_title} --\n")
    # print(f"-- {section_title} --")
    for filename in files:
        file_path = os.path.join(base_dir, folder_name, filename)
        header = get_header(file_path)
        out_file.write(f"{filename}:\n{header}\n\n")
        # print(f"{filename}: {header}")

def record_filename(name_list_file, filename):
    with open(name_list_file, 'a', encoding='utf-8') as f:
        f.write(f"{filename}\n")

def process_folder(folder_name, base_dir, description_file, name_list_file):
    folder_path = os.path.join(base_dir, folder_name)
    description_file.write(f"\n=== Folder: {folder_name} ===\n")
    # print(f"\n=== Folder: {folder_name} ===")

    # Timeseries
    ts_files = find_csv_files(folder_path, 'timeseries')
    if ts_files:
        # Registra nomes
        for fn in ts_files:
            record_filename(name_list_file, fn)
        write_description(description_file, folder_name, 'Timeseries files and headers', ts_files, base_dir)
    else:
        description_file.write("No timeseries files found.\n")
        # print("No timeseries files found.")

    # Cycle data
    cd_files = find_csv_files(folder_path, 'cycle_data')
    if cd_files:
        write_description(description_file, folder_name, 'Cycle_data files and headers', cd_files, base_dir)
    else:
        description_file.write("No cycle_data files found.\n")
        # print("No cycle_data files found.")

def parse_filename_components(filename):
    # Remove extensão .csv e splita por '_'
    name = os.path.splitext(filename)[0]
    return name.split('_')

# formata components e elimina exceções
def pre_process(components: list):
    # Observaçoes:
    # - HNEI não tem cell id e tem dois form factors
    # - Michigan pode não ter o 8° componente
    # - SNL não tem cell id
    
    if components[1] == 'HNEI':
        # Adiciona o cell id
        components.insert(2, '-')
        # Junta components 4 e 5
        components[4] = components[4] + '-' + components[5]
        components.pop(5)
    elif components[1] == 'MICH':
        # Adiciona o oitavo componente
        if components[8] == 'timeseries':
            components.insert(8, '-')
    elif components[1] == 'SNL':
        # Adiciona o cell id
        components.insert(2, '-')
    return components
        
# formata components e adiciona ao dicionário
def process_filename(data_dict: dict, components: list, filename: str):
    components = pre_process(components)
    
    institution_dict = {
        'CALCE'  : 'Calce',
        'HNEI'   : 'HNEI',
        'MICH'   : 'Michigan Expansion',
        'OX'     : 'Oxford',
        'SNL'    : 'SNL',
        'UL-PUR' : 'UL-PUR',
    }
    
    formFactor_dict = {
        'pouch'  : 'Pouch',
        'prism': 'Prismatic',
        '18650'  : '18650',
        '21700'  : '21700',
        '26650'  : '26650',
        '32650'  : '32650',
        '46800'  : '46800',
    }
    
    # Capacidade
    # components[0] = components[0]
    data_dict['Capacity (Ah)'].append(components[0])
    
    # Instituição
    components[1] = institution_dict[components[1]] if components[1] in institution_dict else components[1]
    data_dict['Institution'].append(components[1])

    # Cell ID
    # components[2] = components[2]
    data_dict['Cell ID'].append(components[2])

    # Form Factor
    components[3] = formFactor_dict[components[3]] if components[3] in formFactor_dict else components[3]
    data_dict['Form Factor'].append(components[3])

    # Cathode
    # components[4] = components[4]
    data_dict['Cathode'].append(components[4])
    
    # Temperature
    components[5] = components[5].replace('C', '')
    data_dict['Temperature (°C)'].append(components[5])
    
    # Min-Max SOC
    min, max = components[6].split('-')
    components[6] = max
    components.insert(6, min)
    data_dict['Min SOC (%)'].append(components[6])
    data_dict['Max SOC (%)'].append(components[7])
    
    # Charge-Discharge Rate
    charge, discharge = components[8].split('-')
    components[8] = discharge.replace('C', '')
    components.insert(8, charge)
    data_dict['Charge Rate (C)'].append(components[8])
    data_dict['Discharge Rate (C)'].append(components[9])
    
    # Group
    # components[10] = components[10]
    data_dict['Group'].append(components[10])

    # Full Filename
    data_dict['Full Filename'].append(filename)

    return data_dict

def build_dataframe_from_names(name_list_file):
    # Cria e define o nome das colunas do DataFrame
    data_dict = {
        'Capacity (Ah)'   : [],
        'Institution'       : [],
        'Cell ID'           : [],
        'Form Factor'       : [],
        'Cathode'           : [],
        'Temperature (°C)'  : [],
        'Min SOC (%)'       : [],
        'Max SOC (%)'       : [],
        'Charge Rate (C)'   : [],
        'Discharge Rate (C)': [],
        'Group'             : [],
        'Full Filename'     : []
    }

    with open(name_list_file, 'r', encoding='utf-8') as f:
        for line in f:
            filename = line.strip()
            if not filename: continue
            components = parse_filename_components(filename)
            data_dict = process_filename(data_dict, components, filename)

    df = pd.DataFrame(data_dict)
    df = df.replace('', 'WARNING')
    return df

def calculate_currents(df):
    df['Charge Current (A)'] = df['Capacity (Ah)'].astype(float) * df['Charge Rate (C)'].astype(float)
    df['Discharge Current (A)'] = df['Capacity (Ah)'].astype(float) * df['Discharge Rate (C)'].astype(float)
    
    # Arredonda para duas casas decimais para que os grupos possam ser formados sem considerar diferenças insignificantes como 4.999 != 4.99
    df['Charge Current (A)'] = df['Charge Current (A)'].round(2)
    df['Discharge Current (A)'] = df['Discharge Current (A)'].round(2)
    
    return df

def run_fitting(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo)
    except FileNotFoundError:
        print(f"Arquivo de dados não encontrado em: {caminho_arquivo}")
        return None, None

    if df.empty:
        print(f"Arquivo {caminho_arquivo} está vazio.")
        input("Pressione Enter para continuar...")
        return None, None
    # Capacidade nominal (máxima global)
    # ---> usar capacidade informada no archive e não a do dataset
    # nominal_capacity = df['Discharge_Capacity (Ah)'].max()
    nominal_capacity = float(caminho_arquivo.split('\\')[-1].split('_')[0])
    
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
        print("Não há dados de NCD1% suficientes para realizar o fitting.")
        return None, None

    # Faz o fitting para encontrar os parâmetros da distribuição normal
    # TODO: para cada instituição, fazer um plot do fit para cada instituição, pra ver se a distribuição se encaixa
    mean, std = norm.fit(data)

    print(f"Fitting concluído: μ={mean:.2f}, σ={std:.2f}")
    
    return mean, std

def calculate_mean_std(df):
    # para cada linha de df, pega o nome do arquivo daquela linha
    for index, row in df.iterrows():
        filename = row['Full Filename']
        print(f"Processando arquivo: {filename}")
        # chama run_fitting passando o caminho do arquivo
        mean, std = run_fitting(os.path.join('Battery_Archive_Data_NoSubDirs', filename))
        # adiciona os resultados ao df
        if mean is None or std is None:
            print(f"Erro ao processar o arquivo {filename}. Definindo valores como NaN.")
            mean, std = np.nan, np.nan
        
        df.at[index, 'Mean NCD1%'] = mean
        df.at[index, 'Std NCD1%'] = std
        
    return df

if __name__ == '__main__':
        
    # Limpa/Cria arquivos de saída
    open(PATH_DESCRIPTION_FILE, 'w', encoding='utf-8').close()
    open(PATH_LIST_FILE, 'w', encoding='utf-8').close()
    print(f"Arquivos {PATH_DESCRIPTION_FILE} e {PATH_LIST_FILE} limpos ou criados")

    with open(PATH_DESCRIPTION_FILE, 'w', encoding='utf-8') as desc:
        subfolders = get_subfolders(BASE_DIR)
        for folder in tqdm(subfolders):
            process_folder(folder, BASE_DIR, desc, PATH_LIST_FILE)
    print(f"Arquivos {PATH_DESCRIPTION_FILE} e {PATH_LIST_FILE} atualizados")
            
    df = build_dataframe_from_names(PATH_LIST_FILE)
    
    # Adiciona colunas calculadas de corrente
    df = calculate_currents(df)
    
    # Adiciona colunas mean e std de NCD1%
    df = calculate_mean_std(df)
    
    # Organiza a ordem das colunas
    collumn_order = [
        'Institution',
        'Cell ID',
        'Form Factor',
        'Cathode',
        'Temperature (°C)',
        'Min SOC (%)',
        'Max SOC (%)',
        'Charge Rate (C)',
        'Discharge Rate (C)',
        'Group',
        'Capacity (Ah)',
        'Charge Current (A)',
        'Discharge Current (A)',
        'Mean NCD1%',
        'Std NCD1%',
        'Full Filename',
    ]
    df = df[collumn_order]
    df.to_csv(PATH_CSV_FILE, index=False, encoding='utf-8')
    
    print(f"Arquivo {PATH_CSV_FILE} atualizado")
    print("Análise concluida com sucesso")