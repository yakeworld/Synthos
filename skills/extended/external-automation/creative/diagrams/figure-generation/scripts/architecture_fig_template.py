#!/usr/bin/env python3
"""
Figure 1: CRISP-DM Helix Framework Architecture
figure-generation skill: 契约确认 → 生成Python脚本 → QA审核 → 输出

使用方法:
  1. 修改 DESIGN SYSTEM 变量调整布局
  2. 运行 python3 generate_figN.py
  3. 若 QA 不通过则无输出，修复后重跑
"""
import os, sys, math, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

# ═══════════════════════════════════════════════════════════════════════
# DESIGN SYSTEM — 调整这些变量控制全部布局
# ═══════════════════════════════════════════════════════════════════════
SINGLE_H = 0.50    # 单行文字框高
DOUBLE_H = 0.70    # 双行文字框高
BOX_W    = 3.0     # 侧栏框宽 (≥3.0避免长标题碰边)
CORE_W   = 4.8     # 核心框宽
BOT_W    = 5.2     # 底部链框宽
PAD_BOX  = 0.12    # 所有框统一内边距

GAP_S    = 0.20    # 同区内框间距
GAP_M    = 0.55    # 区间隔
GAP_T    = 0.35    # 标题→内容间距
PAD_BOT  = 0.50    # 底部留白

FIG_W    = 7.5     # 画布宽
FIG_H    = 9.5     # 画布高 (不够会自动扩展)

# ═══════════════════════════════════════════════════════════════════════
# QA: 文字宽度估算 + 验证报告
# ═══════════════════════════════════════════════════════════════════════
def text_width_inches(text, fontsize_pt):
    return len(text) * fontsize_pt * 0.60 / 72.0

class QAReport:
    def __init__(self): self.issues = []
    def check_text_fits(self, label, text, fs, bw, bh, pad):
        tw = text_width_inches(text, fs)
        avail_w = bw - 2*pad; avail_h = bh - 2*pad
        if tw > avail_w:
            self.issues.append(f"[{label}] 文字超宽 '{text[:30]}' ({tw:.2f}in) > {avail_w:.2f}in")
        if fs/72.0 > avail_h:
            self.issues.append(f"[{label}] 文字超高 {fs}pt > {avail_h:.2f}in")
    def check_arrow_inside(self, label, x2, y2, tn, tx, ty, tw, th):
        if not (tx <= x2 <= tx+tw and ty <= y2 <= ty+th):
            self.issues.append(f"[{label}] 箭头终点({x2:.1f},{y2:.1f})在'{tn}'框外")
    def assert_clean(self):
        if self.issues:
            for i in self.issues: print(f"  ❌ {i}")
            sys.exit(1)
        print("  [QA] ✓ All checks passed")

# ═══════════════════════════════════════════════════════════════════════
# LAYOUT: 从底向上计算
# ═══════════════════════════════════════════════════════════════════════
reg_y = PAD_BOT
ab_y  = reg_y + DOUBLE_H + GAP_S
out_y = ab_y  + DOUBLE_H + GAP_S
core_y = out_y + DOUBLE_H + GAP_M
c4_y  = core_y + DOUBLE_H + GAP_M
c3_y  = c4_y   + SINGLE_H + GAP_S
c2_y  = c3_y   + SINGLE_H + GAP_S
c1_y  = c2_y   + SINGLE_H + GAP_S
strand_title_y = c1_y + SINGLE_H + GAP_S
title_y = strand_title_y + SINGLE_H + GAP_T
total_h = title_y + 0.35
fig_h = max(FIG_H, total_h + 0.5)

xc = 5.0; bx0 = xc - BOT_W/2; cx0 = xc - CORE_W/2
lx = xc - 3.2; lx0 = lx - BOX_W/2
rx = xc + 3.2; rx0 = rx - BOX_W/2

# ═══════════════════════════════════════════════════════════════════════
# PRE-GENERATION QA
# ═══════════════════════════════════════════════════════════════════════
print("  [QA] Running...")
qa = QAReport()
qa.check_text_fits('Title', 'CRISP-DM Helix Framework Architecture', 11, 10, 0.5, 0.1)
qa.check_text_fits('LeftTitle', 'Clinical Credibility Strand', 6.5, BOX_W, SINGLE_H, PAD_BOX)
qa.check_text_fits('RightTitle', 'Engineering Execution Strand', 6.5, BOX_W, SINGLE_H, PAD_BOX)
for t in ['Objective: Maximize Recall','Minimize False Negatives','SHAP on Clean Pipeline','Clinical Trustworthiness',
           'CV-Fold Isolation','Within-Fold Fit','No Global Preprocessing','Reproducible Pipelines']:
    qa.check_text_fits('Sub', t, 6.5, BOX_W, SINGLE_H, PAD_BOX)
qa.check_text_fits('Out2', 'F1=0.6868  |  Recall=0.7464  |  Acc=0.7629', 6.5, BOT_W, DOUBLE_H/2, PAD_BOX)
qa.check_text_fits('Abl2', 'No -> Minor -> Medium -> Severe (progressive)', 6.5, BOT_W, DOUBLE_H/2, PAD_BOX)
qa.check_text_fits('Reg2', 'Verified Ceiling -> Automatic Audit Trigger', 6.5, BOT_W, DOUBLE_H/2, PAD_BOX)

