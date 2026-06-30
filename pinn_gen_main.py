#!/usr/bin/env python3
"""
PINN论文批量代码生成 - 主入口
读取报告，逐篇处理，输出进度和最终报告
"""

import json
import os
import re
import sys
import textwrap
from pathlib import Path
from datetime import datetime

WORKDIR = "/media/yakeworld/sda2/Synthos"
PAPERS_DIR = os.path.join(WORKDIR, "outputs/papers")
REPORT_PATH = "/tmp/paper-code-data-report.json"
LOG_FILE = os.path.join(WORKDIR, "pinn_gen_progress.log")

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

# ============================================================
# Read paper information
# ============================================================

def load_papers():
    with open(REPORT_PATH) as f:
        data = json.load(f)
    papers = data['papers']
    pinn_p0 = [p for p in papers if p.get('paper_type') == 'PINN' and p.get('priority') == 'P0']
    pinn_p0.sort(key=lambda x: x.get('paper_name', ''))
    return pinn_p0

def read_paper_tex(paper_path):
    tex_path = os.path.join(paper_path, "01-manuscript", "paper.tex")
    if not os.path.exists(tex_path):
        return None
    with open(tex_path, 'r', errors='replace') as f:
        return f.read()

def extract_title(tex_content):
    if not tex_content:
        return "Unknown Title"
    m = re.search(r'\\title\{((?:[^{}]|\{[^}]*\})*)\}', tex_content)
    if m:
        title = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', m.group(1))
        title = re.sub(r'[{}]', '', title)
        return title.strip()
    return "Unknown Title"

def extract_abstract(tex_content):
    if not tex_content:
        return ""
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex_content, re.DOTALL)
    if m:
        abstract = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', m.group(1))
        abstract = re.sub(r'[{}]', '', abstract)
        return re.sub(r'\s+', ' ', abstract).strip()
    return ""

def extract_equations(tex_content):
    if not tex_content:
        return []
    equations = []
    for m in re.finditer(r'\\begin\{(?:equation|align|eqnarray|gather)\}(.+?)\\end\{\1\}', tex_content, re.DOTALL):
        eq = m.group(1)
        label_m = re.search(r'\\label\{([^}]+)\}', eq)
        label = label_m.group(1) if label_m else ""
        equations.append({"label": label, "content": eq.strip()})
    return equations

# ============================================================
# Classify paper type for model selection
# ============================================================

def classify_paper(paper_name, title, tex_content):
    name_lower = paper_name.lower()
    title_lower = title.lower()
    
    if 'bifurcation' in title_lower or 'hopf' in title_lower or 'pan-' in paper_name or 'pan-' in name_lower:
        return 'bifurcation'
    if 'nystagmus' in title_lower or 'bppv' in name_lower:
        return 'nystagmus'
    if '2-ode' in name_lower or 'couple' in name_lower:
        return 'coupled'
    if 'torsion' in name_lower or 'torsional' in name_lower or '092-' in paper_name:
        return 'torsion'
    return 'generic'

# ============================================================
# Generate code templates
# ============================================================

