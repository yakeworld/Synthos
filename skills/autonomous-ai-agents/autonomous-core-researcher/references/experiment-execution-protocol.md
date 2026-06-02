# Experiment Execution Protocol

> Captured from Cycle 4 (2026-05-29): H01-PINN-OPERATOR-MEDICAL on FastMRI synthetic data.
> Use this pattern when implementing operator learning comparisons from code skeletons.

## When Given a Code Skeleton (100% NotImplementedError)

### Phase 1: Implement Working Code

1. **Architecture first** — PyTorch nn.Module classes before data loading
   - DeepONet pattern: BranchNet(MLP) + TrunkNet(MLP) → einsum('bl,bpl->bp') + bias
   - FNO pattern: SpectralConv2D with FFT → rFFT2 → linear → irFFT2

2. **Dataset design** — Sensor-point sampling is CRITICAL for DeepONet:
   ```python
   # DeepONet datasets must sample the function at specific sensor coordinates
   # NOT flatten the entire function as branch input
   
   class MyDataset(Dataset):
       def _sample_sensors(self, H, W, n_points=64):
           side = int(np.ceil(np.sqrt(n_points)))
           y = torch.linspace(-1, 1, side)
           x = torch.linspace(-1, 1, side)
           gy, gx = torch.meshgrid(y, x, indexing='ij')
           coords = torch.stack([gx.ravel(), gy.ravel()], dim=-1)
           return coords[:n_points]  # ensure exact count
       
       def __getitem__(self, idx):
           # Branch input: interpolate at sensor locations
           grid = sensor_coords.unsqueeze(0).unsqueeze(0)  # (1, 1, S, 2)
           data_4d = measurement.unsqueeze(0).unsqueeze(0)  # (1, 1, H, W)
           branch_in = F.grid_sample(data_4d, grid, mode='bilinear',
                                     align_corners=True).squeeze()  # (S,)
           
           # Trunk: normalized coordinate grid for every output pixel
           y_coords = torch.linspace(-1, 1, H).unsqueeze(1).expand(H, W)
           x_coords = torch.linspace(-1, 1, W).unsqueeze(0).expand(H, W)
           trunk_in = torch.stack([x_coords, y_coords], dim=-1).reshape(-1, 2)  # (H*W, 2)
           
           # Target: flattened ground truth
           target = img.reshape(-1)  # (H*W,)
           return branch_in, trunk_in, target
   ```

3. **Smoke test each dataset BEFORE training loop**:
   ```python
   ds = MyDataset(data_dir, n_samples=1)
   b, t, y = ds[0]
   model = DeepONet(branch_dim=S, trunk_dim=2, latent_dim=128)
   out = model(b.unsqueeze(0), t.unsqueeze(0))
   loss = F.mse_loss(out, y.unsqueeze(0))
   assert loss < 10, f"Loss too high: {loss}"  # random init should be reasonable
   ```

### Phase 2: Training

4. **Checkpoint strategy** — every 10 epochs + best model:
   ```python
   if epoch % 10 == 0:
       torch.save({"epoch": epoch, "model_state_dict": model.state_dict(), ...})
   ```

5. **Metrics** — track RMSE, PSNR, SSIM on validation set. Save to JSON history.

6. **Learning rate scheduling** — ReduceLROnPlateau (factor=0.5, patience=10) works well.

### Phase 3: Per-Instance PINN Comparison

7. **Fair comparison protocol**:
   - DeepONet: single training run → evaluates all test instances (amortized cost)
   - Per-instance PINN: each test instance gets its own optimization run
   
8. **PINN architecture**: small MLP [2→128→128→128→1],
   trained on a single instance's coordinate→value mapping.

9. **Record compute cost**: DeepONet = total training time; PINN = steps × instances.

### Phase 4: Result Interpretation

10. **Patterns to expect**:

| Pattern | Interpretation | Action |
|---------|---------------|--------|
| RMSE ≈ 1.0, SSIM ≈ 0 | Model predicts mean — no learning | Insufficient sensor points or task too hard |
| RMSE < 0.5, SSIM > 0.5 | Model capturing structure | Increase epoch count, try fewer sensors |
| PINN RMSE < DeepONet RMSE | Per-instance helps | Quantify compute cost tradeoff |
| Both fail | Task too hard for both approaches | Write negative result paper |

11. **Negative results are valuable** — they validate the hypothesis that the task requires more sophisticated approaches. Document clearly in pipeline_results.json.

### Phase 5: Save Everything

12. Save to `experiments/{dataset}/`:
    - `training_history.json` — per-epoch metrics
    - `test_metrics.json` — final evaluation
    - `pinn_results.json` — per-instance PINN comparison  
    - `pipeline_results.json` — summary with interpretation
    - `best_model.pt` — trained weights
    - `checkpoint_epoch*.pt` — intermediate checkpoints

## Known Pitfalls

- **CUDA driver too old**: `UserWarning: CUDA initialization: The NVIDIA driver on your system is too old`. Check with `nvidia-smi` → CUDA Version field. PyTorch 2.11 needs driver supporting CUDA 12.4+. On driver 535.309 (CUDA 12.2), all training falls back to CPU. Fix: update NVIDIA driver or install a PyTorch wheel compiled for CUDA 12.2.
- **DMRIDiffusion scalar parameters**: dmri data may have scalar (not per-voxel) ground truth → treat as global parameter estimation, not image mapping. Trunk becomes single point (0,0), output is scalar.
- **JSON serialization**: Never include PyTorch Module objects in dicts that get JSON.dump'd. Remove them from result dicts before saving.
- **ssim metric may be near-zero** for random initialization — not a bug, SSIM measures structural similarity which random noise has none of.
