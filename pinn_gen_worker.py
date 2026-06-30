#!/usr/bin/env python3
"""
PINN论文批量代码生成器
为每篇PINN论文生成: pinn_model.py, train.py, README.md, requirements.txt
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
TASK_DESC = "/tmp/pinn-code-gen-task.md"
LOG_FILE = os.path.join(WORKDIR, "pinn_gen_progress.log")

def log(msg):
    """Write to both stdout and log file"""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    with open(LOG_FILE, 'a') as f:
        f.write(line + "\n")

def load_papers():
    """Load and filter PINN P0 papers from report"""
    with open(REPORT_PATH) as f:
        data = json.load(f)
    
    papers = data['papers']
    pinn_p0 = [p for p in papers if p.get('paper_type') == 'PINN' and p.get('priority') == 'P0']
    
    # Sort by paper_name for consistent ordering
    pinn_p0.sort(key=lambda x: x.get('paper_name', ''))
    return pinn_p0

def read_paper_tex(paper_path):
    """Read paper.tex and extract key information"""
    tex_path = os.path.join(paper_path, "01-manuscript", "paper.tex")
    if not os.path.exists(tex_path):
        return None
    
    with open(tex_path, 'r', errors='replace') as f:
        content = f.read()
    return content

def extract_title(tex_content):
    """Extract title from LaTeX content"""
    if not tex_content:
        return "Unknown Title"
    # Try \title{...}
    m = re.search(r'\\title\{((?:[^{}]|\{[^}]*\})*)\}', tex_content)
    if m:
        title = m.group(1)
        # Remove LaTeX commands for readability
        title = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', title)
        title = re.sub(r'[{}]', '', title)
        return title.strip()
    return "Unknown Title"

def extract_abstract(tex_content):
    """Extract abstract from LaTeX content"""
    if not tex_content:
        return ""
    m = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex_content, re.DOTALL)
    if m:
        abstract = m.group(1)
        abstract = re.sub(r'\\[a-zA-Z]+(?:\{[^}]*\})?', '', abstract)
        abstract = re.sub(r'[{}]', '', abstract)
        abstract = re.sub(r'\s+', ' ', abstract).strip()
        return abstract
    return ""

def extract_equations(tex_content):
    """Extract equation environments and their labels"""
    if not tex_content:
        return []
    equations = []
    # Match equation environments
    for m in re.finditer(r'\\begin\{(?:equation|align|eqnarray|gather)\}(.+?)\\end\{\1\}', tex_content, re.DOTALL):
        eq = m.group(1)
        # Get label if present
        label_m = re.search(r'\\label\{([^}]+)\}', eq)
        label = label_m.group(1) if label_m else ""
        equations.append({"label": label, "content": eq.strip()})
    return equations

def classify_pde_type(tex_content, paper_name):
    """Classify the type of PDE/ODE system from paper content"""
    if not tex_content:
        return "unknown", []
    
    content_lower = tex_content.lower()
    name_lower = paper_name.lower()
    
    # Check for ODE indicators
    ode_indicators = ['ode', 'ordinary differential', '一阶常微分', '常微分方程', 
                       'dy/dt', 'dx/dt', 'd\\theta/dt', 'dot', r'\dot\{', r'\ddot']
    
    # Check for PDE indicators
    pde_indicators = ['pde', 'partial differential', '偏微分方程', r'\frac{\partial', 
                       'spatial', '空间', 'laplacian', 'laplace']
    
    ode_count = sum(1 for ind in ode_indicators if re.search(ind, content_lower))
    pde_count = sum(1 for ind in pde_indicators if re.search(ind, content_lower))
    
    # Check specific equation types from the paper name
    if '2-ode' in name_lower or 'couple' in name_lower:
        return "2-ode-coupled", []
    if 'bvpv' in name_lower or 'nystagmus' in name_lower:
        return "nystagmus-ode", []
    if 'bifurcation' in content_lower or 'hopf' in content_lower:
        return "bifurcation-ode", []
    if ode_count > pde_count:
        return "ode", []
    return "pde", []

def get_system_info(tex_content, paper_name, title):
    """Extract system dimensionality and variables from content"""
    if not tex_content:
        return 1, ["u"], "u"
    
    # Look for system dimension from equation labels or text
    name_lower = paper_name.lower()
    title_lower = title.lower()
    
    # Check for 2D systems
    if '2-ode' in name_lower or 'coupled' in name_lower or \
       re.search(r'two\.*[ ]*dimensional|二维|双变量', tex_content):
        return 2, ["u", "v"], "u"
    
    # Check for single ODE
    if re.search(r'd[^t\s]/dt[^=]*\=', tex_content) and not re.search(r'[^a-z]d[^a-z]d', tex_content):
        return 1, ["u"], "u"
    
    return 1, ["u"], "u"

def generate_pinn_model_py(paper_name, title, abstract, tex_content, pde_type, equations):
    """Generate pinn_model.py content for a specific paper"""
    
    # Determine system specifics
    is_ode = 'ode' in pde_type
    is_coupled = 'coupled' in pde_type
    is_nystagmus = 'nystagmus' in pde_type or 'nystagmus' in paper_name.lower()
    is_bifurcation = 'bifurcation' in pde_type
    
    # Map paper-specific models
    specific_model = get_specific_model(paper_name, title, tex_content)
    
    code = specific_model['code']
    return code

def get_specific_model(paper_name, title, tex_content):
    """Generate paper-specific PINN model code"""
    name_lower = paper_name.lower()
    title_lower = title.lower()
    
    model_templates = {
        # Dissociated Ocular Torsion
        '092-dissociated-ocular-torsion-pin': {
            'title': 'Dissociated Ocular Torsion Dynamics',
            'code': '''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

"""
PINN Model for Dissociated Ocular Torsion Dynamics
A 2-ODE System: Describes torsional eye movement dynamics with dissociated components
"""

class OcularTorsionPINN(nn.Module):
    """
    Physics-Informed Neural Network for Ocular Torsion Dynamics
    
    System of ODEs:
    d^2theta/dt^2 + c1*dtheta/dt + k1*theta = f1(t)  (primary torsion)
    d^2phi/dt^2 + c2*dphi/dt + k2*phi = f2(t)        (dissociated component)
    
    Where:
    - theta: primary torsional position
    - phi: dissociated torsional component
    - c1, c2: damping coefficients
    - k1, k2: stiffness coefficients
    - f1, f2: external driving forces
    """
    
    def __init__(self, hidden_layers=[64, 64, 64], activation='tanh'):
        super().__init__()
        
        # Input: (x, y, t) - 2D spatial + time, or (t,) for temporal dynamics
        input_dim = 3  # x, y, t for spatial torsion
        output_dim = 2  # theta, phi (two torsional components)
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        layers.append(nn.Linear(input_dim, hidden_layers[0]))
        layers.append(act)
        
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        
        layers.append(nn.Linear(hidden_layers[-1], output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Learnable physics parameters (will be optimized)
        self.log_c1 = nn.Parameter(torch.tensor(0.0))  # damping 1
        self.log_c2 = nn.Parameter(torch.tensor(0.0))  # damping 2
        self.log_k1 = nn.Parameter(torch.tensor(1.0))  # stiffness 1
        self.log_k2 = nn.Parameter(torch.tensor(1.0))  # stiffness 2
        self.log_f1 = nn.Parameter(torch.tensor(0.0))  # force 1 amplitude
        self.log_f2 = nn.Parameter(torch.tensor(0.0))  # force 2 amplitude
    
    def forward(self, x, y, t):
        """Forward pass: returns (theta, phi)"""
        inputs = torch.cat([x, y, t], dim=-1)
        return self.network(inputs)
    
    def get_params(self):
        """Get physical parameters from learned parameters"""
        return {
            'c1': torch.exp(self.log_c1).item(),
            'c2': torch.exp(self.log_c2).item(),
            'k1': torch.exp(self.log_k1).item(),
            'k2': torch.exp(self.log_k2).item(),
            'f1': torch.exp(self.log_f1).item(),
            'f2': torch.exp(self.log_f2).item(),
        }
    
    def compute_pde_residual(self, x, y, t):
        """
        Compute physics-informed residuals using autograd
        
        Returns: residual_1 for theta ODE, residual_2 for phi ODE
        """
        x.requires_grad_(True)
        y.requires_grad_(True)
        t.requires_grad_(True)
        
        # Forward pass
        output = self.forward(x, y, t)
        theta = output[:, 0:1]
        phi = output[:, 1:2]
        
        # First derivatives w.r.t. time
        dt_theta = torch.autograd.grad(theta, t, grad_outputs=torch.ones_like(theta), 
                                        create_graph=True)[0]
        dt_phi = torch.autograd.grad(phi, t, grad_outputs=torch.ones_like(phi), 
                                      create_graph=True)[0]
        
        # Second derivatives w.r.t. time
        ddt_theta = torch.autograd.grad(dt_theta, t, grad_outputs=torch.ones_like(dt_theta), 
                                         create_graph=True)[0]
        ddt_phi = torch.autograd.grad(dt_phi, t, grad_outputs=torch.ones_like(dt_phi), 
                                       create_graph=True)[0]
        
        params = self.get_params()
        
        # ODE residuals
        residual_1 = ddt_theta + params['c1'] * dt_theta + params['k1'] * theta - params['f1']
        residual_2 = ddt_phi + params['c2'] * dt_phi + params['k2'] * phi - params['f2']
        
        return residual_1, residual_2


class PINNTrainer:
    """Complete PINN training pipeline for Ocular Torsion Dynamics"""
    
    def __init__(self, model, lr=1e-3, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.lr = lr
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.999))
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=5000)
        
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': []}
    
    def generate_collocation_points(self, n_colloc=500):
        """Generate collocation points for PDE residual computation"""
        t = torch.rand(n_colloc, 1, device=self.device) * 5.0  # t in [0, 5]
        x = torch.rand(n_colloc, 1, device=self.device) * 0.1   # x range
        y = torch.rand(n_colloc, 1, device=self.device) * 0.1   # y range
        return x, y, t
    
    def compute_loss(self, x_data, y_data, t_data, u_data, n_colloc=500):
        """
        Compute combined loss: data fit + physics residual
        
        Args:
            x_data, y_data, t_data: boundary/initial condition points
            u_data: observed values at boundary points
            n_colloc: number of collocation points
        
        Returns: data_loss, physics_loss, total_loss
        """
        # Data loss at boundary/initial conditions
        pred_boundary = self.model(x_data, y_data, t_data)
        data_loss = nn.MSELoss()(pred_boundary, u_data)
        
        # Physics residual at collocation points
        x_c, y_c, t_c = self.generate_collocation_points(n_colloc)
        res1, res2 = self.model.compute_pde_residual(x_c, y_c, t_c)
        physics_loss = nn.MSELoss()(res1, torch.zeros_like(res1)) + \
                       nn.MSELoss()(res2, torch.zeros_like(res2))
        
        total_loss = data_loss + 1.0 * physics_loss
        
        return data_loss, physics_loss, total_loss
    
    def train(self, x_data, y_data, t_data, u_data, epochs=5000, verbose=True, 
              save_path=None, model_name="ocular_torsion"):
        """Full training loop"""
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': [], 'epoch': []}
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            data_loss, physics_loss, total_loss = self.compute_loss(
                x_data, y_data, t_data, u_data
            )
            
            total_loss.backward()
            self.optimizer.step()
            self.scheduler.step()
            
            self.history['total_loss'].append(total_loss.item())
            self.history['data_loss'].append(data_loss.item())
            self.history['physics_loss'].append(physics_loss.item())
            self.history['epoch'].append(epoch)
            
            if verbose and (epoch + 1) % 500 == 0:
                log(f"  Epoch [{epoch+1}/{epochs}] "
                    f"Total: {total_loss.item():.6f} "
                    f"Data: {data_loss.item():.6f} "
                    f"Physics: {physics_loss.item():.6f}")
        
        return self.history
    
    def save_model(self, path):
        """Save model checkpoint"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'params': self.model.get_params(),
            'history': self.history,
        }, path)
        log(f"  Model saved to {path}")
    
    def visualize(self, save_path=None, n_points=200):
        """Visualize prediction and residuals"""
        self.model.eval()
        t_test = torch.linspace(0, 5, n_points).view(-1, 1).to(self.device)
        x_test = torch.zeros(n_points, 1).to(self.device)
        y_test = torch.zeros(n_points, 1).to(self.device)
        
        with torch.no_grad():
            pred = self.model(x_test, y_test, t_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot predictions
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 'b-', label=r'$\\theta(t)$')
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 1].cpu().numpy(), 'r-', label=r'$\\phi(t)$')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Torsion angle (rad)')
        axes[0, 0].set_title('Ocular Torsion Dynamics')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot convergence
        axes[0, 1].plot(self.history['epoch'], self.history['total_loss'], 'b-', label='Total')
        axes[0, 1].plot(self.history['epoch'], self.history['data_loss'], 'g-', label='Data')
        axes[0, 1].plot(self.history['epoch'], self.history['physics_loss'], 'r-', label='Physics')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].set_title('Training Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        axes[0, 1].set_yscale('log')
        
        # Plot residuals
        x_c, y_c, t_c = self.generate_collocation_points(n_points)
        with torch.no_grad():
            res1, res2 = self.model.compute_pde_residual(x_c, y_c, t_c)
        axes[1, 0].hist(res1.cpu().numpy(), bins=50, alpha=0.7, label=r'Residual $\\theta$')
        axes[1, 0].hist(res2.cpu().numpy(), bins=50, alpha=0.7, label=r'Residual $\\phi$')
        axes[1, 0].set_xlabel('Residual value')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('PDE Residual Distribution')
        axes[1, 0].legend()
        
        # Parameter estimation
        params = self.model.get_params()
        axes[1, 1].bar(['c1', 'c2', 'k1', 'k2', 'f1', 'f2'],
                       [params['c1'], params['c2'], params['k1'], params['k2'], 
                        params['f1'], params['f2']], color='steelblue')
        axes[1, 1].set_ylabel('Estimated value')
        axes[1, 1].set_title('Learned Physics Parameters')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            log(f"  Visualization saved to {save_path}")
        else:
            plt.show()
        
        self.model.train()


if __name__ == "__main__":
    # Demo: Train with synthetic data
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    log(f"Using device: {device}")
    
    # Generate synthetic training data
    np.random.seed(42)
    n_data = 100
    t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
    x_data = np.zeros((n_data, 1))
    y_data = np.zeros((n_data, 1))
    
    # Synthetic ground truth with known params
    c1, c2, k1, k2, f1, f2 = 0.5, 0.3, 2.0, 1.5, 0.1, 0.05
    u1 = f1/k1 * (1 - np.exp(-c1*t_data/2) * np.cos(2*t_data))
    u2 = f2/k2 * (1 - np.exp(-c2*t_data/2) * np.cos(2*t_data))
    
    # Add noise to synthetic data
    u_data = np.column_stack([u1, u2]) + np.random.randn(n_data, 2) * 0.01
    
    x_data_t = torch.tensor(x_data, dtype=torch.float32, device=device)
    y_data_t = torch.tensor(y_data, dtype=torch.float32, device=device)
    t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
    u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    # Initialize and train
    model = OcularTorsionPINN(hidden_layers=[64, 64, 64], activation='tanh')
    trainer = PINNTrainer(model, lr=1e-3, device=device)
    
    log("Starting training...")
    trainer.train(x_data_t, y_data_t, t_data_t, u_data_t, epochs=3000, verbose=True)
    
    # Save results
    os.makedirs("results", exist_ok=True)
    trainer.save_model("results/ocular_torsion_model.pth")
    trainer.visualize(save_path="results/ocular_torsion_dynamics.png")
    
    # Print learned parameters
    params = model.get_params()
    log(f"\\nLearned parameters: {params}")
    log(f"\\nTrue parameters: c1={c1}, c2={c2}, k1={k1}, k2={k2}, f1={f1}, f2={f2}")
    
    print("\\n✅ Ocular Torsion PINN training complete!")
'''
        },
    }
    
    # Default templates for categories
    if is_bifurcation:
        return bifurcation_pinn_model(title, paper_name, tex_content)
    elif is_nystagmus:
        return nystagmus_pinn_model(title, paper_name, tex_content)
    elif is_coupled:
        return coupled_ode_pinn_model(title, paper_name, tex_content)
    
    # Generic template based on paper name
    return generic_pinn_model(title, paper_name, tex_content, pde_type)


def generic_pinn_model(title, paper_name, tex_content, pde_type):
    """Generate a generic PINN model based on paper content"""
    
    # Parse title for key information
    title_clean = re.sub(r'[{}]', '', title)
    
    model_desc = f"""Physics-Informed Neural Network for {title_clean}
    """
    
    code = '''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

"""
PINN Model: {title_clean}

This module implements a Physics-Informed Neural Network (PINN) 
to solve the governing differential equations described in the paper.

The PINN approach embeds physical laws directly into the neural network
loss function through automatic differentiation, enabling parameter
estimation and solution of differential equations simultaneously.
"""


class {paper_name.replace("-", "").title()}PINN(nn.Module):
    """
    Physics-Informed Neural Network for the model described in:
    {title_clean}
    
    Network Architecture:
    - Input: spatial coordinates + time (x, y, ..., t)
    - Output: dependent variable(s) of the ODE/PDE system
    - Hidden layers: configurable depth and width
    - Activation: tanh (default) or SiLU for smoother gradients
    
    Physics-Informed Loss:
    - Governing equation residuals computed via autograd
    - Boundary/initial condition constraints
    - Data-fitting loss from experimental observations
    """
    
    def __init__(self, hidden_layers=None, activation='tanh'):
        super().__init__()
        
        # Default: input is (x, t) for temporal dynamics
        self.input_dim = 2  # (position, time)
        self.output_dim = 1  # single dependent variable
        
        if hidden_layers is None:
            hidden_layers = [64, 64, 64]
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        
        # Input layer
        layers.append(nn.Linear(self.input_dim, hidden_layers[0]))
        layers.append(act)
        
        # Hidden layers
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        
        # Output layer (no activation for regression)
        layers.append(nn.Linear(hidden_layers[-1], self.output_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Physics parameters to be learned
        self.learned_params = nn.ParameterDict({
            'param_1': nn.Parameter(torch.tensor(1.0)),
        })
    
    def forward(self, x, t):
        """
        Forward pass: predict the solution u(x,t)
        
        Args:
            x: spatial coordinate tensor (N, 1)
            t: time coordinate tensor (N, 1)
        
        Returns:
            u: predicted solution tensor (N, output_dim)
        """
        inputs = torch.cat([x, t], dim=-1)
        return self.network(inputs)
    
    def forward_nd(self, *coords):
        """
        Forward pass for N-dimensional inputs
        
        Args:
            *coords: variable number of coordinate tensors
        
        Returns:
            u: predicted solution tensor (N, output_dim)
        """
        inputs = torch.cat(coords, dim=-1)
        return self.network(inputs)
    
    def compute_residual(self, x, t):
        """
        Compute the PDE/ODE residual using automatic differentiation.
        
        For a general ODE: du/dt = f(u, x, t, params)
        The residual is: R = du/dt - f(u, x, t, params)
        
        Returns:
            residual: tensor of residual values (N, 1)
        """
        x.requires_grad_(True)
        t.requires_grad_(True)
        
        u = self.forward(x, t)
        
        # First derivative w.r.t. time
        dt_u = torch.autograd.grad(
            u, t, grad_outputs=torch.ones_like(u), 
            create_graph=True
        )[0]
        
        # First derivative w.r.t. space (if applicable)
        dx_u = torch.autograd.grad(
            u, x, grad_outputs=torch.ones_like(u), 
            create_graph=True
        )[0]
        
        # Second derivative w.r.t. space (for diffusion terms)
        dxx_u = torch.autograd.grad(
            dx_u, x, grad_outputs=torch.ones_like(dx_u), 
            create_graph=True
        )[0]
        
        # Compute residual: R = du/dt - (diffusion + reaction terms)
        # TODO: Replace with actual governing equation from the paper
        residual = dt_u - (dxx_u - u + torch.sin(t))
        
        return residual


class {paper_name.replace("-", "").title()}Trainer:
    """
    Complete PINN training pipeline.
    
    Handles:
    1. Data loading (synthetic or experimental)
    2. Collocation point sampling
    3. Loss computation (data + physics)
    4. Training loop with scheduling
    5. Visualization and result saving
    """
    
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
    
    def sample_collocation_points(self, n_colloc=1000):
        """
        Sample collocation points uniformly in space-time domain.
        
        Returns:
            x_colloc: spatial coordinates (N, 1)
            t_colloc: time coordinates (N, 1)
        """
        t_colloc = torch.rand(n_colloc, 1, device=self.device) * 5.0
        x_colloc = torch.rand(n_colloc, 1, device=self.device) * 2.0
        return x_colloc, t_colloc
    
    def compute_loss(self, x_data, t_data, u_data, n_colloc=500):
        """
        Compute combined loss function.
        
        Loss = w_data * L_data + w_physics * L_physics
        
        Args:
            x_data: spatial coords of data points
            t_data: time coords of data points
            u_data: observed values
            n_colloc: number of collocation points
        
        Returns:
            data_loss, physics_loss, total_loss
        """
        # Data-fitting loss at boundary/observed points
        pred_data = self.model(x_data, t_data)
        data_loss = nn.MSELoss()(pred_data, u_data)
        
        # Physics residual loss at collocation points
        x_c, t_c = self.sample_collocation_points(n_colloc)
        residual = self.model.compute_residual(x_c, t_c)
        physics_loss = nn.MSELoss()(residual, torch.zeros_like(residual))
        
        # Combined loss (weights can be tuned)
        w_data = 1.0
        w_physics = 1.0
        total_loss = w_data * data_loss + w_physics * physics_loss
        
        return data_loss, physics_loss, total_loss
    
    def train(self, x_data, t_data, u_data, epochs=5000, verbose=True,
              save_dir=None, model_name="model"):
        """
        Full training loop.
        
        Args:
            x_data: spatial coordinates (N, 1)
            t_data: time coordinates (N, 1)
            u_data: observed values (N, 1)
            epochs: number of training iterations
            verbose: print progress every 500 epochs
            save_dir: directory to save results
            model_name: base name for saved files
        """
        self.history = {
            'total_loss': [], 'data_loss': [], 
            'physics_loss': [], 'epoch': []
        }
        
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            
            data_loss, physics_loss, total_loss = self.compute_loss(
                x_data, t_data, u_data
            )
            
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(), max_norm=1.0
            )
            self.optimizer.step()
            self.scheduler.step()
            
            self.history['total_loss'].append(total_loss.item())
            self.history['data_loss'].append(data_loss.item())
            self.history['physics_loss'].append(physics_loss.item())
            self.history['epoch'].append(epoch)
            
            if verbose and (epoch + 1) % 500 == 0:
                print(f"  Epoch [{epoch+1}/{epochs}] "
                      f"Total: {total_loss.item():.6f} "
                      f"Data: {data_loss.item():.6f} "
                      f"Physics: {physics_loss.item():.6f}")
        
        return self.history
    
    def save_checkpoint(self, path):
        """Save model checkpoint"""
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'model_class': type(self.model).__name__,
            'params': self.model.learned_params,
            'history': {k: v for k, v in self.history.items()},
        }, path)
        print(f"  Checkpoint saved to {path}")
    
    def visualize(self, save_path=None, n_points=200):
        """Generate visualization of training results"""
        self.model.eval()
        t_test = torch.linspace(0, 5, n_points).view(-1, 1).to(self.device)
        x_test = torch.zeros(n_points, 1).to(self.device)
        
        with torch.no_grad():
            pred = self.model(x_test, t_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Plot predictions over time
        axes[0, 0].plot(
            t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 
            'b-', linewidth=2, label='Predicted Solution'
        )
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Solution u')
        axes[0, 0].set_title('Time Evolution of Solution')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Plot loss convergence
        axes[0, 1].plot(
            self.history['epoch'], self.history['total_loss'], 
            'b-', label='Total Loss'
        )
        axes[0, 1].plot(
            self.history['epoch'], self.history['data_loss'], 
            'g-', label='Data Loss'
        )
        axes[0, 1].plot(
            self.history['epoch'], self.history['physics_loss'], 
            'r-', label='Physics Loss'
        )
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].set_title('Training Loss Curve')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        axes[0, 1].set_yscale('log')
        
        # Residual distribution
        x_c, t_c = self.sample_collocation_points(n_points)
        with torch.no_grad():
            residual = self.model.compute_residual(x_c, t_c)
        axes[1, 0].hist(
            residual.cpu().numpy().flatten(), bins=50, 
            alpha=0.7, color='steelblue'
        )
        axes[1, 0].set_xlabel('Residual Value')
        axes[1, 0].set_ylabel('Count')
        axes[1, 0].set_title('PDE Residual Distribution')
        axes[1, 0].grid(True)
        
        # Predicted vs data
        if hasattr(self, '_x_data') and hasattr(self, '_u_data'):
            axes[1, 1].scatter(
                self._x_data.cpu().numpy().flatten(), 
                self._u_data.cpu().numpy().flatten(),
                alpha=0.5, label='Data', s=10
            )
        axes[1, 1].plot(
            t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 
            'r--', linewidth=2, label='PINN Prediction'
        )
        axes[1, 1].set_xlabel('Time (s)')
        axes[1, 1].set_ylabel('Solution u')
        axes[1, 1].set_title('Data vs PINN Prediction')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {save_path}")
        else:
            plt.show()
        
        self.model.train()


