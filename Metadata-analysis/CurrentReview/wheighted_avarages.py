
import pandas as pd
import numpy as np
import os

ERROR_NUM = 999999

# Faça uma função que retorna uma média ponderada de uma coluna "Current (A)". Considere que o tempo é o peso, a diferença entre os tempos é o intervalo de tempo. O tempo entre uma medição de corrente e outra pode ser adquirida usando a coluna "Test_Time (s)". Entretato, as correntes positivas (correntes de carga) devem ser tratadas separadamente das corretente negativas (correntes de descarga). A média ponderada deve ser calculada separadamente para as correntes de carga e descarga. A função deve receber um DataFrame do Pandas como entrada e retornar um dicionário com as médias ponderadas para as correntes de carga e descarga.
def calculate_weighted_average(df: pd.DataFrame) -> dict:
    
    # Ensure Test_Time (s) is sorted
    df = df.sort_values("Test_Time (s)").reset_index(drop=True)
    
    # Calculate time differences
    df['Time_Interval'] = df['Test_Time (s)'].diff().fillna(0)

    # Separate charge and discharge currents
    charge_df = df[df['Current (A)'] > 0].copy()
    discharge_df = df[df['Current (A)'] < 0].copy()

    # Calculate weighted average for charge
    if not charge_df.empty:
        charge_weighted_avg = np.average(charge_df['Current (A)'], weights=charge_df['Time_Interval'])
    else:
        charge_weighted_avg = ERROR_NUM

    # Calculate weighted average for discharge
    if not discharge_df.empty:
        discharge_weighted_avg = np.average(discharge_df['Current (A)'], weights=discharge_df['Time_Interval'])
    else:
        discharge_weighted_avg = ERROR_NUM

    return {
        'charge_weighted_average': charge_weighted_avg,
        'discharge_weighted_average': discharge_weighted_avg
    }
    
# Faça uma main que iniciando no diretório "Battery_Archive_Data", acesse todas as pastas nele informadas numa lista e para cada CSV encontrado, aplique a função de média ponderada. Não crie nenhuma estrutura para testes, os diretórios informados já existem. Cada resultado deve ser escrito num novo arquivo csv com uma coluna contendo o nome do arquivo e outra a média ponderadaa.
def main():
    folder_path = "Battery_Archive_Data_NoSubDirs"
    results = []
    count = 0
    # Itera sobre todos os arquivos dentro da pasta
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv") and ("timeseries" in file_name):
            file_path = os.path.join(folder_path, file_name)
            print(f"  Processando arquivo: {file_name}")
            if count > 8:
                break
            count += 1
            try:
                # Carrega o CSV
                df = pd.read_csv(file_path)

                # Verifica se as colunas necessárias existem
                if 'Current (A)' in df.columns and 'Test_Time (s)' in df.columns:
                    # Aplica a função de média ponderada
                    weighted_averages = calculate_weighted_average(df)

                    # Armazena os resultados
                    results.append({
                        'Full Filename': file_name,
                        'Charge Weighted Average (A)': weighted_averages['charge_weighted_average'],
                        'Discharge Weighted Average (A)': weighted_averages['discharge_weighted_average']
                    })
                else:
                    print(f"    Erro: O arquivo '{file_name}' não contém as colunas 'Current (A)' e/ou 'Test_Time (s)'. Pulando.")

            except Exception as e:
                print(f"    Erro ao processar o arquivo '{file_name}': {e}. Pulando.")

    results_df = pd.DataFrame(results)
    output_csv_name = "Metadata-analysis\CurrentReview\weighted_averages_results.csv"
    results_df.to_csv(output_csv_name)
    print(f"\nProcessamento concluído. Resultados salvos em '{output_csv_name}'")

if __name__ == "__main__":
    main()