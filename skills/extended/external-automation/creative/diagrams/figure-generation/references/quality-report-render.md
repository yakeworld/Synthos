# Quality Report → Visual Figure 渲染模式

## 适用场景
将 Synthos 质检报告（07-quality/*.md）直接渲染为高质量视觉图片。
用于小红书发帖、汇报展示、技术传播。

## 核心模式（三选一）

### 模式 A: HTML + Firefox headless（推荐）
```bash
# 1. 写高质量 HTML（参考 pima-quality-report-render-v2.html）
#    - 深色科技风背景 #0B1120
#    - CSS 表格 + 卡片布局 + 渐变色条
#    - 用 Tailwind 或内联 CSS 均可，内联更可靠
# 2. 起 HTTP 服务器
python3 -c "import http.server,socketserver,threading;h=http.server.SimpleHTTPRequestHandler;s=socketserver.TCPServer(('127.0.0.1',8899),h);threading.Thread(target=s.serve_forever,daemon=True).start()"
# 3. Firefox headless 截图
firefox --headless --screenshot /tmp/report.png http://127.0.0.1:8899/report.html
# 4. 如需要精确 1080px 宽：
python3 -c "from PIL import Image; img=Image.open('report.png'); img2=img.resize((1080,int(img.size[1]*1080/img.size[0])),Image.LANCZOS).convert('RGB'); img2.save('report-1080.png')"
```
**优点**: 保真度最高，CSS 排版精确，表格/渐变/图标完美渲染
**缺点**: 需要 HTTP 服务器（Python 一行即可）
**实测**: 1366×3442 → 缩放到 1080×2721，357KB，清晰可读

### 模式 B: Pillow 纯代码
```python
from PIL import Image, ImageDraw, ImageFont
# 手动计算每个元素位置
# 用 ImageDraw.rounded_rectangle 画卡片
# 用 draw.line 画分隔线
# 用 draw.text 写文字（双描 bold）
```
**优点**: 不依赖任何浏览器
**缺点**: 布局计算量大，长报告容易溢出

### 模式 C: 原始 Markdown 表格直接截图
```bash
# 如果报告本身就是漂亮 markdown（如 G1-G7 审计报告）
# 用任何 Markdown 渲染器导出 PNG 即可
```
**优点**: 零成本，原样输出
**缺点**: 风格统一性差

## 设计模板（深色科技风）

### 颜色方案
```
背景: #0B1120 (深海军)
卡片: #1E293B (略浅)
青色: #00BCD4 (强调)
绿色: #34D399 (通过)
橙色: #FBBF24 (警告)
文字: #F1F5F9 (白) / #94A3B8 (灰)
```

### 结构模板
```
┌──────────────────────────────┐
│ [badge] 标题 + 副标题          │  ← 深色渐变头部
│ ───────────────────────────  │
│ G1 结构完整性   [✅ 完整]     │  ← 卡片 + 状态徽章
│ ┌──────────────┐             │
│ │ 表格内容      │             │
│ └──────────────┘             │
│ ... (6个 G 章节)              │
│ ┌─ 综合评分 122/140 ───────┐ │  ← 汇总卡片
│ │ D1: 15/15  D2: 10/15 ... │ │
│ └──────────────────────────┘ │
│ 修正记录 (旧值→新值 表格)    │
│ ✅ 结论                      │
│ ⏳ 待验证                    │
│ ─────────────────────────── │
│ Synthos Audit Engine · 2026  │  ← 底部
└──────────────────────────────┘
```

### 关键原则
1. **每个章节独立卡片** — 圆角 + 微边框
2. **状态用徽章/颜色** — ✅绿 / ⚠️橙 / ❌红
3. **修正记录用删除线** — 旧值红色删除线，新值绿色高亮
4. **综合评分进度条** — 线性渐变填充
5. **结论前置** — 最重要的信息在最上面

## 相关 HTML 模板
- `/tmp/pima-quality-report-render.html` — 浅色版
- `/tmp/pima-quality-report-render-v2.html` — 深色科技风（推荐）
- `/tmp/pima-quality-report-v4.py` — Pillow 纯代码版

## 已知坑
- Firefox `--width` 只控制渲染宽度，不控制窗口大小。默认 1366px 窗口能完整渲染大部分报告
- Firefox `--screenshot` 路径必须是绝对路径
- 截图是 RGBA，需要 `.convert('RGB')` 保存
- CSS 渐变和边框阴影在截图时可能表现不一致，尽量用纯色替代
