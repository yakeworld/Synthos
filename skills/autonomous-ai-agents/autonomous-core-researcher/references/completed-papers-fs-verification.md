# Completed Papers vs Filesystem Consistency Verification

> 2026-06-04 实战: `completed_papers` 列表含50条目，但 `3d-eye-bppv-diagnosis` 为平铺目录（非09-dir），`pinn-operator-learning-generalization` 为实验结论无 .tex，另有3个空09-dir壳（individualized-bppv-simulation, scc-pd-biomarker, gap-paper-35）。

## 问题

`completed_papers` 是自报告产物，累积方式追加。随时间推移可能出现：
- **历史遗留论文**: 09-dir标准化前完成的论文，平铺在根目录，无QC报告
- **实验结论误归**: 证伪实验报告的目录被加入 completed_papers（有 experiment_conclusion.md 但无 .tex）
- **空壳目录**: paper_init 创建了09-dir结构但从未写入内容

## 一次扫描验证脚本

```bash
cd /media/yakeworld/sda2/Synthos/outputs/papers

# 对所有非 _todo/_hold 子目录，检查结构完备性
for d in */; do
  name=$(basename "$d")
  [[ "$name" == _* ]] && continue
  
  # 检测标准化结构
  has_standard="$([ -d "$d/01-manuscript" ] && echo Y || echo N)$([ -d "$d/06-references" ] && echo Y || echo N)"  
  has_tex=$(find "$d" -maxdepth 1 -name "*.tex" -type f 2>/dev/null | head -1)
  has_manu_tex=$(find "$d/01-manuscript" -name "*.tex" -type f 2>/dev/null | head -1 2>/dev/null)
  has_qc=$(find "$d" -maxdepth 2 -name "quality-report.md" 2>/dev/null | head -1)
  has_conclusion=$(find "$d" -name "experiment_conclusion.md" 2>/dev/null | head -1)
  
  # 检查是否为空洞（有09-dir但全空）
  if [ "$has_standard" = "YY" ]; then
    content_count=$(find "$d" -maxdepth 4 -type f ! -path "*/.git/*" 2>/dev/null | wc -l)
    if [ "$content_count" -le 3 ]; then
      echo "STUB:    $name (dirs but no content)"
    elif [ -z "$has_manu_tex" ] && [ -z "$has_tex" ]; then
      echo "NO_TEX:  $name (standard dirs but no .tex)"
    else
      echo "OK:      $name"  # 标准 + 有tex
    fi
  elif [ -n "$has_tex" ] && [ -n "$has_qc" ]; then
    echo "LEGACY:  $name (flat dir, has QC report)"
  elif [ -n "$has_tex" ] && [ -z "$has_qc" ]; then
    echo "LEGACY:  $name (flat dir, no QC report)"
  elif [ -n "$has_conclusion" ]; then
    echo "EXP_ONLY:$name (experiment conclusion, no paper)"
  elif [ -z "$has_tex" ] && [ -z "$has_manu_tex" ]; then
    echo "EMPTY:   $name (no .tex found)"
  fi
done
```

## 输出解读

| 标签 | 含义 | 处置 |
|:-----|:-----|:------|
| `OK:` | 标准化09-dir + 有 .tex | 正常，跳过 |
| `LEGACY:` | 平铺目录（非09-dir） | 可迁移到09-dir（P2级，非阻塞） |
| `STUB:` | 空09-dir壳 | 记录到 tracker，下轮可删除或填充 |
| `NO_TEX:` | 有标准化目录但缺 .tex | paper_init 中断，重新 init |
| `EXP_ONLY:` | 仅有实验结论文档 | 从 completed_papers 移除（非论文） |
| `EMPTY:` | 无 .tex/无实验结论 | 空目录，可清理 |

## 实战参考 (2026-06-04)

输出/papers/ 扫描结果:
- 50个 completed_papers 条目: 47个 OK, 1个 LEGACY (3d-eye-bppv-diagnosis: 平铺), 1个 EXP_ONLY (pinn-operator-learning-generalization), 1个 LEGACY无水结构
- 3个未在 completed_papers 中的 STUB: individualized-bppv-simulation, scc-pd-biomarker, gap-paper-35-neuromorphic-eye-tracking
- 1个 LEGACY 无 QC: 3d-eye-bppv-diagnosis (400行 elsarticle 完整综述论文，62参考文献，无 QC report)

**启示**: 即使 tracker 报 "all 50 completed", 文件系统扫描能发现隐藏问题。每次发现阶段（Step 2）应先做文件系统扫描再信任 tracker。