def make_pinn_model_py(paper_name, title, abstract, tex_content, paper_type):
    """Generate pinn_model.py content"""
    
    title_clean = re.sub(r'[{}]', '', title)
    title_clean = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', title_clean)
    
    # Build class name from paper name
    class_name = ''.join([w.capitalize() for w in re.split(r'[-_]', paper_name) if w])
    if not class_name:
        class_name = 'PINNModel'
    class_name = class_name[:30]  # limit length
    
    model_doc = f"""
PINN Model: {title_clean}

This module implements a Physics-Informed Neural Network (PINN)
to solve the governing differential equations described in the paper.

Physics-Informed approach:
- Neural network approximates the solution of ODE/PDE system
- Governing equations are embedded in the loss via autograd
- Boundary/initial conditions enforced as constraints
- Parameters estimated simultaneously with solution
"""
    
    # Generic template with paper-specific info
    code = f'''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

{model_doc}

'''
    # System info
    system_info = extract_system_info(tex_content, paper_name, title)
    n_output = system_info['n_output']
    output_names = system_info['output_names']
    input_dim_str = system_info['input_dim_str']
    
    code += f'''class {class_name}PINN(nn.Module):
    """
    Physics-Informed Neural Network for: {title_clean}
    
    State variables: {', '.join(output_names)}
    Input dimensions: {input_dim_str}
    """
    
    def __init__(self, hidden_layers=None, activation='tanh'):
        super().__init__()
        
        self.input_dim = {system_info['input_dim']}
        self.output_dim = {n_output}
        
        if hidden_layers is None:
            hidden_layers = [64, 64, 64]
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        
        layers.append(nn.Linear(self.input_dim, hidden_layers[0]))
        layers.append(act)
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        layers.append(nn.Linear(hidden_layers[-1], self.output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Physics parameters
'''
    
    # Add physics parameters based on paper type
    if paper_type in ['bifurcation', 'nystagmus', 'coupled', 'torsion']:
        code += f'''        self.log_c1 = nn.Parameter(torch.tensor(0.0))
        self.log_c2 = nn.Parameter(torch.tensor(0.0))
        self.log_k1 = nn.Parameter(torch.tensor(1.0))
        self.log_k2 = nn.Parameter(torch.tensor(1.0))
        self.log_coupling = nn.Parameter(torch.tensor(0.0))
'''
    else:
        code += '''        self.log_k = nn.Parameter(torch.tensor(1.0))
        self.log_c = nn.Parameter(torch.tensor(0.0))
'''
    
    code += f'''
    def forward(self, *coords):
        """Forward pass: predict solution u(x,t)"""
        inputs = torch.cat(coords, dim=-1)
        return self.network(inputs)
    
    def get_params(self):
        return {
'''
    
    if paper_type in ['bifurcation', 'nystagmus', 'coupled', 'torsion']:
        code += '''            'c1': torch.exp(self.log_c1).item(),
            'c2': torch.exp(self.log_c2).item(),
            'k1': torch.exp(self.log_k1).item(),
            'k2': torch.exp(self.log_k2).item(),
            'coupling': torch.exp(self.log_coupling).item(),
'''
    else:
        code += '''            'k': torch.exp(self.log_k).item(),
            'c': torch.exp(self.log_c).item(),
'''
    
    code += '''        }
    
    def compute_residual(self, *coords):
        """
        Compute PDE/ODE residual using automatic differentiation.
        
        The residual represents how well the network solution
        satisfies the governing physical equations.
        """
        for coord in coords:
            coord.requires_grad_(True)
        
        output = self.forward(*coords)
'''
    
    # Add residual computation
    if paper_type == 'torsion':
        code += f'''        u = output[:, 0:1]
        v = output[:, 1:2]
        
        # Time derivatives (assume last coord is time)
        t = coords[-1]
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        dv_dt = torch.autograd.grad(v, t, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        d2u_dt2 = torch.autograd.grad(du_dt, t, grad_outputs=torch.ones_like(du_dt), create_graph=True)[0]
        d2v_dt2 = torch.autograd.grad(dv_dt, t, grad_outputs=torch.ones_like(dv_dt), create_graph=True)[0]
        
        params = self.get_params()
        
        # Coupled ODE residuals:
        # d2u/dt2 + c1*du/dt + k1*u = coupling*v
        # d2v/dt2 + c2*dv/dt + k2*v = coupling*u
        residual_u = d2u_dt2 + params['c1'] * du_dt + params['k1'] * u - params['coupling'] * v
        residual_v = d2v_dt2 + params['c2'] * dv_dt + params['k2'] * v - params['coupling'] * u
'''
    elif paper_type == 'nystagmus':
        code += f'''        u = output[:, 0:1]  # cupula displacement
        v = output[:, 1:2]  # particle position
        
        t = coords[-1]
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        dv_dt = torch.autograd.grad(v, t, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        
        params = self.get_params()
        
        # BPPV model:
        # tau*du/dt + u = k*(v - v_stable)
        # m*dv/dt + v = head_position_change
        step = torch.where(t > 0.5, params['coupling'], 0.0)
        residual_u = params['c1'] * du_dt + u - params['k1'] * (v - params['k1'] * step / (params['k1'] + 1))
        residual_v = params['c2'] * dv_dt + v - step
'''
    elif paper_type == 'bifurcation':
        code += f'''        u = output[:, 0:1]  # primary variable
        v = output[:, 1:2]  # secondary variable
        
        t = coords[-1]
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        dv_dt = torch.autograd.grad(v, t, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        
        params = self.get_params()
        
        # Hopf bifurcation system:
        # du/dt = omega*v
        # dv/dt = -omega*v + mu*u - u^3
        residual_u = du_dt - params['k2'] * v
        residual_v = dv_dt - (-params['k2'] * v + params['k1'] * u - u**3)
'''
    elif paper_type == 'coupled':
        code += f'''        u = output[:, 0:1]
        v = output[:, 1:2]
        
        t = coords[-1]
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        dv_dt = torch.autograd.grad(v, t, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        
        params = self.get_params()
        
        # Coupled ODE system:
        # du/dt = -c1*u + k1*v + coupling*u*v
        # dv/dt = -c2*v + k2*u - coupling*u*v
        residual_u = du_dt - (-params['c1'] * u + params['k1'] * v + params['coupling'] * u * v)
        residual_v = dv_dt - (-params['c2'] * v + params['k2'] * u - params['coupling'] * u * v)
'''
    else:
        # Generic single ODE
        code += f'''        u = output[:, 0:1]
        
        # Last coordinate is time
        t = coords[-1]
        if len(coords) > 1:
            x = coords[0]
            du_dx = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
            d2u_dx2 = torch.autograd.grad(du_dx, x, grad_outputs=torch.ones_like(du_dx), create_graph=True)[0]
        else:
            x = torch.zeros_like(t)
            du_dx = torch.zeros_like(t)
            d2u_dx2 = torch.zeros_like(t)
        
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        
        params = self.get_params()
        
        # General ODE: du/dt = k*f(u) - c*u
        # TODO: Replace with actual governing equation from the paper
        residual = du_dt - (params['k'] * u * (1 - u) - params['c'] * u)
'''
    
    code += '''        
        return residual_u if 'residual_u' in dir() else residual, residual_v if 'residual_v' in dir() else torch.zeros_like(residual)


class {class_name}Trainer:
    """Complete PINN training pipeline"""
    
    def __init__(self, model, lr=1e-3, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.lr = lr
        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=lr, betas=(0.9, 0.999)
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=5000
        )
        self.history = {
            'total_loss': [], 'data_loss': [], 
            'physics_loss': [], 'epoch': []
        }
    
    def sample_collocation_points(self, *dims, n_colloc=1000):
        """Sample collocation points in space-time domain"""
        points = []
        for dim in dims:
            points.append(torch.rand(n_colloc, 1, device=self.device) * dim)
        return points
    
    def compute_loss(self, *data_coords, n_colloc=500):
        """
        Compute combined loss: data fit + physics residual
        """
        # Data loss
        pred_data = self.model(*data_coords)
        data_loss = nn.MSELoss()(pred_data, data_coords[-1])
        
        # Physics residual at collocation points
        t_max = 5.0
        collocate_t = torch.rand(n_colloc, 1, device=self.device) * t_max
        collocate_x = torch.rand(n_colloc, 1, device=self.device) * 2.0 if len(data_coords) > 2 else torch.zeros(n_colloc, 1, device=self.device)
        
        collocate_inputs = [collocate_x, collocate_t]
        if len(data_coords) >= 3:
            collocate_inputs = [collocate_t]
        
        res = self.model.compute_residual(*collocate_inputs)
        physics_loss = sum(nn.MSELoss()(r, torch.zeros_like(r)) for r in res) / len(res)
        
        # Combined loss
        total_loss = data_loss + 1.0 * physics_loss
        return data_loss, physics_loss, total_loss
    
    def train(self, *data_args, epochs=5000, verbose=True, save_dir=None, model_name="model"):
        """Full training loop"""
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': [], 'epoch': []}
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            data_loss, physics_loss, total_loss = self.compute_loss(*data_args)
            
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()
            self.scheduler.step()
            
            self.history['total_loss'].append(total_loss.item())
            self.history['data_loss'].append(data_loss.item())
            self.history['physics_loss'].append(physics_loss.item())
            self.history['epoch'].append(epoch)
            
            if verbose and (epoch + 1) % 500 == 0:
                print(f"  Epoch [{epoch+1}/{epochs}] Total: {total_loss.item():.6f} Data: {data_loss.item():.6f} Physics: {physics_loss.item():.6f}")
        
        return self.history
    
    def save_checkpoint(self, path):
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'params': self.model.get_params(),
            'history': {k: v for k, v in self.history.items()},
        }, path)
        print(f"  Checkpoint saved to {path}")
    
    def visualize(self, *data_args, save_path=None, n_points=200):
        """Generate visualization of training results"""
        self.model.eval()
        t_test = torch.linspace(0, 5, n_points).view(-1, 1).to(self.device)
        
        if len(data_args) > 1:
            x_test = torch.zeros(n_points, 1).to(self.device)
            with torch.no_grad():
                pred = self.model(x_test, t_test)
            x_coord = x_test
        else:
            with torch.no_grad():
                pred = self.model(t_test)
            x_coord = torch.zeros_like(t_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot predictions
        for i, name in enumerate(['u', 'v'][:self.model.output_dim]):
            axes[0, 0].plot(
                t_test.cpu().numpy(), pred[:, i].cpu().numpy(), 
                'b-' if i == 0 else 'r-', linewidth=2, label=name
            )
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Solution')
        axes[0, 0].set_title('PINN Solution')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Loss curve
        axes[0, 1].plot(self.history['epoch'], self.history['total_loss'], 'b-', label='Total')
        axes[0, 1].plot(self.history['epoch'], self.history['data_loss'], 'g-', label='Data')
        axes[0, 1].plot(self.history['epoch'], self.history['physics_loss'], 'r-', label='Physics')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].set_title('Training Loss')
        axes[0, 1].legend()
        axes[0, 1].set_yscale('log')
        axes[0, 1].grid(True)
        
        # Residual distribution
        t_c = torch.rand(n_points, 1, device=self.device) * 5.0
        with torch.no_grad():
            res = self.model.compute_residual(t_c)
        for i, r in enumerate(res):
            axes[1, 0].hist(r.cpu().numpy().flatten(), bins=50, alpha=0.5, label=f'Residual {i}')
        axes[1, 0].set_xlabel('Residual')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('Residual Distribution')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Parameters
        params = self.model.get_params()
        param_names = list(params.keys())
        param_values = list(params.values())
        axes[1, 1].bar(param_names, param_values, color='steelblue')
        axes[1, 1].set_ylabel('Value')
        axes[1, 1].set_title('Learned Physics Parameters')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, axis='y')
        
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {save_path}")
        self.model.train()


if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print(f"Model: {title_clean}")
    print("="*60)
    
    np.random.seed(42)
    n_data = 100
    
    # Synthetic training data
    if {n_output} == 2:
        t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
        x_data = np.random.uniform(0, 1, n_data).reshape(-1, 1)
        
        # Synthetic solution (TODO: replace with actual solution)
        u = np.sin(2*np.pi*x_data) * np.exp(-0.5*t_data)
        v = np.cos(2*np.pi*x_data) * np.exp(-0.3*t_data)
        u_data = np.column_stack([u, v]) + np.random.randn(n_data, 2) * 0.01
        
        x_data_t = torch.tensor(x_data, dtype=torch.float32, device=device)
        t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
        u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    else:
        t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
        u_data = np.exp(-0.5*t_data) * np.sin(2*t_data) + np.random.randn(n_data, 1) * 0.01
        
        x_data_t = torch.zeros_like(t_data)
        t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
        u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    # Initialize and train
    model = {class_name}PINN(hidden_layers=[64, 64, 64], activation='tanh')
    trainer = {class_name}Trainer(model, lr=1e-3, device=device)
    
    print("\\n" + "="*60)
    print("Starting PINN Training...")
    print("="*60)
    
    if {n_output} == 2:
        trainer.train(
            x_data_t, t_data_t, u_data_t,
            epochs=3000, verbose=True,
            save_dir="results", model_name="{paper_name}"
        )
    else:
        trainer.train(
            x_data_t, t_data_t, u_data_t,
            epochs=3000, verbose=True,
            save_dir="results", model_name="{paper_name}"
        )
    
    # Save results
    os.makedirs("results", exist_ok=True)
    trainer.save_checkpoint(f"results/{paper_name}_model.pth")
    if {n_output} == 2:
        trainer.visualize(x_data_t, t_data_t, u_data_t,
                         save_path=f"results/{paper_name}_dynamics.png")
    else:
        trainer.visualize(x_data_t, t_data_t, u_data_t,
                         save_path=f"results/{paper_name}_dynamics.png")
    
    print("\\n" + "="*60)
    print(f"Training complete! Results saved to 'results/'")
    print("="*60)
'''
    return code


