import os

def print_headers(base_dir):
    with open('Headers-analysis/headers.txt', 'w', encoding='utf-8') as out:
        # Iterate over each subdirectory in the base directory
        for folder_name in os.listdir(base_dir):
            folder_path = os.path.join(base_dir, folder_name)
            if os.path.isdir(folder_path):
                out.write(f"\n=== Folder: {folder_name} ===\n")
                print(f"\n=== Folder: {folder_name} ===")

                # Find all CSV files containing 'timeseries' in the name
                timeseries_files = [f for f in os.listdir(folder_path) if 'timeseries' in f and f.endswith('.csv')]
                # Find all CSV files containing 'cycle_data' in the name
                cycle_data_files = [f for f in os.listdir(folder_path) if 'cycle_data' in f and f.endswith('.csv')]

                if timeseries_files:
                    out.write("-- Timeseries files and headers --\n")
                    print("-- Timeseries files and headers --")
                    for filename in timeseries_files:
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            header = f.readline().strip()
                        out.write(f"{filename}:\n{header}\n\n")
                        print(f"{filename}: {header}")
                else:
                    out.write("No timeseries files found.\n")
                    print("No timeseries files found.")

                if cycle_data_files:
                    out.write("-- Cycle_data files and headers --\n")
                    print("-- Cycle_data files and headers --")
                    for filename in cycle_data_files:
                        file_path = os.path.join(folder_path, filename)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            header = f.readline().strip()
                        out.write(f"{filename}:\n{header}\n\n")
                        print(f"{filename}: {header}")
                else:
                    out.write("No cycle_data files found.\n")
                    print("No cycle_data files found.")

if __name__ == '__main__':
    # Replace this with the path to your Battery_Archive_Data folder
    base_directory = 'Battery_Archive_Data'
    print_headers(base_directory)