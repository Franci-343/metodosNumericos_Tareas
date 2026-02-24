
"""
Ejemplo práctico: caída de proyectiles y análisis de errores.

Este script:
- Calcula la distancia (alcance) teórica de un proyectil con movimiento parabólico
- Simula 10 disparos con error del tirador (sigma ~ 0.5°)
- Calcula error absoluto y relativo (ver README)
- Guarda gráficos con matplotlib y ofrece una vista rápida con tkinter

Historia:
En el polígono de prácticas de la academia, el instructor José ha preparado una
actividad donde cada cadete debe estimar la elevación correcta para alcanzar un
objetivo a distancia. Algunos cadetes tienden a sobreestimar la inclinación y otros
a subestimar; además, las condiciones ambientales simulan una ligera variación.
El propósito es medir cómo pequeñas diferencias angulares (en décimas o medias de
grado) se traducen en variaciones considerables del alcance por efecto de la
parábola del proyectil. Este ejemplo muestra cómo modelar y cuantificar esos errores
usando fórmulas físicas básicas y medidas simuladas.

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


def range_projectile(v: float, angle_deg: float, g: float = 9.81) -> float:
	theta = math.radians(angle_deg)
	return (v * v) * math.sin(2 * theta) / g


def compute_errors(true_vals: List[float], approx_vals: List[float]) -> Tuple[List[float], List[float]]:
	abs_errs = []
	rel_errs = []
	for t, a in zip(true_vals, approx_vals):
		ea = abs(t - a)
		er = ea / abs(t) if t != 0 else float('inf')
		abs_errs.append(ea)
		rel_errs.append(er)
	return abs_errs, rel_errs


def save_plots(data: List[Dict], out_dir: str):
	os.makedirs(out_dir, exist_ok=True)

	true_ranges = [d['true_range'] for d in data]
	meas_ranges = [d['measured_range'] for d in data]
	abs_errs = [d['abs_err'] for d in data]

	# Scatter true vs medido
	fig1, ax1 = plt.subplots(figsize=(6, 4))
	ax1.scatter(true_ranges, meas_ranges, color='tab:green')
	ax1.plot([min(true_ranges), max(true_ranges)], [min(true_ranges), max(true_ranges)], '--', color='gray')
	ax1.set_xlabel('Alcance teórico (m)')
	ax1.set_ylabel('Alcance medido (m)')
	ax1.set_title('Alcance teórico vs medido')
	fig1.tight_layout()
	fig1.savefig(os.path.join(out_dir, 'scatter_range.png'))
	plt.close(fig1)

	# Error por disparo
	fig2, ax2 = plt.subplots(figsize=(6, 3))
	ax2.plot(range(1, len(abs_errs) + 1), abs_errs, marker='o', color='tab:red')
	ax2.set_xlabel('Disparo #')
	ax2.set_ylabel('Error absoluto (m)')
	ax2.set_title('Error absoluto por disparo')
	fig2.tight_layout()
	fig2.savefig(os.path.join(out_dir, 'abs_error_by_shot.png'))
	plt.close(fig2)

	# Histograma
	fig3, ax3 = plt.subplots(figsize=(6, 3))
	ax3.hist(abs_errs, bins=6, color='tab:orange', edgecolor='black')
	ax3.set_xlabel('Error absoluto (m)')
	ax3.set_ylabel('Frecuencia')
	ax3.set_title('Histograma errores absolutos')
	fig3.tight_layout()
	fig3.savefig(os.path.join(out_dir, 'hist_abs_errors.png'))
	plt.close(fig3)


def run_gui(data: List[Dict]):
	if not TK_AVAILABLE:
		print('tkinter no está disponible; modo GUI no habilitado.')
		return
	true_ranges = [d['true_range'] for d in data]
	meas_ranges = [d['measured_range'] for d in data]

	root = tk.Tk()
	root.title('Caída de balas - Análisis de errores')

	fig, ax = plt.subplots(figsize=(6, 4))
	ax.scatter(true_ranges, meas_ranges, color='tab:green')
	ax.plot([min(true_ranges), max(true_ranges)], [min(true_ranges), max(true_ranges)], '--', color='gray')
	ax.set_xlabel('Alcance teórico (m)')
	ax.set_ylabel('Alcance medido (m)')
	ax.set_title('Alcance teórico vs medido')

	canvas = FigureCanvasTkAgg(fig, master=root)
	canvas.draw()
	canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	mean_abs = statistics.mean([d['abs_err'] for d in data])
	txt = f'Error absoluto medio: {mean_abs:.3f} m'
	lbl = tk.Label(root, text=txt)
	lbl.pack(side=tk.BOTTOM, fill=tk.X)

	root.mainloop()


def main(argv):
	random.seed(1)

	# Parámetros de la simulación
	v0 = 200.0  # velocidad inicial m/s (ejemplo)
	true_angle = 30.0  # grados
	sigma_deg = 0.5  # error típico del tirador en grados
	n_shots = 10

	# Generar disparos: el tirador intenta `true_angle` pero comete errores
	shots: List[Dict] = []
	for i in range(n_shots):
		measured_angle = true_angle + random.gauss(0, sigma_deg)
		true_r = range_projectile(v0, true_angle)
		meas_r = range_projectile(v0, measured_angle)
		# Calcular errores según README
		ea = abs(true_r - meas_r)
		er = ea / abs(true_r) if true_r != 0 else float('inf')
		shots.append({
			'shot': i + 1,
			'true_angle': true_angle,
			'measured_angle': measured_angle,
			'true_range': true_r,
			'measured_range': meas_r,
			'abs_err': ea,
			'rel_err': er,
		})

	out_dir = os.path.join(os.path.dirname(__file__), 'output_ej2')
	save_plots(shots, out_dir)

	# Imprimir resumen
	abs_errs = [s['abs_err'] for s in shots]
	rel_errs = [s['rel_err'] for s in shots]
	print('\nResumen Ejemplo 2 - Caída de balas')
	print('--------------------------------')
	print(f'Tiros: {n_shots}')
	print(f'Error absoluto medio: {statistics.mean(abs_errs):.4f} m')
	print(f'Error absoluto máximo: {max(abs_errs):.4f} m')
	print(f'Error relativo medio: {statistics.mean(rel_errs) * 100:.4f} %')
	print('\nTabla de disparos:')
	print('i | ang_true(°) | ang_med(°) | rango_true(m) | rango_med(m) | err_abs(m) | err_rel(%)')
	for s in shots:
		print(f"{s['shot']:2d} | {s['true_angle']:11.3f} | {s['measured_angle']:9.3f} | {s['true_range']:13.3f} | {s['measured_range']:11.3f} | {s['abs_err']:9.3f} | {s['rel_err']*100:9.4f}")

	if '--gui' in argv:
		run_gui(shots)


if __name__ == '__main__':
	main(sys.argv[1:])