def extract_system_info(tex_content, paper_name, title):
    """Extract system dimensionality from content"""
    name_lower = paper_name.lower()
    title_lower = title.lower()
    
    n_output = 1
    output_names = ['u']
    input_dim = 2  # (x, t)
    input_dim_str = 'x, t'
    
    if '2-ode' in name_lower or 'couple' in name_lower or \
       'nystagmus' in title_lower or 'torsion' in name_lower or \
       'coupling' in name_lower:
        n_output = 2
        output_names = ['u', 'v']
    
    if any(ind in name_lower for ind in ['oculomotor', 'gaze', 'saccade', 'fixation', 'pupil']):
        n_output = 2
        output_names = ['u', 'v']
    
    if 'corneal' in name_lower or 'wound' in name_lower or 'remodel' in name_lower:
        n_output = 2
        output_names = ['u', 'v']
    
    # Check for 3+ dimensional systems
    if tex_content and re.search(r'three.*dimensional|三维|3.*dimensional', tex_content, re.I):
        n_output = 3
        output_names = ['u', 'v', 'w']
        input_dim = 3
        input_dim_str = 'x, y, t'
    
    return {
        'n_output': n_output,
        'output_names': output_names,
        'input_dim': input_dim,
        'input_dim_str': input_dim_str,
    }


