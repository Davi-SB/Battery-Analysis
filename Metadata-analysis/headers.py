import pandas as pd
import os

# Metadata-analysis/
PATH_DESCRIPTION_FILE = 'headers_description.txt'
PATH_LIST_FILE = 'z - filenames.txt'
PATH_CSV_FILE = 'filenames.csv'
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
    
    if components[0] == 'HNEI':
        # Adiciona o cell id
        components.insert(1, '-')
        # Junta components 3 e 4
        components[3] = components[3] + '-' + components[4]
        components.pop(4)
    elif components[0] == 'MICH':
        # Adiciona o oitavo componente
        if components[7] == 'timeseries':
            components.insert(7, '-')
    elif components[0] == 'SNL':
        # Adiciona o cell id
        components.insert(1, '-')
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
    
    # Instituição
    components[0] = institution_dict[components[0]] if components[0] in institution_dict else components[0]
    data_dict['Institution'].append(components[0])

    # Cell ID
    # components[1] = components[1]
    data_dict['Cell ID'].append(components[1])

    # Form Factor
    components[2] = formFactor_dict[components[2]] if components[2] in formFactor_dict else components[2]
    data_dict['Form Factor'].append(components[2])

    # Cathode
    # components[3] = components[3]  
    data_dict['Cathode'].append(components[3])
    
    # Temperature
    components[4] = components[4].replace('C', '')
    data_dict['Temperature (°C)'].append(components[4])
    
    # Min-Max SOC
    min, max = components[5].split('-')
    components[5] = max
    components.insert(5, min)
    data_dict['Min SOC (%)'].append(components[5])
    data_dict['Max SOC (%)'].append(components[6])
    
    # Charge-Discharge Rate
    charge, discharge = components[7].split('-')
    components[7] = discharge.replace('C', '')
    components.insert(7, charge)
    data_dict['Charge Rate (C)'].append(components[7])
    data_dict['Discharge Rate (C)'].append(components[8])
    
    # Group
    # components[9] = components[9]
    data_dict['Group'].append(components[9])

    # Full Filename
    data_dict['Full Filename'].append(filename)

    return data_dict

def build_dataframe_from_names(name_list_file):
    # Cria e define o nome das colunas do DataFrame
    data_dict = {
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

if __name__ == '__main__':
    # Garante que a pasta de saída existe
    if not os.path.exists('Headers-analysis'):
        os.makedirs('Headers-analysis')
        
    # Limpa/Cria arquivos de saída
    open(PATH_DESCRIPTION_FILE, 'w', encoding='utf-8').close()
    open(PATH_LIST_FILE, 'w', encoding='utf-8').close()
    print(f"Arquivos {PATH_DESCRIPTION_FILE} e {PATH_LIST_FILE} limpos ou criados")

    with open(PATH_DESCRIPTION_FILE, 'w', encoding='utf-8') as desc:
        subfolders = get_subfolders(BASE_DIR)
        for folder in subfolders:
            process_folder(folder, BASE_DIR, desc, PATH_LIST_FILE)
    print(f"Arquivos {PATH_DESCRIPTION_FILE} e {PATH_LIST_FILE} atualizados")
            
    df = build_dataframe_from_names(PATH_LIST_FILE)
    df.to_csv(PATH_CSV_FILE, index=False, encoding='utf-8')
    print(f"Arquivo {PATH_CSV_FILE} atualizado")
    print("Análise concluida com sucesso")