if __name__ == "__main__":
    """
    Main entry point for training.
    Uses synthetic data for demonstration.
    Replace with actual experimental data loading.
    """
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print(f"Model: {title_clean}")
    print("="*60)
    
    # === Generate synthetic training data ===
    np.random.seed(42)
    n_data = 100
    t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
    x_data = np.random.uniform(0, 1, n_data).reshape(-1, 1)
    
    # Synthetic ground truth: TODO: replace with actual solution
    u_data = np.sin(2 * np.pi * x_data) * np.exp(-t_data * 0.5) + \
             np.random.randn(n_data, 1) * 0.01
    
    # Convert to tensors
    x_data_t = torch.tensor(x_data, dtype=torch.float32, device=device)
    t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
    u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    # === Initialize and train PINN ===
    model = {paper_name.replace("-", "").title()}PINN(
        hidden_layers=[64, 64, 64], activation='tanh'
    )
    trainer = {paper_name.replace("-", "").title()}Trainer(
        model, lr=1e-3, device=device
    )
    
    # Store data for visualization
    trainer._x_data = x_data_t
    trainer._u_data = u_data_t
    
    print("\\n" + "="*60)
    print("Starting PINN Training...")
    print("="*60)
    
    trainer.train(
        x_data_t, t_data_t, u_data_t,
        epochs=3000,
        verbose=True,
        save_dir="results",
        model_name="{paper_name}"
    )
    
    # === Save results ===
    os.makedirs("results", exist_ok=True)
    trainer.save_checkpoint(f"results/{paper_name}_model.pth")
    trainer.visualize(
        save_path=f"results/{paper_name}_dynamics.png"
    )
    
    print("\\n" + "="*60)
    print(f"✅ Training complete! Results saved to 'results/' directory.")
    print("="*60)
