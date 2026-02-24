
"""
Ejemplo práctico: análisis de errores en artillería (puntería).

Descripción:
- Se genera un conjunto de observaciones (ángulo real vs ángulo disparado)
- Se calculan error absoluto y error relativo según el README
- Se guardan gráficos con matplotlib y (opcional) se muestra una GUI con tkinter

"""

import os
import sys
import math
import random
import statistics
from typing import List, Tuple

import matplotlib
matplotlib.use('Agg')  # por defecto generar archivos (no bloquear)
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


def save_plots(true_vals: List[float], approx_vals: List[float], abs_errs: List[float], out_dir: str):
	os.makedirs(out_dir, exist_ok=True)

	# Scatter: verdadero vs aproximado
	fig1, ax1 = plt.subplots(figsize=(6, 4))
	ax1.scatter(true_vals, approx_vals, color='tab:blue')
	ax1.plot([min(true_vals), max(true_vals)], [min(true_vals), max(true_vals)], '--', color='gray')
	ax1.set_xlabel('Ángulo verdadero (°)')
	ax1.set_ylabel('Ángulo disparado (°)')
	ax1.set_title('Ángulo verdadero vs Ángulo disparado')
	fig1.tight_layout()
	fig1.savefig(os.path.join(out_dir, 'scatter_true_vs_approx.png'))
	plt.close(fig1)

	# Error por tiro
	fig2, ax2 = plt.subplots(figsize=(6, 3))
	ax2.plot(range(1, len(abs_errs) + 1), abs_errs, marker='o')
	ax2.set_xlabel('Disparo #')
	ax2.set_ylabel('Error absoluto (°)')
	ax2.set_title('Error absoluto por disparo')
	fig2.tight_layout()
	fig2.savefig(os.path.join(out_dir, 'error_by_shot.png'))
	plt.close(fig2)

	# Histograma de errores
	fig3, ax3 = plt.subplots(figsize=(6, 3))
	ax3.hist(abs_errs, bins=8, color='tab:orange', edgecolor='black')
	ax3.set_xlabel('Error absoluto (°)')
	ax3.set_ylabel('Frecuencia')
	ax3.set_title('Histograma de errores absolutos')
	fig3.tight_layout()
	fig3.savefig(os.path.join(out_dir, 'hist_errors.png'))
	plt.close(fig3)


def print_summary(true_vals: List[float], approx_vals: List[float], abs_errs: List[float], rel_errs: List[float]):
	print('\nResumen de errores:')
	print('-------------------')
	print(f'Tiros totales: {len(true_vals)}')
	print(f'Error absoluto medio: {statistics.mean(abs_errs):.4f} °')
	print(f'Error absoluto máximo: {max(abs_errs):.4f} °')
	print(f'Error relativo medio: {statistics.mean(rel_errs) * 100:.4f} %')
	print('\nTabla (primeras 12 filas):')
	print('i | verdadero(°) | disparado(°) | err_abs(°) | err_rel(%)')
	for i, (t, a, ea, er) in enumerate(zip(true_vals, approx_vals, abs_errs, rel_errs), start=1):
		print(f'{i:2d} | {t:12.4f} | {a:12.4f} | {ea:9.4f} | {er*100:9.4f}')


def run_gui(true_vals: List[float], approx_vals: List[float], abs_errs: List[float]):
	if not TK_AVAILABLE:
		print('tkinter no está disponible en este entorno; no se puede abrir GUI.')
		return

	root = tk.Tk()
	root.title('Análisis de errores - Artillería')

	fig, ax = plt.subplots(figsize=(6, 4))
	ax.scatter(true_vals, approx_vals, color='tab:blue')
	ax.plot([min(true_vals), max(true_vals)], [min(true_vals), max(true_vals)], '--', color='gray')
	ax.set_xlabel('Ángulo verdadero (°)')
	ax.set_ylabel('Ángulo disparado (°)')
	ax.set_title('Ángulo verdadero vs Ángulo disparado')

	canvas = FigureCanvasTkAgg(fig, master=root)
	canvas.draw()
	canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

	stats_txt = f'Errores absol. medios: {statistics.mean(abs_errs):.4f} °\nMax: {max(abs_errs):.4f} °'
	label = tk.Label(root, text=stats_txt, justify=tk.LEFT)
	label.pack(side=tk.BOTTOM, fill=tk.X)

	root.mainloop()


def main(argv):
	random.seed(42)

	# Dataset: ángulos verdaderos (°) hacia el blanco y disparos del artillero
	# (Se usan 12 datos para observación)
	true_angles = [45.0, 46.0, 44.5, 45.2, 45.8, 44.9, 46.4, 45.1, 45.5, 44.7, 46.2, 45.3]

	# Simular mediciones/disparos con errores del tirador (determinístico por seed)
	# Aquí el error simulado en grados (ruido gaussiano con sigma=1.2°) + un sesgo pequeño
	sigma = 1.2
	bias = 0.3
	approx_angles = [t + bias + random.gauss(0, sigma) for t in true_angles]

	abs_errs, rel_errs = compute_errors(true_angles, approx_angles)

	out_dir = os.path.join(os.path.dirname(__file__), 'output')
	save_plots(true_angles, approx_angles, abs_errs, out_dir)

	print_summary(true_angles, approx_angles, abs_errs, rel_errs)

	# Modo GUI opcional
	if '--gui' in argv:
		run_gui(true_angles, approx_angles, abs_errs)


if __name__ == '__main__':
	main(sys.argv[1:])
