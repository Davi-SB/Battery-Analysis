#### Esse código renomeia os arquivos de Battery_Archive para que eles incuam a capacidade da bateria no nome do arquivo
# Isso é feito manualmente consultando https://batteryarchive.org/cycle_list.html?time=0001 e procurando repetições
# Os nomes dos arquivos contém os dados do experimento separados por "_"
# Para simplificar e evitar casos especiais, a nova convenção de nomenclatura terá como primeiro elemento a capacidade da bateria
# O estudo do Battery Archive e a documentação da consulta manual está disponível em: https://www.notion.so/Renomea-o-com-capacidades-20884748cd91800b8189c850e3cda6a4

# A Battery Archive original foi renomeada para Original_Battery_Archive_Data, e a nova com as alterações será Battery_Archive_Data

import os
import shutil

ORIGINAL_PATH = "Original_Battery_Archive_Data"
NEW_PATH = "Battery_Archive_Data"

# Subfolders tanto de ORIGINAL_PATH como de NEW_PATH : Os prefixos de capacidade serão adicionados aos arquivos dentro dessas subpastas
subfolder_prefixes = {
    "CALCE": "1.35_",
    "HNEI": "2.80_",
    "Michigan Expansion": "5.00_",
    "Michigan Formation": "2.36_",
    "Oxford": "0.74_",
    "SNL LFP": "1.10_",
    "SNL NCA": "3.20_",
    "SNL NMC": "3.00_",
    "UL-Purdue": "3.40_"
}

# Deleta se já existir e cria a pasta de destino
if os.path.exists(NEW_PATH):
    print(f"Atenção: A pasta '{NEW_PATH}' já existe. Deseja deletá-la e criar uma nova? (s/n)")
    resposta = input().strip().lower()
    if resposta != 's':
        print("Operação cancelada. A pasta não foi modificada.")
        exit
    print(f"Deletando a pasta '{NEW_PATH}'...")
    shutil.rmtree(NEW_PATH)
    print(f"A pasta '{NEW_PATH}' foi deletada. Criando nova pasta...")
os.makedirs(NEW_PATH)
print(f"Pasta '{NEW_PATH}' criada.")

# Itera sobre as subpastas e seus prefixos definidos
for subfolder_name, prefix in subfolder_prefixes.items():
    original_subfolder_path = os.path.join(ORIGINAL_PATH, subfolder_name)
    new_subfolder_path      = os.path.join(NEW_PATH, subfolder_name)

    print(f"\nProcessando subpasta: '{original_subfolder_path}'")
    
    # Verifica se a subpasta original existe
    if not os.path.exists(original_subfolder_path):
        print(f"Atenção: Subpasta original '{original_subfolder_path}' não encontrada. Pressione enter para ir para a próxima.")
        input()
        continue

    # Cria a subpasta de destino
    os.makedirs(new_subfolder_path)
    print(f"    Subpasta '{new_subfolder_path}' criada.")

    # Lista todos os arquivos na subpasta original
    try:
        # Lista os arquivos na subpasta original (garantindo que se trata de arquivos)
        files_in_original_subfolder = [f for f in os.listdir(original_subfolder_path) 
                                       if os.path.isfile(os.path.join(original_subfolder_path, f))]
    except Exception as e:
        print(f"Erro ao listar arquivos em '{original_subfolder_path}': {e}. Pressione enter para ir para a próxima.")
        input()
        continue

    print(f"    Encontrados {len(files_in_original_subfolder)} arquivos.")

    # Itera sobre cada arquivo na subpasta original
    for filename in files_in_original_subfolder:
        original_file_path = os.path.join(original_subfolder_path, filename)
        
        # Cria o novo nome do arquivo com o prefixo
        new_filename = prefix + filename
        new_file_path = os.path.join(new_subfolder_path, new_filename)

        try:
            # Copia o arquivo para o novo local com o novo nome
            # shutil.copy2 tenta preservar o máximo de metadados do arquivo original possível
            shutil.copy2(original_file_path, new_file_path)
            print(f"    Copiado: '{filename}' para '{new_filename}' em '{new_subfolder_path}'")
        except Exception as e:
            print(f"------- Erro ao copiar '{original_file_path}' para '{new_file_path}': {e}. Pressione enter para continuar")
            input()

print(f"\n ---------------- Processamento concluído")