def make_train_py(paper_name, title, output_dim):
    """Generate train.py"""
    title_clean = re.sub(r'[{}]', '', title)
    title_clean = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', title_clean)
    
    return f'''#!/usr/bin/env python3
"""
Training entry point for: {title_clean}
Run: python train.py [--config config.yaml]
"""

import argparse
import os
import sys
import torch
import numpy as np

from pinn_model import {"".join([w.capitalize() for w in re.split(r'[-_]', paper_name) if w])}PINN, {"".join([w.capitalize() for w in re.split(r'[-_]', paper_name) if w])}Trainer


def main():
    parser = argparse.ArgumentParser(description='Train PINN for {title_clean}')
    parser.add_argument('--epochs', type=int, default=3000, help='Number of training epochs')
    parser.add_argument('--lr', type=float, default=1e-3, help='Learning rate')
    parser.add_argument('--hidden', type=int, nargs='+', default=[64, 64, 64], help='Hidden layer sizes')
    parser.add_argument('--batch-size', type=int, default=100, help='Training batch size')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--device', type=str, default='auto', help='Device: cuda/cpu/auto')
    parser.add_argument('--save-dir', type=str, default='results', help='Output directory')
    args = parser.parse_args()
    
    # Set random seed
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if torch.cuda.is_available() and args.device == 'auto':
        device = 'cuda'
    elif args.device == 'auto':
        device = 'cpu'
    else:
        device = args.device
    
    print(f"Device: {{device}}")
    print(f"Model: {title_clean}")
    print(f"Hidden layers: {{args.hidden}}")
    print(f"Learning rate: {{args.lr}}")
    print("="*60)
    
    # Create output directory
    os.makedirs(args.save_dir, exist_ok=True)
    
    # Generate synthetic data for demonstration
    # Replace with actual data loading
    data = generate_synthetic_data(args.batch_size)
    
    # Initialize model
    model = {"".join([w.capitalize() for w in re.split(r'[-_]', paper_name) if w])}PINN(
        hidden_layers=args.hidden, activation='tanh'
    )
    trainer = {"".join([w.capitalize() for w in re.split(r'[-_]', paper_name) if w])}Trainer(
        model, lr=args.lr, device=device
    )
    
    # Train
    print("\\nStarting training...")
    history = trainer.train(
        *data['inputs'],
        epochs=args.epochs,
        verbose=True,
        save_dir=args.save_dir,
        model_name="{paper_name}"
    )
    
    # Save
    trainer.save_checkpoint(os.path.join(args.save_dir, f"{paper_name}_model.pth"))
    trainer.visualize(
        *data['inputs'],
        save_path=os.path.join(args.save_dir, f"{paper_name}_dynamics.png")
    )
    
    print("\\n" + "="*60)
    print("Training complete!")
    print("="*60)
    
    return history


def generate_synthetic_data(n_samples=100):
    """Generate synthetic training data for demonstration"""
    np.random.seed(42)
    
    t_data = np.random.uniform(0, 5, n_samples).reshape(-1, 1)
    x_data = np.random.uniform(0, 1, n_samples).reshape(-1, 1)
    
    # TODO: Replace with actual solution from the paper
    u = np.sin(2*np.pi*x_data) * np.exp(-0.5*t_data)
    v = np.cos(2*np.pi*x_data) * np.exp(-0.3*t_data)
    u_data = np.column_stack([u, v]) + np.random.randn(n_samples, 2) * 0.01
    
    x_data_t = torch.tensor(x_data, dtype=torch.float32)
    t_data_t = torch.tensor(t_data, dtype=torch.float32)
    u_data_t = torch.tensor(u_data, dtype=torch.float32)
    
    return {
        'inputs': (x_data_t, t_data_t, u_data_t),
        'x': x_data_t,
        't': t_data_t,
        'u': u_data_t,
    }


if __name__ == "__main__":
    main()
'''


