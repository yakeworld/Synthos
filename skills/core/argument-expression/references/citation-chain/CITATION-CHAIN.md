# 引用链分析 — 方向性与网络结构

> 理论来源：网络科学 (Barabási, 2016); 引文分析理论 (Garfield, 1979)

## 引用方向性分析

### Forward Citation Analysis (前向引用)

```
定义: 分析本文被后续文献引用的情况

检查项:
  - 被引次数 (总/年)
  - 核心文献占比 (高被引 = 引用该领域的基石论文)
  - 引用方向:
    * 正面引用 (支撑本文观点)
    * 负面引用 (反驳/批评本文)
    * 中性引用 (方法引用/背景引用)

评分:
  高被引 + 正面引用为主 → 1.0
  中等被引 + 混合引用 → 0.6
  低被引 + 负面引用为主 → 0.2
```

### Backward Citation Analysis (后向引用)

```
定义: 分析本文引用了哪些"基石文献"

检查项:
  - 是否引用了该领域的关键文献?
  - 是否覆盖了核心引用网络?
  - 自引用比例 (过高 = 自恋; 过低 = 脱离领域)
  - 经典文献 vs 新兴文献的比例

评分:
  覆盖核心网络 + 自引合理 (<10%) → 1.0
  覆盖主要文献 + 自引合理 → 0.7
  遗漏关键文献 → 0.4
  自引过高 (>30%) → 0.2
```

## 网络结构分析

```
核心-边缘结构 (Core-Periphery):
  - 核心: 高被引、高引用文献
  - 边缘: 低被引、低引用文献
  - 本文是否连接了核心?

枢纽检测 (Hub Detection):
  - 高度中心性的文献
  - 本文是否引用了足够多的高中心性文献?

引用时效性:
  - 近5年文献占比 (30-60% 理想)
  - 经典文献占比 (10-30% 理想)
```

## 与6种引用功能的整合

```
引用功能 (BG/SUP/CMP/GAP/METH/OBJ) + 方向性分析:
  BG + 核心文献 → 领域定位准确
  SUP + 正面引用 → 论证支撑有力
  CMP + 混合引用 → 批判性分析
  GAP + 边缘文献 → 定位研究空白
  METH + 方法文献 → 方法选择合理
  OBJ + 枢纽文献 → 研究目标明确

完整画像 = 功能标注 + 方向性 + 网络结构
```

## 不合格标准

```
1. 无 forward citation 数据 → WARNING
2. 无 backward citation 数据 → WARNING
3. 自引用 > 30% → FAIL
4. 引用网络无核心连接 → WARNING
5. 引用时效性异常 (<20% 近5年 OR >80% 近5年) → WARNING
```

## 理论来源

- Garfield, E. (1979). "Citation analysis." *Journal of the American Medical Association*, 242(25), 277-278.
- Barabási, AL (2016). *Network Science*. Cambridge University Press.
- Bornmann, L. & Mutz, R. (2015). "Growth rates of modern science." *Journal of the Association for Information Science and Technology*, 66(7), 1351-1355.
