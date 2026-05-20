#!/usr/bin/env python3
"""
VOR-Kappa Angle Simulation Validation
======================================
Generates synthetic VOR data with known Kappa angle ground truth,
runs the inversion algorithm, and computes accuracy metrics.

For a paper: "Three-dimensional Kappa angle estimation via VOR"
"""

import numpy as np
import json
from sklearn.linear_model import LinearRegression

# ============================================================
# Forward model: given ω, φ, generate eye rotation for head rotation θ
# ============================================================

def deviation_vector(omega, phi):
    """Compute 3D deviation vector D_W."""
    return np.array([
        -np.sin(omega) * np.cos(phi),
        -np.sin(omega) * np.sin(phi),
        1 - np.cos(omega)
    ])

def rodrigues_rotate(D, n, theta):
    """Apply Rodrigues' rotation formula."""
    return (D * np.cos(theta) + 
            np.cross(n, D) * np.sin(theta) + 
            n * np.dot(n, D) * (1 - np.cos(theta)))

def compute_gamma(theta, omega, phi, n):
    """Compute observation angle gamma for given head rotation theta."""
    D_W = deviation_vector(omega, phi)
    D_W_norm2 = np.dot(D_W, D_W)
    D_H = rodrigues_rotate(D_W, n, -theta)  # inverse rotation
    cos_gamma = np.dot(D_W, D_H) / D_W_norm2
    cos_gamma = np.clip(cos_gamma, -1.0, 1.0)
    return np.arccos(cos_gamma)

def simulate_trajectory(omega_true, phi_true, n_axis, 
                         duration=10.0, fps=60, amplitude=np.radians(30),
                         freq=1.0):
    """
    Generate synthetic VOR slow-phase trajectory.
    
    Parameters:
        omega_true: ground truth Kappa angle (radians)
        phi_true: ground truth azimuth (radians)
        n_axis: head rotation axis ([1,0,0] for pitch, [0,1,0] for yaw)
        duration: seconds
        fps: frames per second
        amplitude: max head rotation amplitude (radians)
        freq: head oscillation frequency (Hz)
    
    Returns:
        theta: head rotation angles (n_frames,)
        gamma: observed eye deviation angles (n_frames,)
    """
    t = np.linspace(0, duration, int(duration * fps))
    n_frames = len(t)
    
    # Head rotation: sinusoidal
    theta = amplitude * np.sin(2 * np.pi * freq * t)
    
    # Compute gamma for each frame
    gamma = np.zeros(n_frames)
    for i in range(n_frames):
        gamma[i] = compute_gamma(theta[i], omega_true, phi_true, n_axis)
    
    return theta, gamma, t

def estimate_K(theta, gamma):
    """Estimate K coefficient via linear regression through origin.
    
    Fits: 1 - cos(gamma) = K * (1 - cos(theta))
    """
    x = 1 - np.cos(theta)
    y = 1 - np.cos(gamma)
    
    # Filter out invalid values
    valid = np.isfinite(x) & np.isfinite(y)
    x_fit = x[valid].reshape(-1, 1)
    y_fit = y[valid]
    
    if len(x_fit) < 3:
        return 0.0, 0.0
    
    # Regression through origin
    model = LinearRegression(fit_intercept=False)
    model.fit(x_fit, y_fit)
    K = model.coef_[0]
    r2 = model.score(x_fit, y_fit)
    
    return K, r2

def estimate_kappa_from_trajectories(theta_pitch, gamma_pitch, 
                                      theta_yaw, gamma_yaw):
    """Estimate 3D Kappa angle from pitch and yaw trajectories."""
    Kx, r2x = estimate_K(theta_pitch, gamma_pitch)
    Ky, r2y = estimate_K(theta_yaw, gamma_yaw)
    
    # Closed-form solution
    cos_omega = 3 - 2 * (Kx + Ky)
    cos_omega = np.clip(cos_omega, -1.0, 1.0)
    omega_est = np.arccos(cos_omega)
    
    # Azimuth
    sqrt_1_Ky = np.sqrt(max(1 - Ky, 0))
    sqrt_1_Kx = np.sqrt(max(1 - Kx, 0))
    phi_est = np.arctan2(sqrt_1_Ky, sqrt_1_Kx) if sqrt_1_Kx > 0 else 0.0
    
    return omega_est, phi_est, Kx, Ky, r2x, r2y