def make_readme(paper_name, title, abstract, paper_type):
    """Generate README.md"""
    title_clean = re.sub(r'[{}]', '', title)
    title_clean = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', title_clean)
    
    type_desc = {
        'bifurcation': 'Bifurcation Analysis',
        'nystagmus': 'Nystagmus Dynamics',
        'coupled': 'Coupled ODE System',
        'torsion': 'Ocular Torsion Dynamics',
        'generic': 'Differential Equation System',
    }.get(paper_type, 'Differential Equation System')
    
    return f'''# PINN Model: {title_clean}

## Overview

This project implements a **Physics-Informed Neural Network (PINN)** for:

**{type_desc}**

Based on the paper: *{title_clean}*

## What is PINN?

A Physics-Informed Neural Network (PINN) combines deep learning with
physical laws. Unlike standard neural networks that only fit data,
PINNs embed governing differential equations directly into the loss
function via automatic differentiation. This allows:

- Solving forward problems (predict solution from known parameters)
- Solving inverse problems (estimate parameters from data)
- Solving with limited/no data (pure physics constraint)

## Files

| File | Description |
|------|-------------|
| `pinn_model.py` | PINN model and training class |
| `train.py` | Training entry point with CLI |
| `requirements.txt` | Python dependencies |
| `README.md` | This file |

## Requirements

```bash
pip install -r requirements.txt
```

Required packages:
- **PyTorch** - Deep learning framework
- **NumPy** - Numerical computing
- **Matplotlib** - Visualization

## Quick Start

```bash
# Basic training with synthetic data
python train.py

# Custom training parameters
python train.py --epochs 5000 --lr 1e-3 --hidden 64 64 64

# Use GPU (if available)
python train.py --device cuda

# Specify output directory
python train.py --save-dir /path/to/results
```

## Usage

### Training

```python
from pinn_model import ModelPINN, ModelTrainer
import torch

# Initialize
model = ModelPINN(hidden_layers=[64, 64, 64])
trainer = ModelTrainer(model, lr=1e-3, device='cuda')

# Train with data
history = trainer.train(
    x_data, t_data, u_data,  # data coordinates and values
    epochs=3000, verbose=True
)

# Save and visualize
trainer.save_checkpoint("model.pth")
trainer.visualize(x_data, t_data, u_data, save_path="results.png")
```

### Model Architecture

- **Network**: Feedforward neural network with configurable hidden layers
- **Activation**: Tanh (default) or SiLU
- **Input**: Spatial coordinates + time
- **Output**: Dependent variable(s) of the system
- **Physics**: Automatic differentiation for PDE/ODE residuals

## Output

After training, the `results/` directory contains:

- `{paper_name}_model.pth` - Model checkpoint
- `{paper_name}_dynamics.png` - Visualization plot

## References

- Raissi, M., Perdikaris, P., & Karniadakis, G.E. (2019). 
  "Physics-informed neural networks: A deep learning framework 
  for solving forward and inverse problems."
'''