'''
    
    return {'code': code}


def bifurcation_pinn_model(title, paper_name, tex_content):
    """Generate PINN model for bifurcation/Hopf bifurcation analysis"""
    code = '''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

"""
PINN Model for Bifurcation Analysis (e.g., Hopf Bifurcation)
Uses PINN to estimate bifurcation parameters and analyze stability.

The governing system involves a parameter-dependent ODE where
the qualitative behavior changes at a critical parameter value.

Example: dx/dt = mu*x - x^3  (pitchfork bifurcation)
         dz/dt = w*y
         dy/dt = -w*y + mu*x - x^3  (Hopf-like system)
"""


class BifurcationPINN(nn.Module):
    """
    Physics-Informed Neural Network for Bifurcation Analysis
    
    Governing equations (example):
    dtheta/dt = f(theta, mu)  where mu is bifurcation parameter
    
    The PINN simultaneously learns:
    1. The time evolution solution theta(t)
    2. Bifurcation parameter(s) mu
    3. Stability properties through phase space analysis
    """
    
    def __init__(self, hidden_layers=[64, 64, 64], activation='tanh'):
        super().__init__()
        
        self.input_dim = 1   # time only
        self.output_dim = 2   # theta (angle) + phase variable
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        layers.append(nn.Linear(self.input_dim, hidden_layers[0]))
        layers.append(act)
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        layers.append(nn.Linear(hidden_layers[-1], self.output_dim))
        self.network = nn.Sequential(*layers)
        
        # Bifurcation parameters
        self.log_mu = nn.Parameter(torch.tensor(0.0))   # bifurcation parameter
        self.log_w = nn.Parameter(torch.tensor(1.0))    # angular frequency
        self.log_amplitude = nn.Parameter(torch.tensor(1.0))
    
    def forward(self, t):
        """Forward pass: predict theta(t) and phase"""
        return self.network(t)
    
    def get_params(self):
        return {
            'mu': torch.exp(self.log_mu).item(),
            'omega': torch.exp(self.log_w).item(),
            'amplitude': torch.exp(self.log_amplitude).item(),
        }
    
    def compute_residual(self, t):
        """
        Compute ODE residual for bifurcation system.
        
        System:
        dtheta/dt = omega * phi
        dphi/dt = -omega * phi + mu * theta - theta^3
        """
        t.requires_grad_(True)
        output = self.forward(t)
        theta = output[:, 0:1]
        phi = output[:, 1:2]
        
        dtheta_dt = torch.autograd.grad(
            theta, t, grad_outputs=torch.ones_like(theta), 
            create_graph=True
        )[0]
        
        dphi_dt = torch.autograd.grad(
            phi, t, grad_outputs=torch.ones_like(phi), 
            create_graph=True
        )[0]
        
        params = self.get_params()
        
        # ODE residuals
        res1 = dtheta_dt - params['omega'] * phi
        res2 = dphi_dt - (-params['omega'] * phi + params['mu'] * theta - theta**3)
        
        return res1, res2


