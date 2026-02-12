import pandas as pd
import os
import glob

# Find the latest ODS or CSV file in output directory
list_of_files = [f for f in glob.glob('output/*.ods') + glob.glob('output/*.csv') if not os.path.basename(f).startswith('~$')]
if not list_of_files:
    print("No ODS or CSV file found in output/")
    exit(1)

latest_file = max(list_of_files, key=os.path.getctime)
print(f"Checking file: {latest_file}")

try:
    if latest_file.endswith('.csv'):
        df = pd.read_csv(latest_file)
    else:
        df = pd.read_excel(latest_file, engine='odf')
    
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    print("\nDistribution by Element:")
    print(df['elemento'].value_counts())
    
    print("\nDistribution by Type:")
    print(df['tipo'].value_counts())
    
    print("\nDistribution by Element and Type:")
    print(df.groupby(['elemento', 'tipo']).size())
    
    # Check for nulls
    print(f"\nNull values:\n{df.isnull().sum()}")
    
except Exception as e:
    print(f"Error reading file: {e}")
