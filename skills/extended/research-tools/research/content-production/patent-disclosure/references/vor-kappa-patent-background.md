# VOR-Kappa 角专利：技术背景参考

> 完整交底书：`/media/yakeworld/sda2/Synthos/skills/patent-disclosure/examples/VOR驱动Kappa角闭式标定方法及系统_202605211700.md`
> 完成日期：2026-05-21

## 案件概要
**案件名称**：一种基于VOR驱动三维眼动追踪的Kappa角闭式标定方法及系统
**核心创新**：利用VOR生理机制，仅需3D眼动追踪数据闭式解算三维Kappa角

## 数学核心
- 罗德里格斯变换 → 核心关系：$1-\cos\gamma = K(1-\cos\theta)$
- 正交方向分离 → $K_x$ (Pitch), $K_y$ (Yaw)
- 闭式解：$\omega = \arccos(3-2(K_x+K_y))$, $\phi = \operatorname{atan2}(\sqrt{1-K_y},\sqrt{1-K_x})$

## 查新结论
- Kappa角标定文献65篇，VOR+Kappa组合 **0篇**
- 方法：Semantic Scholar API检索
- **新颖性确认通过**

## 开发陷阱记录

### 陷阱1：VOR≠双约束
❌ 初始将VOR和固视作为两个独立约束。
✅ **正确**：VOR的本质也是固视（VOR维持固视），统一生理过程。

### 陷阱2：不需要头动传感器
❌ 初始考虑用IMU测量头动旋转。
✅ **正确**：3D眼动追踪可直接测量眼球的完整三维旋转（含旋转轴和扭转分量），利用VOR增益≈1，眼动旋转等价于头动旋转。

### 陷阱3：不需要视轴信息
❌ 传统方法必须知道视轴方向。
✅ **正确**：两组正交VOR（Pitch+Yaw）的光轴旋转轨迹本身包含Kappa角的全部信息。