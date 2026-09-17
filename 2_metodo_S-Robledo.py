import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import itertools


years = np.array([
    2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
    2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024
])
values = np.array([
    1, 0, 0, 2, 0, 1, 3, 0, 0, 1, 2, 2, 5, 4, 16, 31, 50, 50, 85, 127, 141, 142
])
# ==========================
# Datos (Profesor Sebastián Robledo)
# ==========================
# years = np.array(
#     [2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013,
#      2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
# )
# values = np.array(
#     [2, 0, 2, 1, 3, 5, 7, 5, 9, 5,
#      6, 6, 3, 3, 12, 13, 19, 11, 10, 23, 19]
# )

# ==========================
# Función para ajuste por tramos (mínimo 3 años por tramo)
# ==========================
def piecewise_linear_fit(years, values, n_breaks=2, min_len=3):
    """
    Ajuste por regresión lineal por tramos que minimiza el error cuadrático total.
    Explora todas las combinaciones posibles de puntos de cambio.
    """
    n = len(years)
    best_sse = np.inf
    best_breaks = None

    # Todas las combinaciones posibles de puntos de cambio
    possible_breaks = range(min_len, n - min_len + 1)
    for breaks in itertools.combinations(possible_breaks, n_breaks):
        breaks = sorted(list(breaks))
        segments = np.split(values, breaks)
        year_segments = np.split(years, breaks)

        # Calcula el SSE total
        sse = 0
        for x, y in zip(year_segments, segments):
            model = LinearRegression().fit(x.reshape(-1, 1), y)
            y_pred = model.predict(x.reshape(-1, 1))
            sse += np.sum((y - y_pred) ** 2)

        if sse < best_sse:
            best_sse = sse
            best_breaks = breaks

    return best_breaks

# ==========================
# Ajuste con 2 puntos de cambio (3 periodos)
# ==========================
break_indices = piecewise_linear_fit(years, values, n_breaks=2, min_len=3)
break_years = [years[i - 1] for i in break_indices]
segments = np.split(values, break_indices)
year_segments = np.split(years, break_indices)

# ==========================
# Gráfica
# ==========================
plt.figure(figsize=(11, 6))
plt.plot(years, values, 'o-', color='black', label='Datos originales')

for i, (x, y) in enumerate(zip(year_segments, segments)):
    model = LinearRegression().fit(x.reshape(-1, 1), y)
    y_pred = model.predict(x.reshape(-1, 1))
    plt.plot(x, y_pred, linewidth=3)

    # Calcular crecimiento total del periodo (porcentaje total)
    start, end = y[0], y[-1]
    if start > 0:
        growth = ((end - start) / start) * 100
        growth_text = f"+{growth:.1f}%"
    else:
        growth_text = "N/A"

    # Posición del texto en el centro del tramo
    mid_x = x[len(x)//2]
    mid_y = y_pred[len(x)//2]
    plt.text(mid_x, mid_y + 1.5, growth_text, fontsize=10, color='blue', ha='center', fontweight='bold')

# ==========================
# Añadir líneas verticales y etiquetas de los años
# ==========================
for by in break_years:
    plt.axvline(by, color='red', linestyle='--', linewidth=1.2)
    plt.text(by + 0.2, plt.ylim()[1] * 0.95, str(by),
             color='red', fontsize=10, rotation=90, va='top', ha='left', fontweight='bold')

# ==========================
# Formato final
# ==========================
plt.title('Periodización por regresión lineal por tramos (2004–2024)')
plt.xlabel('Año')
plt.ylabel('Publicaciones')
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
