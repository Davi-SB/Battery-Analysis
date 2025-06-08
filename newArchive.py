import os
import shutil

def copiar_arquivos_de_subdiretorios(diretorio_raiz, subdiretorios, diretorio_destino):
    """
    Copia todos os arquivos de uma lista de subdiretórios para um diretório de destino.

    Argumentos:
        diretorio_raiz (str): O caminho para o diretório que contém os subdiretórios.
        subdiretorios (list): Uma lista com os nomes dos subdiretórios dos quais os arquivos serão copiados.
        diretorio_destino (str): O caminho para a pasta onde todos os arquivos serão colados.
    """
    # Cria o diretório de destino se ele não existir
    if not os.path.exists(diretorio_destino):
        os.makedirs(diretorio_destino)
        print(f"Diretório de destino criado em: {diretorio_destino}")

    # Itera sobre a lista de subdiretórios especificada
    for subdiretorio in subdiretorios:
        # Monta o caminho completo para o subdiretório de origem
        caminho_subdiretorio = os.path.join(diretorio_raiz, subdiretorio)

        # Verifica se o caminho de origem é realmente um diretório
        if os.path.isdir(caminho_subdiretorio):
            print(f"\nCopiando arquivos de: {caminho_subdiretorio}")
            # Lista todos os arquivos no subdiretório
            for nome_arquivo in os.listdir(caminho_subdiretorio):
                caminho_origem_arquivo = os.path.join(caminho_subdiretorio, nome_arquivo)

                # Verifica se o item é um arquivo (e não uma pasta)
                if os.path.isfile(caminho_origem_arquivo):
                    # Monta o caminho de destino para o arquivo
                    caminho_destino_arquivo = os.path.join(diretorio_destino, nome_arquivo)
                    # Copia o arquivo
                    shutil.copy2(caminho_origem_arquivo, caminho_destino_arquivo)
                    print(f"  -> Copiado: {nome_arquivo}")
        else:
            print(f"\nAviso: O subdiretório '{subdiretorio}' não foi encontrado em '{diretorio_raiz}'.")

    print("\nProcesso de cópia concluído! ✅")

# --- Exemplo de como usar a função ---

# 1. Especifique o diretório principal onde suas pastas estão
diretorio_principal = "Battery_Archive_Data"

# 2. Crie uma lista com os nomes exatos das pastas que você quer acessar
pastas_para_copiar = ["CALCE", "HNEI", "Michigan Expansion", "Michigan Formation", "Oxford", "SNL LFP", "SNL NCA","SNL NMC", "UL-Purdue"]

# 3. Especifique a pasta para onde todos os arquivos serão copiados
pasta_final = "Battery_Archive_Data_NoSubDirs"

# 4. Chame a função com os parâmetros definidos
copiar_arquivos_de_subdiretorios(diretorio_principal, pastas_para_copiar, pasta_final)