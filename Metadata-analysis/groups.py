import json
import pandas as pd
from collections import defaultdict

def json_dump(obj, fp, ensure_ascii=False, indent=4):
    converted_dict = { str(k): list(v) for k, v in obj.items() }
    json_string = json.dumps(converted_dict, ensure_ascii=ensure_ascii, indent=indent)
    fp.write(json_string)

# Removed: 'Institution','Cell ID','Temperature (°C)','Group'
matchingFeatures = ['Form Factor','Cathode','Min SOC (%)','Max SOC (%)','Charge Rate (C)','Discharge Rate (C)']
df = pd.read_csv('filenames.csv')

# [Form Factor,Cathode,Min SOC (%),Max SOC (%),Charge Rate (C),Discharge Rate (C)]: [linha a, linha b]
groups_dict = defaultdict(list)

### Para cada linha do df, se a chave existir no groups_dict, adicionar na lista dessa chave
### Se não, a nova chave é adicionada e a linha atual é associada
# Percorre cada linha do DataFrame
for idx, row in df.iterrows():
    # Monta a tupla que será usada como chave
    key = tuple(row[matchingFeatures])
    # Adiciona o índice da linha à lista correspondente
    groups_dict[key].append(row['Full Filename'])

for key, values in groups_dict.items():
    print(f"Chave <{key}>\t Tem {len(values)} em comum")

# Abre (ou cria) o arquivo em modo escrita e serializa o dicionário em JSON
json_dump(
    obj=groups_dict,
    fp=open('groups.json', 'w', encoding='utf-8'),
    ensure_ascii=False,
    indent=4
)

print(f"Dicionário salvo com sucesso")