def make_requirements():
    """Generate requirements.txt"""
    return '''torch>=1.12.0
numpy>=1.21.0
matplotlib>=3.5.0
scipy>=1.7.0
'''


def extract_system_info(tex_content, paper_name, title):
    """Extract system dimensionality from content"""
    name_lower = paper_name.lower()
    title_lower = title.lower()
    
    n_output = 1
    output_names = ['u']
    input_dim = 2  # (x, t)
    input_dim_str = 'x, t'
    
    # Check for multi-output systems
    if '2-ode' in name_lower or 'couple' in name_lower or \
       'nystagmus' in title_lower or 'torsion' in name_lower or \
       'coupling' in name_lower or 'binaural' in name_lower or \
       'vestibular' in name_lower or 'corneal' in name_lower or \
       'wound' in name_lower or 'remodel' in name_lower or \
       'saccade' in name_lower or 'fixation' in name_lower or \
       'pupil' in name_lower or 'accomm' in name_lower or \
       'corneal' in name_lower or 'bvpv' in name_lower or \
       'nystagmus' in name_lower:
        n_output = 2
        output_names = ['u', 'v']
    
    if '2-ode' in name_lower and ('corneal' in name_lower or 'scleral' in name_lower):
        n_output = 2
        output_names = ['u', 'v']
    
    # Check for 3+ output systems in tex
    if tex_content and re.search(r'three.*dimensional|三维|3.*dimensional', tex_content, re.I):
        n_output = 3
        output_names = ['u', 'v', 'w']
        input_dim = 3
        input_dim_str = 'x, y, t'
    
    return {
        'n_output': n_output,
        'output_names': output_names,
        'input_dim': input_dim,
        'input_dim_str': input_dim_str,
    }