class BifurcationTrainer:
    def __init__(self, model, lr=1e-3, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(
            model.parameters(), lr=lr, betas=(0.9, 0.999)
        )
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            self.optimizer, T_max=5000
        )
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': [], 'epoch': []}
    
    def compute_loss(self, t_data, u_data, n_colloc=500):
        # Data loss
        pred_data = self.model(t_data)
        data_loss = nn.MSELoss()(pred_data, u_data)
        
        # Physics residual
        t_c = torch.rand(n_colloc, 1, device=self.device) * 5.0
        res1, res2 = self.model.compute_residual(t_c)
        physics_loss = nn.MSELoss()(res1, torch.zeros_like(res1)) + \
                       nn.MSELoss()(res2, torch.zeros_like(res2))
        
        total_loss = data_loss + 1.0 * physics_loss
        return data_loss, physics_loss, total_loss
    
    def train(self, t_data, u_data, epochs=5000, verbose=True, save_dir=None, model_name="bifurcation"):
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            data_loss, physics_loss, total_loss = self.compute_loss(t_data, u_data)
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
            'history': self.history,
        }, path)
        print(f"  Checkpoint saved to {path}")
    
    def visualize(self, save_path=None, n_points=200):
        self.model.eval()
        t_test = torch.linspace(0, 5, n_points).view(-1, 1).to(self.device)
        
        with torch.no_grad():
            pred = self.model(t_test)
        
        params = self.model.get_params()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Time evolution
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 'b-', label='theta')
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 1].cpu().numpy(), 'r-', label='phi')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Variable')
        axes[0, 0].set_title('Bifurcation System Dynamics')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Phase portrait
        axes[0, 1].plot(pred[:, 0].cpu().numpy(), pred[:, 1].cpu().numpy(), 'b-', linewidth=2)
        axes[0, 1].set_xlabel('theta')
        axes[0, 1].set_ylabel('phi')
        axes[0, 1].set_title('Phase Portrait')
        axes[0, 1].grid(True)
        
        # Loss curve
        axes[1, 0].plot(self.history['epoch'], self.history['total_loss'], 'b-', label='Total')
        axes[1, 0].plot(self.history['epoch'], self.history['data_loss'], 'g-', label='Data')
        axes[1, 0].plot(self.history['epoch'], self.history['physics_loss'], 'r-', label='Physics')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].set_title('Training Loss')
        axes[1, 0].legend()
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True)
        
        # Bifurcation diagram
        mu_values = np.linspace(0, 2, 200)
        theta_eq = np.sqrt(max(params['mu'], 0))
        axes[1, 1].axvline(params['mu'], color='r', linestyle='--', label=f'est. mu = {params["mu"]:.3f}')
        axes[1, 1].plot(mu_values, theta_eq, 'b-', label='Stable equilibrium')
        axes[1, 1].plot(mu_values, -theta_eq, 'b-')
        axes[1, 1].set_xlabel('mu (bifurcation parameter)')
        axes[1, 1].set_ylabel('theta_eq')
        axes[1, 1].set_title('Bifurcation Diagram')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {save_path}")
        self.model.train()


