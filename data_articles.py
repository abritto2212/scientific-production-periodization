import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuración de estilo visual
sns.set_theme(style="whitegrid")
plt.rcParams.update({'font.size': 10, 'figure.autolayout': True})

file_path = r"C:\Users\User\Documents\UNAL\Articulo_Johan Ceballos\data_articles\data_articles.xlsx"

# Cargar el archivo Excel
try:
    xls = pd.ExcelFile(file_path)
    sheet_names = xls.sheet_names
    print(f"Se detectaron {len(sheet_names)} hojas en el archivo: {sheet_names}")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{file_path}'. Asegúrate de situar el script en la misma carpeta.")
    exit()

summary_list = []
dataframes = {}

# 1. Procesamiento de datos y extracción de métricas clave por estudio
for idx, sheet in enumerate(sheet_names, 1):
    df = pd.read_excel(xls, sheet_name=sheet)
    
    # Limpieza básica de nombres de columnas
    df.columns = [str(c).strip().replace(' ', '_') for c in df.columns]
    
    # Identificar columnas automáticamente
    year_col = [c for c in df.columns if 'year' in c.lower() or 'año' in c.lower()][0]
    pub_col = [c for c in df.columns if 'pub' in c.lower() or 'total' in c.lower()][0]
    
    df[year_col] = df[year_col].astype(int)
    df[pub_col] = df[pub_col].astype(int)
    
    dataframes[sheet] = (df, year_col, pub_col)
    
    # Cálculo de métricas
    start_year = df[year_col].min()
    end_year = df[year_col].max()
    time_span = end_year - start_year + 1
    total_pubs = df[pub_col].sum()
    peak_row = df.loc[df[pub_col].idxmax()]
    
    summary_list.append({
        'Caso': f"Caso {idx}",
        'Hoja': sheet,
        'Año Inicio': start_year,
        'Año Fin': end_year,
        'Periodo (Años)': time_span,
        'Total Pubs': total_pubs,
        'Pico Máx (Año)': int(peak_row[year_col]),
        'Máx Pubs/Año': int(peak_row[pub_col]),
        'Promedio Anual': round(df[pub_col].mean(), 1)
    })

# Convertir a DataFrame el resumen general
df_summary = pd.DataFrame(summary_list)

# Guardar tabla resumen
df_summary.to_csv('resumen_10_estudios.csv', index=False, encoding='utf-8-sig')

print("\n" + "="*80)
print(" TABLA RESUMEN DE LOS 10 CASOS DE ESTUDIO")
print("="*80)
print(df_summary.to_string(index=False))

# 2. Generar panel gráfico de 10 subplots (Grilla 5x2)
fig, axes = plt.subplots(5, 2, figsize=(15, 18))
axes = axes.flatten()

for i, sheet in enumerate(sheet_names[:10]):
    df, y_col, p_col = dataframes[sheet]
    
    ax = axes[i]
    ax.plot(df[y_col], df[p_col], marker='o', color='#b22222', linewidth=2, markersize=4)
    ax.fill_between(df[y_col], df[p_col], color='#b22222', alpha=0.15)
    
    ax.set_title(f"Caso {i+1}: {sheet} ({df[y_col].min()}-{df[y_col].max()})", fontweight='bold')
    ax.set_ylabel('Publicaciones')
    ax.grid(True, linestyle='--', alpha=0.6)

# Ocultar cuadros vacíos si hay menos de 10 hojas
for j in range(len(sheet_names), len(axes)):
    fig.delaxes(axes[j])

plt.suptitle('Evolución Anual de la Producción Científica (10 Casos)', fontsize=16, fontweight='bold', y=1.01)
plt.savefig('panel_10_casos.png', dpi=300, bbox_inches='tight')
plt.close()

# 3. Generar gráfica comparativa normalizada (Trayectorias relativas)
plt.figure(figsize=(12, 6))

for sheet in sheet_names[:10]:
    df, y_col, p_col = dataframes[sheet]
    # Normalización Min-Max (0 a 1) para comparar dinámicas de crecimiento independientemente del volumen
    norm_pubs = (df[p_col] - df[p_col].min()) / (df[p_col].max() - df[p_col].min() + 1e-5)
    plt.plot(df[y_col], norm_pubs, alpha=0.7, label=sheet, linewidth=1.8)

plt.title('Comparativa de Patrones de Crecimiento (Escala Normalizada 0-1)', fontsize=14, fontweight='bold')
plt.xlabel('Año')
plt.ylabel('Crecimiento Relativo')
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=True)
plt.grid(True, linestyle='--', alpha=0.5)
plt.savefig('trayectorias_normalizadas.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "="*80)
print("¡Proceso finalizado! Se generaron los siguientes archivos:")
print(" 1. resumen_10_estudios.csv       -> Tabla consolidada para incluir en los Resultados.")
print(" 2. panel_10_casos.png            -> Imagen HD con las 10 gráficas en cuadrícula.")
print(" 3. trayectorias_normalizadas.png -> Imagen HD para comparar las tendencias relativas.")
print("="*80)