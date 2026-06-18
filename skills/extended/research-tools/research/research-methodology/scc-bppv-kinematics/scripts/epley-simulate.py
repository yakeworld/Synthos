"""Epley Maneuver Kinematic Simulation for SCC Morphology Analysis

Usage:
    python scripts/epley-simulate.py [--specimen DIR] [--canal CANAL]

Given a log-spiral parameter set (a, b, A, ω, φ) or a .mrk.json centerline,
simulate the gravity-driven otoconia displacement during a standard Epley maneuver.

Returns: total travel distance, position-by-position breakdown
"""
import json, os, math, sys
import numpy as np
from scipy.optimize import minimize

def nearest_neighbor_path(pts):
    n = len(pts); visited=[False]*n; path=[0]; visited[0]=True; current=0
    while len(path) < n:
        dists = [np.linalg.norm(pts[current]-pts[j]) if not visited[j] else float('inf') for j in range(n)]
        nearest = np.argmin(dists)
        path.append(nearest); visited[nearest]=True; current=nearest
    return path

def load_pts(path):
    with open(path) as f:
        d = json.load(f)
    return np.array([p['position'] for p in d['markups'][0]['controlPoints']])

def get_maneuver_positions():
    """Returns list of 5 rotation matrices [P0..P4] for right-ear Epley maneuver"""
    yaw_45 = np.array([[math.cos(math.pi/4), -math.sin(math.pi/4), 0],
                       [math.sin(math.pi/4),  math.cos(math.pi/4), 0],
                       [0, 0, 1]])
    pitch = -105 * math.pi / 180
    R_pitch = np.array([[math.cos(pitch), 0, math.sin(pitch)],
                        [0, 1, 0],
                        [-math.sin(pitch), 0, math.cos(pitch)]])
    P2 = R_pitch @ yaw_45
    yaw_m90 = np.array([[math.cos(-math.pi/2), -math.sin(-math.pi/2), 0],
                        [math.sin(-math.pi/2),  math.cos(-math.pi/2), 0],
                        [0, 0, 1]])
    P3 = yaw_m90 @ P2
    roll_m90 = np.array([[1, 0, 0],
                         [0, math.cos(-math.pi/2), -math.sin(-math.pi/2)],
                         [0, math.sin(-math.pi/2),  math.cos(-math.pi/2)]])
    P4 = roll_m90 @ P3
    return [np.eye(3), yaw_45, P2, P3, P4]

def simulate_on_centerline(pts, maneuver_positions):
    """Compute otoconia displacement on a given centerline during maneuver"""
    path = nearest_neighbor_path(pts)
    pts_path = pts[path]
    ds = np.sqrt(np.sum(np.diff(pts_path, axis=0)**2, axis=1))
    tangents = np.diff(pts_path, axis=0) / ds[:, np.newaxis]
    
    g_world = np.array([0, 0, -1])
    total_travel = 0
    pos_breakdown = []
    
    for R in maneuver_positions:
        g_head = R.T @ g_world
        g_tang = np.sum(g_head[np.newaxis, :] * tangents, axis=1)
        travel = np.sum(ds * g_tang)
        total_travel += abs(travel)
        pos_breakdown.append(travel)
    
    return total_travel, np.array(pos_breakdown)

def simulate_on_logspiral(a, b, A_s, om_s, ph_s, centroid, u, v, normal, 
                          theta_min, theta_max, n_pts=200, maneuver_positions=None):
    """Compute displacement on a log-spiral generated centerline"""
    t = np.linspace(theta_min, theta_max, n_pts)
    r = a * np.exp(b * t)
    cx, cy, rot = 0, 0, 0  # note: actual cx/cy/rot shift doesn't affect tangent direction
    cr = cx + r * np.cos(t + rot)
    cy_fit = cy + r * np.sin(t + rot)
    curve = centroid + cr[:,np.newaxis]*u + cy_fit[:,np.newaxis]*v + \
            (A_s*np.sin(om_s*t+ph_s))[:,np.newaxis]*normal
    
    if maneuver_positions is None:
        maneuver_positions = get_maneuver_positions()
    
    return simulate_on_centerline(curve, maneuver_positions)

def monte_carlo_population(canal, n_sim=10000):
    """Run Monte Carlo using 160-CT population parameters
    
    Args:
        canal: 'AC', 'PC', or 'LC'
        n_sim: number of simulations
        
    Returns:
        travel_distances, b_values, statistics dict
    """
    POPULATION = {
        'AC': {'b_mean': 0.096, 'b_sd': 0.039, 'b_range': [0.0002, 0.147],
               'normal': [0.767, 0.626, 0.141], 'arc': 13.0},
        'PC': {'b_mean': 0.032, 'b_sd': 0.039, 'b_range': [0.0002, 0.158],
               'normal': [0.629, -0.700, -0.338], 'arc': 14.5},
        'LC': {'b_mean': 0.048, 'b_sd': 0.043, 'b_range': [0.0003, 0.155],
               'normal': [-0.021, 0.333, -0.943], 'arc': 12.0},
    }
    pop = POPULATION.get(canal)
    if not pop:
        raise ValueError(f"Unknown canal: {canal}")
    
    np.random.seed(42)
    b_samples = np.random.normal(pop['b_mean'], pop['b_sd'], n_sim)
    b_samples = np.clip(np.abs(b_samples), pop['b_range'][0], pop['b_range'][1])
    
    normal = np.array(pop['normal'])
    normal = normal / np.linalg.norm(normal)
    mean_arc = pop['arc']
    
    # Scale factor: canonical radius ~3.5mm
    a_mean = 3.5
    
    # Generate basis
    ref = np.array([1,0,0]) if abs(normal@[1,0,0])<0.9 else np.array([0,1,0])
    u = np.cross(normal, ref); u /= np.linalg.norm(u)
    v = np.cross(normal, u)
    
    centroid = np.array([0, 0, 0])
    theta_range = [0, 2*math.pi]  # approximately one full turn
    
    maneuvers = get_maneuver_positions()
    travels = np.zeros(n_sim)
    
    for i, b in enumerate(b_samples):
        t, d = simulate_on_logspiral(a_mean, b, 0.15, 2.0, 0, centroid, u, v, normal,
                                      theta_range[0], theta_range[1],
                                      n_pts=100, maneuver_positions=maneuvers)
        travels[i] = t
    
    return {
        'canal': canal,
        'n_sim': n_sim,
        'b': b_samples,
        'travels': travels,
        'mean_travel': np.mean(travels),
        'std_travel': np.std(travels),
        'p5_travel': np.percentile(travels, 5),
        'p95_travel': np.percentile(travels, 95),
        'range_travel': np.ptp(travels),
    }

if __name__ == '__main__':
    # Demo: Monte Carlo for all 3 canals
    print("Epley Maneuver Kinematic Simulation")
    print("=" * 50)
    for canal in ['AC', 'PC', 'LC']:
        stats = monte_carlo_population(canal, n_sim=5000)
        print(f"\n{canal}:")
        print(f"  Mean travel: {stats['mean_travel']:.3f}mm")
        print(f"  P5-P95:      [{stats['p5_travel']:.3f}, {stats['p95_travel']:.3f}]mm")
        print(f"  Range:       {stats['range_travel']:.3f}mm")
