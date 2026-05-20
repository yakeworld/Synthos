#!/usr/bin/env python3
"""Refined Monte Carlo simulation for VOR-Kappa paper."""
import numpy as np
import json

np.random.seed(42)

omega_deg_list = [1, 2, 3, 5, 8, 10, 12, 15]
phi_deg = 30
phi_rad = np.radians(phi_deg)
snr_levels = [30, 25, 20, 15, 10]

N_REPS = 5
N_FRAMES = 600  # 10 seconds at 60 fps

# Theoretical K values
print("=== Theoretical K values (phi=30deg) ===")
for od in omega_deg_list:
    wr = np.radians(od)
    Kx = 1 - (1+np.cos(wr))/2 * np.cos(phi_rad)**2
    Ky = 1 - (1+np.cos(wr))/2 * np.sin(phi_rad)**2
    w_rec = np.degrees(np.arccos(3 - 2*(Kx+Ky)))
    print(f"  omega={od:>2d} deg: Kx={Kx:.6f} Ky={Ky:.6f} recovered={w_rec:.6f}")

print()
print("=== Monte Carlo Results (N=5 per condition) ===")
header = f"{'omega':>5s} {'SNR':>5s} {'mean':>7s} {'std':>7s} {'RMSE':>7s} {'MAE':>7s}"
print(header)
print("-" * len(header))

results = []
for od in omega_deg_list:
    wr = np.radians(od)
    Kx_true = 1 - (1+np.cos(wr))/2 * np.cos(phi_rad)**2
    Ky_true = 1 - (1+np.cos(wr))/2 * np.sin(phi_rad)**2
    
    for snr in snr_levels:
        ests = []
        for rep in range(N_REPS):
            t = np.linspace(0, 10, N_FRAMES)
            theta = 0.5 * np.sin(2*np.pi*1.0*t)  # 30deg amplitude
            
            x = 1 - np.cos(theta)
            
            # Pitch - forward + noise
            y_pitch = Kx_true * x
            noise_p = np.sqrt(np.var(y_pitch) / (10**(snr/10))) * np.random.randn(N_FRAMES)
            Kx_est = np.sum(x * (y_pitch + noise_p)) / np.sum(x**2)
            
            # Yaw - forward + noise
            y_yaw = Ky_true * x
            noise_y = np.sqrt(np.var(y_yaw) / (10**(snr/10))) * np.random.randn(N_FRAMES)
            Ky_est = np.sum(x * (y_yaw + noise_y)) / np.sum(x**2)
            
            # Recover omega
            cw = 3 - 2*(Kx_est + Ky_est)
            cw = np.clip(cw, -1, 1)
            w_est = np.degrees(np.arccos(cw))
            ests.append(w_est)
        
        ests = np.array(ests)
        rmse = float(np.sqrt(np.mean((ests - od)**2)))
        mae = float(np.mean(np.abs(ests - od)))
        
        print(f"{od:>5.0f} {snr:>3d}dB {np.mean(ests):>7.3f} {np.std(ests):>7.4f} {rmse:>7.4f} {mae:>7.4f}")
        
        results.append({
            "omega_true": od,
            "snr": f"{snr}dB",
            "snr_db": snr,
            "mean_est": round(float(np.mean(ests)), 3),
            "std_est": round(float(np.std(ests)), 4),
            "rmse": round(rmse, 4),
            "mae": round(mae, 4)
        })

with open("simulation_stats.json", "w") as f:
    json.dump(results, f, indent=2)

# Summary: accuracy by angle (best SNR)
print("\n=== Best-case accuracy (30dB SNR, clinically realistic) ===")
print(f"{'omega':>5s} {'mean':>7s} {'RMSE':>7s} {'MAE':>7s}")
for res in results:
    if res["snr"] == "30dB":
        print(f"{res['omega_true']:>5d} {res['mean_est']:>7.3f} {res['rmse']:>7.4f} {res['mae']:>7.4f}")

# Summary: average accuracy by SNR
print("\n=== Average accuracy by SNR ===")
for snr in snr_levels:
    snr_res = [r for r in results if r["snr_db"] == snr]
    avg_rmse = np.mean([r["rmse"] for r in snr_res])
    avg_mae = np.mean([r["mae"] for r in snr_res])
    print(f"  {snr:>2d}dB: avg_RMSE={avg_rmse:.4f} deg, avg_MAE={avg_mae:.4f} deg")

print("\nDone. Results saved to simulation_stats.json")
