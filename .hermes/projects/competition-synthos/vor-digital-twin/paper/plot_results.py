#!/usr/bin/env python3
"""Generate RMSE plot for VOR-Kappa paper."""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

with open('simulation_stats.json') as f:
    data = json.load(f)

# Nature-style colors
nat_blue = '#0072B2'
nat_green = '#009E73'
nat_orange = '#E69F00'
nat_pink = '#CC79A7'
nat_brown = '#D55E00'

# Organize by SNR
snr_order = [30, 25, 20, 15, 10]
snr_colors = [nat_blue, nat_green, nat_orange, nat_pink, nat_brown]
omega_vals = sorted(set(r['omega_true'] for r in data))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# Left: RMSE vs omega for different SNR levels
for snr, color in zip(snr_order, snr_colors):
    snr_data = [r for r in data if r['snr_db'] == snr]
    snr_data.sort(key=lambda x: x['omega_true'])
    x = [r['omega_true'] for r in snr_data]
    y = [r['rmse'] for r in snr_data]
    ax1.plot(x, y, 'o-', color=color, linewidth=1.5, markersize=4, label=f'{snr} dB')

ax1.set_xlabel('True Kappa Angle $\omega$ (deg)', fontsize=11)
ax1.set_ylabel('RMSE (deg)', fontsize=11)
ax1.legend(fontsize=8, loc='upper left')
ax1.set_xlim(0, 16)
ax1.set_ylim(0, 7)
ax1.grid(True, alpha=0.3)
ax1.set_title('(a) Estimation accuracy by SNR', fontsize=11)

# Right: Bias (mean error) for 30dB SNR
bias_data = [r for r in data if r['snr_db'] == 30]
bias_data.sort(key=lambda x: x['omega_true'])
x_bias = [r['omega_true'] for r in bias_data]
y_bias = [r['mean_est'] - r['omega_true'] for r in bias_data]

ax2.bar(x_bias, y_bias, width=0.8, color=nat_blue, alpha=0.8, edgecolor='white')
ax2.axhline(y=0, color='black', linewidth=0.5)
ax2.set_xlabel('True Kappa Angle $\omega$ (deg)', fontsize=11)
ax2.set_ylabel('Bias $\hat{\omega} - \omega$ (deg)', fontsize=11)
ax2.set_xticks(omega_vals)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_title('(b) Estimation bias at 30 dB SNR', fontsize=11)

plt.tight_layout()
plt.savefig('fig_simulation_results.pdf', bbox_inches='tight', dpi=300)
print("Saved fig_simulation_results.pdf")
print(f"Size: {10}x4 inches")

# Print table for LaTeX insertion
print("\n=== LaTeX Table 1 data ===")
print(r"\begin{table}[t]")
print(r"\caption{Simulation validation of VOR-based 3D Kappa angle estimation.}")
print(r"\label{tab:simulation}")
print(r"\centering")
print(r"\small")
print(r"\begin{tabular}{lcccc}")
print(r"\toprule")
print(r"$\omega_{\text{true}}$ & SNR & $\hat{\omega}$ (mean$\pm$SD) & RMSE & MAE \\")
print(r"\midrule")
for od in omega_vals:
    for snr in [30, 25, 20, 15]:
        r_data = [r for r in data if r['omega_true'] == od and r['snr_db'] == snr]
        if r_data:
            r = r_data[0]
            mean_mae = r['mae']
            mean_rmse = r['rmse']
            print(f"{od}$^\circ$ & {snr}\,dB & ${r['mean_est']:.2f}\pm{r['std_est']:.2f}$ & {mean_rmse:.3f}$^\circ$ & {mean_mae:.3f}$^\circ$ \\\\")
    print(r"\addlinespace")
print(r"\bottomrule")
print(r"\end{tabular}")
print(r"\end{table}")
