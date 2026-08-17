---
name: ellipse-3d-anatomy-constrained
description: 1. 确认输入参数完整
signature: 'ellipse-3d-anatomy-constrained -> mlops: synthetic skill for ellipse 3d
  anatomy constrained'
allowed-tools:
- terminal
- read_file
- write_file
- session_search
version: 1.0.0
license: MIT
metadata:
  synthos:
    atom_type: mechanical
    description: 1. 确认输入参数完整
    signature: 'ellipse-3d-anatomy-constrained -> mlops: synthetic skill for ellipse
      3d anatomy constrained'
    priority: P2
    synthos_version: 1.0.0
    synthos_skill_md_hash: auto
    synthos_asserted_compliance: P2,P3
    synthos_mechanical_atoms: ''
category: private
---

## Operational Steps
1. 确认输入参数完整
2. 执行核心操作（参考本目录下的 scripts/ 或 references/）
3. 验证输出符合契约
4. 保存结果并报告
category: mlops
related_skills: ['ellipse-to-3d-circle']
description: 用户特异性推导：椭圆→3D圆通过解剖约束（R=2r, d=√3r）消除方位角模糊。覆盖法向量公式、光轴平面、Rodrigues旋转、多帧眼球中心求解。源自AKNE眼动研究笔记。
signature: "ellipse-3d-anatomy-constrained -> processed_result"
version: 1.0.0

# ellipse-3d-anatomy-constrained: 椭圆→3D圆解剖约束法

## 边界

将二维椭圆参数反推为三维空间圆几何参数，通过解剖约束消除方位角模糊。

核心创新：用户方法通过 R_eyeball = 2*R_iris、d = √3*R_iris 将自由度从2压缩到0。

输入：椭圆参数 + 旋转角 + （可选）多帧
输出：3D法向量（光轴）、虹膜中心3D、眼球中心、旋转矩阵

## 核心推导

### 法向量
n = [sin(alpha)*sin(beta), -sin(alpha)*cos(beta), cos(alpha)]
cos(alpha) = b/a, beta = 椭圆旋转角。

### 光轴投影直线
cos(beta)*(x - x1) + sin(beta)*(y - y1) = 0

### 多帧确定眼球中心
至少两帧椭圆 → 光轴直线交点 = 眼球中心。

### 解剖约束
R_eyeball = 2*R_iris, d = √3*R_iris
z1 = sqrt(3*R_iris^2 - (x1-x0)^2 - (y1-y0)^2)

