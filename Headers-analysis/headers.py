import pandas as pd
import numpy as np
import os

DESCRIPTION_FILE = 'Headers-analysis/headers_description.txt'
NAME_LIST_FILE = 'Headers-analysis/headers.txt'
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
    print(f"-- {section_title} --")
    for filename in files:
        file_path = os.path.join(base_dir, folder_name, filename)
        header = get_header(file_path)
        out_file.write(f"{filename}:\n{header}\n\n")
        print(f"{filename}: {header}")

def record_filename(name_list_file, filename):
    with open(name_list_file, 'a', encoding='utf-8') as f:
        f.write(f"{filename}\n")

def process_folder(folder_name, base_dir, description_file, name_list_file):
    folder_path = os.path.join(base_dir, folder_name)
    description_file.write(f"\n=== Folder: {folder_name} ===\n")
    print(f"\n=== Folder: {folder_name} ===")

    # Timeseries
    ts_files = find_csv_files(folder_path, 'timeseries')
    if ts_files:
        # Registra nomes
        for fn in ts_files:
            record_filename(name_list_file, fn)
        write_description(description_file, folder_name, 'Timeseries files and headers', ts_files, base_dir)
    else:
        description_file.write("No timeseries files found.\n")
        print("No timeseries files found.")

    # Cycle data
    cd_files = find_csv_files(folder_path, 'cycle_data')
    if cd_files:
        write_description(description_file, folder_name, 'Cycle_data files and headers', cd_files, base_dir)
    else:
        description_file.write("No cycle_data files found.\n")
        print("No cycle_data files found.")

def parse_filename_components(filename):
    # Remove extensão .csv antes de splitar
    name = os.path.splitext(filename)[0]
    return name.split('_')

def process_filename(dict: dict, components: list):
    # Processa os componentes do nome do arquivo
    # Observaçoes:
    # - HNEI não tem cell id e tem dois form factors
    # - Michigan pode não ter o 8° componente
    # - SNL não tem cell id
    
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
    
    components[0] = institution_dict[components[0]] if components[0] in institution_dict else components[0]
    # components[1] = components[1]
    components[2] = formFactor_dict[components[2]] if components[2] in formFactor_dict else components[2]    
    
    # Alguns nomes de arquivos vem com form factor e cathode trocados
    if components[3] in ['Pouch', 'pouch', '']:
        
    
def build_dataframe_from_names(name_list_file):    
    # Cria e define o nome das colunas do DataFrame
    data_dict = {
        'Institution'       : [],
        'Cell ID'           : [],
        'Group?'            : [],
        'Form Factor'       : [],
        'Cathode'           : [],
        'Temperature (°C)'  : [],
        'Min SOC (%)'       : [],
        'Max SOC (%)'       : [],
        'Charge Rate (C)'   : [],
        'Discharge Rate (C)': []
    }
    
    data = []
    with open(name_list_file, 'r', encoding='utf-8') as f:
        for line in f:
            filename = line.strip()
            if not filename: continue
            components = parse_filename_components(filename)
            data_dict = process_filename(data_dict, components)

    df = pd.DataFrame(data_dict)
    df = df.replace('', np.nan)  # Substitui strings vazias por NaN
    return df

if __name__ == '__main__':
    # Garante que a pasta de saída existe
    if not os.path.exists('Headers-analysis'):
        os.makedirs('Headers-analysis')
        
    # Limpa/Cria arquivos de saída
    open(DESCRIPTION_FILE, 'w', encoding='utf-8').close()
    open(NAME_LIST_FILE, 'w', encoding='utf-8').close()

    with open(DESCRIPTION_FILE, 'w', encoding='utf-8') as desc:
        subfolders = get_subfolders(BASE_DIR)
        for folder in subfolders:
            process_folder(folder, BASE_DIR, desc, NAME_LIST_FILE)
            
    df = build_dataframe_from_names(NAME_LIST_FILE)
    #df.to_csv('Headers-analysis/headers.csv', index=False, encoding='utf-8')