if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print("Model: Bifurcation Analysis (Hopf/Pitchfork)")
    print("="*60)
    
    np.random.seed(42)
    n_data = 100
    t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
    
    # Synthetic data: Hopf bifurcation dynamics
    mu_true, w_true = 0.5, 2.0
    theta_true = mu_true * (1 - np.exp(-w_true * t_data)) * np.cos(w_true * t_data)
    phi_true = -theta_true + theta_true * np.exp(-w_true * t_data)
    u_data = np.column_stack([theta_true, phi_true]) + np.random.randn(n_data, 2) * 0.01
    
    t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
    u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    model = BifurcationPINN(hidden_layers=[64, 64, 64])
    trainer = BifurcationTrainer(model, lr=1e-3, device=device)
    
    print("\\nStarting training...")
    trainer.train(t_data_t, u_data_t, epochs=3000, verbose=True)
    
    os.makedirs("results", exist_ok=True)
    trainer.save_checkpoint("results/bifurcation_model.pth")
    trainer.visualize(save_path="results/bifurcation_analysis.png")
    
    params = model.get_params()
    print(f"\\nLearned params: mu={params['mu']:.4f}, omega={params['omega']:.4f}")
    print(f"True params: mu={mu_true}, omega={w_true}")
    print("\\n✅ Bifurcation PINN training complete!")
