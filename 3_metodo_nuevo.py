import os
import numpy as np
import matplotlib.pyplot as plt
import ruptures as rpt

# years = np.array([
#     2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#     2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
# ])
# values = np.array([
#     1, 0, 0, 2, 0, 1, 3, 0, 0, 1, 2, 2, 5, 4, 16, 31, 50, 50, 85, 127, 141, 142
# ])


years = np.array(
    [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 
     2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
)
values = np.array(
    [2, 0, 2, 1, 3, 5, 7, 5, 9, 5, 
     6, 6, 3, 3, 12, 13, 19, 11, 10, 23, 19]
)

# 2. Crear la carpeta de destino si no existe
carpeta = "3_Método"
os.makedirs(carpeta, exist_ok=True)

# 3. Configurar y aplicar el modelo de Detección de Puntos de Cambio
# model="l2" busca cambios abruptos en la media aritmética de los datos.
# min_size=3 asegura que cada periodo tenga al menos 3 años de duración.
algoritmo = rpt.Dynp(model="l2", min_size=3).fit(values)

# Pedimos exactamente 2 puntos de quiebre (n_bkps=2) para obtener 3 periodos.
cortes_indices = algoritmo.predict(n_bkps=2)

# 4. Configurar la figura y graficar la serie temporal original
plt.figure(figsize=(12, 6))
plt.plot(years, values, marker='o', linestyle='-', color='dodgerblue', linewidth=2, label='Total Publicaciones')

# 5. Dibujar las líneas verticales en los años detectados
# ruptures incluye el tamaño total del arreglo como el último "corte", por eso lo ignoramos con [:-1]
for i, indice in enumerate(cortes_indices[:-1]):
    # Mapeamos el índice devuelto por el algoritmo al año correspondiente
    anio_corte = years[indice]
    plt.axvline(x=anio_corte, color='crimson', linestyle='--', linewidth=2, 
                label=f'Transición a Periodo {i+2} ({anio_corte})')
    
    # Agregar un área sombreada para diferenciar visualmente los periodos (opcional, pero estético)
    if i == 0:
        plt.axvspan(years[0], anio_corte, color='gray', alpha=0.1)
    else:
        plt.axvspan(years[cortes_indices[i-1]], anio_corte, color='gray', alpha=0.2)

# Sombreado para el último periodo
plt.axvspan(years[cortes_indices[-2]], years[-1], color='gray', alpha=0.3)

# 6. Detalles estéticos (títulos, ejes y leyenda)
plt.title('Detección Automática de Periodos de Producción Científica', fontsize=15, pad=15)
plt.xlabel('Año', fontsize=12)
plt.ylabel('Número de Publicaciones', fontsize=12)
plt.xticks(years, rotation=45)
plt.yticks(np.arange(0, max(values)+5, 2))
plt.grid(axis='y', linestyle=':', alpha=0.6)
plt.legend(loc='upper left')
plt.tight_layout()

# 7. Guardar la gráfica en la carpeta especificada
ruta_archivo = os.path.join(carpeta, "grafica_puntos_cambio.png")
plt.savefig(ruta_archivo, dpi=300)
print(f"La gráfica ha sido detectada, generada y guardada en: {ruta_archivo}")

# 8. Mostrar la gráfica en pantalla
plt.show()



# import numpy as np
# import matplotlib.pyplot as plt
# from sklearn.cluster import KMeans
# from scipy.ndimage import gaussian_filter1d

# # --- SELECCIONA EL CONJUNTO DE DATOS ---
# # Datos 1
# # years = np.array([
# #     2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
# #     2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
# # ])
# # values = np.array([
# #     1, 0, 0, 2, 0, 1, 3, 0, 0, 1, 2, 2, 5, 4, 16, 31, 50, 50, 85, 127, 141, 142
# # ])

# # Datos 2 (Profesor Sebastián Robledo)
# years = np.array(
#     [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 
#      2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
# )
# values = np.array(
#     [2, 0, 2, 1, 3, 5, 7, 5, 9, 5, 
#      6, 6, 3, 3, 12, 13, 19, 11, 10, 23, 19]
# )

# # --- 1. Suavizado Gaussiano ---
# smoothed = gaussian_filter1d(values, sigma=2)

# # --- 2. Calcular las pendientes suavizadas ---
# slopes = np.diff(smoothed) / np.diff(years)

# # --- 3. Agrupar pendientes con K-means ---
# k = 4  # número máximo de periodos
# model = KMeans(n_clusters=k, random_state=42, n_init=10)
# clusters = model.fit_predict(slopes.reshape(-1, 1))

# # --- 4. Detectar los puntos de cambio (cuando cambia el cluster) ---
# change_points = [0]
# for i in range(1, len(clusters)):
#     if clusters[i] != clusters[i - 1]:
#         change_points.append(i)
# change_points.append(len(values) - 1)

# # --- 5. Calcular porcentaje de aumento por periodo ---
# periods = []
# for i in range(len(change_points) - 1):
#     start, end = change_points[i], change_points[i + 1]
#     v_ini, v_fin = values[start], values[end]
#     if v_ini == 0:
#         pct = np.nan
#     else:
#         pct = ((v_fin - v_ini) / v_ini) * 100
#     periods.append((years[start], years[end], pct))

# # --- 6. Graficar ---
# plt.figure(figsize=(10, 6))
# plt.plot(years, values, 'o-', label='Datos originales', alpha=0.6)
# plt.plot(years, smoothed, '-', color='blue', label='Serie suavizada', linewidth=2)

# # Marcar puntos de cambio
# for i in change_points[1:-1]:
#     plt.axvline(years[i], color='red', linestyle='--', linewidth=1.5)
#     plt.text(years[i], max(values)*0.9, str(years[i]), rotation=90,
#              color="red", fontsize=9, ha="center", va="bottom")

# # Etiquetas con % de crecimiento
# for (start, end, pct) in periods:
#     mid = (start + end) / 2
#     plt.text(mid, max(values)*0.7, f"{start}-{end}\n{pct:.1f}%", 
#              ha="center", fontsize=9, bbox=dict(facecolor="white", alpha=0.6))

# plt.title("Segmentación de periodos mediante K-Means + suavizado gaussiano")
# plt.xlabel("Año")
# plt.ylabel("Número de publicaciones")
# plt.legend()
# plt.grid(True, linestyle="--", alpha=0.6)
# plt.tight_layout()
# plt.savefig("periodos_kmeans_suavizado.png", dpi=300, bbox_inches="tight")
# plt.show()

# # --- 7. Mostrar resumen en consola ---
# print("Periodos detectados con porcentaje de aumento:")
# for i, (start, end, pct) in enumerate(periods, 1):
#     print(f"Periodo {i}: {start}–{end} | Crecimiento = {pct:.2f}%")
