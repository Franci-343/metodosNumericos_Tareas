
"""
Ejemplo práctico: sistema de puntería y análisis de errores.

Descripción:
- Simulamos un conjunto de ángulos de puntería verdaderos (no nulos) y
	las lecturas reales del tirador (con sesgo y ruido).
- Calculamos error absoluto y relativo en grados (ver README).
- Representamos gráficas: verdadero vs real, errores por disparo, impactos en plano
- Opcional: ventana GUI con matplotlib embebido (si tkinter está disponible)

Historia:
En una zona montañosa, un equipo de francotiradores debe ajustar sus miras antes de
una misión de entrenamiento. La topografía y el viento provocan desviaciones muy
pequeñas en ángulos medidos, pero estos se traducen en metros de diferencia en el
impacto para blancos a gran distancia. La sargento Elena toma notas de cada ajuste
y su equipo registra las desviaciones laterales en un blanco objetivo. Con estos
datos, el equipo analiza el comportamiento del sesgo y el ruido para mejorar la
calibración de sus armas.

El presente script simula esa situación: genera ángulos verdaderos y medidos,
calcula errores absolutos/relativos y proyecta los impactos en el plano del blanco
para visualizar la dispersión y el posible sesgo sistemático.
"""

import os
import sys
import math
import random
import statistics
from typing import List, Dict, Tuple

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

try:
	import tkinter as tk
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
	TK_AVAILABLE = True
except Exception:
	TK_AVAILABLE = False


def compute_errors(true_vals: List[float], approx_vals: List[float]) -> Tuple[List[float], List[float]]:
	abs_errs = []
	rel_errs = []
	for t, a in zip(true_vals, approx_vals):
		ea = abs(t - a)
		er = ea / abs(t) if t != 0 else float('inf')
		abs_errs.append(ea)
		rel_errs.append(er)
	return abs_errs, rel_errs


def lateral_displacement(angle_deg: float, distance_m: float) -> float:
	# Desplazamiento lateral en el objetivo a partir del ángulo de desviación
	return distance_m * math.tan(math.radians(angle_deg))


def save_plots(records: List[Dict], out_dir: str):
	os.makedirs(out_dir, exist_ok=True)

	true_angles = [r['true_angle'] for r in records]
	meas_angles = [r['measured_angle'] for r in records]
	abs_errs = [r['abs_err'] for r in records]
	lat_true = [r['lat_true'] for r in records]
	lat_meas = [r['lat_meas'] for r in records]

	# Scatter: ángulo verdadero vs medido
	fig1, ax1 = plt.subplots(figsize=(6, 4))
	ax1.scatter(true_angles, meas_angles, color='tab:blue')
	ax1.plot([min(true_angles), max(true_angles)], [min(true_angles), max(true_angles)], '--', color='gray')
	ax1.set_xlabel('Ángulo verdadero (°)')
	ax1.set_ylabel('Ángulo medido (°)')
	ax1.set_title('Ángulo verdadero vs Ángulo medido')
	fig1.tight_layout()
	fig1.savefig(os.path.join(out_dir, 'angle_true_vs_meas.png'))
	plt.close(fig1)

	# Error por disparo
	fig2, ax2 = plt.subplots(figsize=(6, 3))
	ax2.plot(range(1, len(abs_errs) + 1), abs_errs, marker='o')
	ax2.set_xlabel('Disparo #')
	ax2.set_ylabel('Error absoluto (°)')
	ax2.set_title('Error absoluto por disparo')
	fig2.tight_layout()
	fig2.savefig(os.path.join(out_dir, 'abs_error_by_shot.png'))
	plt.close(fig2)

	# Impactos en plano del blanco (latitud en m)
	fig3, ax3 = plt.subplots(figsize=(6, 3))
	ax3.axvline(0, color='gray', linestyle='--', label='Blanco (centro)')
	ax3.scatter(lat_true, [0]*len(lat_true), marker='x', color='green', label='Esperado')
	ax3.scatter(lat_meas, [0]*len(lat_meas), marker='o', color='red', label='Impactos medidos')
	ax3.set_xlabel('Desplazamiento lateral (m)')
	ax3.set_yticks([])
	ax3.set_title('Impactos en el blanco (proyección lateral)')
	ax3.legend()
	fig3.tight_layout()
	fig3.savefig(os.path.join(out_dir, 'impacts_plane.png'))
	plt.close(fig3)


