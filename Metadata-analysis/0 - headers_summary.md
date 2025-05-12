# Header Datasets *timeseries*
- Todos os headers de todos os arquivos e instituições estão padronizados \
`Date_Time,Test_Time (s),Cycle_Index,Current (A),Voltage (V),Charge_Capacity (Ah),Discharge_Capacity (Ah),Charge_Energy (Wh),Discharge_Energy (Wh),Environment_Temperature (C),Cell_Temperature (C)`

# Header Datasets *cycle_data*
- Há dois formatos de headers, como mostrado abaixo. Porém, **não** serão utilizados nesse momento pois apenas apresentarem um registro por ciclo
    - Os *cycle_data* são uma versão simplificada dos *timeseries*
- CALCE, HNEI, Oxford, SNL LFP, SNL NCA, SNL NMC \
`Cycle_Index,Start_Time,End_Time,Test_Time (s),Min_Current (A),Max_Current (A),Min_Voltage (V),Max_Voltage (V),Charge_Capacity (Ah),Discharge_Capacity (Ah),Charge_Energy (Wh),Discharge_Energy (Wh)`

- Michigan Expansion, Michigan Formation, UL-Purdue \
`Cycle_Index,Test_Time (s),Min_Current (A),Max_Current (A),Min_Voltage (V),Max_Voltage (V),Charge_Capacity (Ah),Discharge_Capacity (Ah),Charge_Energy (Wh),Discharge_Energy (Wh)`