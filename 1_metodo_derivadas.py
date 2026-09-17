import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d

# --- Datos --- 1
# years = np.array([
#     2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#     2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
# ])
# values = np.array([
#     1, 0, 0, 2, 0, 1, 3, 0, 0, 1, 2, 2, 5, 4, 16, 31, 50, 50, 85, 127, 141, 142
# ])


# --- Datos --- 2 (Profesor Sebastián Robledo)
years = np.array(
    [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 
         2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
)
values = np.array(
    [2, 0, 2, 1, 3, 5, 7, 5, 9, 5, 
    6, 6, 3, 3, 12, 13, 19, 11, 10, 23, 19]
          )

# --- Suavizado ---
smoothed = gaussian_filter1d(values, sigma=2)

# --- Derivadas ---
d1 = np.gradient(smoothed)
d2 = np.gradient(d1)

# --- Detectar puntos de cambio (picos en la 2ª derivada) ---
peaks_idx, _ = find_peaks(np.abs(d2), height=np.std(d2))
change_years = years[peaks_idx]

# --- Añadir inicio y fin como bordes de periodos ---
period_limits = np.sort(np.concatenate(([years[0]], change_years, [years[-1]])))

# --- Calcular crecimiento por periodo ---
periods = []
for i in range(len(period_limits)-1):
    start = period_limits[i]
    end = period_limits[i+1]
    start_val = values[np.where(years == start)][0]
    end_val = values[np.where(years == end)][0]
    growth = ((end_val - start_val) / start_val * 100) if start_val > 0 else np.nan
    periods.append((start, end, start_val, end_val, growth))

# --- Graficar ---
plt.figure(figsize=(12,5))
plt.plot(years, values, "o-", label="Publicaciones (datos)")
plt.plot(years, smoothed, "-", label="Suavizado")

# Mostrar el número exacto en cada punto
for x, y in zip(years, values):
    plt.text(x, y + 2, str(y), ha="center", va="bottom", fontsize=8, color="black")

# Marcar años de cambio
for y in change_years:
    plt.axvline(x=y, color="red", linestyle="--", alpha=0.7)
    plt.text(y, max(values)*0.9, str(y), rotation=90, 
             color="red", fontsize=10, ha="center", va="bottom")

# Mostrar info de periodos en la gráfica
for (start, end, s_val, e_val, growth) in periods:
    label = f"{start}-{end}\n{growth:.1f}%"
    plt.text((start+end)/2, max(values)*0.6, label,
             ha="center", va="center", fontsize=9,
             bbox=dict(facecolor="white", alpha=0.6, edgecolor="gray"))

plt.xticks(years, rotation=45)
plt.xlabel("Año")
plt.ylabel("Número de publicaciones")
plt.title("Detección de etapas y crecimiento porcentual")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()

# --- Guardar ---
plt.savefig("cambio_etapas_con_crecimiento.png", dpi=300, bbox_inches="tight")
plt.show()

# --- Mostrar resultados en consola ---
print("Periodos detectados con crecimiento:")
for (start, end, s_val, e_val, growth) in periods:
    print(f"{start}-{end}: {s_val} → {e_val}, Crecimiento = {growth:.1f}%")
