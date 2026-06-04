# WDBC CRISP-DM 双质量检查实战 (2026-06-04)

## 背景

对 crispdm-wdbc 论文（Wisconsin 乳腺癌数据集预测模型）执行完整双质量检查。这是第一篇"null result"论文——发现泄漏在 WDBC 上几乎无影响（ΔF1 = -0.0010）。

## 关键发现

### 🔴 L0.5: 实验从未运行

`03-code/results_wdbc/` 目录不存在。论文 Table 1 (8-classifier benchmark) 和 Table 2 (消融4级) 的全部数值 **未经验证**。

**处置**：后台运行实验（`python3 wdbc_crispdm_helix.py`），待完成后逐条比对。

### 🔴 ProcessDriven 自引环

`ProcessDriven`（Yang & Zhou, 2025, Under review）被 4 处引用（L48, L76, L166, L226）：
- 违反"未发表不引"铁律
- 形成 companion paper 递归自引环（Pima 论文也引用 ProcessDriven）
- D10a=100% 但扫描漏检

### 🟡 消融设计缺陷

Medium Leakage (Level 3) 描述与 Minor Leakage (Level 2) 完全一致（"Global Scale + Isolated SMOTE"），只有 3 个有效级别而非 4 个。

## 手动 Layer B 评审结果

| 维度 | 评分 | 关键问题 |
|:-----|:----:|:---------|
| D1 科学贡献 | 0.82 | "difficulty-proportional damage" 原则新颖，但仅2数据集 |
| D2 方法学 | 0.78 | Medium=Minor设计缺陷，缺标准差 |
| D3 结果可信 | 0.70 | 实验未运行 → 全部数值待定 |
| D4 完整性 | 0.85 | IMRaD 完整 |
| D5 清晰性 | 0.88 | 叙事流畅 |
| D6 新颖性 | 0.80 | null result + 风险分层框架 |
| D7 引用质量 | 0.65 | ProcessDriven + D9=0 |
| **校准分** | **0.78** | 低于 T2 (0.80) |

## 技能提炼

1. **实验运行检查**：L0.5 阶段 I 新增 Step 4，检查实验输出目录是否存在
2. **Companion paper 陷阱**：新增陷阱 #27，检测 "Under review"/"in press" 递归自引
3. **实验未运行降级协议**：新增 Layer B 降级协议分支
