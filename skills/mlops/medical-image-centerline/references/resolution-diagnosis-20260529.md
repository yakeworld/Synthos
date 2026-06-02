# 分辨率参数问题诊断记录 (2026-05-29)

## 问题
centerline_extraction.py 在uCT数据上产生过短的弧长。

## 表现
- AC弧长: 2.6mm (期望 8-12mm)
- PC弧长: 5.3mm (期望 7-12mm)  
- LC弧长: 5.6mm (期望 6-9mm)

## 诊断流
1. 检查提取点数: AC=41（仅覆盖弧顶），正常应有 >100
2. 检查体素范围: 39体素（2.4mm），正常应有 ~160体素（10mm）
3. 对比CT数据（同算法）: AC=11.3mm ✓ → 问题在分辨率而非算法
4. CT间距0.3-0.5mm, uCT间距0.06-0.08mm → max_count固定40步不够用

## 根因
`_greedy_walk` 的 `max_count=40`（硬编码默认值）:
- CT(0.3mm): 40步 × ~1.5体素/步 × 0.4mm/体素 = 24mm → 够
- uCT(0.06mm): 40步 × ~1.5体素/步 × 0.06mm/体素 = 3.6mm → 不够!

## 修复
```python
mean_spacing = np.mean(spacing_zyx)
scale = max(1.0, 0.3 / mean_spacing)  # CT参考=0.3mm
max_count = int(40 * scale)            # uCT→~200
jump_threshold = max(5.0, 3.0 * scale)
```

修复后: AC=11.5mm, PC=17.0mm, LC=10.8mm ✓

## 残余问题
- PC可延伸到~17mm（含总脚），解剖上可接受，不干扰螺旋参数b
- 部分病例只有2管能被提取（如ZETA_R）→ 后备HR贪婪行走
- 各向异性体素(0.05×0.05×0.15mm)需重采样到各向同性

## 更好的替代方案
后来开发的**路线C（中位切+图直径法）** 完全不需要max_count参数，用图直径自动捕获全弧长，对分辨率不敏感。