'''
    return {'code': code}


def nystagmus_pinn_model(title, paper_name, tex_content):
    """Generate PINN model for nystagmus dynamics"""
    code = '''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

"""
PINN Model for BPPV-Induced Nystagmus Dynamics
Models the vestibular system response during positional testing.

System: Two-state model describing canalolithiasis mechanics
  dposition/dt = f(position, velocity, params)
  velocity is measured as nystagmus response
"""


class NystagmusPINN(nn.Module):
    """
    Physics-Informed Neural Network for BPPV Nystagmus Dynamics
    
    State variables:
    - u: cupula displacement (measured as nystagmus velocity)
    - v: otolith position (particle position in canal)
    
    Governing equations:
    du/dt = f(u, v, params)  - cupula dynamics
    dv/dt = g(u, v, params)  - particle dynamics
    
    During BPPV testing, head position changes create characteristic
    nystagmus patterns that can be modeled and fitted using PINN.
    """
    
    def __init__(self, hidden_layers=[64, 64, 64], activation='tanh'):
        super().__init__()
        
        self.input_dim = 1    # time
        self.output_dim = 2   # u (cupula), v (particle)
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        layers.append(nn.Linear(self.input_dim, hidden_layers[0]))
        layers.append(act)
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        layers.append(nn.Linear(hidden_layers[-1], self.output_dim))
        self.network = nn.Sequential(*layers)
        
        # Vestibular parameters
        self.log_tau = nn.Parameter(torch.tensor(0.0))     # cupula time constant
        self.log_k = nn.Parameter(torch.tensor(1.0))       # stiffness
        self.log_m = nn.Parameter(torch.tensor(1.0))       # particle mass/drag
        self.log_pos_change = nn.Parameter(torch.tensor(0.0))  # head position change magnitude
    
    def forward(self, t):
        return self.network(t)
    
    def get_params(self):
        return {
            'tau': torch.exp(self.log_tau).item(),
            'k': torch.exp(self.log_k).item(),
            'm': torch.exp(self.log_m).item(),
            'pos_change': torch.exp(self.log_pos_change).item(),
        }
    
    def compute_residual(self, t):
        """
        Compute nystagmus dynamics residuals.
        
        BPPV model:
        tau * du/dt + u = K * (v - v_stable)   [cupula equation]
        m * dv/dt + v/tau_v = pos_change * f(t) [particle equation]
        """
        t.requires_grad_(True)
        output = self.forward(t)
        u = output[:, 0:1]  # cupula displacement / nystagmus
        v = output[:, 1:2]  # particle position
        
        du_dt = torch.autograd.grad(
            u, t, grad_outputs=torch.ones_like(u), create_graph=True
        )[0]
        dv_dt = torch.autograd.grad(
            v, t, grad_outputs=torch.ones_like(v), create_graph=True
        )[0]
        
        params = self.get_params()
        
        # Step function for head position change (simplified)
        step = torch.where(t > 0.5, params['pos_change'], 0.0)
        
        # Cupula residual
        res1 = params['tau'] * du_dt + u - params['k'] * (v - params['k'] * step / (params['k'] + 1))
        # Particle residual
        res2 = params['m'] * dv_dt + v - step
        
        return res1, res2