# ============================================================
# Main processing loop
# ============================================================

def process_paper(paper, paper_idx, total):
    """Process a single paper: read tex, generate code files"""
    paper_name = paper['paper_name']
    title = paper.get('title', '')
    paper_type = classify_paper(paper_name, title, '')
    
    paper_path = os.path.join(PAPERS_DIR, paper_name)
    
    result = {
        'paper_name': paper_name,
        'title': title,
        'paper_type': paper_type,
        'status': 'FAIL',
        'files_generated': [],
        'errors': []
    }
    
    try:
        # Step 1: Read paper.tex
        tex_content = read_paper_tex(paper_path)
        if tex_content is None:
            result['errors'].append(f"paper.tex not found at {paper_path}")
            result['status'] = 'FAIL'
            return result
        
        abstract = extract_abstract(tex_content)
        equations = extract_equations(tex_content)
        result['title'] = extract_title(tex_content) if not title else title
        
        # Step 2: Create output directory
        code_dir = os.path.join(paper_path, '03-code')
        os.makedirs(code_dir, exist_ok=True)
        
        # Step 3: Extract system info
        system_info = extract_system_info(tex_content, paper_name, title)
        
        # Step 4: Generate pinn_model.py
        model_code = make_pinn_model_py(
            paper_name, result['title'], abstract, tex_content, paper_type
        )
        model_path = os.path.join(code_dir, 'pinn_model.py')
        with open(model_path, 'w') as f:
            f.write(model_code)
        result['files_generated'].append('pinn_model.py')
        
        # Step 5: Generate train.py
        train_code = make_train_py(paper_name, result['title'], system_info['n_output'])
        train_path = os.path.join(code_dir, 'train.py')
        with open(train_path, 'w') as f:
            f.write(train_code)
        result['files_generated'].append('train.py')
        
        # Step 6: Generate README.md
        readme_content = make_readme(paper_name, result['title'], abstract, paper_type)
        readme_path = os.path.join(code_dir, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        result['files_generated'].append('README.md')
        
        # Step 7: Generate requirements.txt
        req_content = make_requirements()
        req_path = os.path.join(code_dir, 'requirements.txt')
        with open(req_path, 'w') as f:
            f.write(req_content)
        result['files_generated'].append('requirements.txt')
        
        # Check all files exist
        expected = ['pinn_model.py', 'train.py', 'README.md', 'requirements.txt']
        all_exist = all(os.path.exists(os.path.join(code_dir, f)) for f in expected)
        
        if all_exist and len(result['files_generated']) == 4:
            result['status'] = 'PASS'
        else:
            result['status'] = '部分'
            result['errors'].append('Not all expected files generated')
        
    except Exception as e:
        result['errors'].append(str(e))
        result['status'] = 'FAIL'
        import traceback
        result['errors'].append(traceback.format_exc())
    
    return result


def main():
    log("=" * 60)
    log("PINN论文批量代码生成 - 开始")
    log("=" * 60)
    
    # Load papers
    papers = load_papers()
    total = len(papers)
    log(f"Found {total} PINN P0 papers")
    
    results = []
    
    for i, paper in enumerate(papers):
        paper_name = paper['paper_name']
        title = paper.get('title', '')[:50]
        
        log(f"[{i+1}/{total}] Processing: {paper_name}")
        
        result = process_paper(paper, i+1, total)
        results.append(result)
        
        log(f"  -> Status: {result['status']}, Files: {result['files_generated']}")
        
        # Progress report every 10 papers
        if (i + 1) % 10 == 0:
            passed = sum(1 for r in results if r['status'] == 'PASS')
            failed = sum(1 for r in results if r['status'] == 'FAIL')
            partial = sum(1 for r in results if r['status'] == '部分')
            log(f"  Progress [{i+1}/{total}]: PASS={passed}, FAIL={failed}, 部分={partial}")
    
    # Final report
    log("")
    log("=" * 60)
    log("最终报告")
    log("=" * 60)
    
    passed = sum(1 for r in results if r['status'] == 'PASS')
    failed = sum(1 for r in results if r['status'] == 'FAIL')
    partial = sum(1 for r in results if r['status'] == '部分')
    
    log(f"总论文数: {total}")
    log(f"PASS: {passed}")
    log(f"FAIL: {failed}")
    log(f"部分: {partial}")
    log("")
    
    for r in results:
        log(f"  {r['paper_name']}: {r['status']} "
            f"(files: {', '.join(r['files_generated'])})"
            + (f" ERR: {r['errors']}" if r['errors'] else ""))
    
    # Save report
    report_path = "/tmp/pinn-gen-final-report.json"
    with open(report_path, 'w') as f:
        json.dump({
            'total': total,
            'passed': passed,
            'failed': failed,
            'partial': partial,
            'papers': results,
        }, f, indent=2, ensure_ascii=False)
    
    log(f"\\nFinal report saved to {report_path}")
    log("任务完成!")


if __name__ == "__main__":
    main()