### Rodrigues 旋转
M = I + [v]_x + [v]_x^2 / (1 + O·O')

## Pitfalls
- 
- 

## Verification
- 
- 
1. 单帧无法确定眼球中心
2. z1 为虚数时：椭圆参数与解剖约束矛盾
3. 用户设定 Center_eye 在 XY 平面 (z=0)
4. 多帧需迭代：先估计 → 计算 → 收敛

## Related
- ellipse-to-3d-circle — 通用椭圆→3D圆方法（正交投影基础）
- eye-tracking-platform — K230嵌入式眼动平台

## 契约层 · BOUNDARY

**边界**：技能功能边界。

## 契约层 · IO_CONTRACT

**输入**：请求描述、上下文信息。
**输出**：执行结果、状态反馈。

## 验证清单 · VERIFICATION

- [ ] 输入椭圆参数（a, b, 旋转角 beta）完整且满足 a≥b，`cos(alpha)=b/a` 在 [-1,1] 内
- [ ] 法向量 n=[sinα·sinβ, -sinα·cosβ, cosα] 单位化且方向正确
- [ ] 解剖约束 R_eyeball=2·R_iris、d=√3·R_iris 已代入，自由度从 2 压缩到 0
- [ ] z1 为实数：3·R_iris²-(x1-x0)²-(y1-y0)² ≥ 0，否则判定椭圆参数与解剖约束矛盾并检查输入
- [ ] 眼球中心由至少两帧光轴投影直线交点求解（单帧无法确定）
- [ ] 多帧求解采用迭代策略（先估计→计算→收敛）以消除初始值依赖
- [ ] Rodrigues 旋转矩阵 M = I + [v]_x + [v]_x²/(1 + O·O') 满足正交性

## 核心原则 · PRINCIPLES

1. **准确为先**: 所有输出必须经过事实核查，不编造数据
2. **证据驱动**: 每个结论必须可追溯到具体证据或数据源
3. **可复现性**: 每一步操作必须可重复，结果可验证

## 约束规则 · RULES

1. **输入约束**: 参数类型、范围、格式必须校验
2. **输出约束**: 返回值结构、编码、命名必须一致
3. **异常约束**: 错误信息必须包含上下文和恢复建议
4. **安全约束**: 不执行未验证的任意代码，不暴露内部状态

## Golden 集合 · GOLDEN SET

- **Golden Input**: 至少两帧椭圆参数（每帧 a≥b、旋转角 β），虹膜半径 R_iris 已知，眼球中心在 XY 平面 (z=0) —— 触发解剖约束 R_eyeball=2R_iris、d=√3·R_iris 将自由度从 2 压缩到 0
- **Golden Output**: 3D 法向量 n=[sinα·sinβ, -sinα·cosβ, cosα]（α 由 cosα=b/a 解出，单位化且方向正确）、虹膜中心 3D 坐标（z1 为实数）、由两帧光轴投影直线交点迭代收敛（先估计→计算→收敛）得到的眼球中心、满足正交性的 Rodrigues 旋转矩阵 M=I+[v]_x+[v]_x²/(1+O·O')
- **Golden Error**: 3·R_iris²-(x1-x0)²-(y1-y0)² < 0 时 z1 为虚数 —— 判定椭圆参数与解剖约束矛盾，不输出虚数，返回带上下文的错误信息并检查输入数据有效性（ELLI-003）；单帧输入则拒绝求解眼球中心（单帧无法确定，ELLI-002）

> Golden 集合是测试的单一真理来源。所有改进必须通过 golden 测试。

> 违反规则的操作视为不安全，必须拒绝或隔离。

> 违反任何原则的输出视为失败。原则优先级：准确 > 证据 > 可复现。

> 每项验证必须可执行、可记录、可复现。验证失败时记录原因和修复。

# Ellipse 3D Anatomy Constrained---

> (P032 去重: 以下为合并前第二份中的 1 行独有内容, 保留以防丢失)
# Ellipse 3D Anatomy Constrained
## Genes (策略基因)
> 紧凑策略表示。条件→策略。需要深度时参考完整文档。
- **[ELLI-001]** 单帧椭圆参数存在方位角模糊 → 引入解剖约束（R_eyeball=2R_iris, d=√3R_iris）将自由度从2压缩至0以消除歧义
- **[ELLI-002]** 需要确定眼球中心位置 → 利用至少两帧椭圆数据，通过光轴投影直线的交点求解眼球中心
- **[ELLI-003]** 计算虹膜中心深度坐标 z1 出现虚数 → 判定椭圆参数与解剖约束矛盾，需检查输入数据有效性
- **[ELLI-004]** 多帧数据求解眼球中心存在初始值依赖 → 采用迭代策略（先估计→计算→收敛）以获取稳定解
- **[ELLI-005]** 需要构建三维空间旋转关系 → 应用 Rodrigues 旋转公式 M = I + [v]_x + [v]_x^2 / (1 + O·O') 进行矩阵推导
- **[ELLI-006]** 输入参数完整性未知 → 在执行核心操作前必须校验参数类型、范围及格式，确保符合输入约束

## 示例 · EXAMPLES

1. **输入**: 单帧椭圆参数 a=8, b=5, 旋转角 beta。
   **操作**: 按 ELI-001 引入解剖约束（R_eyeball=2R_iris, d=√3R_iris）将自由度从 2 压缩到 0，计算 `cos(alpha)=b/a` 与单位化法向量 n。
   **验证**: 核对验证清单第 1、2 条——a≥b 且 cos(alpha)∈[-1,1]，法向量单位化且方向正确。

2. **输入**: 计算 z1 = sqrt(3R_iris²-(x1-x0)²-(y1-y0)²) 时根号内为负。
   **操作**: 按 ELI-003 判定椭圆参数与解剖约束矛盾，不输出虚数结果，检查输入数据有效性并给出恢复建议。
   **验证**: 触发验证清单第 4 条——3R_iris²-(x1-x0)²-(y1-y0)² < 0，返回带上下文的错误信息（RULES 第 3 条）。

3. **输入**: 至少两帧椭圆数据，需求解眼球中心。
   **操作**: 按 ELI-002 取两帧光轴投影直线交点得眼球中心，按 ELI-004 用迭代策略（先估计→计算→收敛）消除初始值依赖。
   **验证**: 核对验证清单第 5、6 条——单帧无法确定已排除，多帧迭代收敛后眼球中心稳定。