class NystagmusTrainer:
    def __init__(self, model, lr=1e-3, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.999))
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=5000)
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': [], 'epoch': []}
    
    def compute_loss(self, t_data, u_data, n_colloc=500):
        pred_data = self.model(t_data)
        data_loss = nn.MSELoss()(pred_data, u_data)
        
        t_c = torch.rand(n_colloc, 1, device=self.device) * 10.0
        res1, res2 = self.model.compute_residual(t_c)
        physics_loss = nn.MSELoss()(res1, torch.zeros_like(res1)) + nn.MSELoss()(res2, torch.zeros_like(res2))
        
        total_loss = data_loss + 1.0 * physics_loss
        return data_loss, physics_loss, total_loss
    
    def train(self, t_data, u_data, epochs=5000, verbose=True, save_dir=None, model_name="nystagmus"):
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            data_loss, physics_loss, total_loss = self.compute_loss(t_data, u_data)
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
            'history': self.history,
        }, path)
        print(f"  Checkpoint saved to {path}")
    
    def visualize(self, save_path=None, n_points=200):
        self.model.eval()
        t_test = torch.linspace(0, 10, n_points).view(-1, 1).to(self.device)
        with torch.no_grad():
            pred = self.model(t_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 'b-', label='Cupula (nystagmus)')
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 1].cpu().numpy(), 'r-', label='Particle position')
        axes[0, 0].set_xlabel('Time (s)')
        axes[0, 0].set_ylabel('Value')
        axes[0, 0].set_title('Nystagmus Dynamics')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        axes[0, 1].plot(self.history['epoch'], self.history['total_loss'], 'b-', label='Total')
        axes[0, 1].plot(self.history['epoch'], self.history['data_loss'], 'g-', label='Data')
        axes[0, 1].plot(self.history['epoch'], self.history['physics_loss'], 'r-', label='Physics')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].set_title('Training Loss')
        axes[0, 1].legend()
        axes[0, 1].set_yscale('log')
        axes[0, 1].grid(True)
        
        params = self.model.get_params()
        axes[1, 0].bar(['tau', 'k', 'm', 'pos_change'],
                       [params['tau'], params['k'], params['m'], params['pos_change']],
                       color='steelblue')
        axes[1, 0].set_ylabel('Value')
        axes[1, 0].set_title('Learned Vestibular Parameters')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, axis='y')
        
        # Phase portrait
        axes[1, 1].plot(pred[:, 0].cpu().numpy(), pred[:, 1].cpu().numpy(), 'b-', linewidth=2)
        axes[1, 1].set_xlabel('Cupula displacement')
        axes[1, 1].set_ylabel('Particle position')
        axes[1, 1].set_title('Phase Portrait')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {save_path}")
        self.model.train()


if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print("Model: BPPV-Induced Nystagmus Dynamics")
    print("="*60)
    
    np.random.seed(42)
    n_data = 100
    t_data = np.random.uniform(0, 10, n_data).reshape(-1, 1)
    
    # Synthetic nystagmus data (characteristic geotropic/apogeotropic response)
    tau_true, k_true, m_true = 0.5, 1.0, 0.3
    pos_true = 0.5
    u_true = pos_true * (1 - np.exp(-t_data / tau_true)) * (1 - np.exp(-t_data * m_true))
    v_true = pos_true * (1 - np.exp(-t_data / tau_true))
    u_data = np.column_stack([u_true, v_true]) + np.random.randn(n_data, 2) * 0.01
    
    t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
    u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    model = NystagmusPINN(hidden_layers=[64, 64, 64])
    trainer = NystagmusTrainer(model, lr=1e-3, device=device)
    
    print("\\nStarting training...")
    trainer.train(t_data_t, u_data_t, epochs=3000, verbose=True)
    
    os.makedirs("results", exist_ok=True)
    trainer.save_checkpoint("results/nystagmus_model.pth")
    trainer.visualize(save_path="results/nystagmus_dynamics.png")
    
    params = model.get_params()
    print(f"\\nLearned params: tau={params['tau']:.4f}, k={params['k']:.4f}, m={params['m']:.4f}")
    print(f"True params: tau={tau_true}, k={k_true}, m={m_true}")
    print("\\n✅ Nystagmus PINN training complete!")
'''
    return {'code': code}


def coupled_ode_pinn_model(title, paper_name, tex_content):
    """Generate PINN model for coupled ODE systems"""
    code = '''import torch
import torch.nn as nn
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

"""
PINN Model for Coupled ODE System
Models a system of two coupled differential equations.

System:
  du/dt = f(u, v, params)
  dv/dt = g(u, v, params)
"""


