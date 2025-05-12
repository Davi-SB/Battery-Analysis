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