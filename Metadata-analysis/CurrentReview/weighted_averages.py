
from tqdm import tqdm
import pandas as pd
import numpy as np
import os

ERROR_NUM = 999999

import pandas as pd
import numpy as np

def manual_weighted_average(df: pd.DataFrame) -> dict:
    """
    Calculates the time-weighted average for charge and discharge currents
    by iterating through the DataFrame rows manually.

    This function replaces the vectorized np.average(..., weights=...) call.

    Args:
        df: Pandas DataFrame with 'Test_Time (s)' and 'Current (A)' columns.

    Returns:
        A dictionary containing the weighted averages for charge and discharge currents.
    """

    # Garante a ordem cronológica
    df = df.sort_values("Test_Time (s)").reset_index(drop=True)

    # Calcula o intervalo de tempo até a PRÓXIMA medição. Esse é o peso para a medição da linha ATUAL.
    df['Time_Interval'] = df['Test_Time (s)'].shift(-1) - df['Test_Time (s)']
    df['Time_Interval'] = df['Time_Interval'].fillna(0) # O último intervalo é 0

    charge_acc = 0.0  # Acumulador para: Current * Time_Interval (Carga)
    charge_weight_acc = 0.0   # Acumulador para: Time_Interval (Carga)

    discharge_acc = 0.0 # Acumulador para: Current * Time_Interval (Descarga)
    discharge_weight_acc = 0.0  # Acumulador para: Time_Interval (Descarga)

    # zip é mais eficiente que df.iterrows()
    for current, interval in zip(df['Current (A)'], df['Time_Interval']):
        # Se a corrente for positiva (carga)
        if current > 0:
            charge_acc += current * interval
            charge_weight_acc += interval
        # Se a corrente for negativa (descarga)
        elif current < 0:
            discharge_acc += current * interval
            discharge_weight_acc += interval
        # Correntes iguais a zero são ignoradas

    # Calcula a média final evitando a divisão por zero
    charge_avg = (
        charge_acc / charge_weight_acc if charge_weight_acc > 0 else np.nan
    )

    discharge_avg = (
        discharge_acc / discharge_weight_acc if discharge_weight_acc > 0 else np.nan
    )

    return {
        'charge_weighted_average': charge_avg,
        'discharge_weighted_average': discharge_avg
    }

# Faça uma main que iniciando no diretório "Battery_Archive_Data", acesse todas as pastas nele informadas numa lista e para cada CSV encontrado, aplique a função de média ponderada. Não crie nenhuma estrutura para testes, os diretórios informados já existem. Cada resultado deve ser escrito num novo arquivo csv com uma coluna contendo o nome do arquivo e outra a média ponderadaa.
def main():
    folder_path = "Battery_Archive_Data_NoSubDirs"
    results = []
    # Itera sobre todos os arquivos dentro da pasta
    for file_name in tqdm(os.listdir(folder_path)):
        if file_name.endswith(".csv") and ("timeseries" in file_name):
            file_path = os.path.join(folder_path, file_name)
            print(f"  Processando arquivo: {file_name}")
            try:
                # Carrega o CSV
                df = pd.read_csv(file_path)

                # Verifica se as colunas necessárias existem
                if 'Current (A)' in df.columns and 'Test_Time (s)' in df.columns:
                    # Aplica a função de média ponderada
                    weighted_averages = manual_weighted_average(df)

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
    output_csv_name = "Metadata-analysis/CurrentReview/weighted_averages_results.csv"
    results_df.to_csv(output_csv_name)
    print(f"\nProcessamento concluído. Resultados salvos em '{output_csv_name}'")

if __name__ == "__main__":
    main()