def run_gui(records: List[Dict]):
	if not TK_AVAILABLE:
		print('tkinter no disponible; GUI no se puede mostrar.')
		return

	lat_true = [r['lat_true'] for r in records]
	lat_meas = [r['lat_meas'] for r in records]

	root = tk.Tk()
	root.title('Sistema de puntería - impactos')

	fig, ax = plt.subplots(figsize=(6, 4))
	ax.axvline(0, color='gray', linestyle='--')
	ax.scatter(lat_true, [0]*len(lat_true), marker='x', color='green', label='Esperado')
	ax.scatter(lat_meas, [0]*len(lat_meas), marker='o', color='red', label='Impactos')
	ax.set_xlabel('Desplazamiento lateral (m)')
	ax.set_yticks([])
	ax.set_title('Impactos proyectados (lateral)')
	ax.legend()

	canvas = FigureCanvasTkAgg(fig, master=root)
	canvas.draw()
	canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	mean_abs = statistics.mean([r['abs_err'] for r in records])
	lbl = tk.Label(root, text=f'Error absoluto medio: {mean_abs:.4f} °')
	lbl.pack(side=tk.BOTTOM, fill=tk.X)

	root.mainloop()


def main(argv):
	random.seed(123)

	# Parámetros: distancia al blanco (m)
	distance = 250.0

	# Definir al menos 10 ángulos verdaderos (no nulos) en grados
	true_angles = [1.5, 2.0, 1.8, 2.2, 1.7, 2.5, 1.9, 2.1, 2.3, 1.6, 2.4, 1.85]

	# Simular mediciones: sesgo + ruido (en grados)
	bias = -0.2  # sesgo de calibración (°), por ejemplo deriva a la izquierda
	sigma = 0.6  # desviación típica del tirador (°)

	records: List[Dict] = []
	for i, t in enumerate(true_angles, start=1):
		measured = t + bias + random.gauss(0, sigma)
		ea = abs(t - measured)
		er = ea / abs(t) if t != 0 else float('inf')
		lat_t = lateral_displacement(t, distance)
		lat_m = lateral_displacement(measured, distance)
		records.append({
			'shot': i,
			'true_angle': t,
			'measured_angle': measured,
			'abs_err': ea,
			'rel_err': er,
			'lat_true': lat_t,
			'lat_meas': lat_m,
		})

	out_dir = os.path.join(os.path.dirname(__file__), 'output_ej3')
	save_plots(records, out_dir)

	abs_errs = [r['abs_err'] for r in records]
	rel_errs = [r['rel_err'] for r in records]
	print('\nResumen Ejemplo 3 - Sistema de puntería')
	print('------------------------------------')
	print(f'Tiros: {len(records)}')
	print(f'Error absoluto medio: {statistics.mean(abs_errs):.4f} °')
	print(f'Error absoluto máximo: {max(abs_errs):.4f} °')
	print(f'Error relativo medio: {statistics.mean(rel_errs) * 100:.4f} %')
	print('\nTabla de resultados:')
	print('i | ang_true(°) | ang_meas(°) | err_abs(°) | err_rel(%) | lat_true(m) | lat_meas(m)')
	for r in records:
		print(f"{r['shot']:2d} | {r['true_angle']:11.3f} | {r['measured_angle']:11.3f} | {r['abs_err']:9.4f} | {r['rel_err']*100:9.4f} | {r['lat_true']:10.3f} | {r['lat_meas']:10.3f}")

	if '--gui' in argv:
		run_gui(records)


if __name__ == '__main__':
	main(sys.argv[1:])