def add_noise(gamma, snr_db):
    """Add Gaussian noise to gamma signal at specified SNR."""
    if snr_db == np.inf:
        return gamma
    signal_power = np.var(gamma)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(len(gamma))
    return gamma + noise

# ============================================================
# Main simulation experiment
# ============================================================

def run_experiment():
    np.random.seed(42)
    
    # Kappa angles to test (degrees) - covers clinical range
    omega_deg_list = [0.5, 1, 2, 3, 5, 8, 10, 12, 15]
    phi_deg = 30  # fixed azimuth for main experiment
    phi_rad = np.radians(phi_deg)
    
    # Noise levels
    snr_levels = [np.inf, 30, 25, 20, 15]
    snr_labels = {np.inf: "∞", 30: "30dB", 25: "25dB", 20: "20dB", 15: "15dB"}
    
    # Rotation axes
    n_x = np.array([1.0, 0.0, 0.0])  # pitch (nodding)
    n_y = np.array([0.0, 1.0, 0.0])  # yaw (shaking)
    
    results = []
    
    for omega_deg in omega_deg_list:
        omega_true = np.radians(omega_deg)
        
        for snr in snr_levels:
            # Generate pitch trajectory
            theta_pitch, gamma_pitch_true, _ = simulate_trajectory(
                omega_true, phi_rad, n_x)
            gamma_pitch = add_noise(gamma_pitch_true, snr)
            
            # Generate yaw trajectory
            theta_yaw, gamma_yaw_true, _ = simulate_trajectory(
                omega_true, phi_rad, n_y)
            gamma_yaw = add_noise(gamma_yaw_true, snr)
            
            # Estimate
            omega_est, phi_est, Kx, Ky, r2x, r2y = \
                estimate_kappa_from_trajectories(
                    theta_pitch, gamma_pitch, theta_yaw, gamma_yaw)
            
            omega_est_deg = np.degrees(omega_est)
            phi_est_deg = np.degrees(phi_est)
            error = abs(omega_est_deg - omega_deg)
            
            results.append({
                'omega_true_deg': omega_deg,
                'omega_est_deg': round(omega_est_deg, 4),
                'phi_true_deg': phi_deg,
                'phi_est_deg': round(phi_est_deg, 2),
                'snr': snr_labels[snr],
                'snr_db': snr,
                'error_deg': round(error, 4),
                'Kx': round(Kx, 6),
                'Ky': round(Ky, 6),
                'R2x': round(r2x, 4),
                'R2y': round(r2y, 4)
            })
            
            print(f"ω_true={omega_deg:>5.1f}°  SNR={snr_labels[snr]:>5s}  "
                  f"ω_est={omega_est_deg:>6.2f}°  error={error:>6.3f}°  "
                  f"φ_est={phi_est_deg:>5.1f}°  "
                  f"Kx={Kx:.4f}  Ky={Ky:.4f}  R²x={r2x:.3f}  R²y={r2y:.3f}")
    
    # Summary statistics
    print("\n=== Summary by ω_true (averaged across SNR) ===")
    for omega_deg in omega_deg_list:
        om_results = [r for r in results if r['omega_true_deg'] == omega_deg]
        errors = [r['error_deg'] for r in om_results]
        mean_err = np.mean(errors)
        max_err = np.max(errors)
        
        # No-noise result
        clean = [r for r in om_results if r['snr_db'] == np.inf][0]
        
        print(f"ω={omega_deg:>4.1f}° | clean:{clean['error_deg']:.4f}° | "
              f"mean:{mean_err:.4f}° | max:{max_err:.4f}°")
    
    # Show φ estimation
    print(f"\n=== φ estimation (true φ = {phi_deg}°) ===")
    for r in results:
        print(f"  ω={r['omega_true_deg']:>4.1f}°  SNR={r['snr']:>5s}  "
              f"φ_est={r['phi_est_deg']:>5.1f}°")
    
    return results

if __name__ == '__main__':
    results = run_experiment()
    
    # Save results
    with open('simulation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to simulation_results.json ({len(results)} data points)")
