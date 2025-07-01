import pandas as pd

# La ruta a tu archivo Excel
file_path = 'data/ALFABETA PUBLICADO EN OCTUBRE.xlsx'

try:
    xls = pd.ExcelFile(file_path)

    print("\n--- Nombres de columnas en la hoja 'Laboratorio' ---")
    df_lab = pd.read_excel(xls, 'Laboratorio')
    print(df_lab.columns.tolist())

    print("\n--- Nombres de columnas en la hoja 'Monodroga' ---")
    df_mono = pd.read_excel(xls, 'Monodroga')
    print(df_mono.columns.tolist())

    print("\n--- Nombres de columnas en la hoja 'Medicamentos' ---")
    df_med = pd.read_excel(xls, 'Medicamentos')
    print(df_med.columns.tolist())

except Exception as e:
    print(f"Ocurrió un error: {e}")