class CoupledODEPINN(nn.Module):
    """
    Physics-Informed Neural Network for a 2-ODE coupled system.
    
    Governing equations:
    du/dt = f(u, v, theta, k, coupling_params)
    dv/dt = g(u, v, theta, k, coupling_params)
    
    Where u and v represent two interacting state variables.
    """
    
    def __init__(self, hidden_layers=[64, 64, 64], activation='tanh'):
        super().__init__()
        
        self.input_dim = 1    # time
        self.output_dim = 2   # u, v (two state variables)
        
        layers = []
        act = nn.Tanh() if activation == 'tanh' else nn.SiLU()
        layers.append(nn.Linear(self.input_dim, hidden_layers[0]))
        layers.append(act)
        for i in range(len(hidden_layers) - 1):
            layers.append(nn.Linear(hidden_layers[i], hidden_layers[i + 1]))
            layers.append(act)
        layers.append(nn.Linear(hidden_layers[-1], self.output_dim))
        self.network = nn.Sequential(*layers)
        
        # Model parameters
        self.log_c1 = nn.Parameter(torch.tensor(0.0))
        self.log_c2 = nn.Parameter(torch.tensor(0.0))
        self.log_k1 = nn.Parameter(torch.tensor(1.0))
        self.log_k2 = nn.Parameter(torch.tensor(1.0))
        self.log_coupling = nn.Parameter(torch.tensor(0.0))
    
    def forward(self, t):
        return self.network(t)
    
    def get_params(self):
        return {
            'c1': torch.exp(self.log_c1).item(),
            'c2': torch.exp(self.log_c2).item(),
            'k1': torch.exp(self.log_k1).item(),
            'k2': torch.exp(self.log_k2).item(),
            'coupling': torch.exp(self.log_coupling).item(),
        }
    
    def compute_residual(self, t):
        """
        Compute coupled ODE residuals.
        
        General form:
        du/dt = -c1*u + k1*v + coupling*u*v
        dv/dt = -c2*v + k2*u - coupling*u*v
        """
        t.requires_grad_(True)
        output = self.forward(t)
        u = output[:, 0:1]
        v = output[:, 1:2]
        
        du_dt = torch.autograd.grad(u, t, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        dv_dt = torch.autograd.grad(v, t, grad_outputs=torch.ones_like(v), create_graph=True)[0]
        
        params = self.get_params()
        
        # Coupled ODE residuals
        res1 = du_dt - (-params['c1'] * u + params['k1'] * v + params['coupling'] * u * v)
        res2 = dv_dt - (-params['c2'] * v + params['k2'] * u - params['coupling'] * u * v)
        
        return res1, res2


class CoupledODETrainer:
    def __init__(self, model, lr=1e-3, device='cpu'):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.9, 0.999))
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=5000)
        self.history = {'total_loss': [], 'data_loss': [], 'physics_loss': [], 'epoch': []}
    
    def compute_loss(self, t_data, u_data, n_colloc=500):
        pred_data = self.model(t_data)
        data_loss = nn.MSELoss()(pred_data, u_data)
        
        t_c = torch.rand(n_colloc, 1, device=self.device) * 5.0
        res1, res2 = self.model.compute_residual(t_c)
        physics_loss = nn.MSELoss()(res1, torch.zeros_like(res1)) + nn.MSELoss()(res2, torch.zeros_like(res2))
        
        total_loss = data_loss + 1.0 * physics_loss
        return data_loss, physics_loss, total_loss
    
    def train(self, t_data, u_data, epochs=5000, verbose=True, save_dir=None, model_name="coupled_ode"):
        for epoch in range(epochs):
            self.optimizer.zero_grad()
            data_loss, physics_loss, total_loss = self.compute_loss(t_data, u_data)
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
            'history': self.history,
        }, path)
        print(f"  Checkpoint saved to {path}")
    
    def visualize(self, save_path=None, n_points=200):
        self.model.eval()
        t_test = torch.linspace(0, 5, n_points).view(-1, 1).to(self.device)
        with torch.no_grad():
            pred = self.model(t_test)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 0].cpu().numpy(), 'b-', label='u(t)')
        axes[0, 0].plot(t_test.cpu().numpy(), pred[:, 1].cpu().numpy(), 'r-', label='v(t)')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Value')
        axes[0, 0].set_title('Coupled ODE Solutions')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        axes[1, 0].plot(self.history['epoch'], self.history['total_loss'], 'b-', label='Total')
        axes[1, 0].plot(self.history['epoch'], self.history['data_loss'], 'g-', label='Data')
        axes[1, 0].plot(self.history['epoch'], self.history['physics_loss'], 'r-', label='Physics')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Loss')
        axes[1, 0].set_title('Training Loss')
        axes[1, 0].legend()
        axes[1, 0].set_yscale('log')
        axes[1, 0].grid(True)
        
        params = self.model.get_params()
        axes[0, 1].bar(['c1', 'c2', 'k1', 'k2', 'coupling'],
                       [params['c1'], params['c2'], params['k1'], params['k2'], params['coupling']],
                       color='steelblue')
        axes[0, 1].set_ylabel('Value')
        axes[0, 1].set_title('Learned Parameters')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(True, axis='y')
        
        axes[1, 1].plot(pred[:, 0].cpu().numpy(), pred[:, 1].cpu().numpy(), 'b-', linewidth=2)
        axes[1, 1].set_xlabel('u')
        axes[1, 1].set_ylabel('v')
        axes[1, 1].set_title('Phase Portrait')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        if save_path:
            os.makedirs(os.path.dirname(save_path) or '.', exist_ok=True)
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"  Visualization saved to {save_path}")
        self.model.train()


if __name__ == "__main__":
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    print("Model: Coupled ODE System")
    print("="*60)
    
    np.random.seed(42)
    n_data = 100
    t_data = np.random.uniform(0, 5, n_data).reshape(-1, 1)
    
    # Synthetic coupled system data
    c1, c2, k1, k2, coup = 0.5, 0.3, 1.0, 0.8, 0.1
    u = 0.5 * np.exp(-c1 * t_data) * np.cos(k1 * t_data)
    v = 0.3 * np.exp(-c2 * t_data) * np.cos(k2 * t_data)
    u_data = np.column_stack([u, v]) + np.random.randn(n_data, 2) * 0.01
    
    t_data_t = torch.tensor(t_data, dtype=torch.float32, device=device)
    u_data_t = torch.tensor(u_data, dtype=torch.float32, device=device)
    
    model = CoupledODEPINN(hidden_layers=[64, 64, 64])
    trainer = CoupledODETrainer(model, lr=1e-3, device=device)
    
    print("\\nStarting training...")
    trainer.train(t_data_t, u_data_t, epochs=3000, verbose=True)
    
    os.makedirs("results", exist_ok=True)
    trainer.save_checkpoint("results/coupled_ode_model.pth")
    trainer.visualize(save_path="results/coupled_ode.png")
    
    params = model.get_params()
    print(f"\\nLearned: c1={params['c1']:.4f}, c2={params['c2']:.4f}, k1={params['k1']:.4f}, k2={params['k2']:.4f}, coupling={params['coupling']:.4f}")
    print("\\n✅ Coupled ODE PINN training complete!")
'''
    return {'code': code}


