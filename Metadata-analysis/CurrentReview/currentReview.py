# Faça um código python que gere um CSV relatório a partir de dois outros:  "Metadata-analysis\CurrentsReview\weighted_averages_results.csv" e "Metadata-analysis\HeadersOutput\filenames.csv". 

# Os dataFrames deve ser juntados utilizando a coluna "Full Filename" como chave. Feito isso, as seguintes colunas devem ser adicionadas:

# - Coluna que mede a diferença em módulo das colunas "Charge Weighted Average (A)" e a coluna "Charge Current (A)".
# - Coluna que mede a diferença percentual dessa diferença de carga
# - Coluna que mede a diferença em módulo das colunas "Disharge_Weighted_Average" e a coluna "Discharge Current (A)".
# - Coluna que mede a diferença percentual dessa diferença de discarga

# Salve esse novo dataframe como "Metadata-analysis\CurrentsReview\currentReview"

import os
import numpy as np
import pandas as pd

filenames_path         = r"Metadata-analysis\HeadersOutput\filenames.csv"
weighted_averages_path = r"Metadata-analysis\CurrentReview\weighted_averages_results.csv"
output_path            = r"Metadata-analysis\CurrentReview\currentReview.csv"

try:
    # Load the DataFrames
    df_filenames = pd.read_csv(filenames_path)
    df_weighted_averages = pd.read_csv(weighted_averages_path)
    print("DataFrames loaded successfully.")

    # Merge the DataFrames
    merged_df = pd.merge(
        df_weighted_averages,
        df_filenames,
        left_on='Full Filename',
        right_on='Full Filename',
        how='outer'
    )

    # Apply abs to all numeric columns
    numeric_cols = merged_df.select_dtypes(include=[np.number]).columns
    merged_df[numeric_cols] = merged_df[numeric_cols].abs()

    # Calculate absolute difference for Charge
    # Ensure columns exist before calculation to prevent KeyError
    if 'Charge Weighted Average (A)' in merged_df.columns and 'Charge Current (A)' in merged_df.columns:
        merged_df['Charge Abs Difference'] = (merged_df['Charge Weighted Average (A)'] - merged_df['Charge Current (A)']).abs()
        # Avoid division by zero for percentage difference
        merged_df['Charge Percentage Difference'] = merged_df.apply(
            lambda row: (row['Charge Abs Difference'] / row['Charge Current (A)']) * 100
            
            if pd.notna(row['Charge Current (A)']) and row['Charge Current (A)'] != 0 else np.nan,
            axis=1
        )
    else:
        print("Warning: Missing 'Charge Weighted Average (A)' or 'Charge Current (A)' column. Skipping charge difference calculations.")
        input("Press Enter to continue...")

    # Calculate absolute difference for Discharge
    if 'Discharge Weighted Average (A)' in merged_df.columns and 'Discharge Current (A)' in merged_df.columns:
        merged_df['Discharge Abs Difference'] = (merged_df['Discharge Weighted Average (A)'] - merged_df['Discharge Current (A)']).abs()
        
        merged_df['Discharge Percentage Difference'] = merged_df.apply(
            lambda row: (row['Discharge Abs Difference'] / row['Discharge Current (A)']) * 100
            if pd.notna(row['Discharge Current (A)']) and row['Discharge Current (A)'] != 0 else np.nan,
            axis=1
        )
    else:
        print("Warning: Missing 'Discharge Weighted Average (A)' or 'Discharge Current (A)' column. Skipping discharge difference calculations.")
        input("Press Enter to continue...")

    # Select and reorder the columns for the final DataFrame
    # merged_df = merged_df[[
    #     'Institution', 
    #     'Charge Current (A)','Charge Weighted Average (A)', 'Charge Abs Difference', 'Charge Percentage Difference',
    #     'Discharge Current (A)','Discharge Weighted Average (A)', 'Discharge Abs Difference', 'Discharge Percentage Difference',
    #     'Full Filename'
    # ]]
    
    merged_df = merged_df[[
        'Institution', 
        'Charge Current (A)', 'Discharge Current (A)', 
        'Charge Weighted Average (A)', 'Discharge Weighted Average (A)', 
        'Charge Abs Difference', 'Discharge Abs Difference',
        'Discharge Percentage Difference', 'Charge Percentage Difference', 
        'Full Filename'
    ]]

    # Save the combined DataFrame to a new CSV
    merged_df.to_csv(output_path)
    print(f"Report successfully generated and saved to: {output_path}")

except FileNotFoundError as e:
    print(f"Error: One of the input files was not found. Please check the paths. {e}")
except KeyError as e:
    print(f"Error: A required column was not found in one of the DataFrames. Please check column names. {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")