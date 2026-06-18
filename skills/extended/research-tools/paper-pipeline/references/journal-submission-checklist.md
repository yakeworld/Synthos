# 期刊投稿清单 — Measurement 及通用Elsevier期刊

> 2026-06-18 新增。用户要求将 3D Eyeball 论文投稿至 Measurement (Elsevier)。

## Measurement 期刊 (ISSN 0263-2241)

- 网址: https://www.sciencedirect.com/journal/measurement
- 投稿系统: Editorial Manager (`https://www.editorialmanager.com/meas/default2.aspx`)
- 影响因子: ~5.6 (2024)
- 范围: 测量科学、仪器、传感器、信号处理、质量评估
- 与本文关联: 虹膜分割精度（Dice/IoU）属于测量科学范畴

## Elsevier 通用投稿文件清单

| # | 文件 | 格式 | 必须 |
|:--|:-----|:-----|:----:|
| 1 | Manuscript (clean) | PDF (from LaTeX) | ✅ |
| 2 | Cover Letter | PDF/Text | ✅ |
| 3 | Graphical Abstract | PDF (嵌入tex或单独) | ✅ |
| 4 | Highlights | 文本(3-5条) | ✅ |
| 5 | Figures | TIFF/JPEG/PDF (≥300dpi) | ✅ |
| 6 | Source Files (.tex) | LaTeX源码 | ✅ |
| 7 | BibTeX file (.bib) | BibTeX | ✅ |
| 8 | CRediT Author Statement | PDF/文本 | ✅ |
| 9 | Declaration of Competing Interest | PDF/文本 | ✅ |
| 10 | Data Availability Statement | PDF/文本 | ✅ |
| 11 | Funding Statement | PDF/文本 | ✅ |
| 12 | 作者信息表 (Name/Affiliation/Email) | 文本 | ✅ |

## Measurement 特殊要求

- 要求作者提供 ORCID
- 建议推荐审稿人（可选）
- 需要声明代码和数据可用性
- 不接受同时投递其他期刊的预印本（arXiv需注意）

## 投稿流程

```
1. 论文干净编译 → 生成 final.pdf
2. 准备 cover letter (2-3段，突出贡献)
3. 生成 CRediT 贡献声明
4. 准备 declarations (COI + Data Availability + Funding)
5. 登录 Editorial Manager → Submit New Submission
6. 按系统引导逐项上传文件
7. 确认所有格式要求
8. 提交，获取 Manuscript ID
```

## 投稿路径速查

| 期刊 | 投稿系统 | 路径 |
|:-----|:---------|:-----|
| Measurement | Editorial Manager | `https://www.editorialmanager.com/meas/` |
| 其他Elsevier | 同左 | 替换期刊缩写 |
| Springer | Springer Manuscript | 不同系统 |
| IEEE Transactions | IEEE eScholarship | 不同系统 |
| Nature Portfolio | 不同系统 | 不同系统 |

## 实战备忘（2026-06-18）

- Editorial Manager 页面在浏览器中可能超时（60s+），优先用终端工具操作
- 论文目录 `/media/yakeworld/sda2/Synthos/outputs/papers/3d-eyeball-iris-segmentation/` 已通过 `scp` 拷贝至 `work1:/mnt/nfs/article/3d-eyeball-iris-segmentation/` 供用户通过 NFS 共享访问
- 最终版本：`revision20241118v3.pdf`（2.7MB，35页，D10a=89.1%，0孤儿，0僵尸，干净编译）
- 作者顺序已调整：Qiqi Shao 移为第二作者
- 作者：Ruihu Yang(1), Qiqi Shao(1), Jie Zhou(2), Yanjun Li(1), Xiaoqing Li(1), Xiaokai Yang(1*)

## 作者单位

| 编号 | 单位 |
|:-----|:-----|
| 1 | Postgraduate Training Base Alliance of Wenzhou Medical University, Wenzhou People's Hospital, Wenzhou, China |
| 2 | National Engineering Research Center of Ophthalmology and Optometry, Eye Hospital, Wenzhou Medical University, Wenzhou, China |
