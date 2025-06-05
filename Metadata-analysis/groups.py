import json
import pandas as pd
from collections import defaultdict

def group_by_features(df, matchingFeatures, file_name):
    # [matchingFeatures]: ["linha a", "linha b"...]
    groups_dict = defaultdict(list)

    ### Para cada linha do df, se a chave existir no groups_dict, adicionar na lista dessa chave
    ### Se não, a nova chave é adicionada e a linha atual é associada
    # Percorre cada linha do DataFrame
    for idx, row in df.iterrows():
        # Monta a tupla que será usada como chave
        key = tuple(row[matchingFeatures])
        # Adiciona o índice da linha à lista correspondente
        groups_dict[key].append(row['Full Filename'])

    converted_dict = defaultdict(list)
    for key, values in groups_dict.items():
        print(f"Chave <{key}>\t Tem {len(values)} em comum")
        converted_dict[str(key)] = (list(values))

    # Salva em JSON
    json.dump(
        obj=converted_dict,
        fp=open(f'Metadata-analysis/GroupsOutput/{file_name}.json', 'w', encoding='utf-8'),
        ensure_ascii=False,
        indent=4
    )

# Removed: 'Institution','Cell ID','Group','Full Filename'
matchingFeatures = [
        'Form Factor',
        'Cathode',
        'Temperature (°C)',
        'Min SOC (%)',
        'Max SOC (%)',
        'Charge Rate (C)',
        'Discharge Rate (C)',
        'Capacity (Ah)',
        'Charge Current (A)',
        'Discharge Current (A)',
    ]

# ❗❗❗❗❗❗ Duvida: o que fazer com as capacidades aqui? Tirar já que a corrente é calculada a partir dela e é o que importa, ou deixar?

# Grupo A: Apenas Charge Current variando, resto constante. Tudo tem que ser igual, exceto Charge Current
groupA_matchingFeatures = matchingFeatures.copy()
groupA_matchingFeatures.remove('Charge Current (A)')

# Grupo B: Apenas Discharge Current variando, resto constante. Tudo tem que ser igual, exceto Discharge Current
groupB_matchingFeatures = matchingFeatures.copy()
groupB_matchingFeatures.remove('Discharge Current (A)')

df = pd.read_csv('Metadata-analysis/HeadersOutput/filenames.csv')

# Estrutura dos json: [matchingFeatures]: ["linha a", "linha b"...]
group_by_features(df, groupA_matchingFeatures, 'Group_A - Charge Current Variations')
group_by_features(df, groupB_matchingFeatures, 'Group_B - Discharge Current Variations')

print(f"Grupos salvos com sucesso")