core_top = core_y + DOUBLE_H
qa.check_arrow_inside('LArrow', cx0+CORE_W*0.25, core_top, 'Core', cx0, core_y, CORE_W, DOUBLE_H)
qa.check_arrow_inside('RArrow', cx0+CORE_W*0.75, core_top, 'Core', cx0, core_y, CORE_W, DOUBLE_H)
qa.check_arrow_inside('CORE-Out', xc, out_y+DOUBLE_H, 'Output', bx0, out_y, BOT_W, DOUBLE_H)
qa.check_arrow_inside('Out-Abl', xc, ab_y+DOUBLE_H, 'Ablation', bx0, ab_y, BOT_W, DOUBLE_H)
qa.check_arrow_inside('Abl-Reg', xc, reg_y+DOUBLE_H, 'Registry', bx0, reg_y, BOT_W, DOUBLE_H)
qa.assert_clean()

# ═══════════════════════════════════════════════════════════════════════
# RENDER
# ═══════════════════════════════════════════════════════════════════════
GREEN='#8BCF8B'; ORANGE='#E8954A'; PURPLE='#7B5EA7'; WHITE='#FFFFFF'
TEXT_D='#222222'; TEXT_M='#555555'

fig, ax = plt.subplots(figsize=(FIG_W, fig_h))
ax.set_xlim(-0.5, 10.5); ax.set_ylim(0, title_y+0.5); ax.axis('off')

def _box(x,y,w,h,face,edge='#555555',lw=0.5):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle=f'round,pad={PAD_BOX}',
                                 facecolor=face,edgecolor=edge,linewidth=lw,zorder=2))
def _txt(x,y,text,fs=7,bold=False,color=TEXT_D,va='center'):
    ax.text(x,y,text,ha='center',va=va,fontsize=fs,fontweight='bold' if bold else 'normal',
            fontfamily='sans-serif',color=color,zorder=3)
def _arrow(x1,y1,x2,y2,color='#666666',lw=1.0,rad=0,dash=False):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='->',
                                  connectionstyle=f'arc3,rad={rad}',
                                  color=color,linewidth=lw,
                                  linestyle='--' if dash else '-',zorder=1))

# Title
_txt(xc, title_y, 'Your Architecture Title', fs=11, bold=True, va='top')

# Strand Titles
_box(lx0, strand_title_y, BOX_W, SINGLE_H, GREEN, lw=1.0)
_txt(lx, strand_title_y+SINGLE_H/2, 'Left Strand', fs=6.5, bold=True, color='#2D5A2D')
_box(rx0, strand_title_y, BOX_W, SINGLE_H, ORANGE, lw=1.0)
_txt(rx, strand_title_y+SINGLE_H/2, 'Right Strand', fs=6.5, bold=True, color='#6B3D00')

# Sub boxes
for yy,t in zip([c1_y,c2_y,c3_y,c4_y], ['Sub 1','Sub 2','Sub 3','Sub 4']):
    _box(lx0,yy,BOX_W,SINGLE_H,WHITE); _txt(lx,yy+SINGLE_H/2,t,fs=6.5)
for yy,t in zip([c1_y,c2_y,c3_y,c4_y], ['Sub 1','Sub 2','Sub 3','Sub 4']):
    _box(rx0,yy,BOX_W,SINGLE_H,WHITE); _txt(rx,yy+SINGLE_H/2,t,fs=6.5)

# Strand->Core arrows (汇聚到核心顶边内侧)
_arrow(lx, c4_y+SINGLE_H/2, cx0+CORE_W*0.25, core_y+DOUBLE_H, rad=-0.20)
_arrow(rx, c4_y+SINGLE_H/2, cx0+CORE_W*0.75, core_y+DOUBLE_H, rad=0.20)

# Core
_box(cx0, core_y, CORE_W, DOUBLE_H, PURPLE, lw=2.0, edge=PURPLE)
_txt(xc, core_y+DOUBLE_H*0.62, 'Core Title', fs=9, bold=True, color=WHITE)
_txt(xc, core_y+DOUBLE_H*0.28, 'Subtitle', fs=7, color='#E8DCF0')
_arrow(xc, core_y, xc, out_y+DOUBLE_H)

# Bottom chain: Output, Ablation, Registry (或自定义)
for yy, title, sub, color in [
    (out_y, 'Output', 'Metrics', '#D0E8D0'),
    (ab_y,  'Analysis', 'Details', '#F0E8C0'),
    (reg_y, 'Registry', 'Trigger', '#F0C8C8'),
]:
    _box(bx0, yy, BOT_W, DOUBLE_H, color, lw=1.0)
    _txt(xc, yy+DOUBLE_H*0.62, title, fs=7, bold=True)
    _txt(xc, yy+DOUBLE_H*0.28, sub, fs=6.5, color=TEXT_M)

# Bottom chain arrows (最后一个用虚线)
_arrow(xc, out_y, xc, ab_y+DOUBLE_H)
_arrow(xc, ab_y, xc, reg_y+DOUBLE_H, dash=True)

OUTDIR = os.path.join(os.path.dirname(__file__), '..', '05-figures')
os.makedirs(OUTDIR, exist_ok=True)
fig.savefig(os.path.join(OUTDIR, 'fig_architecture.pdf'), bbox_inches='tight', pad_inches=0.15, dpi=300)
print('  [OK] Figure generated')
plt.close()
